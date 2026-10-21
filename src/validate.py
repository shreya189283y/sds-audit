
import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

import pandas as pd

from src.cas import is_valid_cas

TRUTH = "data/lists/raw/ground_truth_clean.csv"
RESULTS = "data/results.csv"
OUT = "docs/validation_v1.md"
LABELS = "docs/disagreements.csv" 

MANUAL_LEVELS = ["HIGH", "MEDIUM", "LOW", "NONE"]
TOOL_LEVELS = ["HIGH", "MEDIUM", "UNDISCLOSED", "LOW", "UNREADABLE"]
RANK = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}

SAME_MEANING = {("NONE", "LOW")}
SAFER_LISTS = {"EPA SCIL"}


def require_tag(tag="rules-v1"):
    """Stop if the scoring rules were not frozen first."""
    found = subprocess.run(["git", "tag", "-l", tag],
                           capture_output=True, text=True).stdout.strip()
    if found != tag:
        sys.exit(f"Tag {tag} not found. Do T20 (freeze scoring rules) before validating.")


def norm_cas(value):
    """Return a clean, checksum-valid CAS string, or None."""
    if pd.isna(value):
        return None
    s = str(value).strip().replace("\u2013", "-").replace("\u2014", "-").replace(" ", "")
    s = re.sub(r"^0+(?=\d)", "", s)
    if not re.fullmatch(r"\d{2,7}-\d{2}-\d", s):
        return None
    return s if is_valid_cas(s) else None


def load(truth_path, results_path):
    truth = pd.read_csv(truth_path, dtype=str)
    tool = pd.read_csv(results_path, dtype=str)

    for df in (truth, tool):
        df["product_id"] = df["product_id"].str.strip().str.upper()
    truth["concern_level"] = truth["concern_level"].str.strip().str.upper()
    tool["level"] = tool["level"].str.strip().str.upper()

    bad = set(truth["concern_level"]) - set(MANUAL_LEVELS)
    if bad:
        sys.exit(f"Unknown manual levels in {truth_path}: {sorted(bad)}")

    repeats = tool[tool["product_id"].duplicated(keep=False)]
    if len(repeats):
        sys.exit(f"{results_path} repeats product IDs: {sorted(set(repeats['product_id']))}. "
                 "Fix the manifest duplicate first.")
    return truth, tool


def product_levels(truth):
    """One row per product. Manual level = highest level among its rows."""
    ranked = truth.assign(rank=truth["concern_level"].map(RANK)).reset_index(drop=True)
    top = ranked.loc[ranked.groupby("product_id")["rank"].idxmax()]
    return top[["product_id", "concern_level"]].rename(columns={"concern_level": "manual_level"})


def compare_products(manual, tool):
    merged = pd.merge(manual, tool[["product_id", "product_name", "level"]],
                      on="product_id", how="left", indicator=True)
    missing = merged.loc[merged["_merge"] == "left_only", "product_id"].tolist()
    merged = merged.rename(columns={"level": "tool_level"})
    merged["tool_level"] = merged["tool_level"].fillna("MISSING")
    merged["agree"] = [m == t or (m, t) in SAME_MEANING
                       for m, t in zip(merged["manual_level"], merged["tool_level"])]

    columns = TOOL_LEVELS + (["MISSING"] if missing else [])
    matrix = (pd.crosstab(merged["manual_level"], merged["tool_level"])
                .reindex(index=MANUAL_LEVELS, columns=columns, fill_value=0))
    return merged, matrix, missing


def manual_pairs(truth):
    """(product_id, CAS) pairs flagged by hand, plus rows that could not be compared."""
    flagged = truth[truth["concern_level"].isin(["HIGH", "MEDIUM"])].copy()
    flagged["cas_clean"] = flagged["cas"].map(norm_cas)
    no_cas = flagged[flagged["cas_clean"].isna()]
    ok = flagged[flagged["cas_clean"].notna()]
    pairs = set(zip(ok["product_id"], ok["cas_clean"]))
    names = dict(zip(zip(ok["product_id"], ok["cas_clean"]), ok["chemical_name"]))
    return pairs, names, no_cas


def tool_pairs(tool, ids):
    """(product_id, CAS) pairs the tool flagged, for the products in ids only."""
    pairs = set()
    for pid, raw in zip(tool["product_id"], tool["flags_json"]):
        if pid not in ids or pd.isna(raw) or not str(raw).strip():
            continue
        for hit in json.loads(raw):
            if "cas" not in hit:
                sys.exit(f"A flag in {pid} has no 'cas' key. Keys found: {list(hit)}")
            if hit.get("list_name") in SAFER_LISTS:
                continue
            cas = norm_cas(hit["cas"])
            if cas:
                pairs.add((pid, cas))
    return pairs


