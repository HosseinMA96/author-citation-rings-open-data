"""F12: supplementary tables for the paper, generated from run records only (laptop). Writes paper/content/supp_tables.tex
(generated file: do not edit by hand). Tables: S1 S1 deciles (A4); S2 screening metrics (A5, with P4 clustered lift
intervals); S3 referencing/peer-review screening (P7, post hoc); S4 all MH odds ratios (A2 primary and (a)-(f), P1, P6,
clustered intervals P4); S6 retraction reasons by outcome class (SPEC.md §5 strings; paper counts from Paper D run
d02_rw_20261101_01); S7 odds ratios by outcome class (A3, with clustered intervals P4); S8 classes under the adjusted
strata with the class ratio (P11, post hoc); S9 tie-breaking audit (P12, post hoc); S10 intervals clustered by shared
retraction events (P16). Outcome class 3 is shown as specified (f14, P14), with the first-coded values noted.
Since round 5 the adjusted strata P1/P6 use random decile ties (f13 P12c, f16 P17); row-order ties appear in S9(c).
usage: python f12_tables.py RUN_ID F06_RUN F07_RUN F09_RUN F13_RUN F14_RUN F15_RUN F16_RUN
"""
import csv, json, sys
from common import Run, F_ROOT

F06, F07, F09, F13, F14, F15, F16, F17R = sys.argv[2:10]
E = F_ROOT / "experiments"
rec = lambda exp, r: json.loads((E / exp / "runs" / r / "run.json").read_text())["results"]
r6, r7, r9, r13 = rec("f06_eval", F06), rec("f07_posthoc", F07), rec("f09_posthoc2", F09), rec("f13_posthoc3", F13)
r14, r15, r16 = rec("f14_class3", F14), rec("f15_pubclusters", F15), rec("f16_randties", F16)
C3 = r14["P14_class3"]   # outcome class 3 as specified, keys "<strata>|<exposure>|y_misc_spec"
D02 = F_ROOT.parent / "D_retraction_contamination/experiments/d02_retraction_watch/runs/d02_rw_20261101_01/reason_counts.csv"
run = Run(sys.argv[1], __file__, {"f06": F06, "f07": F07, "f09": F09, "f13": F13, "f14": F14, "f15": F15, "f16": F16, "f17_redacted": F17R, "d02_reason_counts": str(D02.relative_to(F_ROOT.parent))})
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
            f" & {cl} & {ci(r13['P11_P1_randties'][f'{k}|y'])} & {ci(r13['P11_P6_randties'][f'{k}|y'])} \\\\")
