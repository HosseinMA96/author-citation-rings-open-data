"""F7 (POST HOC, POSTHOC.md round 1): P1 citation-volume strata, P2 profiles of flagged groups, P3 size-free pact rate.
Uses the frozen scores (hash checked) and the labels/populations/strata of f06. Aggregates only.
usage: python f07_posthoc.py RUN_ID F05_RUN
"""
import json, sys
import numpy as np, pandas as pd
from common import Run, D_WORK, F_DATA, F_ROOT, duck, sha256

SPEC_SHA = "07200ecb9affa9f2bee88b68becba9ad81900d2cfcc1fc759ba814ced61ca3ec"
F05 = sys.argv[2]; END = "2026-10-30"; T0 = "2024-01-31"
RW_RUN, M_RUN = "d02_rw_20261101_01", "d05_match_20261101_02"
REFPEER = {"Concerns/Issues about Referencing/Attributions", "Compromised Peer Review", "Concerns/Issues about Peer Review",
           "Rogue Editor"}
MISCONDUCT = {"Falsification/Fabrication of Data", "Falsification/Fabrication of Image", "Falsification/Fabrication of Results",
              "Manipulation of Images", "Manipulation of Results", "Manipulation of Data", "Misconduct by Author",
              "Misconduct - Official Investigation(s) and/or Finding(s)", "Euphemisms for Misconduct", "Plagiarism of/in Article",
              "Plagiarism of Text", "Plagiarism of Image", "Plagiarism of Data", "Euphemisms for Plagiarism",
              "Duplication of/in Image", "Compromised Peer Review", "Rogue Editor", "False/Forged Authorship",
              "False/Forged Affiliation", "Computer-Aided Content or Computer-Generated Content", "Hoax Paper",
              "Sabotage of Materials/Methods"}
MISC_OTHER = MISCONDUCT - REFPEER
HONEST = {"Results Not Reproducible", "Contamination of Cell Lines/Tissues", "Contamination of Materials", "Doing the Right Thing"}
honest = lambda s: s.startswith("Error in") or s.startswith("Error by") or s in HONEST

f05 = json.loads((F_ROOT / f"experiments/f05_scores/runs/{F05}/run.json").read_text())
sfile = F_DATA / "f05" / F05 / "scores.parquet"
run = Run(sys.argv[1], __file__, {"f05_run": F05, "posthoc_sha256": sha256(F_ROOT / "POSTHOC.md"),
                                   "spec_sha256": sha256(F_ROOT / "SPEC.md"), "T0": T0, "end": END})
assert sha256(F_ROOT / "SPEC.md") == SPEC_SHA and sha256(sfile) == f05["results"]["scores_frozen"]["sha256"]
run.log("frozen_spec_and_scores_verified", True)
con = duck(memory="40GB")
S = con.execute(f"SELECT * FROM read_parquet('{sfile}') ORDER BY aid").df()
con.execute(f"""CREATE TABLE lab AS SELECT ri.iid, min(r.notice_date) AS first_notice, flatten(list(r.reasons)) AS reasons
   FROM read_parquet('{D_WORK / f'rw_iid_{M_RUN}.parquet'}') ri JOIN read_parquet('{D_WORK / f'rw_papers_{RW_RUN}.parquet'}') r USING (key)
   WHERE NOT coalesce(r.reinstated, false) GROUP BY 1""")
con.register("au", S[["aid"]])
L = con.execute(f"""SELECT s.aid, l.iid, l.first_notice, l.reasons FROM read_parquet('{F_DATA / 'orcid_slots.parquet'}') s
   JOIN au USING (aid) JOIN lab l USING (iid)""").df()
L["reasons"] = L.reasons.map(lambda r: set(r) if r is not None else set())
L["c_refpeer"] = L.reasons.map(lambda r: bool(r & REFPEER)); L["c_mill"] = L.reasons.map(lambda r: "Paper Mill" in r)
L["c_misc"] = L.reasons.map(lambda r: bool(r & MISC_OTHER)); L["c_honest"] = L.reasons.map(lambda r: any(honest(s) for s in r))
w = L[(L.first_notice > pd.Timestamp(T0)) & (L.first_notice <= pd.Timestamp(END))]; g = w.groupby("aid")
o = pd.DataFrame({"y": g.size() > 0, "y_refpeer": g.c_refpeer.any(), "y_mill": g.c_mill.any(), "y_misc": g.c_misc.any(),
                  "y_err_only": g.apply(lambda d: bool((d.c_honest & ~d.c_refpeer & ~d.c_mill & ~d.c_misc).all()))})
Y = S[["aid"]].merge(o, left_on="aid", right_index=True, how="left").set_index("aid").fillna(False).astype(bool)

