# L04 — Research Plan and Development Roadmap

**Goal:** test whether canonical one-target morphological inflection is an empirically valid measurement simplification once zero/one/many realization cardinality is restored.

---

## Phase 0 — Data audit before any GPU

1. Pin the Eesthetic release.
2. Parse the forms, lexeme, cell, and tag tables.
3. reproduce published resource counts;
4. construct lexeme×cell groups;
5. conservatively classify NO/ONE/MULTIPLE;
6. audit duplicate rows and all relevant tags;
7. quantify usable sample sizes.

**Hard stop:** if the data do not yield a clean, adequately sized 0/1/many substrate, KILL before modeling.

---

## Phase 1 — Minimum decisive pilot

### Systems

Use:
- one conventional morphological inflection baseline where feasible;
- a small set of strong current generative models;
- do not over-invest in model breadth.

### Output conditions

1. **Canonical single-form generation**
2. **Direct relation-aware generation**
   - NO_FORM;
   - one form;
   - set of forms.
3. **Explicit cardinality→forms factorization**
   - first predict cardinality;
   - then generate form(s) only when licensed.

### Primary comparisons

- canonical score vs relation-aware score;
- cardinality error vs realization error;
- model ranking agreement;
- explicit factorization effect;
- per-regime conclusion agreement.

---

## Phase 2 — Decide whether the paper exists

### Promote signal A — canonicalization is unsafe

Evidence:
- canonical scores systematically hide NO/MULTIPLE errors;
- relation-aware scoring changes model ranking or generalization interpretation;
- factorization specifically improves noncanonical cells;
- effect is stable enough to matter scientifically.

Conclusion:
> single-target evaluation hides a separate realization-cardinality problem.

### Promote signal B — canonicalization is safe

Evidence:
- strong systems preserve 0/1/many relations;
- canonical and relation-aware conclusions are equivalent within pre-specified margins;
- result holds across enough noncanonical cells and at least one replication setting.

Conclusion:
> despite known noncanonical morphology, one-target evaluation is empirically valid under specified regimes.

### Promote signal C — conditional validity

Evidence:
- canonicalization is safe for some paradigm/frequency/classes but not others.

Conclusion:
> the field can state explicit boundaries for when conventional evaluation is valid.

### Kill

KILL if:
- only rare-item error counts differ;
- no scientific/model conclusion changes and preservation cannot be established with adequate power;
- one model drives the result;
- the story reduces to “models miss Estonian variants”;
- Bouton & Bonami-style paradigm predictability already explains the entire contribution;
- a direct model-evaluation collision is found.

---

## Phase 3 — C1: measurement-validity test

The headline is not raw performance. It is:

> **Does canonical evaluation preserve the conclusions drawn from the same systems under realization-aware gold?**

Pre-specify:
- model-ranking agreement;
- generalization-gap agreement;
- conclusion thresholds;
- equivalence margins where appropriate.

For null/preservation claims, do not use failure to reject significance as evidence of equivalence.

---

## Phase 4 — C2: explain the boundary

Priority decomposition:

1. **Existence vs realization**
   - does the system fail to know whether a form should exist, or only how to spell/realize it?
2. **Defectivity class**
3. **Overabundance class**
4. **Inflection class**
5. **Frequency / attestation**
6. **Cell frequency**
7. **Direct vs explicit factorization**

Avoid adding deep linguistic theory unless it directly explains a robust computational boundary.

---

## Phase 5 — C3: consequence for computational morphology

Possible outcomes:

### If unsafe
- redefine evaluation to support zero/one/many output;
- report cardinality separately from form realization;
- avoid treating canonical accuracy as complete paradigm knowledge.

### If safe
- validate the current canonical simplification;
- state the regimes and empirical margins under which one target is enough.

### If conditional
- recommend a hybrid evaluation protocol for noncanonical paradigm classes.

The consequence must alter an established interpretation or evaluation practice.

---

## Phase 6 — Replication / generality

Only after the pilot has leverage:

1. secure a second exact-gold resource;
2. reproduce the 0/1/many mapping independently;
3. repeat the measurement-validity test;
4. test whether the same preservation/unsafe/boundary conclusion holds.

Do not expand to many languages before the core paper identity is secured.

---

## Paper skeleton

### Introduction
- one target is a historical benchmark simplification;
- real morphology permits zero/one/many;
- both “safe simplification” and “measurement distortion” are plausible.

### Section 2 — Ownership and novelty
- defectivity/overabundance;
- paradigm completion;
- TACL canonicalization;
- Eesthetic/Paralex;
- 2026 overabundance predictability.

### Section 3 — Relation-aware gold
- deterministic extraction;
- canonical comparison.

### Section 4 — C1
- preservation versus change in conclusions.

### Section 5 — C2
- which morphological regimes drive the result?

### Section 6 — C3
- what should computational inflection measure?

### Section 7 — replication

---

## Promotion checklist to paper mainline

- [ ] Eesthetic 0/1/many counts reproduced.
- [ ] DEF vs MISSING and duplicate-row semantics audited.
- [ ] Canonical comparison is non-arbitrary.
- [ ] Pilot has enough noncanonical leverage.
- [ ] Preservation/change/boundary conclusion is statistically supported.
- [ ] Result is about measurement, not rare Estonian errors.
- [ ] Direct-vs-factorized comparison adds interpretation.
- [ ] Fresh novelty audit survives TACL 2022 and Bouton & Bonami 2026.
- [ ] C3 changes a real computational-morphology conclusion.
- [ ] Preferably, a second independent resource replicates the result.