T += ortable("S5", "Mantel--Haenszel odds ratios (95\\% CI), pre-specified (II): robustness analyses (d) outcome publications from "
             "2014--2023, (e) strata by journal only, (f) top 5\\% instead of top 1\\% (rules unchanged); post hoc: 95\\% interval "
             "for the primary estimate from 1,000 resamples of main journals; P1, strata adding deciles of citations received; P6, "
             "strata of main journal $\\times$ productivity decile $\\times$ citation decile $\\times$ start band (decile ties broken at "
             "random; with ties in row order, Table~\\ref{tab:ties}).",
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
    if rsn in ("Compromised Peer Review", "Rogue Editor"):   # also in the specified class 3 (SPEC §5)
        groups.setdefault("Other misconduct", []).append(rsn + f"$^*$ ({n(counts[rsn])})")
T += ["\\begin{table}[htbp]", "\\centering", "\\caption{Retraction Watch reason strings by outcome class "
      "(numbers: retracted papers with the reason in the frozen Retraction Watch copy, all years and fields). An author is in "
      "the honest-error-only class if every outcome publication has at least one honest-error reason and none from the first "
      "three classes; reasons without a class do not define a class by themselves. $^*$Also in the first class: as specified, "
      "class 3 includes these two reasons; the evaluation code had left them out (Methods).}", "\\label{tab:classes}",
      "\\scriptsize", "\\begin{tabular}{p{3.2cm}p{12.2cm}}", "\\toprule", "Class & Reasons (papers) \\\\", "\\midrule"]
for c in ["Referencing or peer-review manipulation", "Paper mill", "Other misconduct", "Honest error",
          "No class (process, notice and other reasons)"]:
    T.append(f"{c} & {'; '.join(groups.get(c, []))} \\\\ \\addlinespace")
T += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
# S7 odds ratios by outcome class (A3, pre-specified) with journal-clustered intervals (P4, post hoc)
A = r6["A1_A2_A3_primary"]; PB = r9["P4_by_class"]; pbc = dict(A["positives_by_class"]); pbc["y_misc"] = r14["P14_counts"]["y_misc_spec"]
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
        if c == "y_misc": m = q = C3[f"primary|{k}|y_misc_spec"]
        cells.append(f"{ci(m)} [{n(m['exposed_pos'])}]")
        cl.append("--" if q.get("cl_lo") is None else f"{q['cl_lo']:.2f}--{q['cl_hi']:.2f}")
    T.append(f"{lab} & " + " & ".join(cells) + " \\\\")
    T.append("\\quad journal-clustered & " + " & ".join(cl) + " \\\\ \\addlinespace")
P5c = r9["P5_positive_control"]
cells = [f"{ci(P5c['by_class'][c])} [{n(P5c['by_class'][c]['exposed_pos'])}]" + ("$^\\S$" if c == "y_misc" else "") for c, _ in CL]
T.append("Prior retraction$^\\ddagger$ & " + " & ".join(cells) + " \\\\")
T.append("\\quad journal-clustered & " + " & ".join(f"{P5c['by_class'][c]['cl_lo']:.2f}--{P5c['by_class'][c]['cl_hi']:.2f}" for c, _ in CL) + " \\\\")
fc = "; ".join(f"{lab} {ci(A['mh_by_class'][f'{k}|y_misc'])} [{A['mh_by_class'][f'{k}|y_misc']['exposed_pos']}]"
               for k, lab in [("top_s1_recip_nc", "S1"), ("top_s5_self", "S5"), ("r2", "R2")])
T += ["\\bottomrule", f"\\multicolumn{{5}}{{p{{14cm}}}}{{Other misconduct is class 3 as specified. As first coded (without the two "
      f"shared peer-review reasons; {n(A['positives_by_class']['y_misc'])} positives): {fc}. $^\\ddagger$Positive control (post hoc): prior "
      f"retraction as the exposure among all {n(P5c['n'])} eligible authors, same strata; all later retractions "
      f"{ci(P5c['primary_strata'])}. $^\\S$Class 3 as first coded.}} \\\\", "\\end{tabular}", "\\end{table}", ""]
# S8 outcome classes under the adjusted strata, with the class ratio (P11, post hoc)
CLS = [("y", "All later\\\\retractions"), ("y_refpeer", "Referencing or\\\\peer review"), ("y_mill", "Paper mill"),
       ("y_misc_spec", "Other\\\\misconduct"), ("y_err_only", "Honest error\\\\only")]
STR = [("primary", "Primary"), ("P1_randties", "P1"), ("P6_randties", "P6")]
hd = lambda lab: f"\\begin{{tabular}}[b]{{@{{}}c@{{}}}}{lab}\\end{{tabular}}"
T += ["\\begin{landscape}", "\\begin{table}[p]", "\\centering", "\\caption{Mantel--Haenszel odds ratios (95\\% CI) of later "
      "retraction by outcome class in the pre-specified strata (Primary) and in the adjusted strata P1 (adding deciles of "
      "citations received) and P6 (main journal $\\times$ productivity decile $\\times$ citation decile $\\times$ start band; "
      "decile ties broken at random); "
      "exposed authors with a later retraction in the class in brackets; second line: 95\\% interval from 1,000 resamples of "
      "main journals. Last column: ratio of the referencing or peer-review odds ratio to the honest-error odds ratio, with its "
      "journal-clustered interval (-- where an odds ratio is undefined: no exposed author is in the honest-error class). Post "
      "hoc, except the primary-strata estimates of S1, S5 and R2 (Table~\\ref{tab:byclass}); the ratio for R3 ($\\dagger$) "
      "was added after its class estimates had been seen, those for S1 and S6 after review, for completeness. Other "
      "misconduct is class 3 as specified; estimates with the class as first coded are in the run records.}", "\\label{tab:byclassadj}", "\\scriptsize", "\\setlength{\\tabcolsep}{2.5pt}", "\\begin{tabular}{llcccccc}",
      "\\toprule", "Exposure & Strata & " + " & ".join(hd(l) for _, l in CLS) + " & " + hd("Ratio, referencing\\\\or peer review\\\\to honest error") + " \\\\",
      "\\midrule"]
for k, lab in [("top_s1_recip_nc", "S1, top 1\\%"), ("top_s4_conc5", "S4, top 1\\%"), ("top_s5_self", "S5, top 1\\%"),
               ("top_s6_co", "S6, top 1\\%"), ("r2", "R2 pact rule"), ("r3", "R3 burst rule")]:
    for j, (st, slab) in enumerate(STR):
        res = r16[f"P17_{st}"]; rat = r16[f"P17_ratio_{st}"].get(k)
        cells = [f"{ci(res[f'{k}|{c}'])} [{res[f'{k}|{c}']['exposed_pos']}]" for c, _ in CLS]
        cl = ["--" if res[f"{k}|{c}"].get("cl_lo") is None else f"{res[f'{k}|{c}']['cl_lo']:.2f}--{res[f'{k}|{c}']['cl_hi']:.2f}" for c, _ in CLS]
        if rat.get("ratio") is None: rc, rl = "--", ""
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
      "cut-offs. (c) Odds ratios for all later retractions in the adjusted strata P1 and P6 (defined in Table~\\ref{tab:allor5}), "
      "with decile ties broken at random (the "
      "values reported in the text and in Table~\\ref{tab:allor5}) and in row order (the order of ORCID iDs; first version).}", "\\label{tab:ties}", "\\footnotesize",
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
      "Exposure & P1, random & P1, row order & P6, random & P6, row order \\\\", "\\midrule"]
