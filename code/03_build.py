#!/usr/bin/env python3
"""03_build.py: turn the author's review decisions into the irAE-Map table, and check it.

Plain-language note: reads your decisions from data/curation/irAE-Map_review.xlsx
and writes the published table to data/processed/, plus a quality report
(qa_report.txt) and a numbers file (stats.json) that every document reads from.
Rows you have not decided are NOT published. Rows you marked exclude are dropped.

  python code/03_build.py              build from your decisions (DRAFT until --final)
  python code/03_build.py --final      same, without the DRAFT status (after the gate)
  python code/03_build.py --preview    build from Claude's SUGGESTIONS instead, into
                                       data/processed/preview/, stamped PREVIEW.
                                       For testing the pipeline only; never released.
"""

import argparse
import datetime
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
from categories import CATEGORIES  # noqa: E402

CUR = ROOT / "data" / "curation"
VERSION = "1.0.0"
VOCAB = {"CTCAE": "CTCAE v6.0", "ICD-10-CM": "ICD-10-CM FY2027", "FAERS": "FAERS MedDRA PT"}
ROLES = {"primary", "supporting", "lookalike", "companion"}
CONF = {"High", "Moderate", "Low"}


def decide(df: pd.DataFrame, preview: bool) -> pd.DataFrame:
    df = df.copy().fillna("")
    for c in ("author_role", "author_confidence", "author_rationale", "author_lookalike_note", "decided_by", "decided_on"):
        df[c] = df[c].astype(str).str.strip().replace("nan", "")
    if preview:
        df["final_role"] = df["proposed_role"]
        df["final_confidence"] = df["proposed_confidence"]
        df["final_rationale"] = df["proposed_rationale"]
        df["decision_type"] = "PREVIEW: Claude suggestion, not an author decision"
        df["decided_by"], df["decided_on"] = "", ""
        return df
    acc = df["author_role"].str.lower() == "accept"
    df["final_role"] = df["author_role"].str.lower().where(~acc, df["proposed_role"])
    df["final_confidence"] = df["author_confidence"].where(~acc | (df["author_confidence"] != ""), df["proposed_confidence"])
    df["final_rationale"] = df["author_rationale"].where(~acc | (df["author_rationale"] != ""), df["proposed_rationale"])
    df["decision_type"] = ["author accepted suggestion" if a else ("author decision" if r else "") for a, r in zip(acc, df["author_role"])]
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--final", action="store_true")
    ap.add_argument("--preview", action="store_true")
    a = ap.parse_args()
    out = ROOT / "data" / "processed" / ("preview" if a.preview else "")
    out.mkdir(parents=True, exist_ok=True)
    status = "PREVIEW (not author-decided)" if a.preview else ("released" if a.final else "DRAFT")

    wb = CUR / "irAE-Map_review.xlsx"
    sheets = {s: pd.read_excel(wb, sheet_name=s, dtype=str) for s in ("Categories", "CTCAE", "ICD-10-CM", "FAERS")}
    cats = sheets["Categories"].fillna("")
    if a.preview:
        cats["author_keep"] = "keep"
    keep = set(cats.loc[cats["author_keep"].str.lower().isin(["keep", "merge"]), "category_id"]) | {"ALL"}
    dropped_cats = sorted(set(cats["category_id"]) - keep)
    undecided_cats = sorted(cats.loc[~cats["author_keep"].str.lower().isin(["keep", "merge", "drop"]), "category_id"])

    qa, problems = [], []
    if undecided_cats:
        problems.append(f"Categories: {len(undecided_cats)} with no keep/merge/drop decision (treated as dropped): {undecided_cats[:8]}")
    rows = []
    for name in ("CTCAE", "ICD-10-CM", "FAERS"):
        df = sheets[name]
        n_all = len(df)
        d = decide(df, a.preview)
        undecided = d[d["final_role"] == ""] if not a.preview else d.iloc[0:0]
        acc_review = d[(d["author_role"].str.lower() == "accept") & (d["proposed_role"] == "review")] if not a.preview else d.iloc[0:0]
        if len(acc_review):
            problems.append(f"{name}: {len(acc_review)} rows marked 'accept' but had no suggestion to accept "
                            f"(proposed_role = review); choose a role instead, e.g. {acc_review.source_id.head(3).tolist()}")
        split = d[d["final_role"] == "split"]
        if len(split):
            problems.append(f"{name}: {len(split)} families marked 'split'; update the rules and rebuild: {split.source_id.tolist()[:10]}")
        bad_role = d[(d["final_role"] != "") & ~d["final_role"].isin(ROLES | {"exclude", "review", "split"})]
        if len(bad_role):
            problems.append(f"{name}: {len(bad_role)} rows with an unrecognized role: {sorted(set(bad_role.final_role))}")
        d = d[d["final_role"].isin(ROLES) & d["category_id"].isin(keep)]
        need_conf = d[(d["final_role"] != "lookalike") & ~d["final_confidence"].isin(CONF)]
        if len(need_conf):
            problems.append(f"{name}: {len(need_conf)} released rows missing a valid confidence (e.g., {need_conf.source_id.head(3).tolist()})")
        need_why = d[d["final_rationale"].str.strip() == ""]
        if len(need_why):
            problems.append(f"{name}: {len(need_why)} released rows missing a rationale (e.g., {need_why.source_id.head(3).tolist()})")
        if not a.preview:
            no_sig = d[d["decided_by"] == ""]
            if len(no_sig):
                problems.append(f"{name}: {len(no_sig)} released rows missing decided_by")
        qa.append(f"{name}: {n_all} candidates; {len(undecided)} undecided (not released); "
                  f"{int((decide(df, a.preview).final_role == 'exclude').sum())} excluded; {len(d)} released")
        d["vocabulary"] = VOCAB[name]
        rows.append(d)

    t = pd.concat(rows, ignore_index=True)
    for col in ("grade_1", "grade_2", "grade_3", "grade_4", "grade_5", "n_billable_codes", "billable_codes",
                "ici_reports", "all_reports", "ici_prr", "new_in_v6", "new_in_fy2027"):
        if col not in t:
            t[col] = ""
    t["code"] = t["source_id"]
    t.loc[t["vocabulary"] == "FAERS MedDRA PT", "code"] = ""  # PT names only; no MedDRA PT codes (licensing)
    t["status"] = status
    t["irae_map_version"] = VERSION
    order = {c["id"]: i for i, c in enumerate(CATEGORIES)}
    order["ALL"] = -1
    t["_o"] = t["category_id"].map(order)
    t["_r"] = t["final_role"].map({"companion": 0, "primary": 1, "supporting": 2, "lookalike": 3})
    t = t.sort_values(["_o", "vocabulary", "_r", "source_term"]).reset_index(drop=True)
    t["map_id"] = [f"IRM-{i:05d}" for i in range(1, len(t) + 1)]

    main_cols = ["map_id", "category_id", "category_label", "organ", "vocabulary", "code", "source_term",
                 "final_role", "final_confidence", "final_rationale", "author_lookalike_note",
                 "decision_type", "decided_by", "decided_on",
                 "n_billable_codes", "new_in_v6", "new_in_fy2027", "ici_reports", "all_reports", "ici_prr",
                 "grade_1", "grade_2", "grade_3", "grade_4", "grade_5", "status", "irae_map_version"]
    final = t[main_cols].rename(columns={
        "category_id": "irae_category_id", "category_label": "irae_category", "organ": "organ_system",
        "source_term": "term", "final_role": "role", "final_confidence": "confidence",
        "final_rationale": "rationale", "author_lookalike_note": "lookalike_note",
        "n_billable_codes": "icd_billable_codes_in_family", "new_in_v6": "ctcae_new_in_v6",
        "new_in_fy2027": "icd_new_in_fy2027", "ici_reports": "faers_ici_reports",
        "all_reports": "faers_all_reports", "ici_prr": "faers_ici_prr",
        "grade_1": "ctcae_grade_1", "grade_2": "ctcae_grade_2", "grade_3": "ctcae_grade_3",
        "grade_4": "ctcae_grade_4", "grade_5": "ctcae_grade_5"})
    final.to_csv(out / "irae_map_v1.0.csv", index=False)

    # ICD-10-CM expanded to billable codes
    icd = t[t["vocabulary"] == "ICD-10-CM FY2027"]
    exp = []
    for _, r in icd.iterrows():
        for code in str(r["billable_codes"]).split(";"):
            if code:
                exp.append(dict(map_id=r["map_id"], irae_category_id=r["category_id"], icd10cm_code=code,
                                code_family=r["source_id"], role=r["final_role"], confidence=r["final_confidence"],
                                status=status, irae_map_version=VERSION))
    exp = pd.DataFrame(exp)
    exp.to_csv(out / "irae_map_icd10cm_expanded.csv", index=False)

    catout = cats[cats["category_id"].isin(keep)][["category_id", "label", "organ", "lookalikes"]].rename(
        columns={"label": "irae_category", "organ": "organ_system", "lookalikes": "category_lookalikes"})
    catout.to_csv(out / "irae_categories.csv", index=False)

    # ---------------- checks
    # Every billable code must exist in FY2027 and be billable
    import zipfile
    with zipfile.ZipFile(ROOT / "data" / "raw" / "icd10cm-code-descriptions-2027.zip") as z:
        nm = next(n for n in z.namelist() if n.endswith("icd10cm-codes-2027.txt"))
        valid = {ln.split()[0] for ln in z.read(nm).decode("latin-1").splitlines() if ln.strip()}
    if len(exp):
        bad = sorted(set(exp.icd10cm_code.str.replace(".", "", regex=False)) - valid)
        if bad:
            problems.append(f"ICD-10-CM: {len(bad)} codes not valid billable FY2027 codes: {bad[:10]}")
    ctcae_terms = set(pd.read_excel(ROOT / "data" / "raw" / "ctcae-v6.0.xlsx", sheet_name="CTCAE v6.0 Clean Copy", dtype=str).iloc[:, 2].str.strip())
    badc = sorted(set(final.loc[final.vocabulary == "CTCAE v6.0", "term"]) - ctcae_terms)
    if badc:
        problems.append(f"CTCAE: terms not in v6.0: {badc}")

    coverage = []
    for cid in [c["id"] for c in CATEGORIES if c["id"] in keep]:
        g = final[(final.irae_category_id == cid) & (final.role == "primary")]
        miss = [v for v in VOCAB.values() if v not in set(g.vocabulary)]
        if miss:
            coverage.append(f"  {cid}: no primary mapping in {', '.join(miss)}")

    multi = final[final.role == "primary"].groupby(["vocabulary", "term"])["irae_category_id"].nunique()
    multi = multi[multi > 1]

    by = final.groupby(["vocabulary", "role"]).size().unstack(fill_value=0)
    stats = dict(
        version=VERSION, status=status, built=datetime.date.today().isoformat(),
        n_categories=len(catout), n_categories_dropped=len(dropped_cats), categories_dropped=dropped_cats,
        n_mappings=len(final), n_icd_billable_codes=int(exp.icd10cm_code.nunique()) if len(exp) else 0,
        by_vocabulary=final.vocabulary.value_counts().to_dict(),
        by_vocabulary_role={v: by.loc[v].to_dict() for v in by.index},
        by_confidence=final.confidence.value_counts().to_dict(),
        n_ctcae_terms=int(final.loc[final.vocabulary == "CTCAE v6.0", "term"].nunique()),
        n_ctcae_terms_new_in_v6=int(final.loc[(final.vocabulary == "CTCAE v6.0") & (final.ctcae_new_in_v6.astype(str) == "True"), "term"].nunique()),
        n_faers_terms=int(final.loc[final.vocabulary == "FAERS MedDRA PT", "term"].nunique()),
        n_terms_primary_in_multiple_categories=int(len(multi)),
        n_problems=len(problems),
        n_accepted_suggestion=int((final.decision_type == "author accepted suggestion").sum()),
        n_author_set=int((final.decision_type == "author decision").sum()),
        n_undecided_not_released=sum(int(q.split("; ")[1].split()[0]) for q in qa),
    )
    of = json.loads((ROOT / "data" / "raw" / "openfda_reactions.json").read_text())
    stats.update(faers_ici_reports_total=of["ici_report_total"], faers_all_reports_total=of["all_report_total"],
                 openfda_last_updated=of["openfda_last_updated"], openfda_accessed=of["accessed"])
    (out / "stats.json").write_text(json.dumps(stats, indent=1, default=str))

    lines = [f"irAE-Map {VERSION} QA report  status: {status}  built: {stats['built']}", "",
             "Plain-language note: the build's own checks. 'PROBLEMS' must be empty before release.", "",
             "Row counts"] + ["  " + q for q in qa] + [
             f"  Released mappings: {len(final)} across {len(catout)} categories "
             f"({len(dropped_cats)} dropped: {', '.join(dropped_cats) or 'none'})",
             f"  ICD-10-CM families expand to {stats['n_icd_billable_codes']} distinct billable codes", "",
             "Released mappings by vocabulary and role", by.to_string(), "",
             "Coverage: categories lacking a primary mapping in a vocabulary"] + (coverage or ["  none"]) + [
             "", f"Terms marked primary in more than one category ({len(multi)}; expected for overlap entities):"] + \
            [f"  {v} | {t}: {n} categories" for (v, t), n in multi.items()] + ["", "PROBLEMS"] + \
            (["  " + p for p in problems] or ["  none"])
    (out / "qa_report.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
