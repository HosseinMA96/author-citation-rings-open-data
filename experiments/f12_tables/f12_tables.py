"""F12: supplementary tables for the paper, generated from run records only (laptop). Writes paper/content/supp_tables.tex
(generated file: do not edit by hand). Tables: S1 S1 deciles (A4); S2 screening metrics (A5, with P4 clustered lift
intervals); S3 referencing/peer-review screening (P7, post hoc); S4 all MH odds ratios (A2 primary and (a)-(f), P1, P6,
clustered intervals P4); S6 retraction reasons by outcome class (SPEC.md §5 strings; paper counts from Paper D run
d02_rw_20261101_01); S7 odds ratios by outcome class (A3, with clustered intervals P4); S8 classes under the adjusted
strata with the class ratio (P11, post hoc); S9 tie-breaking audit (P12, post hoc).
usage: python f12_tables.py RUN_ID F06_RUN F07_RUN F09_RUN F13_RUN
"""
import csv, json, sys
from common import Run, F_ROOT

F06, F07, F09, F13 = sys.argv[2:6]
E = F_ROOT / "experiments"
rec = lambda exp, r: json.loads((E / exp / "runs" / r / "run.json").read_text())["results"]
r6, r7, r9, r13 = rec("f06_eval", F06), rec("f07_posthoc", F07), rec("f09_posthoc2", F09), rec("f13_posthoc3", F13)
D02 = F_ROOT.parent / "D_retraction_contamination/experiments/d02_retraction_watch/runs/d02_rw_20261101_01/reason_counts.csv"
run = Run(sys.argv[1], __file__, {"f06": F06, "f07": F07, "f09": F09, "f13": F13, "d02_reason_counts": str(D02.relative_to(F_ROOT.parent))})
ci = lambda m, d=2: "--" if m.get("or_mh") is None else f"{m['or_mh']:.{d}f} ({m['lo']:.{d}f}--{m['hi']:.{d}f})"
n = lambda v: f"{v:,}"
EXP = [("top_s1_recip_nc", "S1 non-co-author reciprocity, top 1\\%"), ("top_s2_recip", "S2 reciprocity, top 1\\%"),
       ("top_s4_conc5", "S4 concentration, top 1\\%"), ("top_s5_self", "S5 self-citation, top 1\\%"),
       ("top_s6_co", "S6 co-author citation, top 1\\%"), ("bottom_s7_ch2", "S7 low $C/h^2$, bottom 1\\%"),
       ("r1", "R1 co-author rule"), ("r2", "R2 pact rule"), ("r3", "R3 burst rule"), ("r_ge3", "$R \\geq 3$")]
RK = [("s1_recip_nc", "S1"), ("s2_recip", "S2"), ("s3_pact", "S3 pact authors"), ("s4_conc5", "S4"), ("s5_self", "S5"),
      ("s6_co", "S6"), ("s7_ch2_low", "S7 (low)"), ("s8_burst", "S8 burst"), ("r_score", "Rule score $R$"),
      ("rankavg_s1_J", "S1 + journal risk"), ("citations", "Citations received"), ("journal_J", "Journal risk $J$"),
      ("productivity", "Productivity")]
T = []
A4a = r13["P12a_A4_deciles"]; Z = A4a["s1_zero_pooled"]; RT = r13["P12b_A5_ties"]["r_score"]["k1000"]
# S1 deciles
T += ["\\begin{table}[htbp]", "\\centering", "\\caption{Later retraction by decile of S1 (non-co-author "
      "reciprocity) in the primary population, unadjusted; Wilson 95\\% intervals \\citep{wilson1927}. Deciles 1--3 contain "
      f"only authors with S1 = 0 ({n(A4a['authors_with_s1_zero'])} authors, who also fill part of decile 4) and split them by a "
      "seeded uniform key (pre-specified). Their unequal counts are a chance outcome of that split (post hoc: chi-square "
      f"{A4a['chi2_frozen_seed']:.2f}, 2 degrees of freedom; {100 * A4a['share_alt_chi2_ge_frozen']:.1f}\\% of 1,000 alternative "
      f"seeds gave a larger value; Table~\\ref{{tab:ties}}); rate among all authors with S1 = 0: {100 * Z['rate']:.2f}\\% "
      f"({100 * Z['lo']:.2f}--{100 * Z['hi']:.2f}).}}", "\\label{tab:dose}", "\\small", "\\begin{tabular}{lrrrr}", "\\toprule",
      "Decile & S1 range & Authors & With later retraction & Rate, \\% (95\\% CI) \\\\", "\\midrule"]
