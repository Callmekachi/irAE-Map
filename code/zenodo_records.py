#!/usr/bin/env python3
"""zenodo_records.py: reserve DOIs, upload files, and publish the irAE-Map Zenodo records.

Plain-language note: makes two Zenodo records, one for the dataset (table,
codebook, release archive) and one for the mapping rationale document, each
with a permanent DOI. The token is read from the ZENODO_TOKEN environment
variable only and is never written to any file.

  python code/zenodo_records.py reserve    # create drafts, reserve DOIs -> release/zenodo_ids.json
  python code/zenodo_records.py upload     # set metadata, upload files to the drafts
  python code/zenodo_records.py publish    # publish both drafts (mints the DOIs; permanent)
"""

import json
import os
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
API = "https://zenodo.org/api"
IDS = ROOT / "release" / "zenodo_ids.json"
H = {"Authorization": f"Bearer {os.environ.get('ZENODO_TOKEN', '')}"}
GITHUB = "https://github.com/Callmekachi/irae-map"


def creators():
    a = json.loads((ROOT / "AUTHORS.json").read_text())["authors"]
    return [{"name": f"{x['family']}, {x['given']}", "orcid": x["orcid"], "affiliation": x["affiliation"]} for x in a]


def ok(r):
    if r.status_code >= 400:
        sys.exit(f"Zenodo error {r.status_code}: {r.text[:500]}")
    return r.json()


def reserve():
    if IDS.exists():
        print("already reserved:", IDS.read_text())
        return
    out = {}
    for key in ("dataset", "document"):
        d = ok(requests.post(f"{API}/deposit/depositions", headers=H, json={"metadata": {"prereserve_doi": True}}, timeout=60))
        out[key] = {"id": d["id"], "doi": d["metadata"]["prereserve_doi"]["doi"]}
    IDS.parent.mkdir(exist_ok=True)
    IDS.write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


def metadata(ids):
    stats = json.loads((ROOT / "data" / "processed" / "stats.json").read_text())
    common = dict(creators=creators(), access_right="open", version=stats["version"], language="eng",
                  keywords=["immune-related adverse events", "immune checkpoint inhibitors", "CTCAE",
                            "ICD-10-CM", "FAERS", "MedDRA", "crosswalk", "pharmacovigilance", "phenotyping"],
                  notes="Built with AI assistance (Claude, Anthropic) for code, candidate rules and draft rationales; "
                        "mapping decisions by the author (see DECISION_LOG.md).")
    ds = dict(common, upload_type="dataset", license="cc-by-4.0",
              title=f"irAE-Map v{stats['version']}: a clinician-curated crosswalk of immune-related adverse events "
                    "to CTCAE v6.0, ICD-10-CM FY2027 and FAERS reaction terms",
              description=(
                  f"<p>irAE-Map links {stats['n_categories']} categories of immune-related adverse events (irAEs) of immune "
                  f"checkpoint inhibitor therapy to CTCAE v6.0 terms and grades, ICD-10-CM FY2027 codes and MedDRA "
                  f"reaction terms as reported in the FDA Adverse Event Reporting System (FAERS). Version {stats['version']} "
                  f"contains {stats['n_mappings']:,} mappings ({stats['by_vocabulary'].get('CTCAE v6.0', 0)} CTCAE, "
                  f"{stats['by_vocabulary'].get('ICD-10-CM FY2027', 0)} ICD-10-CM code families covering "
                  f"{stats['n_icd_billable_codes']:,} billable codes, {stats['by_vocabulary'].get('FAERS MedDRA PT', 0)} FAERS "
                  "terms). Each mapping has a role (primary, supporting, look-alike, companion), a specificity rating, the "
                  "author's confidence, a clinical rationale and, for FAERS terms, openFDA report counts. Includes the "
                  "drug-cause companion codes T45.AX5- (from 2024-10-01) and T45.1X5-.</p>"
                  "<p>Sources: NCI CTCAE v6.0; CDC/NCHS ICD-10-CM FY2027; openFDA drug adverse event API "
                  f"(data updated {stats['openfda_last_updated']}, accessed {stats['openfda_accessed']}). "
                  "Read docs/LIMITATIONS.md before use: a code is not a validated irAE diagnosis, and FAERS counts are "
                  "reports, not incidence.</p>"),
              related_identifiers=[
                  {"identifier": GITHUB, "relation": "isSupplementTo", "scheme": "url"},
                  {"identifier": ids["document"]["doi"], "relation": "isDocumentedBy", "scheme": "doi"}])
    doc = dict(common, upload_type="publication", publication_type="technicalnote", license="cc-by-4.0",
               title=f"irAE-Map v{stats['version']}: codebook and mapping rationale",
               description=("<p>Codebook and mapping rationale for irAE-Map, a clinician-curated crosswalk of "
                            "immune-related adverse events of immune checkpoint inhibitor therapy to CTCAE v6.0, "
                            "ICD-10-CM FY2027 and FAERS reaction terms. Describes sources, candidate generation, the "
                            "author's decision process, quality checks, results, per-category rationale with look-alike "
                            "diagnoses, the 2024 drug-cause code change, limitations and AI assistance.</p>"),
               related_identifiers=[
                   {"identifier": ids["dataset"]["doi"], "relation": "documents", "scheme": "doi"},
                   {"identifier": GITHUB, "relation": "isSupplementTo", "scheme": "url"}])
    return {"dataset": ds, "document": doc}


FILES = {
    "dataset": ["release/irae-map-v1.0.0.zip", "data/processed/irae_map_v1.0.csv",
                "data/processed/irae_map_icd10cm_expanded.csv", "data/processed/irae_categories.csv",
                "docs/CODEBOOK.md", "docs/LIMITATIONS.md", "README.md"],
    "document": ["report/irAE-Map_mapping_rationale_v1.0.pdf", "report/irAE-Map_mapping_rationale_v1.0.docx"],
}


def upload():
    ids = json.loads(IDS.read_text())
    md = metadata(ids)
    for key in ("dataset", "document"):
        dep = ok(requests.get(f"{API}/deposit/depositions/{ids[key]['id']}", headers=H, timeout=60))
        meta = dict(md[key], prereserve_doi=True)
        ok(requests.put(f"{API}/deposit/depositions/{ids[key]['id']}", headers=H, json={"metadata": meta}, timeout=60))
        have = {f["filename"]: f["id"] for f in dep.get("files", [])}
        for rel in FILES[key]:
            p = ROOT / rel
            if p.name in have:
                requests.delete(f"{API}/deposit/depositions/{ids[key]['id']}/files/{have[p.name]}", headers=H, timeout=60)
            with open(p, "rb") as fh:
                r = requests.put(f"{dep['links']['bucket']}/{p.name}", data=fh, headers=H, timeout=600)
            ok(r)
            print(f"  {key}: uploaded {p.name} ({p.stat().st_size:,} bytes)")
        print(f"{key}: draft ready at https://zenodo.org/deposit/{ids[key]['id']} (DOI {ids[key]['doi']})")


def publish():
    ids = json.loads(IDS.read_text())
    for key in ("document", "dataset"):
        d = ok(requests.post(f"{API}/deposit/depositions/{ids[key]['id']}/actions/publish", headers=H, timeout=120))
        ids[key]["record_url"] = d["links"].get("record_html") or d["links"].get("html")
        print(f"{key}: published {d['doi']} -> {ids[key]['record_url']}")
    IDS.write_text(json.dumps(ids, indent=1))


if __name__ == "__main__":
    {"reserve": reserve, "upload": upload, "publish": publish}[sys.argv[1]]()
