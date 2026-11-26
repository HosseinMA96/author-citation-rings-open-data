"""F9 (POST HOC, POSTHOC.md round 2: P4-P8). Journal-clustered intervals, positive control (prior retraction), finer
adjustment, screening for the referencing/peer-review class, profile of the top 1,000 by pact count.
Frozen scores (hash checked) and the labels/populations/strata of f06. Aggregates only.
usage: python f09_posthoc2.py RUN_ID F05_RUN [n_boot]
"""
import json, sys, zlib
from multiprocessing import Pool
import numpy as np, pandas as pd
from common import Run, D_WORK, F_DATA, F_ROOT, duck, sha256

SPEC_SHA = "07200ecb9affa9f2bee88b68becba9ad81900d2cfcc1fc759ba814ced61ca3ec"
F05 = sys.argv[2]; NB = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
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
run = Run(sys.argv[1], __file__, {"f05_run": F05, "n_boot": NB, "seed": SEED, "posthoc_sha256": sha256(F_ROOT / "POSTHOC.md"),
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
d = S[S.eligible & ~S.prior_0].reset_index(drop=True); y = Y.loc[d.aid]
d["jkey"] = d.jid_main.map(lambda v: "NA" if pd.isna(v) else str(int(v)))   # pandas 3 keeps NaN under astype(str)
d["vdec"] = pd.qcut(d.n_in.rank(method="first"), 10, labels=False)
d["pdec"] = pd.qcut(d.n_bio.rank(method="first"), 10, labels=False)
d["start"] = pd.cut(d.first_y, [2013, 2014, 2016, 2018, 2023], labels=["2014", "2015-16", "2017-18", "2019-23"]).astype(str)
jidx = pd.Index(sorted(d.jkey.unique())); M = jboot(jidx, "primary")
st_prim = key(d[["jid_main", "band"]]); st_p1 = key(d[["jid_main", "band", "vdec"]]); st_p6 = key(d[["jid_main", "pdec", "vdec", "start"]])
F = flags(d)
run.log("primary", {"n": len(d), "positives": int(y.y.sum()), "journals": len(jidx)})
run.log("P4_primary_strata", {k: clustered(st_prim, d.jkey.values, e, y.y.values, M, jidx) for k, e in F.items()})
run.log("P4_by_class", {f"{k}|{c}": clustered(st_prim, d.jkey.values, F[k], y[c].values, M, jidx)
                        for k in ["top_s1_recip_nc", "top_s5_self", "r2"] for c in classes})
run.log("P4_volume_strata", {k: clustered(st_p1, d.jkey.values, e, y.y.values, M, jidx) for k, e in F.items()})
run.log("P6_fine_strata", {k: clustered(st_p6, d.jkey.values, e, y.y.values, M, jidx) for k, e in F.items()})
run.log("P6_strata_count", {"total": int(len(set(st_p6))), "start_band_counts": d.start.value_counts().to_dict()})

# P5 positive control: prior retraction, all eligible authors
ea = S[S.eligible].reset_index(drop=True); ye = Y.loc[ea.aid]; ea["jkey"] = ea.jid_main.map(lambda v: "NA" if pd.isna(v) else str(int(v)))
ea["vdec"] = pd.qcut(ea.n_in.rank(method="first"), 10, labels=False)
jidx_e = pd.Index(sorted(ea.jkey.unique())); Me = jboot(jidx_e, "eligible")
run.log("P5_positive_control", {
    "n": len(ea), "prior": int(ea.prior_0.sum()), "positives": int(ye.y.sum()),
    "primary_strata": clustered(key(ea[["jid_main", "band"]]), ea.jkey.values, ea.prior_0.values, ye.y.values, Me, jidx_e),
    "volume_strata": clustered(key(ea[["jid_main", "band", "vdec"]]), ea.jkey.values, ea.prior_0.values, ye.y.values, Me, jidx_e),
    "by_class": {c: clustered(key(ea[["jid_main", "band"]]), ea.jkey.values, ea.prior_0.values, ye[c].values, Me, jidx_e) for c in classes}})

# P7 screening for the referencing/peer-review class; P4 clustered screening intervals for all later retractions
def rank_order(score, ascending=False):
    v = np.nan_to_num(score.astype(float), nan=(np.inf if ascending else -np.inf))
    u = np.random.default_rng(SEED).random(len(v)); return np.lexsort((u, v if ascending else -v))
ranks = {"s1_recip_nc": rank_order(d.s1_recip_nc.values), "s2_recip": rank_order(d.s2_recip.values),
         "s3_pact": rank_order(d.s3_pact.values), "s4_conc5": rank_order(d.s4_conc5.values), "s5_self": rank_order(d.s5_self.values),
         "s6_co": rank_order(d.s6_co.values), "s7_ch2_low": rank_order(d.s7_ch2.values, ascending=True),
         "s8_burst": rank_order(d.s8_burst.values), "r_score": rank_order(d.r_score.values), "journal_J": rank_order(d.J_0.values),
         "productivity": rank_order(d.n_bio.values), "citations": rank_order(d.n_in.values)}
ra = pd.Series(d.s1_recip_nc.values).rank(pct=True, na_option="bottom") + pd.Series(d.J_0.values).rank(pct=True, na_option="bottom")
ranks["rankavg_s1_J"] = rank_order(ra.values)
jpos = pd.Index(jidx).get_indexer(d.jkey.values)

def metrics(ys, ws):
    cw = np.cumsum(ws); cy = np.cumsum(ws * ys); base = cy[-1] / cw[-1]; m = {}
    for k in KS:
        i = min(np.searchsorted(cw, k), len(cw) - 1); m[f"prec@{k}"] = cy[i] / cw[i]; m[f"lift@{k}"] = m[f"prec@{k}"] / base
    i = min(np.searchsorted(cw, 10000), len(cw) - 1); m["recall@10000"] = cy[i] / cy[-1]
    m["ap"] = float((ws * ys * (cy / np.maximum(cw, 1))).sum() / cy[-1]); return m

def _boot(args):
    yv, rows, kind = args; out = []
    for r in rows:
        wv = (np.random.default_rng(r).poisson(1.0, len(yv)).astype(np.float64) if kind == "author" else M[r][jpos])
        out.append({n: metrics(yv[o], wv[o]) for n, o in ranks.items()})
    return out

def screen(yv, label):
    yv = yv.astype(np.float64)
    point = {n: metrics(yv[o], np.ones(len(yv))) for n, o in ranks.items()}
    seeds = np.random.SeedSequence([SEED, zlib.crc32(label.encode())]).generate_state(NB)
    with Pool(8) as pool:
        ab = [b for c in pool.map(_boot, [(yv, seeds[i::8], "author") for i in range(8)]) for b in c]
        cb = [b for c in pool.map(_boot, [(yv, list(range(NB))[i::8], "cluster") for i in range(8)]) for b in c]
    res = {}
    for n in ranks:
        res[n] = {k: {"point": float(v), "lo": float(np.quantile([b[n][k] for b in ab], .025)), "hi": float(np.quantile([b[n][k] for b in ab], .975)),
                      "cl_lo": float(np.quantile([b[n][k] for b in cb], .025)), "cl_hi": float(np.quantile([b[n][k] for b in cb], .975))}
                  for k, v in point[n].items()}
    return {"positives": int(yv.sum()), "base_rate": float(yv.mean()), **res}

run.log("P7_screen_refpeer", screen(y.y_refpeer.values, "P7"))
run.log("P4_screen_all_clustered", screen(y.y.values, "P4screen"))

# P8 top 1,000 by pact count
top = np.zeros(len(d), bool); top[ranks["s3_pact"][:1000]] = True
prof = {}
for lab_, m in [("top1000_s3", top), ("rest", ~top)]:
    x = d[m]
    prof[lab_] = {"n": int(m.sum()), "positives": int(y.y.values[m].sum()),
                  **{f"median_{c}": float(x[c].median()) for c in ["team", "n_bio", "n_in", "h", "J_0", "s3_pact", "n_cw_nc"]},
                  "share_team_ge20": float((x.team >= 20).mean()), "share_team_ge100": float((x.team >= 100).mean())}
run.log("P8_top1000_pact", prof)
run.finish()
