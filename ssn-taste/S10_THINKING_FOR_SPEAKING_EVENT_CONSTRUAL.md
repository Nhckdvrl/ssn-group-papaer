# S10 — Thinking for Speaking in Multimodal Language Models

**Status:** KILLED — 2026-09-26 POOL-LEVEL POSTMORTEM
**Registered:** 2026-09-21

## Parent question

When a multilingual multimodal language model prepares to describe the same non-linguistic event in different languages, does the anticipated language change how the event is construed **before any description is produced**, or do language-specific differences arise only during verbalization?

The first pilot focuses on motion events because languages differ systematically in how they habitually package **Manner** and **Path**, and the human psycholinguistic literature has used this domain for decades to debate *thinking for speaking*.

This is not a generic multilingual robustness question and not a benchmark of whether a model can name Manner or Path.

## Why this is worth knowing

A central question in language-and-cognition research is whether language merely expresses an independently formed thought or whether preparing to speak selects and organizes aspects of an event in language-specific ways.

Human evidence is difficult to identify cleanly. Cross-linguistic comparisons change language together with culture, developmental history, and experience. Bilingual studies reduce but do not remove acquisition-history differences, and the motion-event literature contains conflicting results.

A multilingual multimodal model creates a newly useful scientific system: **the same agent can be switched between output languages while its weights, visual input, and training history remain fixed**. This permits a within-agent intervention that is unusually difficult in humans.

If anticipated output language changes a visual event judgment before any verbal description is generated, language-conditioned planning is not merely an output-style phenomenon. If it does not, then language-specific verbalization can remain downstream of a comparatively language-invariant event judgment.

Either result changes how we should interpret claims that multilingual models have internalized language-specific “ways of thinking.”

## Scientific pressure

Three bodies of evidence create the pressure:

1. Human motion-event research documents strong cross-linguistic differences in how Manner and Path are encoded, but disagrees on whether these differences alter non-verbal similarity or memory.
2. Human bilingual work reports that the language used to describe an event can shift subsequent Manner/Path judgments, motivating the thinking-for-speaking account.
3. Recent LLM work reports language-specific reasoning biases, but those experiments remain inside language: linguistic input is followed by linguistic reasoning/output. They do not isolate whether anticipated language changes the construal of a non-linguistic event.

The missing question is therefore not “does language matter?” but:

> **Does preparing to speak a particular language change a multimodal model's event decision before it has produced the language-specific description?**

## Main possible worlds

### World A — anticipatory language-conditioned construal

The model's Manner-vs-Path choice shifts with the language it is instructed to use **even when the choice must be emitted before the description**.

This would show that language-conditioned production planning can feed back into event selection before overt verbalization. In a system whose weights and visual input are fixed, the active language would behave as a transient computational context for construing the event.

### World B — verbalization-only effect

Language affects descriptions, and may affect a later judgment when the description appears first, but does **not** affect a choice emitted before the description.

This would support a layered account: multilingual models can reproduce language-specific packaging conventions without those conventions necessarily reorganizing the preceding event judgment. It would also place an important boundary on broad claims of “linguistic relativity in LLMs.”

### World C — no typologically aligned language effect

Descriptions themselves do not reliably reproduce the expected Manner/Path contrast, or choice effects are unstable / unrelated to the typology.

Then current models are not an adequate system for this identification, and the topic should be killed rather than rescued with more models or elaborate prompting.

## Nearest-prior boundary

### Human thinking-for-speaking literature

Prior human work already owns the question of whether motion-language typology affects non-verbal similarity/memory. It also owns the observation that verbalization can modulate Manner/Path judgments.

S10 does **not** claim that thinking for speaking is a new cognitive hypothesis.

The new opportunity is the **within-model intervention**: a single multilingual multimodal model can be assigned different anticipated output languages while holding the agent, visual input, and training history fixed.

### Under the Shadow of Babel / LLM linguistic relativity

Recent work shows that bilingual linguistic inputs can induce language-specific causal-reasoning preferences and attention patterns in LLMs.

Prior knows:

> language choice can correlate with or induce different behavior inside a linguistic reasoning task.

Still unknown:

