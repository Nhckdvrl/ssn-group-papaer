# L06 — Research Plan

**Candidate:** Study Identity Is Not Document Identity  
**Goal:** determine whether explicit study identity is necessary for automated evidence synthesis when the papers themselves are held fixed.

---

## 1. Minimum decisive pilot

### Sample
Target ~25–40 CochraneForest forest plots satisfying:
- ≥3 studies;
- ≥1 multi-report study;
- accessible full papers;
- usable study-level gold.

### Models
Start with:
- one strong open model that can fit the paper context / retrieval package;
- one second model family for replication.

Avoid a large model zoo.

### Conditions
1. ORACLE grouping;
2. FLAT/no grouping;
3. WRONG SPLIT;
4. WRONG MERGE.

Predicted grouping can wait until the necessity signal is understood.

### Outputs
Require structured output:
- inferred studies/evidence units;
- study-specific conclusion/effect;
- final synthesis conclusion.

### Key identification test
Hold the exact paper content and total token budget constant.

Only study membership may change.

## 2. Pilot success criteria

A candidate survives if at least one of these scientifically meaningful outcomes is clean:

### Route A — Explicit identity is necessary
Oracle materially improves correct evidence accounting/synthesis while paper-level extraction remains similar.

### Route B — Explicit identity is dispensable
Flat input reliably reconstructs the same study units and preserves synthesis across multi-report cases.

### Route C — Boundary
Necessity depends systematically on:
- reports per study;
- lexical similarity;
- identifier presence;
- outcome/time-point mismatch;
- review complexity.

### Route D — Error-type asymmetry
Wrong split and wrong merge have qualitatively different downstream consequences.

Any of these can support a Main paper if robust and broad enough.

## 3. What would kill the topic

KILL if:
- oracle and flat are identical only because all multi-report cases are trivial duplicate texts;
- the task has too few genuine multi-report cases;
- a prior paper is found with the same matched-paper identity intervention and synthesis conclusion;
- results reduce to “better publication linkage improves F1”;
- only one cherry-picked forest plot changes conclusion.

## 4. Phase 1 — Establish the necessity curve

Vary:
- reports per study: 1 / 2 / 3+;
- number of studies;
- overlap in authors/identifiers;
- textual similarity among reports;
- whether reports cover same vs different outcomes/time points.

Measure:
> performance gap between oracle and flat as a function of ambiguity.

## 5. Phase 2 — Causal corruption

Construct controlled metadata interventions on natural papers:

### Split intervention
one true study → multiple pseudo-study IDs.

### Merge intervention
multiple true studies → one pseudo-study ID.

### Swap intervention
assign one report to the wrong study.

Use the same papers, question, and model.

This isolates evidence-unit identity from retrieval coverage.

## 6. Phase 3 — Locate the failure stage

For each condition separately evaluate:

1. **document extraction** — did the model recover the numbers/statements?
2. **study construction** — did it combine reports correctly?
3. **synthesis** — did it count/weight studies correctly?

Possible mechanism claim:
> LLMs can read every paper correctly yet still make a scientifically invalid synthesis because they lose the study unit.

That would be substantially stronger than a linkage benchmark.

## 7. Phase 4 — Can predicted identity replace oracle identity?

Only after C1 is established:

- simple identifier/metadata baseline;
- text-based linkage;
- LLM-based grouping;
- oracle upper bound.

Question:
> if identity is necessary, how much grouping accuracy is required before synthesis is preserved?

This yields a practical decision threshold rather than a generic method race.

## 8. Planned C1 → C2 → C3

### C1
**Is oracle study identity necessary?**

### C2
**Why/when?**
- implicit reconstruction;
- split/merge sensitivity;
- failure stage;
- ambiguity conditions.

### C3
**What should NLP systems do?**
- remove explicit grouping;
- recover it automatically;
- or preserve it as a mandatory evidence representation.

## 9. Main-level breadth test

Before mainline approval require:
- more than one model family;
- enough multi-report studies;
- both split and merge interventions;
- synthesis-level consequence, not only study F1;
- at least one replication outside the easiest CochraneForest cases or a strong held-out regime.

## 10. Pre-mainline checklist

- [ ] Same papers held constant across identity conditions.
- [ ] Oracle study membership is external gold.
- [ ] Multi-report cases have sufficient scale.
- [ ] Extraction vs synthesis effects are separated.
- [ ] Wrong split and wrong merge both tested.
- [ ] Flat preservation route is treated as a valid scientific result.
- [ ] Direct modern collision re-checked immediately before expansion.
- [ ] Reviewer compression cannot accurately reduce the paper to “CochraneForest grouping ablation.”

## Final pilot verdict

**PILOT-READY, not yet paper-mainline approved.**
