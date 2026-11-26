# Project F literature (F1 gate, 2026-11-26)

Every DOI below was resolved through the Crossref API (fallback DataCite) on 2026-11-26: `doi_check_20261126.tsv`
(44 of 44 OK; built by `verify_dois.py` from `dois_candidates.tsv`). "Read" says how much was read: **full** (full text),
**sections** (the named sections of the full text), **abstract** (publisher/Crossref/DataCite/arXiv abstract), or
**title** (only cited from another paper; must be read before a specific claim is cited). Raw search results:
`searches_20261126/` (OpenAlex title/abstract searches, arXiv API searches, Semantic Scholar/Crossref/DataCite
metadata; queries listed at the end). Full texts read are not stored in the repository (copyright); they were read
from the publisher or arXiv pages.

## Closest prior work: author-level citation-anomaly signals and retractions

| # | Reference | DOI | Read | What it does | Overlap with F |
|---|---|---|---|---|---|
| 1 | Evdaimon, Ioannidis, Nikolentzos, Chatzianastasis, Panagopoulos & Vazirgiannis (2024, v3 2025), *Metrics to Detect Small-Scale and Large-Scale Citation Orchestration*, arXiv | 10.48550/arXiv.2406.19219 | **full** (v3 HTML, 2026-11-26) | Scopus (ICSR Lab), 1,496,680 authors with >5 full papers and ≥1,000 citations. Three author indicators: C/h² (low = small-scale orchestration), A50%C (number of citing authors explaining 50% of citations), A50 (co-authors with >50 joint papers). Extreme = 1% tails. Retraction check: random samples of 100 authors per indicator group searched by hand in the Retraction Watch database (June 2025), retractions at any time; e.g. 5/100 with only extreme C/h², 1/100 with only extreme A50%C, 5/11 with extreme C/h² and A50. No comparison group matched on field, productivity or career age; data "available from the authors upon request" | **Highest.** Proposes the indicators; its retraction check is retrospective, sampled and uncontrolled. F tests comparable signals prospectively, on open data, within strata |
| 2 | Ali, Basuni, Kamal, Haley, Kadry & Saqr (2026), *PeerTrust Finds Elevated Citation-Forensic Profiles in Recent Highly Cited Research*, XSci preprint | 10.66977/xsci.2610.000r | **sections** (abstract, §1–2.4 of the PDF, the posted AI review; 2026-11-26) | A public researcher-level screening tool keyed on ORCID, on OpenAlex. Three rules: co-author citation share adjusted for team size (NCI_adj > 35), **reciprocal-citation pact nodes** (a citing author with more than two "reciprocal works", i.e. citing works that the subject's works also cite; fires when > 5 such authors), publication burst (B > 3). Benchmark = computational reproducibility on 268 ORCIDs of a citation-enriched cohort; 44.2% crossed the pact threshold. **No outcome labels**: "Sensitivity, specificity, positive predictive value … cannot be estimated from these data". The reviewer asks for prospective validation | **High.** A deployed rule set built on exactly the signals F tests; never validated against an outcome. F is that validation, for the reciprocity and co-author rules, on a different open source |
| 3 | Mohammad (2026), *Self-citation, inclusion and retractions in the "top 2%" lists of top-cited scientists, 2019 to 2026: data and code*, Zenodo | 10.5281/zenodo.24526566 (DataCite) | abstract (record description) | Data/code record of a manuscript "submitted to PNAS" (not public). Pseudonymised matrix of all eight releases of the Ioannidis top-2% lists; includes "the cross-sectional and **prospective** logistic models" of retraction on self-citation. Data derived from Scopus via Elsevier; CC BY-NC | **Closest concurrent work** for the prospective element. Differences: self-citation only (no reciprocity or rings), highly cited authors only, Scopus-derived lists. Cite as concurrent; do not describe its results (manuscript unseen) |
| 4 | Ioannidis, Pezzullo, Cristiano, Boccia & Baas (2025), *Linking citation and retraction data reveals the demographics of scientific retractions among highly cited authors*, PLOS Biology | 10.1371/journal.pbio.3002999 | abstract | Retraction Watch linked to Scopus for 217,097 career-long top-cited scientists; 3.3% have ≥1 retraction; those with retractions have "higher self-citation rates" and larger volume | Cross-sectional association (self-citation ↔ retraction) that F's reference signal replicates prospectively on open data |
| 5 | Ioannidis (2025), *Features and signals in precocious citation impact: A meta-research study*, PLOS ONE | 10.1371/journal.pone.0328531 | **sections** (published full text, abstract and Results, 2026-11-26) | Precocious top-cited authors; 8 signal indicators incl. self-citation > 95th percentile and C/h² < 2.45; published text: "The 17 ultra-precocious citation impact authors in the 2017–2020 top-cited lists who had retractions showed on average **4.1 of these 8** signal indicators" (mean 4.1, median 4; retractions as of 8 Oct 2024). The bioRxiv abstract read first said "4 of these 7": **corrected 2026-11-26 after review** | Retrospective look-back on 17 authors; motivates C/h² as a reference signal |
| 6 | Wren & Georgescu (2022), *Detecting anomalous referencing patterns in PubMed papers suggestive of author-centric reference list manipulation*, Scientometrics | 10.1007/s11192-022-04503-6 | abstract | 20,803 highly published PubMed authors; non-self-citations per citing paper follow Zipf's law; Gini of NSC; 81–231 outlier authors; "Anomalies are not proof" | Same literature (PubMed) and the concentration idea; no retraction outcome (TODO(verify) in the full text) |
| 7 | Li, Aste, Caccioli & Livan (2019), *Reciprocity and impact in academic careers*, EPJ Data Science | 10.1140/epjds/s13688-019-0199-3 | abstract (published version, via Semantic Scholar, 2026-11-26) | Reciprocity in "a citation network of authors" vs an ensemble of null models (data source not checked); "obtaining citations through reciprocity correlates negatively with an impactful career in the long term"; "a steady increase in reciprocity over the years, largely fuelled by the citations reciprocated between coauthors" | Methodological precedent for author reciprocity; reason to separate co-author from non-co-author exchange; no integrity outcome |
| 8 | Spanakis, Alexandrou & Spinellis (2026), *Citation Cliques in Low Impact Journals*, arXiv | 10.48550/arXiv.2605.11930 (DataCite) | abstract | Crossref author-to-author citations; authors in low-impact venues show 4.7× higher reciprocity and 6.7× higher co-author citation; outlier pipeline, cliques | Reciprocity and cohesion at author level; validated against venue impact, not retractions |
| 9 | Fister, Fister & Perc (2016), *Toward the Discovery of Citation Cartels in Citation Networks*, Frontiers in Physics | 10.3389/fphy.2016.00049 | abstract | Defines citation cartels as groups of authors that cite each other disproportionately; algorithmic guide, no empirical test | Definition used in the Introduction |
| 10 | Kojaku, Livan & Masuda (2021), *Detecting anomalous citation groups in journal networks* (CIDRE), Scientific Reports | 10.1038/s41598-021-93572-3 | full (read for Paper C) | Journal-level groups, validated against JCR suspensions | Journal level (Paper C tested it); suggests author–journal networks as future work |

## Related: citation manipulation, self-citation, paper mills, retraction prediction

| Reference | DOI | Read | Notes |
|---|---|---|---|
| Szomszor, Pendlebury & Adams (2020), *How much is too much? …self-citation excess*, Scientometrics | 10.1007/s11192-020-03417-5 | abstract | Self-citation distributions of 3,517 Highly Cited Researchers; expert interpretation needed |
| Bartneck & Kokkelmans (2011), *Detecting h-index manipulation through self-citation analysis*, Scientometrics | 10.1007/s11192-010-0306-5 | title | Background (cited in ref 1) |
| Seeber, Cattaneo, Meoli & Malighetti (2019), *Self-citations as strategic response to the use of metrics for career decisions*, Research Policy | 10.1016/j.respol.2017.12.004 | title | Background; early-career self-citation (ref 1's caveat) |
| Van Noorden & Chawla (2019), *Hundreds of extreme self-citing scientists revealed in new database*, Nature (news) | 10.1038/d41586-019-02479-7 | title | Background |
| Ioannidis, Baas, Klavans & Boyack (2019), *A standardized citation metrics author database annotated for scientific field*, PLOS Biology | 10.1371/journal.pbio.3000384 | title | Source of the top-2% lists behind refs 3–5 |
| Wilhite & Fong (2012), *Coercive Citation in Academic Publishing*, Science | 10.1126/science.1212540 | abstract (Crossref, 2026-11-26) | "Many journal editors appear to strategically target authors and papers to pressure them into citing the editors' journals" (editors, not reviewers: draft wording corrected) |
| Fong & Wilhite (2017), *Authorship and citation manipulation in academic research*, PLOS ONE | 10.1371/journal.pone.0187394 | title | Background |
| Ibrahim, Liu, Zaki & Rahwan (2025), *Citation manipulation through citation mills and pre-print servers*, Scientific Reports | 10.1038/s41598-025-88709-7 | abstract | Purchased citations on Google Scholar; author-level manipulation exists |
| Baccini, De Nicolao & Petrovich (2019), *Citation gaming induced by bibliometric evaluation*, PLOS ONE | 10.1371/journal.pone.0221212 | title | Country-level inwardness; background |
| Park, Yi, Chen, Warnow & Chacko (2026), *Modeling citations and cartels*, Research Square | 10.21203/rs.3.rs-9270520/v1 | abstract | Agent-based model: early advantage to cartels, lost over time |
| Gupta, Udandarao & Bandi (2026), *Trust-Aware Citation Cartel Ranking in Scholarly Knowledge Graphs*, arXiv | 10.48550/arXiv.2607.06528 | abstract | Paper-level communities on DBLP; composite cartel index incl. reciprocity; no outcome labels |
| Zhang, Liu, E et al. (2025), *A paper mill detection model based on citation manipulation paradigm*, JDIS | 10.2478/jdis-2025-0003 | abstract | Paper-level GNN classifier for paper-mill papers |
| Zhang (2026), *Born Flawed? Publication-Time Citation Topology Improves Retraction Early-Warning*, Research Square | 10.21203/rs.3.rs-10177352/v1 | abstract | Paper level, 219 retracted vs 184 controls (OpenAlex); reference-side features incl. self-citation rate raise out-of-time AUC 0.49 → 0.66 |
| Fletcher & Stevenson (2025), *Predicting retracted research*, Res Integr Peer Rev | 10.1186/s41073-025-00168-w | full (for Paper D) | Paper-level prediction from titles, abstracts and metadata; **no citation-network or reference features** (future work). Not to be cited for reference-list features (draft v0.1 did; corrected 2026-11-26) |
| Lou, Zhou & Li (2026), *Beyond Retractions*, JDIS | 10.1515/jdis-2026-0064 | full (for Paper D) | Retractions cluster in citation networks (paper level) |
| Richardson et al. (2025), *The entities enabling scientific fraud at scale are large, resilient, and growing rapidly*, PNAS | 10.1073/pnas.2420092122 | title | Paper mills as organised networks; Introduction |
| Candal-Pedreira et al. (2022), *Retracted papers originating from paper mills*, BMJ | 10.1136/bmj-2022-071517 | title | Background |
| Candal-Pedreira et al. (2024), *…references and citations*, J Clin Epidemiol | 10.1016/j.jclinepi.2024.111397 | abstract (for Paper D) | Interlinked clusters of paper-mill retractions |
| Abalkina (2023), *Publication and collaboration anomalies in academic papers originating from a paper mill*, Learned Publishing | 10.1002/leap.1574 | title | Collaboration anomalies of mill papers |
| Abalkina, Kunešová, Ozturk & Pirelli (2026), *Opening Pandora's box: Paper mills in conference proceedings*, Accountability in Research | 10.1080/08989621.2026.2733727 | abstract (arXiv 2604.22458) | Mill papers show "citation manipulation" and collaboration anomalies |
| Own work: Paper C (arXiv 2611.10471), Paper D (arXiv 2611.10474; data doi:10.5281/zenodo.23874477) | see `doi_check_20261126.tsv` | full | Journal level (C) and paper level (D) on the same snapshot; F is the author level |

Searched and set aside (not relevant enough or not verifiable): "Citation Cartels in Medical and Dental Journals" (editorials),
GADEC (LNCS 2024, no abstract available), Sharma & Khurana (arXiv 2502.00673; self-citation inside retracted papers),
"Datasets for July 2026 Berlin Hackathon on Citation Behavior of Paper Mills" (Zenodo 10.5281/zenodo.20177251; data only).

## Data sources and identity

| Reference | DOI | Read | Notes |
|---|---|---|---|
| Mohasel Arjomandi, Korobskiy & Chacko (2024), *Parsed Open Citations and PubMed Data*, Illinois Data Bank | 10.13012/B2IDB-5216575_V1 | own | The January 2024 graph |
| Massari et al. (2024), *OpenCitations Meta*, QSS | 10.1162/qss_a_00292 | **sections** (arXiv 2306.16191v2, §1–3.2) | "people are deduplicated only if they have an assigned ORCID, and never by other heuristics"; ORCIDs are checked for existence through the ORCID API; within a merge of two records, authors without an identifier are matched by name. **So the author unit in F is the ORCID iD**; authors without ORCID cannot be followed across papers |
| OpenCitations Meta CSV dump v7 (figshare) | 10.6084/m9.figshare.21747461.v7 | – | Author field format `Family, Given [omid:ra/… orcid:…]` (read on the VM) |
| Peroni & Shotton (2020), QSS | 10.1162/qss_a_00023 | – | OpenCitations |
| Haak et al. (2012), *ORCID: a system to uniquely identify researchers*, Learned Publishing | 10.1087/20120404 | title | ORCID |
| Rittman (2025), Crossref blog | 10.13003/692016 | (for Paper D) | Retraction Watch data via Crossref |
| Methods: Mantel & Haenszel 1959; Robins, Breslow & Greenland 1986; Wilson 1927; DuckDB (Raasveldt & Mühleisen 2019); Hirsch 2005 | see tsv | – | As in Paper D |

## Gap statement

Author-level signals of citation manipulation are well described: self-citation excess (refs 4, Szomszor 2020),
concentration of citing authors (ref 1's A50%C; ref 6's Gini of non-self-citations), reciprocity between authors
(refs 7, 8), and screening rules that combine them and are offered to funders and institutions (ref 2). Their link to
retraction has been examined only **cross-sectionally or retrospectively**: ref 1 searched samples of 100 flagged
authors for retractions at any time, with no comparison group; ref 4 compares retraction prevalence with self-citation
among top-cited scientists; ref 5 looks back at 17 authors. Ref 2 has no outcome labels at all. The one prospective
analysis found (ref 3, concurrent, manuscript not public) concerns self-citation among highly cited scientists on
Scopus-derived data. **No study found tests reciprocity- or ring-type signals prospectively against later retractions,
on open data, inside strata of journal and productivity.**

## Gate decision (2026-11-26): PASS, positioned as a prospective validation

F goes ahead as a test of proposed (ref 1, refs 6–8) and deployed (ref 2) author-level screening signals, in the same
frozen-score, out-of-sample design as Paper D:
1. **Prospective, frozen.** Signals computed from the January 2024 graph (complete to about Sept 2023) are hashed before
   any post-snapshot retraction is joined; outcome = a Retraction Watch retraction issued Feb 2024 – Oct 2026 for a paper
   that lists the author's ORCID.
2. **Inside strata.** Comparisons within the author's main journal and productivity band (Mantel–Haenszel), so that
   journal-level retraction waves (special issues, paper-mill journals) do not drive the result.
3. **Reference signals.** Self-citation share and C/h² (refs 1, 4, 5) are computed the same way, so F also gives an
   open-data prospective check of the published cross-sectional associations.
4. **Negative-control outcome.** Retractions for honest error only, which a manipulation-specific signal should not
   predict; and retractions for referencing/peer-review manipulation or paper mills, which it should.
5. **What open data can see.** ORCID coverage of biomedical authorship by year and among retracted papers (Meta
   deduplicates people only by ORCID), reported as a finding.
6. **Completes the series:** journals (C), papers (D), authors (F) on one open snapshot.

**Risks.** ORCID coverage (older papers, some publishers); rare outcome; label noise (retraction ≠ manipulation);
ethics: group-level results only, no author names, no per-author scores released; "anomalous pattern", never
"misconduct". Signals are **adaptations** of refs 1–2 on different data; never claim to reproduce PeerTrust's thresholds.

## Searches run (2026-11-26)
OpenAlex title/abstract (`oa_search.py`): citation cartel; citation ring; citation orchestration; citation cartels authors
detection; citation manipulation retraction; self-citation retraction; reciprocal citation authors; anomalous referencing
patterns; citation cliques; citation mills; retraction prediction; excessive self-citation authors; h-index manipulation;
author citation network anomaly; OpenCitations Meta; ORCID coverage. arXiv (`arxiv_search.py`): "citation cartel(s)";
"citation ring(s)"; "self-citation" AND retraction; "citation manipulation" AND author; "reciprocal citation".
Metadata/abstracts: Semantic Scholar batch (`s2_abstracts.py`), Crossref/DataCite (`meta_fetch.py`). Zenodo's API
returned 403 to scripts (DataCite used instead).

## Added 2026-11-26 (after the external review of draft v0.1)

| Reference | DOI / URL | Read | Use |
|---|---|---|---|
| Lipsitch, Tchetgen Tchetgen & Cohen (2010), *Negative Controls: A Tool for Detecting Confounding and Bias in Observational Studies*, Epidemiology 21(3) | 10.1097/ede.0b013e3181d61eeb | abstract | Negative-control outcomes to detect confounding and bias: the logic of the honest-error class |
| Priem, Piwowar & Orr (2022), *OpenAlex*, arXiv | 10.48550/arXiv.2205.01833 (DataCite) | abstract | OpenAlex and its disambiguated authors |
| OpenAlex Help Center, *Disambiguation – Authors* | https://help.openalex.org/data/authors/disambiguation/ (no DOI) | full page (2026-11-26) | Matching by ORCID, then vectors, then name rules; "precision 97.1% (±0.5) and recall 91.6% (±0.8)" (estimate of 22 Nov 2026, judged by a language model); "about 3 in 100 works on a researcher's main profile belong to someone else" |
| Pendlebury (2025), *The continuing evolution of the Highly Cited Researchers list*, Clarivate blog, 30 April 2025 | https://clarivate.com/academia-government/blog/the-continuing-evolution-of-the-highly-cited-researchers-list-to-promote-fairness-accuracy-and-research-integrity/ (no DOI) | full page (2026-11-26) | Exclusions "~300 researchers or 4.5% of candidates … in 2021. By 2024 … ~2,000 (23%)"; screening for excessive self-citation, "group citation rings: researchers who repeatedly cite one another", hyper-authorship |
| Mohammad (2026), Zenodo | 10.5281/zenodo.24526566 (concept) / .24526567 (version 1.3.0, issued 2026-11-25; DataCite) | record description | Includes code for "cross-sectional and prospective logistic models": the abstract's novelty claim was narrowed to ring-type signals |
| OpenCitations ingestion code (no DOI): `oc_meta` `config/crossref_config.yaml` ("ORCID-DOI index directory"), `oc_ds_converter` `ra_processor.py` (`orcid_finder`) | github.com/opencitations/oc_meta, github.com/opencitations/oc_ds_converter (read 2026-11-26 via the GitHub API) | code | When a Crossref record lacks ORCIDs, Meta's ingestion looks the DOI up in an ORCID-DOI index and attaches iDs by name match: explains why Meta's older records carry more ORCIDs than Crossref (P10) |


## Citation-claim pass (2026-11-26, after external review)

Every sentence of the form "X found / did / says Y" in the manuscript (42 sentences; listing built from the .tex files and
this file) was checked against the source text at the depth recorded above. Abstracts re-read on 2026-11-26 through
Crossref or Semantic Scholar unless stated.

| Source | Manuscript claim | Result |
|---|---|---|
| Fister et al. 2016 | definition "cite each other disproportionately more than … other groups … same subject"; perspective with theoretical examples and an algorithmic guide | matches abstract (near verbatim) |
| Li et al. 2019 | reciprocity vs null models; negative correlation with long-term impact; steady rise, largely co-author reciprocity | matches published abstract |
| Spanakis et al. 2026 | authors matched across low/high-impact venues (by subject and h5) on Crossref; higher reciprocity and co-author citation | matches abstract |
| Wren & Georgescu 2022 | 20,803 authors; NSC from single papers vs Zipf; outliers flagged; anomalies not proof | abstract says "approximates Zipf's law": text changed from "follow" to "approximately follow" |
| Szomszor et al. 2020 | graphical threshold for excessive self-citation; 3,517 HCRs; expert interpretation | matches abstract ("graphical, distribution-driven assessment … demarcates a threshold") |
| Evdaimon et al. 2024 | indicators; samples of 100; 1–5%; 5 of 11; 0.7% overall figure | full text (earlier read) |
| Ioannidis et al. 2025 (PLOS Biol) | top-cited with retractions have higher self-citation rates | matches abstract |
| Ioannidis 2025 (PLOS ONE) | 17 ultra-precocious authors, 4.1 of 8 indicators, retractions by Oct 2024 | matches published text; "when they entered the lists" was not in the source and was **removed** |
| Mohammad 2026 (Zenodo v1.3.0) | record includes cross-sectional and prospective logistic models | matches record description |
| Ibrahim et al. 2025; Park et al. 2026; Gupta et al. 2026 | bought citations; agent-based early advantage that fades; ranking of paper communities | match abstracts (LIT rows) |
| Zhang et al. 2025 (JDIS) | classifier from citation relations and titles | matches abstract (BERT on titles + heterogeneous citation graph) |
| Zhang 2026 (Research Square) | reference-side features incl. self-citation rate add value in a small matched sample | matches abstract ("matched sample of 219 retracted and 184 control papers") |
| Candal-Pedreira et al. 2024 | paper-mill retractions reference and are cited by other mill retractions | matches abstract (checked earlier this day) |
| Fletcher & Stevenson 2025 | text and metadata, no citation links | full text; corrected earlier this day |
| Wilhite & Fong 2012 | editors pressure authors to cite their journals | matches abstract; corrected earlier this day |
| Kojaku et al. 2021 | CIDRE journal groups | full text (Paper C) |
| Pendlebury 2025 (Clarivate) | screening criteria; 300 (4.5%) in 2021, 2,000 (23%) in 2024; "quantitative algorithmic step, creating a longlist of candidates … followed by a qualitative screening process" | matches page (re-read 2026-11-26) |
| Ali et al. 2026 (PeerTrust) | rules; 260 of 268 scored; 44.2% pact; no outcome labels; "These signals neither establish misconduct nor estimate population prevalence" | matches abstract; Discussion no longer says the authors "recommend human review" (not found), it now cites their statement that the signals do not establish misconduct |
| OpenAlex help page | matcher assigns the authors of every new work using ORCID, name, institutions, sources, topics and co-authors; ~3 in 100 works on a main profile belong to someone else | matches page (re-read 2026-11-26) |
| Massari et al. 2024 | people deduplicated only by ORCID; ORCIDs checked for existence | matches sections read |
| Lipsitch et al. 2010; Priem et al. 2022; Haak et al. 2012 | negative-control logic; OpenAlex; ORCID registry | match abstracts / title |


## Second external review (2026-11-26): three references re-checked

| Source | Finding | Action |
|---|---|---|
| OpenAlex help page, *Disambiguation – Authors* | The page (last updated 23 November 2026) contains "Our latest estimate, from 22 November 2026, is precision 97.1% (±0.5) and recall 91.6% (±0.8)… On average, about 3 in 100 works on a researcher's main profile belong to someone else", "judged by a language model, not by people". Two matching systems: the July 2023 V3 model "weighed name similarity, co-authors, institutional affiliations, research topics, citation patterns and ORCID" and assigned works added up to early November 2025; the nightly matcher (works added since 20 December 2025) uses ORCID, printed name, institutions, sources, topics and context (incl. three co-authors) and "does not use citation patterns". The reviewer did not find the accuracy figure, probably in an earlier version of the page | Text now describes both systems and attributes the estimate as OpenAlex's own, LLM-judged; citation points to the Wayback snapshot `web.archive.org/web/20261126210020/https://help.openalex.org/data/authors/disambiguation/` (Markdown copy: `…/20261126210139/https://help.openalex.org/data/authors/disambiguation.md`); both checked to contain the passage |
| Evdaimon et al., arXiv:2406.19219 | v3 (24 June 2025) HTML, §2.7 and §3.7, re-read: "We select a random sample of 100 authors from each group… 5 of the 6 groups had more than 100 authors"; "very high (45.5%, 5/11) for those with both C/h² and A50. It was 5% (5/100)… 3% (3/100)… only 1% (1/100)"; Discussion: "only 0.7% of authors with at least 5 full papers across science have had one retraction due to reasons other than publisher/journal error" | All numbers in the text confirmed; reference now cites v3 (year 2025, version and date in the entry) |
| Park et al., *Modeling citations and cartels* | Cited version (Research Square v1, 2 April 2026) was revised after an error in a figure (Zenodo concept 10.5281/zenodo.19368703: v3 18 May 2026; v4 6 October 2026, doi:10.5281/zenodo.23196050, "Accepted in abbreviated form as a full paper in Complex Networks 2026"). Zenodo returns 403 to this network, so the corrected text could not be read | **Cut** (user decision, 2026-11-26): sentence and reference removed |

PeerTrust (Ali et al. 2026), PDF re-read on 2026-11-26 (§2.2.2 and §1): "A pact node is a citing author associated with
more than two such reciprocal works. The pact statistic P_i is the number of these citing-author nodes. The rule fires
when P_i > 5 and contributes three points"; the definition does not exclude co-authors. Purpose: "an evidence-oriented
screen intended to identify cases that merit human examination, not an automated finding of misconduct". Benchmark: "One
researcher crossed the coauthor-citation-isolation threshold" (of 260 scored). Used for: the description of the adapted
rules (methods), R1's 12 flagged authors (results), and the third implication (discussion).

OpenAlex snapshot re-opened on 2026-11-26 (third check, after the reviewer reported seeing a page "Last updated August 19,
2026"): `web.archive.org/web/20261126210020/https://help.openalex.org/data/authors/disambiguation/` contains "Our latest
estimate, from 22 November 2026, is precision 97.1% (±0.5) and recall 91.6% (±0.8), with 95% intervals. On average, about
3 in 100 works on a researcher's main profile belong to someone else" and "They are judged by a language model, not by
people."

Reference metadata fixed on 2026-11-26: Fister et al. (2016) first author Iztok Fister Jr. (publisher's page; Crossref
gives both first authors as "Iztok Fister"), Front. Phys. 4:49 (article number from Semantic Scholar); Fletcher &
Stevenson (2025) article 9 (Crossref); Robins et al. (1986) pages 311–323 (Semantic Scholar; Crossref gives only 311).
