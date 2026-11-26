# F10 post hoc P9 (what S1 counts as "outside"): lab notebook

Plan: `../../POSTHOC.md` round 2. Names (Meta author strings) used on the VM only; aggregates here.

## f10_names_20261126_01 (272 s)
- Sample: primary authors with `hash(aid, 20261126) % 400 = 0`: **2,033 authors**. Their citing works rebuilt with the score
  library's rules: **S1 reproduced exactly for all 2,033** (0 mismatches with the frozen scores).
- Records needing names 915,276 (915,257 with an author string).
- Non-self, non-co-author citing works (author–work pairs): 976,721. Name-matched **hidden self-citation 0.9%**, **hidden
  co-author 19.6%**, either **19.8%**.
- Among the reciprocal ones (16,116 pairs; the numerator of S1): hidden self 9.2%, hidden co-author 38.8%, either **39.5%**.
- S1 without flagged works: Spearman 0.85 with S1; median 0.0070 → 0.0028; mean 0.0159 → 0.0112. Sampled authors at or
  above the population top-1% threshold (0.1111): 21 before, 11 after (all 11 were above before).
- Reading: up to two fifths of the exchange counted as "outside" involves people listed on the author's own papers (or the
  author under a non-ORCID listing); name keys over-match common names, so this is an upper bound. The ranking is largely
  preserved, but about half of the top-1% authors in the sample owe their status to such works.
