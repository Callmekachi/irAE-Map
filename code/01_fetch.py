#!/usr/bin/env python3
"""01_fetch.py: download every raw input for irAE-Map and log where it came from.

Plain-language note: this script downloads the three public sources (the NCI
CTCAE v6.0 spreadsheet, the CDC ICD-10-CM FY2027 code list, and openFDA
adverse event reaction counts) into data/raw/, and writes a line for each file
into data/raw/PROVENANCE.txt (file size, fingerprint, web address, date).
You do not need to open this file; run it once with `python code/01_fetch.py`.

Idempotent: files already present are not downloaded again unless --refresh.
"""

import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROV = RAW / "PROVENANCE.txt"

SOURCES = {
    "ctcae-v6.0.xlsx": (
        "https://dctd.cancer.gov/research/ctep-trials/trial-development/ctcae-v6.0.xlsx",
        "Linked from https://dctd.cancer.gov/research/ctep-trials/for-sites/adverse-events (CTCAE section)",
    ),
    "ctcae-v6.pdf": (
        "https://dctd.cancer.gov/research/ctep-trials/for-sites/adverse-events/ctcae-v6.pdf",
        "Human-readable CTCAE v6.0, same page as above",
    ),
    "icd10cm-code-descriptions-2027.zip": (
        "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Publications/ICD10CM/2027/icd10cm-code-descriptions-2027.zip",
        "CDC NCHS ICD-10-CM FY2027 release (effective 2026-10-01); folder listing at .../ICD10CM/2027/",
    ),
    "icd10cm-addenda-2027.zip": (
        "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Publications/ICD10CM/2027/icd10cm-addenda-2027.zip",
        "FY2027 additions/deletions/revisions; used to flag codes new in this release",
    ),
}

OPENFDA = "https://api.fda.gov/drug/event.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from categories import CATEGORIES, ICI_BRANDS, ICI_DRUGS  # noqa: E402
import os  # noqa: E402

API_KEY = os.environ.get("OPENFDA_API_KEY", "")
LIMIT = 1000 if API_KEY else 100


def log(path: Path, url: str, note: str = ""):
    cmd = [sys.executable, str(ROOT / "code" / "provenance.py"), str(path), url, "--log", str(PROV)]
    if note:
        cmd += ["--note", note]
    subprocess.run(cmd, check=True, capture_output=True)


def download(url: str, dest: Path):
    req = urllib.request.Request(url, headers={"User-Agent": "irAE-Map/1.0 (research; contact via GitHub)"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        f.write(r.read())


def _q(search: str) -> str:
    return urllib.parse.quote(search, safe=':"()+')


def _get(url: str) -> dict:
    if API_KEY:
        url += f"&api_key={API_KEY}"
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 404:  # openFDA returns 404 for "no matches"
                return {"results": [], "meta": {"results": {"total": 0}}}
            if attempt == 3:
                raise
            time.sleep(5 * (attempt + 1))
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            if attempt == 3:
                raise
            time.sleep(5 * (attempt + 1))


def openfda_total(search: str) -> int:
    return _get(f"{OPENFDA}?search={_q(search)}&limit=1")["meta"]["results"]["total"]


def openfda_count(search: str, field: str, limit: int = LIMIT) -> dict:
    url = f"{OPENFDA}?search={_q(search)}&count={field}&limit={limit}"
    return {"url": url, "data": _get(url)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    a = ap.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)

    for name, (url, note) in SOURCES.items():
        dest = RAW / name
        if dest.exists() and not a.refresh:
            print(f"have  {name}")
            continue
        print(f"fetch {name}")
        download(url, dest)
        log(dest, url, note)

    # openFDA. For each category keyword, count the exact MedDRA reaction terms
    # (a) in reports that name any of the 13 ICIs and (b) in all reports.
    # The keyword search is on the analyzed reaction field, so it returns
    # every reaction co-reported in matching reports; 02_candidates.py keeps
    # only terms matching the category's regex.
    # Note: openFDA cannot require that the ICI is the *suspect* drug within
    # the same drug record, so (a) is "reports naming an ICI". See LIMITATIONS.
    dest = RAW / "openfda_reactions.json"
    kws_needed = sorted({k for c in CATEGORIES for k in c["faers_kw"]})
    if dest.exists() and not a.refresh:
        out = json.loads(dest.read_text())
        missing = [k for k in kws_needed if k not in out["keywords"]]
        if missing:
            ici = out["ici_search"]
            for kw in missing:
                rx = f'patient.reaction.reactionmeddrapt:"{kw}"'
                r_ici = openfda_count(f"{ici}+AND+{rx}", "patient.reaction.reactionmeddrapt.exact")
                r_all = openfda_count(rx, "patient.reaction.reactionmeddrapt.exact")
                out["keywords"][kw] = {"ici": r_ici["data"]["results"], "all": r_all["data"]["results"],
                                       "ici_url": r_ici["url"], "added": time.strftime("%Y-%m-%d")}
                print(f"  top-up {kw}: {len(r_ici['data']['results'])} ICI terms")
            dest.write_text(json.dumps(out, indent=1))
            log(dest, OPENFDA, f"top-up: added keywords {missing}")
    if not dest.exists() or a.refresh:
        group = "+".join(f'"{d}"' for d in ICI_DRUGS)
        names = "+".join(f'"{d}"' for d in ICI_DRUGS + ICI_BRANDS)
        ici = f"(patient.drug.openfda.generic_name:({group})+patient.drug.medicinalproduct:({names}))"
        out = {"accessed": time.strftime("%Y-%m-%d"), "count_limit": LIMIT,
               "ici_search": ici, "keywords": {}}
        first = _get(f"{OPENFDA}?search={_q(ici)}&limit=1")
        out["openfda_last_updated"] = first["meta"].get("last_updated")
        out["ici_report_total"] = first["meta"]["results"]["total"]
        out["all_report_total"] = openfda_total("_exists_:patient.reaction.reactionmeddrapt")
        out["reports_per_drug"] = {
            d: openfda_total(f'(patient.drug.openfda.generic_name:"{d}"+patient.drug.medicinalproduct:"{d}")')
            for d in ICI_DRUGS}
        kws = sorted({k for c in CATEGORIES for k in c["faers_kw"]})
        for kw in kws:
            rx = f'patient.reaction.reactionmeddrapt:"{kw}"'
            r_ici = openfda_count(f"{ici}+AND+{rx}", "patient.reaction.reactionmeddrapt.exact")
            r_all = openfda_count(rx, "patient.reaction.reactionmeddrapt.exact")
            out["keywords"][kw] = {"ici": r_ici["data"]["results"], "all": r_all["data"]["results"],
                                   "ici_url": r_ici["url"]}
            print(f"  {kw}: {len(r_ici['data']['results'])} ICI terms")
            time.sleep(0.3)
        dest.write_text(json.dumps(out, indent=1))
        log(dest, OPENFDA, f"openFDA drug/event count queries, {len(kws)} keywords x (ICI reports, all reports); query strings stored in file")
        print(f"fetch openfda_reactions.json ({out['ici_report_total']} ICI reports of {out['all_report_total']})")


if __name__ == "__main__":
    main()
