# F4 specification: lab notebook

## SPEC v1 frozen 2026-11-26T18:43:04Z (true UTC; the laptop clock reads 1 h behind UTC: it wrote 17:43:04Z)
- File: `../../SPEC.md` (copy: `SPEC_v1_frozen.md`), SHA-256 **07200ecb9affa9f2bee88b68becba9ad81900d2cfcc1fc759ba814ced61ca3ec**.
- Frozen **before** the full score run (`f05_scores_20261126_01`, started 18:43:21Z by the VM clock, which is correct) and before any post-T0 label was joined to any score.
- Seen before freezing: literature (`lit/LIT.md`); F3 identity checks, coverage and label counts (`f03_authors_20261126_01`);
  the score unit test (`f05_scores/test_scores.py`, 20 toy graphs, all values equal to brute force); a 1% test run of the
  score code (`f05_test_20261126_01`: row counts and score quantiles; no label joined).
- Every score and evaluation run stores this hash (`spec_sha256` in run.json); the evaluation script refuses to run if
  SPEC.md no longer has this hash.
- Amendments: none.

## Versions before the freeze (added 2026-11-27)
The 1% test run `f05_test_20261126_01` (no labels; started 18:40:49Z) recorded the SHA-256 of an earlier draft
(5518ab49…). Every state of `SPEC.md` before the freeze is now kept here. They were rebuilt from the coding
assistant's session log, which records the text of each change. Each rebuild is checked by its hash: draft 2 matches
the hash in the test run's record, and applying the last two changes reproduces the frozen file. Times are true UTC
(the laptop wrote them one hour earlier):

| File | SHA-256 | Written | Change from the previous version |
|---|---|---|---|
| `SPEC_draft1_0151fc.md` | 0151fc27… | 18:34:28 | First version |
| `SPEC_draft2_5518ab.md` | 5518ab49… | 18:39:24 | §3 eligibility: at least 20 non-self, **non-co-author** citing works (was: non-self citing works), so that every share-based score has a denominator of at least 20 works; the score code was changed with it. Set **before** any score was computed on the graph; used by the 1% test run (18:40:49) |
| `SPEC_draft3_9411b6.md` | 9411b6d0… | 18:42:34 | Preamble: what had been seen now lists the unit test and the 1% test run (no label joined); it also said that the test run had motivated the eligibility rule, which was wrong |
| `SPEC_v1_frozen.md` (= `../../SPEC.md`) | 07200ecb… | 18:42:47 (frozen 18:43:04) | Preamble corrected: the eligibility rule was set before the test run. §6 A5: the burst statistic S8 and citations received added to the screening rankings, and productivity defined |

No version was linked to any outcome; the score run (18:43:21) and the evaluation run (18:54:42) used the frozen file.
