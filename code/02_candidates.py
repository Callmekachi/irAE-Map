#!/usr/bin/env python3
"""02_candidates.py: propose candidate mappings for every irAE category.

Plain-language note: this script reads the three downloaded sources and, using
the rules in code/categories.py, lists every CTCAE term, ICD-10-CM code, and
FDA reaction term that might belong to each side-effect category. Each row
gets a SUGGESTED role, confidence, and reason, and empty columns for
Onyekachi's decision. Output: data/curation/candidates_*.csv and the review
workbook data/curation/irAE-Map_review.xlsx. You do not need to open this
script; you will work in the workbook.

Re-running this script never overwrites decisions: if a review workbook
already exists, author_* columns are carried over by (category, source, id).
"""

import json
import re
import sys
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
from categories import CATEGORIES, COMPANION_CODES, FAERS_EXTRA, FAERS_FIRST, FAERS_GENERIC  # noqa: E402

RAW = ROOT / "data" / "raw"
CUR = ROOT / "data" / "curation"
CUR.mkdir(parents=True, exist_ok=True)

AUTHOR_COLS = ["author_role", "author_confidence", "author_rationale", "author_lookalike_note",
               "decided_by", "decided_on"]


# --------------------------------------------------------------- loaders
def load_ctcae() -> pd.DataFrame:
    df = pd.read_excel(RAW / "ctcae-v6.0.xlsx", sheet_name="CTCAE v6.0 Clean Copy", dtype=str)
    df.columns = [re.sub(r"\s+", " ", c.replace("\xa0", " ")).strip() for c in df.columns]
    df = df.rename(columns={
        "CTCAE v6.0 MedDRA 28.0 LLT Code": "meddra_llt_code",
        "CTCAE v6.0 MedDRA 28.0 SOC": "soc",
        "CTCAE v6.0 MedDRA 28.0 Term": "ctcae_term",
        "Grade 1": "grade_1", "Grade 2": "grade_2", "Grade 3": "grade_3",
        "Grade 4": "grade_4", "Grade 5": "grade_5",
        "Definition": "definition", "Navigational Note": "navigational_note",
        "CTCAE v6.0 Change": "v6_change",
    })
    for c in df.columns:
        df[c] = df[c].fillna("").str.strip()
    df["new_in_v6"] = df["v6_change"].str.contains("Addition: Term", regex=False)
    return df


def load_icd() -> pd.DataFrame:
    """ICD-10-CM order file: fixed-width (order, code, billable flag, short, long)."""
    with zipfile.ZipFile(RAW / "icd10cm-code-descriptions-2027.zip") as z:
        name = next(n for n in z.namelist() if n.endswith("icd10cm-order-2027.txt"))
        lines = z.read(name).decode("latin-1").splitlines()
    rows = []
    for ln in lines:
        rows.append(dict(code=ln[6:13].strip(), billable=ln[14] == "1",
                         short_desc=ln[16:76].strip(), description=ln[77:].strip()))
    df = pd.DataFrame(rows)
    # Codes new in FY2027 (for the "changed this year" flag)
    with zipfile.ZipFile(RAW / "icd10cm-code-descriptions-2027.zip") as z:
        name = next(n for n in z.namelist() if n.endswith("codes-addenda-2027.txt"))
        add = z.read(name).decode("latin-1").splitlines()
    new = {ln.split()[1] for ln in add if ln.startswith("Add:")}
    df["new_in_fy2027"] = df["code"].isin(new)
    return df


def dotted(code: str) -> str:
    return code if len(code) <= 3 else f"{code[:3]}.{code[3:]}"


# ------------------------------------------------------------- proposals
def longest_prefix(code: str, proposals: dict):
    best = None
    for pfx in proposals:
        if code.startswith(pfx) and (best is None or len(pfx) > len(best)):
            best = pfx
    return best


def build_ctcae(ctcae: pd.DataFrame) -> pd.DataFrame:
    by_term = ctcae.set_index("ctcae_term")
    rows, missing = [], []
    for c in CATEGORIES:
        for term, (role, conf, why) in c["ctcae"].items():
            if term not in by_term.index:
                missing.append((c["id"], term))
                continue
            r = by_term.loc[term]
            rows.append(dict(category_id=c["id"], category_label=c["label"], organ=c["organ"],
                             source="CTCAE v6.0", source_id=r["meddra_llt_code"], source_term=term,
                             soc=r["soc"], new_in_v6=r["new_in_v6"],
                             grade_1=r["grade_1"], grade_2=r["grade_2"], grade_3=r["grade_3"],
                             grade_4=r["grade_4"], grade_5=r["grade_5"],
                             proposed_role=role, proposed_confidence=conf, proposed_rationale=why,
                             match_basis="named in category rules"))
    if missing:
        raise SystemExit(f"CTCAE terms not found in v6.0: {missing}")
    return pd.DataFrame(rows)


