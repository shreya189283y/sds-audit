# split_sections(text) -> dict[int, str]. 
# Regex must handle 'SECTION 3', 'Section 3:', '3. 
# Composition/Information on Ingredients', and all-caps variants. 
# Section 3 ends where Section 4 (First Aid) begins.

import re

TITLES = {1: "identification", 2: "hazard", 3: "composition", 4: "first",
          5: "fire", 6: "accidental", 7: "handling", 8: "exposure",
          9: "physical", 10: "stability", 11: "toxicolog", 12: "ecolog",
          13: "disposal", 14: "transport", 15: "regulatory", 16: "other"}

def split_sections(text):
    starts = []
    for num, word in TITLES.items():
        pattern = rf"^\s*(?:section\s*)?{num}\s*[.:\-]?\s*{word}"
        m = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if m:
            starts.append((m.start(), num))
    starts.sort()

    sections = {}
    for i, (pos, num) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(text)
        sections[num] = text[pos:end]
    return sections