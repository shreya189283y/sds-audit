import csv, os

folder = "data/sds_pdfs"
manifest = "data/manifest.csv" if os.path.exists("data/manifest.csv") else "data/manifest_draft.csv"
rows = list(csv.DictReader(open(manifest, newline="", encoding="utf-8-sig")))

renamed, missing = 0, 0
for r in rows:
    old = os.path.join(folder, r["original_filename"])
    new = os.path.join(folder, r["filename"])
    if os.path.exists(old):
        os.rename(old, new)
        renamed += 1
    elif not os.path.exists(new):
        print("MISSING:", r["product_id"], r["original_filename"])
        missing += 1

print("Used", manifest)
print(len(rows), "rows,", renamed, "renamed,", missing, "missing")