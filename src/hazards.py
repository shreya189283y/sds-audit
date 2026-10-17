import sqlite3
import os 
import pandas as pd

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(PROJECT, "data", "hazard.db")
GROUPS_FILE = os.path.join(PROJECT, "data", "cas_groups.csv")
 
PROP65_URL = "https://oehha.ca.gov/proposition-65/proposition-65-list/"
GROUPS = pd.read_csv(GROUPS_FILE, dtype=str).fillna("")

def lookup(cas):
    con = sqlite3.connect(DB)
    rows = con.execute(
    "SELECT DISTINCT list_name, endpoint, source_url FROM hazard_list WHERE cas = ?",
    (cas,),).fetchall()
    con.close()

    hits = []
    for list_name, endpoint, source_url in rows:
        
        hits.append({
            "list_name": list_name, 
            "endpoint": endpoint,
            "source_url": source_url,
            "via_group": "", 
            "condition":"", 
        })
    
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
    con = sqlite3.connect(DB)
    row = con.execute(
    "SELECT 1 FROM safer_list WHERE cas = ? LIMIT 1",
    (cas,),).fetchone()
    con.close()
    return row is not None

