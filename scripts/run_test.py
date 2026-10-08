import csv
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import csv
from src.extract import read_pdf, is_scanned
from src.extract import read_pdf, is_scanned

MANIFEST = "/Users/shreya/Documents/sds-audit/data/manifest_draft.csv"
PDF_FOLDER = "/Users/shreya/Documents/sds-audit/data/sds_pdfs"
TEXT_FOLDER = "data/text"
SCANNED = "data/scanned.csv"


def read_manifest():
    with open(MANIFEST, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def save(path, rows, fields):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main():
    os.makedirs(TEXT_FOLDER, exist_ok=True)
    scanned = []
    written = 0

    for row in read_manifest():
        pid = row["product_id"]
        path = os.path.join(PDF_FOLDER, row["filename"])
        try:
            text = read_pdf(path)
        except Exception as e:
            scanned.append({"product_id": pid, "chars": 0, "reason": str(e)})
            print("FAILED:", pid, e)
            continue

        if is_scanned(text):
            scanned.append({"product_id": pid, "chars": len(text.strip()), "reason": "too little text"})

        out_path = os.path.join(TEXT_FOLDER, pid + ".txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
        written += 1

    save(SCANNED, scanned, ["product_id", "chars", "reason"])
    print(written, "text files written,", len(scanned), "flagged as scanned or failed")


if __name__ == "__main__":
    main()