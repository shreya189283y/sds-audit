import csv, os, sys
from collections import Counter 

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.extract import split_sections, parse_ingredients, check_undisclosed

with open("data/manifest_draft.csv", newline="", encoding="utf-8") as f:
    manifest = list(csv.DictReader(f))

ingredient_rows = []
failure_rows = []

for row in manifest:
    try:
        pid = row["product_id"]
        path = "data/text/"+pid+".txt"
        if not os.path.exists(path):
            failure_rows.append({"product_id": pid, "reason": "scanned", "detail": "no text file"})
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        if len(text.strip())<200:
            failure_rows.append({"product_id":pid, "reason":"scanned", "detail": "under 200 characters"})
            continue
        sections = split_sections(text)
        if 3 not in sections:
            failure_rows.append({"product_id": pid, "reason":"no_section_3","detail": "No section 3 exists"})
            continue

        section3 = sections[3]
        ingredients = parse_ingredients(section3)
        flag, evidence = check_undisclosed(section3)
        if not ingredients:
            failure_rows.append({"product_id": pid, "reason":"no_cas","detail": "No CAS available"})
            continue

        for item in ingredients:
            ingredient_rows.append({
                "product_id": pid,
                "name": item.name,
                "cas": item.cas,
                "conc_min": item.conc_min,
                "conc_max": item.conc_max,
                "undisclosed": flag,
                "evidence": evidence,
                "raw_line": item.raw_line,
            })
    except Exception as e:
        failure_rows.append({"product_id": pid, "reason":"exception","detail": "Exception; "+str(e)})
        
ING_FIELDS = ["product_id", "name", "cas", "conc_min", "conc_max", "undisclosed", "evidence", "raw_line"]
FAIL_FIELDS = ["product_id", "reason", "detail"]

with open("data/ingredients.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=ING_FIELDS)
    w.writeheader()
    w.writerows(ingredient_rows)

with open("data/extract_failures.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=FAIL_FIELDS)
    w.writeheader()
    w.writerows(failure_rows)

parsed = len(manifest) - len(failure_rows)
print("Products in manifest:", len(manifest))
print("Products parsed:", parsed)
print("Failures:", len(failure_rows))
for reason, count in Counter(r["reason"] for r in failure_rows).items():
    print("   ", reason, count)
print("Ingredient rows:", len(ingredient_rows))