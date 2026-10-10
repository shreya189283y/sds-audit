import csv
import random

DEV = {"P001", "P024", "P037", "P053", "P0116"}  

with open("data/ingredients.csv", encoding="utf-8") as f:
    ids = sorted({r["product_id"] for r in csv.DictReader(f)} - DEV)

random.seed(1)
print(random.sample(ids, 10))