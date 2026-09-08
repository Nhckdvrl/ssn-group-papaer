# E000 Data-Yield Audit Report

**Verdict:** **GO for minimum model pilot; not approved as paper mainline.**
**Run date:** 2026-09-08
**Claim tested:** D0 only.

## Evidence table

| Quantity | Result |
|---|---:|
| Complete PubMed frame | 121,396 records |
| Fixed-seed sample | 500 records |
| `ErratumFor` + PMCID validation | 500 / 500 |
| JATS is the correction notice itself | 355 / 500 (71.0%) |
| Notice PMCID points to original article | 145 / 500 (29.0%) |
| Manually reviewed content records | 162 |
| Confirmed T1 yield, weighted to all 500 | 10.99% |
| Stratified design-based 95% CI | 8.69–13.28% |
| T1 + unverified T2 ceiling | 14.15% (11.70–16.60%) |

The T2 ceiling is not a gold result. Those records remain excluded until the linked original is fetched and the old span is deterministically verified.

## What the audit established

- The source is viable without constructing synthetic corrections: the conservative T1 estimate alone supports scaling to a 150–300-pair pilot.
- Using the lower confidence bound, plan to screen roughly 1.7k records for 150 T1 pairs or 3.5k for 300.
- The 40 directly verified T1 records span 33 journals and 2011–2026. Their classes are 14 numeric/result, 7 method/scientific-entity, 8 qualifier/prose, and 11 textual table/figure label or unit updates.
- A PMCID on a correction record does not prove that PMC exposes the correction notice. JATS PMID equality is load-bearing; omitting it contaminated the parser with original-article text in 29% of this sample.
- Visual-only corrections are common enough to matter but remain a separate T3 track. They must not inflate the text-pair yield.

## What the audit did not establish

- No LLM was evaluated.
- C1–C3 remain hypotheses.
- We have not shown that a model needs explicit update state; many T1 notices may be lexically easy.
- `T2_PENDING` records are not yet gold.
- The query frame is PMC-associated biomedical-heavy PubMed, not all publishers or disciplines.

## Decision rationale

The candidate survives because direct publisher-authored proposition updates are neither a tiny handful nor one homogeneous correction type. The absolute frame is large, the lower-bound acquisition cost is manageable, and meaningful text classes exist. It is not promoted beyond a pilot because the remaining scientific risk is now model/task validity: if strong models simply copy Y at ceiling and authority/order controls add no boundary, the paper identity collapses to “LLMs can read errata.”

## Reproducibility pointers

- Config: `configs/e000_yield_audit.json`
- Collection/parser: `scripts/run_yield_audit.py`
- Frozen review sampler: `scripts/make_review_queue.py`
- Manual labels: `data/annotations/e000/manual_labels.json`
- Statistical summary: `scripts/summarize_review.py`
- Raw PubMed/PMC XML and complete sampling frame: `data/raw/e000/`
- Parsed records/review queue: `data/processed/e000/`
- Machine-readable results: `results/e000/manifest.json`, `results/e000/manual_review_summary.json`
- Environment: Python 3.12.3, requests 2.31.0; no new environment or dependency.

## Next experiment

Acquire a 150-item T1 pilot set using the same identity checks, then preregister ORIGINAL ONLY / FLAT / EXPLICIT UPDATE with order swap and a newer-but-unofficial conflict control. Before inference, verify that questions require reconciling X and Y rather than locating a replacement string.
