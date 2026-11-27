"""F17 (POSTHOC.md round 6: P18-P19). Outcome attribution through the ORCID iDs in today's Crossref records. P18: the
Frontiers "peer review manipulation network" retractions (Retraction Watch, Frontiers, notices 1 July-30 September 2025,
peer-review/referencing/conflict-of-interest reasons): graph match, ORCID coverage in Meta and Crossref, attached
primary authors and their ranks on the signals. P19: all later-retracted graph publications; primary authors who gain a
later retraction only through Crossref ORCID iDs become positives; primary ORs, R2 classes and S1 lift recomputed.
Frozen scores (hash checked); setup code of f13/f14. ORCID iDs stay in memory; aggregates only.
usage: CROSSREF_MAILTO=<optional> python f17_attribution.py RUN_ID F05_RUN [n_boot]
"""
import json, os, sys, time, zlib, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
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

# --- P18/P19 ------------------------------------------------------------------------------------------------------------
T0_, END_ = pd.Timestamp(T0), pd.Timestamp(END)
RWP, RWI = D_WORK / f"rw_papers_{RW_RUN}.parquet", D_WORK / f"rw_iid_{M_RUN}.parquet"
labx = con.execute(f"""SELECT ri.iid, min(r.notice_date) AS first_notice, flatten(list(r.reasons)) AS reasons,
       min(lower(r.doi)) AS doi FROM read_parquet('{RWI}') ri JOIN read_parquet('{RWP}') r USING (key)
       WHERE NOT coalesce(r.reinstated, false) GROUP BY 1""").df()
labx = labx[(labx.first_notice > T0_) & (labx.first_notice <= END_)].reset_index(drop=True)
labx["reasons"] = labx.reasons.map(lambda r: set(r) if r is not None else set())
labx["c_refpeer"] = labx.reasons.map(lambda r: bool(r & REFPEER)); labx["c_mill"] = labx.reasons.map(lambda r: "Paper Mill" in r)
labx["c_misc"] = labx.reasons.map(lambda r: bool(r & MISCONDUCT)); labx["c_honest"] = labx.reasons.map(lambda r: any(honest(s) for s in r))
FRS = {"Compromised Peer Review", "Concerns/Issues about Peer Review", "Concerns/Issues about Referencing/Attributions", "Conflict of Interest"}
fr = con.execute(f"""SELECT r.key, r.doi, r.notice_date, r.reasons, ri.iid FROM read_parquet('{RWP}') r
       LEFT JOIN read_parquet('{RWI}') ri USING (key)
       WHERE r.publisher ILIKE '%frontiers%' AND r.notice_date BETWEEN TIMESTAMP '2025-07-01' AND TIMESTAMP '2025-09-30 23:59:59'""").df()
fr = fr[fr.reasons.map(lambda r: bool(set(r if r is not None else []) & FRS))]
run.log("P18_selection", {"records": int(fr.key.nunique()), "notice_months": fr.notice_date.dt.strftime("%Y-%m").value_counts().sort_index().to_dict(),
                          "matched_to_graph": int(fr.iid.notna().sum()), "distinct_graph_publications": int(fr.iid.dropna().nunique())})

# Crossref ORCID iDs for every later-retracted graph publication (and the Frontiers set)
MAILTO = os.environ.get("CROSSREF_MAILTO", "")
norm = lambda o: o.strip().rstrip("/").split("/")[-1].upper()
def cr(doi):
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi) + (f"?mailto={urllib.parse.quote(MAILTO)}" if MAILTO else "")
    for a in range(6):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "F-attribution-check/1.0" + (f" (mailto:{MAILTO})" if MAILTO else "")})
            m = json.load(urllib.request.urlopen(req, timeout=60))["message"]
            return ("ok", [norm(x["ORCID"]) for x in (m.get("author") or []) if x.get("ORCID")], len(m.get("author") or []))
        except urllib.error.HTTPError as e:
            if e.code == 404: return ("not_found", [], 0)
            time.sleep(3 * (a + 1))
        except Exception:
            time.sleep(3 * (a + 1))
    return ("error", [], 0)
dois = sorted(set(labx.doi.dropna()) | set(fr.doi.dropna().str.lower()))
t0 = time.time()
with ThreadPoolExecutor(8) as ex:
    res = dict(zip(dois, ex.map(cr, dois)))
run.log("crossref", {"dois": len(dois), "status": pd.Series([v[0] for v in res.values()]).value_counts().to_dict(),
                     "seconds": round(time.time() - t0, 1), "polite_pool": bool(MAILTO), "retrieved": time.strftime("%Y-%m-%d")})
amap = con.execute(f"SELECT aid, orcid FROM read_parquet('{F_DATA / 'aid_map.parquet'}')").df()
amap["orcid"] = amap.orcid.map(norm); o2a = dict(zip(amap.orcid, amap.aid))
prim_aids = set(d.aid.values)
def cr_links(frame):
    rows = [(i, o2a[o]) for i, doi in zip(frame.iid, frame.doi) if isinstance(doi, str) for o in res.get(doi.lower(), ("", [], 0))[1] if o in o2a]
    return pd.DataFrame(rows, columns=["iid", "aid"]).drop_duplicates()
