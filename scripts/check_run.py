import csv
from collections import Counter

with open("data/ingredients.csv", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
with open("data/extract_failures.csv", encoding="utf-8") as f:
    fails = list(csv.DictReader(f))

per_product = Counter(r["product_id"] for r in rows)
print("Top 10 by row count:", per_product.most_common(10))
print("P001 rows:", per_product["P001"], " P104 rows:", per_product["P104"])
print("Rows with a CAS:", sum(1 for r in rows if r["cas"] != ""))
print("Rows without a CAS:", sum(1 for r in rows if r["cas"] == ""))
print("Products with 15 or fewer rows:", sum(1 for n in per_product.values() if n <= 15))
print("Failure details:", Counter(r["detail"] for r in fails))