import pdfplumber
import re 
from src.cas import find_cas

def read_pdf(path):
    #Return all the text in a PDF as one string.
    with pdfplumber.open(path) as pdf:
        return "\n".join(p.extract_text() or "" for p in pdf.pages)


def is_scanned(text):
    #True if the PDF gave back too little text to be a real SDS.
    return len(text.strip()) < 200

# split_sections(text) -> dict[int, str]. 
# Regex must handle 'SECTION 3', 'Section 3:', '3. 
# Composition/Information on Ingredients', and all-caps variants. 
# Section 3 ends where Section 4 (First Aid) begins.

NUMBER = r"(?:\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten)"

TITLES = {1: "identification", 2: r"hazards?(?!ous)",
          3: r"(?:composition|ingredients|hazardous\s+(?:ingredients|components))",
          4: "first", 5: "fire", 6: "accidental", 7: "handling", 8: "exposure",
          9: "physical", 10: "stability", 11: "toxicolog", 12: "ecolog",
          13: "disposal", 14: "transport", 15: "regulatory", 16: "other"}

def split_sections(text):
    starts = []
    for num, word in TITLES.items():
        pattern = rf"^\s*(?:section\s*)?{NUMBER}\s*[.:\-–]?\s*{word}"
        m = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if m:
            starts.append((m.start(), num))
    starts.sort()

    sections = {}
    for i, (pos, num) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
        sections[num] = text[pos:end]
    return sections

from dataclasses import dataclass
from typing import Optional

@dataclass
class Ingredient:
    name: str
    cas: Optional[str]
    conc_min: Optional[float]
    conc_max: Optional[float]
    raw_line: str

NUM = r"(\d+(?:\.\d+)?)"
RANGE = (r"(?<![\d.\-/])(?:[<>]=?\s*)?" + NUM
         + r"\s*%?\s*(?:-|–|—|to)\s*(?:[<>]=?\s*)?" + NUM
         + r"(?!\d|\.\d|\s*[-/]\s*\d)")

# Structure of Section 3 = includes the chemical name, CAS number, and weight % and some form of hazadorous status (usually)
def parse_concentration(text):
    #1 - Range: 1-5%, 1 - 5, of 1 to 5 are all options
    m = re.search(RANGE, text)
    if m:
        low,high = float(m.group(1)), float(m.group(2))
        if low <= 100 and high <= 100:
            return low, high
        return None, None
    
    m = re.search(r"([<>]=?)\s*"+NUM, text)
    if m:
        symbol, value = m.group(1), float(m.group(2))
        if value <= 100:
            if symbol.startswith("<"):
                return 0.0, value
            return value, 100.0
        return None, None
    m=re.search(NUM, text)
    if m:
        value = float(m.group(1))
        if value <= 100:
            return value, value
        
    return None,None

def find_range(text):
    return re.search(RANGE + r"|[<>]=?\s*" + NUM, text)
def parse_ingredients(section3):
    results = []
    stripped_list = []
    lines = section3.splitlines()
    for i in lines:
        if i == "":
            continue
        else:
            stripped_i = i.strip()
            stripped_list.append(stripped_i)
    for k in stripped_list:
        valid, invalid = find_cas(k)
        if valid:
            cas = valid[0]
            name = k.split(cas)[0].strip()
            conc_min, conc_max = parse_concentration(k.split(cas)[1])
            item = Ingredient(name = name, cas = cas, conc_min = conc_min, conc_max = conc_max, raw_line = k)
            results.append(item)
        elif invalid:
            print ("Warning, an invalid CAS has been found: ", invalid, "in line:", k)
            bad = invalid[0]
            name = k.split(bad)[0].strip()
            conc_min, conc_max = parse_concentration(k.split(bad)[1])
            item = Ingredient(name = name, cas =  None, conc_min = conc_min, conc_max = conc_max, raw_line = k)
            results.append(item)

        elif "proprietary" in k.lower() or "trade secret" in k.lower():
            conc_min, conc_max = parse_concentration(k)
            if conc_min is not None:
                item = Ingredient(name = k, cas = None, conc_min = conc_min, conc_max = conc_max, raw_line = k)
                results.append(item)

        else:
            m= find_range(k)
            if m:
                name = k[:m.start()].strip()
                conc_min, conc_max = parse_concentration(k[m.start():])
                if name and conc_min is not None:
                    item = Ingredient(name = name, cas = None, conc_min = conc_min, conc_max = conc_max, raw_line = k)
                    results.append(item)
    return results 

def check_undisclosed(section3):
    keywords = ["trade secret", "proprietary", "confidential", "withheld"]
    text = section3.lower()
    for key in keywords:
        if key in text:
            return True, key
    if re.search(r"\bcbi\b", text):
        return True, "cbi"
    valid, invalid = find_cas(section3)
    if not valid:
        return True, "no valid CAS numbers"
    results = parse_ingredients(section3)
    missing = []
    for r in results:
        if r.cas is None:
            missing.append(r.name)
    if missing:
        return True, "no CAS for: " + "; ".join(missing)
    return False, ""

