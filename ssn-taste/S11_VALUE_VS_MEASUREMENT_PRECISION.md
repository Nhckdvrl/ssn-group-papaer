# S11 — Same Number, Different Information: Value vs Measurement Precision

**Status:** CANCELLED — CURRENT THRESHOLD DESIGN KILLED AFTER E03 (mother question unresolved)  
**Registered:** 2026-09-21  
**Target venues:** ACL / EMNLP / NAACL Main  
**Scientific type:** numerical semantics / selective invariance / scientific language understanding

## Parent question

When two numerical expressions denote the same central value but carry different measurement precision — for example, `2.0 m` versus `2.00 m` — does a language model preserve the distinction between **what value is being reported** and **how precisely that value is known/reported**?

A stronger formulation is:

> **Does an LM know when numerical formatting should be ignored and when numerical formatting is itself information?**

The project is not a significant-figures quiz and not a generic numeracy benchmark. The scientific object is **selective invariance**: numerical form should be ignored when it is merely an alternative notation for the same value, but preserved when it changes the epistemic content of a measurement.

## Why this is worth knowing

Recent work on numerical representations in LMs has emphasized increasingly format-invariant representations of number magnitude. This is desirable for nuisance variants such as `1729` versus `1,729`, or decimal versus scientific notation when both carry the same information.

But scientific measurements create a boundary case where value invariance alone is wrong.

Under standard measurement conventions, `2.0 m` and `2.00 m` share the same central value while reporting different precision. Metrology treats measurement uncertainty/precision as information distinct from numerical value; significant digits are one conventional way in which that information can be expressed.

So a representation that collapses every numerically equivalent string to one value may be excellent for arithmetic and still lose information required for scientific communication.

This creates a simple scientific pressure:

> **Can LMs separate a representation's value-invariant component from its epistemic-precision component, or do they collapse the two?**

## Scientific pressure

Three nearby literatures establish the ingredients without answering the parent question.

1. **Numerical representation.** Recent ACL/EACL work studies whether LMs encode number magnitude systematically and whether equivalent numerical formats map to common representations.
2. **Numerical-format robustness.** Recent work shows that scripts and formatting can change arithmetic performance even when mathematical value is unchanged; those format differences are treated as nuisance variation.
3. **Measurement reasoning.** Earlier NLP work studies quantities, units, scales and reference ranges, but does not ask whether same-value strings with different reporting precision remain epistemically distinct.

The missing boundary is precisely where "format invariance" should stop being desirable.

## Knowledge-delta statement

**Prior knows:** LMs encode numerical magnitude, are sensitive to numeral formats, and can reason to some extent about quantities and units.

**Still unknown:** whether they disentangle **central numerical value** from **measurement precision** when surface form is sometimes nuisance and sometimes semantically load-bearing.

**Our experiment separates:**

- a **value-collapse world**, where equivalent values are treated the same even when precision should matter;
- a **surface-sensitive world**, where formatting affects behavior even when it should not;
- a **selective-invariance world**, where the model is invariant to notation but sensitive to epistemic precision only in measurement contexts.

## Main possible worlds

### World A — value collapse

The model normalizes `2.0` and `2.00` to essentially the same numerical object.

Predictions:
- good invariance on pure value tasks;
- failure to use precision differences in measurement decisions;
- information-preserving rewrites/conversions tend to drop significant precision distinctions.

This would show that successful magnitude representation can erase scientifically meaningful metadata.

### World B — generic surface sensitivity

The model reacts to extra digits/notation changes even when they are mathematically or semantically irrelevant.

Predictions:
- precision-sensitive behavior may appear in measurement tasks;
- but the same formatting differences also perturb pure equality/value tasks where they should not.

This would imply that apparent precision awareness is not a clean epistemic distinction; it is surface-form dependence.

### World C — selective invariance

The model treats notation changes as irrelevant when only value matters, while preserving precision differences when the context establishes a measurement.

Predictions:
- `2.0 = 2.00` for pure mathematical value;
- `2.0 m` and `2.00 m` support different precision-sensitive downstream decisions;
- equivalent notations that preserve both value and precision behave alike.

This would show that LMs represent/use a numerical quantity along at least two functionally separable dimensions: value and reported precision.

## Nearest-prior boundary

### Park et al. — Do Language Models Understand Measurements? (EMNLP Findings 2022)

This work studies measurement reasoning over numbers and units, including scale/reference-range style tasks. It does not make same-value/different-precision expressions the scientific object, nor test whether value invariance and precision sensitivity are selectively separated.

### Yuchi et al. — LLMs Know More About Numbers than They Can Say (EACL 2026)

This work studies latent magnitude/ranking representations across numerical notation. Its object is **how much number magnitude is encoded**, not whether equal magnitudes can carry distinct epistemic precision.

### Štefánik et al. — Language Models Learn Universal Representations of Numbers and Here’s Why You Should Care (ACL 2026)

This work finds highly systematic and broadly interchangeable number representations across model families. S11 does not challenge value invariance itself; it asks for its **semantic boundary**: some same-value surface distinctions are intentionally informative.

### Reddy et al. — 1,729 vs. 1729: The Effect of Scripts and Formats on LLM Numeracy (ACL Findings 2026)

This work treats format variation as a robustness problem under unchanged mathematical content. S11 instead contrasts nuisance format changes with **information-bearing precision changes** under the same central value.

### Numerical approximation / pragmatic precision work

Work on "around 8:30", contextual rounding, and verbal uncertainty studies when speakers choose more or less precise expressions. S11 studies a different object: whether an already given numerical measurement retains its precision as part of the information state.

## Minimum decisive pilot

Use a tiny programmatic factorial experiment. No training, probe, LLM judge, or annotation is required.