for k, lab in EXP:   # row order: f07 P1 and f09 P6 (reproduced exactly by f13); random ties: f13
    cols = [r13["P11_P1_randties"][f"{k}|y"], r7["P1_volume_strata"][k], r13["P11_P6_randties"][f"{k}|y"], r9["P6_fine_strata"][k]]
    T.append(f"{lab} & " + " & ".join(ci(m) for m in cols) + " \\\\")
T += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
# S10 intervals clustered by shared retraction events (P16, post hoc)
P16, cl16 = r15["P16_or"], r15["P16_clusters"]
iv = lambda m: f"{m['lo']:.2f}--{m['hi']:.2f}"
T += ["\\begin{table}[htbp]", "\\centering", "\\caption{Intervals that allow for shared retraction events (post hoc): 95\\% "
      "intervals from 1,000 resamples of clusters of primary authors linked by shared later-retracted publications (Poisson "
      f"weights; {n(cl16['clusters_with_positives'])} clusters hold the {n(r6['A1_A2_A3_primary']['positives'])} positives, the "
      f"largest {cl16['largest_cluster_positives']}; authors without a later retraction are singletons), beside the author-level "
      "and journal-clustered intervals. (a) Odds ratios in the primary strata. (b) Class estimates (class 3 as specified) and, "
      "for R2, the ratio of the referencing or peer-review to the honest-error odds ratio. (c) Lift among the top 10,000.}",
      "\\label{tab:pubclusters}", "\\footnotesize", "\\setlength{\\tabcolsep}{3pt}",
      "\\begin{tabular}{lcccc}", "\\multicolumn{5}{l}{(a) All later retractions} \\\\", "\\toprule",
      "Exposure & Odds ratio & Author-level CI & Journal-clustered & Publication-clustered \\\\", "\\midrule"]
for k, lab in EXP:
    m6 = r6["A1_A2_A3_primary"]["mh"][k]; q9 = r9["P4_primary_strata"][k]; p16 = P16[f"{k}|y"]
    if m6.get("or_mh") is None or k == "r1": continue
    T.append(f"{lab} & {m6['or_mh']:.2f} & {m6['lo']:.2f}--{m6['hi']:.2f} & "
             + ("--" if q9.get("cl_lo") is None else f"{q9['cl_lo']:.2f}--{q9['cl_hi']:.2f}") + f" & {iv(p16)} \\\\")
T += ["\\bottomrule", "\\end{tabular}", "", "\\medskip", "", "\\begin{tabular}{llccc}",
      "\\multicolumn{5}{l}{(b) Outcome classes} \\\\", "\\toprule",
      "Exposure & Class & Odds ratio & Author-level CI & Publication-clustered \\\\", "\\midrule"]
CN = [("y_refpeer", "Referencing or peer review"), ("y_mill", "Paper mill"), ("y_misc_spec", "Other misconduct"),
      ("y_err_only", "Honest error only")]
