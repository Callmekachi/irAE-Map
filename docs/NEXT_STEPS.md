# Next steps and roadmap

*Plain-language note: what comes after v1.0, in order, so v1.0 is understood as a first step.*

| Target | Date | What it is | Depends on |
|---|---|---|---|
| irAE-Map v1.0 + codebook and mapping rationale document | December 2026 | The table and its documentation, each with a Zenodo DOI | Author decisions (done 2026-10-13, accepted as a group); verification checklist |
| iraemap v0.1 | March 2027 | Python package that assigns ICD-10-CM codes and FAERS terms to irAE categories using the released table (GitHub + PyPI). Claude writes code and tests; the author verifies outputs against irAE-Map | v1.0 released |
| Coverage analysis dataset | April 2027 | Which CTCAE v6.0 immune-related terms lack a specific ICD-10-CM code (`code/05_coverage.py`), Zenodo DOI. Before release, the author names the single best ICD-10-CM code for each primary CTCAE term so coverage is judged term by term, not by category | v1.0 released; term-level links |
| irAE-Map v2.0 | October 2027 | Realigned to FY2028 ICD-10-CM; diff report of added, deleted and revised codes | CMS/CDC FY2028 code files (usually published in summer, effective October 1) |

Candidate additions raised by the v1.0 data (author decides):
- Categories for immune-mediated cholangitis and gastritis (FAERS: 330 and 182 reports of the immune-mediated terms).
- Re-run the FAERS pull with an openFDA API key (1,000-term cap instead of 100).
- A validation study of the ICD-10-CM code sets against chart review (sensitivity and PPV), for example at UF Health.
- An OMOP concept-set export, linking irAE-Map to the author's OMOP-based irAE data model.
