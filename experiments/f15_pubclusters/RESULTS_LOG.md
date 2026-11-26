# F15 post hoc P16 (intervals clustered by shared retraction events): lab notebook

Plan: `../../POSTHOC.md` round 4 addendum, written after reading `f14_class3_20261126_01` (69.6% of positives share a
later-retracted publication with another positive author) and before this run.

## f15_pubclusters_20261126_01 (385 s on the VM): cited
Clusters: connected components of primary authors linked by shared later-retracted publications; 792,104 clusters, 1,224
of them holding the 2,419 positives (largest 36 positives; 1,683 positives in clusters of two or more). Poisson(1)
weights per cluster, 1,000 resamples. Point estimates equal f06 exactly.
- Primary strata, publication-clustered 95% intervals: S1 0.85 (0.42-1.42); S2 0.99 (0.47-1.68); S4 1.45 (0.72-2.40);
  S5 1.32 (0.86-1.89); S6 1.50 (0.66-2.45); low S7 1.27 (0.71-1.95); R2 1.52 (1.25-1.79); R3 1.40 (1.28-1.54);
  R >= 3 1.53 (1.25-1.79). Close to the journal-clustered intervals; no conclusion changes.
- Classes (class 3 as specified): R2 referencing/peer review 2.79 (1.95-3.90), paper mill 1.54 (0.48-3.85), other
  misconduct 1.48 (1.14-1.85), honest error only 1.86 (1.18-2.82); ratio referencing/peer review to honest error 1.50
  (0.87-2.68). S5 referencing/peer review 1.85 (0.97-3.02). S1 referencing/peer review 1.83 (0.61-3.35).
- Lift at 10,000: S1 0.69 (0.36-1.07); S4 0.62 (0.30-1.05) (so "no better than chance", not "worse"); S5 1.41
  (0.92-2.05); S8 2.95 (2.31-3.71); journal risk 5.28 (4.30-6.18); productivity 4.30 (3.42-5.18).
