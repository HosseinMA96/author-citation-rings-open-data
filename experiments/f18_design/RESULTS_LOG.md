# f18 design figures: results log

Run `f18_design_20261126_01` (laptop). Reads f03, f05, f06 and the run records of the post hoc VM runs (f17 through its
redacted record). Outputs `fig_flow.pdf` and `fig_timeline.pdf` (copied to `paper/figures/`).

- Flow: 877,590 ORCID iDs with at least five biomedical publications in W → 859,157 with a publication in 2019–2023
  (18,433 without) → 800,996 eligible (58,161 with fewer than 20 non-self, non-co-author citing works) → 793,299 in the
  primary population (7,697 with a retraction by 31 January 2024) → 2,419 with a later retraction (0.305%).
- Timeline (UTC): specification frozen 18:43:04 (true UTC, f04 log); score run 18:43:21; evaluation run 18:54:42 (VM
  clock); first post hoc run 19:00:51; first push to the public repository 21:24:18 (GitHub server time, repository
  activity API); last post hoc run 05:49:17 on 27 November (f17). The analysis panel is drawn in order, not to scale.
- A test copy of the script (outside the project tree, without f17) was used to check the layout; it wrote no record.

## f18_design_20261126_02: cited
As `_01` (superseded) with the evaluation run labelled "first to link scores to outcome labels" instead of "first to
read the outcome labels": f03 had counted labels per author before the specification (sixth external review).
