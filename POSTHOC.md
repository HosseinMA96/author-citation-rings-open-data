# Project F: post hoc analyses

Each plan is written **before** it is run and is reported in the paper as post hoc (SPEC.md §9 lists no amendment: these
do not change any pre-specified analysis). All use the frozen scores of `f05_scores_20261126_01` (hash checked) and the
labels, populations and strata of `f06_eval_20261126_02`. Aggregates only.

## Round 1 (written 2026-11-26, after reading f06_eval_20261126_02)

**Why.** The pact rule R2 is associated with later retraction (MH OR 1.52) but also with honest-error-only retractions
(1.86), and its OR falls from 3.20 to 1.52 when the four productivity bands enter the strata. S3 is a count: it grows with
the number of citing works and citing authors, which the coarse bands only partly hold fixed. The questions are whether
R2 (and R3) measure citation volume rather than exchange, and what the flagged groups look like.

- **P1, citation-volume strata.** Repeat A2 (all exposures) and A3 for R2 with strata = main journal × productivity band ×
  decile of citations received (`n_in`, deciles over the primary population). Expectation: if R2's OR moves to about 1,
  the pact rule mostly measures citation volume; if it stays near 1.5, it does not.
- **P2, profiles (no outcomes).** For S1 top 1%, S5 top 1%, R2 and R3, exposed vs unexposed: medians of biomedical papers,
  citations received, h, mean team size, journal risk J, non-co-author citing works; share by productivity band.
- **P3, size-free pact rate.** Pact authors per 100 non-self citing works, `100 * s3_pact / n_cw`, built from frozen
  columns only. Top 1% vs the rest: MH OR in the primary strata and in the P1 strata, and by outcome class
  (including the honest-error negative control).
- Multiplicity: none of these is a test of a new hypothesis on which the conclusions rest; they are reported with their
  intervals and the label "post hoc".

## Round 2 (written 2026-11-26, after an external review of draft v0.1; before any of these runs)

**Why.** The reviewer raised: non-independence of authors (co-authors of the same retracted paper, mass retractions in
one journal), so the author-level intervals may be too narrow; residual confounding (coarse productivity bands, no
career-age adjustment) and the lack of a positive control; screening dominated by productivity; the zero lift of the
pact count at k = 1,000; what S1 measures when only ORCID-identified co-authors can be excluded; and the dip in ORCID
coverage in 2021-2022. Every item below is post hoc and labelled so.

- **P4, intervals clustered by main journal.** Resample main journals with replacement (1,000 resamples, seed
  `SeedSequence([20261126, crc32(label)])`); strata are nested in journals, so each resample re-weights whole strata.
  Mantel-Haenszel ORs for all A2 exposures and for A3 (S1, S5, R2 by class) in the primary strata, for P1 (volume strata)
  and for P5-P6; percentile 95% intervals. Screening (A5, P7): author weights = the multiplicity of their main journal.
- **P5, positive control.** Exposure = prior retraction (first notice <= T0); population = all eligible authors
  (800,996); strata = main journal x band, and the P1 strata. Expected: a clear association, showing that the design can
  detect one.
- **P6, finer adjustment.** Strata = main journal x productivity decile (biomedical papers, rank-based) x citation-volume
  decile x start band (first year with a paper in W: 2014 [includes earlier starters], 2015-2016, 2017-2018,
  2019-2023). All A2 exposures.
- **P7, screening for the referencing/peer-review class.** A5 metrics with y = referencing/peer-review outcome
  (622 positives), all rankings; author-level paired bootstrap and journal-clustered bootstrap.
- **P8, the top 1,000 by pact count S3.** Medians of team size, biomedical papers, citations received, h, journal risk;
  shares with mean team size >= 20 and >= 100; against the rest of the primary population. No outcome beyond the known
  count (0 of 1,000).
- **P9, what S1 counts as "outside" (name matching, sample).** Authors with `hash(aid, 20261126) % 400 = 0` in the primary
  population. For each, name keys (lower-case family name + first initial, from the Meta author strings) of every person
  listed on their papers in W (with or without ORCID) and of the author themself (the name on their ORCID slots). Among
  their non-co-author citing works (CW_nc), flag works whose listed names include (i) the author's own name key
  (hidden self-citation) or (ii) a name key of someone listed on the author's papers (hidden co-author). Report the shares
  of CW_nc works and of reciprocal CW_nc works flagged, and S1 recomputed without flagged works (Spearman correlation with
  S1; share of sampled authors above the population S1 threshold before and after). Names are used only on the VM; only
  aggregates leave it. Name keys over-match common names, so (ii) is an upper bound.
- **P10, the 2021-2022 ORCID dip.** (a) Meta coverage of biomedical publications by publisher, 2019 vs 2022 (top 15
  publishers by volume), from the Meta `publisher` column. (b) A deterministic sample of 100 biomedical DOIs per year
  2018-2023 (`hash(iid, 20261126)` order); for each, the number of ORCID iDs on the authors in Meta and in the Crossref
  REST API record today. If Crossref has ORCIDs that Meta lacks mainly in 2021-2022, the dip comes from Meta's
  ingestion; if Crossref lacks them too, from the source metadata.

