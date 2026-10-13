# Limitations

*Plain-language note: what irAE-Map can and cannot tell you. Read this before using or citing the table. Each point is specific so a reader can judge whether it matters for their use.*

1. **A code is not a diagnosis of an irAE.** An ICD-10-CM code such as K52.1 (toxic gastroenteritis and colitis) says what the clinician recorded, not that an immune checkpoint inhibitor caused it. Attribution in records usually depends on a companion drug-cause code (T45.AX5- or T45.1X5-), clinical notes, and timing. irAE-Map supplies the code lists; it does not validate them against chart review. Sensitivity and positive predictive value of these code sets in real EHR data are unknown until someone measures them (see NEXT_STEPS).

2. **The drug-cause code changed on 2024-10-01.** T45.AX5- (adverse effect of immune checkpoint inhibitors and immunostimulant drugs) entered ICD-10-CM in FY2025. Before that date, ICI adverse effects were coded with T45.1X5-, which also covers chemotherapy and immunosuppressants. Analyses spanning that date must use both, and T45.1X5- alone cannot separate ICI from chemotherapy toxicity. T45.AX5- also covers "immunostimulant drugs" beyond checkpoint inhibitors.

3. **Many codes are shared with non-immune causes.** Codes rated Moderate or Low confidence (for example E03.9 hypothyroidism, unspecified; K52.9 noninfective colitis, unspecified) are common in patients who never received immunotherapy. Their usefulness depends on the analyst restricting to treated patients and a time window.

4. **FAERS counts are reports, not patients or incidence.** FAERS is a spontaneous reporting system. Counts reflect reporting behavior, duplicates, stimulated reporting after publications and label changes, and missing data. They cannot estimate how often an irAE happens. `ici_prr` compares how often a term appears in reports naming an ICI versus all other reports; it is a descriptive over-representation measure, not a validated disproportionality signal (no confidence interval, no stratification, no deduplication).

5. **openFDA cannot tie the reaction to the ICI within a report.** The query finds reports in which any listed drug is one of the 13 ICIs (by harmonized generic name or by raw product name, generic or brand). It cannot require that the ICI is the *suspect* drug, because openFDA does not match drug-level fields within the same drug record. Some counted reports will list the ICI as a concomitant drug.

6. **openFDA coverage of drug names is incomplete.** On 2026-10-13, openFDA's harmonized generic-name field returned 0 reports for avelumab, tislelizumab and retifanlimab; we added raw product-name matching (generic and brand names) to recover them. Misspelled or foreign product names are still missed.

7. **FAERS candidate terms come from keyword searches capped at 100 terms each** (without an openFDA API key). Rare MedDRA terms outside the top 100 for every keyword can be missed. Re-running `code/01_fetch.py` with `OPENFDA_API_KEY` set raises the cap to 1,000. Report counts for the candidate terms themselves are exact (direct per-term queries where the keyword count was not exact).

8. **Category boundaries are a clinical judgment.** The categories follow the ASCO 2021 irAE guideline's organ groups, with additions. Other groupings (for example combining thyroid categories, or separating cholangitis from hepatitis) are equally defensible. Some terms legitimately map to more than one category (thyroiditis; the myocarditis-myositis-myasthenia overlap).

9. **MedDRA licensing.** CTCAE v6.0 terms and FAERS reaction terms are MedDRA terms. MedDRA is maintained by ICH and licensed through MSSO. irAE-Map republishes term names and the CTCAE LLT codes exactly as they appear in NCI's and FDA's free public releases, and does not redistribute the MedDRA hierarchy or MedDRA PT codes. [VERIFY] Users who need MedDRA codes or hierarchy should obtain a MedDRA license.

10. **ICD-10-CM is US-specific and versioned.** Codes are valid for FY2027 (2026-10-01 to 2027-09-30). Codes added, deleted or revised in later releases require a new irAE-Map version (v2.0 planned for FY2028). Other countries' ICD-10 modifications differ.

11. **CTCAE grade text is copied verbatim.** irAE-Map does not convert grades into code-based rules; ICD-10-CM codes do not carry CTCAE grade except G92.0- (ICANS), which is not an ICI irAE.

12. **Candidates were proposed by rules and drafted with AI assistance.** Search rules, code families and draft rationales were produced by Claude (Anthropic) from the public sources. In v1.0 the author accepted the drafted suggestions as a group and set individual rows where needed (`data/curation/DECISION_LOG.md`); rows without a drafted suggestion are not released. Accepted rows have therefore not each been individually reviewed, and errors in the drafts may remain; please report them through the issue tracker. Rules can still miss relevant codes or terms; the full candidate lists are published so others can check what was considered.
