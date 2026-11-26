# F11 post hoc P10 (the 2021-2022 ORCID dip): lab notebook

Plan: `../../POSTHOC.md` round 2.

## f11_cov_20261126_01 (401 s, VM)
Biomedical publications 2018–2023 with ≥ 1 ORCID author / ORCID share of author positions (Meta): 2018 68.5% / 24.8%;
2019 71.1% / 26.3%; 2020 70.8% / 26.8%; 2021 66.2% / 24.7%; 2022 60.7% / 23.1%; 2023 63.1% / 24.7% (as f03). By Meta
publisher, share with ≥ 1 ORCID author 2019 → 2022 (biomedical papers 2019 → 2022): Frontiers 60.9% → 3.1% (29,356 →
103,372); Elsevier 66.9% → 44.9% (254,445 → 300,172); Springer 77.3% → 60.5%; Wolters Kluwer (Ovid) 41.4% → 17.8%;
Cureus 30.3% → 2.5%; stable or rising: Wiley 89.6% → 88.6%, MDPI 84.2% → 90.1%, ACS 99.4% → 99.2%, PLOS 95.2% → 94.8%,
Sage 81.5% → 89.3% (`coverage_by_publisher.csv`). DOI sample: 100 per year (`doi_sample.csv`; Meta share with ORCID in the
sample: 0.75, 0.72, 0.76, 0.73, 0.67, 0.68 for 2018–2023).

## f11_crossref_20261126_01 (159 s, laptop; Crossref REST API, 26 Nov 2026): superseded by `_02`, same results
599 of 600 DOIs found. Share with ≥ 1 ORCID author, **Meta vs Crossref today**: 2018 0.75 vs **0.43**; 2019 0.72 vs 0.50;
2020 0.76 vs 0.60; 2021 0.74 vs 0.68; 2022 0.67 vs 0.71; 2023 0.68 vs 0.68. ORCID slots Meta vs Crossref: 153 vs 64 (2018),
169 vs 92, 197 vs 133, 178 vs 166, 177 vs 192, 194 vs 194 (2023). Papers where Crossref has fewer ORCIDs than Meta: 50, 47,
36, 16, 1, 0.
**Reading:** for 2018–2020 papers Meta carries far more ORCID iDs than Crossref holds even today, so Meta added them from
another source; OpenCitations' ingestion code does this (`oc_ds_converter` `ra_processor.py`, `orcid_finder`: when a
Crossref record lacks ORCIDs, the DOI is looked up in an ORCID-DOI index and iDs are attached by name; `oc_meta`
`config/crossref_config.yaml`). For 2022–2023 the two sources agree. Crossref's own share rises (0.43 → 0.71, 2018 →
2022), so the dip in Meta comes from how Meta loaded the data (enrichment that adds less for recent papers, and
publisher-level gaps such as Frontiers and Elsevier in 2022), not from falling ORCID use in the source metadata.

## f11_crossref_20261126_02 (127 s, laptop; Crossref REST API, 26 Nov 2026): cited
Rerun after the release guard found a personal contact address in the script (the polite-pool `mailto`); the address is
now read from `CROSSREF_MAILTO` and not written anywhere (`polite_pool: true` in the config). Results and
`crossref_vs_meta.csv` byte-identical to `_01` (599 of 600 DOIs found).
