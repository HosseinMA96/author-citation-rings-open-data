# F5 frozen scores: lab notebook

Score definitions: `../../SPEC.md` §4 (v1, SHA-256 07200ecb…). Library `score_lib.py`; driver `f05_scores.py`; unit test
`test_scores.py`. Per-author scores stay on the VM (`~/f/data/work/f05/<run>/scores.parquet`); the run folder holds counts
and quantiles only.

## Unit test (2026-11-26)
`test_scores.py`: random toy graphs (260 nodes, 40 ORCID authors, ~2,200 random links, a planted 4-author ring with 5 papers
each), every column of `score_lib.build` compared with a brute-force implementation of the definitions. First version had
no pact node in seed 0 (assertion), so the planted ring was added; seed 7 then failed only because the comparison helper
did not treat pandas `<NA>` as missing (fixed in the test, not the library). Final: **20 toy graphs, 19,675 values, all
equal**; rerun after each library change (eligibility on |CW_nc|; `aid_mod` sampling switch).

## f05_test_20261126_01 (78 s; TEST = authors with aid % 100 = 0; computed under a pre-freeze SPEC draft; not cited)
Rows: lin 5,437,957; cwf 4,403,948; rw 2,845,745; win 6,380,863. Pre-eligible 8,592; eligible 7,995; primary 7,917.
Quantiles only, no label joined. Peak memory 5.9 GB. Used to check run time and score ranges before freezing SPEC v1.

## f05_scores_20261126_01 (473 s; frozen)
SPEC v1 hash checked into run.json; Retraction Watch status cut at T0 when loaded (44,400 retracted nodes with a first
notice ≤ 2024-01-31; max notice date 2024-01-31). Peak memory 44.2 GB (DuckDB on-disk scratch, deleted).
- Rows: links into eligible-candidate papers (lin) 544,694,936; distinct (author, citing work) 441,332,887; distinct (author, cited work) 283,714,281; (author, citing author) pairs 639,260,086.
- **Pre-eligible authors 859,157** (≥ 5 biomedical papers in 2014–2023, a paper in 2019–2023); **eligible 800,996**
  (|CW_nc| ≥ 20); eligible with a prior retraction 7,697; **primary 793,299**; by band 5–9: 362,727; 10–19: 250,354;
  20–49: 143,642; ≥ 50: 36,576; 8,486 distinct main journals; 5 without a main journal.
- Score quantiles in the primary population (p50 / p90 / p99): S1 0.0081 / 0.0434 / 0.1111; S2 0.0144 / 0.0611 / 0.1429;
  rule hits R1 12, R2 58,933 (7.4%), R3 291,668 (36.8%), R ≥ 3 58,943, R ≥ 6 2 (others in run.json).
- **Frozen:** `scores.parquet`, 859,157 rows, SHA-256 **5b7036b4eb000063ce4a7d51d71fd37c91394a29ebd7f326237c9fd11a651c21**.

VM housekeeping (2026-11-26, during this run): deleted on F's disk copy only (the snapshot keeps them) two inputs F never
reads, to make room for the scratch database: `~/c/data/work/c6_full_20261031_01/` (superseded C run, 12 GB) and
`~/c/data/raw/meta_csv_dump.zip` (11 GB; the extracted CSVs remain; zip SHA-256 924ac7ac… is in D's REPRODUCE.md).
