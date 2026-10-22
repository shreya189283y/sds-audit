"""Step 0: why does the undisclosed flag fire?

Reads SDS text only. Never opens ground_truth.csv.
Run from the project root:
    python -m scripts.check_undisclosed
"""
import contextlib
import io
import re
from pathlib import Path

import pandas as pd

from src.extract import split_sections, parse_ingredients, check_undisclosed

RESULTS = "data/results.csv"
TEXT_DIR = Path("data/text")
OUT = "docs/undisclosed_check.csv"

KEYWORDS = ["trade secret", "proprietary", "confidential", "withheld", "cbi"]
PERCENT_WORDS = re.compile(r"percent|percentage|concentration|%|exact|range", re.I)


def snippet(text, width=120):
    """The text around the first keyword, so you can read what it refers to."""
    lowered = text.lower()
    for key in KEYWORDS:
        m = re.search(r"\bcbi\b", lowered) if key == "cbi" else re.search(re.escape(key), lowered)
        if m:
            start = max(0, m.start() - width)
            return key, " ".join(text[start:m.end() + width].split())
    return "", ""


def classify(rows, key, around):
    """Sort each flagged product into one bucket."""
    if not rows:
        return "no ingredient rows parsed"
    missing = [r.name for r in rows if r.cas is None]
    if missing:
        return "some ingredient has no CAS"
    if key and PERCENT_WORDS.search(around):
        return "all CAS present, keyword near % words"
    if key:
        return "all CAS present, keyword elsewhere"
    return "all CAS present, no keyword"


def main():
    results = pd.read_csv(RESULTS, dtype=str)
    flagged = results[results["undisclosed"].str.strip().str.lower() == "true"]

    out = []
    for pid, level in zip(flagged["product_id"], flagged["level"]):
        path = TEXT_DIR / f"{pid}.txt"
        if not path.exists():
            out.append({"product_id": pid, "level": level, "bucket": "no text file"})
            continue
        section3 = split_sections(path.read_text(encoding="utf-8")).get(3, "")

        # parse_ingredients prints CAS warnings. Hide them so the output stays readable.
        with contextlib.redirect_stdout(io.StringIO()):
            rows = parse_ingredients(section3)
            flag, evidence = check_undisclosed(section3)

        key, around = snippet(section3)
        out.append({
            "product_id": pid,
            "level": level,
            "bucket": classify(rows, key, around),
            "n_rows": len(rows),
            "rows_without_cas": "; ".join(r.name for r in rows if r.cas is None),
            "evidence": evidence,
            "keyword": key,
            "context": around,
        })

    df = pd.DataFrame(out).sort_values(["bucket", "product_id"])
    Path(OUT).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)

    print(f"{len(flagged)} products have undisclosed = True\n")
    print(df["bucket"].value_counts().to_string())
    print("\nBy current level:")
    print(pd.crosstab(df["bucket"], df["level"]).to_string())
    print(f"\nFull detail with context: {OUT}")


if __name__ == "__main__":
    main()