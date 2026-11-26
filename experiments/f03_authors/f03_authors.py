"""F3: author identities in OpenCitations Meta (ORCID coverage and disambiguation) and population sizes.
Coverage, identity checks and label COUNTS only. No ring score is computed and nothing is cross-tabulated with
post-T0 outcomes (that waits for the frozen specification, F4).

Meta deduplicates people only by ORCID (Massari et al. 2024), so the author identity in F is the ORCID iD.
Outputs (large, VM only, in $F_DATA): orcid_slots.parquet (iid, pos, n_auth, aid), paper_auth.parquet
(iid, n_auth, n_orcid), aid_map.parquet (aid, orcid; never leaves the VM), bio.parquet (iid).
The run folder gets counts only.
usage: python f03_authors.py RUN_ID [TEST]      (TEST: only Meta files 1000-1099, no edge pass)
"""
import sys
from common import Run, C_WORK, D_WORK, META_DIR, F_DATA, duck

TEST = len(sys.argv) > 2 and sys.argv[2] == "TEST"
T0, END = "2024-01-31", "2026-10-30"
WIN = (2014, 2023)            # descriptive author window (proposal for F4; counts only here)
RW_RUN, M_RUN = "d02_rw_20261101_01", "d05_match_20261101_02"
glob = str(META_DIR / ("10[0-9][0-9].csv" if TEST else "*.csv"))
out = F_DATA / ("test" if TEST else "")
out.mkdir(parents=True, exist_ok=True)
run = Run(sys.argv[1], __file__, {"meta_glob": glob, "pubs_slim": str(C_WORK / "pubs_slim.parquet"),
                                   "pubs_j": str(C_WORK / "pubs_j.parquet"), "edges": str(C_WORK / "edges.parquet"),
                                   "idmap": str(D_WORK / "idmap.parquet"), "pubmed": str(D_WORK / "pubmed26.parquet"),
                                   "rw_run": RW_RUN, "match_run": M_RUN, "T0": T0, "end": END, "window": WIN,
                                   "test": TEST, "out": str(out)})
DB = out / f"f03_{sys.argv[1]}.duckdb"   # scratch database (slots table is ~0.5 billion rows); deleted at the end
con = duck(path=DB)
q = lambda s: con.execute(s).fetchall()
one = lambda s: q(s)[0][0]
ORCID_RE = r"orcid:([0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X])"

# --- 1. Parse every author slot of every Meta record (identifiers only; names are dropped here) ------------
# RFC 4180 quoting set explicitly (the sniffer misses doubled quotes on small file subsets).
CSV = f"""read_csv('{glob}', header=true, all_varchar=true, parallel=true, delim=',', quote='"', escape='"',
                columns={{'id':'VARCHAR','title':'VARCHAR','author':'VARCHAR','issue':'VARCHAR','volume':'VARCHAR',
                          'venue':'VARCHAR','page':'VARCHAR','pub_date':'VARCHAR','type':'VARCHAR','publisher':'VARCHAR',
                          'editor':'VARCHAR'}})"""
run.log("meta_records", dict(zip(["rows", "rows_with_author"], q(f"SELECT count(*), count(*) FILTER (author IS NOT NULL AND author <> '') FROM {CSV}")[0])))
con.execute(f"""
CREATE TABLE slots AS
WITH m AS (
  SELECT regexp_extract(id, 'omid:(br/[0-9]+)', 1) AS omid, string_split(author, '; ') AS a
  FROM {CSV}
  WHERE author IS NOT NULL AND author <> ''),
s AS (SELECT omid, len(a) AS n_auth, unnest(range(1, len(a) + 1)) AS pos, unnest(a) AS s FROM m)
SELECT omid, CAST(n_auth AS SMALLINT) AS n_auth, CAST(pos AS SMALLINT) AS pos,
       regexp_extract(s, 'omid:(ra/[0-9]+)', 1) AS ra, NULLIF(regexp_extract(s, '{ORCID_RE}', 1), '') AS orcid
FROM s""")
run.log("records_with_authors", one("SELECT count(DISTINCT omid) FROM slots"))
run.log("author_slots", one("SELECT count(*) FROM slots"))
run.log("slots_with_orcid", one("SELECT count(*) FROM slots WHERE orcid IS NOT NULL"))
run.log("slots_without_ra_omid", one("SELECT count(*) FROM slots WHERE ra = ''"))
run.log("slots_orcid_token_unparsed", one("""SELECT count(*) FROM slots WHERE orcid IS NULL AND ra <> ''
                                            AND ra IN (SELECT ra FROM slots WHERE orcid IS NOT NULL)"""))
