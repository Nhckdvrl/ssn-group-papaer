# L03 — Research Plan and Development Roadmap

**Goal:** determine whether typed observation status is a necessary representation for real-world statistical TableQA, or whether document-conditioned generation can safely absorb that layer.

---

## Phase 0 — Lock the ACS data contract

1. Query a fixed ACS release.
2. Enumerate estimate/annotation variable pairs.
3. reproduce official sentinel→annotation mappings;
4. measure the frequency of each usable status;
5. construct deterministic typed gold;
6. build table snippets with the exact local documentation needed to interpret them.

**Exit condition:** enough independently labeled VALUE and non-VALUE cases exist for a balanced pilot.

---

## Phase 1 — Minimum decisive pilot

### Conditions

1. **Ordinary direct answer**
   - ask the natural question over the table/documentation.
2. **Structured typed observation**
   - require status first, value only if defined.
3. **Two-stage factorization**
   - determine observation status;
   - recover value conditional on VALUE.
4. **Documentation ablation**
   - local legend/docs present vs absent.

### Models

Use a small set of strong current systems with different training families.

Do not use dozens of models to compensate for a weak scientific design.

### Primary estimands

- false scalarization;
- typed-status accuracy;
- direct vs factorized performance;
- documentation dependence;
- conventional answer score versus typed-observation score.

---

## Phase 2 — Outcome decision

### Promote signal A — direct generation is sufficient

Evidence:
- models infer status from documentation;
- performance transfers beyond memorized ACS patterns;
- explicit typing adds little;
- scalar/value answering is not semantically corrupted.

Scientific conclusion:
> long-context document conditioning can safely replace an explicit status parser under specified conditions.

### Promote signal B — explicit typing remains load-bearing

Evidence:
- direct answers copy sentinel values or collapse statuses;
- structured status→value factorization fixes errors;
- failure persists despite documentation;
- errors are not just OCR/formatting mistakes.

Scientific conclusion:
> value-centric TableQA is structurally mis-specified for status-bearing statistical cells.

### Promote signal C — identifiable boundary

Evidence:
- direct generation is safe for simple/familiar states;
- explicit typing is needed for suppression, reliability, qualification, or unfamiliar provider conventions.

Scientific conclusion:
> provider/status complexity determines when typed observation modeling is required.

### Kill

KILL if:
- all usable cases are trivial symbol lookup;
- all strong models are at ceiling and transfer adds no scientific information;
- status cases are too sparse;
- the only result is a benchmark-specific accuracy difference;
- a direct paper-level collision is found.

---

## Phase 3 — C1: establish typed-observation validity

Compare conventional answer evaluation against typed-observation evaluation.

Questions:
- does a value-only output space mis-score official semantics?
- do models preserve the difference between zero, unavailable, not applicable, suppressed, and qualified states?
- does ordinary direct generation already solve this without explicit state?

Use paired confidence intervals and equivalence/non-inferiority tests for preservation claims.

---

## Phase 4 — C2: identify why / where

Priority axes:

1. **Documentation access**
   - absent vs present.
2. **Provider familiarity**
   - familiar vs unseen.
3. **Status family**
   - not-applicable/unavailable vs suppressed/reliability/qualified.
4. **Surface realization**
   - numeric sentinel, symbol, blank, text annotation.
5. **Representation**
   - direct answer vs typed object vs two-stage status→value.

Do not drift into generic table reasoning categories unless they explain the status result.

---

## Phase 5 — C3: task-definition consequence

The paper must finish by answering:

> What should a real-world TableQA system be asked to output?

Potential consequences:
- typed observation objects should replace scalar/string-only targets for official statistical data;
- explicit status parsers are no longer needed when documentation-conditioned generation passes transfer tests;
- hybrid systems should activate explicit typing only for identified source/status regimes;
- evaluation should distinguish wrong scalarization from ordinary value errors.

This is the Main-level consequence. Ranking reversal is strong evidence but not mandatory.

---

## Phase 6 — Cross-provider replication

Before mainline approval:

1. secure a second official source with exact status gold;
2. freeze its provider-defined mapping without author relabeling;
3. evaluate zero-shot or minimal-adaptation transfer;
4. test whether the same direct-vs-typed conclusion survives.

CDC/NCHS is currently the leading replication family but is **not counted as verified load-bearing gold yet**.

---

## Paper skeleton

### Introduction
- official tables sometimes encode states, not values;
- modern LLMs may reconstruct local ontologies dynamically;
- explicit typing may be obsolete or necessary.

### Section 2 — Related work
- real-world TableQA;
- irregular/missing tables;
- data-referencing errors;
- precise typed-observation gap.

### Section 3 — Official data and semantics
- ACS;
- typed gold;
- natural document rendering.

### Section 4 — C1
- direct generation vs typed observation.

### Section 5 — C2
- documentation, provider, status, representation boundaries.

### Section 6 — C3
- corrected task/evaluation formulation.

### Section 7 — Cross-provider replication

---

## Promotion checklist to paper mainline

- [ ] ACS mapping and frequencies reproduced.
- [ ] Natural table/document rendering validated.
- [ ] Direct vs typed comparison is stable.
- [ ] Preservation/failure/boundary result has a substantive interpretation.
- [ ] Result is not sentinel memorization.
- [ ] At least one second provider has exact independent gold.
- [ ] Fresh 2024–2026 novelty audit still survives.
- [ ] C3 changes a real TableQA output/evaluation assumption.
- [ ] Reviewer compression cannot reduce the paper to missing-value TableQA.
