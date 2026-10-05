import csv, sys
import pdfplumber

pid = sys.argv[1].upper()
path = "data/manifest.csv"
try:
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8-sig")))
except FileNotFoundError:
    path = "data/manifest_draft.csv"
    rows = list(csv.DictReader(open(path, newline="", encoding="utf-8-sig")))

row = next((r for r in rows if r["product_id"] == pid), None)
print("CSV says:", row["product_name"] if row else "no row for " + pid, "| from", path)
with pdfplumber.open(f"data/sds_pdfs/{pid}.pdf") as pdf:
    text = pdf.pages[0].extract_text() or "(no readable text, likely a scan)"
print("PDF says:\n" + "\n".join(text.splitlines()[:12]))