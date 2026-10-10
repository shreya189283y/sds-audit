import sys
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from src.extract import split_sections, parse_ingredients, check_undisclosed

product_id = sys.argv[1]
path = "data/text/" + product_id + ".txt"

with open(path, encoding="utf-8") as f:
    text = f.read()

sections = split_sections(text)
if 3 not in sections:
    print("No Section 3 found for ", product_id)
    sys.exit()

section3 = sections[3]
results = parse_ingredients(section3)

for item in results:
    print(item)

results = check_undisclosed(section3)
print(results)