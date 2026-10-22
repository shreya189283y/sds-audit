import streamlit as st
import pandas as pd
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.audit import audit_one

st.set_page_config(page_title = "SDS Chemical Audit", layout="wide")
st.title("SDS Audit: First Comphrensive Review of EDCs in School Products")
st.write("Upload your school district's SDS PDFs, and the app checks every ingredient against established datasets like Prop 65, EU SVHC, and the EU endocrien disruptor lists to determine any potential health or environmental risks. ")

files = st.file_uploader("Upload SDS PDFs", type = "pdf", accept_multiple_files = True)
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
if "results" in st.session_state:
    st.dataframe(st.session_state["results"])
    