for k, lab in [("top_s1_recip_nc", "S1, top 1\\%"), ("top_s5_self", "S5, top 1\\%"), ("r2", "R2 pact rule")]:
    for j, (c, cl_) in enumerate(CN):
        p16 = P16[f"{k}|{c}"]
        m = C3[f"primary|{k}|y_misc_spec"] if c == "y_misc_spec" else r6["A1_A2_A3_primary"]["mh_by_class"][f"{k}|{c}"]
        T.append(f"{lab if j == 0 else ''} & {cl_} & {m['or_mh']:.2f} & {m['lo']:.2f}--{m['hi']:.2f} & {iv(p16)} \\\\")
rr, r13p = r15["P16_ratio_r2_refpeer_over_err"], r13["P11_ratio_refpeer_over_err_primary"]["r2"]
T.append(f"R2 pact rule & Ratio, referencing to error & {rr['point']:.2f} & journal-cl. {r13p['cl_lo']:.2f}--{r13p['cl_hi']:.2f} & {iv(rr)} \\\\")
T += ["\\bottomrule", "\\end{tabular}", "", "\\medskip", "", "\\begin{tabular}{lcccc}",
      "\\multicolumn{5}{l}{(c) Lift among the top 10,000} \\\\", "\\toprule",
      "Ranking & Lift & Author bootstrap & Journal-clustered & Publication-clustered \\\\", "\\midrule"]
for k, lab in RK:
    a5 = A5[k]["lift@10000"]; c9 = P4s[k]["lift@10000"]; p16 = r15["P16_lift10000"][k]
    T.append(f"{lab} & {a5['point']:.2f} & {a5['lo']:.2f}--{a5['hi']:.2f} & {c9['cl_lo']:.2f}--{c9['cl_hi']:.2f} & {iv(p16)} \\\\")
T += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
# S11 later retractions attributed through Crossref ORCID iDs (P19, post hoc), from the redacted f17 record
P19 = json.loads((E / "f17_attribution" / "runs" / F17R / "record.json").read_text())["results"]
e19, o19, c19 = P19["P19_estimates"], P19["P19_outcome"], P19["P19_coverage"]
rat = lambda m: f"{m['ratio']:.2f} ({m['cl_lo']:.2f}--{m['cl_hi']:.2f})"
T += ["\\begin{table}[htbp]", "\\centering", "\\caption{Later retractions attributed through the ORCID iDs in today's "
      f"Crossref records (post hoc). Of the {n(c19['later_publications'])} later-retracted publications in the graph, "
      f"{n(c19['with_meta_orcid'])} list an ORCID iD in OpenCitations Meta, {n(c19['with_crossref_orcid'])} in Crossref "
      f"(queried {P19['crossref']['retrieved']}) and {n(c19['with_either'])} in either. Crossref adds "
      f"{n(c19['crossref_only_links_primary'])} author links to primary authors; {o19['added']} of these authors gain a later "
      f"retraction ({n(o19['positives_meta'])} to {n(o19['positives_augmented'])} positives, none lost); the population "
      "is unchanged. Mantel--Haenszel odds ratios (95\\% CI) with the outcome as defined (Meta) and with the re-attributed "
      "outcome (Meta and Crossref). P1 and P6 as in Table~\\ref{tab:byclassadj}; the class ratio has journal-clustered "
      "intervals.}", "\\label{tab:attrib}", "\\footnotesize", "\\setlength{\\tabcolsep}{3pt}", "\\begin{tabular}{llcc}",
      "\\toprule", "Exposure & Strata & Meta & Meta and Crossref \\\\", "\\midrule"]
for k, lab in EXP:
    if k == "r1": continue
    T.append(f"{lab} & Primary & {ci(r6['A1_A2_A3_primary']['mh'][k])} & {ci(e19[k])} \\\\")
T.append("\\addlinespace")
for c, lab in [("y_refpeer", "referencing or peer review"), ("y_err_only", "honest error only")]:
    T.append(f"R2 pact rule, {lab} & Primary & {ci(r6['A1_A2_A3_primary']['mh_by_class'][f'r2|{c}'])} & {ci(e19[f'r2|{c}'])} \\\\")
