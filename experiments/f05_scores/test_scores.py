"""Unit test for score_lib.build: random toy graphs, every score recomputed by brute force from SPEC.md §4.
Runs on the laptop or the VM (needs duckdb, numpy). usage: python test_scores.py [n_graphs]"""
import math, sys, random
from collections import Counter, defaultdict
import duckdb
import score_lib

P = {"W0": 2014, "W1": 2023, "min_bio": 2, "active_from": 2016, "min_cw": 3, "T0s": ["2024-01-31", "2023-09-30"], "m": 100}

def toy(seed):
    r = random.Random(seed)
    n_nodes, n_auth = 260, 40
    nodes = {}
    for i in range(1, n_nodes + 1):
        nodes[i] = (r.randint(2008, 2024), r.choice([None, 1, 2, 3, 4]), r.random() < 0.7)   # y, jid, bio
    slots, pauth = set(), {}
    for i in nodes:
        k = r.randint(0, 4)
        authors = r.sample(range(1, n_auth + 1), k)
        for a in authors:
            slots.add((i, a))
        pauth[i] = k + r.randint(0, 3)                 # listed authors include people without ORCID
    # a few dense "rings" so that reciprocity and pact nodes are non-trivial
    edges = set()
    for _ in range(2200):
        p, q = r.randint(1, n_nodes), r.randint(1, n_nodes)
        if p != q and nodes[p][0] >= nodes[q][0] - 1:
            edges.add((p, q))
    # plant a ring: 4 authors, 5 papers each, citing each other's papers in both directions
    ring = r.sample(range(1, n_auth + 1), 4); nid = n_nodes
    rp = defaultdict(list)
    for a in ring:
        for _ in range(5):
            nid += 1; nodes[nid] = (r.randint(2017, 2023), r.choice([1, 2]), True)
            slots.add((nid, a)); pauth[nid] = 1 + r.randint(0, 2); rp[a].append(nid)
    for a in ring:
        for b in ring:
            if a != b:
                for p in rp[a]:
                    for q in rp[b]:
                        if r.random() < 0.6:
                            edges.add((p, q))
    stat = {}
    for i in r.sample(sorted(nodes), 25):
        stat[i] = r.choice(["2015-05-01", "2023-06-01", "2023-12-01", "2024-01-15"])
    return nodes, slots, pauth, edges, stat