NOISE_CHAPTERS = tuple("COPSTVWXYZ")

# Generic suggestions for codes no category rule covers. Applied in order;
# first match wins. Each is labeled "generic rule" so the author can see it.
GENERIC_RULES = [
    (lambda code, d: code[0] in "AB", ("lookalike", "High", "Infectious cause; exclude infection before attributing to an ICI")),
    (lambda code, d: re.search(r"influenza|pneumonia due to|chlamydial|mycoplasma|infective|infectious", d, re.I), ("lookalike", "High", "Infectious cause")),
    (lambda code, d: re.search(r"neoplasm", d, re.I), ("lookalike", "High", "Neoplasm (tumor involvement mimics the irAE)")),
    (lambda code, d: re.search(r"postprocedural|following .*surgery|intraoperative", d, re.I), ("lookalike", "High", "Post-procedural cause")),
    (lambda code, d: re.search(r"diabetes mellitus", d, re.I), ("lookalike", "Moderate", "Diabetic complication")),
    (lambda code, d: re.search(r"lupus|systemic sclerosis|sjogren|sarcoidosis", d, re.I), ("lookalike", "Moderate", "Pre-existing systemic autoimmune or granulomatous disease; may also flare on ICI")),
    (lambda code, d: re.search(r"rheumatic (fever|myocarditis|pericarditis)|acute rheumatic|chronic rheumatic", d, re.I), ("exclude", "", "Rheumatic fever sequelae")),
    (lambda code, d: re.search(r"endometriosis|smoke inhalation|anesthesia|heavy metals|wernicke|hypertensive", d, re.I), ("exclude", "", "Unrelated specific cause")),
    (lambda code, d: re.search(r"due to radiation|radiation", d, re.I), ("lookalike", "High", "Radiation-induced; key confounder in patients who had radiotherapy")),
    (lambda code, d: re.search(r"alcohol", d, re.I), ("lookalike", "High", "Alcohol-related")),
    (lambda code, d: re.search(r"juvenile|congenital|hereditary|neonat|familial", d, re.I), ("exclude", "", "Congenital, hereditary or childhood-onset condition; not a treatment effect")),
    (lambda code, d: re.search(r"calculus|cyst|fistula|perforation|obstruction|abscess|stricture|spasm|sequelae|traumatic|injury", d, re.I), ("exclude", "", "Structural, mechanical, traumatic or late-effect condition; not an immune-mediated process")),
    (lambda code, d: re.search(r"osteoarthritis|gout|chondrocalcinosis|crystal", d, re.I), ("lookalike", "High", "Degenerative or crystal arthropathy")),
    (lambda code, d: re.search(r"rheumatoid", d, re.I), ("review", "", "Rheumatoid disease; pre-existing RA vs ICI inflammatory arthritis")),
    (lambda code, d: re.search(r"pyogenic|bacterial|streptococc|staphylococc|tubercul|fungal|viral|herpe", d, re.I), ("lookalike", "High", "Infectious cause")),
]  # neoplasm, pregnancy, perinatal, injury, external cause, Z


