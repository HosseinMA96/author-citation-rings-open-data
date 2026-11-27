# Reproducing Paper F

Every number in the paper comes from a run listed below; `FINDINGS.md` maps each claim to its run. Each run folder
(`experiments/<exp>/runs/<run_id>/`) holds `run.json` (parameters, SHA-256 of the script and of `common.py`, input paths,
counts, run time), `stdout.log`, small aggregate outputs and `SHA256SUMS`. Scripts refuse to write into an existing run
folder, so a rerun always gets a new run ID. No per-author table leaves the analysis machine. One run record
(`f17_attribution_20261126_01`) is kept in full only on the VM because it profiled a single author; its redacted copy
is released (`f17_redact_20261126_01`).

## 1. Machine and environment
- Steps that read the citation graph need about 64 GB of RAM and 100 GB of free disk. They were run on one Azure
  `Standard_E8s_v6` VM (8 vCPU, 64 GB, Ubuntu 24.04); total compute for all runs: 2.47 logged VM-hours in seven sessions (`vm/sessions.log`).
- Python environment: `vm/environment_f.lock.yml` (micromamba/conda-forge; Python 3.11.18, DuckDB 1.5.6, pandas 3.1.0,
  NumPy 2.4.6, pyarrow 25.0.0, SciPy 1.17.1). Create it with `micromamba create -n d -f vm/environment_f.lock.yml`.
- Figures run on a laptop from the run records (Matplotlib 3.11.1).
- VM control: `vm/vmctl.sh` (`restore` builds the VM from a disk snapshot in its own resource group; `start`, `stop` =
  deallocate, `ssh`, `push` copies the code to `~/f`, `fetch RUN` copies a run back and checks its checksums).
- `experiments/<exp>/common.py` is the same file in every folder (identical SHA-256, recorded in every run.json).
  Paths: `C_WORK` (graph tables), `D_WORK` (Paper D's tables), `META_DIR` (Meta CSV dump), `F_DATA` (F's work tables).

## 2. Inputs
| Input | Source | Check |
|---|---|---|
| Citation graph, January 2024 | Illinois Data Bank, doi:10.13012/B2IDB-5216575_V1 | sizes and SHA-256 in the companion repository of Paper C (`citation-stacking-open-data`, `c01_journal_graph/RESULTS_LOG.md`) |
| Graph tables (`edges.parquet`, `pubs_slim.parquet`, `pubs_j.parquet`) | `c6_full_run.py` run `c6_full_20261031_02` (Paper C) | that run's run.json |
| OpenCitations Meta CSV dump v7 | figshare doi:10.6084/m9.figshare.21747461.v7, `meta_csv_dump.zip`, extracted to `~/c/data/raw/meta_csv/` (28,255 files) | zip SHA-256 `924ac7acc838024bdc78982970c7b1a4bcd4da5f8ad62c47a94d9580df10ca44` |
| Retraction Watch | `git clone https://gitlab.com/crossref/retraction-watch-data`, commit `a98cc7e2dd37b8affab780096048b261833ecc11` (2026-10-30) | `retraction_watch.csv` SHA-256 `7a729a87837985954a34326202cb98c4bff4b2b142fda8695febb613cf45a7f4` |
| Retraction Watch paper table and graph matching; PubMed 2026 baseline parse; ID map | Paper D runs `d02_rw_20261101_01`, `d05_match_20261101_02`, `d04_pubmed_20261101_01`, `d00_idmap_20261101_01` (companion repository `retracted-neighbours-open-data`, `REPRODUCE.md`) | those runs' run.json |

## 3. Runs, in order (the runs cited in the paper)
Run each from its experiment folder: `python <script> <run_id> [args]`.

