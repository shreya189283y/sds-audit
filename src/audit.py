import json, sys, os, re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.extract import read_pdf, is_scanned, split_sections, parse_ingredients, check_undisclosed
from src.score import score
OCR_PAGES = 4   
OCR_DPI = 200   
 
_engine = None
 
 
def _ocr_engine():
    global _engine
    if _engine is None:
        from rapidocr_onnxruntime import RapidOCR
        _engine = RapidOCR()
    return _engine
 
 
def _boxes_to_lines(result):
    result = sorted(result, key=lambda r: (round(r[0][0][1] / 12), r[0][0][0]))
    lines, current, last_y = [], [], None
    for box, text, _conf in result:
        y = round(box[0][1] / 12)
        if last_y is not None and y != last_y:
            lines.append(" ".join(current))
            current = []
        current.append(text)
        last_y = y
    if current:
        lines.append(" ".join(current))
    return "\n".join(lines)
 
 
def ocr_pdf(pdf_file):
    try:
        import pymupdf
        engine = _ocr_engine()
    except ImportError:
        return ""
 
    try:
        if isinstance(pdf_file, str):
            doc = pymupdf.open(pdf_file)
        else:
            doc = pymupdf.open(stream=pdf_file.getvalue(), filetype="pdf")
        pages = []
        for i, page in enumerate(doc):
            if i >= OCR_PAGES:
                break
            image = page.get_pixmap(dpi=OCR_DPI).tobytes("png")
            result, _ = engine(image)
            if result:
                pages.append(_boxes_to_lines(result))
        return "\n".join(pages)
    except Exception:
        return ""
 
 
def clean_ocr(text):
    return re.sub(r"^[\W_]+(?=\w)", "", text, flags=re.MULTILINE)
 
 
def find_section3_ocr(text):
    start = re.search(r"^.{0,12}\b(composition|composici)", text, re.IGNORECASE | re.MULTILINE)
    if not start:
        return None
    rest = text[start.end():]
    end = re.search(r"^.{0,12}(first[\s-]*aid|primeros\s+auxilios)", rest, re.IGNORECASE | re.MULTILINE)
    return text[start.start(): start.end() + (end.start() if end else 3000)]
 
 
def unreadable(product_id, product_name, reason, ocr):
    return {
        "product_id": product_id,
        "product_name": product_name,
        "level": "UNREADABLE",
        "n_flags": 0,
        "undisclosed": False,
        "flags_json": json.dumps([]),
        "rule": reason,
        "evidence": "",
        "ocr": ocr,
    }
 
 
def audit_one(pdf_file, product_id, product_name):
    text = read_pdf(pdf_file)
    ocr = False
 
    if is_scanned(text):
        text = clean_ocr(ocr_pdf(pdf_file))
        ocr = True
        if is_scanned(text):
            return unreadable(product_id, product_name,
                              "Scanned PDF that OCR could not read. Review it by hand.", ocr)
 
    section3 = split_sections(text).get(3)
    if section3 is None and ocr:
        section3 = find_section3_ocr(text)
    if section3 is None:
        low = text.lower()
        if "safety data sheet" in low or "msds" in low:
            reason = "SDS found, but its ingredient section is in a format the tool cannot read."
        else:
            reason = ("This file does not look like an SDS. It may be a product label. "
                      "Upload the product's SDS instead.")
        return unreadable(product_id, product_name, reason, ocr)
 
    rows = parse_ingredients(section3)
    undisclosed, evidence = check_undisclosed(section3)
    cas_list = [r.cas for r in rows if r.cas is not None]
 
    result = score(cas_list, undisclosed)
 
    rule = result["rule"]
    if evidence == "no valid CAS numbers":
        rule = ("The SDS lists no ingredients with CAS numbers, so nothing could be checked. "
                "This is often legal when no ingredient is classified as hazardous.")
 
    return {
        "product_id": product_id,
        "product_name": product_name,
        "level": result["level"],
        "n_flags": len(result["flags"]),
        "undisclosed": undisclosed,
        "flags_json": json.dumps(result["flags"]),
        "rule": rule,
        "evidence": evidence,
        "ocr": ocr,
    }