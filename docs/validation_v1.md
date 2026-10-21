# Validation report

Generated 2026-10-21 from `data/lists/raw/ground_truth_clean.csv` and `data/results.csv`.
Scoring rules frozen at tag `rules-v1`. All figures are counts.
Counted as agreement besides exact matches: [('NONE', 'LOW')].

## Coverage

Products in ground truth: 35
Products found in tool output: 35
Missing from tool output: none

## Product level

Rows are the manual level. Columns are the tool level.

| manual \ tool | HIGH | MEDIUM | UNDISCLOSED | LOW | UNREADABLE |
|---|---|---|---|---|---|
| HIGH | 6 | 1 | 9 | 0 | 0 |
| MEDIUM | 3 | 1 | 1 | 5 | 0 |
| LOW | 1 | 0 | 2 | 5 | 0 |
| NONE | 0 | 0 | 1 | 0 | 0 |

Agreement: 12 of 35 products.

### Product disagreements

| product_id | product_name | manual | tool | label | explanation |
|---|---|---|---|---|---|
| P005 | Product name 24-5-11 TurfGro 50% XCU, 2% Fe, w WT Fe | HIGH | MEDIUM |  |  |
| P015 | BEST Dimension 270G | MEDIUM | UNDISCLOSED |  |  |
| P017 | Product Name: BIORENEWABLES GLASS CLEANER | HIGH | UNDISCLOSED |  |  |
| P018 | BOND COAT | MEDIUM | LOW |  |  |
| P029 | Product Name: CLEAN ON THE GO BIORENEWABLES GLASS CLEANER [18] | HIGH | UNDISCLOSED |  |  |
| P042 | Dura Seal Concrete Sealer | MEDIUM | LOW |  |  |
| P047 | EcoPCO AR-X Multi-Purpose Insecticide | MEDIUM | LOW |  |  |
| P054 | FINAL COAT | HIGH | UNDISCLOSED |  |  |
| P058 | Product Name: GREEN SOLUTIONS INDUSTRIAL CLEANER | HIGH | UNDISCLOSED |  |  |
| P076 | Product Name: MILLENNIA BRIGHT DURA PRIME | HIGH | UNDISCLOSED |  |  |
| P078 | EPA Reg. No.: 228-570 | LOW | UNDISCLOSED |  |  |
| P079 | Product Name: ON BASE | HIGH | UNDISCLOSED |  |  |
| P082 | Polaris® Herbicide | LOW | UNDISCLOSED |  |  |
| P086 | Product Name Quali-Pro Oxadiazon 2G | LOW | HIGH |  |  |
| P087 | Ranger PRO® Herbicide | MEDIUM | HIGH |  |  |
| P089 | Roundup PROMAX® Herbicide | MEDIUM | HIGH |  |  |
| P091 | Product Name: SHINELINE SEAL | HIGH | UNDISCLOSED |  |  |
| P099 | SPEED GLOSS | MEDIUM | LOW |  |  |
| P106 | Product Description: Surflan AS AG | MEDIUM | HIGH |  |  |
| P108 | Product Name: TERRA GLAZE | HIGH | UNDISCLOSED |  |  |
| P111 | TRAPPER® RAT GLUE, MOUSE GLUE, BULK GLUE, PRO PACK | NONE | UNDISCLOSED |  |  |
| P112 | Product Name: TRIBASE MULTI PURPOSE CLEANER | HIGH | UNDISCLOSED |  |  |
| P114 | TURFLON™ Ester Issue Date: 05/04/2015 | MEDIUM | LOW |  |  |

## Chemical level

Found by both: 10
Manual only (tool missed): 37
Tool only (not in manual review): 2

### Manual only

| product_id | cas | chemical_name | label | explanation |
|---|---|---|---|---|
| P003 | 121-44-8 | Triethylamine |  |  |
| P005 | 77536-68-6 | trace prismatic tremolite |  |  |
| P015 | 97886-45-8 | Dithiopyr |  |  |
| P017 | 26172-55-4 | MCI |  |  |
| P017 | 2682-20-4 | MIT |  |  |
| P018 | 111-90-0 | Diethylene Glycol Monoethyl Ether |  |  |
| P018 | 78-51-3 | Tributoxyethyl Phosphate |  |  |
| P029 | 26172-55-4 | MCI |  |  |
| P029 | 2682-20-4 | MIT |  |  |
| P042 | 770-35-4 | Propylene Glycol Phenyl Ether |  |  |
| P047 | 8003-34-7 | Natural pyrethrins |  |  |
| P052 | 78-51-3 | tris |  |  |
| P054 | 822-06-0 | Hexamethylene-1,6-Diisocyanate / HDI |  |  |
| P058 | 26172-55-4 | MCI |  |  |
| P058 | 2682-20-4 | MIT |  |  |
| P069 | 7440-38-2 | Arsenic |  |  |
| P076 | 26172-55-4 | MCI |  |  |
| P076 | 2682-20-4 | MIT |  |  |
| P079 | 26172-55-4 | Methylchloroisothiazolinone/Methylisothiazolinone |  |  |
| P079 | 2682-20-4 | Methylchloroisothiazolinone/Methylisothiazolinone |  |  |
| P079 | 78-51-3 | Tributoxyethyl Phosphate / TBEP |  |  |
| P087 | 1071-83-6 | Glyphosate |  |  |
| P091 | 26172-55-4 | Methylchloroisothiazolinone/Methylisothiazolinone |  |  |
| P091 | 2682-20-4 | Methylchloroisothiazolinone/Methylisothiazolinone |  |  |
| P091 | 78-51-3 | Tributoxyethyl Phosphate / TBEP |  |  |
| P099 | 111-90-0 | Diethylene Glycol Monoethyl Ether / Ethoxydiglycol |  |  |
| P099 | 78-51-3 | Tributoxyethyl Phosphate |  |  |
| P103 | 112-34-5 | Diethylene Glycol Monobutyl Ether |  |  |
| P103 | 78-51-3 | Tributoxyethyl Phosphate |  |  |
| P108 | 26172-55-4 | Methylchloroisothiazolinone/Methylisothiazolinone |  |  |
| P108 | 2682-20-4 | Methylchloroisothiazolinone/Methylisothiazolinone |  |  |
| P108 | 78-51-3 | Tributoxyethyl Phosphate / TBEP |  |  |
| P109 | 111-76-2 | 2-Butoxyethanol |  |  |
| P112 | 26172-55-4 | Methylchloroisothiazolinone / MCI |  |  |
| P112 | 2682-20-4 | Methylisothiazolinone / MIT |  |  |
| P114 | 111-76-2 | Ethylene glycol monobutyl ether |  |  |
| P114 | 64700-56-7 | Triclopyr |  |  |

### Tool only

| product_id | cas | chemical_name | label | explanation |
|---|---|---|---|---|
| P086 | 19666-30-9 |  |  |  |
| P087 | 38641-94-0 |  |  |  |

## Manual rows not compared

Flagged by hand but no valid CAS, so they cannot be matched by CAS.

| product_id | cas | chemical_name | concern_level |
|---|---|---|---|
| P054 |  | Aliphatic Polyisocyanate based on HDI | HIGH |
