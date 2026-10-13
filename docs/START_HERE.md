# Start Here: irAE-Map

*Read this first. It explains the project in plain language. Words in bold are explained in [GLOSSARY.md](GLOSSARY.md).*

## What you are building

A free, public lookup table that says, for each kind of immunotherapy side effect (for example "immune-related colitis"), which official grading terms, which diagnosis codes, and which FDA safety-report terms describe it.

## Why it matters

Immunotherapy drugs (**immune checkpoint inhibitors**) can make the immune system attack healthy organs: the gut, liver, lungs, thyroid, skin, heart, and more. These are called **immune-related adverse events (irAEs)**.

The same side effect is described three different ways depending on who writes it down:

- Cancer trials grade it with **CTCAE** terms ("Colitis, grade 3").
- Hospitals bill it with **ICD-10-CM** codes ("K52.1 Toxic gastroenteritis and colitis", plus a code saying a drug caused it).
- The FDA's safety database (**FAERS**) files it under **MedDRA** reaction terms ("Immune-mediated enterocolitis").

Nobody has published a checked, public table that connects all three. So every hospital, researcher, and drug-safety team builds its own, in private, and their numbers do not agree.

In 2026 the National Cancer Institute released CTCAE version 6.0, which added terms partly to describe immunotherapy side effects better (Hepatitis, Thyroiditis, Diabetes mellitus, Encephalitis, Tubulointerstitial nephritis, and others are new). That makes now the right time for a public crosswalk.

Think of it like a translation dictionary between three languages that describe the same illnesses.

## Where the information comes from

All sources are free and public. Nothing here needs special permission.

| Source | In plain terms | What one row looks like | Link |
|---|---|---|---|
| CTCAE v6.0 (NCI, 2026) | The cancer field's official list of side-effect names and how to grade them 1 to 5 | One side effect: name, organ group, what grades 1 to 5 mean | https://dctd.cancer.gov/research/ctep-trials/for-sites/adverse-events |
| ICD-10-CM FY2027 (CDC/NCHS) | The US list of diagnosis codes used in medical records and billing, in effect since October 1, 2026 | One code and its description | https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Publications/ICD10CM/2027/ |
| openFDA FAERS | The FDA's public database of reported drug side effects | One reaction term and how many reports mention it with these drugs | https://open.fda.gov/apis/drug/event/ |

## What you will have at the end

- [ ] **irAE-Map v1.0**, the table itself, on GitHub with a permanent **DOI** from Zenodo (December 2026)
- [ ] **A codebook and mapping rationale document**, released with v1.0, with its own DOI (December 2026)
- [ ] **A coverage analysis dataset** showing which CTCAE v6.0 immune-related terms have no specific ICD-10-CM code, with its own DOI (April 2027). This shows coders and the CDC where the code set falls short.
- [ ] **iraemap v0.1**, a small Python package that applies the table to someone's own codes (GitHub and PyPI, March 2027)
- [ ] **irAE-Map v2.0**, updated to the FY2028 ICD-10-CM codes (October 2027, after CDC publishes them)

## How it connects to your work

This is the coding layer under your OMOP-based irAE data model: it gives the irAE categories in that model a documented, citable link to the codes that actually appear in EHRs and FDA reports.

## Who decides what

Claude writes the code and proposes candidate mappings with a suggested reason. You decide them. For v1.0 you accepted the suggestions as a group and changed E27.1; the documents say so plainly, and each row records how it was decided.

## What you need to do

| Your task | When | Time |
|---|---|---|
| Create accounts (ORCID, GitHub, Zenodo) | Now | 15 min |
| Answer five setup questions | Now | 10 min |
| Review and decide the proposed mappings in the review workbook | Oct to Nov 2026 | about 5 to 7 hours in total, in sittings of 30 to 60 min |
| Check the results using the checklist | When the draft is ready | 1 to 2 hours |
| Approve publishing | After checking | 5 min |

## The steps ahead

1. **Data collected.** Download the three public sources and record exactly where each came from.
2. **Candidates proposed.** For each irAE category, list every CTCAE term, ICD-10-CM code, and FAERS term that might belong, with a suggested decision and reason.
3. **Your review.** You decide each candidate in a spreadsheet: include or exclude, confidence, look-alikes.
4. **Table built and checked.** Your decisions become the final table, with automatic quality checks.
5. **Codebook and rationale document.** Every number in it comes straight from the data.
6. **Ready for your final check.** You verify, then we publish v1.0 with a DOI.

*You are here: steps 1 to 5 done. Step 6 (your final check) is next.*
