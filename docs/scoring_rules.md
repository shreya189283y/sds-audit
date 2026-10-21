# Scoring rules

This file defines how the tool assigns a concern level to each product.
The rules were written before validation and are frozen as of the date below.
Any change after that date is recorded in the change log at the end, with
the reason.

**Frozen:** TODO (date you start validation)

## Levels

Each product gets exactly one level. Levels are checked from the top down.
The first rule that applies sets the level.

| Order | Level | Rule |
|---|---|---|
| 1 | HIGH | At least one ingredient is on Prop 65, the EU SVHC Candidate List, or EU ED List I, and that match has no condition attached. |
| 2 | MEDIUM | At least one ingredient is on EU ED List II or III, or has a conditional match. No HIGH match. |
| 3 | UNDISCLOSED | No matches on any list, and the SDS withholds part of the formula. |
| 4 | LOW (no list matches) | No matches on any list, and the formula is fully disclosed. |
| n/a | UNREADABLE | The SDS could not be read. The product was not checked. |

## Why each rule

**HIGH.** Prop 65, the SVHC Candidate List, and ED List I are formal
government determinations. Each one means an authority has concluded the
chemical causes cancer, reproductive harm, or endocrine disruption, or is of
equivalent concern. One such ingredient is enough to put the product at the
top of the review list.

**MEDIUM.** ED List II covers chemicals still under evaluation in the EU. ED
List III reflects the view of a single national authority that has not been
reviewed by other member states. The evidence is real but not settled.
Conditional matches also go here. The Prop 65 listings for crystalline silica
and titanium dioxide apply only to airborne particles of respirable size, so
whether they apply depends on the product's form.

## UNDISCLOSED (updated before validation)

UNDISCLOSED means at least one ingredient's identity is hidden: a row with
no CAS number, or a statement that "other ingredients" or a chemical
identity is withheld.

Not UNDISCLOSED:
- Every ingredient is named with a CAS and only the exact percentage is
  hidden. The tool notes "exact % withheld only" but does not flag it.
- "Other components below reportable levels." This is a legal threshold
  statement, not a hidden ingredient.
- Bacterial spores or cultures. These have no CAS by nature.

Order: HIGH > UNDISCLOSED > MEDIUM > LOW.

**LOW (no list matches).** Every disclosed ingredient was checked and none
appeared on the four lists.

**UNREADABLE.** The SDS was a scanned image or had a garbled text layer. The
tool reports these products so a district knows what was not checked.

## Order of levels

HIGH > MEDIUM > UNDISCLOSED > LOW.

A product's level is the highest level any of its ingredients reaches.

MEDIUM ranks above UNDISCLOSED. A known match is stronger evidence than
missing information. If UNDISCLOSED ranked higher, a product with a List II
chemical and a hidden fragrance would be labeled only UNDISCLOSED, and the
known match would disappear from the label. The undisclosed flag is still
shown for every product it applies to, whatever the level.

## What LOW does not mean

LOW means the product matched none of the four lists. It does not mean the
product is safe. Some chemicals of concern are on none of these lists,
including TBEP and the isothiazolinone preservatives. A product containing
them is scored LOW. See Known limits in `docs/sources.md`.

## Concentration

Concentration ranges are shown for every flagged ingredient. In this version
they do not raise or lower the level. A chemical at 0.1% and one at 30% are
scored the same.

This is deliberate. The lists identify hazard, not exposure. Choosing a
concentration cutoff would require a separate exposure judgment for each
chemical, which this version does not attempt.

## EPA Safer Chemical Ingredients List

SCIL is not used for scoring. A match on SCIL never raises or lowers a level.
It is used only to mark ingredients as safer and to support replacement
suggestions.

## What every result includes

- The level
- The rule that set it, in one sentence
- Every match: ingredient, CAS, list, endpoint, source link, and any group or
  condition
- Whether the formula is undisclosed

## Change log

| Date | Change | Reason |
|---|---|---|
| | | |