T.append(f"R2, ratio of the two & Primary & {rat(r16['P17_ratio_primary']['r2'])} & {rat(e19['r2|ratio'])} \\\\ \\addlinespace")
for st, slab in [("P1_randties", "P1"), ("P6_randties", "P6")]:
    for k, lab in [("top_s1_recip_nc", "S1, top 1\\%"), ("top_s4_conc5", "S4, top 1\\%"), ("top_s5_self", "S5, top 1\\%"),
                   ("r2", "R2 pact rule"), ("r3", "R3 burst rule")]:
        T.append(f"{lab} & {slab} & {ci(r16[f'P17_{st}'][f'{k}|y'])} & {ci(e19[f'{st}|{k}'])} \\\\")
    T.append("\\addlinespace")
li = e19["s1_lift10000"]
T += [f"S1, lift among the top 10,000 & -- & {li['meta']:.2f} & {li['augmented']:.2f} \\\\", "\\bottomrule", "\\end{tabular}",
      "\\end{table}", ""]
# S12 informative strata of every pre-specified Mantel-Haenszel estimate (SPEC section 6), from f06
ROB = [("A1_A2_A3_primary", "Primary"), ("rob_a_all_eligible_prior_stratum", "(a)"), ("rob_b_T0p", "(b)"),
       ("rob_c_cwnc_ge100", "(c)"), ("rob_d_outcome_papers_in_W", "(d)"), ("rob_e_strata_journal_only", "(e)"),
       ("rob_f_top5pct", "(f)")]
cell = lambda m: f"{n(m['strata_informative'])} ({n(m['positives_in_informative'])})"
c3i = {k: C3[f"primary|{k}|y_misc_spec"]["strata_informative"] for k in ("top_s1_recip_nc", "top_s5_self", "r2")}
T += ["\\begin{table}[htbp]", "\\centering", "\\caption{Informative strata of every pre-specified Mantel--Haenszel "
      "estimate: strata with both exposed and unexposed authors and at least one positive, the only strata that contribute, "
      "with the positives they hold in parentheses. The first row gives all strata and all positives of each analysis. "
      "(a) All later retractions in the primary strata and in robustness analyses (a)--(f) (Section~\\ref{sec:res-robust}); "
      "in (e) the 8,487 strata are the 8,486 main journals and one group of authors without a main journal. (b) Outcome "
      "classes in the primary strata, with the positives of each class in the head.}", "\\label{tab:informative}",
      "\\scriptsize", "\\setlength{\\tabcolsep}{1.8pt}", "\\begin{tabular}{lccccccc}",
      "\\multicolumn{8}{l}{(a) All later retractions} \\\\", "\\toprule",
      "Exposure & " + " & ".join(l for _, l in ROB) + " \\\\", "\\midrule",
      "All strata (positives) & " + " & ".join(f"{n(r6[k]['mh']['top_s1_recip_nc']['strata_total'])} ({n(r6[k]['positives'])})" for k, _ in ROB) + " \\\\",
      "\\midrule"]
SHORT = {"top_s1_recip_nc": "S1, top 1\\%", "top_s2_recip": "S2, top 1\\%", "top_s4_conc5": "S4, top 1\\%",
         "top_s5_self": "S5, top 1\\%", "top_s6_co": "S6, top 1\\%", "bottom_s7_ch2": "S7, bottom 1\\%", "r1": "R1",
         "r2": "R2", "r3": "R3", "r_ge3": "$R \\geq 3$"}
for k, lab in EXP:
    T.append(f"{SHORT[k]} & " + " & ".join(cell(r6[a]["mh"][k]) for a, _ in ROB) + " \\\\")
CLI = [("y_refpeer", "Referencing or peer review"), ("y_mill", "Paper mill"), ("y_misc", "Other misconduct$^{a}$"),
       ("y_err_only", "Honest error only")]
T += ["\\bottomrule", "\\end{tabular}", "", "\\medskip", "", "\\begin{tabular}{lcccc}",
      "\\multicolumn{5}{l}{(b) Outcome classes, primary strata} \\\\", "\\toprule",
      "Exposure & " + " & ".join(f"{lab} ({n(A['positives_by_class'][c])})" for c, lab in CLI) + " \\\\", "\\midrule"]
for k, lab in [("top_s1_recip_nc", "S1, top 1\\%"), ("top_s5_self", "S5, top 1\\%"), ("r2", "R2 pact rule")]:
    T.append(f"{lab} & " + " & ".join(cell(A["mh_by_class"][f"{k}|{c}"]) for c, _ in CLI) + " \\\\")