slots = con.execute(f"SELECT DISTINCT iid, aid FROM read_parquet('{F_DATA / 'orcid_slots.parquet'}')").df()
meta_l = slots[slots.iid.isin(set(labx.iid))]
cr_l = cr_links(labx)
new_l = cr_l.merge(meta_l, on=["iid", "aid"], how="left", indicator=True); new_l = new_l[new_l["_merge"] == "left_only"][["iid", "aid"]]
cov = {"later_publications": len(labx), "with_doi": int(labx.doi.notna().sum()),
       "with_meta_orcid": int(labx.iid.isin(set(meta_l.iid)).sum()),
       "with_crossref_orcid": int(labx.doi.map(lambda x: isinstance(x, str) and len(res.get(x, ("", [], 0))[1]) > 0).sum()),
       "with_either": int((labx.iid.isin(set(meta_l.iid)) | labx.doi.map(lambda x: isinstance(x, str) and len(res.get(x, ("", [], 0))[1]) > 0)).sum()),
       "crossref_links_to_any_author": len(cr_l), "crossref_only_links": len(new_l),
       "crossref_only_links_primary": int(new_l.aid.isin(prim_aids).sum())}
run.log("P19_coverage", cov)

# augmented outcome for the primary population (population unchanged)
links = pd.concat([meta_l, new_l]).drop_duplicates()
lk = links[links.aid.isin(prim_aids)].merge(labx[["iid", "c_refpeer", "c_mill", "c_misc", "c_honest"]], on="iid")
g2 = lk.groupby("aid")
oa = pd.DataFrame({"y": g2.size() > 0, "y_refpeer": g2.c_refpeer.any(), "y_mill": g2.c_mill.any(), "y_misc_spec": g2.c_misc.any(),
                   "y_err_only": g2.apply(lambda q: bool((q.c_honest & ~q.c_refpeer & ~q.c_mill & ~q.c_misc).all()))})
YA = d[["aid"]].merge(oa, left_on="aid", right_index=True, how="left").set_index("aid").fillna(False).astype(bool)
added = YA.y.values & ~y.y.values
run.log("P19_outcome", {"positives_meta": int(y.y.sum()), "positives_augmented": int(YA.y.sum()), "added": int(added.sum()),
                        "lost": int((~YA.y.values & y.y.values).sum()),
                        "by_class_augmented": {c: int(YA[c].sum()) for c in ["y_refpeer", "y_mill", "y_misc_spec", "y_err_only"]}})
def ratio(o1, b1, o2, b2):
    r = {"or_refpeer": o1.get("or_mh"), "or_err_only": o2.get("or_mh")}
    if not o1.get("or_mh") or not o2.get("or_mh"): return {**r, "ratio": None}
    ok = np.isfinite(b1) & np.isfinite(b2) & (b2 > 0); rb = b1[ok] / b2[ok]
    return {**r, "ratio": o1["or_mh"] / o2["or_mh"], "cl_lo": float(np.quantile(rb, .025)), "cl_hi": float(np.quantile(rb, .975))}
res19 = {k: mh_boot("primary", e, YA.y.values)[0] for k, e in F.items()}
a1, b1_ = mh_boot("primary", F["r2"], YA.y_refpeer.values); a2, b2_ = mh_boot("primary", F["r2"], YA.y_err_only.values)
res19["r2|y_refpeer"], res19["r2|y_err_only"], res19["r2|ratio"] = a1, a2, ratio(a1, b1_, a2, b2_)
for st in ["P1_randties", "P6_randties"]:
    for k in ["top_s1_recip_nc", "top_s4_conc5", "top_s5_self", "r2", "r3"]:
        res19[f"{st}|{k}"] = mh_boot(st, F[k], YA.y.values)[0]
u = np.random.default_rng(SEED).random(N)
o_s1 = np.lexsort((u, -np.nan_to_num(d.s1_recip_nc.values.astype(float), nan=-np.inf)))
lift = lambda yv: float(yv[o_s1[:10000]].mean() / yv.mean())
res19["s1_lift10000"] = {"meta": lift(y.y.values.astype(float)), "augmented": lift(YA.y.values.astype(float))}
run.log("P19_estimates", res19)

# P18: the Frontiers set
fr_i = fr.dropna(subset=["iid"]).drop_duplicates("iid"); fr_i = fr_i.assign(iid=fr_i.iid.astype("int64"))
fm = slots[slots.iid.isin(set(fr_i.iid))]
fc = cr_links(fr_i.assign(doi=fr_i.doi.str.lower()))
fc_only = fc.merge(fm, on=["iid", "aid"], how="left", indicator=True); fc_only = fc_only[fc_only["_merge"] == "left_only"][["iid", "aid"]]
pr = {c: pd.Series(d[c].astype(float).values, index=d.aid).rank(pct=True) for c in ["s1_recip_nc", "s4_conc5"]}
flags_by_aid = {k: pd.Series(F[k], index=d.aid) for k in ["top_s1_recip_nc", "top_s4_conc5", "top_s5_self", "r2", "r3"]}
def prof(aids):
    aids = [a for a in set(aids) if a in prim_aids]
    if not aids: return {"authors": 0}
    out = {"authors": len(aids), "already_positive_via_meta": int(y.y.loc[aids].sum())}
    for c in pr:
        q = pr[c].loc[aids]; out[f"pct_{c}_q25_50_75"] = [float(q.quantile(x)) for x in (.25, .5, .75)]
    for k, s_ in flags_by_aid.items(): out[f"share_{k}"] = float(s_.loc[aids].mean())
    return out
run.log("P18_frontiers", {
    "graph_publications": int(fr_i.iid.nunique()),
    "with_meta_orcid": int(fr_i.iid.isin(set(fm.iid)).sum()),
    "with_crossref_orcid": int(fr_i.doi.str.lower().map(lambda x: len(res.get(x, ("", [], 0))[1]) > 0).sum()),
    "crossref_authors_per_paper_median": float(fr_i.doi.str.lower().map(lambda x: res.get(x, ("", [], 0))[2]).median()),
    "primary_authors_via_meta": prof(fm.aid), "primary_authors_via_crossref_only": prof(fc_only.aid),
    "reference_shares_primary": {k: float(v.mean()) for k, v in flags_by_aid.items()}})
run.finish()
