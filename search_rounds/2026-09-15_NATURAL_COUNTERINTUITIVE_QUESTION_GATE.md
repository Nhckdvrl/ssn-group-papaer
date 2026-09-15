# Natural / Counterintuitive Question Gate — 2026-09-15

## Why this correction is needed

Recent topic search improved ancestry, novelty, ownership, and identification discipline, but created a new failure mode: the *experimental identification* became cleaner than the *scientific question*. Candidates increasingly required several layers of setup before another researcher could understand why the question was interesting.

That is the wrong direction.

A strong Main-level question can be technically deep, but the depth should mostly live in the explanation and answer—not in the statement of the question itself.

This does **not** mean optimizing for pop-science appeal or questions that any outsider instantly finds exciting. The target listener is another strong NLP/ML/language-science researcher.

The desired reaction is:

> “That is strange. I would have expected the opposite / I genuinely do not know the answer.”

before hearing the method.

## The 10-second test

Before opening Selection, state only:

1. **one sentence question**;
2. **one sentence tension / counterintuitive fact**.

No method names. No probe. No benchmark. No special metric. No owner discussion. No three-stage theory reconstruction.

If a domain researcher still needs a long setup to understand why the question matters, the candidate is not yet natural enough.

## Three-layer separation

### Layer 1 — Question

Must stand alone.

Examples of the right shape:

- “Why can increasing beam size make translation catastrophically worse?”
- “Why can a model solve a problem during training and lose the solution later?”
- “Why can a stronger teacher produce a worse student?”
- “Why can more correct updated information make reasoning worse?”

These examples may already be owned; they are taste calibrators, not candidate suggestions.

### Layer 2 — Science

Only after the question survives Layer 1:

- old scientific ancestry;
- load-bearing assumption;
- rival explanations;
- consequence if either answer is true;
- direct ownership.

### Layer 3 — Identification

Only after Layers 1–2 survive:

- same-object / same-unit / same-observable tests;
- crossover / intervention;
- causal design;
- MDE / seeds / controls;
- pilot card.

A beautiful Layer-3 design cannot rescue an awkward Layer-1 question.

## New hard gates

A candidate may enter Selection only if all hold:

1. **Question-first compression** — removing model names, dataset names, method names, and technical terminology still leaves an intelligible question.
2. **Immediate tension** — a knowledgeable researcher can say what the default expectation was and why the observed/possible opposite is surprising.
3. **No method dependency** — the question remains interesting if the proposed identifying method disappears tomorrow.
4. **No ancestry dependence for interest** — ancestry is needed to establish scientific ownership, not to make the question sound interesting in the first place.
5. **Answer asymmetry is not required** — both major answers should teach us something; the project must not rely on one lucky positive.
6. **Complexity budget** — if the one-sentence question requires more than one uncommon technical distinction, do not promote it yet.

## Counterexamples / warning signs

Do **not** promote candidates whose main pitch is:

- “We can finally identify X using Y.”
- “Prior A predicts this cell and Prior B predicts that cell.”
- “This operator has signature +|- under polarity reversal.”
- “No one has connected semantic object A to training quantity B.”

Those statements may support a project, but they are not the project’s natural question.

## Current portfolio calibration

### L36

Taste-wise, L36 is a strong positive calibrator because the pressure is immediate:

> Increasing search should help find a better translation, yet sufficiently wide beam search can make translation collapse.

The mechanism can be subtle; the question is not.

### L41

L41 remains `PILOT-AUTHORIZED — E01 ONLY`, but should **not** become the template for future generation.

Its current scientific design is careful, but the natural question is weaker than the identification design. The simplest honest compression is approximately:

> Can a language model correctly understand what a sentence says, yet learn the opposite world belief from training on that sentence?

That version is worth piloting, but future candidates should ideally begin with such a natural contradiction rather than arrive there only after a long formal-semantics derivation.

## Search behavior from now on

During SEARCH:

- prefer robust anomalies, reversals, failed monotonicities, and broken default expectations;
- prefer questions whose surprising direction is visible before mechanism analysis;
- explicitly collect “I expected A, but evidence says B” statements from strong papers and lineages;
- use frontier papers as evidence of tension, not as limitation generators;
- if a candidate starts becoming more elegant only after adding technical machinery, stop and re-evaluate Layer 1.

The target remains:

> **Easy to state. Hard to explain.**

not:

> **Hard to state. Clever to identify.**
