import sys
import pdfplumber

with pdfplumber.open(sys.argv[1]) as pdf:
    text = pdf.pages[0].extract_text() or "(no readable text, likely a scan)"
print(text[:800])