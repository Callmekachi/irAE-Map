# Build spec: irAE-Map v1.0

*Plain-language note: this is the one-page plan the build follows. The table at the bottom says what each line means for you. If the project changes shape, this file changes first.*

```
PROJECT:        irAE-Map. Archetype: open dataset (crosswalk table) + technical
                report (codebook and mapping rationale). Later: pipeline/tool
                (iraemap Python package, v0.1 March 2027).

QUESTION:       For each immune-related adverse event (irAE) category, which
                CTCAE v6.0 terms and grades, ICD-10-CM codes, and FAERS
                (MedDRA) reaction terms describe it, how confidently, and what
                does it get confused with?

SOURCES:        1. NCI CTCAE v6.0 spreadsheet (MedDRA 28.0), errata 2026-01-20.
                   https://dctd.cancer.gov/research/ctep-trials/trial-development/ctcae-v6.0.xlsx
                   Freely distributed by NCI. Its terms are MedDRA terms;
                   MedDRA is licensed by ICH/MSSO (see LIMITATIONS 9).
                   Accessed 2026-10-13.
                2. CDC/NCHS ICD-10-CM FY2027 code descriptions and addenda,
                   effective 2026-10-01.
                   https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Publications/ICD10CM/2027/
                   US government work, public domain. Accessed 2026-10-13.
                3. openFDA drug adverse event endpoint (FAERS), data last
                   updated 2026-07-30. https://api.fda.gov/drug/event.json
                   CC0 per https://open.fda.gov/license/. Accessed 2026-10-13.
                Checksums and exact URLs: data/raw/PROVENANCE.txt.

UNIT:           One mapping = (irAE category, source vocabulary, source code
                or term). ICD-10-CM is reviewed by code family (parent code +
                billable children) and published expanded to every billable
                code.

MEASURES:       role         primary / supporting / lookalike / companion
                confidence   author's confidence the role is correct (High, all rows)
                specificity  High / Moderate / Low
                rationale    one sentence, author's words or accepted draft
                lookalike    note on confusable diagnoses
                ici_reports  FAERS reports naming any of 13 ICIs with the term
                ici_prr      (a/N_ici) / ((b-a)/(N_all-N_ici)); descriptive
                             over-representation, not a signal statistic
                grades       CTCAE v6.0 grade 1-5 text, copied verbatim

OUTPUTS:        data/processed/irae_map_v1.0.csv          (long table)
                data/processed/irae_map_icd10cm_expanded.csv
                data/processed/irae_categories.csv
                data/processed/qa_report.txt, stats.json
                docs/CODEBOOK.md
                report/irAE-Map_mapping_rationale_v1.0.docx (DOI)
                CITATION.cff, LICENSE, LICENSE-DATA
                data/processed/coverage/ctcae_icd10cm_coverage.csv and
                  coverage_stats.json: which CTCAE v6.0 immune-related terms
                  lack a specific ICD-10-CM code (code/05_coverage.py)

VENUES:         1. GitHub repository (public), tagged v1.0.0
                2. Zenodo: dataset DOI (table + codebook), Dec 2026
                3. Zenodo: rationale document DOI, Dec 2026
                4. Zenodo: coverage analysis dataset DOI, Apr 2027
                5. Later: PyPI package iraemap 0.1 (Mar 2027); data descriptor
                   paper (e.g., JAMIA Open, Scientific Data) optional

VERIFY POINTS:  a. Category list (keep / merge / drop / add)
                b. Every mapping row: role, confidence, rationale
                c. ICD-10-CM scope: symptom codes as "supporting" only
                d. Companion-code rule: T45.AX5- from 2024-10-01, T45.1X5- before
                e. Drug list for FAERS (13 ICIs)
                f. Confidence scale definitions
                g. Spot checks in VERIFY_CHECKLIST.md
                h. Coverage definitions (specific / nonspecific / none) and,
                   for April 2027, the best ICD-10-CM code per CTCAE term

LICENSE:        Table and documents CC BY 4.0. Code MIT.

DECISIONS:      Author answered 2026-10-13 (data/curation/DECISION_LOG.md):
                accept all drafted suggestions; E27.1 rated High; defaults
                for categories, companion codes, drug list; licenses default.
```

## What each line means for you

| Field | In plain terms |
|---|---|
| Project | You are publishing a lookup table plus a document explaining it. A small software package comes later. |
| Question | For each kind of immunotherapy side effect, which official terms and codes describe it. |
| Sources | Three free government sources. All are public domain or CC0, so you can republish derived work. |
| Unit | Every row of the final table is one link, for example "Colitis category, ICD-10-CM, K52.1". |
| Measures | Each link carries your decision (role, confidence, reason) plus some facts copied from the sources. |
| Outputs | The files people will download. |
| Venues | GitHub first, then Zenodo for the permanent DOI. |
| Verify points | The decisions only you can make. |
| License | Anyone can reuse the table if they credit you. |
