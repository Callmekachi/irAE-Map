# Decision log

*Plain-language note: a dated record of the author's instructions that shaped the review workbook, so anyone auditing the table can see how decisions were made.*

## 2026-10-13, Onyekachi Innocent Ike-Okpe

- **Review method (option B):** accept every drafted suggestion (role, confidence, rationale) unchanged. Recorded in the workbook as `author_role = accept`, `decided_by = O. I. Ike-Okpe`, `decided_on = 2026-10-13`. Released rows show `decision_type = author accepted suggestion`.
- **Rows without a suggestion** (proposed_role = review): no decision given, so not released in v1.0. Count at time of decision: 132 ICD-10-CM families and 33 FAERS terms. They remain in the workbook for a later version.
- **E27.1 Primary adrenocortical insufficiency** (ADRENAL_INSUFFICIENCY): author set confidence to **High** (suggestion was Moderate). Recorded as an author decision.
- **Setup questions 1 to 3: defaults.** Keep the 36 categories (no cholangitis or gastritis category in v1.0); companion codes T45.AX5- from 2024-10-01 and T45.1X5- before, symptom codes supporting only; 13 checkpoint inhibitors.
- **Question 4 (confidence scale):** author clarified that confidence is High for all rows. Author chose (option 1) to publish two columns: `confidence` = High for every released row (the author's confidence that each row's role is correct), and `specificity` = the drafted High / Moderate / Low rating of how specific a code is to the irAE. E27.1 specificity also set to High.
- **Question 5:** author details as above; affiliation "Independent Researcher". Licenses not specified, so defaults: CC BY 4.0 (table, documents), MIT (code).

## 2026-10-13, corrections to drafted suggestions after the author's blanket acceptance

Found by Claude's spot checks of the first build. Because the author's instruction was "accept the suggestions", rows marked `accept` now resolve to the corrected suggestions below. The author confirmed on 2026-10-13 that everything had been cross-checked and approved publishing.

- **Infection and tumor terms checked first.** A broad category pattern had marked four infectious FAERS terms as primary for ENCEPHALITIS: meningoencephalitis bacterial, viral, herpetic, and herpes zoster meningoencephalitis. They are now look-alikes. "Pulmonary tumour thrombotic microangiopathy" (TMA) is now a look-alike (tumor-related).
- **DIABETES:** Diabetes insipidus is a look-alike (pituitary). Diabetes mellitus inadequate control is supporting, Low. Euglycaemic diabetic ketoacidosis is a look-alike (SGLT2 inhibitors).
- **OPTIC_NEURITIS:** Toxic optic neuropathy (FAERS) is a look-alike, matching ICD-10-CM H46.3.
- **DERM_SCAR:** Palmoplantar pustulosis is a look-alike (psoriasis variant).
- **APLASTIC_ANEMIA:** Febrile bone marrow aplasia is a look-alike (chemotherapy).
- **AIHA:** Haemolysis is supporting, Moderate. **DERM_INFLAMMATORY:** Lichenoid keratosis is supporting, Low.
- **ENCEPHALITIS / MYELITIS:** G04.89 Other myelitis moved from an ENCEPHALITIS primary to a MYELITIS primary (look-alike under ENCEPHALITIS). G04.02 Postimmunization ADEM is a look-alike.
- **Rationales rewritten** from short labels (552 of 916 were under 30 characters, e.g. "Core terms") into full sentences. Each now says what the item is, its role for the category, and, for FAERS terms, how many reports name a checkpoint inhibitor.
- **Accept applied to two rows** that gained a suggestion through these fixes: ICD-10-CM MYELITIS G04.89 and FAERS HEPATITIS "Cholangitis infective" (look-alike).
