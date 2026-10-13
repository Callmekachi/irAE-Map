#!/usr/bin/env python3
"""05_coverage.py: which CTCAE v6.0 immune-related terms lack a specific ICD-10-CM code?

Plain-language note: for every CTCAE v6.0 term in irAE-Map, this asks whether a
clinician recording that side effect in a medical record has an ICD-10-CM code
that names it specifically. Output: data/processed/coverage/ctcae_icd10cm_coverage.csv
plus coverage_stats.json. This is the derived "coverage analysis dataset"
(target release April 2027, own DOI). Every number in any write-up comes from
coverage_stats.json.

Definitions (provisional; the author confirms them before the April 2027 release):
  coverage_level, per CTCAE term within its irAE category:
    specific      the category has at least one ICD-10-CM family the author
                  rated primary with High specificity
    nonspecific   primary ICD-10-CM families exist, but none rated High specificity
    none          no primary ICD-10-CM family in the category
  drug_attributable_code: at least one primary family's description says the
    condition is drug-induced (e.g., E06.4 Drug-induced thyroiditis), so the
    code itself carries attribution, independent of T45.AX5-.

Version 0 limitation: coverage is judged at the CATEGORY level (any High primary
ICD-10-CM family in the term's category). For the April 2027 release the author
names, per CTCAE term, the single best ICD-10-CM code (term-level link), and
coverage is recomputed from that.

Only CTCAE terms with role primary are assessed (supporting terms such as
"Diarrhea" grade a category but do not define it).

  python code/05_coverage.py            from data/processed/
  python code/05_coverage.py --preview  from data/processed/preview/ (not author-decided)
"""

import argparse
import datetime
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DRUG = re.compile(r"drug[- ]induced|due to drugs|induced by (other )?drugs|due to medicaments|adverse effect", re.I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    a = ap.parse_args()
    src = ROOT / "data" / "processed" / ("preview" if a.preview else "")
    out = src / "coverage"
    out.mkdir(parents=True, exist_ok=True)
    t = pd.read_csv(src / "irae_map_v1.0.csv", dtype=str).fillna("")
    status = t["status"].iloc[0] if len(t) else ""

    ct = t[(t.vocabulary == "CTCAE v6.0") & (t.role == "primary")]
    icd = t[(t.vocabulary == "ICD-10-CM FY2027") & (t.role == "primary")]
    fa = t[(t.vocabulary == "FAERS MedDRA PT") & (t.role == "primary")]

    rows = []
    for _, r in ct.iterrows():
        g = icd[icd.irae_category_id == r.irae_category_id]
        high = g[g.specificity == "High"]
        level = "specific" if len(high) else ("nonspecific" if len(g) else "none")
        drug = g[g.term.apply(lambda x: bool(DRUG.search(x)))]
        f = fa[fa.irae_category_id == r.irae_category_id]
        rows.append(dict(
            ctcae_term=r.term, ctcae_llt_code=r.code, irae_category_id=r.irae_category_id,
            irae_category=r.irae_category, organ_system=r.organ_system,
            ctcae_new_in_v6=r.ctcae_new_in_v6,
            coverage_level=level,
            n_primary_icd_families=len(g), n_primary_icd_high=len(high),
            best_icd_codes=";".join((high if len(high) else g).code.head(5)),
            best_icd_terms=" | ".join((high if len(high) else g).term.head(5)),
            drug_attributable_code=bool(len(drug)),
            drug_attributable_codes=";".join(drug.code),
            faers_primary_terms=len(f),
            faers_ici_reports_max=int(pd.to_numeric(f.faers_ici_reports, errors="coerce").max()) if len(f) else 0,
            status=status))
    cov = pd.DataFrame(rows).sort_values(["coverage_level", "organ_system", "ctcae_term"])
    cov.to_csv(out / "ctcae_icd10cm_coverage.csv", index=False)

    n = len(cov)
    vc = cov.coverage_level.value_counts().to_dict()
    new = cov[cov.ctcae_new_in_v6 == "True"]
    stats = dict(
        built=datetime.date.today().isoformat(), status=status, n_ctcae_terms_assessed=n,
        coverage_counts=vc,
        coverage_pct={k: round(100 * v / n, 1) for k, v in vc.items()} if n else {},
        n_new_in_v6=len(new), coverage_counts_new_in_v6=new.coverage_level.value_counts().to_dict(),
        n_drug_attributable=int(cov.drug_attributable_code.sum()),
        terms_without_specific_code=sorted(cov.loc[cov.coverage_level != "specific", "ctcae_term"].unique().tolist()),
    )
    (out / "coverage_stats.json").write_text(json.dumps(stats, indent=1))
    print(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
