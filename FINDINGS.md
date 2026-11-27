# Project F findings: claim → number → run

Every number in the paper, with the run that produced it (`experiments/<exp>/runs/<run>/run.json` unless stated). Post hoc
results are marked. Laptop clock is 1 h behind UTC; run timestamps come from the VM clock.

## Data and identity (f03_authors_20261126_01; graph size from Paper C's c6_full_20261031_02)
| Claim | Number | Source |
|---|---|---|
| Graph publications / citation links | 107,030,533 / 1,962,840,983 | `graph_nodes`; C run `c6_full_20261031_02` (edges) |
| Meta records | 107,067,700 | `meta_records.rows` |
| Biomedical publications | 31,464,435 | `biomedical_nodes` (= D5) |
| Author positions / with ORCID | 352,057,220 / 52,206,594 (14.8%) | `author_slots`, `slots_with_orcid` |
| Distinct ORCID iDs | 5,723,850 | `distinct_orcid` |
| Non-ORCID internal ids in exactly one record (2% sample) | 5,827,133 of 5,827,133 | `non_orcid_ra_sample_2pct` |
| ORCID iDs under several internal ids | 1,315,288 | `orcid_with_several_ra_omids` |
| ORCID coverage, biomedical, author positions / publications with ≥ 1 | 2014: 20.1% / 54.9%; 2019: 26.3% / 71.1%; 2020: 26.8% / 70.8%; 2023: 24.7% / 63.1% | `bio_coverage_by_year` |
| Retracted biomedical publications after T0 with ≥ 1 ORCID author | 2,946 of 5,117 (57.6%) | `retracted_bio_nodes_by_period_with_orcid` |
| Retraction Watch match rate | 83.3% (52,254 of 62,735) | D run `d05_match_20261101_02` |
| Graph complete to about Sept 2023 | – | D run `d00_cutoff_20261101_01` |

## Populations and scores (f05_scores_20261126_01, frozen; f06_eval_20261126_02)
| Claim | Number | Source |
|---|---|---|
| Pre-eligible (≥ 5 biomedical papers 2014–2023, a paper 2019–2023) | 859,157 | f05 `authors_pre_eligible` |
| Eligible (|CW_nc| ≥ 20) | 800,996 | f05 `authors_eligible` |
| Eligible with prior retraction | 7,697 | f05 |
| Primary population | 793,299 | f05, f06 `counts` |
| Bands 5–9 / 10–19 / 20–49 / ≥ 50 | 362,727 / 250,354 / 143,642 / 36,576 | f05 `primary_by_band` |
| Main journals; strata | 8,486; 24,026 | f05; f06 `strata_total` |
| Positives (primary); base rate | 2,419; 0.305% | f06 |
| By class: referencing/peer review, paper mill, other misconduct, honest error only | 622, 141, 1,304, 248 | f06 `positives_by_class` |
| S1 median / p90 / p99 | 0.0081 / 0.0434 / 0.1111 | f05 `primary_score_quantiles` |
| Rule hits R1 / R2 / R3 | 12 / 58,933 (7.4%) / 291,668 (36.8%) | f05 `primary_rule_hits` |
| Score frozen SHA-256 | 5b7036b4eb000063… | f05 `scores_frozen` |
| SPEC v1 SHA-256 | 07200ecb9affa9f2… | `experiments/f04_spec/RESULTS_LOG.md` |

