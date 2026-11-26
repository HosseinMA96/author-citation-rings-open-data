"""F5 score library: author-level citation-ring signals (SPEC.md §4), in DuckDB SQL.

build(con, P) expects these tables/views in `con` (built by f05_scores.py on the VM, or by test_scores.py on a toy graph):
  nodes(iid, y, jid, bio)        every graph node (publication year, journal id or NULL, biomedical flag)
  slots(iid, aid)                ORCID author slots of every graph node (any year); aid = integer author id
  pauth(iid, n_auth)             number of listed authors per node (any identity)
  edges(citing_iid, cited_iid)   citations
  stat(iid, first_notice)        first Retraction Watch notice per node, ALREADY CUT at the latest pre-snapshot date
It creates table `scores` (one row per pre-eligible author). No post-T0 label is read here.
P: dict with W0, W1, min_bio, active_from, min_cw, T0s (list of date strings, all <= the main T0), m.
"""

def build(con, P):
    W0, W1 = P["W0"], P["W1"]
    x = con.execute
    x(f"CREATE TABLE nw AS SELECT iid, y, jid, bio FROM nodes WHERE y BETWEEN {W0} AND {W1}")
    x("CREATE TABLE sw AS SELECT DISTINCT s.iid, s.aid FROM slots s JOIN nw USING (iid)")
    x("""CREATE TABLE act AS SELECT s.aid, count(*) AS n_all, count(*) FILTER (n.bio) AS n_bio,
         min(n.y) AS first_y, max(n.y) AS last_y FROM sw s JOIN nw n USING (iid) GROUP BY 1""")
    x(f"""CREATE TABLE pop0 AS SELECT aid FROM act WHERE n_bio >= {P['min_bio']} AND last_y >= {P['active_from']}
         AND aid % {P.get('aid_mod', 1)} = 0""")
    x("CREATE TABLE ap AS SELECT s.aid, s.iid FROM sw s JOIN pop0 USING (aid)")
    # links into P(a): (aid, p, q), p -> q, q in P(a), p in W
    x("""CREATE TABLE lin AS SELECT ap.aid, e.citing_iid AS p, e.cited_iid AS q
         FROM edges e JOIN ap ON ap.iid = e.cited_iid JOIN nw c ON c.iid = e.citing_iid""")
    # co-authors (ORCID) in W
    x("CREATE TABLE co AS SELECT DISTINCT a.aid, b.aid AS bid FROM ap a JOIN sw b ON b.iid = a.iid WHERE b.aid <> a.aid")
    # citing works with self / co-author flags
    x("""CREATE TABLE cwf AS
         SELECT c.aid, c.p, coalesce(bool_or(s.aid = c.aid), false) AS self,
                coalesce(bool_or(s.aid <> c.aid AND co.bid IS NOT NULL), false) AS coauth
         FROM (SELECT DISTINCT aid, p FROM lin) c
         LEFT JOIN sw s ON s.iid = c.p
         LEFT JOIN co ON co.aid = c.aid AND co.bid = s.aid
         GROUP BY 1, 2""")
    # works in W cited by a's papers, and the reciprocal flag
    x("""CREATE TABLE rw AS SELECT DISTINCT ap.aid, e.cited_iid AS r
         FROM edges e JOIN ap ON ap.iid = e.citing_iid JOIN nw d ON d.iid = e.cited_iid""")
    x("""CREATE TABLE cwr AS SELECT f.aid, f.p, f.self, f.coauth, (r.r IS NOT NULL) AS recip
         FROM cwf f LEFT JOIN rw r ON r.aid = f.aid AND r.r = f.p""")
    x("""CREATE TABLE s_work AS SELECT aid,
           count(*) FILTER (NOT self) AS n_cw,
           count(*) FILTER (NOT self AND NOT coauth) AS n_cw_nc,
           count(*) FILTER (NOT self AND recip) AS n_recip,
           count(*) FILTER (NOT self AND NOT coauth AND recip) AS n_recip_nc
         FROM cwr GROUP BY 1""")
    # pact nodes: ORCID authors b != a with >= 3 reciprocal (non-self) works
    x("""CREATE TABLE s_pact AS SELECT aid, count(*) FILTER (k >= 3) AS pact FROM (
           SELECT c.aid, s.aid AS bid, count(DISTINCT c.p) AS k FROM cwr c JOIN sw s ON s.iid = c.p
           WHERE c.recip AND NOT c.self AND s.aid <> c.aid GROUP BY 1, 2) GROUP BY 1""")
    # link-level counts
    x("CREATE TABLE lk AS SELECT l.aid, l.p, l.q, f.self, f.coauth FROM lin l JOIN cwf f USING (aid, p)")
    x("""CREATE TABLE s_link AS SELECT aid, count(*) AS n_in, count(*) FILTER (self) AS n_self,
           count(*) FILTER (NOT self AND coauth) AS n_co FROM lk GROUP BY 1""")
    # concentration: top-5 citing ORCID authors by non-self links; share of non-self links from works listing any of them
    x("""CREATE TABLE win AS SELECT k.aid, s.aid AS bid, count(*) AS w FROM lk k JOIN sw s ON s.iid = k.p
         WHERE NOT k.self AND s.aid <> k.aid GROUP BY 1, 2""")
    x("""CREATE TABLE top5 AS SELECT aid, bid FROM (SELECT aid, bid, row_number() OVER (PARTITION BY aid ORDER BY w DESC, bid)
         AS rn FROM win) WHERE rn <= 5""")
    x("""CREATE TABLE ptop AS SELECT DISTINCT c.aid, c.p FROM cwf c JOIN sw s ON s.iid = c.p
         JOIN top5 t ON t.aid = c.aid AND t.bid = s.aid WHERE NOT c.self""")
    x("""CREATE TABLE s_conc AS SELECT k.aid, count(*) FILTER (t.p IS NOT NULL) AS n_top5_links
         FROM lk k LEFT JOIN ptop t ON t.aid = k.aid AND t.p = k.p WHERE NOT k.self GROUP BY 1""")
    # h-index over a's papers (links in W, self included)
    x("""CREATE TABLE s_h AS SELECT aid, coalesce(max(rk) FILTER (c >= rk), 0) AS h FROM (
           SELECT aid, c, row_number() OVER (PARTITION BY aid ORDER BY c DESC) AS rk
           FROM (SELECT aid, q, count(*) AS c FROM lin GROUP BY 1, 2)) GROUP BY 1""")
    # publication burst, team size, main journal, productivity
    yrs = ", ".join(f"count(*) FILTER (n.y = {t}) AS n{t}" for t in range(W0, W1 + 1))
    x(f"CREATE TABLE s_year AS SELECT a.aid, {yrs} FROM ap a JOIN nw n USING (iid) GROUP BY 1")
    ratios = ", ".join(f"n{t} / greatest(1, n{t - 1})" for t in range(W0 + 1, W1 + 1))
    x(f"CREATE TABLE s_burst AS SELECT aid, greatest({ratios}) AS burst FROM s_year")
    x("CREATE TABLE s_team AS SELECT a.aid, avg(pa.n_auth) AS team FROM ap a JOIN pauth pa USING (iid) GROUP BY 1")
    x("""CREATE TABLE s_jmain AS SELECT aid, jid AS jid_main FROM (
           SELECT a.aid, n.jid, count(*) AS k, row_number() OVER (PARTITION BY a.aid ORDER BY count(*) DESC, n.jid) AS rn
           FROM ap a JOIN nw n USING (iid) WHERE n.bio AND n.jid IS NOT NULL GROUP BY 1, 2) WHERE rn = 1""")
    # pre-T0 information only: journal risk and prior retraction at each cut date
    jcols, pcols = [], []
    for i, T in enumerate(P["T0s"]):
        x(f"""CREATE TABLE jr{i} AS WITH b AS (
                SELECT n.jid, count(*) AS nj, count(s.iid) FILTER (s.first_notice <= TIMESTAMP '{T}') AS rj
                FROM nodes n LEFT JOIN stat s USING (iid) WHERE n.bio AND n.jid IS NOT NULL AND n.y BETWEEN 2010 AND {W1}
                GROUP BY 1), g AS (SELECT sum(rj) / sum(nj) AS g FROM b)
              SELECT b.jid, (b.rj + {P['m']} * g.g) / (b.nj + {P['m']}) AS rate, g.g FROM b, g""")
        x(f"""CREATE TABLE sj{i} AS SELECT a.aid, avg(coalesce(j.rate, (SELECT any_value(g) FROM jr{i}))) AS J
              FROM ap a JOIN nw n USING (iid) LEFT JOIN jr{i} j ON j.jid = n.jid WHERE n.bio GROUP BY 1""")
        x(f"""CREATE TABLE pr{i} AS SELECT DISTINCT s.aid FROM slots s JOIN pop0 USING (aid)
              JOIN stat t ON t.iid = s.iid WHERE t.first_notice <= TIMESTAMP '{T}'""")
        jcols.append(f"sj{i}.J AS J_{i}"); pcols.append(f"(pr{i}.aid IS NOT NULL) AS prior_{i}")
    jjoin = " ".join(f"LEFT JOIN sj{i} USING (aid) LEFT JOIN pr{i} USING (aid)" for i in range(len(P["T0s"])))
    x(f"""CREATE TABLE scores AS SELECT
           p.aid, a.n_all, a.n_bio, a.first_y, a.last_y,
           CASE WHEN a.n_bio < 10 THEN '05-09' WHEN a.n_bio < 20 THEN '10-19' WHEN a.n_bio < 50 THEN '20-49' ELSE '50+' END AS band,
           j.jid_main,
           coalesce(w.n_cw, 0) AS n_cw, coalesce(w.n_cw_nc, 0) AS n_cw_nc, coalesce(w.n_recip, 0) AS n_recip,
           coalesce(w.n_recip_nc, 0) AS n_recip_nc,
           CAST(w.n_recip_nc AS DOUBLE) / nullif(w.n_cw_nc, 0) AS s1_recip_nc,
           CAST(w.n_recip AS DOUBLE) / nullif(w.n_cw, 0) AS s2_recip,
           coalesce(pc.pact, 0) AS s3_pact,
           CAST(c.n_top5_links AS DOUBLE) / nullif(l.n_in - l.n_self, 0) AS s4_conc5,
           coalesce(l.n_in, 0) AS n_in, coalesce(l.n_self, 0) AS n_self, coalesce(l.n_co, 0) AS n_co,
           CAST(l.n_self AS DOUBLE) / nullif(l.n_in, 0) AS s5_self,
           CAST(l.n_co AS DOUBLE) / nullif(l.n_in, 0) AS s6_co,
           coalesce(h.h, 0) AS h,
           CAST(l.n_in AS DOUBLE) / nullif(h.h * h.h, 0) AS s7_ch2,
           b.burst AS s8_burst, t.team,
           100 * (CAST(l.n_co AS DOUBLE) / nullif(l.n_in, 0)) / ln(1 + t.team) AS nci_adj,
           {", ".join(jcols)}, {", ".join(pcols)}
         FROM pop0 p JOIN act a USING (aid) LEFT JOIN s_work w USING (aid) LEFT JOIN s_pact pc USING (aid)
         LEFT JOIN s_link l USING (aid) LEFT JOIN s_conc c USING (aid) LEFT JOIN s_h h USING (aid)
         LEFT JOIN s_burst b USING (aid) LEFT JOIN s_team t USING (aid) LEFT JOIN s_jmain j USING (aid) {jjoin}""")
    x(f"""ALTER TABLE scores ADD COLUMN eligible BOOLEAN; UPDATE scores SET eligible = (n_cw_nc >= {P['min_cw']});
          ALTER TABLE scores ADD COLUMN r1 BOOLEAN; UPDATE scores SET r1 = coalesce(nci_adj > 35, false);
          ALTER TABLE scores ADD COLUMN r2 BOOLEAN; UPDATE scores SET r2 = (s3_pact > 5);
          ALTER TABLE scores ADD COLUMN r3 BOOLEAN; UPDATE scores SET r3 = coalesce(s8_burst > 3, false);
          ALTER TABLE scores ADD COLUMN r_score INTEGER;
          UPDATE scores SET r_score = 3 * CAST(r1 AS INTEGER) + 3 * CAST(r2 AS INTEGER) + 2 * CAST(r3 AS INTEGER);""")
    return [r[0] for r in x("DESCRIBE scores").fetchall()]
