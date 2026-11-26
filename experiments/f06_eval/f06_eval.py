"""F6: evaluate the FROZEN author scores against retractions issued after T0, exactly as SPEC.md §5-§7.
First script that reads post-T0 labels. Refuses to run if SPEC.md or the frozen score file changed.
Aggregates only: no per-author output is written anywhere.
usage: python f06_eval.py RUN_ID F05_RUN [n_boot]
"""
import json, sys, zlib
from multiprocessing import Pool
import numpy as np, pandas as pd
from common import Run, C_WORK, D_WORK, F_DATA, F_ROOT, duck, sha256

SPEC_SHA = "07200ecb9affa9f2bee88b68becba9ad81900d2cfcc1fc759ba814ced61ca3ec"   # frozen 2026-11-26 (f04_spec)
F05 = sys.argv[2]; NB = int(sys.argv[3]) if len(sys.argv) > 3 else 1000
SEED, END, KS = 20261126, "2026-10-30", [100, 1000, 10000]
T0S = {"main": "2024-01-31", "T0p": "2023-09-30"}
RW_RUN, M_RUN = "d02_rw_20261101_01", "d05_match_20261101_02"
REFPEER = {"Concerns/Issues about Referencing/Attributions", "Compromised Peer Review", "Concerns/Issues about Peer Review",
           "Rogue Editor"}
MISCONDUCT = {"Falsification/Fabrication of Data", "Falsification/Fabrication of Image", "Falsification/Fabrication of Results",
              "Manipulation of Images", "Manipulation of Results", "Manipulation of Data", "Misconduct by Author",
              "Misconduct - Official Investigation(s) and/or Finding(s)", "Euphemisms for Misconduct", "Plagiarism of/in Article",
              "Plagiarism of Text", "Plagiarism of Image", "Plagiarism of Data", "Euphemisms for Plagiarism",
              "Duplication of/in Image", "Compromised Peer Review", "Rogue Editor", "False/Forged Authorship",
              "False/Forged Affiliation", "Computer-Aided Content or Computer-Generated Content", "Hoax Paper",
              "Sabotage of Materials/Methods"}          # E's SPEC §4 class 2
MISC_OTHER = MISCONDUCT - REFPEER                         # SPEC §5 class 3 "misconduct (other)": without the refpeer strings
HONEST = {"Results Not Reproducible", "Contamination of Cell Lines/Tissues", "Contamination of Materials", "Doing the Right Thing"}
honest = lambda s: s.startswith("Error in") or s.startswith("Error by") or s in HONEST

f05 = json.loads((F_ROOT / f"experiments/f05_scores/runs/{F05}/run.json").read_text())
sfile = F_DATA / "f05" / F05 / "scores.parquet"
run = Run(sys.argv[1], __file__, {"f05_run": F05, "n_boot": NB, "seed": SEED, "end": END, "T0s": T0S, "ks": KS,
                                   "spec_sha256": sha256(F_ROOT / "SPEC.md"), "rw_run": RW_RUN, "match_run": M_RUN})
assert sha256(F_ROOT / "SPEC.md") == SPEC_SHA, "SPEC.md changed after freezing (amend it formally first)"
assert f05["config"]["spec_sha256"] == SPEC_SHA, "scores were computed under another SPEC version"
assert sha256(sfile) == f05["results"]["scores_frozen"]["sha256"], "frozen scores changed"
run.log("frozen_spec_and_scores_verified", True)

con = duck(memory="40GB")
S = con.execute(f"SELECT * FROM read_parquet('{sfile}') ORDER BY aid").df()
# --- labels (first read of post-T0 information) ---------------------------------------------------------------
con.execute(f"""CREATE TABLE lab AS SELECT ri.iid, min(r.notice_date) AS first_notice, flatten(list(r.reasons)) AS reasons
   FROM read_parquet('{D_WORK / f'rw_iid_{M_RUN}.parquet'}') ri JOIN read_parquet('{D_WORK / f'rw_papers_{RW_RUN}.parquet'}') r USING (key)
   WHERE NOT coalesce(r.reinstated, false) GROUP BY 1""")
