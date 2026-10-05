import csv, os, re
import pdfplumber

folder = "data/sds_pdfs"
files = sorted(f for f in os.listdir(folder) if f.lower().endswith(".pdf"))

def find(pattern, text):
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1).strip() if m else ""

with open("data/manifest_draft.csv", "w", newline="", encoding="utf-8") as out:
    w = csv.writer(out)
    w.writerow(["product_id", "product_name", "manufacturer", "original_filename",
                "filename", "category", "department", "reviewed"])
    for i, f in enumerate(files, 1):
        try:
            with pdfplumber.open(os.path.join(folder, f)) as pdf:
                text = pdf.pages[0].extract_text() or ""
        except Exception:
            text = ""
        name = find(r"(?:product name|product identifier|trade name)\s*[:\-]?\s*(.+)", text)
        maker = find(r"(?:manufacturer|company name|supplier)\s*[:\-]?\s*(.+)", text)
        w.writerow([f"P{i:03d}", name, maker, f, f"P{i:03d}.pdf", "", "", ""])

print(len(files), "files written to data/manifest_draft.csv")