for r in r6["A4_dose_s1"]:
    lab = "Top 1\\%" if r["decile"] == "top1%" else str(r["decile"])
    T.append(f"{lab} & {r['s1_min']:.4f}--{r['s1_max']:.4f} & {n(r['n'])} & {n(r['pos'])} & "
             f"{100 * r['rate']:.2f} ({100 * r['lo']:.2f}--{100 * r['hi']:.2f}) \\\\")
T += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
# S2 screening (every A5 metric with its pre-specified interval)
A5, P4s = r6["A5_screening"], r9["P4_screen_all_clustered"]
T += ["\\begin{landscape}", "\\begin{table}[p]", "\\centering", "\\caption{Screening metrics for all later retractions in the "
      f"primary population ({n(A5['n'])} authors, {n(A5['positives'])} positives, base rate {100 * A5['base_rate']:.3f}\\%). "
      "Precision (\\%) and lift (precision divided by the base rate) among the top $k$ authors, recall among the top 10,000 and "
      "average precision (AP). Intervals: 95\\%, 1,000 paired Poisson bootstrap resamples of authors (pre-specified; the "
      "precision interval is the lift interval times the base rate); last column: lift at 10,000 with resampling of main "
      "journals (post hoc). The rule score $R$ takes few values: all three cut-offs fall within one group of "
      f"{n(RT['tie_group_size'])} tied authors ({RT['tie_group_positives']} with a later retraction), so its values at these cut-offs "
      f"depend on the random tie-break (expected lift {RT['tie_group_positives'] / RT['tie_group_size'] / A5['base_rate']:.2f}; post hoc, "
      "Table~\\ref{tab:ties}).}", "\\label{tab:screen}", "\\scriptsize", "\\setlength{\\tabcolsep}{2.5pt}",
      "\\begin{tabular}{lrrrrrrrrr}", "\\toprule",
      " & \\multicolumn{2}{c}{Top 100} & \\multicolumn{2}{c}{Top 1,000} & \\multicolumn{2}{c}{Top 10,000} & & & \\\\",
      "\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}\\cmidrule(lr){6-7}",
      "Ranking & Prec. & Lift (95\\% CI) & Prec. & Lift (95\\% CI) & Prec. & Lift (95\\% CI) & Recall@10,000 (95\\% CI) & "
      "AP (95\\% CI) & Lift@10,000, clustered \\\\", "\\midrule"]
for k, lab in RK:
    m, c = A5[k], P4s[k]["lift@10000"]
    pr = lambda key: f"{100 * m[key]['point']:.2f}"
    lf = lambda key: f"{m[key]['point']:.2f} ({m[key]['lo']:.2f}--{m[key]['hi']:.2f})"
    T.append(f"{lab} & {pr('prec@100')} & {lf('lift@100')} & {pr('prec@1000')} & {lf('lift@1000')} & {pr('prec@10000')} & "
             f"{lf('lift@10000')} & {m['recall@10000']['point']:.3f} ({m['recall@10000']['lo']:.3f}--{m['recall@10000']['hi']:.3f}) & "
             f"{m['ap']['point']:.4f} ({m['ap']['lo']:.4f}--{m['ap']['hi']:.4f}) & {c['cl_lo']:.2f}--{c['cl_hi']:.2f} \\\\")
