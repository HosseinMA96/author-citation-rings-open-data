"""F11b (POST HOC P10b, POSTHOC.md round 2; laptop): for the 600 sampled biomedical DOIs of f11_cov (100 per year
2018-2023), the number of authors and of ORCID iDs in today's Crossref REST API record, against Meta's counts.
Per-DOI counts and aggregates (no names, no ORCID iDs). usage: python f11_crossref.py RUN_ID F11_RUN
"""
import csv, json, os, sys, time, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor
from common import Run, F_ROOT

F11 = sys.argv[2]
src = F_ROOT / f"experiments/f11_coverage/runs/{F11}/doi_sample.csv"
rows = list(csv.DictReader(open(src)))
MAILTO = os.environ.get("CROSSREF_MAILTO", "")   # contact address for the polite pool; never written to files
run = Run(sys.argv[1], __file__, {"f11_run": F11, "dois": len(rows), "api": "https://api.crossref.org/works/{doi}", "polite_pool": bool(MAILTO),
                                   "retrieved": time.strftime("%Y-%m-%d")})
def get(doi):
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi) + (f"?mailto={urllib.parse.quote(MAILTO)}" if MAILTO else "")
    for a in range(6):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "F-coverage-check/1.0" + (f" (mailto:{MAILTO})" if MAILTO else "")})
            m = json.load(urllib.request.urlopen(req, timeout=60))["message"]
            au = m.get("author", []) or []
            return {"cr_status": "ok", "cr_n_auth": len(au), "cr_n_orcid": sum(1 for x in au if x.get("ORCID"))}
        except urllib.error.HTTPError as e:
            if e.code == 404: return {"cr_status": "not_found", "cr_n_auth": None, "cr_n_orcid": None}
            time.sleep(3 * (a + 1))
        except Exception:
            time.sleep(3 * (a + 1))
    return {"cr_status": "error", "cr_n_auth": None, "cr_n_orcid": None}
with ThreadPoolExecutor(4) as ex:
    res = list(ex.map(lambda r: get(r["doi"]), rows))
out = [{**r, **x} for r, x in zip(rows, res)]
with open(run.dir / "crossref_vs_meta.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
agg = {}
for y in sorted({r["year"] for r in out}):
    g = [r for r in out if r["year"] == y and r["cr_status"] == "ok"]
    agg[y] = {"dois": sum(1 for r in out if r["year"] == y), "found_in_crossref": len(g),
              "meta_share_with_orcid": round(sum(int(r["n_orcid"]) > 0 for r in g) / len(g), 3),
              "crossref_share_with_orcid": round(sum((r["cr_n_orcid"] or 0) > 0 for r in g) / len(g), 3),
              "meta_orcid_slots": sum(int(r["n_orcid"]) for r in g), "crossref_orcid_slots": sum(r["cr_n_orcid"] or 0 for r in g),
              "meta_slots": sum(int(r["n_auth"]) for r in g), "crossref_slots": sum(r["cr_n_auth"] or 0 for r in g),
              "crossref_more_orcid_than_meta": sum((r["cr_n_orcid"] or 0) > int(r["n_orcid"]) for r in g),
              "crossref_fewer_orcid_than_meta": sum((r["cr_n_orcid"] or 0) < int(r["n_orcid"]) for r in g)}
run.log("by_year", agg)
run.log("status_counts", {s: sum(1 for r in out if r["cr_status"] == s) for s in {r["cr_status"] for r in out}})
run.finish()
