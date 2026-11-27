# F6 evaluation: lab notebook

First contact with post-T0 labels. Script `f06_eval.py` checks, before reading any label, that `SPEC.md` has the frozen
hash 07200ecb… and that the score file has the hash recorded by `f05_scores_20261126_01` (5b7036b4…). Aggregates only.

## f06_eval_20261126_01: FAILED (kept on the VM; folder without run.json)
Stopped at the stratum keys (`TypeError: sequence item 0: expected str instance, float found`: pandas `astype(str)` on
the nullable journal-id column). Before the error it had logged only the population counts (identical to `_02`); no
exposure was cross-tabulated with an outcome. Fix: keys built with a plain Python join of the stratum values.

## f06_eval_20261126_02 (62 s): the evaluation cited in the paper
**Counts.** Pre-eligible 859,157; eligible 800,996; eligible with prior retraction 7,697; **primary 793,299 with 2,419
positives (base rate 0.305%)**; eligible positives 2,853 (434 among authors with a prior retraction). Positives by class
(primary): referencing/peer review 622; paper mill 141; other misconduct 1,304; honest error only 248. Strata
(main journal × band): 24,026.

**A1 (primary, decision rule).** Top 1% of S1 (S1 ≥ 0.1111): 8,044 authors, 15 positives (0.19%); unexposed 2,404 positives.
**MH OR 0.85 [0.51, 1.43]** (424 informative strata, 1,198 positives in them, 15 exposed). The CI includes 1: by the
pre-specified rule, **the non-co-author reciprocity signal does not hold within journal and productivity.**

**A2 (other signals; MH OR [95% CI], exposed positives / exposed).** Top 1% S2 reciprocity (all works) 0.99 [0.61, 1.59]
(18/8,165); S4 concentration 1.45 [0.91, 2.30] (19/7,934); S5 self-citation 1.32 [0.95, 1.84] (38/7,933); S6 co-author
citation 1.50 [0.95, 2.36] (20/7,933); bottom 1% S7 C/h² 1.27 [0.83, 1.96] (22/8,042); **R1** co-author rule 118.5
[9.7, 1,448.6] (1/12; 5 informative strata; not interpretable); **R2 pact rule 1.52 [1.32, 1.75] (372/58,933)**; **R3
burst rule 1.40 [1.29, 1.53] (1,196/291,668)**; R ≥ 3 1.53 [1.33, 1.75] (373/58,943).

**A3 (by outcome class).** S1 top 1%: referencing/peer review 1.83 [0.90, 3.74] (8 exposed positives); paper mill 1.21
[0.17, 8.94] (1); other misconduct 0.82 [0.38, 1.73] (7); honest error only 0.77 [0.19, 3.06] (2).
S5 top 1%: 1.85 [1.09, 3.14] (15); 1.02 [0.14, 7.57] (1); 1.34 [0.86, 2.09] (21); 0.72 [0.18, 2.85] (2).
**R2: referencing/peer review 2.79 [2.15, 3.62] (116); paper mill 1.54 [0.72, 3.30] (8); other misconduct 1.27
[1.04, 1.55] (164); honest error only (negative control) 1.86 [1.27, 2.72] (60).** R2 is elevated for the negative
control too: it is not specific to manipulation.

**A4 (dose, S1 deciles, unadjusted).** Positive rate 0.18% (decile 1), 0.25%, 0.23% (deciles 1–3 all S1 = 0, split at
random), 0.38%, 0.42%, 0.37%, 0.39%, 0.32%, 0.28%, 0.22% (decile 10, S1 0.0434–0.52); top 1% 0.19% [0.11, 0.31]. No
increase at high S1. `A4_dose_s1.csv`.

**A5 (screening; primary population; base rate 0.305%).** Precision@1,000 (lift) / lift@10,000 [95% CI] / AP:
S1 0.20% (0.66) / 0.69 [0.41, 0.99] / 0.0030; S2 0.10% (0.33) / 0.72; S3 pact count 0.00% (0) / 1.90 [1.46, 2.47];
S4 0.50% (1.64) / 0.62; S5 0.70% (2.30) / 1.41 [1.01, 1.89]; S6 0.40% (1.31) / 0.79; low S7 0.30% (0.98) / 0.92;
S8 burst 0.40% (1.31) / 2.95 [2.35, 3.61]; R score 1.10% (3.61) / 2.20 [1.68, 2.72]; **journal risk J 1.60% (5.25) /
5.28 [4.45, 6.04] / 0.0087; productivity 3.10% (10.17) / 4.30 [3.54, 4.96] / 0.0076; citations 1.00% (3.28) / 4.23
[3.51, 4.91]**; rank average of S1 and J 1.70% (5.58) / 2.62. **Primary comparison S1 − J at k = 1,000: −1.4 points
[−2.3, −0.6].** `A5_screening.csv`.

**Pre-specified robustness (MH OR for S1 top 1% | R2).** (a) all eligible, prior-retraction stratum: 0.78 [0.47, 1.30] |
1.52 [1.33, 1.73]; (b) T0' = 2023-09-30 (3,457 positives): 0.88 [0.57, 1.35] | 1.42 [1.25, 1.60]; (c) |CW_nc| ≥ 100
(548,033 authors): 1.13 [0.68, 1.88] | 1.51 [1.31, 1.73] (S4 1.65 [1.08, 2.51] here); (d) outcome papers from 2014–2023
(2,151 positives): 0.92 [0.55, 1.53] | 1.52 [1.31, 1.77] (S5 1.42 [1.01, 1.98], S6 1.60 [1.01, 2.52] here);
(e) strata by journal only: 0.74 [0.45, 1.24] | **3.20 [2.84, 3.61]** (R3 1.68); (f) top 5%: 0.93 [0.75, 1.15] | 1.52.
Reading: S1 is null throughout; R2 is positive throughout but its OR halves when productivity bands enter the strata
(e vs primary), so part of it may be residual productivity or citation volume. A few top-1% signals cross 1 in single
robustness analyses (S4 in c; S5, S6 in d), not in the primary analysis: no correction for multiple comparisons was
pre-specified, so these are reported as such, without emphasis.

## Correction (2026-11-27)
"First contact with post-T0 labels" (top of this log) is inaccurate: run `f03_authors_20261126_01` had already counted
labels per author before the specification was written (for example 806 authors with at least five biomedical
publications and a later referencing or peer-review retraction), as the paper's Methods §3.1 discloses. This run is the
first to link scores to outcome labels. The paper and the timeline figure (`f18_design_20261126_02`) say so.
