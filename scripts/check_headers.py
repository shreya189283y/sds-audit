import csv

with open("data/extract_failures.csv", encoding="utf-8") as f:
    fails = [r for r in csv.DictReader(f) if r["reason"] == "no_section_3"]

for r in fails:
    pid = r["product_id"]
    with open("data/text/" + pid + ".txt", encoding="utf-8") as f:
        text = f.read()
    print("=====", pid, "| characters:", len(text))
    hits = [line for line in text.splitlines()
            if "composition" in line.lower() or "ingredient" in line.lower()]
    for line in hits[:6]:
        print("   ", repr(line))
    if not hits:
        print("    (no line mentions composition or ingredient)")