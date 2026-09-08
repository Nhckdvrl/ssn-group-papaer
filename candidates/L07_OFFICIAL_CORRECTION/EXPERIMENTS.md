# L07 Experiment Registry

## E000 — PMC/PubMed correction-notice data-yield audit

**Status:** complete; data gate GO
**Linked claim:** D0
**Question:** Does an official, reproducible PubMed→PMC sampling frame yield enough direct and diverse proposition-level old→new corrections for the planned pilot?

### Sampling frame

- Source: NCBI E-utilities PubMed and PMC.
- Query: `"Published Erratum"[Publication Type] AND "pubmed pmc"[sb]`.
- Unit: one PubMed correction-notice record with a PMC full-text identifier and at least one `ErratumFor` link.
- Sample: simple random sample of 500 unique PubMed IDs from the complete query result returned on the run date.
- Seed: `20260908`.
- Snapshot: save the query, result count, complete eligible PMID frame, sampled IDs, PubMed XML, and PMC JATS XML.

This frame is intentionally narrower than all errata: it guarantees an NLM-linked original and machine-readable correction notice. It does **not** guarantee that the original full text is in PMC; this matters for Tier 2 feasibility and will be measured.

### Deterministic screening categories

1. `exact_replacement_candidate`: explicit replacement language likely containing both old and new content.
2. `numeric_or_symbolic_candidate`: a correction statement containing multiple numeric/symbolic values but no safely parsed exact replacement.
3. `location_plus_new_candidate`: an exact corrected location and replacement content, requiring original lookup for old content.
4. `semantic_not_alignable`: substantive correction language without deterministic old→new alignment.
5. `metadata_or_nonpropositional`: author, affiliation, citation, funding, spelling, or formatting only.
6. `unusable_or_ambiguous`: empty/inaccessible notice or no licensed mapping.

Parser categories are triage labels, not gold tiers. Human verification will estimate precision and missed yield using source snippets.

After E000f, the corrected parser strata contain 70 exact, 6 location-plus-new, 148 numeric, 153 metadata, 6 semantic-unaligned, and 117 unusable candidates. The unchanged review seed selects 45/4/50/30/3/30 respectively (162 records total).

### Gold audit labels

- `T1`: publisher explicitly provides exact old and new proposition/value.
- `T2`: publisher gives an exact location and corrected proposition/value, and old content is deterministically recoverable from the linked original.
- `T3_visual`: old/new table or figure content requires reliable visual/structured extraction; report separately, not in the decisive text pilot count.
- `NONPROP`: metadata/formatting/bibliographic only.
- `SEMANTIC_UNALIGNED`: scientifically substantive but no direct old→new proposition gold.
- `UNUSABLE`: inaccessible, empty, or ambiguous.

### Primary outputs and uncertainty

- Verified T1 yield with a stratified design-based 95% confidence interval; unverified T2 is reported only as a ceiling.
- Absolute projected count in this PMC-linked sampling frame.
- Correction class, year, journal, and domain diversity.
- Fraction requiring table/figure extraction.
- Parser candidate precision and an audited estimate of parser false negatives.

### Data-gate decision

- **GO:** evidence supports at least 150–300 high-confidence T1/T2 pairs with several substantive classes and plausible multi-journal expansion.
- **CONDITIONAL:** scale is plausible but one bounded issue (for example, original-PMC availability for Tier 2 or low parser recall) needs repair and re-audit.
- **NO-GO:** direct gold is a tiny/homogeneous subset, mostly metadata/lexical edits, or depends on subjective reconstruction.

No hard percentage is treated as scientifically magical. The decision uses absolute projected count, verified lower bounds, diversity, and whether the resulting QA/IE task would require genuine supersession rather than lexical copying.

### Protocol events before valid audit output

