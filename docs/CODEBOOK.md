# Codebook: irAE-Map v1.0

*Plain-language note: this defines every column in every file people download. If someone asks "what does this column mean?", the answer is here. You do not need to edit it unless a column changes.*

## Files

| File | One row is | Use it for |
|---|---|---|
| `data/processed/irae_map_v1.0.csv` | One mapping: an irAE category linked to one CTCAE term, one ICD-10-CM code family, or one FAERS reaction term | The main table |
| `data/processed/irae_map_icd10cm_expanded.csv` | One billable ICD-10-CM code within a mapped code family | Joining directly to diagnosis tables in EHR or claims data |
| `data/processed/irae_categories.csv` | One irAE category | Category definitions and category-level look-alikes |
| `data/curation/irAE-Map_review.xlsx` | Every candidate considered, with the suggestion and the author's decision | Auditing what was considered and why |
| `data/processed/qa_report.txt`, `stats.json` | Build checks and headline numbers | Verifying a release |

## `irae_map_v1.0.csv`

| Column | Definition | Source / transformation |
|---|---|---|
| `map_id` | Stable row identifier within a version, `IRM-00001` | Assigned at build, ordered by category, vocabulary, role, term |
| `irae_category_id` | Category code, e.g. `COLITIS`; `ALL` for drug-cause companion codes | `code/categories.py` |
| `irae_category` | Category label | `code/categories.py` |
| `organ_system` | Organ group following the ASCO 2021 irAE guideline | `code/categories.py` |
| `vocabulary` | `CTCAE v6.0`, `ICD-10-CM FY2027`, or `FAERS MedDRA PT` | |
| `code` | CTCAE: MedDRA 28.0 LLT code as printed in CTCAE v6.0. ICD-10-CM: code family with a dot; a trailing `*` means "this code and its billable children listed in the expanded file". FAERS: blank (MedDRA PT codes are not redistributed; see LIMITATIONS 9) | Source files |
| `term` | CTCAE term; ICD-10-CM long description of the family's parent code; FAERS MedDRA preferred term in sentence case | Source files, verbatim except FAERS case |
| `role` | `primary`, `supporting`, `lookalike`, or `companion` (definitions below) | Author decision |
| `confidence` | The author's confidence that the row's role is correct (including that a look-alike is a look-alike). `High` for every released row in v1.0 | Author decision, 2026-10-13 |
| `specificity` | How specific the term or code is to the irAE: `High`, `Moderate`, or `Low` (definitions below); may be blank for look-alikes. **Filter on this column, not on confidence, when selecting codes** | Drafted, accepted by the author |
| `rationale` | One- or two-sentence clinical reason for the role | Author's words, or Claude's draft that the author accepted (see `decision_type`) |
| `lookalike_note` | Diagnoses easily confused with this row, where the author added one | Author |
| `decision_type` | `author decision` (author set the row individually) or `author accepted suggestion` (author accepted the drafted role, specificity and rationale as part of a group decision; see `data/curation/DECISION_LOG.md`) | Review workbook |
| `decided_by`, `decided_on` | Reviewer initials and date (YYYY-MM-DD) | Review workbook |
| `icd_billable_codes_in_family` | Number of billable FY2027 codes in the family | ICD-10-CM order file |
| `ctcae_new_in_v6` | `True` if NCI lists the term as an addition in v6.0 | CTCAE "CTCAE v6.0 Change" column = "Addition: Term" |
| `icd_new_in_fy2027` | `True` if any code in the family was added in FY2027 | ICD-10-CM codes addenda |
| `faers_ici_reports` | Number of FAERS reports naming any of the 13 ICIs that include this reaction term | openFDA; see "FAERS counts" |
| `faers_all_reports` | Number of FAERS reports, any drug, that include this term | openFDA |
| `faers_ici_prr` | `(a / N_ici) / ((b - a) / (N_all - N_ici))` with a = `faers_ici_reports`, b = `faers_all_reports`, N_ici and N_all from `stats.json`. Above 1: over-represented in ICI reports. Descriptive only | Computed |
| `ctcae_grade_1` ... `ctcae_grade_5` | CTCAE v6.0 grade definitions, verbatim; `-` where NCI defines no grade | CTCAE v6.0 |
| `status` | `released` in a published version (`draft (not verified)` or `preview (not author-decided)` in working builds) | Build flag |
| `irae_map_version` | Semantic version of the release | Build |

## `irae_map_icd10cm_expanded.csv`

| Column | Definition |
|---|---|
| `map_id` | Links back to the main table |
| `irae_category_id` | Category |
| `icd10cm_code` | One billable FY2027 code, with dot |
| `code_family` | The family it belongs to (main table `code`) |
| `role`, `confidence`, `specificity` | Inherited from the family's mapping |
| `status`, `irae_map_version` | As above |

## Roles

- **primary**: names the condition itself; enough on its own to identify the irAE category (with a drug-cause code or clinical context for attribution).
- **supporting**: a laboratory, symptom, severity or grading term consistent with the category but not specific to it.
- **lookalike**: a different condition often confused with this one, listed so analysts can exclude it on purpose. Never count a look-alike as the irAE.
- **companion**: an ICD-10-CM drug-cause code (T45.AX5- from 2024-10-01; T45.1X5- before) that should accompany a condition code. Category `ALL`.

## Specificity

- **High**: the term or code names the condition and is used for it in practice.
- **Moderate**: right organ and process, but also used for non-immune causes.
- **Low**: supporting or non-specific.

## How ICD-10-CM code families work

Many conditions have billable children that differ only by site, laterality or encounter (for example M06.0- seronegative rheumatoid arthritis has one code per joint). irAE-Map decides once per family; the family is either a code the category rules named (then every billable code under it), or the remaining billable codes in a three-character block that no named code covered (labeled "remaining codes in this block"). The expanded file lists every billable code exactly, so a user never has to expand wildcards themselves.

## FAERS counts

Counts come from the openFDA drug adverse event endpoint (FAERS data last updated 2026-07-30; accessed 2026-10-13). A report "names an ICI" if any drug in it matches one of the 13 ICIs by openFDA's harmonized generic name, or by the raw product name (generic or brand). Candidate terms were found by keyword searches within those reports; each term's counts are exact (`count_method` in the review workbook: "keyword count" when the keyword query returned the exact term, otherwise "direct count" from a per-term query). The 13 ICIs: pembrolizumab, nivolumab, cemiplimab, dostarlimab, retifanlimab, toripalimab, tislelizumab (PD-1); atezolizumab, durvalumab, avelumab (PD-L1); ipilimumab, tremelimumab (CTLA-4); relatlimab (LAG-3). Brand names: `code/categories.py`.

## How to use the table (example)

To find hospital encounters coded as ICI colitis after 2024-10-01: select `icd10cm_code` from the expanded file where `irae_category_id = COLITIS` and `role = primary`; require a code from category `ALL`, `role = companion` (T45.AX5-) on the same encounter; exclude encounters with a `COLITIS` look-alike code (e.g., A04.7- C. difficile). Choose a `specificity` threshold (High only, or High and Moderate) to trade sensitivity for specificity.
