import pandas as pd, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.audit import audit_one

manifest = pd.read_csv("data/manifest_draft.csv", dtype=str).fillna("")
PDF_FOLDER = "data/sds_pdfs"

results = []
for _, row in manifest.iterrows():
    path = os.path.join(PDF_FOLDER, row["filename"])
    result = audit_one(path, row["product_id"], row["product_name"])
    result["category"] = row["category"]
    results.append(result)

out = pd.DataFrame(results)
out.to_csv("data/results.csv", index=False)

print()
print("Results rows:", len(out))
print(out["level"].value_counts())
print("Saved to data/results.csv")