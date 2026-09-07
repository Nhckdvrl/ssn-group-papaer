# L02 — Data and Independent Gold

**Core rule:** the experiment must never depend on author-invented labels for whether a missing role has a specific referent.

---

## 1. Primary decisive substrate

### SemEval-2010 Task 10 — Linking Events and Their Participants in Discourse

Paper:
https://aclanthology.org/S10-1008/

Why it is valuable:
- running-text discourse rather than synthetic worlds;
- pre-LLM annotation;
- explicit null-instantiation distinctions;
- many definite omissions include links to concrete discourse fillers;
- the original task itself separates detection/status/resolution stages.

Current repository audit records the following published corpus statistics:

- train: 438 sentences, 303 DNI, 277 INI, 245 resolved DNI;
- test: 525 sentences, 349 DNI, 361 INI, 259 resolved DNI.

These numbers should be programmatically re-verified against the released task data before final experiment scripts are frozen.

---

## 2. Gold quantities needed

For each target omitted role, derive only quantities explicitly supported by corpus annotation.

### Referential status

- SPECIFIC_REFERENT
- NON_SPECIFIC

The mapping must be deterministic from the task’s null-instantiation annotation, not manually inferred from text.

### Filler identity

For SPECIFIC_REFERENT cases with released links:
- gold discourse span / entity filler.

For NON_SPECIFIC:
- no filler should be required or credited.

### Role/type

Use the corpus frame / role labels only as an independent diagnostic of whether the model understood the semantic slot even when referential commitment is wrong.

---

## 3. Required experimental record

Construct one machine-readable unit per target with at least:

- document ID;
- target predicate;
- frame;
- role;
- null status;
- gold filler span(s), if any;
- full usable context;
- discourse-distance metadata;
- source split.

Do not add theory-heavy labels unless they are optional analysis variables and are not load-bearing gold.

---

## 4. FrameNet as scale / replication

FrameNet is a natural extension because null-instantiated frame elements are part of the resource design.

Use it only after verifying:
- exact release fields;
- whether the relevant DNI/INI-like annotations are extractable at scale;
- whether sufficient discourse context is available for filler resolution;
- whether annotation conventions match the SemEval mapping closely enough for replication.

FrameNet must not be invoked with vague language such as “after verifying.” If exact extraction is not established, it is not part of the decisive evidence package.

---

## 5. Sampling plan

The minimum pilot should be stratified rather than simply random.

Required strata:
- specific/recoverable omissions;
- non-specific omissions.

Useful pre-specified analysis strata:
- discourse distance to filler;
- predicate/frame;
- presence of salient but incorrect candidate entities;
- local versus broader discourse evidence;
- frequency / annotation density where recoverable.

Avoid selecting cases based on model failure.

---

## 6. Output formulations

### Direct generation

Model receives context and target role and must return either:
- a specific filler;
- an explicit non-specific / no-specific-referent response.

### Explicit factorization

Stage 1:
> Does this omitted role refer to a particular discourse entity?

Stage 2 only when Stage 1 = yes:
> Which entity?

### Independent role probe

Ask for the semantic role/type without demanding an entity. This is diagnostic only; it allows the paper to separate:
- failure to understand the role;
- failure to judge referential status;
- failure to resolve the correct filler.

---

## 7. Primary metrics

Pre-specify:

- referential-status accuracy / macro-F1;
- non-specific overcommitment rate;
- filler resolution accuracy conditional on SPECIFIC_REFERENT;
- role/type accuracy;
- filler-generation rate conditional on correct role knowledge;
- direct vs factorized change in status and filler errors;
- calibration / abstention metrics only if they do not replace the central estimand.

Do not let generic answer accuracy become the headline metric.

---

## 8. Data validity kill conditions

KILL or demote if:

- the released labels cannot cleanly determine the needed status;
- filler links are too sparse or ambiguous for the decisive comparison;
- corpus size/domain makes estimates unstable and no credible replication is available;
- FrameNet replication requires substantial author re-annotation;
- evaluation requires subjective decisions about whether an invented entity is “plausible enough.”

The gold must force the action independently of the model.
