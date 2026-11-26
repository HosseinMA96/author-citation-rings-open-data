"""F8 figures for the paper, from run records only (no data access; runs on the laptop).
Fig 1: within-stratum Mantel-Haenszel odds ratios (primary strata, pre-specified; volume strata, post hoc) and by outcome class.
Fig 2: screening, lift at k = 1,000 and k = 10,000 with paired-bootstrap 95% intervals.
Fig 3: ORCID coverage of biomedical publications by year.
usage: python f08_figures.py RUN_ID F03_RUN F06_RUN F07_RUN
"""
import json, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter, FixedLocator
from common import Run, F_ROOT

F03, F06, F07 = sys.argv[2:5]
E = F_ROOT / "experiments"
rec = lambda exp, r: json.loads((E / exp / "runs" / r / "run.json").read_text())["results"]
r3, r6, r7 = rec("f03_authors", F03), rec("f06_eval", F06), rec("f07_posthoc", F07)
run = Run(sys.argv[1], __file__, {"f03_run": F03, "f06_run": F06, "f07_run": F07, "matplotlib": matplotlib.__version__})
plt.rcParams.update({"pdf.fonttype": 42, "font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False})
BLUE, ORANGE, GREY = "#2a78d6", "#eb6834", "#666666"

# --- Figure 1 ---------------------------------------------------------------------------------------------------
LAB = [("top_s1_recip_nc", "S1 non-co-author reciprocity (primary)"), ("top_s2_recip", "S2 reciprocity, all citing works"),
       ("top_s4_conc5", "S4 concentration of citing authors"), ("top_s5_self", "S5 self-citation share"),
       ("top_s6_co", "S6 co-author citation share"), ("bottom_s7_ch2", "S7 low $C/h^2$ (bottom 1%)"),
       ("r2", "R2 pact rule (> 5 pact authors)"), ("r3", "R3 burst rule (> 3)"), ("r_ge3", "Rule score R ≥ 3")]
prim, vol = r6["A1_A2_A3_primary"]["mh"], r7["P1_volume_strata"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 4.0), gridspec_kw={"width_ratios": [1.15, 1]})
for i, (k, lab) in enumerate(LAB):
    yv = len(LAB) - 1 - i
    for m, dy, col, mk in [(prim[k], 0.15, BLUE, "o"), (vol[k], -0.15, ORANGE, "s")]:
        a1.errorbar(m["or_mh"], yv + dy, xerr=[[m["or_mh"] - m["lo"]], [m["hi"] - m["or_mh"]]], fmt=mk, color=col, ms=4,
                    capsize=2, lw=1)
a1.axvline(1, color=GREY, lw=0.8, ls="--")
a1.set_xscale("log"); a1.set_xlim(0.4, 4); a1.xaxis.set_major_locator(FixedLocator([0.5, 1, 2, 4]))
a1.set_xticklabels(["0.5", "1", "2", "4"]); a1.xaxis.set_minor_formatter(NullFormatter())
a1.set_yticks(range(len(LAB))); a1.set_yticklabels([l for _, l in LAB][::-1])
a1.set_xlabel("Odds ratio of later retraction (Mantel–Haenszel)")
a1.plot([], [], "o", color=BLUE, label="strata: journal × productivity (pre-specified)")
a1.plot([], [], "s", color=ORANGE, label="strata: + citation-volume deciles (post hoc)")
a1.set_title("All later retractions, primary population", fontsize=8.5)
CL = [("y_refpeer", "Referencing / peer review"), ("y_mill", "Paper mill"), ("y_misc", "Other misconduct"),
      ("y_err_only", "Honest error only (control)")]
byc = r6["A1_A2_A3_primary"]["mh_by_class"]
SIG = [("top_s1_recip_nc", "S1", "#1b7837", "o"), ("top_s5_self", "S5", "#762a83", "D"), ("r2", "R2", "#333333", "s")]
for j, (c, lab) in enumerate(CL):
    for s, (k, nm, col, mk) in enumerate(SIG):
        m = byc[f"{k}|{c}"]; yv = (len(CL) - 1 - j) + (0.22 - 0.22 * s)
        lo, hi = max(m["lo"], 0.1), min(m["hi"], 10)
        a2.errorbar(m["or_mh"], yv, xerr=[[m["or_mh"] - lo], [hi - m["or_mh"]]], fmt=mk, color=col, ms=4, capsize=2, lw=1,
                    label=nm if j == 0 else None)
a2.axvline(1, color=GREY, lw=0.8, ls="--")
a2.set_xscale("log"); a2.set_xlim(0.1, 10); a2.xaxis.set_major_locator(FixedLocator([0.1, 0.3, 1, 3, 10]))
a2.set_xticklabels(["0.1", "0.3", "1", "3", "10"]); a2.xaxis.set_minor_formatter(NullFormatter())
a2.set_yticks(range(len(CL))); a2.set_yticklabels([l for _, l in CL][::-1])
a2.set_xlabel("Odds ratio")
a2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3, fontsize=7, frameon=False, handletextpad=0.2, columnspacing=0.8)
a2.set_title("By retraction reason", fontsize=8.5)
a1.legend(loc="upper center", bbox_to_anchor=(0.2, -0.2), ncol=1, fontsize=7, frameon=False)
fig.tight_layout(); fig.subplots_adjust(bottom=0.27, wspace=0.9, right=0.97); fig.savefig(run.dir / "fig1_forest.pdf"); fig.savefig(run.dir / "fig1_forest.png", dpi=200); plt.close(fig)

