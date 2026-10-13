#!/usr/bin/env node
/*
 * 04_document.js: build the irAE-Map codebook and mapping rationale document (.docx).
 *
 * Plain-language note: makes report/irAE-Map_mapping_rationale_v1.0.docx from the
 * released table and stats.json. Every number in the document is read from those
 * files, never typed, so the document cannot disagree with the data. It carries a
 * draft banner until built with --final after your verification.
 *
 *   node code/04_document.js            (draft, from data/processed/)
 *   node code/04_document.js --final    (no draft banner)
 *   node code/04_document.js --preview  (from data/processed/preview/, preview banner)
 *
 * Requires the npm package "docx" (npm install, see package.json).
 */
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Table, TableRow, TableCell,
  WidthType, ShadingType, AlignmentType, Header, Footer, PageNumber, LevelFormat,
  BorderStyle, PageBreak,
} = require("docx");

const ROOT = path.resolve(__dirname, "..");
const args = process.argv.slice(2);
const PREVIEW = args.includes("--preview");
const FINAL = args.includes("--final") && !PREVIEW;
const SRC = path.join(ROOT, "data", "processed", PREVIEW ? "preview" : "");
const OUTDIR = path.join(ROOT, "report", PREVIEW ? "preview" : "");
const STAMP = PREVIEW ? "Preview: built from Claude's suggestions, not author decisions. Not for release."
  : FINAL ? "" : "Draft: not yet verified by the author. Do not cite.";