## Round 3 (written 2026-11-26, after an external review of draft v0.2; before any of these runs)
Prompted by three review points: the specificity argument for the pact rule set an adjusted estimate (referencing or peer
review under P1, 1.63) against an unadjusted one (honest error, 1.86); adjustment for citation volume strengthens S4 and
S5; and the unequal counts of Table S1 deciles 1-3 (144, 195, 184) raise the question of how ties are broken. Known when
this was written: f07 `P1_r2_by_class` (R2 under P1: referencing/peer review 1.63 [1.23, 2.16], honest error only 1.42
[0.94, 2.16]); f09 P6 for all later retractions only; the f06 code breaks ties in A4 and A5 with a seeded uniform key,
while the post hoc decile variables of P1 and P6 (`rank(method="first")`) break ties in row order, that is ORCID iD order.
Every item below is post hoc.

- **P11, outcome classes under the adjusted strata.** Exposures: top 1% of S1, S4, S5, S6; R2; R3. Outcomes: all later
  retractions and the four classes. Mantel-Haenszel ORs with RBG intervals in the P1 strata (main journal x band x
  citation decile) and the P6 strata (main journal x productivity decile x citation decile x start band), as defined in
  f07/f09, with journal-clustered percentile intervals (1,000 resamples of main journals). For R2, S4 and S5, the ratio
  of the referencing/peer-review OR to the honest-error-only OR in the same strata, with a journal-clustered percentile
  interval (resamples in which both ORs are defined and positive). Reading, fixed now: an exposure is called specific to
  referencing/peer-review retractions only if, in the same strata, that class's interval excludes 1 and the ratio's
  interval excludes 1. If the honest-error estimate falls toward 1 (point estimate at most 1.2) while the ratio's interval
  includes 1, the text will say that a modest residual association remains that may be specific but is not shown to be.
  Screening value is reported separately in every case: the share of flagged authors with a later retraction (all, and
  referencing/peer review), against the base rate.
- **P12, tie-breaking audit.** (a) A4: check that deciles 1-3 contain only authors with S1 = 0; mean and median `aid`
  (the rank of the ORCID iD) in deciles 1-3; the chi-square statistic of their three positive counts and its distribution
  over 1,000 alternative seeds of the tie-break key (share at or above the frozen seed's value); the pooled rate of all
  authors with S1 = 0 (Wilson interval). (b) A5: for every ranking and k = 100, 1,000, 10,000, the number of authors tied
  with the k-th author, and lift at k over 200 alternative tie-break seeds (minimum, median, maximum). (c) P1 and P6
  recomputed with citation and productivity deciles whose ties are broken by a seeded uniform key instead of row order:
  all exposures for all later retractions, and the P11 exposures by class.
- **P13 (descriptive, laptop).** Share of author positions with an ORCID iD, and of publications with at least one ORCID
  author, among biomedical publications of 2014-2023, from the per-year counts of `f03_authors_20261126_01`.

### Round 3 addendum (written 2026-11-26 after reading `f13_posthoc3_20261126_01`; data-driven)
In P11, the burst rule R3 had honest-error estimates near 1 (P6: 1.01) while its referencing/peer-review estimates stayed
above 1 (P6: 1.45). The ratio test of P11 was pre-stated only for R2, S4 and S5. Added now, and labelled data-driven
wherever used: the same ratio, with the same journal-clustered interval, for R3 (primary, P1, P6 strata and their
random-tie versions). The run is repeated in full as `f13_posthoc3_20261126_02` (same code otherwise; same seeds), so that
every round-3 number comes from one run.

## Round 4 (written 2026-11-26, after an internal critique; before these runs)
The internal critique found that the evaluation code (f06, and f07/f09/f13 after it) defines outcome class 3 as E's
misconduct list **minus** the four referencing/peer-review strings, whereas SPEC §5 defines it as "any paper with a reason
in E's misconduct list", which includes `Compromised Peer Review` and `Rogue Editor`. This is a deviation from the frozen
specification. Classes 1, 2 and 4 are unaffected (class 4 already excludes papers in class 1).
- **P14, class 3 as specified.** Positives in the primary population; overlap with class 1; Mantel-Haenszel ORs (RBG CI)
  and journal-clustered intervals (as f13) for S1, S5 and R2 in the primary strata (the pre-specified A3 estimates), and
  for the P11 exposures in the primary, P1 and P6 strata. Check that classes 1, 2 and 4 and the implemented class 3
  reproduce f06/f13. The paper will report the specified definition as the pre-specified one and the implemented one as a
  disclosed deviation.
- **P15, shared retraction events (descriptive).** For the 2,419 primary positives: the number of distinct
  later-retracted publications linked to them; positive authors per publication (distribution, maximum); the share of
  positives who share a later-retracted publication with another positive primary author.

### Round 4 addendum (written 2026-11-26 after reading `f14_class3_20261126_01`; before this run)
P15 showed that the 2,419 primary positives are linked to 1,910 distinct later-retracted publications and that 1,683 of
them (69.6%) share such a publication with another positive author; journal-clustered intervals may not capture this.
- **P16, intervals clustered by shared retraction events.** Clusters: connected components of primary authors linked
  through shared later-retracted publications (outcome window); authors without a later retraction are singletons.
  Poisson(1) weight per cluster, 1,000 resamples (seed `SeedSequence([20261126, crc32("pubclusters")])`); percentile
  95% intervals for the primary-strata ORs of all exposures, for the class estimates of S1, S5 and R2 (class 3 as
  specified) and for the class ratio of R2, and for lift at 10,000 of every ranking.
