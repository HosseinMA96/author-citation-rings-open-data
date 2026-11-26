"""F11 (POST HOC P10a, POSTHOC.md round 2): ORCID coverage of biomedical publications by Meta publisher, 2019-2023,
and a deterministic sample of 100 biomedical DOIs per year 2018-2023 (for the Crossref comparison, f11_crossref.py,
run on the laptop). Aggregates and public paper DOIs only. usage: python f11_coverage.py RUN_ID
"""
import sys
from common import Run, C_WORK, D_WORK, F_DATA, META_DIR, duck

run = Run(sys.argv[1], __file__, {"years": [2018, 2023], "sample_per_year": 100, "sample_order": "hash(iid, 20261126)"})
con = duck(); x = con.execute
x(f"""CREATE TABLE mp AS SELECT regexp_extract(id, 'omid:(br/[0-9]+)', 1) AS omid,
        trim(regexp_replace(coalesce(publisher, ''), '\\s*\\[.*$', '')) AS publisher
      FROM read_csv('{META_DIR}/*.csv', header=true, all_varchar=true, parallel=true, delim=',', quote='"', escape='"',
           columns={{'id':'VARCHAR','title':'VARCHAR','author':'VARCHAR','issue':'VARCHAR','volume':'VARCHAR','venue':'VARCHAR',
                     'page':'VARCHAR','pub_date':'VARCHAR','type':'VARCHAR','publisher':'VARCHAR','editor':'VARCHAR'}})""")
x(f"""CREATE TABLE bn AS SELECT p.iid, p.pub_year AS y, m.publisher, coalesce(a.n_auth, 0) AS n_auth, coalesce(a.n_orcid, 0) AS n_orcid
      FROM read_parquet('{C_WORK / 'pubs_slim.parquet'}') p JOIN read_parquet('{F_DATA / 'bio.parquet'}') b USING (iid)
      LEFT JOIN mp m USING (omid) LEFT JOIN read_parquet('{F_DATA / 'paper_auth.parquet'}') a USING (iid)
      WHERE p.pub_year BETWEEN 2018 AND 2023""")
tot = x("""SELECT y, count(*), count(*) FILTER (n_orcid > 0), sum(n_auth), sum(n_orcid), count(*) FILTER (publisher = '')
           FROM bn GROUP BY 1 ORDER BY 1""").fetchall()
run.log("by_year", [dict(zip(["year", "papers", "with_orcid", "slots", "orcid_slots", "no_publisher"], r)) for r in tot])
top = [r[0] for r in x("SELECT publisher, count(*) k FROM bn WHERE y = 2022 GROUP BY 1 ORDER BY k DESC LIMIT 15").fetchall()]
con.register("top", __import__("pandas").DataFrame({"publisher": top}))
pub = x("""SELECT publisher, y, count(*) AS papers, count(*) FILTER (n_orcid > 0) AS with_orcid
           FROM bn JOIN top USING (publisher) WHERE y BETWEEN 2019 AND 2023 GROUP BY ALL ORDER BY publisher, y""").df()
pub.to_csv(run.dir / "coverage_by_publisher.csv", index=False)
run.log("top15_publishers_2022", top)
# share of the 2019 -> 2022 drop in papers with >= 1 ORCID author attributable to each top publisher (counts)
run.log("coverage_by_publisher_rows", len(pub))
smp = x(f"""SELECT y AS year, doi, n_auth, n_orcid FROM (
              SELECT bn.y, i.id AS doi, bn.n_auth, bn.n_orcid,
                     row_number() OVER (PARTITION BY bn.y ORDER BY hash(bn.iid, 20261126), bn.iid) AS rn
              FROM bn JOIN (SELECT iid, min(id) AS id FROM read_parquet('{D_WORK / 'idmap.parquet'}') WHERE id_type = 'doi'
                            AND iid IS NOT NULL GROUP BY 1) i USING (iid)
              WHERE bn.n_auth > 0) WHERE rn <= 100 ORDER BY year, rn""").df()
smp.to_csv(run.dir / "doi_sample.csv", index=False)
run.log("doi_sample", {"rows": len(smp), "meta_share_with_orcid_by_year": smp.groupby("year").apply(lambda d: float((d.n_orcid > 0).mean())).to_dict()})
run.finish()
