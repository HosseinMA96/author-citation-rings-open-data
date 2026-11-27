# f17 attribution: results log (POSTHOC.md round 6, P18–P19; post hoc)

Run `f17_attribution_20261126_01` (VM, started 2026-11-27T05:49:17Z, 2,858 s; Crossref queried 2026-11-27 in the polite
pool, 8 threads, about 47 min). The original `run.json` and `stdout.log` stay on the VM: P18 profiled a single author
(POSTHOC.md round 6 addendum). The redacted record, with every count and estimate below, is
`runs/f17_redact_20261126_01/record.json` (redaction run on the laptop; SHA-256 of the originals in its `run.json`).
Setup checks: frozen spec and scores verified; primary population 793,299 with 2,419 positives, as in f06.

## Crossref
8,705 distinct DOIs (all later-retracted graph publications with a DOI, plus the Frontiers set): 8,689 found, 16 not
found, no errors.

## P18: the Frontiers network (2025)
- Selection: 124 Retraction Watch records (publisher Frontiers, first notice 1 July to 30 September 2025, a peer-review,
  referencing or conflict-of-interest reason); every record matched to the graph; 124 distinct graph publications.
- ORCID iDs: 4 of the 124 list an ORCID iD in OpenCitations Meta; none in Crossref (median 5 authors per paper in
  Crossref).
- Primary authors attached: 1 through Meta (already a positive); 0 more through Crossref. Its profile is not reported
  (fewer than 10 authors).
- Reading: open ORCID metadata cannot attach this network's retractions; the design cannot see it.

## P19: later retractions attributed through Crossref ORCID iDs as well
- Coverage: 8,769 later-retracted graph publications (8,748 with a DOI); 3,989 list an ORCID iD in Meta, 2,880 in
  Crossref, 4,112 in either. Crossref gives 5,266 links to authors in the ORCID map, of which 117 are not in Meta and
  29 go to primary authors.
- Outcome: 2,419 → 2,438 positives (19 added, none lost). By class: referencing or peer review 622 → 625, paper mill
  141 → 141, other misconduct (as specified) 1,545 → 1,557, honest error only 248 → 249.
- Estimates (Meta → Meta and Crossref; Supplementary Table S11): S1 0.85 → 0.84 (0.50–1.41); S2 0.99 → 1.03;
  S4 1.45 → 1.51 (0.96–2.38); S5 1.32 → 1.31; S6 1.50 → 1.56 (1.00–2.44, lower bound 1.0040: now just excludes one);
  S7 1.27 → 1.26; R2 1.52 → 1.51 (1.31–1.74); R3 1.40 → 1.41; R ≥ 3 1.53 → 1.52. R2 by class: referencing or peer
  review 2.79 → 2.75, honest error 1.86 → 1.89, ratio 1.50 (0.77–2.70) → 1.45 (0.75–2.65, journal-clustered).
  P1: S1 1.01 → 0.99, S4 1.71 → 1.78 (1.10–2.86), S5 1.59 → 1.57, R2 1.16 → 1.15, R3 1.40 → 1.42.
  P6: S1 0.86 → 0.85, S4 1.44 → 1.55 (0.85–2.83), S5 1.40 → 1.40, R2 1.26 → 1.26, R3 1.18 → 1.19.
  S1 lift among the top 10,000: 0.69 → 0.72.
- Derived (stated in the text): the largest change of any odds ratio is +0.117 (S4 in P6; f16 1.437 → 1.554), so "no odds
  ratio moves by more than 0.12"; in the primary strata the largest is +0.067 (S6). Exposed positives of R3 rise from
  1,196 to 1,210, so 14 of the 19 added authors are flagged by the burst rule (expected about 7 at its 36.8% share);
  S4 and S6 gain one each, R2 two, S1 and S5 none.
- Reading: Crossref adds little beyond Meta; the pre-specified conclusions are unchanged. Missed attributions fall
  more often on burst-flagged authors, so missed retractions can bias toward no association, but the 19 that Crossref
  recovers move nothing materially. Retractions without any iD (in either source) remain unknown.