> whether the language a multimodal model is preparing to speak changes its construal of a previously observed non-linguistic event **before verbal output exists**.

### Multilingual VLM/VLA robustness

Recent multilingual multimodal work shows performance differences under translated instructions.

Those papers ask whether models remain robust across instruction languages. S10 instead holds the visual event and decision task fixed and uses **anticipated output language + output order** as an identification intervention on event construal.

## Minimum decisive pilot

Use small controlled motion-event triads inspired by the classical psycholinguistic paradigm.

Each item contains:

- a target event with Manner M1 and Path P1;
- alternate A: same Manner M1, different Path P2;
- alternate B: different Manner M2, same Path P1.

Randomize A/B placement and balance Manner/Path values.

The crucial factorial manipulation is:

1. **Choice → Description**
   - Tell the model it will describe the target naturally in language L.
   - Require the first output token/field to be the A/B similarity choice.
   - Only after that choice may it produce the description in language L.

2. **Description → Choice**
   - Require the language-L description first.
   - Then require the A/B similarity choice.

Run at least two typologically contrasting languages in the pilot, initially English plus Spanish or Japanese.

Primary quantities:

- language effect on Manner-vs-Path choice in **Choice → Description**;
- language × output-order interaction;
- manipulation check: whether descriptions actually differ in Manner/Path packaging in the expected direction.

The decisive result is the first quantity. The description-first condition diagnoses the easier language-as-strategy / self-generated-text route.

## Why the first experiment is direct

The pilot does not require:

- a probe;
- an SAE/vector/circuit;
- a new evaluator;
- a learned metric;
- human annotation;
- model training;
- a model zoo.

The stimuli can be simple programmatic animations. Their role is solely to orthogonalize Manner and Path with known ground truth.

The key causal variable is assigned output language, and the key identification intervention is whether the non-verbal choice occurs before or after language-specific verbalization.

## Critical controls

Keep these minimal and interpretation-driven:

- A/B side randomization.
- Same visual stimuli and same decision wording across language conditions as far as possible.
- A neutral/no-description condition for baseline Manner/Path preference.
- Verify that the tested model is competent in both languages and that language-L descriptions exhibit the intended packaging contrast.
- Use exact-match structured choice output so scoring is deterministic.

Do not expand into a broad multilingual benchmark.

## Execution reality

A pilot can use tens to low hundreds of procedurally generated 2D motion clips and 1–2 strong open multimodal models. No training is required.

If the basic manipulation works, robustness can later add one additional model family and one additional language contrast. This should not become a model-zoo paper.

## Kill conditions

Kill S10 if any of the following holds:

1. A nearest prior is found that already performs the same within-model anticipated-language × pre/post-verbalization intervention on non-linguistic event judgments.
2. Models fail the basic language-specific Manner/Path description manipulation, making the scientific contrast uninterpretable.
3. Any apparent Choice → Description effect disappears under trivial prompt/position controls or is dominated by A/B side bias.
4. The only robust effect occurs after the model has already produced the description; in that case the result compresses to ordinary self-conditioning / language-as-strategy and is not enough for the parent claim.
5. Establishing the claim requires hidden-state probing, custom representation metrics, or a large multimodal benchmark rather than the behavioral intervention.
6. The project collapses to “English model better than language X” or generic multilingual robustness.

## Claim boundary

Do **not** claim that a positive result proves human linguistic relativity.

The defensible claim is about multilingual multimodal models:

> switching the language the same model is preparing to speak does or does not causally alter its pre-verbal event construal under a controlled Manner/Path contrast.

Human psycholinguistics supplies the scientific question and experimental logic; the model supplies a new within-agent identification opportunity.


---

## 2026-09-26 pool-level final adjudication

**KILL.** This topic was cancelled as part of the full reset of the Sasano-taste pool. The failure is attributed to the selection process, not to a completed empirical falsification of the mother question. The old admission process overvalued clean conceptual dichotomies and hypothetical identifiability before requiring a naturally observed, stable phenomenon or contradiction that survives trivial formulations.

Do not treat this registration as a latent candidate. Any future related idea must re-enter from a new natural pressure under the revised canonical search guide, not by repairing this design.