# --- Figure 2 ---------------------------------------------------------------------------------------------------
A5 = r6["A5_screening"]
RK = [("s1_recip_nc", "S1 (primary)"), ("s2_recip", "S2"), ("s3_pact", "S3 pact authors"), ("s4_conc5", "S4"),
      ("s5_self", "S5 self-citation"), ("s6_co", "S6"), ("s7_ch2_low", "S7 low $C/h^2$"), ("s8_burst", "S8 burst"),
      ("r_score", "Rule score R"), ("rankavg_s1_J", "S1 + journal risk"), ("citations", "Citations received"),
      ("journal_J", "Journal risk J"), ("productivity", "Productivity")]
fig, axs = plt.subplots(1, 2, figsize=(7.2, 3.3), sharey=True)
for ax, k in zip(axs, [1000, 10000]):
    for i, (n, lab) in enumerate(RK):
        m = A5[n][f"lift@{k}"]; yv = len(RK) - 1 - i
        col = ORANGE if n in ("journal_J", "productivity", "citations") else BLUE
        ax.errorbar(m["point"], yv, xerr=[[m["point"] - m["lo"]], [m["hi"] - m["point"]]], fmt="o", color=col, ms=4,
                    capsize=2, lw=1)
    ax.axvline(1, color=GREY, lw=0.8, ls="--")
    ax.set_xlabel(f"Lift among the top {k:,} authors")
axs[0].set_yticks(range(len(RK))); axs[0].set_yticklabels([l for _, l in RK][::-1])
axs[0].plot([], [], "o", color=BLUE, label="citation signals"); axs[0].plot([], [], "o", color=ORANGE, label="baselines")
axs[0].legend(loc="upper right", fontsize=7, frameon=False)
fig.tight_layout(); fig.savefig(run.dir / "fig2_screening.pdf"); fig.savefig(run.dir / "fig2_screening.png", dpi=200); plt.close(fig)

# --- Figure 3 ---------------------------------------------------------------------------------------------------
rows = [r for r in r3["bio_coverage_by_year"] if 2000 <= r["year"] <= 2023]
yr = [r["year"] for r in rows]
slot = [100 * r["orcid_slots"] / r["slots"] for r in rows]; paper = [100 * r["with_ge1_orcid"] / r["papers"] for r in rows]
fig, ax = plt.subplots(figsize=(3.5, 2.4))
ax.plot(yr, paper, "-o", color=BLUE, ms=3, lw=1.2, label="publications with ≥ 1 ORCID-identified author")
ax.plot(yr, slot, "-s", color=ORANGE, ms=3, lw=1.2, label="author positions with an ORCID iD")
ax.axvspan(2014, 2023, color="#dddddd", alpha=0.5, lw=0); ax.text(2018.5, 3, "window W", ha="center", fontsize=7)
ax.set_ylim(0, 118); ax.set_yticks([0, 20, 40, 60, 80, 100]); ax.set_ylabel("Percent")
ax.set_xlabel("Publication year"); ax.legend(loc="upper left", fontsize=6.5, frameon=False)
fig.tight_layout(); fig.savefig(run.dir / "fig3_orcid_coverage.pdf"); fig.savefig(run.dir / "fig3_orcid_coverage.png", dpi=200); plt.close(fig)
run.log("figures", sorted(p.name for p in run.dir.glob("fig*")))
run.finish()
