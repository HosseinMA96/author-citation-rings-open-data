"""F13 (POST HOC, POSTHOC.md round 3: P11-P12). P11: outcome classes under the adjusted strata P1 and P6, with the ratio of
the referencing/peer-review OR to the honest-error-only OR, and the screening value of each flag. P12: tie-breaking audit
(A4 deciles, A5 cut-offs, P1/P6 deciles with random instead of row-order ties). Frozen scores (hash checked); labels,
populations and strata as in f06/f07/f09; journal bootstrap as in f09 (same seed label). Aggregates only.
usage: python f13_posthoc3.py RUN_ID F05_RUN [n_boot]
"""
import json, sys, zlib
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
    out = {"exposed": int(e.sum()), "exposed_pos": int((e * yv).sum()), "strata_informative": int(inf.sum()),
           "exposed_positives_in_informative": int(a[inf].sum())}
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

# --- P11: classes under the primary, P1 and P6 strata; ratio refpeer / honest error ------------------------------------
def ratio(o1, b1, o2, b2):
    r = {"or_refpeer": o1.get("or_mh"), "or_err_only": o2.get("or_mh")}
    if not o1.get("or_mh") or not o2.get("or_mh"):
        return {**r, "ratio": None}
    ok = np.isfinite(b1) & np.isfinite(b2) & (b2 > 0)
    rb = b1[ok] / b2[ok]
    return {**r, "ratio": o1["or_mh"] / o2["or_mh"], "cl_lo": float(np.quantile(rb, .025)), "cl_hi": float(np.quantile(rb, .975)),
            "cl_valid": int(ok.sum())}

for lab_ in ["primary", "P1", "P6", "P1_randties", "P6_randties"]:
    res, bsd = {}, {}
    for k in EXP:
        for c in OUTS:
            res[f"{k}|{c}"], bsd[f"{k}|{c}"] = mh_boot(lab_, F[k], y[c].values)
    if lab_.endswith("randties"):
        for k in F:
            if k not in EXP:
                res[f"{k}|y"] = mh_boot(lab_, F[k], y.y.values)[0]
    rat = {k: ratio(res[f"{k}|y_refpeer"], bsd[f"{k}|y_refpeer"], res[f"{k}|y_err_only"], bsd[f"{k}|y_err_only"])
           for k in ["r2", "top_s4_conc5", "top_s5_self", "r3"]}          # r3 added by the data-driven addendum (POSTHOC.md)
    run.log(f"P11_{lab_}", res); run.log(f"P11_ratio_refpeer_over_err_{lab_}", rat)

def wilson(k, n, z=1.96):
    p = k / n; den = 1 + z * z / n; c = (p + z * z / (2 * n)) / den; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return p, c - h, c + h
base, base_rp = float(y.y.mean()), float(y.y_refpeer.mean())
scr = {}
for k, e in F.items():
    n1 = int(e.sum()); k_all = int(y.y.values[e].sum()); k_rp = int(y.y_refpeer.values[e].sum())
    p, lo, hi = wilson(k_all, n1); prp, lorp, hirp = wilson(k_rp, n1)
    scr[k] = {"flagged": n1, "share_of_population": n1 / N, "positives": k_all, "precision": p, "lo": lo, "hi": hi, "lift": p / base,
              "positives_refpeer": k_rp, "precision_refpeer": prp, "lo_refpeer": lorp, "hi_refpeer": hirp, "lift_refpeer": prp / base_rp}
run.log("P11_flag_screening", {"base_rate": base, "base_rate_refpeer": base_rp, **scr})

# --- P12a: A4 deciles (exact reproduction of f06) -----------------------------------------------------------------
yy = y.y.values.astype(int); s1 = d.s1_recip_nc.fillna(-1).values
rng = np.random.default_rng(SEED)
order = np.lexsort((rng.random(N), s1)); dec = np.empty(N, int); dec[order] = np.arange(N) * 10 // N
cnt = [int(yy[dec == k].sum()) for k in range(3)]; nk = [int((dec == k).sum()) for k in range(3)]
exp_ = sum(cnt) / 3; chi = float(sum((x - exp_) ** 2 / exp_ for x in cnt))
z0 = s1 == 0; N0 = int(z0.sum()); y0 = yy[z0]
alt = []
for sd in range(1000):
    pr = np.random.default_rng(np.random.SeedSequence([SEED, zlib.crc32(b"A4alt"), sd])).permutation(y0)[: 3 * nk[0]]
    c3 = [int(pr[i * nk[0]:(i + 1) * nk[0]].sum()) for i in range(3)]; e3 = sum(c3) / 3
    alt.append(sum((x - e3) ** 2 / e3 for x in c3))
