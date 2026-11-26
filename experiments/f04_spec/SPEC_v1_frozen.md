# Project F specification (pre-specified design, v1, 2026-11-26)

Written **before any author score is computed and before any score is joined with post-snapshot retractions**. What had
been seen when it was frozen: the literature (`lit/LIT.md`); ORCID coverage, identity checks, population sizes and label
**counts** (run `f03_authors_20261126_01`: 877,590 ORCID authors with ≥ 5 biomedical papers in W, of whom 2,519 have a
first retraction after T0 and none before; no score existed); the score code's unit test against brute force on toy
graphs (`f05_scores/test_scores.py`); and a 1% test run of the score code (`f05_test_20261126_01`: run time, row counts
and score quantiles, **no label joined**). The |CW_nc| ≥ 20 rule in §3 was set before that run, after noting that
eligibility on |CW| alone would let S1 rest on one or two works. Its SHA-256 is recorded in `experiments/f04_spec/RESULTS_LOG.md` when frozen
and stored in the `run.json` of every score and evaluation run. Any later change is an **amendment** (§9: dated, with its
reason; affected analyses are labelled post hoc). This is a pre-specified design in a private repository, not a public
pre-registration; never call it "pre-registered".

## 1. Question
Do author-level citation-ring signals, measured on the open citation graph as it stood in January 2024, predict which
authors will have a paper retracted afterwards, beyond the journals they publish in and how much they publish? Are
they useful as a screen? The signals are adaptations of published indicators (Evdaimon et al. 2024; Li et al. 2019)
and of a deployed rule set (PeerTrust, Ali et al. 2026); none has been tested prospectively (`lit/LIT.md`).
- **RQ1 (primary):** is the top 1% of non-co-author reciprocity (S1) associated with later retraction within strata of
  main journal × productivity?
- **RQ2:** the same for the other signals and for the PeerTrust-style rules (§4).
- **RQ3:** by retraction reason: referencing/peer-review manipulation and paper mills (where a ring signal should
  work) against honest error only (negative control, where it should not).
- **RQ4:** screening value: precision and lift among the top-ranked authors, against a journal-risk baseline.

## 2. Data (all on the F VM; no new downloads)
- Graph: OpenCitations January 2024 (Illinois Data Bank doi:10.13012/B2IDB-5216575_V1), C's `edges.parquet`
  (citing_iid → cited_iid, 1,962,840,983 rows), `pubs_slim.parquet` (pub_year), `pubs_j.parquet` (journal_id; rule
  `main` of run `c6_full_20261031_02`). Effectively complete to about Sept 2023 (D run `d00_cutoff_20261101_01`).
- Authors: OpenCitations Meta CSV dump v7 (doi:10.6084/m9.figshare.21747461.v7), parsed by `f03_authors_20261126_01`:
  `orcid_slots.parquet` (iid, pos, n_auth, aid), `paper_auth.parquet` (iid, n_auth, n_orcid). **Author = ORCID iD**
  (`aid` = row number of the sorted ORCID list; the map stays on the VM). Meta deduplicates people only by ORCID
  (Massari et al. 2024); authors without ORCID cannot be followed and are invisible to every author-level measure.
