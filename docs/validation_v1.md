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
| P005 | Product name 24-5-11 TurfGro 50% XCU, 2% Fe, w WT Fe | HIGH | MEDIUM | manual judgment | Tool matched silica but scored MEDIUM; manual rated HIGH on silica plus tremolite. CHECK why silica scored MEDIUM. |
| P015 | BEST Dimension 270G | MEDIUM | UNDISCLOSED | list gap | Dithiopyr is on none of the four lists; tool flags Biodac with no CAS. Manual marked this DISPUTED. |
| P017 | Product Name: BIORENEWABLES GLASS CLEANER | HIGH | UNDISCLOSED | list gap | MIT/MCI drive the manual HIGH; neither is on any of the four lists. Tool flags a hidden fragrance or colorant. |
| P018 | BOND COAT | MEDIUM | LOW | list gap | TBEP and ethoxydiglycol are on none of the four lists. |
| P029 | Product Name: CLEAN ON THE GO BIORENEWABLES GLASS CLEANER [18] | HIGH | UNDISCLOSED | list gap | MIT/MCI not on any list. Tool flags a hidden fragrance or colorant. |
| P042 | Dura Seal Concrete Sealer | MEDIUM | LOW | manual judgment | Manual concern is acute toxicity; manual notes no carcinogen or EDC listing applies. |
| P047 | EcoPCO AR-X Multi-Purpose Insecticide | MEDIUM | LOW | manual judgment | Manual marked pyrethrins DISPUTED; not on any list. |
| P054 | FINAL COAT | HIGH | UNDISCLOSED | list gap | HDI is a respiratory sensitizer and is on none of the four lists. Tool flags the trade secret polyisocyanate. |
| P058 | Product Name: GREEN SOLUTIONS INDUSTRIAL CLEANER | HIGH | UNDISCLOSED | list gap | MIT/MCI not on any list. Tool flags a hidden ingredient. |
| P076 | Product Name: MILLENNIA BRIGHT DURA PRIME | HIGH | UNDISCLOSED | list gap | MIT/MCI not on any list. Tool flags the proprietary fluorosurfactant. |
| P078 | EPA Reg. No.: 228-570 | LOW | UNDISCLOSED | no manual equivalent | Tool flags a withheld ingredient identity. The manual review had no UNDISCLOSED level. |
| P079 | Product Name: ON BASE | HIGH | UNDISCLOSED | list gap | MIT/MCI and TBEP not on any list. Tool flags the proprietary fluorosurfactant. |
| P082 | Polaris® Herbicide | LOW | UNDISCLOSED | no manual equivalent | Manual noted Other Ingredients withheld as trade secret but had no UNDISCLOSED level. |
| P086 | Product Name Quali-Pro Oxadiazon 2G | LOW | HIGH | manual judgment | Oxadiazon is Prop 65 listed. Manual rated LOW because the review focused on endocrine disruption. |
| P087 | Ranger PRO® Herbicide | MEDIUM | HIGH | manual judgment | Glyphosate salt matches Prop 65 via group mapping. Manual rated MEDIUM as scientifically disputed. |
| P089 | Roundup PROMAX® Herbicide | MEDIUM | HIGH | manual judgment | Glyphosate salt matches Prop 65 via group mapping. Manual rated MEDIUM as scientifically disputed. |
| P091 | Product Name: SHINELINE SEAL | HIGH | UNDISCLOSED | list gap | MIT/MCI and TBEP not on any list. Tool flags the proprietary fluorosurfactant. |
| P099 | SPEED GLOSS | MEDIUM | LOW | list gap | TBEP and ethoxydiglycol are on none of the four lists. |
| P106 | Product Description: Surflan AS AG | MEDIUM | HIGH | manual judgment | Oryzalin is a Prop 65 carcinogen. Manual rated MEDIUM because the review focused on endocrine disruption. |
| P108 | Product Name: TERRA GLAZE | HIGH | UNDISCLOSED | list gap | MIT/MCI and TBEP not on any list. Tool flags the proprietary fluorosurfactant. |
| P111 | TRAPPER® RAT GLUE, MOUSE GLUE, BULK GLUE, PRO PACK | NONE | UNDISCLOSED | no manual equivalent | SDS lists 100% proprietary ingredients. Tool flags the hidden identity; manual cleared it as non-hazardous. |
| P112 | Product Name: TRIBASE MULTI PURPOSE CLEANER | HIGH | UNDISCLOSED | list gap | MIT/MCI not on any list. Tool flags a hidden fragrance. |
| P114 | TURFLON™ Ester Issue Date: 05/04/2015 | MEDIUM | LOW | manual judgment | Manual marked triclopyr DISPUTED; 2-butoxyethanol concern is ACGIH A3 which is not one of the four lists. |

## Chemical level

Found by both: 10
Manual only (tool missed): 37
Tool only (not in manual review): 2

### Manual only

