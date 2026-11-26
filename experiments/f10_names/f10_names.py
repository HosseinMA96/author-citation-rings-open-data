"""F10 (POST HOC P9, POSTHOC.md round 2): what S1 counts as "outside". Sample of primary authors
(hash(aid, 20261126) % 400 = 0). Their non-self, non-co-author citing works (CW_nc) are rebuilt with the score
library's rules (checked against the frozen S1), then flagged by NAME: the work lists the author's own name key
(hidden self-citation) or a name key of someone listed on the author's papers (hidden co-author; upper bound, common
names over-match). Name key = lower-case family name + first initial, accents removed. Names are used on the VM only;
only aggregates are written. usage: python f10_names.py RUN_ID F05_RUN
"""
import json, re, sys, unicodedata
import numpy as np, pandas as pd
from common import Run, C_WORK, F_DATA, F_ROOT, META_DIR, duck, sha256

SPEC_SHA = "07200ecb9affa9f2bee88b68becba9ad81900d2cfcc1fc759ba814ced61ca3ec"
F05 = sys.argv[2]; W0, W1 = 2014, 2023; THR_S1 = 0.1111111111111111   # population 99th percentile of S1 (f06)
f05 = json.loads((F_ROOT / f"experiments/f05_scores/runs/{F05}/run.json").read_text())
sfile = F_DATA / "f05" / F05 / "scores.parquet"
run = Run(sys.argv[1], __file__, {"f05_run": F05, "sample": "eligible & not prior_0 & hash(aid, 20261126) % 400 = 0",
                                   "posthoc_sha256": sha256(F_ROOT / "POSTHOC.md"), "s1_threshold": THR_S1})
assert sha256(F_ROOT / "SPEC.md") == SPEC_SHA and sha256(sfile) == f05["results"]["scores_frozen"]["sha256"]
DB = F_DATA / f"f10_{sys.argv[1]}.duckdb"
con = duck(path=DB); x = con.execute; one = lambda s: x(s).fetchall()[0][0]
E = C_WORK / "edges.parquet"; PUBS = C_WORK / "pubs_slim.parquet"
x(f"CREATE TABLE samp AS SELECT aid, s1_recip_nc, n_cw_nc FROM read_parquet('{sfile}') WHERE eligible AND NOT prior_0 AND hash(aid, 20261126) % 400 = 0")
x(f"CREATE TABLE nw AS SELECT iid FROM read_parquet('{PUBS}') WHERE pub_year BETWEEN {W0} AND {W1}")
x(f"CREATE TABLE sw AS SELECT DISTINCT s.iid, s.aid, s.pos FROM read_parquet('{F_DATA / 'orcid_slots.parquet'}') s JOIN nw USING (iid)")
x("CREATE TABLE ap AS SELECT s.aid, s.iid, s.pos FROM sw s JOIN samp USING (aid)")
x(f"CREATE TABLE lin AS SELECT ap.aid, e.citing_iid AS p FROM read_parquet('{E}') e JOIN ap ON ap.iid = e.cited_iid JOIN nw c ON c.iid = e.citing_iid")
x("CREATE TABLE co AS SELECT DISTINCT a.aid, b.aid AS bid FROM ap a JOIN sw b ON b.iid = a.iid WHERE b.aid <> a.aid")
x("""CREATE TABLE cwf AS SELECT c.aid, c.p, coalesce(bool_or(s.aid = c.aid), false) AS self,
     coalesce(bool_or(s.aid <> c.aid AND co.bid IS NOT NULL), false) AS coauth
     FROM (SELECT DISTINCT aid, p FROM lin) c LEFT JOIN (SELECT DISTINCT iid, aid FROM sw) s ON s.iid = c.p
     LEFT JOIN co ON co.aid = c.aid AND co.bid = s.aid GROUP BY 1, 2""")
x(f"CREATE TABLE rw AS SELECT DISTINCT ap.aid, e.cited_iid AS r FROM read_parquet('{E}') e JOIN ap ON ap.iid = e.citing_iid JOIN nw d ON d.iid = e.cited_iid")
x("CREATE TABLE cwr AS SELECT f.*, (r.r IS NOT NULL) AS recip FROM cwf f LEFT JOIN rw r ON r.aid = f.aid AND r.r = f.p")
chk = x("""SELECT count(*), count(*) FILTER (abs(s.s1_recip_nc - c.s1) > 1e-12) FROM samp s JOIN (
           SELECT aid, count(*) FILTER (NOT self AND NOT coauth AND recip)::DOUBLE / count(*) FILTER (NOT self AND NOT coauth) AS s1
           FROM cwr GROUP BY 1) c USING (aid)""").fetchall()[0]
