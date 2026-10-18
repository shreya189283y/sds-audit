# Hazard list sources
 
This file records where each list came from, which version is used, and what
being on the list means. Fill in every `TODO` when you download the file.
Retrieval dates matter: these lists change several times a year.
 
## Summary
 
| List | Publisher | Type | Raw file | Version | Retrieved |
|---|---|---|---|---|---|
| Proposition 65 | California OEHHA | Hazard | `data/lists/raw/TODO` | TODO (list date) | TODO |
| EU SVHC Candidate List | European Chemicals Agency (ECHA) | Hazard | `data/lists/raw/TODO` | TODO (last update date) | TODO |
| EU Endocrine Disruptor Lists I, II, III | National authorities of BE, DK, FR, NL, SE, ES | Hazard | `data/lists/raw/TODO` | TODO (last update date) | TODO |
| EPA Safer Chemical Ingredients List (SCIL) | US EPA Safer Choice | Safer (positive) | `data/lists/raw/TODO` | TODO | TODO |
 
---
 
## 1. California Proposition 65
 
- **URL:** https://oehha.ca.gov/proposition-65/proposition-65-list/
- **File used:** Excel version of the list
- **Version:** TODO (the date printed on the list)
- **Retrieved:** TODO
**What it is.** California's list of chemicals known to the State to cause
cancer, reproductive toxicity, or both. The Governor must republish it at least
once a year. Each listing names a toxicity type: cancer, developmental,
female reproductive, or male reproductive.
 
**What listing means legally.** Businesses must give a clear warning before
knowingly exposing people in California to a listed chemical, unless the
exposure is below the safe harbor level. Listing is not a ban. It is based on
hazard. Whether a warning is required depends on exposure.
 
**Data notes.**
- Chemicals that were listed and later removed appear in strikeout in the
  official list. These rows must be dropped. Method used: TODO
- Some entries are groups with no CAS number. These are handled in
  `data/cas_groups.csv`.
**How this tool uses it.** Any ingredient on this list sets the product to HIGH.
 
---
 
## 2. EU SVHC Candidate List (REACH)
 
- **URL:** https://echa.europa.eu/candidate-list-table
- **File used:** Excel export of the candidate list table
- **Version:** TODO (date of last update shown on the page)
- **Entries:** TODO
- **Retrieved:** TODO
**What it is.** The EU list of Substances of Very High Concern under REACH
(Regulation (EC) 1907/2006). Substances are added for reasons such as being
carcinogenic, mutagenic, or toxic to reproduction; persistent and
bioaccumulative; or of equivalent concern, which includes endocrine disruption.
The reason for each substance is listed.
 
**What listing means legally.** Listing triggers information duties, not a ban.
Suppliers must provide a safety data sheet. Suppliers of articles containing
more than 0.1% by weight must share safe use information and notify ECHA.
Listed substances may later be moved to the Authorisation List, which restricts
use. This is EU law. It has no legal force for a California school district. It
is used here as an expert hazard identification.
 
**Data notes.**
- Some entries are groups (for example, nonylphenol ethoxylates) with no single
  CAS number. These are handled in `data/cas_groups.csv`.
**How this tool uses it.** Any ingredient on this list sets the product to HIGH.
The endpoint column stores the reason for inclusion.
 
---
 
## 3. EU Endocrine Disruptor Lists
 
- **URL:** https://edlists.org/
- **Files used:** List I, List II, List III
- **Version:** TODO (last update date shown on the site)
- **Retrieved:** TODO
**What it is.** A compilation maintained by national authorities in Belgium,
Denmark, France, the Netherlands, and Sweden, joined by Spain in 2021. It has
three lists:
 
- **List I:** substances identified as endocrine disruptors at EU level.
- **List II:** substances under evaluation for endocrine disruption under an EU
  law.
- **List III:** substances that one national authority considers to have
  endocrine disrupting properties.
**What listing means legally.** The website itself is not a legal instrument.
List I reflects formal EU decisions. List II reflects open evaluations. List III
reflects the opinion of a single authority and has not been reviewed by other
member states. The site states this in its own disclaimer.
 
**How this tool uses it.**
- List I sets the product to HIGH.
- Lists II and III set the product to MEDIUM, because the evidence has not
  completed an EU review.
---
 
## 4. EPA Safer Chemical Ingredients List (SCIL)
 
- **URL:** https://www.epa.gov/saferchoice/safer-ingredients
- **File used:** downloadable spreadsheet on that page
- **Version:** TODO
- **Retrieved:** TODO
**What it is.** A list of ingredients, grouped by function, that EPA's Safer
Choice program has evaluated and found to be safer than traditional ingredients
for that function. Each chemical has a rating:
 