T += ["\\bottomrule", "\\end{tabular}", "\\end{table}", "\\end{landscape}", ""]
# S3 refpeer screening (post hoc)
P7 = r9["P7_screen_refpeer"]
T += ["\\begin{table}[htbp]", "\\centering", "\\caption{Screening for later retraction in the "
      f"referencing or peer-review class only (post hoc; {n(P7['positives'])} positives, base rate {100 * P7['base_rate']:.3f}\\%). Lift with "
      "author-level and journal-clustered 95\\% bootstrap intervals.}", "\\label{tab:screenrp}", "\\small",
      "\\begin{tabular}{lrrrr}", "\\toprule",
      "Ranking & Lift@1,000 (authors) & Lift@10,000 (authors) & Lift@10,000 (clustered) & AP \\\\", "\\midrule"]
for k, lab in RK:
    m = P7[k]
    T.append(f"{lab} & {m['lift@1000']['point']:.2f} ({m['lift@1000']['lo']:.2f}--{m['lift@1000']['hi']:.2f}) & "
             f"{m['lift@10000']['point']:.2f} ({m['lift@10000']['lo']:.2f}--{m['lift@10000']['hi']:.2f}) & "
             f"{m['lift@10000']['cl_lo']:.2f}--{m['lift@10000']['cl_hi']:.2f} & {m['ap']['point']:.4f} \\\\")
T += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
# S4/S5 all odds ratios (pre-specified, then robustness and post hoc), landscape
def ortable(num, title, colspec, rows_fn, header):
    return (["\\begin{landscape}", "\\begin{table}[p]", "\\centering", f"\\caption{{{title}}}",
             f"\\label{{tab:allor{num[-1]}}}", "\\scriptsize", "\\setlength{\\tabcolsep}{3pt}", f"\\begin{{tabular}}{{{colspec}}}",
             "\\toprule", header, "\\midrule"] + [rows_fn(k, lab) for k, lab in EXP] +
            ["\\bottomrule", "\\end{tabular}", "\\end{table}", "\\end{landscape}", ""])
pre = [("A1_A2_A3_primary", "Primary"), ("rob_a_all_eligible_prior_stratum", "(a) all eligible"), ("rob_b_T0p", "(b) $T_0'$"),
       ("rob_c_cwnc_ge100", "(c) $|CW_{nc}| \\geq 100$")]
T += ortable("S4", "Mantel--Haenszel odds ratios (95\\% CI) of later retraction for every exposure, pre-specified (I): "
             "primary strata (main journal $\\times$ productivity band) and robustness analyses (a) all eligible authors with prior "
             "retraction as a stratum, (b) $T_0'$ = 30 September 2023, (c) at least 100 outside citing works.",
             "l" + "c" * len(pre), lambda k, lab: f"{lab} & " + " & ".join(ci(r6[t]["mh"][k]) for t, _ in pre) + " \\\\",
             "Exposure & " + " & ".join(c for _, c in pre) + " \\\\")
post = [("rob_d_outcome_papers_in_W", "(d) outcome in $W$"), ("rob_e_strata_journal_only", "(e) journal strata"),
        ("rob_f_top5pct", "(f) top 5\\%")]
def row5(k, lab):
    pc = r9["P4_primary_strata"][k]
    cl = "--" if pc.get("cl_lo") is None else f"{pc['cl_lo']:.2f}--{pc['cl_hi']:.2f}"
    return (f"{lab} & " + " & ".join(ci(r6[t]["mh"][k]) for t, _ in post) +
            f" & {cl} & {ci(r7['P1_volume_strata'][k])} & {ci(r9['P6_fine_strata'][k])} \\\\")
T += ortable("S5", "Mantel--Haenszel odds ratios (95\\% CI), pre-specified (II): robustness analyses (d) outcome publications from "
             "2014--2023, (e) strata by journal only, (f) top 5\\% instead of top 1\\% (rules unchanged); post hoc: 95\\% interval "
             "for the primary estimate from 1,000 resamples of main journals; P1, strata adding deciles of citations received; P6, "
             "strata of main journal $\\times$ productivity decile $\\times$ citation decile $\\times$ start band.",
             "l" + "c" * (len(post) + 3), row5,
             "Exposure & " + " & ".join(c for _, c in post) + " & Journal-clustered & P1 & P6 \\\\")
