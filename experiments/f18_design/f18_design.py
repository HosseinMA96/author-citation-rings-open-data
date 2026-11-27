"""F18: design figures from run records (laptop). Fig A: flow of the study population. Fig B: timeline of the data and of
the analysis steps (run start times from run.json, VM clock = UTC; the specification freeze time is the true-UTC value in
experiments/f04_spec/RESULTS_LOG.md; the first push to the public repository is GitHub's server time from the repository activity API).
usage: python f18_design.py RUN_ID F03_RUN F05_RUN F06_RUN
"""
import json, sys
from datetime import datetime, timedelta
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch
from common import Run, F_ROOT

F03, F05, F06 = sys.argv[2:5]
E = F_ROOT / "experiments"
REDACTED = {"f17_attribution_20261126_01": "f17_redact_20261126_01"}   # original kept on the VM (POSTHOC.md round 6 addendum)
def rec(exp, r):
    p = E / exp / "runs" / r / "run.json"
    if not p.exists() and r in REDACTED:
        p = E / exp / "runs" / REDACTED[r] / "record.json"
    return json.loads(p.read_text())
r3, r6 = rec("f03_authors", F03)["results"], rec("f06_eval", F06)["results"]
# post hoc runs on the VM, in order (cited runs)
POSTHOC = [("f07_posthoc", "f07_posthoc_20261126_01"), ("f09_posthoc2", "f09_posthoc2_20261126_02"),
           ("f10_names", "f10_names_20261126_01"), ("f11_coverage", "f11_cov_20261126_01"), ("f13_posthoc3", "f13_posthoc3_20261126_02"),
           ("f14_class3", "f14_class3_20261126_01"), ("f15_pubclusters", "f15_pubclusters_20261126_01"),
           ("f16_randties", "f16_randties_20261126_01"), ("f17_attribution", "f17_attribution_20261126_01")]
SPEC_FROZEN = "2026-11-26T18:43:04Z"      # true UTC, experiments/f04_spec/RESULTS_LOG.md
REPO_CREATED = "2026-11-26T21:24:18Z"     # first push to the public repository, GitHub server time (repos/.../activity API)
run = Run(sys.argv[1], __file__, {"f03": F03, "f05": F05, "f06": F06, "posthoc_runs": [p[1] for p in POSTHOC],
                                  "spec_frozen_utc": SPEC_FROZEN, "repo_created_utc": REPO_CREATED,
                                  "matplotlib": matplotlib.__version__})
plt.rcParams.update({"pdf.fonttype": 42, "font.size": 8.5})
BLUE, ORANGE, GREY, DARK = "#2a78d6", "#eb6834", "#666666", "#222222"
n = lambda v: f"{v:,}"

# --- Fig A: population flow -----------------------------------------------------------------------------------------------
c = r6["counts"]; g5 = r3["orcid_by_min_bio_papers"]["5"]
steps = [(f"{n(g5)} ORCID iDs with at least five\nbiomedical publications in 2014–2023", None),
         (f"{n(c['pre_eligible'])} with a publication in 2019–2023", f"{n(g5 - c['pre_eligible'])} with no publication\nin 2019–2023"),
         (f"{n(c['eligible'])} eligible: at least 20 citing works\nthat are neither their own nor a co-author's",
          f"{n(c['pre_eligible'] - c['eligible'])} with fewer than 20"),
         (f"{n(c['primary'])} in the primary population", f"{n(c['eligible_prior_T0'])} with a retraction\nby 31 January 2024"),
         (f"{n(c['primary_positives'])} with a later retraction\n(February 2024 to October 2026; {100 * c['primary_positives'] / c['primary']:.3f}%)", None)]
fig, ax = plt.subplots(figsize=(6.4, 4.2)); ax.set_xlim(0, 10); ax.set_ylim(0, len(steps) * 1.3); ax.axis("off")
for i, (txt, side) in enumerate(steps):
    y = (len(steps) - 1 - i) * 1.3 + 0.15
    last = i == len(steps) - 1
    ax.add_patch(FancyBboxPatch((0.3, y), 5.6, 0.85, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc="#fdf0e8" if last else "#eef4fb", ec=ORANGE if last else BLUE, lw=1))
    ax.text(3.1, y + 0.425, txt, ha="center", va="center", fontsize=8)
    if i > 0:
        ax.annotate("", xy=(3.1, y + 0.88), xytext=(3.1, y + 1.28), arrowprops=dict(arrowstyle="->", color=DARK, lw=1))
    if side:
        ax.annotate("", xy=(6.3, y + 1.08), xytext=(3.1, y + 1.08), arrowprops=dict(arrowstyle="->", color=GREY, lw=0.8))
        ax.text(6.4, y + 1.08, "excluded: " + side, ha="left", va="center", fontsize=7.5, color=GREY)