- Biomedical paper: PMID in Meta, or DOI in the PubMed 2026 baseline (D's rule; `bio.parquet` from f03).
- Retractions: Retraction Watch frozen copy (commit a98cc7e, 2026-10-30), D runs `d02_rw_20261101_01` (paper table with
  reasons) and `d05_match_20261101_02` (paper → graph node). Nature = Retraction; reinstated papers excluded.

## 3. Time and populations
- **Window W = publication years 2014–2023** for every paper used in a score (the author's papers, citing papers, cited
  papers). A *link* is an edge p → q with both p and q in W.
- **T0 = 2024-01-31** (main). Outcome window (T0, 2026-10-30]. Sensitivity T0' = 2023-09-30 (§7).
- An author's papers P(a): graph nodes in W whose Meta record lists a's ORCID (any field). O(p): the ORCID authors of p.
- **Co-authors** CO(a): authors b ≠ a with at least one paper in W listing both a and b.
- **Eligible author:** at least 5 biomedical papers in W; at least one paper in 2019–2023; at least 20 distinct
  non-self, non-co-author citing works (|CW_nc(a)| ≥ 20, §4), so that every share-based score has a denominator of at
  least 20 works (without it the top 1% of S1 would be filled with authors whose S1 rests on one or two works).
- **Prior retraction:** any graph paper listing a's ORCID with a first Retraction Watch notice ≤ T0.
- **Primary population:** eligible authors without a prior retraction.
- **Outcome Y(a):** a graph paper (any year, any field) listing a's ORCID has its first Retraction Watch notice in
  (T0, 2026-10-30].
- **Strata:** main journal (the journal_id of most of a's biomedical papers in W; ties → smallest journal_id) ×
  productivity band (biomedical papers in W: 5–9, 10–19, 20–49, ≥ 50).

## 4. Scores (computed by `f05_scores.py`, which reads no post-T0 label)
Notation: CW(a) = distinct citing works p of a's papers (links into P(a)) with a ∉ O(p) (non-self);
CW_nc(a) = those with O(p) ∩ CO(a) = ∅ (no ORCID co-author of a); RW(a) = distinct works in W cited by a's papers.
- **S1 (primary): non-co-author reciprocity** = |CW_nc ∩ RW| / |CW_nc|: the share of a's non-self, non-co-author citing
  works that a's own papers also cite (work-level citation exchange; after PeerTrust's "reciprocal works" and the
  author reciprocity of Li et al. 2019).
- **S2: reciprocity, all citing works** = |CW ∩ RW| / |CW| (PeerTrust's definition, without the co-author filter).
- **S3: pact nodes** P(a) = number of ORCID authors b ≠ a with at least 3 works in CW ∩ RW ("more than two
  reciprocal works", PeerTrust rule 2). Rule R2: P(a) > 5.
- **S4: concentration** = share of a's non-self links that come from works listing at least one of the 5 ORCID authors
  who send a the most non-self links (ties by aid). After A50%C (Evdaimon et al.), without double counting.
- **S5: self-citation share** = links into P(a) from works listing a / all links into P(a) (reference signal).
- **S6: co-author citation share** = links from works with a ∉ O(p) and O(p) ∩ CO(a) ≠ ∅ / all links into P(a).
  PeerTrust-style rule R1: NCI_adj = 100·S6 / ln(1 + mean number of authors of a's papers) > 35.
- **S7: C/h²** = (all links into P(a)) / h², h = h-index of a's papers counting links in W; undefined if h = 0.
  Low values are the signal (Evdaimon et al.: bottom 1%).
- **S8: publication burst** B = max over t = 2015…2023 of n_t / max(1, n_{t−1}), n_t = a's papers in year t.
  PeerTrust-style rule R3: B > 3.
- **PeerTrust-style raw score** R = 3·R1 + 3·R2 + 2·R3 (0–8). These are adaptations on different data
  (OpenCitations, not OpenAlex) and must never be described as PeerTrust itself.
- **Baselines (pre-T0 information only):** journal risk J(a) = mean over a's biomedical papers in W of the journal's
  shrunken retraction rate at T0, (r_j + m·g)/(n_j + m), n_j = biomedical items of journal j published 2010–2023,
  r_j = those with a first notice ≤ T0, g = Σr/Σn, m = 100 (D's B); productivity (biomedical papers in W); citations
  received (links into P(a)).
- Also stored per author (VM only): |CW|, |CW_nc|, link counts, h, mean team size, first/last year, n per year,
  main journal, band, prior-retraction flag.
- Scores are written sorted by aid and frozen: SHA-256 in `run.json` before the evaluation script runs; the evaluation
  checks the hash first.

## 5. Outcome classes (RQ3)
From the Retraction Watch reasons of the retracted papers counted in Y(a) (exact strings; D run `d02_rw_20261101_01`,
`reason_counts.csv`). An author can be positive in several classes.
1. **refpeer** (referencing or peer-review manipulation): any paper with `Concerns/Issues about Referencing/Attributions`,
   `Compromised Peer Review`, `Concerns/Issues about Peer Review` or `Rogue Editor`.
2. **mill:** any paper with `Paper Mill`.
3. **misconduct (other):** any paper with a reason in E's misconduct list (`../E_disruption/SPEC.md` §4, class 2).
4. **honest error only (negative control):** every retracted paper of the author in the outcome window has at least one
   reason starting with `Error in` / `Error by`, or `Results Not Reproducible`, `Contamination of Cell Lines/Tissues`,
   `Contamination of Materials`, `Doing the Right Thing`, and none in classes 1–3.

## 6. Analyses (primary population unless stated)
- **A1 (primary):** Mantel–Haenszel odds ratio of Y for E1 = (S1 ≥ its 99th percentile in the population), strata §3,
  Robins–Breslow–Greenland 95% CI. Strata without both exposed and unexposed authors, or without a positive, do not
  contribute (counted). **Decision rule (fixed now):** the ring signal "holds within journal and productivity" if the
  95% CI lies above 1; otherwise the paper reports that it does not, at this data's resolution.
- **A2:** the same for: top 1% of S2, S4, S5, S6; bottom 1% of S7; rules R1, R2, R3; R ≥ 3. Report all; no selection.
- **A3:** A1 and A2 (S1, S5, R2) for each outcome class of §5. Expectation stated in advance: a manipulation-specific
  signal gives a larger OR for refpeer/mill than for honest error only.
- **A4: dose:** positive rate (Wilson 95% CI) by S1 decile, with the top 1% separately.
- **A5: screening:** rank authors by S1 (descending; ties by seed 20261126), S2–S6, −S7, S8, R, J, productivity
  (biomedical papers in W), citations received (links into P(a)), and the rank average of S1 and J (no fitted model). Precision@k and lift (precision / base rate) for k = 100, 1,000, 10,000;
  recall@10,000; average precision. 95% CIs by bootstrap over authors (1,000 resamples, seed 20261126). Primary
  comparison: S1 vs J at k = 1,000.
- Counts at every filter step (ORCID authors → eligible → primary; strata informative; exposed; positives by class).

## 7. Pre-specified robustness
(a) All eligible authors, with prior retraction as an extra stratum variable; (b) T0' = 2023-09-30 (prior/outcome split
moves; scores unchanged); (c) authors with |CW_nc| ≥ 100; (d) outcome restricted to retracted papers published in W;
(e) strata = main journal only; (f) top 5% instead of top 1% for A1–A2.

## 8. Reporting rules
- Group-level results only. No author names, ORCIDs or per-author scores in the paper, the repository or any release;
  per-author tables stay on the VM. Retracted papers are public labels but are not listed per author.
- "Anomalous citation pattern" or "signal", never "manipulation" or "misconduct" for an author; retraction ≠ misconduct.
- Every number in the paper traces to a run in `experiments/*/runs/` (`FINDINGS.md`).

## 9. Amendments
(none yet)
