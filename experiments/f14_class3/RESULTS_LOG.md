# F14 post hoc round 4 (P14-P15): lab notebook

Plan: `../../POSTHOC.md` round 4 (written before this run), after an internal critique found that outcome class 3 had
been coded as E's misconduct list minus the four referencing/peer-review strings, whereas SPEC §5 specifies E's full list
(which includes `Compromised Peer Review` and `Rogue Editor`). A deviation from the frozen specification.

## f14_class3_20261126_01 (VM): cited
Frozen SPEC and score hashes verified. Implemented class 3 reproduces f13 exactly (18 of 18 estimates).
**P14, class 3 as specified:** 1,545 positives (implemented 1,304; 241 authors added whose only misconduct reasons are the
two shared strings; 485 also in class 1); classes 1, 2 and 4 unchanged (class 4 identical by construction).
Pre-specified A3 estimates with class 3 as specified (primary strata; RBG CI {journal-clustered} [exposed positives]):
S1 0.89 (0.46-1.74) {0.38, 1.47} [9]; S5 1.43 (0.96-2.13) {0.85, 2.12} [26]; **R2 1.48 (1.24-1.77) {1.11, 1.97} [221]**
(implemented: 0.82, 1.34, 1.27 (1.04-1.55)). Other exposures, primary strata: S4 1.54 (0.88-2.69); S6 1.53 (0.85-2.76);
R3 1.39 (1.25-1.54). P1: R2 1.15 (0.95-1.39); S5 1.70 (1.11-2.59). P6: R2 1.18 (0.96-1.45); S6 2.29 (1.09-4.80).
**P15, shared retraction events:** the 2,419 primary positives are linked to 1,910 distinct later-retracted publications;
positive authors per publication: median 1, 90th percentile 3, 99th 7, maximum 23; 748 publications have at least two
positive primary authors; 1,683 positives (69.6%) share a later-retracted publication with another positive author.