alt = np.array(alt)
aid = d.aid.values.astype(float)
p0, l0, h0 = wilson(int(y0.sum()), N0)
run.log("P12a_A4_deciles", {
    "decile_sizes_1_3": nk, "positives_1_3": cnt, "max_s1_in_deciles_1_3": float(d.s1_recip_nc.values[dec <= 2].max()),
    "authors_with_s1_zero": N0, "deciles_fully_zero": int((3 * nk[0]) <= N0),
    "mean_aid_1_3": [float(aid[dec == k].mean()) for k in range(3)], "median_aid_1_3": [float(np.median(aid[dec == k])) for k in range(3)],
    "chi2_frozen_seed": chi, "alt_seeds": 1000, "share_alt_chi2_ge_frozen": float((alt >= chi).mean()),
    "alt_chi2_quantiles_50_95_99": [float(np.quantile(alt, q)) for q in (.5, .95, .99)],
    "s1_zero_pooled": {"n": N0, "positives": int(y0.sum()), "rate": p0, "lo": l0, "hi": h0}})

# --- P12b: A5 cut-offs: tie groups and lift under random ties (exact hypergeometric draws) --------------------------
def rank_order(score, ascending=False):
    v = np.nan_to_num(score.astype(float), nan=(np.inf if ascending else -np.inf))
    u = np.random.default_rng(SEED).random(len(v)); return np.lexsort((u, v if ascending else -v)), v
RANK = {"s1_recip_nc": (d.s1_recip_nc.values, False), "s2_recip": (d.s2_recip.values, False), "s3_pact": (d.s3_pact.values, False),
        "s4_conc5": (d.s4_conc5.values, False), "s5_self": (d.s5_self.values, False), "s6_co": (d.s6_co.values, False),
        "s7_ch2_low": (d.s7_ch2.values, True), "s8_burst": (d.s8_burst.values, False), "r_score": (d.r_score.values, False),
        "journal_J": (d.J_0.values, False), "productivity": (d.n_bio.values, False), "citations": (d.n_in.values, False)}
ra = (pd.Series(d.s1_recip_nc.values).rank(pct=True, na_option="bottom") + pd.Series(d.J_0.values).rank(pct=True, na_option="bottom"))
RANK["rankavg_s1_J"] = (ra.values, False)
hg = np.random.default_rng(np.random.SeedSequence([SEED, zlib.crc32(b"A5ties")]))
base_all = yy.mean(); tie = {}
for name, (sc, asc) in RANK.items():
    o_, v = rank_order(sc, asc); tie[name] = {}
    for k in KS:
        vk = v[o_[k - 1]]; better = (v < vk) if asc else (v > vk); grp = v == vk
        nb, pb, T, P = int(better.sum()), int(yy[better].sum()), int(grp.sum()), int(yy[grp].sum()); m = k - nb
        if m <= 0 or P == 0: draws = np.zeros(1000, int)
        elif m >= T: draws = np.full(1000, P)
        elif P == T: draws = np.full(1000, m)
        else: draws = hg.hypergeometric(P, T - P, m, size=1000)
        lifts = (pb + draws) / k / base_all
        tie[name][f"k{k}"] = {"tie_group_size": T, "tie_group_positives": P, "taken_from_tie_group": m,
                              "lift_frozen": float(yy[o_[:k]].sum() / k / base_all),
                              "lift_min": float(lifts.min()), "lift_q025": float(np.quantile(lifts, .025)),
                              "lift_median": float(np.median(lifts)), "lift_q975": float(np.quantile(lifts, .975)), "lift_max": float(lifts.max())}
run.log("P12b_A5_ties", tie)
pd.DataFrame([{"ranking": n, "k": kk, **v} for n, t in tie.items() for kk, v in t.items()]).to_csv(run.dir / "P12b_A5_ties.csv", index=False)
run.finish()
