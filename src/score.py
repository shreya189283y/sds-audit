import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.hazards import lookup
STRONG_LISTS = ["Prop 65", "EU SVHC", "EU ED List I"]

def score (cas_list, undisclosed):
    all_hits = []
    for cas in cas_list:
        for hit in lookup(cas):
            hit["cas"]=cas
            all_hits.append(hit)

    strong = []
    weak = []
    conditional = []

    for hit in all_hits:
        if hit["condition"] != "":
            conditional.append(hit)
        elif hit["list_name"] in STRONG_LISTS:
            strong.append(hit)
        else:
            weak.append(hit)

    if strong:
        level = "HIGH"
        rule = "At least one ingredient is on Prop 65, EU SVHC, or EU ED LIST I."
    elif weak or conditional:
        level = "MEDIUM"
        rule = "Matches only on EU ED List II or III, or only conditional matches."
    elif undisclosed:
        level = "UNDISCLOSED"
        rule = "No list matches, but part of the formula is withheld."
    else:
        level = "LOW"
        rule = "No list matches, and the formula is fully disclosed"

    return {
        "level": level, 
        "rule": rule, 
        "flags": all_hits, 
        "undisclosed": undisclosed,
    }
    
