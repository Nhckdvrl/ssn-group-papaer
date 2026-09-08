# L07 — Research Plan

**Candidate:** Official Correction ≠ Current Scholarly Claim

---

## 0. Phase zero — data audit before any model run

This is mandatory.

### Goal
Determine whether official correction notices yield enough direct proposition-level old→new gold.

### Procedure
1. collect ~500 linked PMC/PubMed corrections;
2. parse exact replacement patterns;
3. verify a stratified sample;
4. report usable Tier 1/2 yield;
5. estimate final dataset scale.

### Promotion threshold
Do not use a hard arbitrary percentage as a scientific gate.

Promote if the absolute count and diversity support:
- a decisive pilot;
- multiple correction types;
- a credible Main-scale expansion.

If the usable set is only a tiny, homogeneous handful of lexical edits, kill.

## 1. Minimum decisive model pilot

### Data
~150–300 high-confidence old→new pairs.

Balance:
- numbers;
- methods;
- qualifiers;
- prose claims;
- table/figure facts when extractable.

### Conditions
- original only;
- original + correction flat;
- explicit X→Y update representation.

### Models
Two strong model families; one open model preferred for later mechanistic analysis if needed.

### Primary estimand
> probability of returning the **current** proposition Y rather than historical X.

## 2. Outcome routes

### Route A — Flat reading is sufficient
Original+correction ≈ explicit update across correction types.

Conclusion:
> official notices provide enough natural signal for current-state scientific QA without explicit state machinery under validated conditions.

### Route B — Explicit update is necessary
Flat aggregation repeats/blends X substantially more than structured update.

Conclusion:
> corrected scholarship cannot be modeled as a flat document set.

### Route C — Boundary
Simple local replacements are handled; diffuse/table/figure/method changes are not.

Conclusion:
> use direct reading for simple updates and explicit state for complex updates.

## 3. Causal/diagnostic manipulations

To separate semantics from superficial recency:

- reverse document order;
- remove update labels while keeping text;
- retain update label but paraphrase the notice;
- include a newer unrelated conflicting paper;
- include correction plus distractor conflicting evidence.

Key question:
> does the model understand **official supersession**, or merely favor the most recent/last text?

## 4. Phase 2 — Task generality

Run the same correction relation through:
- QA;
- structured IE;
- summarization;
- citation-grounded answer generation.

The paper is stronger if the same current-state failure appears across tasks.

## 5. Phase 3 — Consequence for retrieval/indexing

Compare:
1. flat RAG index containing original + correction;
2. retrieval with update-aware metadata;
3. proposition-state index where X is marked superseded.

This is C3, not the primary novelty.

## 6. Planned C1 → C2 → C3

### C1
Can models recover the corrected/current proposition from natural official updates?

### C2
What determines success?
- explicit update relation;
- locality;
- type;
- document order/salience;
- modality.

### C3
Should scholarly NLP represent correction/supersession explicitly?

## 7. Kill conditions after pilot

KILL if:
- exact corrections are so explicit that every competent model copies Y with ceiling performance and no meaningful boundary;
- only obscure OCR/table extraction causes errors;
- direct collision is found;
- update-aware modeling never changes any scientific QA/IE conclusion;
- the usable dataset is too small or homogeneous.

## 8. Main-level expansion requirements

Before mainline approval require:
- substantial natural scale;
- multiple publishers/journals;
- more than one correction type;
- clear distinction from ordinary temporal conflict;
- a direct modeling/evaluation consequence;
- simple plain-language identity preserved.

## 9. Pre-mainline checklist

- [ ] Document-level links are official.
- [ ] Old→new gold is publisher-authored/deterministic.
- [ ] Metadata-only corrections excluded from decisive set.
- [ ] Flat vs explicit update compared.
- [ ] Recency/order confound controlled.
- [ ] At least two NLP tasks or one strong task plus a system consequence.
- [ ] Preservation result is meaningful.
- [ ] Reviewer compression “temporal QA over errata” is demonstrably false.

## Final pilot verdict

**RUN DATA-YIELD AUDIT NOW. Pilot-authorize only if the gold yield is sufficient.**
