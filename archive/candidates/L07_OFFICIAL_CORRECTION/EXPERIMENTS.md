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

## E003 — Scaled item acquisition and gold construction

**Status:** paused at a clean checkpoint; collection and deterministic proposals complete
**Linked claim:** D1
**Question:** Can the natural correction stream yield at least 150 leak-free, proposition-level items under the unchanged publisher-licensed gold contract?

### E003a — Frozen expansion collection (complete)

- Start from the E000 complete 121,396-PMID frame and exclude all 500 E000 sample IDs.
- Draw 4,100 deterministic candidates with seed `20260910`, targeting 4,000 accepted records plus a 100-record reserve.
- Apply the same record-level `ErratumFor`, PMCID, and correction-JATS PMID identity checks repaired in E000f.
- Result: 4,000 accepted notices, zero E000 overlap, and 4,000/4,000 JATS identity matches. One candidate before the stopping boundary (PMID 24278899) lacked `ErratumFor` and was replaced deterministically.
- Parser triage: 582 exact-replacement, 32 location-plus-new, 1,194 numeric/symbolic, 1,231 metadata/nonpropositional, 36 semantic-unaligned, and 925 unusable/ambiguous. These categories are not gold.

### E003b — Deterministic high-precision proposals (complete)

- Run quote-aware direction patterns only over the 582 exact-replacement candidates.
- Require distinct normalized old/new strings; retain the publisher notice evidence and identifiers with every proposal.
- Result: 140 candidate pairs from 72 unique notices across eight pattern families.
- Scientific interpretation: this is a compact manual-review queue, not a yield estimate and not evidence for C1–C3. Multiple proposals may come from one notice, and metadata or incorrectly directed matches may remain.

### E003c — Local-model recall proposals (paused before output)

- Planned role: screen the same 582 notices for verbatim X→Y proposals missed by rules, excluding metadata and nonpropositional changes.
- Safeguard: accept a model proposal only if both strings occur verbatim after normalization; human review and linked-original validation remain mandatory.
- A Qwen2.5-14B run was started locally, then terminated during model loading/inference to control compute consumption. The script writes only after full completion, so no partial proposal, summary, or scientific result exists.
- This interrupted run must not be counted as an experiment or compared with E003b.

### E003d–E003f — Not started

1. Merge and de-duplicate rule/model proposals by correction PMID plus normalized X/Y.
2. Manually label each proposal as `ACCEPT_SUBSTANTIVE`, `NONPROP`, `VISUAL`, `BAD_DIRECTION`, `NOT_EXACT`, or `OTHER_REJECT`, with a source-grounded note.
3. Fetch linked originals only for accepted pairs; identify a model-facing historical excerpt containing X and excluding Y, and record failures rather than repairing them synthetically.
4. Author and independently check one natural question/current-answer target per surviving operation; reject leakage, ambiguous answers, and questions answerable without reconciling the update.
5. Freeze 150 items with journal/year/domain/update-class composition reported before model evaluation. If fewer than 150 survive, extend the same deterministic frame/reserve procedure; do not relax gold.

### Exact resume order

1. Decide whether model-assisted recall is worth its compute. If yes, rerun `propose_pairs_with_llm.py` to completion with the frozen config; if no, proceed with the 140 rule proposals and later expand deterministic patterns based only on documented false negatives.
2. Run `merge_pair_proposals.py` only after the chosen proposal sources exist, then freeze the review queue hash before annotation.
3. Complete double-check review and report acceptance/rejection counts by source and pattern. Do not calculate a paper result from proposal counts.
4. Complete original-state validation and question construction; freeze the final 150-item data card and exclusion flow.
5. Run E004 free generation on three serious model families using original-only, correction-only, flat original+correction in both document orders, explicit-update, and unrelated-correction conditions. Use greedy decoding, item-level outputs, current-only/obsolete/blend/error adjudication, paired bootstrap confidence intervals, and correction-type boundary analyses.

### Claim and stop rules

- C1 requires a robust flat-condition deficit relative to original-only comprehension and correction-only interpretability, with obsolete reuse or blending measured directly in free answers.
- C2 requires a reproducible interaction with update representation or correction complexity; an isolated aggregate accuracy difference is insufficient.
- C3 is considered only if explicit state materially repairs C1 without causing false overrides under unrelated corrections.
- If flat reading is near ceiling with tight intervals, explicit state provides no meaningful gain, or failures reduce to unreadable notices/task artifacts, L07 does not support an ACL/EMNLP/NAACL mainline in this form.
- If failures persist across model families and controls, and their boundaries distinguish authoritative supersession from generic recency/order effects, the result is eligible for mainline promotion and a broader robustness phase.

Full checkpoint counts and artifact boundaries are in `results/e003/REPORT.md`.