def brute(nodes, slots, pauth, edges, stat):
    W = {i for i, v in nodes.items() if P["W0"] <= v[0] <= P["W1"]}
    O = defaultdict(set)
    for i, a in slots:
        if i in W:
            O[i].add(a)
    papers = defaultdict(set)
    for i, s in O.items():
        for a in s:
            papers[a].add(i)
    out = {}
    for a, Pa in papers.items():
        n_bio = sum(nodes[i][2] for i in Pa); last = max(nodes[i][0] for i in Pa)
        if n_bio < P["min_bio"] or last < P["active_from"]:
            continue
        co = {b for i in Pa for b in O[i] if b != a}
        L = [(p, q) for (p, q) in edges if q in Pa and p in W]
        cw_all = {p for p, _ in L}
        self_ = {p for p in cw_all if a in O[p]}
        coauth = {p for p in cw_all if any(b != a and b in co for b in O[p])}
        RW = {r_ for (q2, r_) in edges if q2 in Pa and r_ in W}
        CW = cw_all - self_; CWnc = {p for p in CW if p not in coauth}
        rec = CW & RW
        kb = Counter(b for p in rec for b in O[p] if b != a)
        n_in = len(L); n_self = sum(1 for p, _ in L if p in self_)
        n_co = sum(1 for p, _ in L if p not in self_ and p in coauth)
        w = Counter(b for p, _ in L if p not in self_ for b in O[p] if b != a)
        top = [b for b, _ in sorted(w.items(), key=lambda t: (-t[1], t[0]))[:5]]
        n_top = sum(1 for p, _ in L if p not in self_ and any(b in top for b in O[p]))
        indeg = Counter(q for _, q in L); cs = sorted(indeg.values(), reverse=True)
        h = max([k + 1 for k, c in enumerate(cs) if c >= k + 1], default=0)
        nt = Counter(nodes[i][0] for i in Pa)
        burst = max(nt[t] / max(1, nt[t - 1]) for t in range(P["W0"] + 1, P["W1"] + 1))
        team = sum(pauth[i] for i in Pa) / len(Pa)
        jc = Counter(nodes[i][1] for i in Pa if nodes[i][2] and nodes[i][1] is not None)
        jmain = sorted(jc.items(), key=lambda t: (-t[1], t[0]))[0][0] if jc else None
        res = {"n_bio": n_bio, "n_cw": len(CW), "n_cw_nc": len(CWnc), "n_recip": len(rec), "n_recip_nc": len(CWnc & RW),
               "s1_recip_nc": len(CWnc & RW) / len(CWnc) if CWnc else None, "s2_recip": len(rec) / len(CW) if CW else None,
               "s3_pact": sum(1 for k in kb.values() if k >= 3), "n_in": n_in, "n_self": n_self, "n_co": n_co,
               "s4_conc5": n_top / (n_in - n_self) if n_in - n_self else None,
               "s5_self": n_self / n_in if n_in else None, "s6_co": n_co / n_in if n_in else None, "h": h,
               "s7_ch2": n_in / h ** 2 if h else None, "s8_burst": burst, "team": team, "jid_main": jmain,
               "eligible": len(CWnc) >= P["min_cw"]}
        res["nci_adj"] = 100 * res["s6_co"] / math.log(1 + team) if res["s6_co"] is not None else None
        for k, T in enumerate(P["T0s"]):
            nj, rj = Counter(), Counter()
            for i, (y, j, bio) in nodes.items():
                if bio and j is not None and 2010 <= y <= P["W1"]:
                    nj[j] += 1; rj[j] += int(i in stat and stat[i] <= T)
            g = sum(rj.values()) / sum(nj.values())
            rate = {j: (rj[j] + P["m"] * g) / (nj[j] + P["m"]) for j in nj}
            bios = [i for i in Pa if nodes[i][2]]
            res[f"J_{k}"] = sum(rate.get(nodes[i][1], g) for i in bios) / len(bios)
            res[f"prior_{k}"] = any(i in stat and stat[i] <= T for (i, b) in slots if b == a)
        out[a] = res
    return out

def run_sql(nodes, slots, pauth, edges, stat):
    con = duckdb.connect()
    con.execute("CREATE TABLE nodes(iid BIGINT, y INTEGER, jid INTEGER, bio BOOLEAN)")
    con.executemany("INSERT INTO nodes VALUES (?, ?, ?, ?)", [(i, *v) for i, v in nodes.items()])
    con.execute("CREATE TABLE slots(iid BIGINT, aid BIGINT)"); con.executemany("INSERT INTO slots VALUES (?, ?)", sorted(slots))
    con.execute("CREATE TABLE pauth(iid BIGINT, n_auth INTEGER)"); con.executemany("INSERT INTO pauth VALUES (?, ?)", list(pauth.items()))
    con.execute("CREATE TABLE edges(citing_iid BIGINT, cited_iid BIGINT)"); con.executemany("INSERT INTO edges VALUES (?, ?)", sorted(edges))
    con.execute("CREATE TABLE stat(iid BIGINT, first_notice TIMESTAMP)")
    con.executemany("INSERT INTO stat VALUES (?, CAST(? AS TIMESTAMP))", list(stat.items()))
    score_lib.build(con, P)
    df = con.execute("SELECT * FROM scores ORDER BY aid").df()
    return {int(r.aid): r for r in df.itertuples()}

def missing(u):
    try:
        import pandas as pd
        return u is None or bool(pd.isna(u))
    except (TypeError, ValueError):
        return False

def same(u, v):
    if missing(u) or missing(v):
        return missing(u) and missing(v)
    return abs(float(u) - float(v)) < 1e-9

n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
checked = 0
for seed in range(n):
    g = toy(seed); b = brute(*g); s = run_sql(*g)
    assert set(b) == set(s), f"seed {seed}: author sets differ {set(b) ^ set(s)}"
    for a, ref in b.items():
        row = s[a]
        for k, v in ref.items():
            got = getattr(row, k)
            assert same(v, None if got is None else got), f"seed {seed} author {a} {k}: brute {v} sql {got}"
            checked += 1
    assert any(r["s3_pact"] > 0 for r in b.values()), "toy graph too sparse: no pact node"
print(f"test_scores: OK ({n} toy graphs, {checked} values compared)")