run.log("records_with_ge1_orcid", one("SELECT count(DISTINCT omid) FROM slots WHERE orcid IS NOT NULL"))
run.log("records_same_orcid_twice", one("""SELECT count(*) FROM (SELECT omid, orcid FROM slots WHERE orcid IS NOT NULL
                                          GROUP BY ALL HAVING count(*) > 1)"""))

# --- 2. Identity checks -----------------------------------------------------------------------------------
run.log("distinct_orcid", one("SELECT count(DISTINCT orcid) FROM slots WHERE orcid IS NOT NULL"))
run.log("orcid_with_several_ra_omids", one("""SELECT count(*) FROM (SELECT orcid FROM slots WHERE orcid IS NOT NULL
                                             GROUP BY 1 HAVING count(DISTINCT ra) > 1)"""))
run.log("ra_omid_with_several_orcids", one("""SELECT count(*) FROM (SELECT ra FROM slots WHERE orcid IS NOT NULL
                                             GROUP BY 1 HAVING count(DISTINCT orcid) > 1)"""))
# Non-ORCID people: is an ra OMID ever reused across records? Exact on a 2% sample of ra OMIDs (sampled by key,
# so every record of a sampled OMID is included).
con.execute("""CREATE TABLE nos AS SELECT ra, count(DISTINCT omid) AS recs FROM slots
               WHERE orcid IS NULL AND ra <> '' AND hash(ra) % 50 = 0 GROUP BY 1""")
run.log("non_orcid_ra_sample_2pct", {"ra_omids": one("SELECT count(*) FROM nos"),
                                     "in_1_record": one("SELECT count(*) FROM nos WHERE recs = 1"),
                                     "in_2plus_records": one("SELECT count(*) FROM nos WHERE recs >= 2"),
                                     "max_records": one("SELECT max(recs) FROM nos")})
con.execute("""CREATE TABLE os AS SELECT orcid, count(DISTINCT omid) AS recs FROM slots WHERE orcid IS NOT NULL GROUP BY 1""")
run.log("orcid_records_quantiles", q("SELECT quantile_disc(recs, [0.5, 0.75, 0.9, 0.99]) FROM os")[0][0])

# --- 3. Records -> graph nodes; biomedical set (as D5: PMID in Meta, or DOI in the PubMed baseline) -------
con.execute(f"CREATE TABLE pubs AS SELECT iid, omid, pub_year FROM read_parquet('{C_WORK / 'pubs_slim.parquet'}')")
con.execute(f"""CREATE TABLE bio AS
   SELECT DISTINCT iid FROM read_parquet('{D_WORK / 'idmap.parquet'}') WHERE id_type = 'pmid' AND iid IS NOT NULL
   UNION SELECT DISTINCT i.iid FROM read_parquet('{D_WORK / 'idmap.parquet'}') i
         JOIN (SELECT DISTINCT doi FROM read_parquet('{D_WORK / 'pubmed26.parquet'}') WHERE doi IS NOT NULL) d
         ON i.id_type = 'doi' AND i.id = d.doi AND i.iid IS NOT NULL""")
run.log("biomedical_nodes", one("SELECT count(*) FROM bio"))
con.execute("""CREATE TABLE aid_map AS SELECT row_number() OVER (ORDER BY orcid) AS aid, orcid
               FROM (SELECT DISTINCT orcid FROM slots WHERE orcid IS NOT NULL)""")
con.execute("""CREATE TABLE oslots AS SELECT DISTINCT p.iid, s.pos, s.n_auth, a.aid FROM slots s JOIN pubs p USING (omid)
               JOIN aid_map a USING (orcid)""")
con.execute("""CREATE TABLE pauth AS SELECT p.iid, max(s.n_auth) AS n_auth, count(DISTINCT s.orcid) AS n_orcid
               FROM slots s JOIN pubs p USING (omid) GROUP BY 1""")
