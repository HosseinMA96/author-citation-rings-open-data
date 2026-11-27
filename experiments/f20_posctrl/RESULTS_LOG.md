# f20 positive control with outcome class 3 as specified: results log (POSTHOC.md round 8, P21; post hoc, reporting only)

Run `f20_posctrl_20261127_01` (VM, started 2026-11-27T20:19:41Z, 7 s). Code, labels and bootstrap seeds of f09 (P5),
with class 3 as specified added. Frozen spec and scores verified. Checks passed: the eligible population (800,996
authors, 7,697 with a prior retraction, 2,853 later positives), the all-cause estimate and the four first-coded classes
reproduce f09 P5 exactly (exposed counts, informative strata, odds ratios, intervals, journal-clustered intervals).

Prior retraction as the exposure, all eligible authors, primary strata:
| Class (positives) | Odds ratio (95% CI) | Journal-clustered | Exposed positives | Informative strata |
|---|---|---|---|---|
| Other misconduct, as specified (1,861) | 7.21 (6.18–8.42) | 5.82–9.14 | 316 | 631 |
| Other misconduct, as first coded (1,571) | 7.03 (5.95–8.31) | 5.62–8.85 | 267 | 574 |

Used in Supplementary Table S7 (`f12_tables_20261127_01`): the prior-retraction row now uses class 3 as specified, like
every other row; the first-coded value is in the note. A first launch failed before running (the code push to the VM
hit an SSH error); nothing was written, and the run above is the only f20 run.
