# Glossary

Plain definitions of the terms you will see in this project. Copy this file into each project as `docs/GLOSSARY.md`.

**Abstract.** A short summary at the top of a paper, usually 150 to 300 words.

**Archive (release archive).** A single zip file containing a frozen copy of the whole project at one point in time.

**arXiv, medRxiv, bioRxiv, engrXiv.** Free public websites where researchers post papers before or alongside journal review. Each covers different fields.

**Citation file (CITATION.cff).** A small file that tells people and software exactly how to cite your project.

**Codebook.** A list explaining every column in your data: what it means, its units, and where it came from.

**Commit.** A saved snapshot of changes to the project, with a note describing what changed.

**Dataset.** An organized table (or set of tables) of information, like a spreadsheet.

**Docket.** The public file for a proposed government rule. Comments submitted to it become part of the official record.

**DOI (Digital Object Identifier).** A permanent link and ID for your work, like a library call number that never changes. It looks like `10.5281/zenodo.1234567`.

**Draft stamp.** A "draft" label on every figure and document until you have checked everything. It is removed only after your approval.

**Endorsement (arXiv).** A one-time approval some arXiv categories require from an existing author before your first post there.

**Figure.** A chart, graph, or map in a paper or report.

**GitHub.** A website that stores project files publicly and keeps every past version.

**License.** The terms under which others may reuse your work. CC BY 4.0 means anyone can reuse it if they credit you. MIT is a common equivalent for code.

**Limitations.** An honest list of what the project cannot tell you and where its data is weak. Every credible project has one.

**Metadata.** Information about your work: title, authors, description, keywords, license.

**Open data.** Information published free for anyone to use, usually by governments or research bodies.

**ORCID iD.** A free, permanent ID number for researchers, so your work is linked to you even if your name is spelled differently somewhere. It looks like `0000-0002-1825-0097`.

**Pipeline.** The set of scripts that downloads the data, cleans it, and produces the results, in order. Running it again gives the same results.

**Preprint.** A paper posted publicly before peer review.

**Provenance.** A record of exactly where each piece of data came from and when it was downloaded.

**Public comment.** Written feedback submitted to a government agency on a proposed rule, during a set comment period.

**QA (quality assurance) report.** A file listing the checks run on the data: counts, matches, and anything unusual.

**README.** The front page of a project. It explains what the project is and how to use it.

**Release.** A named, frozen version of the project (for example v1.0) that can be cited.

**Reproduce.** To re-run the project from scratch and get the same numbers. It proves the results are real.

**Repository (repo).** The project folder that lives online, usually on GitHub, with its full history.

**Sandbox.** A practice version of a website (like Zenodo's) for testing before doing it for real.

**Script.** A small program file that does one job, such as downloading data.

**Spot check.** Picking a few rows by hand and comparing them to the original source.

**Stats file.** A file the pipeline writes with every number used in the paper, so the text always matches the data.

**Token.** A temporary password that lets Claude upload to GitHub or Zenodo on your behalf. You can cancel it at any time.

**Tracking number.** The receipt ID you get after submitting a public comment. Save it.

**Vintage.** The year or edition of a data source.

**Zenodo.** A free, permanent research archive run by CERN. It gives your project a DOI.

## Terms specific to irAE-Map

**Code family.** A diagnosis code plus its more detailed child codes, which usually differ only by body site, side, or visit type. You decide once per family; the published file lists every child code.
**Companion code.** A second diagnosis code that says a drug caused the condition. For immunotherapy, T45.AX5- (since October 1, 2024) or T45.1X5- (before).
**Crosswalk.** A table that links the same idea across different coding systems, like a translation dictionary.
**CTCAE (Common Terminology Criteria for Adverse Events).** The National Cancer Institute's list of side-effect names and how to grade their severity from 1 (mild) to 5 (death). Version 6.0 was released in 2026.
**FAERS (FDA Adverse Event Reporting System).** The FDA's database of side-effect reports sent in by doctors, patients and drug companies. openFDA is the free public website for searching it.
**ICD-10-CM.** The US list of diagnosis codes used in medical records and billing. It is updated every October 1; the current edition is called FY2027.
**Immune checkpoint inhibitor (ICI).** A type of immunotherapy drug (for example pembrolizumab or nivolumab) that releases the brakes on the immune system so it attacks cancer.
**irAE (immune-related adverse event).** A side effect of an ICI in which the immune system attacks a healthy organ.
**Look-alike.** A different condition that is easily mistaken for the side effect (for example an infection that looks like immune colitis). Listed so analysts can rule it out.
**MedDRA.** The medical dictionary of side-effect terms used by drug regulators and by CTCAE. It is licensed, so irAE-Map publishes term names only, not its internal codes.
**PRR (proportional reporting ratio).** How much more often a side effect is reported with a drug than with all other drugs. Above 1 means over-represented. It does not measure how often the side effect happens.
**Role.** What a code does in the table: primary (names the condition), supporting (a symptom or lab result), look-alike (something to rule out), or companion (the drug-cause code).
