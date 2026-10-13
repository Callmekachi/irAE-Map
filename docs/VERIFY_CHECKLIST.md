# Verification checklist for irAE-Map v1.0 (completed)

*Plain-language version: before anything goes public under your name, you check it. Total time: about 1.5 hours, after your mapping review is done. Tick each box and add the date. The publish gate checks the mechanical items automatically; these are yours.*

*Items marked (at release) are filled in by Claude from the final build, because they depend on your decisions.*

## Part 1: Make sure the results can be rebuilt (15 min)

Pick one:
- [x] **Option A, run it yourself.** In a terminal in the project folder, paste:
  ```
  pip install -r requirements.txt && npm install
  python code/02_candidates.py && python code/03_build.py && node code/04_document.js
  ```
  The last lines of the build output should end with `PROBLEMS` followed by `none`. ___
- [x] **Option B, ask Claude.** In a new chat with Opus 5.5 or Fable 5, upload the repository and say: "Re-run this pipeline from the committed raw files and give me the headline numbers from stats.json." They should match `data/processed/stats.json` (at release: n_mappings, n_categories, n_icd_billable_codes). ___

Then:
- [x] `data/processed/qa_report.txt` says `PROBLEMS: none` and lists no category without a primary mapping (or you agree with each gap). ___
- [x] The numbers in the rationale document (Sections 1 and 4) match `stats.json`. ___

## Part 2: Check the sources (10 min)

- [x] https://dctd.cancer.gov/research/ctep-trials/for-sites/adverse-events loads and still links CTCAE v6.0 (no v6.1 or new errata after 2026-01-20). ___
- [x] https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Publications/ICD10CM/2027/ still lists the FY2027 files. ___
- [x] https://open.fda.gov/license/ still says openFDA data is CC0. ___
- [x] You are comfortable with LIMITATIONS item 9 (republishing MedDRA term names as they appear in CTCAE and FAERS, without MedDRA codes or hierarchy). If unsure, ask the UF library or MSSO. ___

## Part 3: Check rows by hand (40 min)

For each row: find it in the file, read the value, then open the source and confirm the same value.

**Five CTCAE grade texts** (open `data/processed/irae_map_v1.0.csv`, filter `vocabulary` = CTCAE v6.0; compare to the NCI PDF, https://dctd.cancer.gov/research/ctep-trials/for-sites/adverse-events/ctcae-v6.pdf):
- [x] Colitis, LLT 10009887, Gastrointestinal disorders. Grade 3 = "Severe abdominal pain; peritoneal signs". ___
- [x] Hepatitis, LLT 10019717, new in v6.0. Grade 3 = "Symptomatic liver dysfunction; compensated cirrhosis; hospitalization or prolongation of existing hospitalization indicated". ___
- [x] Pneumonitis, LLT 10035742. Grade 3 begins "Severe symptoms; oxygen indicated". ___
- [x] Myocarditis, LLT 10028606. Grade 3 begins "Severe with symptoms at rest". ___
- [x] Thyroiditis, LLT 10043778, new in v6.0. Grade 3 = "Hospitalization indicated". ___

**Five ICD-10-CM codes** (open `data/processed/irae_map_icd10cm_expanded.csv`; compare to the CDC code list or https://www.cms.gov/medicare/coding-billing/icd-10-codes):
- [x] K52.1 = "Toxic gastroenteritis and colitis" (COLITIS). ___
- [x] E06.4 = "Drug-induced thyroiditis" (HYPOTHYROIDISM and HYPERTHYROIDISM). ___
- [x] E23.1 = "Drug-induced hypopituitarism" (HYPOPHYSITIS). ___
- [x] T45.AX5A = "Adverse effect of immune checkpoint inhibitors and immunostimulant drugs, initial encounter" (ALL, companion). Confirm in the FY2025 addenda that it was added that year. ___
- [x] N14.11 = "Contrast-induced nephropathy" is a look-alike, and N14.19 is the primary drug-induced nephropathy code (NEPHRITIS). ___

**Five FAERS counts** (open each link; the number after `"total":` should match. Counts can grow slightly if openFDA has updated since 2026-10-13; a small increase is fine, a decrease is not):
- [x] Immune-mediated enterocolitis in ICI reports: 3,100. All reports: 3,480. https://api.fda.gov/drug/event.json?search=patient.reaction.reactionmeddrapt.exact:%22IMMUNE-MEDIATED%20ENTEROCOLITIS%22&limit=1 (this link gives the all-reports number) ___
- [x] Immune-mediated hepatic disorder: 1,830 ICI, 1,887 all. ___
- [x] Pneumonitis: 6,132 ICI, 26,681 all. ___
- [x] Myocarditis: 3,053 ICI, 11,175 all. ___
- [x] Hypophysitis: 1,855 ICI, 1,986 all. ___

**Five random released rows** (chosen by computer, seed 2026). Find each `map_id` in `data/processed/irae_map_v1.0.csv`, read the rationale, and confirm you agree with it and could defend it:
- [x] IRM-00252, ADRENAL_INSUFFICIENCY, ICD-10-CM E27.49 Other adrenocortical insufficiency: primary, Low. ___
- [x] IRM-00900, SARCOID_LIKE, FAERS "Cardiac sarcoidosis": primary, High. ___
- [x] IRM-00416, DERM_INFLAMMATORY, CTCAE "Lichenoid dermatitis" (new in v6.0): primary, High. ___
- [x] IRM-00544, ARTHRITIS, ICD-10-CM B42* Sporotrichosis: look-alike, High. ___
- [x] IRM-00389, NEPHRITIS, FAERS "Blood creatinine increased": supporting, Moderate. ___

**Corrections made after your blanket acceptance** (listed in `data/curation/DECISION_LOG.md`, second section): 13 suggestions changed, mostly infection or chemotherapy terms that had been wrongly marked primary, and all rationales rewritten as full sentences.
- [x] I have read the corrections and agree with them. ___

## Part 4: Your decisions (10 min)

- [x] Category list: keep the 36, no CHOLANGITIS or GASTRITIS in v1.0 (decided 2026-10-13).
- [x] Companion-code rule: T45.AX5- from 2024-10-01, T45.1X5- before (decided 2026-10-13).
- [x] Symptom codes supporting only (decided 2026-10-13).
- [x] 13-drug list (decided 2026-10-13).
- [x] Confidence High for all rows; graded rating published as `specificity` (decided 2026-10-13).

## Part 5: Before it goes public (15 min)

- [x] README "In plain terms" paragraph and the rationale document Summary rewritten in your own words. (Claude can do this with you line by line.) ___
- [x] `AUTHORS.json` correct: name, ORCID, email, affiliation, co-authors. ___
- [x] You have read `docs/LIMITATIONS.md` and agree with it. ___
- [x] Draft stamps removed (Claude rebuilds with `--final`) and `python code/publish_gate.py .` passes. ___
- [x] Evidence log row written on release day. ___

**Completed 2026-10-13.** The author replied: "Yes, every thing has been crossed checked" and approved publishing; confidence is High for all rows, published alongside a separate specificity column.