## Main results (f06_eval_20261126_02; pre-specified)
| Claim | Number |
|---|---|
| **A1** S1 top 1% (S1 ≥ 0.1111): exposed, positives | 8,044; 15 (0.19%) |
| **A1** MH OR | **0.85 [0.51, 1.43]**; 424 informative strata |
| A2 S2 / S4 / S5 / S6 / low S7 | 0.99 [0.61, 1.59] / 1.45 [0.91, 2.30] / 1.32 [0.95, 1.84] / 1.50 [0.95, 2.36] / 1.27 [0.83, 1.96] |
| A2 R1 | 12 authors, 1 positive; 118.5 [9.7, 1,448.6] (5 informative strata) |
| A2 R2 / R3 / R ≥ 3 | **1.52 [1.32, 1.75]** (372/58,933) / **1.40 [1.29, 1.53]** (1,196/291,668) / 1.53 [1.33, 1.75] |
| A3 R2 by class: refpeer / mill / other misconduct / honest error only | **2.79 [2.15, 3.62]** / 1.54 [0.72, 3.30] / 1.27 [1.04, 1.55] / **1.86 [1.27, 2.72]** |
| A3 S1 by class | 1.83 [0.90, 3.74] / 1.21 [0.17, 8.94] / 0.82 [0.38, 1.73] / 0.77 [0.19, 3.06] |
| A3 S5 by class | 1.85 [1.09, 3.14] / 1.02 [0.14, 7.57] / 1.34 [0.86, 2.09] / 0.72 [0.18, 2.85] |
| A4 positive rate by S1 decile | 0.18%, 0.25%, 0.23%, 0.38%, 0.42%, 0.37%, 0.39%, 0.32%, 0.28%, 0.22%; top 1% 0.19% [0.11, 0.31] |
| A5 S1: precision@1,000 (lift), lift@10,000 | 0.20% (0.66); 0.69 [0.41, 0.99] |
| A5 journal risk J | 1.60% (5.25); 5.28 [4.45, 6.04]; AP 0.0087 |
| A5 productivity | 3.10% (10.17); 4.30 [3.54, 4.96]; precision@100 8% |
| A5 citations received | 1.00% (3.28); 4.23 [3.51, 4.91] |
| A5 R score / S8 burst / S3 pact count / S5 | lift@1,000 3.61 / 1.31 / 0 / 2.30; lift@10,000 2.20 / 2.95 / 1.90 / 1.41 |
| A5 rank average S1 + J | 1.70% (5.58); lift@10,000 2.62 |
| A5 primary comparison S1 − J at k = 1,000 | −1.4 points [−2.3, −0.6] |
| Robustness S1 (a)–(f) | 0.78, 0.88, 1.13, 0.92, 0.74, 0.93 (CIs all include 1) |
| Robustness R2 (a)–(f) | 1.52, 1.42, 1.51, 1.52, **3.20 [2.84, 3.61]** (journal-only strata), 1.52 |
| Single-analysis crossings | S4 (c) 1.65 [1.08, 2.51]; S5 (d) 1.42 [1.01, 1.98]; S5 (e) 1.44 [1.04, 2.00]; S6 (d) 1.60 [1.01, 2.52] |
| T0' population, positives | 794,337; 3,457 |

## Post hoc (f07_posthoc_20261126_01; POSTHOC.md round 1)
| Claim | Number |
|---|---|
| P1 (+ citation-volume deciles): R2 | **1.16 [0.99, 1.35]** |
| P1 R2 by class: refpeer / mill / other / honest error | 1.63 [1.23, 2.16] / 0.95 [0.39, 2.28] / 1.01 [0.82, 1.26] / 1.42 [0.94, 2.16] |
| P1 S1 / S5 / S4 / R3 | 1.02 [0.59, 1.74] / **1.61 [1.13, 2.29]** / 1.70 [1.04, 2.77] / 1.40 [1.28, 1.54] |
| P3 work-normalised pact rate top 1% (≥ 4.08 per 100 citing works; median team 21.2 vs 7.6) | 0.77 [0.37, 1.57]; 8 exposed positives |
| P2 R2-flagged vs not: biomedical papers, citations, h | 29 vs 10; 1,925 vs 211; 21 vs 7 |
| P2 S1 top 1% vs not: citations, team, journal risk | 137 vs 240; 5.7 vs 7.6; 0.00044 vs 0.00057 |

## Post hoc round 2 (f09_posthoc2_20261126_02, f10_names_20261126_01, f11_cov_20261126_01, f11_crossref_20261126_02; POSTHOC.md round 2)
| Claim | Number |
|---|---|
| P4 journal clusters (main journals, incl. "NA") | 8,487 |
| P4 S1 top 1%, journal-clustered interval | 0.85 {0.41, 1.35} |
| P4 R2 / R3 / R ≥ 3, clustered | 1.52 {1.23, 1.88} / 1.40 {1.24, 1.57} / 1.53 {1.23, 1.89} |
| P4 R2 by class, clustered: refpeer / mill / other / honest error | 2.79 {1.70, 4.29} / 1.54 {0.52, 3.42} / 1.27 {0.95, 1.69} / 1.86 {1.27, 2.69} |
| P4 S5 refpeer; S1 refpeer (clustered) | 1.85 [1.09, 3.14] {0.99, 3.02}; 1.83 {0.56, 3.34} |
| P4 volume strata, clustered: R2 / S5 / S1 | 1.16 {0.96, 1.39} / 1.61 {1.08, 2.22} / 1.02 {0.47, 1.58} |
| P6 finest strata (journal × productivity decile × citation decile × start band; 304,910 strata) | S1 0.88 [0.44, 1.79]; S5 1.32 [0.86, 2.03]; S6 1.72 [0.97, 3.04]; **R2 1.27 [1.07, 1.49]**; R3 1.17 [1.05, 1.30] |
| P5 positive control (800,996 eligible; 7,697 with prior retraction, 434 positive) | **6.76 [5.93, 7.71] {5.73, 8.14}**; volume strata 5.82 [5.04, 6.72]; honest error only 2.67 [1.42, 5.03] |
| P7 screening, refpeer class (622 positives, base rate 0.078%), lift@10,000 | J 10.59 [8.50, 12.59] {6.67, 14.60}; citations 5.36; S8 4.72; productivity 3.44; R score 3.32; S5 2.04 [1.08, 3.03]; S1 1.28 [0.51, 2.03] |
| P4 screening, all later retractions, S1 lift@10,000 clustered | 0.69 {0.35, 1.03}; J 5.28 {3.75, 6.26}; productivity 4.30 {3.24, 5.47} |
| P8 top 1,000 by S3 (0 positives) | median mean team size 2,398 (rest 7.6); 98.5% with mean team ≥ 100 (rest 1.0%) |
| P9 sample (2,033 authors; S1 reproduced exactly) | name-flagged: 19.8% of outside citing works, 39.5% of reciprocal ones; Spearman 0.85; top-1% in sample 21 → 11 |
| P10 Meta, papers with ≥ 1 ORCID author, 2019 → 2022 | 71.1% → 60.7% |
| P10 Meta vs Crossref today (100 DOIs per year) | 2018 0.75 vs 0.43; 2019 0.72 vs 0.50; 2022 0.67 vs 0.71; 2023 0.68 vs 0.68 |
| P10 publisher drops in Meta 2019 → 2022 | Frontiers 60.9% → 3.1%; Elsevier 66.9% → 44.9% |

