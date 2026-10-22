# Validation report

Generated 2026-10-21 from `docs/heldout_manual.csv` and `data/results.csv`.
Scoring rules frozen at tag `rules-v1`. All figures are counts.
Counted as agreement besides exact matches: [('NONE', 'LOW')].

## Coverage

Products in ground truth: 10
Products found in tool output: 10
Missing from tool output: none

## Product level

Rows are the manual level. Columns are the tool level.

| manual \ tool | HIGH | MEDIUM | UNDISCLOSED | LOW | UNREADABLE |
|---|---|---|---|---|---|
| HIGH | 1 | 0 | 0 | 0 | 0 |
| MEDIUM | 0 | 0 | 0 | 0 | 0 |
| UNDISCLOSED | 0 | 0 | 2 | 0 | 2 |
| LOW | 0 | 0 | 0 | 4 | 1 |
| NONE | 0 | 0 | 0 | 0 | 0 |

Agreement: 7 of 10 products.

### Product disagreements

| product_id | product_name | manual | tool | label | explanation |
|---|---|---|---|---|---|
| P022 |  | UNDISCLOSED | UNREADABLE |  |  |
| P024 |  | UNDISCLOSED | UNREADABLE |  |  |
| P075 |  | LOW | UNREADABLE |  |  |

## Chemical level

Found by both: 2
Manual only (tool missed): 0
Tool only (not in manual review): 0

### Manual only

None.

### Tool only

None.

## Manual rows not compared

Flagged by hand but no valid CAS, so they cannot be matched by CAS.

None.
