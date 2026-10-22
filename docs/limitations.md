# Limitations

This tool checks the ingredients in a Safety Data Sheet (SDS) against four regulatory lists: California Prop 65, the EU SVHC Candidate List, the EU Endocrine Disruptor Lists I to III, and EPA's Safer Chemical Ingredients List. Everything below follows from that design.

**LOW means no list match. It does not mean safe.**

## 1. The SDS does not show the whole formula

- SDSs must list ingredients classified as health hazards that are present above their cut-off limits. Unclassified ingredients do not have to appear. [1]
- The cut-off for carcinogens is 0.1%. [2] Most other health hazards use a 1% cut-off. [VERIFY: cite 29 CFR 1910.1200 Appendix A]
- So a product can contain an endocrine disruptor below the cut-off, or one that is not classified, and the SDS will not show it.

## 2. Trade secrets hide what the tool needs

- Manufacturers may withhold an ingredient's identity, its exact percentage, or both. The required statement reads "the specific chemical identity and/or exact percentage (concentration) of composition has been withheld as a trade secret." [1]
- That wording does not say which was withheld. Many SDSs print it even when every ingredient is named.
- The tool marks a product UNDISCLOSED only when an ingredient has no CAS number, or the SDS says an ingredient's identity is withheld. A hidden percentage alone is noted but not flagged.

## 3. There is no US hazard class for endocrine disruption

- In 2023 the EU added endocrine disruption hazard classes to its CLP Regulation. Mixtures must be labeled by May 1, 2026. [3][4]
- The US OSHA Hazard Communication Standard has no such class. [VERIFY: cite the hazard class list in 1910.1200 Appendix A] US SDSs are therefore not required to flag endocrine disruption as a hazard.

## 4. The lists lag the science

- The tool only knows what is on its four lists. In validation, 11 of 23 product-level disagreements came from chemicals no list covers.
- Examples: the isothiazolinone preservatives MIT and MCI, the floor-finish plasticizer TBEP, the isocyanate HDI, and 2-butoxyethanol. Peer-reviewed studies raise endocrine or sensitization concerns for several of these. The tool rates them LOW.

## 5. Some listings cannot be matched by CAS

- Some entries name a group or a condition instead of one CAS number, such as "Arsenic (inorganic arsenic compounds)" or "Silica, crystalline (airborne particles of respirable size)."
- Groups are mapped to CAS numbers by hand in `data/cas_groups.csv`. Missing mappings cause missed hits. Validation found one, arsenic, which is now fixed. Others may remain.
- Conditional listings are rated MEDIUM, because an SDS cannot show the physical form or exposure route. Listings that depend on refinement, such as "mineral oils, untreated and mildly treated," are not judged.

## 6. Concentration is ignored

A listed chemical at 0.1% and at 50% gets the same level. Concentration is shown for context only.

## 7. Scanned and unusual files

- The tool reads text-based PDFs only. It has no OCR.
- 14 of 116 products in the development district could not be read. In the held-out sample, 3 of 10 were scans. Unreadable products are shown as UNREADABLE, never dropped.
- The parser can also miss ingredient lists without CAS numbers, CAS numbers split across two lines, and manufacturer CAS typos.

## 8. Validation is small and has limits

- **Development set:** 35 products from one district's manual audit, used to find bugs. Four audited products could not be matched to their files. This is not an accuracy measure.
- **Held-out set:** 10 products drawn at random (seed 42) from the 80 unreviewed. The tool agreed on 7. All 3 misses were scanned PDFs. This review was AI-assisted and spot-checked by the author.
- Both sets were graded against the lists, so neither measures chemicals the lists miss.
- All data comes from one California school district.

## Sources

1. OSHA, 29 CFR 1910.1200 Appendix D, Section 3 requirements. https://www.osha.gov/sites/default/files/appendix_d.pdf
2. OSHA standard interpretation, July 24, 2017. https://www.osha.gov/laws-regs/standardinterpretations/2017-07-24
3. CIRS, "New hazard classes introduced for CLP regulation." https://www.cirs-group.com/en/chemicals/new-hazards-classes-introduced-for-clp-regulation
4. Health and Safety Authority (Ireland), "New CLP hazard classes for endocrine disrupting properties for human health." https://hsa.ie/media/miqocxlq/2-new-clp-hazard-classes-for-endocrine-disrupting-properties-for-human-health.pdf