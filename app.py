import json
import os
import re
import sys

import pandas as pd
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.audit import audit_one

st.set_page_config(page_title="SDS Chemical Audit", layout="wide")

# ---------- Settings ----------
LEVELS = ["HIGH", "MEDIUM", "UNDISCLOSED", "LOW", "UNREADABLE"]
RANK = {"HIGH": 5, "MEDIUM": 4, "UNDISCLOSED": 3, "LOW": 2, "UNREADABLE": 1}

LEVEL_STYLE = {
    "HIGH": "background-color: #fde2e2; color: #9b1c1c; font-weight: 600",
    "MEDIUM": "background-color: #fdf0d5; color: #8a4b08; font-weight: 600",
    "UNDISCLOSED": "background-color: #ede9fe; color: #5b21b6; font-weight: 600",
    "LOW": "background-color: #e0ecf8; color: #1e4e79",
    "UNREADABLE": "background-color: #eeeeee; color: #444444",
}

LEVEL_MEANING = {
    "HIGH": "At least one ingredient is on Prop 65, the EU SVHC list, or EU Endocrine Disruptor List I.",
    "MEDIUM": "Matches only EU Endocrine Disruptor List II or III, or a listing that applies only under a condition, such as a particle size.",
    "UNDISCLOSED": "No list matches, but at least one ingredient's identity is hidden, so it cannot be checked.",
    "LOW": "No list matches and every ingredient is named. This is not proof that the product is safe.",
    "UNREADABLE": "Scanned or unusual PDF. The tool could not find the ingredient section.",
}

NEXT_STEP = {
    "HIGH": "Consider a replacement. Check whether the listed chemical is a main ingredient or a minor one.",
    "MEDIUM": "Review before reordering. Check the hazard and the concentration on the SDS.",
    "UNDISCLOSED": "Ask the manufacturer for the full composition, or choose a fully disclosed product.",
    "LOW": "No list matches. Chemicals not on these lists are not checked.",
    "UNREADABLE": "Ask the supplier for a text-based SDS, or review this one by hand.",
}

# Keyword in the official endpoint -> plain-language meaning
PLAIN_ENDPOINT = [
    (("cancer", "carcinogen", "57a"), "Linked to cancer"),
    (("mutagen", "57b"), "Can damage genes"),
    (("developmental",), "Can harm a developing baby"),
    (("female", "male", "reproduct", "57c"), "Can harm fertility or reproduction"),
    (("endocrine",), "Can disrupt hormones"),
    (("pbt", "vpvb", "57d", "57e"), "Persists and builds up in the environment"),
    (("57f",), "Of equivalent concern under EU REACH"),
]

PREFIX = r"^(Product\s*(Name|name|Description)|Trade\s*name)\s*:?\s*"


def clean_name(text):
    """Readable product name for display."""
    if pd.isna(text) or str(text).strip() == "":
        return "(no name)"
    name = re.sub(PREFIX, "", str(text)).strip()
    if name.lower().endswith(".pdf"):
        name = name[:-4].replace("_", " ").replace("-", " ").strip().title()
    return name


def plain_endpoint(endpoint):
    """Turn official endpoint wording into plain phrases."""
    low = str(endpoint).lower()
    found = [plain for keys, plain in PLAIN_ENDPOINT if any(k in low for k in keys)]
    return ", ".join(dict.fromkeys(found)) or str(endpoint)


def style_level(value):
    return LEVEL_STYLE.get(value, "")


# ---------- Sidebar: controls ----------
with st.sidebar:
    st.header("Run an audit")
    files = st.file_uploader("Upload SDS PDFs", type="pdf", accept_multiple_files=True)

    if st.button("Run audit", type="primary", use_container_width=True):
        if not files:
            st.warning("Upload at least one PDF first.")
        else:
            bar = st.progress(0, text="Reading SDS files...")
            rows = []
            for i, f in enumerate(files, start=1):
                rows.append(audit_one(f, f"U{i:03d}", f.name))
                bar.progress(i / len(files), text=f"Audited {i} of {len(files)}")
            st.session_state["results"] = pd.DataFrame(rows)
            st.session_state["source"] = f"your upload of {len(files)} files"
            st.success(f"Audited {len(files)} files.")

    if st.button("Try a sample district", use_container_width=True):
        sample = pd.read_csv("data/results.csv")
        st.session_state["results"] = sample
        st.session_state["source"] = f"a sample district of {len(sample)} products"

    st.divider()
    st.markdown(
        "**How it works**\n\n"
        "1. Upload a district's SDS PDFs.\n"
        "2. The tool reads Section 3 and finds each ingredient's CAS number.\n"
        "3. It checks each one against Prop 65, the EU SVHC list, and the EU "
        "endocrine disruptor lists."
    )

# ---------- Header ----------
st.title("SDS Chemical Audit")
st.write(
    "Find which products in a school district's inventory contain chemicals on "
    "major regulatory hazard lists, and which ones hide their ingredients."
)