def mh(strata, e, y):
    t = pd.DataFrame({"s": strata, "e": e.astype(bool), "y": y.astype(bool)})
    gg = t.groupby("s").agg(n=("e", "size"), n1=("e", "sum"), pos=("y", "sum"))
    a = t[t.e & t.y].groupby("s").size().reindex(gg.index, fill_value=0)
    n1 = gg.n1; n0 = gg.n - gg.n1; c = gg.pos - a; b = n1 - a; dd = n0 - c; n = gg.n.astype(float)
    inf = (n1 > 0) & (n0 > 0) & (gg.pos > 0)
    a, b, c, dd, n = a[inf].astype(float), b[inf].astype(float), c[inf].astype(float), dd[inf].astype(float), n[inf]
    R, Sx = a * dd / n, b * c / n; P_, Q = (a + dd) / n, (b + c) / n
    out = {"exposed": int(t.e.sum()), "exposed_pos": int((t.e & t.y).sum()), "strata_informative": int(inf.sum()),
           "exposed_positives_in_informative": int(a.sum())}
    if R.sum() == 0 or Sx.sum() == 0:
        return {**out, "or_mh": None, "lo": None, "hi": None}
    orr = R.sum() / Sx.sum()
    v = (P_ * R).sum() / (2 * R.sum() ** 2) + (P_ * Sx + Q * R).sum() / (2 * R.sum() * Sx.sum()) + (Q * Sx).sum() / (2 * Sx.sum() ** 2)
    se = np.sqrt(v)
    return {**out, "or_mh": orr, "lo": orr * np.exp(-1.96 * se), "hi": orr * np.exp(1.96 * se)}

d = S[S.eligible & ~S.prior_0].reset_index(drop=True); y = Y.loc[d.aid]
key = lambda cols: np.array(["|".join(map(str, t)) for t in cols.itertuples(index=False, name=None)])
d["vdec"] = pd.qcut(d.n_in.rank(method="first"), 10, labels=False)
st_prim, st_p1 = key(d[["jid_main", "band"]]), key(d[["jid_main", "band", "vdec"]])
run.log("primary", {"n": len(d), "positives": int(y.y.sum())})
q = lambda c, p=0.99: np.quantile(d[c].astype(float).dropna(), p, method="inverted_cdf")
F = {f"top_{c}": (d[c].astype(float) >= q(c)).values for c in ["s1_recip_nc", "s2_recip", "s4_conc5", "s5_self", "s6_co"]}
F["bottom_s7_ch2"] = (d.s7_ch2.astype(float) <= q("s7_ch2", 0.01)).values
F["r1"], F["r2"], F["r3"] = d.r1.values.astype(bool), d.r2.values.astype(bool), d.r3.values.astype(bool)
F["r_ge3"] = (d.r_score >= 3).values
d["pact_rate"] = 100 * d.s3_pact / d.n_cw
F["top_pact_rate"] = (d.pact_rate >= q("pact_rate")).values
run.log("pact_rate_q99", float(q("pact_rate")))
classes = ["y_refpeer", "y_mill", "y_misc", "y_err_only"]
# P1: strata add deciles of citations received
run.log("P1_volume_strata", {k: mh(st_p1, e, y.y.values) for k, e in F.items()})
run.log("P1_r2_by_class", {c: mh(st_p1, F["r2"], y[c].values) for c in classes})
# P3: size-free pact rate, primary strata and P1 strata
run.log("P3_pact_rate_primary_strata", mh(st_prim, F["top_pact_rate"], y.y.values))
run.log("P3_pact_rate_by_class_primary_strata", {c: mh(st_prim, F["top_pact_rate"], y[c].values) for c in classes})
# P2: profiles (no outcomes)
prof = {}
for k in ["top_s1_recip_nc", "top_s5_self", "r2", "r3", "top_pact_rate"]:
    for lab_, m in [("exposed", F[k]), ("unexposed", ~F[k])]:
        x = d[m]
        prof[f"{k}|{lab_}"] = {"n": int(m.sum()), **{f"median_{c}": float(x[c].median()) for c in
                               ["n_bio", "n_in", "h", "team", "J_0", "n_cw_nc", "s3_pact"]},
                               "band_share": {b: round(float((x.band == b).mean()), 4) for b in ["05-09", "10-19", "20-49", "50+"]}}
run.log("P2_profiles", prof)
pd.DataFrame([{"group": k, **{kk: vv for kk, vv in v.items() if kk != "band_share"}, **{f"band_{b}": s for b, s in v["band_share"].items()}}
              for k, v in prof.items()]).to_csv(run.dir / "P2_profiles.csv", index=False)
run.finish()