run.log("graph_nodes", one("SELECT count(*) FROM pubs"))
run.log("graph_nodes_with_authors", one("SELECT count(*) FROM pauth"))
run.log("graph_nodes_with_ge1_orcid", one("SELECT count(*) FROM pauth WHERE n_orcid > 0"))
run.log("orcid_slots_on_graph_nodes", one("SELECT count(*) FROM oslots"))
run.log("orcid_on_graph_nodes", one("SELECT count(DISTINCT aid) FROM oslots"))
run.log("iids_with_same_aid_twice", one("SELECT count(*) FROM (SELECT iid, aid FROM oslots GROUP BY ALL HAVING count(*) > 1)"))

# --- 4. Coverage of biomedical nodes by publication year ---------------------------------------------------
run.log("bio_coverage_by_year", [dict(zip(["year", "papers", "with_authors", "slots", "orcid_slots", "with_ge1_orcid",
                                            "mean_n_auth"], r)) for r in q("""
   SELECT p.pub_year, count(*), count(a.iid), sum(a.n_auth), sum(a.n_orcid), count(*) FILTER (a.n_orcid > 0),
          round(avg(a.n_auth), 2)
   FROM bio b JOIN pubs p USING (iid) LEFT JOIN pauth a USING (iid)
   WHERE p.pub_year BETWEEN 2000 AND 2024 GROUP BY 1 ORDER BY 1""")])
run.log("all_nodes_coverage_2014_2023", q(f"""
   SELECT count(*), count(a.iid), sum(a.n_auth), sum(a.n_orcid), count(*) FILTER (a.n_orcid > 0)
   FROM pubs p LEFT JOIN pauth a USING (iid) WHERE p.pub_year BETWEEN {WIN[0]} AND {WIN[1]}""")[0])

# --- 5. ORCID authors' activity in the window (biomedical papers) -----------------------------------------
con.execute(f"""CREATE TABLE act AS SELECT o.aid, count(DISTINCT o.iid) AS n_bio, min(p.pub_year) AS first_y,
                max(p.pub_year) AS last_y FROM oslots o JOIN bio USING (iid) JOIN pubs p USING (iid)
                WHERE p.pub_year BETWEEN {WIN[0]} AND {WIN[1]} GROUP BY 1""")
run.log("orcid_with_bio_papers_in_window", one("SELECT count(*) FROM act"))
run.log("orcid_by_min_bio_papers", {k: one(f"SELECT count(*) FROM act WHERE n_bio >= {k}") for k in (1, 3, 5, 10, 20, 50, 100)})
run.log("orcid_ge5_and_active_2019_2023", one("SELECT count(*) FROM act WHERE n_bio >= 5 AND last_y >= 2019"))
run.log("orcid_n_bio_quantiles", q("SELECT quantile_disc(n_bio, [0.5, 0.75, 0.9, 0.99, 0.999]) FROM act")[0][0])

# --- 6. Label coverage (counts only; Retraction Watch frozen copy, D matching) -----------------------------
con.execute(f"""CREATE TABLE lab AS
   SELECT ri.iid, min(r.notice_date) AS first_notice,
          bool_or(list_contains(r.reasons, 'Paper Mill')) AS mill,
          bool_or(len(list_filter(r.reasons, x -> x IN ('Concerns/Issues about Referencing/Attributions',
              'Compromised Peer Review', 'Concerns/Issues about Peer Review', 'Rogue Editor'))) > 0) AS refpeer
   FROM read_parquet('{D_WORK / f'rw_iid_{M_RUN}.parquet'}') ri
   JOIN read_parquet('{D_WORK / f'rw_papers_{RW_RUN}.parquet'}') r USING (key)
   WHERE NOT coalesce(r.reinstated, false) GROUP BY 1""")
run.log("retracted_nodes", one("SELECT count(*) FROM lab"))
run.log("retracted_bio_nodes_by_period_with_orcid", q(f"""
   SELECT l.first_notice > TIMESTAMP '{T0}' AS after_T0, count(*), count(a.iid) FILTER (a.n_orcid > 0)
   FROM lab l JOIN bio USING (iid) LEFT JOIN pauth a USING (iid) GROUP BY 1 ORDER BY 1"""))
