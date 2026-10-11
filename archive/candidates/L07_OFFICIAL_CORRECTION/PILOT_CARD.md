# L07 — Minimum Decisive Pilot Card

**Candidate:** Official Correction ≠ Current Scholarly Claim  
**Status:** DATA-AUDIT FIRST  
**Goal:** Establish that publisher-defined corrections yield enough direct old→new proposition gold, then test whether flat document reading preserves the current scholarly claim.

## Phase 0 — Mandatory data-yield audit
Do **before target-model compute**.

Collect roughly **500 linked PMC/PubMed correction notices** using official original↔correction relations.

Classify each notice into:
1. **Tier 1 exact proposition replacement** — explicit “X should read Y / instead of X, Y”.
2. **Tier 2 recoverable semantic update** — publisher clearly identifies old and corrected content, but extraction requires structured alignment.
3. **Metadata/non-propositional** — author, affiliation, citation, formatting only.
4. **Unusable/ambiguous**.

Record:
- notice type;
- corrected location (text/table/figure);
- old proposition;
- new proposition;
- extraction confidence;
- whether mapping is publisher-authored or author-inferred.

### Data-gate survival
Survive only if absolute usable count and correction-type diversity are enough for:
- a 150–300 example pilot;
- multiple substantive correction classes;
- plausible Main-scale expansion.

Kill if usable gold is tiny, mostly lexical/metadata, or requires subjective author interpretation.

## Minimum model pilot
Use **150–300 Tier 1/2 pairs**, balanced across numbers, methods, qualifiers, prose claims, and table/figure facts when available.

Conditions:
1. **ORIGINAL ONLY**
2. **ORIGINAL + CORRECTION FLAT**
3. **EXPLICIT UPDATE** — structured old→new / superseded-by representation

Use two strong model families.

## Primary estimand
Does the system return the **current proposition Y** rather than historical **X**, and does explicit update state improve over flat aggregation?

## Metrics
- current-proposition accuracy;
- obsolete-X repetition rate;
- blended X+Y rate;
- update-type confusion;
- explicit-update gain over flat input;
- robustness to original/correction order.

## Informative outcomes
### A — Direct reading sufficient
Flat ≈ explicit update across correction types.

### B — Explicit state necessary
Flat frequently repeats/blends X while structured update recovers Y.

### C — Boundary
Local replacements succeed; diffuse/table/figure/method corrections fail.

All are valid.

## Reviewer-compression kill
Kill if the final story is only “LLMs can read errata” or “newest document wins.”  
Survive only as **official scholarly supersession is a distinct operation that changes scientific QA/IE state**.