### Factor 1 — epistemic precision

Hold the central value fixed while varying reported precision, e.g.:

- `2.0 m`
- `2.00 m`

Use many values/orders of magnitude so the result cannot depend on one memorized item.

### Factor 2 — notation

Express the same value and same precision in alternative notations, e.g.:

- `2.00 m`
- `2.00 × 10^0 m`

These should be behaviorally equivalent if notation itself is nuisance.

### Factor 3 — context

Use two contexts:

1. **Pure-value context**: only mathematical value matters.  
   Expected behavior: formatting/precision variants should collapse.

2. **Measurement context**: a device reports a measured quantity to its displayed resolution / last reported digit.  
   Expected behavior: `2.0` and `2.00` should support different uncertainty/precision-sensitive decisions.

### Direct readout A — value invariance

Forced-choice/equality items with exact scoring.

Question type:
- do two expressions denote the same mathematical value?

A semantically competent model should be invariant across notation and trailing-zero variants here.

### Direct readout B — precision-sensitive decision

Use a downstream threshold placed so that a coarse report cannot certify a decision while a finer report with the same central value can.

Example logic:
- coarse reading: `2.00` rounded to the last shown digit;
- fine reading: `2.000` rounded to the last shown digit;
- choose a threshold that lies outside the compatible interval of the fine reading but inside the coarse reading's interval.

Then ask a deterministic question such as whether the measurement is sufficient to certify the threshold condition.

The answer changes solely because reported precision changes, not because central value changes.

### Explicit-rule control

Include a condition where the rounding/display convention is spelled out explicitly.

This separates:
- failure to know the conventional meaning of significant digits;
- failure to reason with precision even when the semantics are explicit.

The implicit scientific-reporting condition is the main test; the explicit condition is diagnostic.

## Why the pilot is direct

The manipulated scientific variable is **whether a same-valued numerical expression carries more or less measurement precision**.

The first experiment directly asks whether this information changes downstream inference only when it should.

It does not require:
- hidden-state probes;
- mechanistic components;
- new benchmarks;
- human annotation;
- training;
- a model zoo;
- LLM-as-judge scoring.

All ground truth is analytic.

## Execution discipline

Start with one strong open instruct model and tens to low hundreds of items.

Vary:
- several central values;
- several decimal positions/orders of magnitude;
- 2–4 SI units;
- decimal versus scientific notation.

Do not initially expand to:
- arbitrary uncertainty notation;
- confidence intervals;
- medical risk;
- large scientific QA collections;
- broad arithmetic benchmarks;
- many model families.

One second model family is a robustness check only after the first pilot gives a clean qualitative result.

## Kill conditions

Kill S11 if any of the following occurs:

1. A nearest prior is found that already performs the same **value-invariance vs measurement-precision sensitivity** contrast under matched same-value expressions.
2. The distinction cannot be made well-defined without teaching each item a long metrology rule, so the project collapses into instruction following.
3. Performance is explainable entirely by memorized textbook significant-figure procedures and does not survive the value-vs-measurement context contrast.
4. The only interesting result requires hidden-state probing or mechanistic analysis; the behavioral distinction itself is weak.
5. The project expands into a broad numeracy/science benchmark rather than answering selective invariance.
6. Robust results require many domains/model families/prompts to become interpretable.

## Claim boundary

Do not claim that significant figures are a complete representation of measurement uncertainty.

The defensible claim is narrower:

> **Numerically equal expressions can differ in epistemic precision, and S11 tests whether language models preserve that distinction selectively rather than either collapsing all formats to value or reacting indiscriminately to surface form.**

## Final pilot adjudication — 2026-09-26

E01–E03 were executed and the registered threshold route is **KILLED**.

E01 showed:
- pure-value invariance: 100/100;
- notation nuisance: 98/100 explicit, 100/100 natural;
- explicit measurement threshold: 58/200;
- natural measurement threshold: 100/200.

E02 independently replicated a strong direction-dependent failure under the same explicit rule.

E03 then supplied the compatible true-value interval directly on a fresh held-out batch. The key analytic correctness counts were:

| Evidence | Greater coarse | Greater fine | Less coarse | Less fine |
|---|---:|---:|---:|---:|
| Rounded report | 0/40 | 40/40 | 4/40 | 2/40 |
| Explicit interval | 16/40 | 40/40 | 40/40 | 40/40 |

Thus directly providing the interval repaired the less-than arm but did not make greater-than universal certification stable. The downstream readout itself therefore fails in at least one direction and cannot serve as a clean instrument for the selective-invariance mother question.

**Verdict:** KILL current S11 threshold route. The broader value-vs-measurement-precision mother question remains unadjudicated.

Do not revive by:
- further strengthening or rewriting the threshold question;
- adding CoT/few-shot scaffolding;
- adding model families before a valid instrument exists;
- interpreting the inequality-direction asymmetry as the paper;
- moving directly to hidden-state or mechanistic analysis.

Any future revival requires an independently motivated new instrument that measures whether equal-valued expressions preserve measurement precision without depending on unstable interval-threshold certification.

See `experiments/S11_E03/RESEARCH_LOG.md` and commit `9de6d60`.

## Promotion status

**CANCELLED from current selection.**

S11 survives because:
- the why-care is understandable without specialist linguistic terminology;
- the parent is undercrowded relative to current reasoning/agent/RL lines;
- nearest priors study magnitude, formatting or measurement reasoning but not the same decisive unknown;
- the question does not depend on observing a new anomaly;
- a tiny programmatic behavioral experiment directly separates three scientific worlds;
- the data path and scoring are exact;
- no training recipe, evaluator, probe or benchmark construction is required before the scientific question is answered.