con.register("au", S[["aid"]])
L = con.execute(f"""SELECT s.aid, l.iid, l.first_notice, l.reasons, p.pub_year
   FROM read_parquet('{F_DATA / 'orcid_slots.parquet'}') s JOIN au USING (aid) JOIN lab l USING (iid)
   JOIN read_parquet('{C_WORK / 'pubs_slim.parquet'}') p USING (iid)""").df()
L["reasons"] = L.reasons.map(lambda r: set(r) if r is not None else set())
L["c_refpeer"] = L.reasons.map(lambda r: bool(r & REFPEER))
L["c_mill"] = L.reasons.map(lambda r: "Paper Mill" in r)
L["c_misc"] = L.reasons.map(lambda r: bool(r & MISC_OTHER))
L["c_honest"] = L.reasons.map(lambda r: any(honest(s) for s in r))
run.log("author_paper_retraction_links", len(L))

def outcomes(T, in_window=False):
    w = L[(L.first_notice > pd.Timestamp(T)) & (L.first_notice <= pd.Timestamp(END))]
    if in_window:
        w = w[w.pub_year.between(2014, 2023)]
    g = w.groupby("aid")
    o = pd.DataFrame({"y": g.size() > 0, "y_refpeer": g.c_refpeer.any(), "y_mill": g.c_mill.any(), "y_misc": g.c_misc.any(),
                      "y_err_only": g.apply(lambda d: bool((d.c_honest & ~d.c_refpeer & ~d.c_mill & ~d.c_misc).all()))})
    o = S[["aid"]].merge(o, left_on="aid", right_index=True, how="left").set_index("aid")
    return o.fillna(False).astype(bool)

def wilson(k, n, z=1.96):
    if n == 0: return (None, None, None)
    p = k / n; den = 1 + z * z / n; c = (p + z * z / (2 * n)) / den; h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (p, c - h, c + h)

def mh(strata, e, y):
    t = pd.DataFrame({"s": strata, "e": e.astype(bool), "y": y.astype(bool)})
    g = t.groupby("s").agg(n=("e", "size"), n1=("e", "sum"), pos=("y", "sum"))
    a = t[t.e & t.y].groupby("s").size().reindex(g.index, fill_value=0)
    n1 = g.n1; n0 = g.n - g.n1; c = g.pos - a; b = n1 - a; dd = n0 - c; n = g.n.astype(float)
    inf = (n1 > 0) & (n0 > 0) & (g.pos > 0)
    a, b, c, dd, n = a[inf].astype(float), b[inf].astype(float), c[inf].astype(float), dd[inf].astype(float), n[inf]
    R, Sx = a * dd / n, b * c / n; P_, Q = (a + dd) / n, (b + c) / n
    out = {"exposed": int(t.e.sum()), "exposed_pos": int((t.e & t.y).sum()), "unexposed": int((~t.e).sum()),
           "unexposed_pos": int((~t.e & t.y).sum()), "strata_total": int(len(g)), "strata_informative": int(inf.sum()),
           "positives_in_informative": int((a + c).sum()), "exposed_positives_in_informative": int(a.sum())}
    if R.sum() == 0 or Sx.sum() == 0:
        return {**out, "or_mh": None, "lo": None, "hi": None}
    orr = R.sum() / Sx.sum()
    v = (P_ * R).sum() / (2 * R.sum() ** 2) + (P_ * Sx + Q * R).sum() / (2 * R.sum() * Sx.sum()) + (Q * Sx).sum() / (2 * Sx.sum() ** 2)
    se = np.sqrt(v)
    return {**out, "or_mh": orr, "lo": orr * np.exp(-1.96 * se), "hi": orr * np.exp(1.96 * se)}