T += ["\\bottomrule", f"\\multicolumn{{5}}{{p{{13cm}}}}{{$^{{a}}$As first coded by the evaluation code. As specified "
      f"(Table~\\ref{{tab:byclass}}; post hoc run), the informative strata number {n(c3i['top_s1_recip_nc'])} for S1, "
      f"{n(c3i['top_s5_self'])} for S5 and {n(c3i['r2'])} for R2.}} \\\\", "\\end{tabular}", "\\end{table}", ""]
# S13 profiles of the flagged groups and the work-normalised pact rate (P2, P3; post hoc), from f07
P2, P3 = r7["P2_profiles"], r7["P3_pact_rate_primary_strata"]
GR = [("top_s1_recip_nc", "S1, top 1\\%"), ("top_s5_self", "S5, top 1\\%"), ("r2", "R2 pact rule"), ("r3", "R3 burst rule"),
      ("top_pact_rate", "Pact rate, top 1\\%$^{a}$")]
pair = lambda e, u, key, fmt: f"{fmt(e[key])} / {fmt(u[key])}"
T += ["\\begin{table}[htbp]", "\\centering", "\\caption{Profiles of the flagged groups (post hoc): medians among flagged "
      "authors and among all other authors of the primary population (flagged / others). Team size: mean number of listed "
      "authors of the author's publications. $J$: journal risk (Section~\\ref{sec:signals}), here $\\times 10^{3}$. Outside "
      "citing works: distinct citing works without the author or an ORCID-identified co-author.}", "\\label{tab:profiles}",
      "\\footnotesize", "\\setlength{\\tabcolsep}{3pt}", "\\begin{tabular}{lrcccccc}", "\\toprule",
      "Group & Flagged & \\begin{tabular}[b]{@{}c@{}}Biomedical\\\\publications\\end{tabular} & "
      "\\begin{tabular}[b]{@{}c@{}}Citations\\\\received\\end{tabular} & $h$-index & \\begin{tabular}[b]{@{}c@{}}Team\\\\size\\end{tabular} & "
      "$J \\times 10^{3}$ & \\begin{tabular}[b]{@{}c@{}}Outside\\\\citing works\\end{tabular} \\\\", "\\midrule"]
for k, lab in GR:
    e, u = P2[f"{k}|exposed"], P2[f"{k}|unexposed"]
    T.append(f"{lab} & {n(e['n'])} & {pair(e, u, 'median_n_bio', lambda v: f'{v:.0f}')} & "
             f"{pair(e, u, 'median_n_in', lambda v: f'{v:,.0f}')} & {pair(e, u, 'median_h', lambda v: f'{v:.0f}')} & "
             f"{pair(e, u, 'median_team', lambda v: f'{v:.1f}')} & {pair(e, u, 'median_J_0', lambda v: f'{1000 * v:.2f}')} & "
             f"{pair(e, u, 'median_n_cw_nc', lambda v: f'{v:,.0f}')} \\\\")
T += ["\\bottomrule", f"\\multicolumn{{8}}{{p{{14cm}}}}{{$^{{a}}$Work-normalised pact rule: pact authors per 100 citing works, "
      f"top 1\\% (at least {r7['pact_rate_q99']:.2f}). Mantel--Haenszel odds ratio of later retraction in the primary strata "
      f"{ci(P3)}, {P3['exposed_pos']} flagged authors with a later retraction.}} \\\\", "\\end{tabular}", "\\end{table}", ""]
out = F_ROOT / "paper/content/supp_tables.tex"
out.write_text("% GENERATED by experiments/f12_tables/f12_tables.py from run records; do not edit by hand.\n" + "\n".join(T))
(run.dir / "supp_tables.tex").write_text(out.read_text())
run.log("tables", ["S1 deciles", "S2 screening", "S3 refpeer screening", "S4 ORs pre-specified I", "S5 ORs pre-specified II + post hoc", "S6 reasons by class", "S7 ORs by class", "S8 classes under adjusted strata", "S9 tie audit", "S10 publication-clustered intervals", "S11 attribution through Crossref", "S12 informative strata", "S13 profiles"])
run.log("reasons_by_class", {c: len(v) for c, v in groups.items()})
run.finish()