| Step | Command | Time |
|---|---|---|
| Author identities, coverage, label counts | `f03_authors/f03_authors.py f03_authors_20261126_01` | 12 min |
| Score unit test | `f05_scores/test_scores.py 20` (20 toy graphs vs brute force) | 1 min |
| Design specification | `SPEC.md` v1, SHA-256 `07200ecb9affa9f2bee88b68becba9ad81900d2cfcc1fc759ba814ced61ca3ec`, frozen before the score run (`experiments/f04_spec/`) | – |
| Frozen scores | `f05_scores/f05_scores.py f05_scores_20261126_01 f03_authors_20261126_01` | 8 min |
| Evaluation (first run to link scores to the labels; checks both hashes first) | `f06_eval/f06_eval.py f06_eval_20261126_02 f05_scores_20261126_01 1000` | 1 min |
| Post hoc round 1 (`POSTHOC.md`) | `f07_posthoc/f07_posthoc.py f07_posthoc_20261126_01 f05_scores_20261126_01` | 8 s |
| Figures (laptop) | `f08_figures/f08_figures.py f08_fig_20261126_07 f03_authors_20261126_01 f06_eval_20261126_02 f07_posthoc_20261126_01 f14_class3_20261126_01 f13_posthoc3_20261126_02` | 3 s |
| Post hoc round 2 (`POSTHOC.md`): clustered intervals, finer strata, positive control, refpeer screening, top pact counts | `f09_posthoc2/f09_posthoc2.py f09_posthoc2_20261126_02 f05_scores_20261126_01 1000` | 4 min |
| Post hoc P9, names (VM only; aggregates written) | `f10_names/f10_names.py f10_names_20261126_01 f05_scores_20261126_01` | 5 min |
| Post hoc P10, coverage by publisher and DOI sample (VM) | `f11_coverage/f11_coverage.py f11_cov_20261126_01` | 7 min |
| Post hoc P10, Crossref comparison (laptop; Crossref REST API, retrieved 26 Nov 2026) | `CROSSREF_MAILTO=<your address> f11_coverage/f11_crossref.py f11_crossref_20261126_02 f11_cov_20261126_01` (the address is optional; it selects Crossref's polite pool and is not recorded) | 3 min |
| Post hoc round 3 (`POSTHOC.md`): classes under the adjusted strata, class ratios, tie-breaking audit (VM) | `bash vm/run_round3.sh f13_posthoc3_20261126_02` (runs `f13_posthoc3/f13_posthoc3.py f13_posthoc3_20261126_02 f05_scores_20261126_01 1000`) | 1 min |
| ORCID share of biomedical author positions 2014–2023 (laptop) | `f13_posthoc3/f13_desc.py f13_desc_20261126_01 f03_authors_20261126_01` | 1 s |
| Post hoc round 4: outcome class 3 as specified, shared retraction events (VM) | `bash vm/run_round4.sh f14_class3_20261126_01` (runs `f14_class3/f14_class3.py f14_class3_20261126_01 f05_scores_20261126_01 1000`) | 1 min |
| Post hoc round 4 addendum: intervals clustered by shared retraction events (VM) | `bash vm/run_round4b.sh f15_pubclusters_20261126_01` (runs `f15_pubclusters/f15_pubclusters.py f15_pubclusters_20261126_01 f05_scores_20261126_01 1000`) | 7 min |
| Post hoc round 5: main adjusted values with random decile ties, all class ratios (VM) | `bash vm/run_round5.sh f16_randties_20261126_01` (runs `f16_randties/f16_randties.py f16_randties_20261126_01 f05_scores_20261126_01 1000`) | 1 min |
| Post hoc round 6 (`POSTHOC.md`): the Frontiers network retractions (P18), attribution through Crossref ORCID iDs (P19) (VM; Crossref REST API, queried 27 Nov 2026) | `CROSSREF_MAILTO=<your address> bash vm/run_round6.sh f17_attribution_20261126_01` (runs `f17_attribution/f17_attribution.py f17_attribution_20261126_01 f05_scores_20261126_01 1000`; the address is optional and selects Crossref's polite pool) | 48 min |
| Disclosure control of the f17 record (laptop; POSTHOC.md round 6 addendum) | `f17_attribution/f17_redact.py f17_redact_20261126_01 f17_attribution_20261126_01`, then the two original files are deleted from the laptop copy (`runs/f17_attribution_20261126_01/REDACTED.md`) | 1 s |
| Design figures: population flow and timeline (laptop) | `f18_design/f18_design.py f18_design_20261126_02 f03_authors_20261126_01 f05_scores_20261126_01 f06_eval_20261126_02` | 1 s |
| Supplementary tables (laptop) | `f12_tables/f12_tables.py f12_tables_20261126_17 f06_eval_20261126_02 f07_posthoc_20261126_01 f09_posthoc2_20261126_02 f13_posthoc3_20261126_02 f14_class3_20261126_01 f15_pubclusters_20261126_01 f16_randties_20261126_01 f17_redact_20261126_01` | 1 s |
| Paper | `cd paper && python build_refs.py && tectonic -X compile main.tex`; number trace: `python trace_numbers.py` | – |

## 4. Determinism
- The author identifier `aid` is the row number of the sorted list of distinct ORCID iDs; score tables are written sorted by
  `aid`. Thresholds use the `inverted_cdf` quantile. Ties in rankings and bootstrap weights use NumPy generators seeded
  from 20261126; decile ties in A4 are broken by a seeded random key.
- Floating-point sums in parallel DuckDB aggregations can differ in the last digits between runs.

## Clocks and time stamps
Run records written on the VM (f03, f05, f06, f07, f09, f10, f11_cov, f13 `posthoc3`, f14, f15, f16, f17) use its
system clock, which is synchronised to UTC. Records written on the laptop (f08, f11_crossref, f12, f13_desc, f18), `vm/sessions.log` and the
git commits of 26 November 2026 use the laptop clock, which ran one hour behind UTC that day (checked against HTTP `Date`
headers: the laptop read 22:40:45Z when two servers reported 23:40:41 and 23:40:34 GMT). The freeze time of the
specification in `experiments/f04_spec/RESULTS_LOG.md` is given in true UTC (18:43:04Z; the laptop wrote 17:43:04Z), and
the order of the score and evaluation runs rests on the VM clock alone (18:43:21Z and 18:54:42Z). The first commit of the
public repository, stamped 20:24 UTC, was therefore made at about 21:24 UTC, after the VM runs of 21:08–21:11 UTC that it
contains. GitHub's own record agrees: its repository activity API (`gh api repos/HosseinMA96/author-citation-rings-open-data/activity`)
lists the first push (branch creation with commit `f010080`) at 21:24:18Z, server time. The empty repository had been
created at 19:52:50Z (`created_at`). The paper's timeline figure (run `f18_design`) uses the push time.

## 5. Runs not cited (kept for the record)
| Run | Why |
|---|---|
| `f03_test_20261126_01` | Failed: CSV sniffer missed RFC 4180 doubled quotes on a 100-file subset (empty folder on the VM) |
| `f03_test_20261126_02` | Test mode (100 Meta files), SQL check |
| `f05_test_20261126_01` | 1% of authors, under a pre-freeze SPEC draft; no labels |
| `f06_eval_20261126_01` | Failed at the stratum keys (pandas nullable column); only population counts had been logged |
| `f08_fig_20261126_01`–`_05` | Layout iterations (same values), `_04` with outcome class 3 as first coded, `_05` with row-order ties in the post hoc squares; the paper uses `_07` |
| `f11_crossref_20261126_01` | Same results as `_02` (byte-identical); the script then held a contact address, now read from the environment |
| `f09_posthoc2_20261126_01` | Failed before any estimate: pandas 3 kept missing journal ids as NaN, so sorting journal keys failed |
| `f12_tables_20261126_01`–`_05` | Layout iterations, a local absolute path in the config of `_01`–`_03` (those three are not in the public repository), and the completeness fix of `_05` (Table S7 and the full A5 intervals added; existing values unchanged), `_06`–`_08` (Tables S8–S9 and tie notes added after the second review; layout) `_09` (class 3 as first coded), `_10` (row-order adjusted strata) and `_11`–`_12` (captions and layout); the paper uses `_14` |
| `f13_posthoc3_20261126_01` | Identical to `_02` except that `_02` adds the burst-rule class ratio (data-driven addendum in `POSTHOC.md`) |
| `f12_tables_20261126_13` | As `_14` without the positive-control row of Table S7 and without Table S11 |
| `f12_tables_20261126_14`–`_16` | `_14` without Tables S12–S13; `_15`–`_16` layout iterations of S12 (column widths, short labels); the paper uses `_17` |
| `f08_fig_20261126_06` | As `_07` except that the hybrid ranking (S1 + journal risk) had the colour of the citation signals in Fig. 5 |
| `f18_design_20261126_01` | As `_02` except the timeline label "first to read the outcome labels" (f03 had already counted labels per author) |

## 6. Large intermediate data
Per-author tables (`orcid_slots.parquet`, `paper_auth.parquet`, `aid_map.parquet`, `bio.parquet`, frozen
`scores.parquet`) stay on the VM disk (`~/f/data/work/`) and are archived with the disk snapshot when the project ends.
They are never published: they identify individual researchers.