## Post hoc round 3 (f13_posthoc3_20261126_02, f13_desc_20261126_01; POSTHOC.md round 3 and its data-driven addendum)
| Claim | Number |
|---|---|
| Reproduction of f06/f07/f09 estimates by the f13 code | 23 of 23 identical |
| R2 referencing/peer review vs honest error only, primary strata | 2.79 (2.15–3.62) vs 1.86 (1.27–2.72); ratio 1.50 {0.77, 2.70} |
| R2 in P1 strata | 1.63 (1.23–2.16) vs 1.42 (0.94–2.16); ratio 1.15 {0.58, 2.03} |
| R2 in P6 strata | **1.84 (1.33–2.55) vs 1.67 (1.07–2.61); ratio 1.10 {0.60, 1.83}**: not shown to be specific |
| R3 ratio referencing/peer review to honest error (data-driven addendum) | 1.77 {1.26, 2.41} primary; 1.71 {1.20, 2.33} P1; 1.43 {0.98, 2.01} P6; honest error 1.15, 1.17, 1.01 |
| S4 top 1%: P1; P6; referencing/peer review primary | 1.70 (1.04–2.77) {0.94, 2.69}; 1.46 (0.80–2.65); 2.53 (1.24–5.20) [8 of 19 exposed positives; 0 honest error] |
| S1 referencing/peer review: primary; P1; P6 | 1.83 (0.90–3.74); 2.16 (1.01–4.59) {0.63, 3.98}; 2.38 (0.87–6.51) [8 exposed positives] |
| S5 class ratio P1; P6 | 2.54 {0.60, 9.57}; 0.84 {0.14, 3.36} |
| Flag precision (lift): R2; R3; S4; S5; S1 | 0.63% (2.07), refpeer 0.197% (2.51); 0.41% (1.34), flags 36.77%; 0.24% (0.79); 0.48% (1.57); 0.19% (0.61) |
| S1 = 0 authors; pooled rate | 266,818; 580 positives, 0.217% (0.200–0.236) |
| Deciles 1–3: chi-square; alternative seeds at least as large; mean ORCID rank | 8.26; 1.6% of 1,000; 2,813,227 / 2,817,046 / 2,812,506 |
| R score tie group at all screening cut-offs | 26,737 authors, 176 positives (0.658%, expected lift 2.16); lift@1,000 3.61 as computed, median 2.30 (0.66–3.94) over random tie-breaks |
| Random instead of row-order decile ties, P1/P6, all later retractions | max change 0.09 (S7 low C/h² in P6 1.51 → 1.42); 4,414 / 134,618 authors change citation / productivity decile |
| Biomedical publications 2014–2023: author positions with ORCID iD; publications with ≥ 1 ORCID author | **23.8%** (17,849,778 of 75,141,872); 63.7% (7,510,543 of 11,782,947) |

