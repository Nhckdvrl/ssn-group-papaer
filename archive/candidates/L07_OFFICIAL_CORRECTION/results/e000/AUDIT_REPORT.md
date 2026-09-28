# E000 Data-Yield Audit Report

**Verdict:** GO for scaled acquisition and model pilot; not yet a paper-mainline claim.
**Run date:** 2026-09-08
**Claim tested:** D0 only.

## Corrected evidence table

| Quantity | Result |
|---|---:|
| Complete PubMed frame | 121,396 records |
| Fixed-seed sample | 500 records |
| Record-level `ErratumFor` + PMCID validation | 500 / 500 |
| JATS PMID matches correction PMID | 500 / 500 |
| Frozen stratified manual review | 162 records |
| Confirmed T1 yield, weighted to all 500 | 12.81% |
| Stratified design-based 95% CI | 9.49–16.13% |
| T1 + unverified T2 ceiling | 19.10% (15.13–23.07%) |

The T2 ceiling is not gold. T2 records remain excluded until the linked original deterministically supplies the old span.

## What the audit established

- Direct publisher-authored updates are sufficiently common to scale without synthetic corrections.
- At the lower confidence bound, screening about 1.6k notices should produce 150 T1 pairs before applying the separate original-state requirement.
- The 33 T1 records directly observed in the corrected review span 27 journals, 2015–2026, and four balanced classes: 8 numeric/result, 8 method/entity, 8 qualifier/prose, and 9 table/figure-text/unit.
- Visual-only changes remain a separate T3 track and do not inflate textual yield.

## E000f identifier-scope repair

The first completed audit incorrectly collected every descendant `ArticleId` in a PubMed record. IDs in `ReferenceList` could therefore overwrite the record's own IDs. The implausible E001 result that only 1/32 linked originals had PMC text exposed this bug.

The repair reads only `PubmedData/ArticleIdList`, retains the identical 121,396-ID frame and fixed 500-ID sample, re-downloads PMC XML using corrected identifiers, regenerates the review queue with the unchanged seed/quotas, and rechecks all 162 selected records. After repair, all 500 JATS PMIDs match their correction PMIDs. The superseded 10.99% estimate and 145/500 “unavailable notice” statement must not be cited.

## What remains unestablished

- E000 does not establish model behavior or C1–C3.
- The query is PMC-linked and biomedical-heavy, not a population of all publishers.
- T1 yield is not the same as historical-original yield; E001 measures that additional constraint.

## Reproduction

```bash
python3 scripts/run_yield_audit.py --config configs/e000_yield_audit.json
python3 scripts/make_review_queue.py --config configs/e000_yield_audit.json
python3 scripts/summarize_review.py --config configs/e000_yield_audit.json
```

Machine-readable outputs are `manifest.json` and `manual_review_summary.json`. Raw XML is re-downloadable and ignored; the complete PMID frame, annotations, code, and results are versioned.
