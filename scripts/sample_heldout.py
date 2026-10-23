import random
import sys
from pathlib import Path

import pandas as pd

MANIFEST = "data/manifest_draft.csv"
AUDITED = "data/lists/raw/ground_truth_clean.csv"
OUT = "docs/heldout_manual.csv"
EXCLUDE = {"P012"}  # duplicate Ranger Pro sheet
SEED = 42
N_DRAW = 15 


def main():
    if Path(OUT).exists():
        sys.exit(f"{OUT} already exists. The sample is drawn once. Do not redraw.")

    ids = pd.read_csv(MANIFEST, dtype=str)["product_id"].str.strip().str.upper()
    audited = set(pd.read_csv(AUDITED, dtype=str)["product_id"].str.strip().str.upper())
    pool = sorted(set(ids) - audited - EXCLUDE)

    random.seed(SEED)
    order = random.sample(pool, N_DRAW)

    print(f"Pool: {len(pool)} unreviewed products. Seed {SEED}.\n")
    print("Review in this order. Keep the first 10 that are NOT one of the 4")
    print("unmatched audit products (Quali-Pro Dithiopyr 2 L, PT Phantom II,")
    print("EcoEXEMPT D, EcoEXEMPT IC2). Skip those and take the next one.\n")
    for i, pid in enumerate(order, 1):
        print(f"{i:2}. {pid}")

    rows = [{"product_id": pid, "cas": "", "chemical_name": "", "concern_level": "",
             "notes": ""} for pid in order]
    Path(OUT).parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"\nBlank answer sheet: {OUT}")


if __name__ == "__main__":
    main()