def load_labels(path):
    """T22 labels keyed by (product_id, cas). Product-level rows leave cas blank."""
    if not Path(path).exists():
        return {}
    df = pd.read_csv(path, dtype=str).fillna("")
    return {(r.product_id.strip().upper(), r.cas.strip()): (r.label, r.explanation)
            for r in df.itertuples()}


def md_table(df):
    """Markdown table without needing the tabulate package."""
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for row in df.itertuples(index=False):
        lines.append("| " + " | ".join("" if pd.isna(v) else str(v) for v in row) + " |")
    return "\n".join(lines)


def build_report(truth_path, results_path, labels_path, expect):
    truth, tool = load(truth_path, results_path)

    manual = product_levels(truth)
    if len(manual) != expect:
        sys.exit(f"Expected {expect} products in {truth_path}, found {len(manual)}.")

    merged, matrix, missing = compare_products(manual, tool)
    labels = load_labels(labels_path)
    ids = set(manual["product_id"])

    m_pairs, names, no_cas = manual_pairs(truth)
    t_pairs = tool_pairs(tool, ids)
    both = sorted(m_pairs & t_pairs)
    manual_only = sorted(m_pairs - t_pairs)
    tool_only = sorted(t_pairs - m_pairs)

    def label_of(pid, cas=""):
        return labels.get((pid, cas), ("", ""))

    out = [f"# Validation report", "",
           f"Generated {date.today()} from `{truth_path}` and `{results_path}`.",
           "Scoring rules frozen at tag `rules-v1`. All figures are counts.",
           f"Counted as agreement besides exact matches: {sorted(SAME_MEANING)}.", ""]

    out += ["## Coverage", "",
            f"Products in ground truth: {len(manual)}",
            f"Products found in tool output: {len(manual) - len(missing)}",
            f"Missing from tool output: {', '.join(missing) if missing else 'none'}", ""]

    agree = int(merged["agree"].sum())
    out += ["## Product level", "",
            "Rows are the manual level. Columns are the tool level.", "",
            md_table(matrix.reset_index().rename(columns={"manual_level": "manual \\ tool"})), "",
            f"Agreement: {agree} of {len(merged)} products.", ""]

    dis = merged[~merged["agree"]].sort_values("product_id")
    rows = [(r.product_id, r.product_name, r.manual_level, r.tool_level, *label_of(r.product_id))
            for r in dis.itertuples()]
    out += ["### Product disagreements", "",
            md_table(pd.DataFrame(rows, columns=["product_id", "product_name", "manual",
                                                 "tool", "label", "explanation"]))
            if rows else "None.", ""]

    out += ["## Chemical level", "",
            f"Found by both: {len(both)}",
            f"Manual only (tool missed): {len(manual_only)}",
            f"Tool only (not in manual review): {len(tool_only)}", ""]

    for title, pairs in [("Manual only", manual_only), ("Tool only", tool_only)]:
        rows = [(pid, cas, names.get((pid, cas), ""), *label_of(pid, cas)) for pid, cas in pairs]
        out += [f"### {title}", "",
                md_table(pd.DataFrame(rows, columns=["product_id", "cas", "chemical_name",
                                                     "label", "explanation"]))
                if rows else "None.", ""]

    out += ["## Manual rows not compared", "",
            "Flagged by hand but no valid CAS, so they cannot be matched by CAS.", "",
            md_table(no_cas[["product_id", "cas", "chemical_name", "concern_level"]])
            if len(no_cas) else "None.", ""]

    summary = (f"{agree} of {len(merged)} products agree. Chemicals: {len(both)} both, "
               f"{len(manual_only)} manual only, {len(tool_only)} tool only. "
               f"{len(no_cas)} manual rows not compared.")
    return "\n".join(out), summary


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--truth", default=TRUTH)
    p.add_argument("--results", default=RESULTS)
    p.add_argument("--labels", default=LABELS)
    p.add_argument("--out", default=OUT)
    p.add_argument("--expect", type=int, default=35)
    args = p.parse_args()

    require_tag()
    report, summary = build_report(args.truth, args.results, args.labels, args.expect)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(report, encoding="utf-8")
    print(summary)
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    main()