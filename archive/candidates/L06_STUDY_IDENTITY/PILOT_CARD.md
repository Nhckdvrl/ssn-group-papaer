# L06 — Minimum Decisive Pilot Card

**Candidate:** Study Identity Is Not Document Identity  
**Status:** PILOT-READY  
**Goal:** Test whether the same papers yield the same scientific synthesis when oracle study membership is removed or corrupted.

## Load-bearing estimand
Not publication-linkage accuracy. Measure whether **study identity is necessary to preserve evidence accounting and synthesis conclusions**.

## Data
Use CochraneForest cases with:
- ≥3 studies;
- ≥1 genuine multi-report study;
- accessible paper text;
- provider/review-defined study↔paper membership;
- usable study-level evidence/synthesis target.

Target first pass: **25–40 forest plots**.

## Conditions
Hold exact paper content and total evidence budget fixed.

1. **ORACLE** — true study membership.
2. **FLAT** — papers supplied without study grouping.
3. **WRONG-SPLIT** — reports from one study assigned to separate pseudo-studies.
4. **WRONG-MERGE** — reports from distinct studies assigned to one pseudo-study.

Predicted grouping is Phase 2, not required for the first pilot.

## Required outputs
For each condition:
- inferred evidence units/studies;
- study-specific conclusion/effect;
- final synthesis conclusion;
- optional confidence/weight.

## Primary comparisons
- ORACLE vs FLAT: is explicit identity necessary?
- ORACLE vs WRONG-SPLIT: does duplicate evidence inflate support?
- ORACLE vs WRONG-MERGE: does conflation erase independent evidence?
- paper-level extraction accuracy vs synthesis correctness: can extraction stay right while evidence accounting becomes wrong?

## Metrics
- study-unit reconstruction accuracy;
- study-level inference accuracy;
- final synthesis agreement with oracle/reference;
- false evidence-count inflation;
- false evidence-collapse rate;
- conclusion flips / materially changed synthesis.

## Informative outcomes
### A — Identity necessary
ORACLE > FLAT while paper extraction is similar.

### B — Identity dispensable
FLAT reconstructs the same study units and preserves synthesis.

### C — Boundary
Need depends on number of reports, identifier presence, lexical similarity, outcome/timepoint mismatch, or review complexity.

### D — Error asymmetry
Split and merge produce different scientific failure modes.

All four are valid scientific routes.

## Immediate kill conditions
Kill if:
- genuine multi-report cases are too few/trivial;
- results reduce to generic publication linkage F1;
- no synthesis-level quantity changes can be measured;
- a direct prior paper already performs the same matched-paper oracle/flat/split/merge intervention;
- only isolated cherry-picked cases move.

## Promotion condition
Promote only if the pilot supports a general **evidence-unit representation** conclusion, not “CochraneForest works better with grouping.”