# ---------- Welcome screen ----------
if "results" not in st.session_state:
    st.info("Upload SDS PDFs in the sidebar, or click **Try a sample district** to see an example.")
    c1, c2, c3 = st.columns(3)
    c1.markdown("### 1. Upload\nDrop in the Safety Data Sheets for your district's products.")
    c2.markdown("### 2. Audit\nEvery ingredient is checked against four regulatory lists.")
    c3.markdown("### 3. Review\nSee which products to replace first, and why.")
    st.stop()

# ---------- Results ----------
df = st.session_state["results"].copy()
df["display_name"] = df["product_name"].map(clean_name)
st.caption(f"Showing results for {st.session_state.get('source', 'your audit')}.")

# Summary
st.subheader("Summary")
counts = df["level"].value_counts()
for col, level in zip(st.columns(5), LEVELS):
    col.metric(level, counts.get(level, 0), help=LEVEL_MEANING[level])

st.info(
    "Ingredients are checked against Prop 65, the EU SVHC list, and the EU endocrine "
    "disruptor lists. **LOW means no list match, not proven safe.** Chemicals not on "
    "these lists, such as some preservatives and plasticizers, are not flagged."
)
with st.expander("What the levels mean"):
    st.markdown("\n".join(f"- **{lv}:** {LEVEL_MEANING[lv]}" for lv in LEVELS))

# Product table
st.subheader("Products")
picked = st.multiselect("Show levels", LEVELS, default=LEVELS)
shown = df[df["level"].isin(picked)].copy()
shown["rank"] = shown["level"].map(RANK)
shown = shown.sort_values(["rank", "product_id"], ascending=[False, True]).reset_index(drop=True)

table = shown[["product_id", "display_name", "level", "n_flags"]].rename(
    columns={"product_id": "ID", "display_name": "Product", "level": "Level", "n_flags": "List matches"}
)
styled = table.style.map(style_level, subset=["Level"])

selected_id = None
try:
    event = st.dataframe(
        styled, hide_index=True, use_container_width=True,
        on_select="rerun", selection_mode="single-row",
    )
    if event.selection.rows:
        selected_id = shown.iloc[event.selection.rows[0]]["product_id"]
    st.caption("Click a row to see its details.")
except TypeError:
    # Streamlit older than 1.35 has no row selection
    st.dataframe(styled, hide_index=True, use_container_width=True)

# Product detail
st.subheader("Product detail")
ids = df["product_id"].tolist()
labels = (df["product_id"] + ": " + df["display_name"]).tolist()
start = ids.index(selected_id) if selected_id in ids else 0
pick = st.selectbox("Pick a product", labels, index=start)
pid = pick.split(":")[0]
row = df[df["product_id"] == pid].iloc[0]
level = row["level"]

st.markdown(f"### {row['display_name']}")
box = {"HIGH": st.error, "MEDIUM": st.warning, "UNDISCLOSED": st.warning,
       "LOW": st.info}.get(level, st.error)
box(f"**{level}.** {LEVEL_MEANING.get(level, '')}")
st.markdown(f"**What to do next:** {NEXT_STEP.get(level, '')}")

if "rule" in row.index and not pd.isna(row["rule"]):
    st.caption(f"Rule applied: {row['rule']}")

if str(row["undisclosed"]) == "True":
    st.write("At least one ingredient's identity is withheld by the manufacturer.")
    if "evidence" in row.index and not pd.isna(row["evidence"]) and row["evidence"]:
        st.caption(f"Evidence: {row['evidence']}")

flags_text = row["flags_json"]
if pd.isna(flags_text) or flags_text in ("", "[]"):
    if level != "UNREADABLE":
        st.write("No list matches.")
else:
    # One block per chemical, with every list it appears on
    grouped = {}
    for flag in json.loads(flags_text):
        grouped.setdefault(flag["cas"], []).append(flag)

    st.markdown(f"**Flagged chemicals ({len(grouped)})**")
    for cas, flags in grouped.items():
        with st.container(border=True):
            meanings = ", ".join(dict.fromkeys(plain_endpoint(f["endpoint"]) for f in flags))
            st.markdown(f"**CAS {cas}**: {meanings}")
            for f in flags:
                line = f"- [{f['list_name']}]({f['source_url']})"
                if f.get("via_group"):
                    line += f", listed as *{f['via_group']}*"
                if f.get("condition"):
                    line += f". Applies only: {f['condition']}"
                st.markdown(line)
            st.caption("Official wording: " + "; ".join(dict.fromkeys(f["endpoint"] for f in flags)))

# Download
st.subheader("Download")
st.download_button(
    "Download audit (CSV)",
    data=df.drop(columns=["display_name"]).to_csv(index=False),
    file_name="sds_audit.csv",
    mime="text/csv",
)