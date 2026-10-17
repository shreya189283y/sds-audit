import pandas as pd, json, subprocess, sys
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.score import score

subprocess.run([sys.executable, "scripts/run_extract.py"], check=True)
manifest = pd.read_csv("data/manifest_draft.csv", dtype=str).fillna("")
ingredients = pd.read_csv("data/ingredients.csv", dtype=str)
failures = pd.read_csv("data/extract_failures.csv", dtype = str)

unreadable_rows = failures[failures["reason"].isin(["scanned", "no_section_3"])]
unreadable = unreadable_rows["product_id"].tolist()

undisclosed_rows = ingredients[ingredients["undisclosed"]== 'True']
undisclosed_ids = undisclosed_rows["product_id"].unique().tolist()
print("Undisclosed products:", len(undisclosed_ids))

results = []
for _, row in manifest.iterrows():
    pid = row["product_id"]
    if pid in unreadable:
        level = "UNREADABLE"
        flags = []
        undisclosed = False
    else:
        product_rows = ingredients[ingredients["product_id"]==pid]
        cas_list = product_rows["cas"].dropna().tolist()
        undisclosed = pid in undisclosed_ids
        result = score(cas_list, undisclosed)
        level = result["level"]
        flags = result["flags"]

    results.append({
        "product_id": pid,
        "product_name": row["product_name"],
        "category": row["category"],
        "level": level,
        "n_flags": len(flags),
        "undisclosed": undisclosed,
        "flags_json": json.dumps(flags),
    })

out = pd.DataFrame(results)
out.to_csv("data/results.csv", index=False)

print()
print("Results rows:", len(out))
print(out["level"].value_counts())
print("Saved to data/results.csv")