def flags(d, q):
    """Exposure flags of SPEC §6 A1-A2 inside population d; q = 0.99 (top 1%) or 0.95 (top 5%)."""
    f, th = {}, {}
    for c in ["s1_recip_nc", "s2_recip", "s4_conc5", "s5_self", "s6_co"]:
        v = d[c].astype(float); thr = np.quantile(v.dropna(), q, method="inverted_cdf"); f[f"top_{c}"] = (v >= thr).values; th[c] = float(thr)
    v = d.s7_ch2.astype(float); thr = np.quantile(v.dropna(), 1 - q, method="inverted_cdf"); f["bottom_s7_ch2"] = (v <= thr).values
    th["s7_ch2"] = float(thr)
    f["r1"], f["r2"], f["r3"] = d.r1.values.astype(bool), d.r2.values.astype(bool), d.r3.values.astype(bool)
    f["r_ge3"] = (d.r_score >= 3).values
    return f, th

def analyse(tag, d, Y, strata_cols=("jid_main", "band"), q=0.99, classes=True):
    d = d.reset_index(drop=True); y = Y.loc[d.aid]
    strata = np.array(["|".join(map(str, t)) for t in d[list(strata_cols)].itertuples(index=False, name=None)])
    res = {"n": len(d), "positives": int(y.y.sum()), "base_rate": float(y.y.mean()),
           "positives_by_class": {k: int(y[k].sum()) for k in ["y_refpeer", "y_mill", "y_misc", "y_err_only"]},
           "q": q}
    F, res["thresholds"] = flags(d, q)
    res["mh"] = {k: mh(strata, e, y.y.values) for k, e in F.items()}
    if classes:
        res["mh_by_class"] = {f"{k}|{c}": mh(strata, F[k], y[c].values)
                              for k in ["top_s1_recip_nc", "top_s5_self", "r2"] for c in ["y_refpeer", "y_mill", "y_misc", "y_err_only"]}
    run.log(tag, res)
    return res

# --- primary and pre-specified robustness ---------------------------------------------------------------------
Ym, Yp, Yw = outcomes(T0S["main"]), outcomes(T0S["T0p"]), outcomes(T0S["main"], in_window=True)
elig = S[S.eligible]
prim = elig[~elig.prior_0]
run.log("counts", {"pre_eligible": len(S), "eligible": len(elig), "eligible_prior_T0": int(elig.prior_0.sum()), "primary": len(prim),
                   "primary_positives": int(Ym.loc[prim.aid].y.sum()), "eligible_positives": int(Ym.loc[elig.aid].y.sum()),
                   "eligible_prior_positives": int(Ym.loc[elig[elig.prior_0].aid].y.sum())})
P = analyse("A1_A2_A3_primary", prim, Ym)
analyse("rob_a_all_eligible_prior_stratum", elig.assign(pr=elig.prior_0.astype(str)), Ym, ("jid_main", "band", "pr"), classes=False)
analyse("rob_b_T0p", elig[~elig.prior_1], Yp, classes=False)
analyse("rob_c_cwnc_ge100", prim[prim.n_cw_nc >= 100], Ym, classes=False)
analyse("rob_d_outcome_papers_in_W", prim, Yw, classes=False)
analyse("rob_e_strata_journal_only", prim, Ym, ("jid_main",), classes=False)
analyse("rob_f_top5pct", prim, Ym, q=0.95, classes=False)

# --- A4 dose: S1 deciles (equal size, seeded tie-break) and the top 1% -------------------------------------------
rng = np.random.default_rng(SEED)
d = prim.reset_index(drop=True); y = Ym.loc[d.aid].y.values
order = np.lexsort((rng.random(len(d)), d.s1_recip_nc.fillna(-1).values))   # ascending S1, random ties
dec = np.empty(len(d), int); dec[order] = np.arange(len(d)) * 10 // len(d)
rows = []
for k in range(10):
    m = dec == k; p, lo, hi = wilson(int(y[m].sum()), int(m.sum()))
    rows.append({"decile": k + 1, "n": int(m.sum()), "pos": int(y[m].sum()), "rate": p, "lo": lo, "hi": hi,
                 "s1_min": float(d.s1_recip_nc.values[m].min()), "s1_max": float(d.s1_recip_nc.values[m].max())})
