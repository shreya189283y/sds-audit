import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.audit import audit_one
print(audit_one("data/sds_pdfs/P069.pdf", "P069", "Lead Acid Battery"))
