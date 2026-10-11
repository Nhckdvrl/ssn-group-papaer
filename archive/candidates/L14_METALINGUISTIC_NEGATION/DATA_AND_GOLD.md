# L14 — Data and Gold Contract

**Date:** 2026-09-11  
**Rule:** no LLM-generated main data and no LLM-created load-bearing gold.

## 1. Scientific unit

The independent unit is a **human-audited lexical/discourse base** that supports matched descriptive-negation (DN), metalinguistic-negation (MN), and non-negated controls.

The target is not the label `MN` itself. The load-bearing outcome is a simple proposition about the described world.

Example:

- DN: `The movie wasn't good — it was terrible.`
- MN: `The movie wasn't good — it was excellent.`
- positive control: `The movie was excellent.`
- target: `The movie was at least good.`

Gold:
- DN → NO;
- MN → YES;
- positive control → YES.

This allows evaluation of whether the same surface cue `not` produces the correct **world-state commitment** under different targets.

---

## 2. Human experimental seed

Use the classical literature as a stimulus-design and validation source, not as an automatically translated benchmark.

Primary seed:
- Blochowiak & Grisot (2018), *The pragmatics of descriptive and metalinguistic negation: experimental data from French*.
- Public Experiment 1/2 data and metadata are available through SWISSUbase.

Sources:
- https://doi.org/10.5334/gjgl.440
- https://www.swissubase.ch/en/catalogue/studies/13418/latest/datasets/1022/1629
- https://www.swissubase.ch/en/catalogue/studies/13418/latest/datasets/1023/1630/overview

Noh et al. (2013) supplies an independent psycholinguistic processing design in Korean:
- https://doi.org/10.1016/j.pragma.2013.07.005

These sources establish that DN/MN and the context manipulation are real human experimental objects. They do **not** by themselves provide English load-bearing gold.

---

## 3. Pilot stimulus budget

Target **40–60 human-audited bases**. Do not scale before the pilot decision.

Each base should instantiate at least:

1. **POS** — direct positive/stronger state, no negation;
2. **DN** — ordinary descriptive negation with a continuation that fixes the weaker target as false;
3. **MN** — metalinguistic correction with a continuation that fixes the weaker world proposition as true;
4. **PARAPHRASE CONTROL** — non-negated or explicitly metalinguistic paraphrase that tests whether the model knows the lexical/world relation independently of `not`.

For C2-capable bases, additionally prepare:

5. **PRE-MN CONTEXT** — discourse context makes a corrective/metalinguistic reading available before `not X`;
6. **PRE-DN CONTEXT** — matched context supports ordinary world-state denial.

The first pilot need not run all six forms if the first four already kill the route.

---

## 4. Subtype composition

The pilot must not be driven by one pragmatic family.

### Primary subtype A — lexical-strength correction

Examples like `good → excellent`, `like → love`, where the correction is stronger and independently preserves the weaker world-state proposition.

Requirements:
- human judges agree that Y entails or clearly licenses X in the intended context;
- avoid scales with weak/controversial entailment;
- include non-negated paraphrase controls.

### Primary subtype B — clearly linguistic/form correction

Corrections of wording, morphology, pronunciation/label/register where the discourse makes clear that the world fact itself is not being denied.

Purpose:
- demonstrate that the phenomenon is not merely scalar implicature cancellation;
- test whether a literal polarity operation leaks into an explicitly linguistic correction.

These items require especially careful QA so that the downstream world-state question remains meaningful and unique.

### Secondary / diagnostic only — scalar quantifier cases

Examples such as `some → all` may be included only as a small diagnostic slice.

They are **not load-bearing** because ImplicatureX (Spinoso-Di Piano et al., 2026) already studies scalar/conversational implicature cancellation and belief updates:
- https://arxiv.org/abs/2607.25094

If the effect exists only here, kill/reconstruct rather than claiming L14.

---

## 5. Human validation contract

Before any paper-level claim, every critical base must be validated by humans for three separate quantities:

1. **Naturalness** — the DN and MN utterances are acceptable English in the intended discourse;
2. **Intended target** — judges agree whether the `not` is naturally understood as world-state denial or linguistic/metalinguistic rejection;
3. **World-state gold** — judges agree on the truth/commitment of the target proposition after the full utterance.

Do not infer gold from the authors' intended label alone.

For the bounded discovery pilot, a manually audited draft may be used only to decide whether further investment is warranted; such results remain exploratory until independent human validation is complete.

No LLM judge may supply the load-bearing truth labels.

---

## 6. Prompt/output contract

Use a proposition-level forced choice rather than asking the model to label `metalinguistic negation`.

Preferred probe:

> Based only on what the speaker means in the dialogue, is the target statement true?  
> Answer with one option only: YES / NO.

Where useful for ambiguity controls, add `NOT DETERMINED`, but do not introduce it unless the item set genuinely contains unresolved cases.

For open-weight scoring, permute neutral option codes / label order and score label probability mass to prevent a fixed-token artifact.

The model is never taught the terms DN/MN in the baseline condition.

---

## 7. Identification controls

A base is invalid if any of these fail:

- POS/PARAPHRASE control shows the model does not know the relevant lexical/world relation;
- DN and MN differ in unrelated entities/events or world knowledge;
- MN can be answered only by memorizing a phrase template;
- the target proposition changes between matched conditions;
- a scalar pair is debatable enough that the YES label depends on author intuition;
- the continuation directly repeats the target answer in an unnatural way.

Primary analyses are paired within base.

---

## 8. Data kill conditions

Kill or redesign before model expansion if:

- fewer than ~40 clean bases survive human audit;
- intended DN/MN readings are unstable;
- world-state targets cannot be made independently clear without making the task trivial;
- only scalar-implicature cases are clean;
- lexical/form controls explain the entire model difference;
- the English construction is so marked that failures reduce to unnatural-stimulus handling.

---

## 9. Current data verdict

**DATA PATH: PASS FOR BOUNDED PILOT DESIGN, NOT YET PAPER-LEVEL GOLD.**

The classical experiments make the object and context manipulation credible. The remaining blocking data task is to produce and independently validate a compact English matched set without relying on LLM-generated main stimuli or labels.