thr = np.quantile(d.s1_recip_nc.dropna(), 0.99, method="inverted_cdf"); m = (d.s1_recip_nc >= thr).values
p, lo, hi = wilson(int(y[m].sum()), int(m.sum()))
rows.append({"decile": "top1%", "n": int(m.sum()), "pos": int(y[m].sum()), "rate": p, "lo": lo, "hi": hi, "s1_min": float(thr),
             "s1_max": float(d.s1_recip_nc.max())})
run.log("A4_dose_s1", rows)
pd.DataFrame(rows).to_csv(run.dir / "A4_dose_s1.csv", index=False)

# --- A5 screening (paired bootstrap over authors: one weight vector per resample, shared by all rankings) ---------
def rank_order(score, ascending=False):
    v = np.nan_to_num(score.astype(float), nan=(np.inf if ascending else -np.inf))
    u = np.random.default_rng(SEED).random(len(v))
    return np.lexsort((u, v if ascending else -v))

ranks = {"s1_recip_nc": rank_order(d.s1_recip_nc.values), "s2_recip": rank_order(d.s2_recip.values),
         "s3_pact": rank_order(d.s3_pact.values), "s4_conc5": rank_order(d.s4_conc5.values), "s5_self": rank_order(d.s5_self.values),
         "s6_co": rank_order(d.s6_co.values), "s7_ch2_low": rank_order(d.s7_ch2.values, ascending=True),
         "s8_burst": rank_order(d.s8_burst.values), "r_score": rank_order(d.r_score.values), "journal_J": rank_order(d.J_0.values),
         "productivity": rank_order(d.n_bio.values), "citations": rank_order(d.n_in.values)}
ra = (pd.Series(d.s1_recip_nc.values).rank(pct=True, na_option="bottom") + pd.Series(d.J_0.values).rank(pct=True, na_option="bottom"))
ranks["rankavg_s1_J"] = rank_order(ra.values)

def metrics(ys, ws):
    cw = np.cumsum(ws, dtype=np.int64); cy = np.cumsum(ws * ys, dtype=np.int64); base = cy[-1] / cw[-1]; m = {}
    for k in KS:
        i = min(np.searchsorted(cw, k), len(cw) - 1); m[f"prec@{k}"] = cy[i] / cw[i]; m[f"lift@{k}"] = m[f"prec@{k}"] / base
    i = min(np.searchsorted(cw, 10000), len(cw) - 1); m["recall@10000"] = cy[i] / cy[-1]
    m["ap"] = float((ws * ys * (cy / np.maximum(cw, 1))).sum() / cy[-1])
    return m

def _boot(seeds):
    out = []
    for s in seeds:
        w = np.random.default_rng(s).poisson(1.0, len(y)).astype(np.int64)
        out.append({name: metrics(y[o].astype(np.int64), w[o]) for name, o in ranks.items()})
    return out

point = {name: metrics(y[o].astype(np.int64), np.ones(len(y), np.int64)) for name, o in ranks.items()}
seeds = np.random.SeedSequence([SEED, zlib.crc32(b"A5")]).generate_state(NB)
with Pool(8) as pool:
    boots = [b for chunk in pool.map(_boot, [seeds[i::8] for i in range(8)]) for b in chunk]
A5 = {}
for name in ranks:
    A5[name] = {k: {"point": float(v), "lo": float(np.quantile([b[name][k] for b in boots], .025)),
                    "hi": float(np.quantile([b[name][k] for b in boots], .975))} for k, v in point[name].items()}
diff = [b["s1_recip_nc"]["prec@1000"] - b["journal_J"]["prec@1000"] for b in boots]
A5["primary_comparison_prec@1000_s1_minus_J"] = {"point": float(point["s1_recip_nc"]["prec@1000"] - point["journal_J"]["prec@1000"]),
                                                  "lo": float(np.quantile(diff, .025)), "hi": float(np.quantile(diff, .975))}
run.log("A5_screening", {"base_rate": float(y.mean()), "n": len(y), "positives": int(y.sum()), **A5})
pd.DataFrame([{"ranking": n, "metric": k, **v} for n in ranks for k, v in A5[n].items()]).to_csv(run.dir / "A5_screening.csv", index=False)
run.finish()
