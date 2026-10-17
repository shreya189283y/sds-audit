import sys, os 
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
 
import pandas as pd
from src.hazards import lookup

ingredients = pd.read_csv("data/ingredients.csv", dtype=str)
ingredients = ingredients[ingredients["cas"].notna() & (ingredients["cas"] != "")]

summary = ingredients.groupby("cas").agg(
    name=("name", "first"),
    n_products=("product_id", "nunique"),
).reset_index()
 
summary["n_hits"] = summary["cas"].apply(lambda cas: len(lookup(cas)))
unmatched = summary[summary["n_hits"] == 0].sort_values("n_products", ascending=False)
 
print("Unique CAS in your products:", len(summary))
print("Matched at least one list:  ", (summary["n_hits"] > 0).sum())
print("Matched nothing:            ", len(unmatched))
print()
for _, row in unmatched.iterrows():
    print(f'{row["cas"]:14} {row["n_products"]:>3} products   {row["name"]}')
 
unmatched[["cas", "name", "n_products"]].to_csv("data/unmatched_cas.csv", index=False)
print("\nSaved to data/unmatched_cas.csv")