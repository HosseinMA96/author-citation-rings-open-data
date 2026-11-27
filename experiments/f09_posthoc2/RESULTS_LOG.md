# F9 post hoc round 2 (P4-P8): lab notebook

Plans: `../../POSTHOC.md` round 2, written before these runs (after the review of draft v0.1). Post hoc.

## f09_posthoc2_20261126_01: FAILED (kept on the VM; folder without run.json)
Stopped before any estimate: pandas 3 keeps missing journal ids as NaN under `astype(str)`, so sorting the journal keys
failed (`'<' not supported between float and str`). Fix: explicit "NA" key for the 5 authors without a main journal.

## f09_posthoc2_20261126_02 (263 s)
Frozen SPEC and score hashes verified; primary population 793,299 (2,419 positives), 8,487 journal clusters (incl. "NA").
**P4, journal-clustered 95% intervals (1,000 resamples of main journals; OR [RBG CI] {clustered}).** Primary strata:
S1 0.85 [0.51, 1.43] {0.41, 1.35}; S2 0.99 {0.47, 1.54}; S4 1.45 {0.79, 2.26}; S5 1.32 {0.89, 1.79}; S6 1.50 {0.80, 2.31};
low S7 1.27 {0.80, 1.79}; R2 1.52 {1.23, 1.88}; R3 1.40 {1.24, 1.57}; R ≥ 3 1.53 {1.23, 1.89}; R1 not interpretable.
By class: R2 refpeer 2.79 {1.70, 4.29}, mill 1.54 {0.52, 3.42}, other misconduct 1.27 {0.95, 1.69}, honest error only
1.86 {1.27, 2.69}; S5 refpeer 1.85 {0.99, 3.02}; S1 refpeer 1.83 {0.56, 3.34}. Volume strata (P1): R2 1.16 {0.96, 1.39};
S5 1.61 {1.08, 2.22}; S4 1.70 {0.94, 2.69}; S1 1.02 {0.47, 1.58}.
**P6, finer strata** (main journal × productivity decile × citation decile × start band; 304,910 strata):
S1 0.88 [0.44, 1.79] {0.28, 1.66}; S2 1.25; S4 1.46; S5 1.32 [0.86, 2.03]; S6 1.72 [0.97, 3.04]; low S7 1.51;
**R2 1.27 [1.07, 1.49] {1.06, 1.50}; R3 1.17 [1.05, 1.30] {1.04, 1.29}**. Start bands: 2014 351,492; 2015–16 163,744;
2017–18 167,322; 2019–23 110,741 authors.
**P5, positive control** (all eligible, 800,996; 7,697 with prior retraction, 434 of them positive): prior retraction
**6.76 [5.93, 7.71] {5.73, 8.14}**; volume strata 5.82 [5.04, 6.72]; by class: refpeer 8.40 [6.62, 10.64], mill 10.66
[7.01, 16.21], other misconduct 7.03 [5.95, 8.31], honest error only 2.67 [1.42, 5.03]. The design detects a real association.
**P7, screening for the referencing/peer-review class** (622 positives, base rate 0.078%; lift [author bootstrap]
{clustered}): at 10,000: journal risk 10.59 [8.50, 12.59] {6.67, 14.60}; citations 5.36; S8 burst 4.72; rank average
S1 + J 3.95; productivity 3.44; R score 3.32; S5 2.04 [1.08, 3.03] {1.05, 3.21}; S3 2.04; S1 1.28 [0.51, 2.03]
{0.39, 2.25}. At 1,000: J 15.30, productivity 12.75, R score 10.20, S5 5.10 [1.21, 10.64].
**P4 screening, all later retractions, clustered:** S1 lift@10,000 0.69 {0.35, 1.03} (author bootstrap of this run
[0.42, 0.99]; the pre-specified f06 interval is [0.41, 0.99]); J 5.28 {3.75, 6.26}; productivity 4.30 {3.24, 5.47};
S5 1.41 {0.93, 1.96}; S8 2.95 {1.89, 3.96}; R score 2.20 {1.61, 2.90}.
**P8, top 1,000 by pact count S3** (0 positives): median mean team size **2,398** (rest 7.6); 98.5% with mean team size
≥ 100 (rest 1.0%); median biomedical papers 80, citations received 10,655, h 52, pact authors 1,382; journal risk 0.00023
(rest 0.00057). Consortium authorship: S3 counts co-authors of hyper-authored works as pact authors.
