# Extraction spot check

Date: 2026-10-10
Sample: 10 products chosen with random.seed(1) from parsed products,
excluding the 5 products used during parser development.
Sample IDs: P023, P090, P012, P043, P020, P079, P072, P076, P103, P063

Method: each extracted row was compared to Section 3 of the SDS.
- Correct: name, CAS, and concentration all match.
- Wrong: the row exists but a value differs.
- Missed: in the SDS but not in the output.
- Extra: in the output but not an ingredient in the SDS.

## Run 1 (before fixes)

| Product | In SDS | Correct | Wrong | Missed | Extra | Flag right? | Notes |
|---|---|---|---|---|---|---|---|
| P023 | 9 | 1 | 8 | 0 | 0 | Yes | En dash ranges read as one number. First row name empty (name wraps onto two lines). |
| P090 | 3 | 3 | 0 | 0 | 0 | Yes | One name cut short ("Chloride" wrapped to next line). |
| P012 | 2 | 1 | 1 | 0 | 0 | Yes | ">=5.0 – <=10.0" read as 5 to 100. |
| P043 | 9 | 9 | 0 | 0 | 0 | Yes | |
| P020 | 2 | 0 | 2 | 0 | 0 | Yes | "1% - < 3%" read as 0 to 3. |
| P079 | 10 | 10 | 0 | 0 | 0 | Yes | Table spans a page break. |
| P072 | 0 | 0 | 0 | 0 | 1 | Yes | Footer date "12-19-2018" read as an ingredient at 12 to 19%. |
| P076 | 10 | 10 | 0 | 0 | 0 | Yes | Table spans a page break. |
| P103 | 5 | 5 | 0 | 0 | 0 | Yes | Table spans a page break. |
| P063 | 4 | 0 | 4 | 0 | 0 | Yes | En dash ranges read as one number. |

### Totals
- Ingredient rows in SDSs: 54
- Fully correct: 39 (72%)
- Wrong concentration: 15
- Missed: 0
- Extra: 1
- CAS numbers correct: 46 of 46
- Undisclosed flag correct: 10 of 10

### Verification status
- P023, P012, P020, P072, P063: output compared to the PDF.
- P090, P043, P079, P076, P103: output compared to extracted text only.
  PDF comparison still to do.

### Error patterns
1. En dash used as the range separator, for example "3 – 4%". 12 rows.
2. Percent sign and a bound inside a range, "1% - < 3%". 2 rows.
3. Bounds on both ends of a range, ">=5.0 – <=10.0". 1 row.
4. A date in a page footer read as a concentration range. 1 extra row.
5. Ingredient names that wrap onto two lines come out empty or cut short.
   Values are correct. 2 rows.

All 15 wrong values are concentration errors. No CAS number was wrong or missed.

## Run 2 (after fixes)

Changes made: the range pattern now accepts en and em dashes, a percent sign
after the first number, and bounds on either end. Number chains such as dates
are rejected.

| Product | In SDS | Correct | Wrong | Missed | Extra | Flag right? | Notes |
|---|---|---|---|---|---|---|---|
| P023 | 9 | 8 | 1 | 0 | 0 | Yes | All concentrations fixed. First row still has an empty name. |
| P090 | 3 | 3 | 0 | 0 | 0 | Yes | One name still cut short. |
| P012 | 2 | 2 | 0 | 0 | 0 | Yes | Now 5.0 to 10.0. |
| P043 | 9 | 9 | 0 | 0 | 0 | Yes | Unchanged. |
| P020 | 2 | 2 | 0 | 0 | 0 | Yes | Now 1.0 to 3.0. |
| P079 | 10 | 10 | 0 | 0 | 0 | Yes | Unchanged. |
| P072 | 0 | 0 | 0 | 0 | 0 | Yes | Date row gone. |
| P076 | 10 | 10 | 0 | 0 | 0 | Yes | Unchanged. |
| P103 | 5 | 5 | 0 | 0 | 0 | Yes | Unchanged. |
| P063 | 4 | 4 | 0 | 0 | 0 | Yes | All concentrations fixed. |

### Totals
- Fully correct: 53 of 54 (98%)
- Wrong: 1 (empty name in P023; its CAS and concentration are correct)
- Missed: 0
- Extra: 0
- CAS numbers correct: 46 of 46
- Concentrations correct: 54 of 54

Note: Run 2 uses the same 10 products that revealed the errors, so it shows
the fixes work. It is not an independent accuracy estimate.

## Known limits
- Only Section 3 is parsed. Some SDSs disclose more ingredients in Section 15.
  Seen in P020 (Right to Know table) and P063 (CA Cleaning Product Right to
  Know table, 10 ingredients versus 4 in Section 3).
- Ingredient lists given as names only, with no CAS numbers, are not parsed.
  Seen in P088.
- Names that wrap onto two lines are not rejoined.
- Scanned and garbled PDFs are not read.
- The undisclosed flag matches keywords, not meaning. The evidence string can
  point at boilerplate text.