# S5 reasons by class
REFPEER = ["Concerns/Issues about Referencing/Attributions", "Compromised Peer Review", "Concerns/Issues about Peer Review", "Rogue Editor"]
MISC = ["Falsification/Fabrication of Data", "Falsification/Fabrication of Image", "Falsification/Fabrication of Results",
        "Manipulation of Images", "Manipulation of Results", "Manipulation of Data", "Misconduct by Author",
        "Misconduct - Official Investigation(s) and/or Finding(s)", "Euphemisms for Misconduct", "Plagiarism of/in Article",
        "Plagiarism of Text", "Plagiarism of Image", "Plagiarism of Data", "Euphemisms for Plagiarism", "Duplication of/in Image",
        "False/Forged Authorship", "False/Forged Affiliation", "Computer-Aided Content or Computer-Generated Content",
        "Hoax Paper", "Sabotage of Materials/Methods"]
HON = {"Results Not Reproducible", "Contamination of Cell Lines/Tissues", "Contamination of Materials", "Doing the Right Thing"}
counts = {r["reason"]: int(r["papers"]) for r in csv.DictReader(open(D02))}
def cls(rsn):
    if rsn in REFPEER: return "Referencing or peer-review manipulation"
    if rsn == "Paper Mill": return "Paper mill"
    if rsn in MISC: return "Other misconduct"
    if rsn.startswith("Error in") or rsn.startswith("Error by") or rsn in HON: return "Honest error"
    return "No class (process, notice and other reasons)"
groups = {}
for rsn in sorted(counts, key=lambda r: -counts[r]):
    groups.setdefault(cls(rsn), []).append(rsn.replace("&", "\\&") + f" ({n(counts[rsn])})")
T += ["\\begin{table}[htbp]", "\\centering", "\\caption{Retraction Watch reason strings by outcome class "
      "(numbers: retracted papers with the reason in the frozen Retraction Watch copy, all years and fields). An author is in "
      "the honest-error-only class if every outcome publication has at least one honest-error reason and none from the first "
      "three classes; reasons without a class do not define a class by themselves.}", "\\label{tab:classes}",
      "\\scriptsize", "\\begin{tabular}{p{3.2cm}p{12.2cm}}", "\\toprule", "Class & Reasons (papers) \\\\", "\\midrule"]
for c in ["Referencing or peer-review manipulation", "Paper mill", "Other misconduct", "Honest error",
          "No class (process, notice and other reasons)"]:
    T.append(f"{c} & {'; '.join(groups.get(c, []))} \\\\ \\addlinespace")
T += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
# S7 odds ratios by outcome class (A3, pre-specified) with journal-clustered intervals (P4, post hoc)
A = r6["A1_A2_A3_primary"]; PB = r9["P4_by_class"]; pbc = A["positives_by_class"]
CL = [("y_refpeer", "Referencing or\\\\peer review"), ("y_mill", "Paper mill"), ("y_misc", "Other\\\\misconduct"),
      ("y_err_only", "Honest error\\\\only")]
T += ["\\begin{table}[htbp]", "\\centering", "\\caption{Mantel--Haenszel odds ratios (95\\% CI) of later retraction by "
      "outcome class (pre-specified; primary strata), with the number of exposed authors with a later retraction in the "
      "class in brackets; second line: 95\\% interval from 1,000 resamples of main journals (post hoc). The honest-error-only "
      "class is the negative control.}", "\\label{tab:byclass}", "\\footnotesize", "\\setlength{\\tabcolsep}{3pt}",
      "\\begin{tabular}{lcccc}", "\\toprule",
      "Exposure & " + " & ".join(f"\\begin{{tabular}}[b]{{@{{}}c@{{}}}}{lab}\\\\({n(pbc[c])})\\end{{tabular}}" for c, lab in CL) + " \\\\", "\\midrule"]
for k, lab in [("top_s1_recip_nc", "S1, top 1\\%"), ("top_s5_self", "S5, top 1\\%"), ("r2", "R2 pact rule")]:
    cells, cl = [], []
    for c, _ in CL:
        m = A["mh_by_class"][f"{k}|{c}"]; q = PB[f"{k}|{c}"]
        cells.append(f"{ci(m)} [{n(m['exposed_pos'])}]")
        cl.append("--" if q.get("cl_lo") is None else f"{q['cl_lo']:.2f}--{q['cl_hi']:.2f}")
    T.append(f"{lab} & " + " & ".join(cells) + " \\\\")
    T.append("\\quad journal-clustered & " + " & ".join(cl) + " \\\\ \\addlinespace")
T += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
# S8 outcome classes under the adjusted strata, with the class ratio (P11, post hoc)
CLS = [("y", "All later\\\\retractions"), ("y_refpeer", "Referencing or\\\\peer review"), ("y_mill", "Paper mill"),
       ("y_misc", "Other\\\\misconduct"), ("y_err_only", "Honest error\\\\only")]
STR = [("primary", "Primary"), ("P1", "P1"), ("P6", "P6")]
hd = lambda lab: f"\\begin{{tabular}}[b]{{@{{}}c@{{}}}}{lab}\\end{{tabular}}"
T += ["\\begin{landscape}", "\\begin{table}[p]", "\\centering", "\\caption{Mantel--Haenszel odds ratios (95\\% CI) of later "
      "retraction by outcome class in the pre-specified strata (Primary) and in the adjusted strata P1 (adding deciles of "
      "citations received) and P6 (main journal $\\times$ productivity decile $\\times$ citation decile $\\times$ start band); "
      "exposed authors with a later retraction in the class in brackets; second line: 95\\% interval from 1,000 resamples of "
      "main journals. Last column: ratio of the referencing or peer-review odds ratio to the honest-error odds ratio, with its "
      "journal-clustered interval (-- where an odds ratio is undefined). Post hoc, except the primary-strata estimates of "
      "S1, S5 and R2 (Table~\\ref{tab:byclass}); the ratio for R3 ($\\dagger$) was added after its class estimates had been "
      "seen.}", "\\label{tab:byclassadj}", "\\scriptsize", "\\setlength{\\tabcolsep}{2.5pt}", "\\begin{tabular}{llcccccc}",
      "\\toprule", "Exposure & Strata & " + " & ".join(hd(l) for _, l in CLS) + " & " + hd("Ratio, referencing\\\\or peer review\\\\to honest error") + " \\\\",
      "\\midrule"]
for k, lab in [("top_s1_recip_nc", "S1, top 1\\%"), ("top_s4_conc5", "S4, top 1\\%"), ("top_s5_self", "S5, top 1\\%"),
               ("top_s6_co", "S6, top 1\\%"), ("r2", "R2 pact rule"), ("r3", "R3 burst rule")]:
    for j, (st, slab) in enumerate(STR):
        res = r13[f"P11_{st}"]; rat = r13[f"P11_ratio_refpeer_over_err_{st}"].get(k)
        cells = [f"{ci(res[f'{k}|{c}'])} [{res[f'{k}|{c}']['exposed_pos']}]" for c, _ in CLS]
        cl = ["--" if res[f"{k}|{c}"].get("cl_lo") is None else f"{res[f'{k}|{c}']['cl_lo']:.2f}--{res[f'{k}|{c}']['cl_hi']:.2f}" for c, _ in CLS]
        if rat is None: rc, rl = "", ""
        elif rat.get("ratio") is None: rc, rl = "--", ""
        else:
            rc = f"{rat['ratio']:.2f}" + ("$^\\dagger$" if k == "r3" else ""); rl = f"{rat['cl_lo']:.2f}--{rat['cl_hi']:.2f}"
        T.append(f"{lab if j == 0 else ''} & {slab} & " + " & ".join(cells) + f" & {rc} \\\\")
        T.append(" & & " + " & ".join(cl) + f" & {rl} \\\\" + (" \\addlinespace" if j == 2 else ""))
