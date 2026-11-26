"""F5: frozen author scores (SPEC.md §4). Reads NO post-T0 label: the Retraction Watch status is cut at T0 = 2024-01-31
when it is loaded (used only for the prior-retraction flag and the journal-risk baseline, both pre-T0 information).
Output (VM only): $F_DATA/f05/<RUN_ID>/scores.parquet, sorted by aid; its SHA-256 goes into run.json (frozen).
The run folder gets descriptive counts and score quantiles only.
usage: python f05_scores.py RUN_ID F03_RUN [TEST]     (TEST: 1% of authors, by aid % 100 = 0)
"""
import sys
from pathlib import Path
import score_lib
from common import Run, C_WORK, D_WORK, F_DATA, F_ROOT, duck, sha256

F03 = sys.argv[2]; TEST = len(sys.argv) > 3 and sys.argv[3] == "TEST"
T0 = "2024-01-31"
RW_RUN, M_RUN = "d02_rw_20261101_01", "d05_match_20261101_02"
P = {"W0": 2014, "W1": 2023, "min_bio": 5, "active_from": 2019, "min_cw": 20, "T0s": [T0, "2023-09-30"], "m": 100,
     "aid_mod": 100 if TEST else 1}
spec = F_ROOT / "SPEC.md"
out = F_DATA / "f05" / sys.argv[1]; out.mkdir(parents=True, exist_ok=False)
run = Run(sys.argv[1], __file__, {"params": P, "f03_run": F03, "rw_run": RW_RUN, "match_run": M_RUN, "test": TEST,
                                   "spec_sha256": sha256(spec), "score_lib_sha256": sha256(Path(__file__).parent / "score_lib.py"),
                                   "inputs": {"edges": str(C_WORK / "edges.parquet"), "pubs_slim": str(C_WORK / "pubs_slim.parquet"),
                                              "pubs_j": str(C_WORK / "pubs_j.parquet"), "slots": str(F_DATA / "orcid_slots.parquet"),
                                              "paper_auth": str(F_DATA / "paper_auth.parquet"), "bio": str(F_DATA / "bio.parquet")}})
f03 = __import__("json").loads((F_ROOT / f"experiments/f03_authors/runs/{F03}/run.json").read_text())
run.log("f03_outputs_present", all((F_DATA / f"{n}.parquet").exists() for n in ["orcid_slots", "paper_auth", "bio"]))
DB = out / "scratch.duckdb"
con = duck(path=DB)
x = con.execute; one = lambda s: x(s).fetchall()[0][0]

x(f"""CREATE TABLE nodes AS SELECT p.iid, CAST(p.pub_year AS INTEGER) AS y, j.journal_id AS jid, (b.iid IS NOT NULL) AS bio
      FROM read_parquet('{C_WORK / 'pubs_slim.parquet'}') p LEFT JOIN read_parquet('{C_WORK / 'pubs_j.parquet'}') j USING (iid)
      LEFT JOIN read_parquet('{F_DATA / 'bio.parquet'}') b USING (iid)""")
x(f"CREATE TABLE slots AS SELECT DISTINCT iid, aid FROM read_parquet('{F_DATA / 'orcid_slots.parquet'}')")
x(f"CREATE TABLE pauth AS SELECT iid, n_auth FROM read_parquet('{F_DATA / 'paper_auth.parquet'}')")
x(f"CREATE VIEW edges AS SELECT citing_iid, cited_iid FROM read_parquet('{C_WORK / 'edges.parquet'}')")
# Retraction Watch status CUT AT T0 here (retractions only, reinstated excluded): nothing after T0 enters this script
x(f"""CREATE TABLE stat AS SELECT ri.iid, min(r.notice_date) AS first_notice
      FROM read_parquet('{D_WORK / f'rw_iid_{M_RUN}.parquet'}') ri JOIN read_parquet('{D_WORK / f'rw_papers_{RW_RUN}.parquet'}') r USING (key)
      WHERE NOT coalesce(r.reinstated, false) GROUP BY 1 HAVING min(r.notice_date) <= TIMESTAMP '{T0}'""")
run.log("stat_rows_cut_at_T0", one("SELECT count(*) FROM stat"))
run.log("stat_max_notice", str(one("SELECT max(first_notice) FROM stat")))

cols = score_lib.build(con, P)
for t in ["lin", "cwf", "rw", "lk", "win"]:
    run.log(f"rows_{t}", one(f"SELECT count(*) FROM {t}"))
run.log("authors_pre_eligible", one("SELECT count(*) FROM scores"))
run.log("authors_eligible", one("SELECT count(*) FROM scores WHERE eligible"))
run.log("authors_eligible_prior_T0", one("SELECT count(*) FROM scores WHERE eligible AND prior_0"))
run.log("authors_primary", one("SELECT count(*) FROM scores WHERE eligible AND NOT prior_0"))
run.log("primary_by_band", dict(x("SELECT band, count(*) FROM scores WHERE eligible AND NOT prior_0 GROUP BY 1 ORDER BY 1").fetchall()))
run.log("primary_without_main_journal", one("SELECT count(*) FROM scores WHERE eligible AND NOT prior_0 AND jid_main IS NULL"))
run.log("primary_distinct_main_journals", one("SELECT count(DISTINCT jid_main) FROM scores WHERE eligible AND NOT prior_0"))
qs = [0.01, 0.1, 0.25, 0.5, 0.75, 0.9, 0.99]
desc = {}
for c in ["s1_recip_nc", "s2_recip", "s3_pact", "s4_conc5", "s5_self", "s6_co", "s7_ch2", "s8_burst", "nci_adj", "J_0",
          "n_cw_nc", "n_in", "h", "team"]:
    desc[c] = {"n_nonnull": one(f"SELECT count({c}) FROM scores WHERE eligible AND NOT prior_0"),
               "quantiles": [round(float(v), 6) for v in one(f"SELECT quantile_cont({c}, {qs}) FROM scores WHERE eligible AND NOT prior_0")],
               "mean": round(float(one(f"SELECT avg({c}) FROM scores WHERE eligible AND NOT prior_0")), 6)}
run.log("primary_score_quantiles", {"q": qs, **desc})
run.log("primary_rule_hits", dict(zip(["r1", "r2", "r3", "r_ge3", "r_ge6"], x("""SELECT count(*) FILTER (r1), count(*) FILTER (r2),
        count(*) FILTER (r3), count(*) FILTER (r_score >= 3), count(*) FILTER (r_score >= 6) FROM scores WHERE eligible AND NOT prior_0""").fetchall()[0])))
f = out / "scores.parquet"
x(f"COPY (SELECT * FROM scores ORDER BY aid) TO '{f}' (FORMAT parquet, COMPRESSION zstd)")
run.log("scores_frozen", {"path": str(f), "sha256": sha256(f), "rows": one(f"SELECT count(*) FROM read_parquet('{f}')"),
                          "columns": cols})
con.close(); DB.unlink(missing_ok=True)
run.finish()