| product_id | cas | chemical_name | label | explanation |
|---|---|---|---|---|
| P003 | 121-44-8 | Triethylamine | list gap | Triethylamine is on none of the four lists. |
| P005 | 77536-68-6 | trace prismatic tremolite | group mapping gap | Tremolite asbestos is covered by the asbestos group listing. CHECK whether the SDS gives this CAS and whether cas_groups.csv covers asbestos. |
| P015 | 97886-45-8 | Dithiopyr | list gap | Dithiopyr is on none of the four lists. |
| P017 | 26172-55-4 | MCI | list gap | MCI is on none of the four lists. |
| P017 | 2682-20-4 | MIT | list gap | MIT is on none of the four lists. |
| P018 | 111-90-0 | Diethylene Glycol Monoethyl Ether | list gap | Ethoxydiglycol is on none of the four lists. |
| P018 | 78-51-3 | Tributoxyethyl Phosphate | list gap | TBEP is on none of the four lists. |
| P029 | 26172-55-4 | MCI | list gap | MCI is on none of the four lists. |
| P029 | 2682-20-4 | MIT | list gap | MIT is on none of the four lists. |
| P042 | 770-35-4 | Propylene Glycol Phenyl Ether | list gap | Propylene glycol phenyl ether is on none of the four lists. |
| P047 | 8003-34-7 | Natural pyrethrins | list gap | Natural pyrethrins are on none of the four lists. |
| P052 | 78-51-3 | tris | list gap | TBEP is on none of the four lists. |
| P054 | 822-06-0 | Hexamethylene-1,6-Diisocyanate / HDI | list gap | HDI is on none of the four lists. |
| P058 | 26172-55-4 | MCI | list gap | MCI is on none of the four lists. |
| P058 | 2682-20-4 | MIT | list gap | MIT is on none of the four lists. |
| P069 | 7440-38-2 | Arsenic | extraction error | Arsenic is Prop 65 listed but was not matched. CHECK Section 3 of P069 for how arsenic is written. |
| P076 | 26172-55-4 | MCI | list gap | MCI is on none of the four lists. |
| P076 | 2682-20-4 | MIT | list gap | MIT is on none of the four lists. |
| P079 | 26172-55-4 | Methylchloroisothiazolinone/Methylisothiazolinone | list gap | MCI is on none of the four lists. |
| P079 | 2682-20-4 | Methylchloroisothiazolinone/Methylisothiazolinone | list gap | MIT is on none of the four lists. |
| P079 | 78-51-3 | Tributoxyethyl Phosphate / TBEP | list gap | TBEP is on none of the four lists. |
| P087 | 1071-83-6 | Glyphosate | CAS form mismatch | Manual named glyphosate (acid CAS); SDS and tool use the isopropylamine salt. Same chemical. |
| P091 | 26172-55-4 | Methylchloroisothiazolinone/Methylisothiazolinone | list gap | MCI is on none of the four lists. |
| P091 | 2682-20-4 | Methylchloroisothiazolinone/Methylisothiazolinone | list gap | MIT is on none of the four lists. |
| P091 | 78-51-3 | Tributoxyethyl Phosphate / TBEP | list gap | TBEP is on none of the four lists. |
| P099 | 111-90-0 | Diethylene Glycol Monoethyl Ether / Ethoxydiglycol | list gap | Ethoxydiglycol is on none of the four lists. |
| P099 | 78-51-3 | Tributoxyethyl Phosphate | list gap | TBEP is on none of the four lists. |
| P103 | 112-34-5 | Diethylene Glycol Monobutyl Ether | list gap | Diethylene glycol monobutyl ether is on none of the four lists. |
| P103 | 78-51-3 | Tributoxyethyl Phosphate | list gap | TBEP is on none of the four lists. |
| P108 | 26172-55-4 | Methylchloroisothiazolinone/Methylisothiazolinone | list gap | MCI is on none of the four lists. |
| P108 | 2682-20-4 | Methylchloroisothiazolinone/Methylisothiazolinone | list gap | MIT is on none of the four lists. |
| P108 | 78-51-3 | Tributoxyethyl Phosphate / TBEP | list gap | TBEP is on none of the four lists. |
| P109 | 111-76-2 | 2-Butoxyethanol | list gap | 2-Butoxyethanol is on none of the four lists. |
| P112 | 26172-55-4 | Methylchloroisothiazolinone / MCI | list gap | MCI is on none of the four lists. |
| P112 | 2682-20-4 | Methylisothiazolinone / MIT | list gap | MIT is on none of the four lists. |
| P114 | 111-76-2 | Ethylene glycol monobutyl ether | list gap | 2-Butoxyethanol is on none of the four lists. |
| P114 | 64700-56-7 | Triclopyr | list gap | Triclopyr is on none of the four lists. |

### Tool only

| product_id | cas | chemical_name | label | explanation |
|---|---|---|---|---|
| P086 | 19666-30-9 |  | manual judgment | Oxadiazon is Prop 65 listed but the manual review did not flag it as a chemical of concern. |
| P087 | 38641-94-0 |  | CAS form mismatch | Isopropylamine salt of glyphosate. Same chemical the manual review flagged. |

## Manual rows not compared

Flagged by hand but no valid CAS, so they cannot be matched by CAS.

| product_id | cas | chemical_name | concern_level |
|---|---|---|---|
| P054 |  | Aliphatic Polyisocyanate based on HDI | HIGH |
