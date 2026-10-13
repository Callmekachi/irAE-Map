# Talking about irAE-Map

*Plain-language note: what to say when someone asks about this project. Every number matches `data/processed/stats.json`.*

## 60-second version

**The problem:** Immunotherapy drugs called checkpoint inhibitors can make the immune system attack healthy organs: the bowel, liver, lungs, thyroid, heart and more. The same side effect is written down three different ways: cancer trials use CTCAE terms, hospitals use ICD-10-CM codes, and the FDA's safety database uses MedDRA terms. There was no public, documented table linking them, so every hospital and research team built its own.

**What I built:** irAE-Map, a free, open crosswalk. It links 36 kinds of immunotherapy side effects to CTCAE v6.0 terms, ICD-10-CM codes and FDA reaction terms: 918 mappings covering 1,939 billable diagnosis codes. Each link says whether the code names the condition, supports it, or is a look-alike to rule out, with a reason.

**What it makes possible:** Health systems, registries and drug-safety analysts can find immunotherapy side effects in records and reports the same way, and compare results. It also documents that since October 2024 ICD-10-CM has a dedicated drug-cause code for checkpoint inhibitors (T45.AX5-).

**Who can use it:** EHR and claims researchers, cancer registries, pharmacovigilance teams, clinical informatics groups.

**Where it is:** github.com/Callmekachi/irAE-Map; dataset DOI 10.5281/zenodo.23351502; documentation DOI 10.5281/zenodo.23351504.

## Two-sentence version

I built irAE-Map, an open, versioned crosswalk that links immunotherapy side effects to the CTCAE v6.0 grading terms, ICD-10-CM diagnosis codes and FDA adverse-event terms used to record them. It gives health systems and drug-safety analysts a public, documented way to find these side effects consistently in records and reports.

## Questions you may be asked

1. **Where does the data come from?** Three free government sources: NCI's CTCAE v6.0, the CDC's ICD-10-CM FY2027 code files, and the FDA's adverse-event database through openFDA. Every download is logged with its date and checksum.
2. **What are its limits?** A diagnosis code is not a confirmed side effect; the code sets have not yet been validated against chart review. FDA reports show what was reported, not how often it happens. The candidate mappings and draft reasons were produced with AI assistance and I decided them, accepting the drafted suggestions as a group for this first version; rows with no draft were left out.
3. **Why does it matter?** Immunotherapy use is growing fast, and NCI revised CTCAE in 2026 partly to describe these side effects better. Without a shared, public definition, studies and safety signals cannot be compared across institutions.