T += ["\\bottomrule", "\\end{tabular}", "\\end{table}", "\\end{landscape}", ""]
# S9 tie-breaking audit (P12, post hoc)
T += ["\\begin{table}[htbp]", "\\centering", "\\caption{Tie-breaking audit (post hoc). (a) The three lowest deciles of S1 "
      "(Table~\\ref{tab:dose}): all their authors have S1 = 0; mean rank of the ORCID iD in each decile, which would differ if "
      "ties followed identifier order. (b) Rankings with ties at the screening cut-offs (Table~\\ref{tab:screen}): authors "
      "sharing the value of the $k$-th ranked author, how many of them enter the top $k$, and lift as computed (seeded key) and "
      "over 1,000 random tie-breaks (median and central 95\\%). Rankings not listed have no ties that matter at these "
      "cut-offs. (c) Odds ratios for all later retractions in the adjusted strata, with decile ties broken in row order "
      "(the order of ORCID iDs; as in Table~\\ref{tab:allor5}) and at random.}", "\\label{tab:ties}", "\\footnotesize",
      "\\setlength{\\tabcolsep}{3pt}", "\\begin{tabular}{lrrr}", "\\multicolumn{4}{l}{(a) S1 deciles 1--3} \\\\", "\\toprule",
      "Decile & Authors & With later retraction & Mean ORCID-iD rank \\\\", "\\midrule"]
for i in range(3):
    T.append(f"{i + 1} & {n(A4a['decile_sizes_1_3'][i])} & {A4a['positives_1_3'][i]} & {n(round(A4a['mean_aid_1_3'][i]))} \\\\")
T += ["\\bottomrule", f"\\multicolumn{{4}}{{l}}{{Chi-square {A4a['chi2_frozen_seed']:.2f}; alternative seeds with a larger value: "
      f"{100 * A4a['share_alt_chi2_ge_frozen']:.1f}\\%.}} \\\\", "\\end{tabular}", "", "\\medskip", "",
      "\\begin{tabular}{lrrrrr}", "\\multicolumn{6}{l}{(b) Ties at the screening cut-offs} \\\\", "\\toprule",
      "Ranking & $k$ & Tied authors & Taken into top $k$ & Lift as computed & Lift, random ties \\\\", "\\midrule"]
RKL = dict(RK)
for name in ["r_score", "s8_burst", "productivity", "s7_ch2_low", "s3_pact"]:
    for kk in ["k100", "k1000", "k10000"]:
        v = r13["P12b_A5_ties"][name][kk]
        if v["tie_group_size"] > 1 and 0 < v["taken_from_tie_group"] < v["tie_group_size"] and v["lift_q975"] > v["lift_q025"]:
            T.append(f"{RKL[name]} & {n(int(kk[1:]))} & {n(v['tie_group_size'])} & {n(v['taken_from_tie_group'])} & {v['lift_frozen']:.2f} & "
                     f"{v['lift_median']:.2f} ({v['lift_q025']:.2f}--{v['lift_q975']:.2f}) \\\\")
T += ["\\bottomrule", "\\end{tabular}", "", "\\medskip", "", "\\begin{tabular}{lcccc}",
      "\\multicolumn{5}{l}{(c) Adjusted strata with random decile ties, all later retractions} \\\\", "\\toprule",
      "Exposure & P1, row order & P1, random & P6, row order & P6, random \\\\", "\\midrule"]
for k, lab in EXP:   # row order: f07 P1 and f09 P6 (reproduced exactly by f13); random ties: f13
    cols = [r7["P1_volume_strata"][k], r13["P11_P1_randties"][f"{k}|y"], r9["P6_fine_strata"][k], r13["P11_P6_randties"][f"{k}|y"]]
    T.append(f"{lab} & " + " & ".join(ci(m) for m in cols) + " \\\\")
T += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
out = F_ROOT / "paper/content/supp_tables.tex"
out.write_text("% GENERATED by experiments/f12_tables/f12_tables.py from run records; do not edit by hand.\n" + "\n".join(T))
(run.dir / "supp_tables.tex").write_text(out.read_text())
run.log("tables", ["S1 deciles", "S2 screening", "S3 refpeer screening", "S4 ORs pre-specified I", "S5 ORs pre-specified II + post hoc", "S6 reasons by class", "S7 ORs by class", "S8 classes under adjusted strata", "S9 tie audit"])
run.log("reasons_by_class", {c: len(v) for c, v in groups.items()})
run.finish()
