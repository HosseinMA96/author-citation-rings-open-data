"""F13 desc (POSTHOC.md round 3, P13; laptop): share of author positions with an ORCID iD, and of publications with at least
one ORCID author, among biomedical publications of 2014-2023, from the per-year counts logged by f03 (no new data).
usage: python f13_desc.py RUN_ID F03_RUN
"""
import json, sys
from common import Run, F_ROOT

F03 = sys.argv[2]
rec = json.loads((F_ROOT / f"experiments/f03_authors/runs/{F03}/run.json").read_text())["results"]["bio_coverage_by_year"]
run = Run(sys.argv[1], __file__, {"f03_run": F03, "years": [2014, 2023]})
rows = [r for r in rec if 2014 <= r["year"] <= 2023]
slots, orc = sum(r["slots"] for r in rows), sum(r["orcid_slots"] for r in rows)
pubs, pubs_orc = sum(r["with_authors"] for r in rows), sum(r["with_ge1_orcid"] for r in rows)
run.log("biomedical_2014_2023", {"years": [r["year"] for r in rows], "author_positions": slots, "with_orcid": orc,
                                 "share_positions_with_orcid": orc / slots, "publications_with_authors": pubs,
                                 "publications_with_ge1_orcid": pubs_orc, "share_publications_with_ge1_orcid": pubs_orc / pubs})
run.log("by_year_share_positions", {r["year"]: round(r["orcid_slots"] / r["slots"], 4) for r in rows})
run.finish()
