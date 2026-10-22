import streamlit as st
import pandas as pd
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.audit import audit_one

st.set_page_config(page_title = "SDS Chemical Audit", layout="wide")
st.title("SDS Audit: First Comphrensive Review of EDCs in School Products")
st.write("Upload your school district's SDS PDFs, and the app checks every ingredient against established datasets like Prop 65, EU SVHC, and the EU endocrien disruptor lists to determine any potential health or environmental risks. ")

files = st.file_uploader("Upload SDS PDFs", type = "pdf", accept_multiple_files = True)

if "results" in st.session_state:
    st.dataframe(st.session_state["results"])

col1, col2 = st.columns(2)
with col1:
    if st.button("Run audit"):
        if files is None:
            st.warning("Upload at least one PDF first.")
            st.stop()
        bar = st.progress(0)
        rows = []
        for i, f in enumerate(files, start=1):
            result = audit_one(f, f"U{i:03d}",f.name)
            rows.append(result)
            bar.progress(i/len(files))
        st.session_state["results"] = pd.DataFrame(rows)
        st.success(f"Audited {len(files)} files")
with col2:
    if st.button("Try a sample district"):
        sample = pd.read_csv("data/results.csv")
        st.session_state["results"] = sample
        st.info (f"Showing a sample district of {len(sample)} products. ")
        
if "results" in st.session_state:
    df = st.session_state["results"]
    counts = df["level"].value_counts()
    counts.get("HIGH", 0)
    cols = st.columns(5)
    levels = ["HIGH", "MEDIUM", "UNDISCLOSED", "LOW", "UNREADABLE"]
    for c, l in zip(cols, levels):
        c.metric(l, counts.get(l,0))
    st.info("“Ingredients are checked against Prop 65, the EU SVHC list, and the EU endocrine disruptor lists. LOW means no list match, not proven safe. Chemicals not on these lists, such as some preservatives and plasticizers, are not flagged.")
    with st.expander("What the levels mean"):
            st.markdown(
            "- **HIGH:** at least one ingredient is on Prop 65, the EU SVHC list, "
            "or EU Endocrine Disruptor List I.\n"
            "- **MEDIUM:** matches only EU Endocrine Disruptor List II or III, "
            "or a listing that applies only under a condition, such as a particle size.\n"
            "- **UNDISCLOSED:** no list matches, but at least one ingredient's identity "
            "is hidden, so it cannot be checked.\n"
            "- **LOW:** no list matches and every ingredient is named. "
            "This is not proof that the product is safe.\n"
            "- **UNREADABLE:** scanned or unreadable PDF. Check this SDS by hand."
    )
    st.subheader("Summary")
    st.write(f"{len(df)} products audited.")
    st.subheader("Products")
    picked = st.multiselect("Show levels", levels, default=levels)
    shown = df[df["level"].isin(picked)]
    RANK = {"HIGH": 5, "MEDIUM":4, "UNDISCLOSED":3, "LOW":2, "UNREADABLE":1}
    shown = shown.assign(RANK=shown["level"].map(RANK))
    shown = shown.sort_values("RANK", ascending=False)
    shown["product_name"]=shown["product_name"].str.replace(r"^(Product\s*(Name|name|Description)|Trade name)\s*:?\s*", "", regex=True)
    st.dataframe(shown[["product_id", "product_name", "level", "n_flags"]],hide_index=True, use_container_width=True)

    st.subheader("Product detail")

    labels = (df["product_id"] + ": " + df["product_name"].fillna("(no name)").astype(str)).tolist()
    pick = st.selectbox("Pick a product", labels)
    pid = pick.split(":")[0]
    row = df[df["product_id"] == pid].iloc[0]
    level = row["level"]

    if level == "HIGH":
        st.error("HIGH: at least one ingredient is on Prop 65, EU SVHC, or EU ED List I.")
    elif level == "MEDIUM":
        st.warning("MEDIUM: matches only EU ED List II or III, or a conditional listing.")
    elif level == "UNDISCLOSED":
        st.warning("UNDISCLOSED: no list matches, but an ingredient's identity is hidden.")
    elif level == "LOW":
        st.info("LOW: no list matches and every ingredient is named. Not proof of safety.")
    else:
        st.error("UNREADABLE: could not read this SDS. Check it by hand.")

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
        st.markdown("**Flagged chemicals**")
        for flag in json.loads(flags_text):
            line = (f"- **CAS {flag['cas']}** on "
                    f"[{flag['list_name']}]({flag['source_url']}): {flag['endpoint']}")
            if flag.get("via_group"):
                line += f" (listed as: {flag['via_group']})"
            if flag.get("condition"):
                line += f". Applies only: {flag['condition']}"
            st.markdown(line)

    st.subheader("Download")
    st.download_button(
        "Download audit (CSV)",
        data=df.to_csv(index=False),
        file_name="sds_audit.csv",
        mime="text/csv",
    )