## Post hoc round 4 (f14_class3_20261126_01, f15_pubclusters_20261126_01; POSTHOC.md round 4 and addendum)
| Claim | Number |
|---|---|
| Outcome class 3: as specified (E's full misconduct list) vs as first coded (minus the four referencing/peer-review strings) | 1,545 vs 1,304 positives (241 added; 485 also in class 1); classes 1, 2, 4 unchanged |
| Pre-specified A3 with class 3 as specified: S1; S5; R2 | 0.89 (0.46–1.74); 1.43 (0.96–2.13); **1.48 (1.24–1.77)** {1.11, 1.97} (first coded: 0.82; 1.34; 1.27) |
| Shared retraction events behind the 2,419 positives | 1,910 distinct later-retracted publications; 1,683 positives (69.6%) share one with another positive; max 23 on one publication |
| Publication-clustered intervals (P16), primary strata: S1; R2; R3 | 0.42–1.42; 1.25–1.79; 1.28–1.54 |
| P16 R2 classes: referencing/peer review; honest error; ratio | 2.79 (1.95–3.90); 1.86 (1.18–2.82); 1.50 (0.87–2.68) |
| P16 lift at 10,000: S1; S4; journal risk; productivity | 0.69 (0.36–1.07); 0.62 (0.30–1.05); 5.28 (4.30–6.18); 4.30 (3.42–5.18) |
| Precision at k = 100: S4; S6; journal risk; productivity | 3%; 3%; 2%; 8% (f06 A5) |

## Main adjusted values with random decile ties (f16_randties_20261126_01; POSTHOC.md round 5)
Since round 5 the paper reports the P1 and P6 strata with random decile ties; the row-order values above (f07, f09, f13)
are the check (largest difference 0.09).
| Claim | Number |
|---|---|
| P1: S4; S5 (journal-clustered) | 1.71 (1.05–2.78) {0.94, 2.69}; 1.59 (1.11–2.26) {1.07, 2.17} |
| P1: R2; S1 | 1.16 (0.99–1.35); 1.01 (0.59–1.72) |
| P6 (304,817 strata): R2; R3; S1; S4; S5 | 1.26 (1.07–1.49); 1.18 (1.06–1.31); 0.86 (0.42–1.78); 1.44 (0.77–2.67); 1.40 (0.89–2.19) |
| P6 R2: referencing/peer review vs honest error; ratio | 1.85 (1.34–2.55) vs 1.62 (1.03–2.55); **1.14 {0.63, 1.94}** |
| P6 R3 ratio (data-driven) | 1.50 {1.06, 2.08}; honest error 1.00 (0.73–1.37) |
| P6 S1 referencing/peer review | 2.19 (0.79–6.06) |

## Post hoc round 6: outcome attribution (f17_attribution_20261126_01, redacted record f17_redact_20261126_01; POSTHOC.md round 6 and addendum)
| Claim | Value |
|---|---|
| Frontiers network (announced 29 July 2025): Retraction Watch records, July–Sept 2025, peer-review/referencing/COI reasons | 124, all in the graph (124 publications) |
| ... with an ORCID iD in Meta; in Crossref | 4; 0 |
| Primary authors attached (Meta; Crossref only) | 1 (already positive; profile not reported, fewer than 10); 0 |
| Later-retracted graph publications: with DOI; ORCID iD in Meta; in Crossref; in either | 8,769: 8,748; 3,989; 2,880; 4,112 |
| Crossref query: DOIs; found; not found; errors | 8,705; 8,689; 16; 0 |
| Positives, Meta → Meta and Crossref (added; lost) | 2,419 → 2,438 (19; 0) |
| Largest change of any OR (S4 in P6); in primary strata (S6) | 1.44 → 1.55 (+0.12); 1.50 → 1.56 (+0.07) |
| S6 with re-attributed outcome | 1.56 (1.00–2.44), lower bound 1.004 |
| R2; S1; R2 class ratio | 1.51 (1.31–1.74); 0.84 (0.50–1.41); 1.45 {0.75, 2.65} |
| S1 lift at 10,000 | 0.69 → 0.72 |
| Added positives flagged by R3 (R3 share 36.8%) | 14 of 19 (exposed positives 1,196 → 1,210) |

## Design figures (f18_design_20261126_01)
`fig_flow.pdf` (population flow from f03 and f06 counts), `fig_timeline.pdf` (data windows; analysis steps in order with
UTC times from the run records, the f04 freeze log and GitHub's push record).

## Supplementary tables (f12_tables_20261126_14)
`paper/content/supp_tables.tex`: Tables S1–S11 generated from f06, f07, f09, f13, f14, f15, f16, f17 (redacted) and Paper D `d02_rw_20261101_01` (reason counts).

## Figures (f08_fig_20261126_06)
`fig1_forest.pdf` (f06 A2/A3 + f07 P1), `fig2_screening.pdf` (f06 A5), `fig3_orcid_coverage.pdf` (f03).