run.log("sample_authors", one("SELECT count(*) FROM samp"))
run.log("rebuilt_s1_matches_frozen", {"authors": chk[0], "mismatches": chk[1]})
assert chk[1] == 0, "rebuilt S1 differs from the frozen S1"
x("CREATE TABLE need AS SELECT DISTINCT iid FROM ap UNION SELECT DISTINCT p FROM cwr WHERE NOT self AND NOT coauth")
x(f"CREATE TABLE need_omid AS SELECT n.iid, p.omid FROM need n JOIN read_parquet('{PUBS}') p USING (iid)")
run.log("records_needed", one("SELECT count(*) FROM need_omid"))
x(f"""CREATE TABLE names AS SELECT n.iid, m.author FROM (
       SELECT regexp_extract(id, 'omid:(br/[0-9]+)', 1) AS omid, author
       FROM read_csv('{META_DIR}/*.csv', header=true, all_varchar=true, parallel=true, delim=',', quote='"', escape='"',
            columns={{'id':'VARCHAR','title':'VARCHAR','author':'VARCHAR','issue':'VARCHAR','volume':'VARCHAR','venue':'VARCHAR',
                      'page':'VARCHAR','pub_date':'VARCHAR','type':'VARCHAR','publisher':'VARCHAR','editor':'VARCHAR'}})) m
     JOIN need_omid n USING (omid)""")
run.log("records_with_names", one("SELECT count(*) FROM names WHERE author IS NOT NULL AND author <> ''"))

def norm(s):
    s = unicodedata.normalize("NFKD", s); s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z]", "", s.lower())
def keys(author):
    out = []
    for i, s in enumerate((author or "").split("; "), 1):
        nm = re.sub(r"\s*\[[^\]]*\]\s*$", "", s).strip(); fam, _, giv = nm.partition(", ")
        if fam:
            out.append((i, norm(fam) + "_" + norm(giv)[:1]))
    return out
NK = {iid: keys(a) for iid, a in x("SELECT iid, author FROM names").fetchall()}
AP = x("SELECT aid, iid, pos FROM ap").df()
own, collab = {}, {}
for aid, iid, pos in AP.itertuples(index=False):
    for i, k in NK.get(iid, []):
        (own if i == pos else collab).setdefault(aid, set()).add(k)
CW = x("SELECT aid, p, recip FROM cwr WHERE NOT self AND NOT coauth").df()
hs, hc = np.zeros(len(CW), bool), np.zeros(len(CW), bool)
for r, (aid, p, _) in enumerate(CW.itertuples(index=False)):
    pk = {k for _, k in NK.get(p, [])}; ow = own.get(aid, set())
    hs[r] = bool(pk & ow); hc[r] = bool(pk & (collab.get(aid, set()) - ow))
CW["hidden_self"], CW["hidden_co"] = hs, hc; CW["flag"] = hs | hc
g = CW.groupby("aid").agg(n=("p", "size"), rec=("recip", "sum"), flag=("flag", "sum"),
                          rec_kept=("recip", lambda s: int((s & ~CW.loc[s.index, "flag"]).sum())))
g["s1"] = g.rec / g.n; g["s1_name"] = g.rec_kept / (g.n - g.flag).replace(0, np.nan)
rec = CW[CW.recip]
run.log("P9_shares", {
    "cw_nc_works": len(CW), "share_hidden_self": float(hs.mean()), "share_hidden_co": float(hc.mean()), "share_flagged": float(CW.flag.mean()),
    "reciprocal_cw_nc_works": len(rec), "reciprocal_share_hidden_self": float(rec.hidden_self.mean()),
    "reciprocal_share_hidden_co": float(rec.hidden_co.mean()), "reciprocal_share_flagged": float(rec.flag.mean()),
    "authors_without_own_name_key": int(len(set(g.index) - set(own)))})
run.log("P9_s1_vs_s1_name", {
    "authors": int(len(g)), "spearman": float(g[["s1", "s1_name"]].corr(method="spearman").iloc[0, 1]),
    "median_s1": float(g.s1.median()), "median_s1_name": float(g.s1_name.median()),
    "mean_s1": float(g.s1.mean()), "mean_s1_name": float(g.s1_name.mean()),
    "above_threshold_before": int((g.s1 >= THR_S1).sum()), "above_threshold_after": int((g.s1_name >= THR_S1).sum()),
    "above_before_and_after": int(((g.s1 >= THR_S1) & (g.s1_name >= THR_S1)).sum()),
    "share_of_author_flagged_works_quantiles": [float(v) for v in (g.flag / g.n).quantile([0.25, 0.5, 0.75, 0.9]).values]})
con.close(); DB.unlink(missing_ok=True); DB.with_suffix(".duckdb.wal").unlink(missing_ok=True)
run.finish()