def build_icd(icd: pd.DataFrame) -> pd.DataFrame:
    """One review row per code FAMILY: a parent code plus all its billable
    children (site, laterality, encounter). The published table expands each
    family back to every billable code, so nothing is lost."""
    header = dict(zip(icd["code"], icd["description"]))
    rows = []
    for c in CATEGORIES:
        rx = re.compile(c["icd_regex"], re.I)
        pfx = tuple(c["icd_prefix"]) + tuple(c["icd"].keys())
        by_pfx = icd["code"].str.startswith(pfx)
        by_rx = icd["description"].apply(lambda d: bool(rx.search(d))) & ~icd["code"].str.startswith(NOISE_CHAPTERS)
        hit = icd[(by_pfx | by_rx) & icd["billable"]].copy()
        hit["basis"] = ["prefix rule" if b else "description keyword" for b in by_pfx[hit.index]]
        fam = []
        for code in hit["code"]:
            best = longest_prefix(code, c["icd"])
            fam.append(best if best else code[:3])
        hit["family"] = fam
        for f, g in hit.groupby("family"):
            if f in c["icd"]:
                role, conf, why = c["icd"][f]
                basis = "proposed code family"
            else:
                role, conf, why = "review", "", ""
                basis = g["basis"].iloc[0]
                d = header.get(f, g["description"].iloc[0])
                for test, prop in GENERIC_RULES:
                    if test(f, d):
                        role, conf, why = prop
                        basis += " + generic rule"
                        break
            codes = sorted(g["code"])
            rows.append(dict(category_id=c["id"], category_label=c["label"], organ=c["organ"],
                             source="ICD-10-CM FY2027", source_id=dotted(f) + ("*" if len(codes) > 1 or codes[0] != f else ""),
                             source_term=header.get(f, g["description"].iloc[0]) + (
                                 " (remaining codes in this block; see billable_codes)"
                                 if f not in c["icd"] and any(k.startswith(f) and k != f for k in c["icd"]) else ""),
                             n_billable_codes=len(codes), billable_codes=";".join(dotted(x) for x in codes),
                             new_in_fy2027=bool(g["new_in_fy2027"].any()),
                             proposed_role=role, proposed_confidence=conf, proposed_rationale=why,
                             match_basis=basis))
    df = pd.DataFrame(rows)
    for cc in COMPANION_CODES:
        g = icd[icd["code"].str.startswith(cc["prefix"]) & icd["billable"]]
        df.loc[len(df)] = dict(category_id="ALL", category_label="Drug-cause companion code", organ="All",
                               source="ICD-10-CM FY2027", source_id=dotted(cc["prefix"]) + "*",
                               source_term=header.get(cc["prefix"], ""), n_billable_codes=len(g),
                               billable_codes=";".join(dotted(x) for x in g["code"]),
                               new_in_fy2027=bool(g["new_in_fy2027"].any()), proposed_role=cc["role"],
                               proposed_confidence=cc["confidence"], proposed_rationale=cc["note"],
                               match_basis="companion code rule")
    return df


def openfda_exact_totals(terms, ici_search):
    """Exact report counts for terms whose keyword-query counts were not exact.

    Batches of terms: filter reports to those containing ANY term in the batch
    (exact field), then count the exact field. Each listed term's count is
    then its exact number of reports. One query per batch, for ICI reports
    and for all reports. Cached in data/raw/openfda_term_totals.json (logged).
    """
    import subprocess
    import time
    import urllib.parse
    import urllib.request
    cache_p = RAW / "openfda_term_totals.json"
    cache = json.loads(cache_p.read_text()) if cache_p.exists() else {}
    todo = sorted(t for t in terms if t not in cache or set(cache[t]) != {"ici", "all"})
    base = "https://api.fda.gov/drug/event.json"
    q = lambda s: urllib.parse.quote(s, safe=':"()+')  # noqa: E731

    def get(url):
        for attempt in range(8):
            try:
                with urllib.request.urlopen(url, timeout=60) as r:
                    return json.load(r)
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    return {"results": [], "meta": {"results": {"total": 0}}}
                print(f"      HTTP {e.code}, retry {attempt + 1}", flush=True)
                if e.code == 400:
                    raise
                time.sleep(6 * (attempt + 1))
            except Exception:
                time.sleep(6 * (attempt + 1))
        raise RuntimeError(f"openFDA failed: {url[:200]}")

    # One exact query per term (meta.results.total). Slower than batching but
    # exact: batched count queries are capped at 100 terms and can drop rare
    # terms. Progress is saved every 10 terms, so a re-run resumes.
    for i, t in enumerate(todo, 1):
        if "^" in t:
            # FAERS stores apostrophes as "^", which openFDA's query parser
            # rejects even when escaped. Every report containing the term
            # contains the name before the caret, so search that word on the analyzed
            # field and read the term's exact count from the breakdown.
            # use the eponym before the caret (rare word), not a common word after it
            word = max(re.findall(r"[A-Z]+", t.split("^")[0]), key=len)
            rx = f'patient.reaction.reactionmeddrapt:"{word}"'
            for k, sq in (("ici", f"{ici_search}+AND+{rx}"), ("all", rx)):
                res = get(f"{base}?search={q(sq)}&count=patient.reaction.reactionmeddrapt.exact&limit=100")
                cache.setdefault(t, {})[k] = {x["term"]: x["count"] for x in res.get("results", [])}.get(t, 0)
                time.sleep(0.25)
        else:
            rx = 'patient.reaction.reactionmeddrapt.exact:"' + t.replace('"', "") + '"'
            for k, sq in (("ici", f"{ici_search}+AND+{rx}"), ("all", rx)):
                res = get(f"{base}?search={q(sq)}&limit=1")
                cache.setdefault(t, {})[k] = res.get("meta", {}).get("results", {}).get("total", 0)
                time.sleep(0.25)
        if i % 10 == 0 or i == len(todo):
            cache_p.write_text(json.dumps(cache, indent=1, sort_keys=True))
            print(f"    direct counts: {i}/{len(todo)}", flush=True)
    if todo:
        subprocess.run([sys.executable, str(ROOT / "code" / "provenance.py"), str(cache_p), base,
                        "--log", str(RAW / "PROVENANCE.txt"),
                        "--note", f"per-term exact counts (ICI reports, all reports) for {len(cache)} reaction terms"],
                       check=True, capture_output=True)
    return cache


