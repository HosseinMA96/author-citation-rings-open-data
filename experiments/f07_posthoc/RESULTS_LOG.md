# F7 post hoc analyses: lab notebook

Plans in `../../POSTHOC.md` (round 1), written before the run. Reported in the paper as post hoc.

## f07_posthoc_20261126_01 (8 s)
Frozen SPEC and score hashes verified; same labels, primary population (793,299 authors, 2,419 positives) and strata as
`f06_eval_20261126_02`.

**P1, strata + deciles of citations received (MH OR [95% CI], exposed positives / exposed).** S1 top 1% 1.02 [0.59, 1.74]
(15/8,044); S2 1.20 [0.72, 1.99]; S4 1.70 [1.04, 2.77] (19/7,934); **S5 self-citation 1.61 [1.13, 2.29]** (38/7,933);
S6 1.53 [0.95, 2.46]; low S7 1.49 [0.94, 2.37]; R1 60.9 [4.5, 827.1] (1/12); **R2 pact rule 1.16 [0.99, 1.35]**
(372/58,933; was 1.52 in the primary strata); **R3 burst rule 1.40 [1.28, 1.54]** (unchanged); R ≥ 3 1.16 [1.00, 1.35].
R2 by class in these strata: referencing/peer review 1.63 [1.23, 2.16] (116); paper mill 0.95 [0.39, 2.28] (8); other
misconduct 1.01 [0.82, 1.26] (164); honest error only 1.42 [0.94, 2.16] (60).
Reading: most of the pact rule's association is citation volume; a residual association with referencing/peer-review
retractions remains.

**P3, size-free pact rate** (pact authors per 100 non-self citing works; top 1% = rate ≥ 4.08): primary strata 0.77
[0.37, 1.57] (8/7,961); by class: referencing/peer review and paper mill 0 exposed positives; other misconduct 0.64
[0.21, 1.98] (3); honest error only 2.22 [0.81, 6.11] (5).

**P2, profiles (medians, exposed vs unexposed; no outcomes).**
- S1 top 1%: biomedical papers 9 vs 10; citations received 137 vs 240; h 6 vs 7; mean team 5.7 vs 7.6; journal risk
  0.00044 vs 0.00057; non-co-author citing works 74.5 vs 190; band 5–9 53.7% vs 45.6%.
- S5 top 1%: 11 vs 10; 142 vs 240; h 7 vs 7; team 5.3 vs 7.7; J 0.00041 vs 0.00057.
- R2: **29 vs 10 papers; 1,925 vs 211 citations; h 21 vs 7**; team 9.6 vs 7.5; band ≥ 50 28.1% vs 2.7%.
- R3: 14 vs 9; 329 vs 196; h 9 vs 6.
- Pact-rate top 1%: 12 vs 10; 815 vs 237; team 21.2 vs 7.6 (large-team authors).
`P2_profiles.csv`.
