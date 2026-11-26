# F3 author identities: lab notebook

Coverage, identity checks and label **counts** only; no score computed, nothing cross-tabulated with outcomes.
Script `f03_authors.py`; scratch database deleted at the end; outputs on the VM in `~/f/data/work/`
(`orcid_slots.parquet` 266 MB, `paper_auth.parquet` 172 MB, `aid_map.parquet` 26 MB (ORCID ↔ aid; never leaves the VM),
`bio.parquet` 33 MB).

## 2026-11-26: VM
`vm-project-f` in its own resource group `rg-project-f`, restored by `vm/vmctl.sh restore` from
`snap-project-d-osdisk-20261109` (D's archive; never modified; Project E's VM and group untouched). Standard_E8s_v6
(8 vCPU, 62 GiB visible), Premium 256 GB disk: 81 GB free after restore. The OS hostname is still `vm-project-c`
(inherited from the disk); the Azure VM name is `vm-project-f`. Inputs present: C's graph tables
(`~/c/data/work/c6_full_20261031_02/`), the Meta CSV dump (`~/c/data/raw/meta_csv/`, 28,255 files, 45 GB), D's tables
(`~/d/data/work/`: idmap, pubmed26, rw/rw_iid/status), raw PubMed and Retraction Watch. Python env `d` (micromamba).
Meta author field format (read on the VM): `Family, Given [omid:ra/… orcid:0000-…]; …`.

## f03_test_20261126_01: FAILED (kept on the VM; empty folder, no run.json)
DuckDB's CSV sniffer, on a 100-file subset, did not detect RFC 4180 doubled quotes (`""`) and stopped at line 623 of
`1003.csv`. Fix: `delim=',', quote='"', escape='"'` set explicitly (the full-dump sniff in D's `d00_idmap` had found it).

## f03_test_20261126_02 (50 s; TEST = Meta files 1000–1099, no edge pass)
SQL checked end to end on 383,060 records. Not cited.

## f03_authors_20261126_01 (723 s)
**Meta records:** 107,067,700 (= D's `d00_idmap` count), 97,269,934 with authors; 352,057,220 author slots,
**52,206,594 with an ORCID (14.8%)**; 26,626,530 records with ≥ 1 ORCID; **5,723,850 distinct ORCIDs**; no `ra` OMID
appears both with and without an ORCID; 8,540,427 slots without an `ra` OMID; 740 records list the same ORCID twice
(one slot kept).

**Identity checks**
- `ra` OMIDs with several ORCIDs: **0**. ORCIDs with several `ra` OMIDs: **1,315,288** (23%; cause not investigated), so the
  author key must be the ORCID itself, not the `ra` OMID.
- People without ORCID (2% sample of `ra` OMIDs by hash, all their records included): 5,827,133 OMIDs, **all in exactly one
  record**. Confirms Massari et al. (2024): without an ORCID an author cannot be followed across papers.
- Records per ORCID: median 2, p75 6, p90 20, p99 115.

**Graph nodes:** 107,030,533; with authors 94,049,595; with ≥ 1 ORCID 26,626,530. Biomedical nodes (D's rule) 31,464,435.

**ORCID coverage of biomedical papers** (share of author slots with ORCID / share of papers with ≥ 1 ORCID author):
2005 13.1%/37.3%; 2010 17.4%/47.5%; 2014 20.1%/54.9%; 2016 20.9%/58.4%; 2018 24.8%/68.5%; 2019 26.3%/71.1%;
2020 26.8%/70.8%; 2021 24.7%/66.2%; 2022 23.1%/60.7%; 2023 24.7%/63.1% (full table in run.json `bio_coverage_by_year`).
All graph nodes 2014–2023: 36,833,518 papers, 169,216,774 slots, 36,279,419 with ORCID (21.4%), 16,465,934 papers with ≥ 1 ORCID (44.7%).

**ORCID authors with biomedical papers 2014–2023:** 3,239,463; with ≥ 3: 1,342,771; **≥ 5: 877,590**; ≥ 10: 446,017; ≥ 20: 185,006;
≥ 50: 38,161; ≥ 100: 8,290. ≥ 5 and a paper in 2019–2023: 851,943. Quantiles of biomedical papers: median 2, p75 5, p90 13, p99 54.

**Labels (counts only; Retraction Watch a98cc7e via D's matching; reinstated excluded)**
- Retracted graph nodes 53,169. Biomedical retracted by T0: 23,741 (12,259 with ≥ 1 ORCID, 51.6%); **after T0: 5,117
  (2,946 with ≥ 1 ORCID, 57.6%)**.
- ORCID authors with ≥ 5 biomedical papers: 877,590; a retraction by T0: 8,105; after T0: 2,983; **after T0 and none by T0:
  2,519**; paper mill after T0: 207; referencing/peer-review class after T0: 806. (≥ 1 paper: 3,239,463 / 21,853 / 5,308 /
  4,732 / 734 / 2,027; ≥ 10: 446,017 / 5,996 / 2,153 / 1,794 / 111 / 508.)

**Citation volume (sizes for F5):** links with both ends published 2014–2023: 394,512,740; cited biomedical 229,511,893;
cited biomedical with ORCID 166,498,809; both ends with ORCID 107,927,361 (1,843,450,863 author pairs if fully expanded,
which F5 avoids).

**Implications for F4:** ORCID is the only usable identity; about a quarter of biomedical author slots carry one, so every
author-level measure sees part of an author's network. Label base rate among authors with ≥ 5 biomedical papers ≈ 0.29%:
enough positives for within-stratum odds ratios and precision@k; paper-mill positives (207) are few.
