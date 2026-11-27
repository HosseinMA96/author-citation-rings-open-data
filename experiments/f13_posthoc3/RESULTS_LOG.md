# F13 post hoc round 3 (P11-P13): lab notebook

Plans: `../../POSTHOC.md` round 3 (written before `_01`) and its data-driven addendum (written after reading `_01`, before
`_02`). After a review of draft v0.2. Everything here is post hoc.

## f13_posthoc3_20261126_01 (20 s on the VM): superseded by `_02`
All results identical to `_02` except that `_02` adds the R3 ratio. Reproduction check against earlier runs: 23 of 23
estimates identical (f06 primary and A3 for R2; f07 P1 for S1, S4, S5, R2, R3 and P1 by class for R2; f09 P6 for the
same exposures; f09 journal-clustered interval for R2 in P6).

## f13_posthoc3_20261126_02 (VM): cited
Frozen SPEC and score hashes verified; primary population 793,299 (2,419 positives; classes 622 / 141 / 1,304 / 248);
8,487 journals; strata: primary 24,026, P1 99,015, P6 304,910.

**P11, classes under the same strata** (OR (RBG CI) {journal-clustered} [exposed positives]). Pact rule R2:
- primary: referencing/peer review 2.79 (2.15-3.62) [116]; honest error only 1.86 (1.27-2.72) [60]; ratio 1.50 {0.77, 2.70};
- P1: 1.63 (1.23-2.16) {1.04, 2.34}; honest error only 1.42 (0.94-2.16) {0.95, 2.10}; ratio 1.15 {0.58, 2.03};
- P6: 1.84 (1.33-2.55) {1.24, 2.45}; honest error only **1.67 (1.07-2.61)** {1.12, 2.46}; ratio **1.10 {0.60, 1.83}**.
Reading (fixed in POSTHOC.md before the run): the honest-error estimate does not fall toward 1 and the ratio's interval
includes 1 in every stratification, so the pact rule is not shown to be specific to referencing/peer-review retractions.

Burst rule R3 (ratio added by the data-driven addendum): referencing/peer review 2.04 (1.72-2.42) primary, 2.01 P1, 1.45
(1.16-1.80) P6; honest error only 1.15 (0.88-1.50), 1.17 (0.89-1.55), 1.01 (0.73-1.39); ratio 1.77 {1.26, 2.41}, 1.71
{1.20, 2.33}, 1.43 {0.98, 2.01}.

Concentration S4 (top 1%): all later retractions 1.45 (0.91-2.30) primary, 1.70 (1.04-2.77) {0.94, 2.69} P1, 1.46
(0.80-2.65) P6; referencing/peer review 2.53 (1.24-5.20) [8] primary, 3.32 (1.52-7.27) {0.84, 7.67} P1, 2.98 (0.98-9.05)
P6; no exposed author in the honest-error class (ratio undefined).
Self-citation S5: P1 1.61 (1.13-2.29), referencing/peer review 2.59 (1.48-4.54) {1.38, 4.36} [15], honest error 1.02
(0.25-4.20) [2]; P6 1.32 (0.86-2.03), referencing/peer review 1.58 (0.78-3.22), honest error 1.87 (0.40-8.67) [2]; ratio
2.54 {0.60, 9.57} (P1), 0.84 {0.14, 3.36} (P6).
Reciprocity S1: referencing/peer review 1.83 (0.90-3.74) primary, **2.16 (1.01-4.59)** {0.63, 3.98} P1, 2.38 (0.87-6.51)
P6, all from 8 exposed positives; all later retractions 0.85, 1.02, 0.88.

**Screening value of the flags** (share with a later retraction; lift = share / base rate 0.305%; referencing/peer review
base 0.078%): R2 flags 58,933 authors (7.43%), 0.63% (0.57-0.70) retracted, lift 2.07; referencing/peer review 0.197%,
lift 2.51. R3 flags 291,668 (36.77%), 0.41%, lift 1.34. Top 1% S4: 0.24% (0.15-0.37), lift 0.79. Top 1% S5: 0.48%
(0.35-0.66), lift 1.57. Top 1% S1: 0.19% (0.11-0.31), lift 0.61.

**P12a, A4 deciles.** Deciles 1-3 (79,330 authors each) contain only authors with S1 = 0 (266,818 authors in all); the
split is by the seeded uniform key: mean `aid` (ORCID iD rank) 2,813,227 / 2,817,046 / 2,812,506. Positive counts 144,
195, 184: chi-square 8.26; over 1,000 alternative seeds of the key, 1.6% gave a value at least as large (median 1.40, 95th
percentile 5.74), so the imbalance is a chance outcome of the split. Pooled S1 = 0: 580 positives, 0.217% (0.200-0.236).

**P12b, A5 ties.** Every ranking breaks ties with the seeded uniform key (not by identifier or row order). Ties matter
only for the rule score R: 26,737 authors share the value at the 100, 1,000 and 10,000 cut-offs (176 positives, 0.658%,
expected lift 2.16), so its top-k metrics are draws from the tie group: lift at 100 6.56 as frozen (95% of random
tie-breaks 0.00-9.84; median 0.00), at 1,000 3.61 (0.66-3.94; median 2.30), at 10,000 2.20 (1.74-2.59; median 2.16).
Minor: S8 at 10,000 2.95 (2.79-3.08), productivity at 1,000 10.17 (9.84-10.49), S7 at 10,000 0.92 (0.89-0.92), S3 at
10,000 1.90 (1.87-1.90); all others have no ties at the cut-offs.

**P12c, P1 and P6 with random ties.** The decile variables of f07/f09 broke ties in row order (ORCID iD order); with a
seeded uniform key, 4,414 authors change citation decile and 134,618 change productivity decile. Estimates for all later retractions change by at most 0.09 (S7 low C/h² in P6: 1.51 -> 1.42; S2 1.25 -> 1.17; S5 1.32 -> 1.40; S6 1.72 -> 1.64; R2 1.27 -> 1.26; row-order values from f07/f09, which `_01` reproduced exactly); class estimates with few
exposed positives move more (S6 referencing/peer review in P6, 6 positives: 3.27 -> 1.87), within their intervals. No
reading changes; R2 in P6: referencing/peer review 1.85, honest error only 1.62, ratio 1.14 {0.63, 1.94}.

## f13_desc_20261126_01 (laptop): cited
P13 from the f03 per-year counts: biomedical publications 2014-2023 have 75,141,872 author positions, of which 17,849,778
(**23.8%**) carry an ORCID iD; 7,510,543 of 11,782,947 publications with authors (63.7%) have at least one ORCID author.