fig.tight_layout(); fig.savefig(run.dir / "fig_flow.pdf"); fig.savefig(run.dir / "fig_flow.png", dpi=200); plt.close(fig)

# --- Fig B: timeline ------------------------------------------------------------------------------------------------------
p = lambda s: datetime.strptime(s.replace("Z", ""), "%Y-%m-%dT%H:%M:%S")
fig, (a1, a2) = plt.subplots(2, 1, figsize=(7.2, 3.7), gridspec_kw={"height_ratios": [1, 1.3]})
a1.set_xlim(datetime(2013, 6, 1), datetime(2027, 3, 1)); a1.set_ylim(0, 3); a1.set_yticks([])
for s in ["left", "right", "top"]: a1.spines[s].set_visible(False)
a1.axvspan(datetime(2014, 1, 1), datetime(2024, 1, 1), ymin=0.55, ymax=0.85, color=BLUE, alpha=0.25)
a1.text(datetime(2019, 1, 1), 2.05, "window W: publications and citations used for the signals (2014–2023)", ha="center", fontsize=7.5)
a1.axvspan(datetime(2024, 2, 1), datetime(2026, 10, 30), ymin=0.15, ymax=0.45, color=ORANGE, alpha=0.3)
a1.text(datetime(2025, 6, 15), 0.85, "outcome window", ha="center", fontsize=7.5)
for d_, lab, ha in [(datetime(2024, 1, 31), "graph snapshot, $T_0$ = 31 Jan 2024 ", "right"),
                    (datetime(2026, 10, 30), " Retraction Watch\n copy, 30 Oct 2026", "left")]:
    a1.axvline(d_, color=DARK, lw=0.8, ls="--"); a1.text(d_, 2.95, lab, ha=ha, va="top", fontsize=7)
a1.set_title("Data", fontsize=8.5, loc="left")
ph = sorted(p(rec(e, r)["started_utc"]) for e, r in POSTHOC)
ev = [(p(SPEC_FROZEN), "specification\nfrozen, hash\nrecorded", DARK),
      (p(rec("f05_scores", F05)["started_utc"]), "score run", DARK),
      (p(rec("f06_eval", F06)["started_utc"]), "evaluation run:\nfirst to read the\noutcome labels", ORANGE),
      (ph[0], "first post hoc\nrun", BLUE), (p(REPO_CREATED), "first push to\nthe public\nrepository", GREY), (ph[-1], "last post hoc\nrun", BLUE)]
assert [e[0] for e in ev] == sorted(e[0] for e in ev), "events out of order"
a2.set_xlim(-0.6, len(ev) - 0.4); a2.set_ylim(-1.25, 1.55); a2.axis("off")
a2.annotate("", xy=(len(ev) - 0.45, 0), xytext=(-0.55, 0), arrowprops=dict(arrowstyle="->", color=DARK, lw=0.9))
a2.axvspan(3, 5, ymin=0.36, ymax=0.52, color=BLUE, alpha=0.15, lw=0)
a2.text(4, -0.42, "post hoc analyses", ha="center", va="center", fontsize=7, color=BLUE)
for i, (t, lab, col) in enumerate(ev):
    a2.plot(i, 0, "o", color=col, ms=5, zorder=3)
    a2.text(i, 0.2, lab, ha="center", va="bottom", fontsize=7, color=col)
    a2.text(i, -0.75, t.strftime("%d %b\n%H:%M:%S"), ha="center", va="center", fontsize=6.5, color=GREY)
a2.set_title("Analysis steps in order (not to scale; times UTC from the run records)", fontsize=8.5, loc="left")
fig.tight_layout(); fig.savefig(run.dir / "fig_timeline.pdf"); fig.savefig(run.dir / "fig_timeline.png", dpi=200); plt.close(fig)
run.log("flow", [s[0].replace("\n", " ") for s in steps])
run.log("timeline", {"spec": SPEC_FROZEN, "score": rec("f05_scores", F05)["started_utc"], "eval": rec("f06_eval", F06)["started_utc"],
                     "posthoc": {r: rec(e, r)["started_utc"] for e, r in POSTHOC}, "repo": REPO_CREATED})
run.finish()
