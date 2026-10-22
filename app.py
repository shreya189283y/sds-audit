import streamlit as st
import pandas as pd
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.audit import audit_one

st.set_page_config(page_title = "SDS Chemical Audit", layout="wide")
st.title("SDS Audit: First Comphrensive Review of EDCs in School Products")
st.write("Upload your school district's SDS PDFs, and the app checks every ingredient against established datasets like Prop 65, EU SVHC, and the EU endocrien disruptor lists to determine any potential health or environmental risks. ")