def build_faers(of: dict) -> pd.DataFrame:
    n_ici, n_all = of["ici_report_total"], of["all_report_total"]
    rows = []
    claimed_primary = set()
    cats = sorted(CATEGORIES, key=lambda c: c["id"] == "IRAE_UNSPECIFIED")  # catch-all last
    raw = []
    for c in cats:
        rx = re.compile(c["faers_regex"], re.I)
        ici_ct, all_ct, exact = {}, {}, set()
        for kw in c["faers_kw"]:
            res = of["keywords"][kw]
            toks = kw.upper().split()
            has_kw = lambda term: all(tok in term for tok in toks)  # noqa: E731
            for t in res["ici"]:
                if rx.search(t["term"]) and has_kw(t["term"]):
                    ici_ct[t["term"]] = t["count"]
                    exact.add(t["term"])
                elif rx.search(t["term"]):
                    ici_ct.setdefault(t["term"], None)
            for t in res["all"]:
                if has_kw(t["term"]):
                    all_ct[t["term"]] = t["count"]
        raw.append((c, ici_ct, all_ct, exact))

    # Fill counts that are not exact with direct queries
    need = set()
    for c, ici_ct, all_ct, exact in raw:
        need |= {t for t in ici_ct if t not in exact or t not in all_ct}
    direct = openfda_exact_totals(need, of["ici_search"])

    for c, ici_ct, all_ct, exact in raw:
        for term in ici_ct:
            if term in exact and term in all_ct:
                a, b, how = ici_ct[term], all_ct[term], "keyword count"
            else:
                a, b, how = direct[term].get("ici"), direct[term].get("all"), "direct count"
            if not a:
                continue  # co-reported term with no exact ICI reports
            # Infectious and tumor terms are checked FIRST so a broad category
            # pattern (e.g. "MENINGOENCEPHALITIS") can never make them primary.
            props = FAERS_FIRST + FAERS_EXTRA.get(c["id"], []) + list(c["faers"].items()) + FAERS_GENERIC
            role, conf, why = "review", "", ""
            for pat, prop in props:
                if re.search(pat, term, re.I):
                    role, conf, why = prop
                    break
            if c["id"] == "IRAE_UNSPECIFIED" and term in claimed_primary:
                continue
            if role == "primary":
                claimed_primary.add(term)
            prr = None
            if b and b > a and n_all > n_ici:
                prr = (a / n_ici) / ((b - a) / (n_all - n_ici))
            rows.append(dict(category_id=c["id"], category_label=c["label"], organ=c["organ"],
                             source="FAERS (openFDA)", source_id=term, source_term=term.capitalize(),
                             ici_reports=a, all_reports=b, ici_prr=round(prr, 1) if prr else None,
                             count_method=how,
                             proposed_role=role, proposed_confidence=conf, proposed_rationale=why,
                             match_basis="openFDA keyword search + category pattern"))
    df = pd.DataFrame(rows)
    return df.sort_values(["category_id", "ici_reports"], ascending=[True, False])


# ------------------------------------------------------------ rationales
GENERIC_WHY = {"core terms", "core", "core term", "specific by construction", "specific", "core/immune terms",
               "graded term", "symptom", "non-specific", "new in v6.0", "lab terms", "lab term",
               "explicitly immune-mediated medra term", "infectious", "infectious cause", "descriptive terms",
               "symptoms", "lab/finding terms", "lab/severity terms", "enzyme terms", "effusion terms",
               "renal function terms", "biomarker", "conduction", "tumor-related", "aihA subtypes".lower()}