- **E000a — invalid shorthand query.** The preregistered shorthand `published erratum[pt] AND haserratumfor AND pmc[filter]` returned zero records on 2026-09-08. The expanded official field/filter query now in the config returned 121,396. `ErratumFor` remains a hard post-download XML check, so the scientific inclusion contract did not change.
- **E000b — ESearch cap.** One ESearch response exposed only 9,999 of the 121,396 IDs. The collector was changed to partition the identical query into non-overlapping publication-date shards, verify each shard, de-duplicate their union, and require equality with the undated count before sampling.
- **E000c — JATS identifier spelling.** The first local parse required `pub-id-type="pmc"`, while the downloaded JATS uses `pub-id-type="pmcid"`. This produced a visibly invalid 0/500 parse and no scientific statistic. The parser now accepts both NLM spellings and reuses the unchanged raw sample.
- **E000d — correction-record/full-text identity.** The audit requires JATS internal PMID equality before treating a document as notice text.
- **E000e — JATS evidence-window fidelity.** Pre-review inspection found that replacement cues and their quoted old/new text are often split across adjacent body paragraphs, while front/back extraction can introduce unrelated cues. Evidence extraction was frozen to notice `<body>` blocks with one preceding and two following blocks around each cue. No item had yet received a gold label.

These repairs occurred before manual review or any data-yield decision. The unchanged sample IDs and raw responses are preserved.

- **E000f — PubMed identifier scope (post-commit repair).** E001 exposed that the parser allowed `ReferenceList/ArticleId` values to overwrite record identifiers. The parser now reads only `PubmedData/ArticleIdList`. The identical frame/sample was replayed, PMC XML was re-downloaded, the unchanged review design was regenerated, and all 162 records were rechecked. All 500 notices now pass JATS PMID identity. Earlier 10.99%/145-unavailable results are superseded.

### Reproduction

Core command:

```bash
python3 scripts/run_yield_audit.py --config configs/e000_yield_audit.json
```

Raw outputs will live under `data/raw/e000/`; parsed/review data under `data/processed/e000/`; summaries under `results/e000/`.

### Result

Command:

```bash
python3 scripts/run_yield_audit.py --config configs/e000_yield_audit.json
python3 scripts/make_review_queue.py --config configs/e000_yield_audit.json
python3 scripts/summarize_review.py --config configs/e000_yield_audit.json
```

- Complete query frame: 121,396 PubMed IDs; fixed-seed sample: 500.
- Official relationship/identifier validation: 500/500 had `ErratumFor` and PMCID.
- Correction notice full text identity: 500/500 after E000f.
- Manual review: 162 records under frozen stratified quotas.
- Confirmed T1 yield: 12.81%; stratified design-based 95% CI 9.49–16.13%.
- T1+unverified-T2 ceiling: 19.10%; T2 is not counted as gold.
- Directly reviewed T1 diversity: 33 records, 27 journals, 2015–2026; 8 numeric/result, 8 method/entity, 8 qualifier/prose, 9 table/figure-text/unit.
- Environment: Python 3.12.3; requests 2.31.0; no new environment or dependency.

**Interpretation:** D0 is supported for pilot acquisition. L07 is not promoted to a paper mainline: C1–C3 remain untested, and ceiling performance on explicit lexical notices remains a kill condition.

## E001 — Original-state recoverability

**Status:** complete; narrower data contract adopted
**Question:** Does the currently available linked original still expose old X, or has the publisher overwritten it with new Y?

Thirty-two directly quoted operations were checked against current PMC title/abstract/body, excluding back-matter change notes. Seven were old-only, seven contained both, ten were new-only, seven matched neither selector, and one lacked PMC full text. Fourteen of 32 expose X. This is a diagnostic convenience set, not a population estimate.

**Decision:** every scaled item must verify that its model-facing original excerpt contains X and excludes Y. See `results/e001/REPORT.md`.

## E002a — Fixed-position forced-choice pilot

**Status:** invalid for scientific inference; retained as a design event

OLD was always presented first. Mistral selected OLD in 51/60 outputs, making update failure inseparable from candidate-position bias. No C1/C2 evidence is taken from this run.

## E002b — Position-counterbalanced forced-choice pilot

**Status:** complete; expansion GO

Ten leak-free items, three model families (12B, 24B, 32B), six evidence conditions, two A/B candidate orders, and greedy decoding produced 360 decisions. Macro original-only accuracy is 91.7%, correction-only 80.0%, flat 70.0%, explicit-update 76.7%, and unrelated-correction 85.0%. Position-robust flat accuracy is 56.7%.

**Decision:** the lexical-ceiling kill condition did not fire. Scale to 150 items and free generation; E002b is too small and too constrained to establish a paper claim. See `results/e002b_counterbalanced/REPORT.md`.