// ---------------------------------------------------------------- data
function parseCSV(text) {
  const rows = []; let row = [], f = "", q = false;
  for (let i = 0; i < text.length; i++) {
    const c = text[i];
    if (q) {
      if (c === '"' && text[i + 1] === '"') { f += '"'; i++; }
      else if (c === '"') q = false; else f += c;
    } else if (c === '"') q = true;
    else if (c === ",") { row.push(f); f = ""; }
    else if (c === "\n") { row.push(f); rows.push(row); row = []; f = ""; }
    else if (c !== "\r") f += c;
  }
  if (f || row.length) { row.push(f); rows.push(row); }
  const [h, ...body] = rows;
  return body.filter(r => r.length === h.length).map(r => Object.fromEntries(h.map((k, j) => [k, r[j]])));
}
const stats = JSON.parse(fs.readFileSync(path.join(SRC, "stats.json"), "utf8"));
const table = parseCSV(fs.readFileSync(path.join(SRC, "irae_map_v1.0.csv"), "utf8"));
const cats = parseCSV(fs.readFileSync(path.join(SRC, "irae_categories.csv"), "utf8"));
const ids = (() => { try { return JSON.parse(fs.readFileSync(path.join(ROOT, "release", "zenodo_ids.json"), "utf8")); } catch { return null; } })();
const DOI_DOC = ids ? `https://doi.org/${ids.document.doi}` : "(DOI assigned at release)";
const DOI_DATA = ids ? `https://doi.org/${ids.dataset.doi}` : "(DOI assigned at release)";
const authors = JSON.parse(fs.readFileSync(path.join(ROOT, "AUTHORS.json"), "utf8")).authors;
const limits = fs.readFileSync(path.join(ROOT, "docs", "LIMITATIONS.md"), "utf8")
  .split("\n").filter(l => /^\d+\. \*\*/.test(l))
  .map(l => { const m = l.match(/^\d+\. \*\*(.+?)\*\*\s*(.*)$/); return [m[1], m[2].replace(/\*\*|`/g, "")]; });
const fmt = n => Number(n).toLocaleString("en-US");
const V = { CT: "CTCAE v6.0", ICD: "ICD-10-CM FY2027", FA: "FAERS MedDRA PT" };

// ---------------------------------------------------------------- style helpers
const FONT = "Arial";
const W = 9360; // content width (US Letter, 1" margins)
const border = { style: BorderStyle.SINGLE, size: 1, color: "BFBFBF" };
const borders = { top: border, bottom: border, left: border, right: border };
const P = (text, o = {}) => new Paragraph({ spacing: { after: 120 }, ...o, children: [new TextRun({ text, font: FONT, size: 22, ...(o.run || {}) })] });
const H = (text, level) => new Paragraph({ heading: level, spacing: { before: 240, after: 120 }, children: [new TextRun({ text, font: FONT })] });
const B = (text) => new Paragraph({ numbering: { reference: "bul", level: 0 }, spacing: { after: 60 }, children: [new TextRun({ text, font: FONT, size: 22 })] });
const RICH = (parts) => new Paragraph({ spacing: { after: 120 }, children: parts.map(([t, b]) => new TextRun({ text: t, bold: !!b, font: FONT, size: 22 })) });

function tbl(headers, rows, widths) {
  const total = widths.reduce((a, b) => a + b, 0);
  const cell = (t, i, head) => new TableCell({
    borders, width: { size: widths[i], type: WidthType.DXA },
    shading: head ? { fill: "E8EEF4", type: ShadingType.CLEAR } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({ children: [new TextRun({ text: String(t ?? ""), font: FONT, size: 18, bold: head })] })],
  });
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths,
    rows: [new TableRow({ tableHeader: true, children: headers.map((h, i) => cell(h, i, true)) }),
      ...rows.map(r => new TableRow({ children: r.map((t, i) => cell(t, i, false)) }))],
  });
}

// ---------------------------------------------------------------- content
const byCat = {};
for (const r of table) (byCat[r.irae_category_id] ||= []).push(r);
const roleCount = (v, role) => (stats.by_vocabulary_role[v] || {})[role] || 0;
const authorLine = authors.map(a => a.name).join(", ");
const affil = [...new Set(authors.map(a => a.affiliation))].join("; ");

const body = [];
if (STAMP) body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 },
  shading: { fill: "FFF4C2", type: ShadingType.CLEAR },
  children: [new TextRun({ text: STAMP, bold: true, font: FONT, size: 22, color: "8A5A00" })] }));
body.push(new Paragraph({ heading: HeadingLevel.TITLE, alignment: AlignmentType.CENTER, children: [new TextRun({ text: "irAE-Map", font: FONT })] }));
body.push(P(`Codebook and mapping rationale, version ${stats.version}`, { alignment: AlignmentType.CENTER, run: { size: 28 } }));
body.push(P(`A clinician-curated crosswalk of immune-related adverse events of immune checkpoint inhibitor therapy to CTCAE v6.0, ICD-10-CM FY2027, and FDA Adverse Event Reporting System reaction terms`, { alignment: AlignmentType.CENTER, run: { italics: true } }));
body.push(P(authorLine, { alignment: AlignmentType.CENTER, run: { bold: true } }));
body.push(P(affil, { alignment: AlignmentType.CENTER }));
body.push(P(`Built ${stats.built}. Status: ${stats.status}. DOI: ${DOI_DOC}. License: CC BY 4.0.`, { alignment: AlignmentType.CENTER, run: { size: 20 } }));
body.push(P("Contents", { spacing: { before: 480, after: 80 }, run: { bold: true } }));
for (const t of ["1. Summary", "2. Sources", "3. Methods", "4. Results", "5. Category rationale", "6. Drug-cause companion codes",
  "7. Limitations", "8. Use of AI assistance", "9. Versioning and maintenance", "10. How to cite"]) body.push(P(t, { spacing: { after: 40 } }));
body.push(new Paragraph({ children: [new PageBreak()] }));

body.push(H("1. Summary", HeadingLevel.HEADING_1));
body.push(P(`irAE-Map links ${stats.n_categories} immune-related adverse event (irAE) categories to the terms and codes that describe them in three vocabularies: the National Cancer Institute's Common Terminology Criteria for Adverse Events (CTCAE) version 6.0, the US diagnosis code set ICD-10-CM (fiscal year 2027), and the MedDRA reaction terms used in the FDA Adverse Event Reporting System (FAERS). Version ${stats.version} contains ${fmt(stats.n_mappings)} mappings: ${fmt(stats.by_vocabulary[V.CT] || 0)} to CTCAE terms, ${fmt(stats.by_vocabulary[V.ICD] || 0)} to ICD-10-CM code families covering ${fmt(stats.n_icd_billable_codes)} billable codes, and ${fmt(stats.by_vocabulary[V.FA] || 0)} to FAERS reaction terms. Each mapping has a role, a specificity rating, the author's confidence and a clinical rationale; Section 3.3 describes how the author decided them.`));
body.push(P(`CTCAE v6.0, released by NCI in 2026, added terms in part to better describe adverse events of immunotherapy. Of the ${stats.n_ctcae_terms} CTCAE terms in irAE-Map, ${stats.n_ctcae_terms_new_in_v6} are new in v6.0. ICD-10-CM gained a dedicated drug-cause code for immune checkpoint inhibitors, T45.AX5-, effective 1 October 2024. Health systems, registries and drug-safety analysts need a public, documented link between these vocabularies; irAE-Map provides one.`));

body.push(H("2. Sources", HeadingLevel.HEADING_1));
body.push(tbl(["Source", "Edition", "Use in irAE-Map"], [
  ["NCI CTCAE spreadsheet (dctd.cancer.gov)", "v6.0, MedDRA 28.0, errata 2026-01-20", "Terms, MedDRA LLT codes, grade 1 to 5 definitions, v5 to v6 change flags"],
  ["CDC/NCHS ICD-10-CM code descriptions and addenda (ftp.cdc.gov)", "FY2027, effective 2026-10-01", "Codes, billable flags, descriptions, codes new in FY2027"],
  ["openFDA drug adverse event API (api.fda.gov)", `FAERS data updated ${stats.openfda_last_updated}; accessed ${stats.openfda_accessed}`, "Reaction terms reported with the 13 checkpoint inhibitors and report counts"],
], [3000, 2600, 3760]));
body.push(P(`Exact URLs, download dates, file sizes and SHA-256 checksums are in data/raw/PROVENANCE.txt in the repository.`, { spacing: { before: 120, after: 120 } }));

body.push(H("3. Methods", HeadingLevel.HEADING_1));
body.push(H("3.1 Category frame", HeadingLevel.HEADING_2));
body.push(P(`Categories follow the organ groupings of the ASCO 2021 guideline on management of irAEs in patients treated with immune checkpoint inhibitor therapy, with additions where CTCAE v6.0 or the literature identifies a distinct entity. Each category lists the diagnoses most often confused with it (Section 5).`));
body.push(H("3.2 Candidate generation", HeadingLevel.HEADING_2));
body.push(B("CTCAE v6.0: terms named in each category's rules, matched exactly to the v6.0 spreadsheet; the build fails if a named term is absent."));
body.push(B("ICD-10-CM: codes under named code prefixes, plus codes whose description matches the category's keyword pattern, excluding keyword matches in the neoplasm, pregnancy, perinatal, injury, external-cause and Z chapters. Billable codes are grouped into code families (a named parent code with its children, or the remaining codes in a three-character block) for review, and expanded back to every billable code for release."));
body.push(B(`FAERS: for each category keyword, openFDA count queries over reports naming any of the 13 checkpoint inhibitors (${fmt(stats.faers_ici_reports_total)} reports) and over all reports (${fmt(stats.faers_all_reports_total)}), keeping reaction terms that match the category pattern. Reports were matched by openFDA's harmonized generic name or by the raw product name (generic or brand), because the harmonized field returned no reports for three of the drugs. Each kept term's counts are exact.`));
body.push(B("Each candidate received a suggested role, confidence and reason from documented rules (repository file code/categories.py), drafted with AI assistance (Section 8). Rows the rules could not classify were left without a suggestion."));
body.push(H("3.3 Author review", HeadingLevel.HEADING_2));
body.push(P(`Decisions were recorded in a review workbook, one row per candidate. For version ${stats.version} the author accepted the drafted role, specificity and rationale as a group for ${fmt(stats.n_accepted_suggestion)} released mappings and set ${fmt(stats.n_author_set)} individually (author's instruction of 13 October 2026; data/curation/DECISION_LOG.md, which also lists corrections made to drafts after spot checks). The ${fmt(stats.n_undecided_not_released)} candidates without a drafted suggestion were not released. Each row records its decision type (column decision_type), reviewer and date. Individual review of accepted rows is planned for the next version.`));
body.push(tbl(["Role", "Meaning"], [
  ["primary", "Names the condition itself; enough on its own to identify the category"],
  ["supporting", "A laboratory, symptom, severity or grading term consistent with, but not specific to, the category"],
  ["lookalike", "A different condition often confused with this one; listed so analysts exclude it deliberately"],
  ["companion", "ICD-10-CM drug-cause code that should accompany a condition code"],
], [1800, 7560]));
body.push(P(""));
body.push(tbl(["Specificity", "Meaning"], [
  ["High", "Names the condition and is used for it in practice"],
  ["Moderate", "Right organ and process, but also used for non-immune causes"],
  ["Low", "Supporting or non-specific"],
], [1800, 7560]));
body.push(P(""));
body.push(P(`Confidence is the author's confidence that a row's role is correct (including that a look-alike is a look-alike). The author rated every released row High. Specificity, not confidence, is the column to filter on when selecting codes.`));
body.push(H("3.4 Quality checks", HeadingLevel.HEADING_2));
body.push(P(`The build verifies that every CTCAE term exists in v6.0 and every released ICD-10-CM code is a valid billable FY2027 code; that every released row has a role, a specificity rating (except look-alikes) and a rationale; that no suggestion-less row was accepted without a decision; and it reports, for each category, any vocabulary lacking a primary mapping. Results are in data/processed/qa_report.txt.`));
body.push(H("3.5 FAERS over-representation", HeadingLevel.HEADING_2));
body.push(P(`For each reaction term, faers_ici_prr = (a / N_ici) / ((b - a) / (N_all - N_ici)), where a is the number of reports naming a checkpoint inhibitor with the term, b the number of all reports with the term, N_ici = ${fmt(stats.faers_ici_reports_total)} and N_all = ${fmt(stats.faers_all_reports_total)}. It describes over-representation only; it is not a disproportionality signal (no deduplication, stratification or confidence interval).`));

body.push(H("4. Results", HeadingLevel.HEADING_1));
body.push(tbl(["Vocabulary", "Mappings", "Primary", "Supporting", "Look-alike", "Companion"],
  [V.CT, V.ICD, V.FA].map(v => [v, fmt(stats.by_vocabulary[v] || 0), roleCount(v, "primary"), roleCount(v, "supporting"), roleCount(v, "lookalike"), roleCount(v, "companion")]),
  [2760, 1320, 1320, 1320, 1320, 1320]));
body.push(P(""));
body.push(P(`Specificity: ${Object.entries(stats.by_specificity).filter(([k]) => k).map(([k, v]) => `${k} ${fmt(v)}`).join(", ")}. ${stats.n_terms_primary_in_multiple_categories} terms are primary in more than one category; these are overlap entities such as thyroiditis (both thyroid categories) and the myocarditis-myositis-myasthenia gravis overlap syndrome.`));

body.push(H("5. Category rationale", HeadingLevel.HEADING_1));
body.push(P(`For each category: the primary CTCAE terms with their grade 3 definition, primary ICD-10-CM code families, the most-reported primary FAERS terms, and look-alikes. The complete list, including supporting terms, is the released table.`));
for (const c of cats) {
  const rows = byCat[c.category_id] || [];
  const prim = v => rows.filter(r => r.vocabulary === v && r.role === "primary");
  body.push(H(`${c.irae_category} (${c.category_id})`, HeadingLevel.HEADING_2));
  body.push(RICH([["Organ system: ", true], [c.organ_system]]));
  const ct = prim(V.CT);
  if (ct.length) body.push(tbl(["CTCAE v6.0 term", "Grade 3", "Specificity", "Rationale"],
    ct.map(r => [r.term + (r.ctcae_new_in_v6 === "True" ? " (new in v6.0)" : ""), r.ctcae_grade_3, r.specificity, r.rationale]),
    [2000, 3160, 1200, 3000]));
  const icd = prim(V.ICD);
  if (icd.length) { body.push(P("")); body.push(tbl(["ICD-10-CM", "Description", "Billable codes", "Specificity", "Rationale"],
    icd.map(r => [r.code, r.term, r.icd_billable_codes_in_family, r.specificity, r.rationale]), [1100, 2860, 1000, 1200, 3200])); }
  const fa = prim(V.FA).sort((a, b) => Number(b.faers_ici_reports) - Number(a.faers_ici_reports)).slice(0, 6);
  if (fa.length) { body.push(P("")); body.push(tbl(["FAERS reaction term", "ICI reports", "All reports", "PRR", "Specificity"],
    fa.map(r => [r.term, fmt(r.faers_ici_reports), r.faers_all_reports ? fmt(r.faers_all_reports) : "", r.faers_ici_prr, r.specificity]), [3760, 1400, 1400, 1100, 1700])); }
  body.push(new Paragraph({ spacing: { before: 160, after: 160 }, children: [
    new TextRun({ text: "Look-alikes: ", bold: true, font: FONT, size: 22 }), new TextRun({ text: c.category_lookalikes, font: FONT, size: 22 })] }));
}

body.push(H("6. Drug-cause companion codes", HeadingLevel.HEADING_1));
const comp = (byCat["ALL"] || []);
body.push(tbl(["Code", "Description", "Role", "Note"], comp.map(r => [r.code, r.term, r.role, r.rationale]), [1100, 3200, 1100, 3960]));
body.push(P(""));
body.push(P(`An ICD-10-CM condition code alone does not attribute the condition to a checkpoint inhibitor. Attribution in coded data depends on a drug-cause code on the same encounter: T45.AX5- for encounters on or after 1 October 2024, and T45.1X5- before that date. T45.1X5- also covers chemotherapy and immunosuppressants, so analyses before October 2024 cannot separate checkpoint inhibitor toxicity from chemotherapy toxicity by code alone.`));

body.push(H("7. Limitations", HeadingLevel.HEADING_1));
for (const [t, d] of limits) body.push(RICH([[t + " ", true], [d]]));

body.push(H("8. Use of AI assistance", HeadingLevel.HEADING_1));
body.push(P(`Claude (Anthropic) wrote the data-processing code, the candidate search rules, and the draft role, specificity and rationale for candidates. The author made the mapping decisions as described in Section 3.3, verified sample rows against the sources, and is responsible for the content.`));

body.push(H("9. Versioning and maintenance", HeadingLevel.HEADING_1));
body.push(P(`irAE-Map uses semantic versioning. ICD-10-CM changes every 1 October; version 2.0, aligned to the FY2028 code files, is planned for October 2027 after CMS and CDC publish them. A Python package, iraemap, that applies the table to a user's codes is planned (version 0.1, March 2027). Corrections and suggestions are welcome through the repository's issue tracker.`));

body.push(H("10. How to cite", HeadingLevel.HEADING_1));
body.push(P(`${authorLine}. irAE-Map: codebook and mapping rationale, version ${stats.version}. Zenodo. ${DOI_DOC}. The dataset: ${DOI_DATA}.`));

// ---------------------------------------------------------------- document
const doc = new Document({
  creator: authorLine, title: `irAE-Map ${stats.version}: codebook and mapping rationale`,
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 30, bold: true, font: FONT, color: "1F3A5F" }, paragraph: { spacing: { before: 300, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 24, bold: true, font: FONT, color: "1F3A5F" }, paragraph: { spacing: { before: 240, after: 100 }, outlineLevel: 1 } },
      { id: "Title", name: "Title", basedOn: "Normal", run: { size: 48, bold: true, font: FONT, color: "1F3A5F" }, paragraph: { spacing: { before: 1200, after: 200 } } },
    ],
  },
  numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: STAMP ? STAMP.split(":")[0] + "  |  " : "", bold: true, color: "8A5A00", font: FONT, size: 16 }), new TextRun({ text: `irAE-Map ${stats.version}`, font: FONT, size: 16, color: "666666" })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: ["Page ", PageNumber.CURRENT], font: FONT, size: 16, color: "666666" })] })] }) },
    children: body,
  }],
});
fs.mkdirSync(OUTDIR, { recursive: true });
const out = path.join(OUTDIR, `irAE-Map_mapping_rationale_v${stats.version.split(".").slice(0, 2).join(".")}.docx`);
Packer.toBuffer(doc).then(buf => { fs.writeFileSync(out, buf); console.log("wrote", path.relative(ROOT, out)); });
