"""F19 (POSTHOC.md round 7: P20; reporting only). Informative strata and the positives they hold for outcome class 3 as
specified and as first coded, primary strata, every exposure of P14 (setup and MH code of f14, plus the count of positives
in informative strata). Checks: first coded reproduces f06 A3, as specified reproduces f14 P14. Aggregates only.
usage: python f19_informative.py RUN_ID F05_RUN F06_RUN F14_RUN [n_boot]
"""
import json, sys, zlib
import numpy as np, pandas as pd
from common import Run, D_WORK, F_DATA, F_ROOT, duck, sha256

SPEC_SHA = "07200ecb9affa9f2bee88b68becba9ad81900d2cfcc1fc759ba814ced61ca3ec"
F05, F06, F14 = sys.argv[2:5]; NB = int(sys.argv[5]) if len(sys.argv) > 5 else 1000
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
run = Run(sys.argv[1], __file__, {"f05_run": F05, "f06_run": F06, "f14_run": F14, "n_boot": NB, "seed": SEED, "posthoc_sha256": sha256(F_ROOT / "POSTHOC.md"),
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
o = pd.DataFrame({"y": g.size() > 0, "y_refpeer": g.c_refpeer.any(), "y_mill": g.c_mill.any(), "y_misc": g.c_misc.any(),
                  "y_misc_spec": g.c_misc_spec.any(),
                  "y_err_only": g.apply(lambda d: bool((d.c_honest & ~d.c_refpeer & ~d.c_mill & ~d.c_misc).all())),
                  "y_err_only_spec": g.apply(lambda d: bool((d.c_honest & ~d.c_refpeer & ~d.c_mill & ~d.c_misc_spec).all()))})
Y = S[["aid"]].merge(o, left_on="aid", right_index=True, how="left").set_index("aid").fillna(False).astype(bool)
key = lambda cols: np.array(["|".join(map(str, t)) for t in cols.itertuples(index=False, name=None)])

classes = ["y_refpeer", "y_mill", "y_misc", "y_err_only"]
d = S[S.eligible & ~S.prior_0].reset_index(drop=True); y = Y.loc[d.aid]; N = len(d)
d["jkey"] = d.jid_main.map(lambda v: "NA" if pd.isna(v) else str(int(v)))
jidx = pd.Index(sorted(d.jkey.unique())); jcode = jidx.get_indexer(d.jkey.values); J = len(jidx)

def jboot(label):
    rng = np.random.default_rng(np.random.SeedSequence([SEED, zlib.crc32(label.encode())]))
    return np.stack([np.bincount(rng.integers(0, J, J), minlength=J) for _ in range(NB)]).astype(np.float64)
M = jboot("primary")                                   # identical to f09's journal resamples

def rand_decile(v, label):
    u = np.random.default_rng(np.random.SeedSequence([SEED, zlib.crc32(label.encode())])).random(len(v))
    dec = np.empty(len(v), int); dec[np.lexsort((u, v))] = np.arange(len(v)) * 10 // len(v); return dec

# decile variables: as f07/f09 (ties in row order = aid order) and with seeded random ties (P12c)
d["vdec"] = pd.qcut(d.n_in.rank(method="first"), 10, labels=False)
d["pdec"] = pd.qcut(d.n_bio.rank(method="first"), 10, labels=False)
d["vdec_r"] = rand_decile(d.n_in.values.astype(float), "ties_vdec")
d["pdec_r"] = rand_decile(d.n_bio.values.astype(float), "ties_pdec")
d["start"] = pd.cut(d.first_y, [2013, 2014, 2016, 2018, 2023], labels=["2014", "2015-16", "2017-18", "2019-23"]).astype(str)
STRATA = {"primary": key(d[["jid_main", "band"]]), "P1": key(d[["jid_main", "band", "vdec"]]),
          "P6": key(d[["jid_main", "pdec", "vdec", "start"]]), "P1_randties": key(d[["jid_main", "band", "vdec_r"]]),
          "P6_randties": key(d[["jid_main", "pdec_r", "vdec_r", "start"]])}
CODES = {}
for lab_, st in STRATA.items():
    c, _ = pd.factorize(st); js = np.zeros(c.max() + 1, int); js[c] = jcode; CODES[lab_] = (c, js)
run.log("strata_counts", {k: int(v[0].max() + 1) for k, v in CODES.items()})
run.log("vdec_moved_by_random_ties", int((d.vdec.values != d.vdec_r.values).sum()))
run.log("pdec_moved_by_random_ties", int((d.pdec.values != d.pdec_r.values).sum()))

def mh_boot(lab_, e, yv):
    """MH OR with RBG CI (f06/f09 formulas) and the journal-bootstrap ORs (NaN where undefined)."""
    s, js = CODES[lab_]; K = len(js); e = e.astype(float); yv = yv.astype(float)
    n = np.bincount(s, minlength=K).astype(float); n1 = np.bincount(s, e, K); pos = np.bincount(s, yv, K); a = np.bincount(s, e * yv, K)
    b = n1 - a; c = pos - a; n0 = n - n1; dd = n0 - c
    R, Sx = a * dd / n, b * c / n; P_, Q = (a + dd) / n, (b + c) / n
    inf = (n1 > 0) & (n0 > 0) & (pos > 0)
    out = {"exposed": int(e.sum()), "exposed_pos": int((e * yv).sum()), "strata_total": int(K), "strata_informative": int(inf.sum()),
           "positives_in_informative": int(pos[inf].sum()), "exposed_positives_in_informative": int(a[inf].sum())}
    if R.sum() == 0 or Sx.sum() == 0:
        out.update(or_mh=None, lo=None, hi=None); return out, np.full(NB, np.nan)
    orr = R.sum() / Sx.sum()
    v = (P_ * R).sum() / (2 * R.sum() ** 2) + (P_ * Sx + Q * R).sum() / (2 * R.sum() * Sx.sum()) + (Q * Sx).sum() / (2 * Sx.sum() ** 2)
    se = np.sqrt(v); out.update(or_mh=float(orr), lo=float(orr * np.exp(-1.96 * se)), hi=float(orr * np.exp(1.96 * se)))
    num, den = M @ np.bincount(js, R, J), M @ np.bincount(js, Sx, J)
    with np.errstate(divide="ignore", invalid="ignore"):
        bs = np.where(den > 0, num / den, np.nan)
    ok = np.isfinite(bs)
    if ok.sum() > 0:
        out.update(cl_lo=float(np.quantile(bs[ok], .025)), cl_hi=float(np.quantile(bs[ok], .975)), cl_valid=int(ok.sum()))
    return out, bs

def flags(dd_):
    q = lambda c, p=0.99: np.quantile(dd_[c].astype(float).dropna(), p, method="inverted_cdf")
    F = {f"top_{c}": (dd_[c].astype(float) >= q(c)).values for c in ["s1_recip_nc", "s2_recip", "s4_conc5", "s5_self", "s6_co"]}
    F["bottom_s7_ch2"] = (dd_.s7_ch2.astype(float) <= q("s7_ch2", 0.01)).values
    F["r1"], F["r2"], F["r3"] = dd_.r1.values.astype(bool), dd_.r2.values.astype(bool), dd_.r3.values.astype(bool)
    F["r_ge3"] = (dd_.r_score >= 3).values
    return F

F = flags(d)
EXP = ["top_s1_recip_nc", "top_s4_conc5", "top_s5_self", "top_s6_co", "r2", "r3"]
OUTS = ["y"] + classes
run.log("primary", {"n": N, "positives": int(y.y.sum()), "journals": J, "positives_by_class": {c: int(y[c].sum()) for c in classes}})

# --- P20: informative strata for class 3, primary strata -------------------------------------------------------------
r6 = json.loads((F_ROOT / f"experiments/f06_eval/runs/{F06}/run.json").read_text())["results"]["A1_A2_A3_primary"]
r14 = json.loads((F_ROOT / f"experiments/f14_class3/runs/{F14}/run.json").read_text())["results"]["P14_class3"]
res, checks = {}, {}
for k in EXP:
    for c in ["y_misc", "y_misc_spec"]:
        m = mh_boot("primary", F[k], y[c].values)[0]
        res[f"primary|{k}|{c}"] = {x: m.get(x) for x in ["exposed_pos", "strata_total", "strata_informative", "positives_in_informative",
                                                          "exposed_positives_in_informative", "or_mh", "lo", "hi"]}
        ref = r14[f"primary|{k}|{c}"]
        checks[f"f14|{k}|{c}"] = (ref["strata_informative"] == m["strata_informative"]) and (
            (ref["or_mh"] is None and m["or_mh"] is None) or abs(ref["or_mh"] - m["or_mh"]) < 1e-12)
        if c == "y_misc" and f"{k}|y_misc" in r6["mh_by_class"]:
            r = r6["mh_by_class"][f"{k}|y_misc"]
            checks[f"f06|{k}|{c}"] = (r["strata_informative"], r["positives_in_informative"]) == (m["strata_informative"], m["positives_in_informative"]) and abs(r["or_mh"] - m["or_mh"]) < 1e-12
run.log("P20_class3_informative", res)
run.log("P20_checks", checks)
assert all(checks.values()), "reproduction check failed"
run.finish()