con.execute(f"""CREATE TABLE alab AS SELECT o.aid,
       bool_or(l.first_notice <= TIMESTAMP '{T0}') AS any_by_T0,
       bool_or(l.first_notice > TIMESTAMP '{T0}' AND l.first_notice <= TIMESTAMP '{END}') AS any_after_T0,
       bool_or(l.first_notice > TIMESTAMP '{T0}' AND l.first_notice <= TIMESTAMP '{END}' AND l.mill) AS mill_after_T0,
       bool_or(l.first_notice > TIMESTAMP '{T0}' AND l.first_notice <= TIMESTAMP '{END}' AND l.refpeer) AS refpeer_after_T0
   FROM oslots o JOIN lab l USING (iid) GROUP BY 1""")
for k in (1, 5, 10):
    run.log(f"label_counts_orcid_n_bio_ge{k}", dict(zip(["authors", "any_by_T0", "after_T0", "after_T0_not_by_T0",
                                                         "mill_after_T0", "refpeer_after_T0"], q(f"""
       SELECT count(*), count(*) FILTER (alab.any_by_T0), count(*) FILTER (alab.any_after_T0),
              count(*) FILTER (alab.any_after_T0 AND NOT coalesce(alab.any_by_T0, false)),
              count(*) FILTER (alab.mill_after_T0), count(*) FILTER (alab.refpeer_after_T0)
       FROM act LEFT JOIN alab USING (aid) WHERE act.n_bio >= {k}""")[0])))

# --- 7. Citation volume between ORCID-identified papers (sizes for F5; no scores) -------------------------
if not TEST:   # one streaming pass over the 1.96 billion edges; nothing is materialised
    con.execute("""CREATE TABLE node AS SELECT p.iid, p.pub_year, (b.iid IS NOT NULL) AS is_bio,
                   CAST(coalesce(a.n_orcid, 0) AS INTEGER) AS n_orcid
                   FROM pubs p LEFT JOIN bio b USING (iid) LEFT JOIN pauth a USING (iid)""")
    run.log("edges_window_volume", dict(zip(["edges_both_ends_in_window", "cited_bio", "cited_bio_with_orcid",
                                             "cited_bio_both_orcid", "pair_rows_cited_bio_both_orcid",
                                             "both_bio_both_orcid", "pair_rows_both_bio_both_orcid"], q(f"""
       SELECT count(*), count(*) FILTER (d.is_bio), count(*) FILTER (d.is_bio AND d.n_orcid > 0),
              count(*) FILTER (d.is_bio AND d.n_orcid > 0 AND c.n_orcid > 0),
              sum(CAST(d.n_orcid AS BIGINT) * c.n_orcid) FILTER (d.is_bio AND d.n_orcid > 0 AND c.n_orcid > 0),
              count(*) FILTER (d.is_bio AND c.is_bio AND d.n_orcid > 0 AND c.n_orcid > 0),
              sum(CAST(d.n_orcid AS BIGINT) * c.n_orcid) FILTER (d.is_bio AND c.is_bio AND d.n_orcid > 0 AND c.n_orcid > 0)
       FROM read_parquet('{C_WORK / 'edges.parquet'}') e JOIN node c ON c.iid = e.citing_iid JOIN node d ON d.iid = e.cited_iid
       WHERE c.pub_year BETWEEN {WIN[0]} AND {WIN[1]} AND d.pub_year BETWEEN {WIN[0]} AND {WIN[1]}""")[0])))

# --- 8. Save the identity tables (VM only) -----------------------------------------------------------------
for t, f in [("oslots", "orcid_slots"), ("pauth", "paper_auth"), ("aid_map", "aid_map"), ("bio", "bio")]:
    con.execute(f"COPY (SELECT * FROM {t} ORDER BY ALL) TO '{out / (f + '.parquet')}' (FORMAT parquet, COMPRESSION zstd)")
run.log("saved", {f: str(out / (f + ".parquet")) for f in ["orcid_slots", "paper_auth", "aid_map", "bio"]})
con.close(); DB.unlink()
run.finish()
