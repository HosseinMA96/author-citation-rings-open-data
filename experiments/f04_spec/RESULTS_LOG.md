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
