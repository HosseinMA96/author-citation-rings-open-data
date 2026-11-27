"""F20 (POSTHOC.md round 8: P21; reporting only). Positive control (prior retraction, all eligible authors, primary
strata) for outcome class 3 as specified, with the code, labels and bootstrap seeds of f09; all-cause and the four
first-coded classes must reproduce f09 P5 exactly. Frozen scores (hash checked). Aggregates only.
usage: python f20_posctrl.py RUN_ID F05_RUN F09_RUN [n_boot]
"""
import json, sys, zlib
from multiprocessing import Pool
import numpy as np, pandas as pd
from common import Run, D_WORK, F_DATA, F_ROOT, duck, sha256

SPEC_SHA = "07200ecb9affa9f2bee88b68becba9ad81900d2cfcc1fc759ba814ced61ca3ec"
F05, F09 = sys.argv[2:4]; NB = int(sys.argv[4]) if len(sys.argv) > 4 else 1000
SEED, END, T0, KS = 20261126, "2026-10-30", "2024-01-31", [100, 1000, 10000]
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
run = Run(sys.argv[1], __file__, {"f05_run": F05, "f09_run": F09, "n_boot": NB, "seed": SEED, "posthoc_sha256": sha256(F_ROOT / "POSTHOC.md"),
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
L["c_misc"] = L.reasons.map(lambda r: bool(r & MISC_OTHER)); L["c_misc_spec"] = L.reasons.map(lambda r: bool(r & MISCONDUCT)); L["c_honest"] = L.reasons.map(lambda r: any(honest(s) for s in r))
w = L[(L.first_notice > pd.Timestamp(T0)) & (L.first_notice <= pd.Timestamp(END))]; g = w.groupby("aid")
o = pd.DataFrame({"y": g.size() > 0, "y_refpeer": g.c_refpeer.any(), "y_mill": g.c_mill.any(), "y_misc": g.c_misc.any(), "y_misc_spec": g.c_misc_spec.any(),
                  "y_err_only": g.apply(lambda d: bool((d.c_honest & ~d.c_refpeer & ~d.c_mill & ~d.c_misc).all()))})
Y = S[["aid"]].merge(o, left_on="aid", right_index=True, how="left").set_index("aid").fillna(False).astype(bool)
key = lambda cols: np.array(["|".join(map(str, t)) for t in cols.itertuples(index=False, name=None)])

def tables(strata, journal, e, y):
    """Per-stratum MH pieces R = a*d/n, S = b*c/n (0 for non-informative strata), summed per journal."""
    t = pd.DataFrame({"s": strata, "j": journal, "e": e.astype(bool), "y": y.astype(bool)})
    gg = t.groupby("s").agg(n=("e", "size"), n1=("e", "sum"), pos=("y", "sum"), j=("j", "first"))
    a = t[t.e & t.y].groupby("s").size().reindex(gg.index, fill_value=0).astype(float)
    n1 = gg.n1.astype(float); n0 = (gg.n - gg.n1).astype(float); c = gg.pos - a; b = n1 - a; dd = n0 - c; n = gg.n.astype(float)
    R, Sx = a * dd / n, b * c / n
    P_, Q = (a + dd) / n, (b + c) / n
    inf = (n1 > 0) & (n0 > 0) & (gg.pos > 0)
    out = {"exposed": int(t.e.sum()), "exposed_pos": int((t.e & t.y).sum()), "strata_informative": int(inf.sum()),
           "exposed_positives_in_informative": int(a[inf].sum())}
    if R.sum() == 0 or Sx.sum() == 0:
        out.update(or_mh=None, lo=None, hi=None)
    else:
        orr = R.sum() / Sx.sum()
        v = (P_ * R).sum() / (2 * R.sum() ** 2) + (P_ * Sx + Q * R).sum() / (2 * R.sum() * Sx.sum()) + (Q * Sx).sum() / (2 * Sx.sum() ** 2)
        se = np.sqrt(v); out.update(or_mh=orr, lo=orr * np.exp(-1.96 * se), hi=orr * np.exp(1.96 * se))
    return out, R.groupby(gg.j).sum(), Sx.groupby(gg.j).sum()

def clustered(strata, journal, e, y, M, jidx):
    out, Rj, Sj = tables(strata, journal, e, y)
    R = Rj.reindex(jidx, fill_value=0).values; Sx = Sj.reindex(jidx, fill_value=0).values
    num, den = M @ R, M @ Sx
    ok = den > 0
    bs = num[ok] / den[ok]
    if out["or_mh"] is not None and ok.sum() > 0:
        out.update(cl_lo=float(np.quantile(bs, .025)), cl_hi=float(np.quantile(bs, .975)), cl_valid=int(ok.sum()))
    return out

def flags(d):
    q = lambda c, p=0.99: np.quantile(d[c].astype(float).dropna(), p, method="inverted_cdf")
    F = {f"top_{c}": (d[c].astype(float) >= q(c)).values for c in ["s1_recip_nc", "s2_recip", "s4_conc5", "s5_self", "s6_co"]}
    F["bottom_s7_ch2"] = (d.s7_ch2.astype(float) <= q("s7_ch2", 0.01)).values
    F["r1"], F["r2"], F["r3"] = d.r1.values.astype(bool), d.r2.values.astype(bool), d.r3.values.astype(bool)
    F["r_ge3"] = (d.r_score >= 3).values
    return F

def jboot(jidx, label):
    rng = np.random.default_rng(np.random.SeedSequence([SEED, zlib.crc32(label.encode())]))
    J = len(jidx); return np.stack([np.bincount(rng.integers(0, J, J), minlength=J) for _ in range(NB)]).astype(np.float64)

classes = ["y_refpeer", "y_mill", "y_misc", "y_err_only"]
# P21 positive control: prior retraction, all eligible authors (as f09 P5), plus class 3 as specified
ea = S[S.eligible].reset_index(drop=True); ye = Y.loc[ea.aid]; ea["jkey"] = ea.jid_main.map(lambda v: "NA" if pd.isna(v) else str(int(v)))
jidx_e = pd.Index(sorted(ea.jkey.unique())); Me = jboot(jidx_e, "eligible")
st = key(ea[["jid_main", "band"]])
res = {"n": len(ea), "prior": int(ea.prior_0.sum()), "positives": int(ye.y.sum()),
       "positives_by_class": {c: int(ye[c].sum()) for c in classes + ["y_misc_spec"]},
       "primary_strata": clustered(st, ea.jkey.values, ea.prior_0.values, ye.y.values, Me, jidx_e),
       "by_class": {c: clustered(st, ea.jkey.values, ea.prior_0.values, ye[c].values, Me, jidx_e) for c in classes + ["y_misc_spec"]}}
run.log("P21_positive_control", res)
ref = json.loads((F_ROOT / f"experiments/f09_posthoc2/runs/{F09}/run.json").read_text())["results"]["P5_positive_control"]
same = lambda a, b: all((a.get(k) == b.get(k)) if not isinstance(a.get(k), float) else abs(a[k] - b[k]) < 1e-12
                        for k in ["exposed", "exposed_pos", "strata_informative", "or_mh", "lo", "hi", "cl_lo", "cl_hi"])
checks = {"n_prior_positives": (ref["n"], ref["prior"], ref["positives"]) == (res["n"], res["prior"], res["positives"]),
          "primary_strata": same(ref["primary_strata"], res["primary_strata"])}
checks.update({f"class|{c}": same(ref["by_class"][c], res["by_class"][c]) for c in classes})
run.log("P21_checks", checks)
assert all(checks.values()), "reproduction check failed"
run.finish()
