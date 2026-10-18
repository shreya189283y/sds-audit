import sqlite3
import os
import pandas as pd

# Build paths from this file's location, so they work from any folder
PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(PROJECT, "data", "hazard.db")
GROUPS_FILE = os.path.join(PROJECT, "data", "cas_groups.csv")

PROP65_URL = "https://oehha.ca.gov/proposition-65/proposition-65-list/"

# Prop 65 listings that apply only to one route or form. The condition is
# written in the chemical's name on the list, e.g. "Ethylene glycol (ingested)".
CONDITION_WORDS = ["(ingested)", "airborne", "respirable"]

# Read the group mapping once, when this file is imported
GROUPS = pd.read_csv(GROUPS_FILE, dtype=str).fillna("")


def lookup(cas):
    """Return every hazard list this CAS number is on, directly or through a group."""
    con = sqlite3.connect(DB)
    rows = con.execute(
        "SELECT DISTINCT chemical_name, list_name, endpoint, source_url FROM hazard_list WHERE cas = ?",
        (cas,),
    ).fetchall()
    con.close()

    hits = []
    seen = []
    for chemical_name, list_name, endpoint, source_url in rows:
        condition = ""
        if list_name == "Prop 65":
            for word in CONDITION_WORDS:
                if word in chemical_name.lower():
                    condition = chemical_name

        # The same chemical can appear under several names on one list.
        # Keep one hit per list, endpoint and condition.
        key = (list_name, endpoint, condition)
        if key in seen:
            continue
        seen.append(key)

        hits.append({
            "list_name": list_name,
            "endpoint": endpoint,
            "source_url": source_url,
            "via_group": "",
            "condition": condition,
        })

    # Group entries that have no CAS on the list itself
    matches = GROUPS[GROUPS["member_cas"] == cas]
    for _, group in matches.iterrows():
        hits.append({
            "list_name": group["list_name"],
            "endpoint": group["endpoint"],
            "source_url": PROP65_URL,
            "via_group": group["group_name"],
            "condition": group["condition"],
        })

    return hits


def is_safer(cas):
    """Return True if this CAS number is on EPA's Safer Chemical Ingredients List."""
    con = sqlite3.connect(DB)
    row = con.execute(
        "SELECT 1 FROM safer_list WHERE cas = ? LIMIT 1",
        (cas,),
    ).fetchone()
    con.close()
    return row is not None