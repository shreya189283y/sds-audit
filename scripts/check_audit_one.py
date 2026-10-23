import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from src.audit import audit_one

PDF_FOLDER = "data/sds_pdfs"  

if not os.path.isdir(PDF_FOLDER):
    sys.exit(f"Folder {PDF_FOLDER} not found. Set PDF_FOLDER to the one run_extract.py uses.")

results = pd.read_csv("data/results.csv", dtype=str)
manifest = pd.read_csv("data/manifest_draft.csv", dtype=str).fillna("")

expected = results.set_index("product_id")["level"].to_dict()

mismatches = 0
for _, row in manifest.iterrows():
    pid = row["product_id"]
    path = os.path.join(PDF_FOLDER, row["filename"])

    if not os.path.exists(path):
        print(f"{pid}: PDF not found at {path}")
        mismatches += 1
        continue

    got = audit_one(path, pid, row["product_name"])["level"]
    want = expected.get(pid, "NOT IN RESULTS")

    if got != want:
        print(f"{pid}: audit_one says {got}, results.csv says {want}")
        mismatches += 1

print(f"\nChecked {len(manifest)} products. Mismatches: {mismatches}")