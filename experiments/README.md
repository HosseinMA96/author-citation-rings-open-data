# Project F experiments: index and where every record lives

| Folder | Step | Runs cited in the paper | Notebook |
|---|---|---|---|
| `f03_authors/` | ORCID identities from OpenCitations Meta; coverage; identity checks; label counts | `f03_authors_20261126_01` | `RESULTS_LOG.md` |
| `f04_spec/` | Freezing record of `../SPEC.md` (hash) | – | `RESULTS_LOG.md` |
| `f05_scores/` | Score library, unit test against brute force, frozen scores | `f05_scores_20261126_01` | `RESULTS_LOG.md` |
| `f06_eval/` | Pre-specified evaluation (first contact with post-T0 labels) | `f06_eval_20261126_02` | `RESULTS_LOG.md` |
| `f07_posthoc/` | **Post hoc** round 1 (`../POSTHOC.md`): citation-volume strata, profiles, size-free pact rate | `f07_posthoc_20261126_01` | `RESULTS_LOG.md` |
| `f08_figures/` | Paper figures from run records | `f08_fig_20261126_05` | `RESULTS_LOG.md` |
| `f09_posthoc2/` | **Post hoc** round 2 (`../POSTHOC.md`): journal-clustered intervals, finer strata, positive control, screening for the referencing/peer-review class, top pact-count authors | `f09_posthoc2_20261126_02` | `RESULTS_LOG.md` |
| `f10_names/` | **Post hoc** P9: what S1 counts as outside citation (name matching on a 1-in-400 sample; names on the VM only) | `f10_names_20261126_01` | `RESULTS_LOG.md` |
| `f11_coverage/` | **Post hoc** P10: the 2021–2022 ORCID dip (Meta by publisher on the VM; Crossref comparison on the laptop) | `f11_cov_20261126_01`, `f11_crossref_20261126_02` | `RESULTS_LOG.md` |
| `f13_posthoc3/` | **Post hoc** round 3: outcome classes under the adjusted strata with class ratios, flag precision, tie-breaking audit; ORCID share of biomedical author positions in W (laptop) | `f13_posthoc3_20261126_02`, `f13_desc_20261126_01` | `RESULTS_LOG.md` |
| `f14_class3/` | **Post hoc** round 4: outcome class 3 as specified (a deviation in the evaluation code), shared retraction events | `f14_class3_20261126_01` | `RESULTS_LOG.md` |
| `f15_pubclusters/` | **Post hoc** round 4 addendum: intervals from resampling clusters of authors linked by shared later-retracted publications | `f15_pubclusters_20261126_01` | `RESULTS_LOG.md` |
| `f12_tables/` | Supplementary tables S1–S10 from run records (laptop) | `f12_tables_20261126_10` | `RESULTS_LOG.md` |

Runs not cited (failed, test or superseded) are listed with the reason in `../REPRODUCE.md` §5; superseded figure and table runs
carry a `SUPERSEDED.txt`.

| Record | Where |
|---|---|
| Lab notebook | `<exp>/RESULTS_LOG.md` |
| Per-run config, script and `common.py` hashes, counts | `<exp>/runs/<run_id>/run.json` |
| Per-run checksums | `<exp>/runs/<run_id>/SHA256SUMS` |
| Run stdout | `<exp>/runs/<run_id>/stdout.log` |
| Per-author tables (identities, frozen scores) | VM disk `~/f/data/work/` only; never published |
| Raw inputs | VM `~/c/data/raw/` (Meta dump), `~/c/data/work/` (graph tables), `~/d/data/` (Paper D tables, Retraction Watch, PubMed) |
| VM billing events | `../vm/sessions.log` (laptop clock, 1 h behind UTC) |

`common.py` is identical in every folder (same SHA-256). Scripts refuse to overwrite an existing run folder.
