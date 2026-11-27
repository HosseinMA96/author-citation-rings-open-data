# F12 supplementary tables: lab notebook

Laptop; reads run records only (`f06_eval_20261126_02`, `f07_posthoc_20261126_01`, `f09_posthoc2_20261126_02`) and the
reason counts of Paper D run `d02_rw_20261101_01`; writes `../../paper/content/supp_tables.tex` (generated; do not edit).
Added after the review of draft v0.1, which noted that pre-specified outputs (decile rates with Wilson
intervals, recall at 10,000, average precision) and the reason-to-class mapping were not shown.

## f12_tables_20261126_01: superseded
Tables S2 (screening) and S4 (all odds ratios) were too wide for the page (overfull by 93 pt and 305 pt).

## f12_tables_20261126_02: superseded
S2 and the odds-ratio tables set in landscape; the odds ratios split into two tables. Captions repeated the number
("Table 3: Supplementary Table S2") and every table was forced to its own page.

## f12_tables_20261126_03: superseded, not released
Captions without the prefix (the appendix numbers tables S1–S6), portrait tables placed `[htbp]`. The config recorded a
local absolute path for the Paper D input.

## f12_tables_20261126_04: superseded
Same tables as `_03` (file identical); the Paper D input is recorded relative to the series root. Six tables: S1 later
retraction by S1 decile with Wilson intervals (A4); S2 screening metrics for every ranking, with precision and lift at
100/1,000/10,000, recall at 10,000, average precision (A5) and the journal-clustered lift interval (P4); S3 screening for
the referencing/peer-review class (P7, post hoc); S4 odds ratios, pre-specified I (primary and robustness (a)–(c)); S5
odds ratios, pre-specified II ((d)–(f)) with post hoc columns (journal-clustered interval, P1, P6); S6 Retraction Watch
reason strings by outcome class with paper counts. Reason strings per class: referencing or peer-review 4, paper mill 1,
other misconduct 20, honest error 14, no class 71. Values are identical in all four runs (layout only).

## f12_tables_20261126_05: superseded
Completeness check against SPEC §6 found two pre-specified outputs shown only in part: the A5 intervals (only precision at
1,000 and lift at 10,000 had intervals) and A3 (odds ratios by outcome class, shown only graphically in Fig. 1). Table S2
now gives lift with its interval at 100, 1,000 and 10,000 and intervals for recall and AP; new Table S7 lists every A3
estimate with the number of exposed positives and the journal-clustered interval (P4). Existing cells unchanged. S7 was
too wide (95 pt).

## f12_tables_20261126_06: superseded
As `_05`, with two-line column heads and a smaller font in S7 (layout only; same values). Tables S1–S7.

## f12_tables_20261126_07: superseded
After the second review: new input `f13_posthoc3_20261126_02`; Table S8 (outcome classes in the primary, P1
and P6 strata, journal-clustered intervals, class ratio) and Table S9 (tie-breaking audit); tie notes in the captions of
S1 and S2; "A3" removed from the S7 caption. Panel (c) of S9 showed "--" for the row-order P1/P6 estimates of four
exposures.

## f12_tables_20261126_08: superseded
Panel (c) takes the row-order P1/P6 estimates from f07/f09 (which f13 reproduces exactly). Panel (c) was 4 pt too wide.

## f12_tables_20261126_09: superseded
As `_08` with narrower column spacing in S9 (layout only; same values). Tables S1–S9.

## f12_tables_20261126_10: superseded
After the AI review by the coding assistant (Copilot CLI's rubber-duck agent): outcome class 3 as specified (f14) in Tables S6 (the two shared reasons listed in class 3
as well, marked), S7 (with the first-coded values in a note) and S8; new Table S10, intervals clustered by shared
retraction events (f15). Inputs: f06, f07, f09, f13, f14, f15 and Paper D's reason counts.

## f12_tables_20261126_11 and _12: superseded
After the fourth review: P1/P6 columns of S5 and all of S8 from the random-tie strata (f13, f16); S8 has the
class ratio for every exposure and explains "--"; S9(c) puts the random-tie values first; run labels removed from the
captions (`_12` adds a pointer to the definition of P1/P6 in S9).

## f12_tables_20261126_13: superseded by `_14`
As `_12` with shorter column heads in S9(c) (layout only). Inputs: f06, f07, f09, f13, f14, f15, f16, Paper D's reason
counts.

## f12_tables_20261126_14: superseded by `_17`
As `_13`, plus (a) Table S7: the post hoc positive control (prior retraction, f09 P5) by outcome class, with
journal-clustered intervals (class 3 as first coded, marked); (b) new Table S11: estimates with later retractions
attributed through Crossref ORCID iDs as well (P19), from the redacted f17 record `f17_redact_20261126_01`. Inputs: f06,
f07, f09, f13, f14, f15, f16, f17 (redacted), Paper D's reason counts.

## f12_tables_20261126_15, _16: superseded by `_17`
`_15` adds Table S12 (informative strata and the positives they hold, for every pre-specified estimate; f06) and Table
S13 (profiles of the flagged groups and the work-normalised pact rule; f07 P2–P3). `_16` shortens the exposure labels of
S12 and `_17` narrows its column spacing (layout only; values identical).

## f12_tables_20261126_17: superseded by `_18`
Tables S1–S13. Inputs as `_14` (f06, f07, f09, f13, f14, f15, f16, f17 redacted, Paper D's reason counts).

## f12_tables_20261126_18: cited
As `_17`, but Table S12(b) shows outcome class 3 as specified (1,545 positives; informative strata and their positives
from `f19_informative_20261126_01`), as Tables S7 and S8 do, with the first-coded counts in its note. Inputs: f06, f07,
f09, f13, f14, f15, f16, f17 (redacted), f19, Paper D's reason counts.