- Green circle: verified low concern.
- Green half circle: expected low concern, more data would help.
- Yellow triangle: best available for its function, with some hazard gaps.
- Grey square: may be removed. Removal follows 12 months later unless data
  justifies keeping it.
**What listing means legally.** Nothing is required or banned. It is guidance
for manufacturers. The list is not complete, so an ingredient missing from it is
not evidence of hazard. EPA does not list fragrances or impurities.
 
**How this tool uses it.** This is not a hazard list. It is stored in a separate
table, `safer_list`, and never counts as a flag. It is used only to mark
ingredients as safer and to support replacement suggestions. Grey square
chemicals are not marked as safer.
 
---
 
## Rows dropped during normalization
 
Filled in by the output of `python src/build_db.py`.
 
| List | Rows in raw file | Dropped: no CAS | Dropped: invalid CAS | Dropped: delisted | Rows kept |
|---|---|---|---|---|---|
| Prop 65 | TODO | TODO | TODO | TODO | TODO |
| SVHC | TODO | TODO | TODO | n/a | TODO |
| ED List I | TODO | TODO | TODO | n/a | TODO |
| ED List II | TODO | TODO | TODO | n/a | TODO |
| ED List III | TODO | TODO | TODO | n/a | TODO |
| SCIL | TODO | TODO | TODO | n/a | TODO |
 
## Known limits
 
- Matching is by CAS number only. Ingredients listed without a CAS number
  cannot be matched, except through group mapping.
- Group entries are mapped only where a basis can be cited. Unmapped groups
  are missed.
- Being on a hazard list describes hazard, not exposure. A HIGH product is a
  product to review, not proof of harm at the concentration used.
 - Some chemicals of concern are on none of the four lists, including TBEP
  (78-51-3) and the isothiazolinone preservatives (2682-20-4, 26172-55-4,
  2634-33-5). Products containing them are not flagged by the tool.
- Prop 65 delisted chemicals are removed using the word "Delisted" in the
  chemical name (25 rows). Two partial endpoint removals were fixed by hand:
  toluene (female reproductive removed) and 2,4-D butyric acid
  (developmental removed).
 ## Group mappings

Some Prop 65 entries name a group of chemicals and give no CAS number, for
example "Lead and lead compounds". These rows are dropped during
normalization because they cannot be matched by CAS. The groups most likely
to appear in school products are mapped to specific CAS numbers in
`data/cas_groups.csv`. `lookup()` checks this file after the database, and
each match records the group name in `via_group`.

Every mapping cites where its CAS number comes from in the `basis` column.
A CAS is only mapped when a source links it to the listing.

| Prop 65 group | CAS mapped | Source for the CAS |
|---|---|---|
| Lead / Lead and lead compounds | 7439-92-1 | NTP Report on Carcinogens |
| Cocamide diethanolamine | 68603-42-9 | OEHHA notice of intent to list |
| Diisononyl phthalate (DINP) | 28553-12-0, 68515-48-0 | US EPA DINP risk evaluation (2025) |
| Silica, crystalline (respirable) | 14808-60-7, 14464-46-1, 15468-32-3 | IARC Monograph 68 |
| Titanium dioxide (respirable) | 13463-67-7 | Japan NITE GHS classification |
| Glyphosate (salts) | 38641-94-0, 40465-66-5, 69254-40-6, 34494-03-6, 81591-81-3 | OEHHA notice of intent to list glyphosate (2017) |

### Conditional listings

The silica and titanium dioxide listings apply only to airborne particles of
respirable size. A match on these is stored with a `condition` and must be
read against the product's form. Titanium dioxide in a liquid is not the
listed hazard.
Ethylene glycol (107-21-1) and carbon black (1333-86-4) are also conditional.
Their Prop 65 names state the condition: "Ethylene glycol (ingested)" and
"Carbon black (airborne, unbound particles of respirable size)". lookup()
reads the condition from the name, so these score MEDIUM, not HIGH.
### Glyphosate salts

Products list glyphosate as a salt, not as glyphosate itself. OEHHA's 2017
notice names five salts as relevant because they dissociate to free
glyphosate. Only those five are mapped. 

### Checked and deliberately not mapped

- Amorphous silica (7631-86-9, 112926-00-8). Prop 65 lists only crystalline
  silica.
- White mineral oil and hydrotreated petroleum distillates. Prop 65 lists
  only untreated and mildly treated mineral oils.
- Cocamide MEA (68140-00-1). A different chemical from cocamide DEA.
- Elemental arsenic (7440-38-2). Prop 65 lists inorganic arsenic compounds.
  OEHHA does not state whether the element is included. Flagged for manual
  review.