def enrich(df: pd.DataFrame) -> pd.DataFrame:
    """Turn short drafted reasons into full one-sentence rationales that say
    what the item is and why it has its role. Draft text only; the author
    accepts or rewrites it."""
    labels = {c["id"]: c["label"].split(" (")[0].lower() for c in CATEGORIES}
    out = []
    for _, r in df.iterrows():
        role, why = r["proposed_role"], str(r["proposed_rationale"] or "").strip()
        lab = labels.get(r["category_id"], "this irAE")
        term = str(r["source_term"]).strip()
        extra = "" if (why.lower() in GENERIC_WHY or why.lower().rstrip(".") == term.lower()
                       or not why) else why.rstrip(".")
        new_v6 = str(r.get("new_in_v6", "")) == "True"
        if role in ("review", "exclude", "companion") or r["category_id"] == "ALL":
            out.append(why)
            continue
        src = r["source"]
        if src.startswith("CTCAE"):
            base = {"primary": f"CTCAE v6.0 term that names {lab} and grades its severity",
                    "supporting": f"CTCAE v6.0 term that grades a feature of {lab} but is not specific to it",
                    "lookalike": f"CTCAE v6.0 term for a different condition to rule out before grading {lab}"}[role]
            if new_v6:
                base += " (new in v6.0)"
        elif src.startswith("ICD"):
            base = {"primary": f"ICD-10-CM code family that names {lab}",
                    "supporting": f"ICD-10-CM code for a finding consistent with {lab}, not specific to it",
                    "lookalike": f"ICD-10-CM code for a different condition often confused with {lab}"}[role]
        else:
            a_, b_ = r.get("ici_reports"), r.get("all_reports")
            share = ""
            try:
                if a_ and b_ and float(b_) > 0:
                    share = f"; {int(float(a_)):,} of {int(float(b_)):,} FAERS reports with this term name a checkpoint inhibitor"
            except ValueError:
                pass
            base = {"primary": f"MedDRA reaction term that names {lab}",
                    "supporting": f"MedDRA reaction term for a finding consistent with {lab}, not specific to it",
                    "lookalike": f"MedDRA reaction term for a different condition often confused with {lab}"}[role] + share
        out.append(base + (f". {extra[0].upper() + extra[1:]}." if extra else "."))
    df["proposed_rationale"] = out
    return df


# ---------------------------------------------------------------- output
def carry_over(df: pd.DataFrame, old: pd.DataFrame) -> pd.DataFrame:
    for col in AUTHOR_COLS:
        df[col] = ""
    if old is None or old.empty:
        return df
    key = ["category_id", "source", "source_id"]
    old = old[key + AUTHOR_COLS].drop_duplicates(key).astype(str).replace("nan", "")
    df = df.drop(columns=AUTHOR_COLS).merge(old, on=key, how="left")
    df[AUTHOR_COLS] = df[AUTHOR_COLS].fillna("")
    return df


def main():
    ctcae, icd = load_ctcae(), load_icd()
    of = json.loads((RAW / "openfda_reactions.json").read_text())
    wb_path = CUR / "irAE-Map_review.xlsx"
    old = {}
    if wb_path.exists():
        for s in ("CTCAE", "ICD-10-CM", "FAERS"):
            try:
                old[s] = pd.read_excel(wb_path, sheet_name=s, dtype=str)
            except ValueError:
                old[s] = None

    parts = {
        "CTCAE": carry_over(enrich(build_ctcae(ctcae)), old.get("CTCAE")),
        "ICD-10-CM": carry_over(enrich(build_icd(icd)), old.get("ICD-10-CM")),
        "FAERS": carry_over(enrich(build_faers(of)), old.get("FAERS")),
    }
    for name, df in parts.items():
        df.to_csv(CUR / f"candidates_{name.lower().replace('-', '')}.csv", index=False)

    cats = pd.DataFrame([dict(category_id=c["id"], label=c["label"], organ=c["organ"],
                              lookalikes=c["lookalikes"], author_keep="", author_note="")
                         for c in CATEGORIES])
    if wb_path.exists():  # carry over category decisions too
        try:
            oc = pd.read_excel(wb_path, sheet_name="Categories", dtype=str).fillna("")
            oc = oc.set_index("category_id")[["author_keep", "author_note"]]
            for col in ("author_keep", "author_note"):
                cats[col] = cats["category_id"].map(oc[col]).fillna("")
        except ValueError:
            pass
    summary = []
    for name, df in parts.items():
        for cid, g in df.groupby("category_id"):
            summary.append(dict(category_id=cid, source=name, candidates=len(g),
                                **{f"proposed_{r}": int((g.proposed_role == r).sum())
                                   for r in ("primary", "supporting", "lookalike", "companion", "review")}))
    summary = pd.DataFrame(summary)
    (CUR / "candidate_summary.csv").write_text(summary.to_csv(index=False))

    import write_review_workbook
    write_review_workbook.write(wb_path, cats, parts, of)
    print("candidates:", {k: len(v) for k, v in parts.items()})
    print(summary.groupby("source")[["candidates", "proposed_review"]].sum())


if __name__ == "__main__":
    main()
