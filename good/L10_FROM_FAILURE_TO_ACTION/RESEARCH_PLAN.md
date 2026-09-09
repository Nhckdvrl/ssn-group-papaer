# L10 — Research Plan

**Goal:** locate the failure→action bottleneck before scaling models, datasets, or mechanistic tooling.

---

# Phase 0 — Artifact audit

Before target-model compute:
- pin ImplicitMemBench repository commit;
- validate the 20 released tool-like items from Conditioned API Aversion + Tool Use with Side-Effects;
- verify objective failed action, alternative action, outcome, and next-request mapping;
- freeze transformation script and hashes.

If identification fails, repair the substrate first.

---

# L10-E01 — Untouched-History Stage Decomposition

## Question

> From the same experienced failure history, does the model retain the outcome, attribute it to the correct action, know the replacement policy, and actually execute that policy?

## Setup

- 20 released item instances;
- one strong open instruct model first;
- native chat/tool format;
- fixed decoding;
- independent M/C/P/A forks from H.

## Primary evidence

Report four branch accuracies and item-level dissociations, especially:

> **policy correct + actual action wrong**

This is the clean Stage-4 signature, but E01 remains informative if the break occurs earlier.

No hidden-state probe is needed for E01.

---

# L10-E02 — Matched Stage Completion

From untouched H, run action-only branches:
- raw;
- outcome reminder;
- causal binding;
- negative prohibition;
- positive replacement.

## Question

> Which missing piece, when supplied alone, causally changes the first real action?

Interpret relative to E01:
- outcome reminder rescues → retention;
- causal binding adds rescue → attribution;
- replacement needed → fact-to-policy conversion;
- policy already verbalized but direct policy completion changes action → policy/action dissociation;
- positive replacement ≫ prohibition → negative-specification boundary.

Do not claim a stage solely from questionnaire accuracy.

---

# Phase 2 — Replication / boundary

Only after E01/E02:
- second open model family;
- one matched success-experience control;
- interference/delay if retention is implicated;
- feedback-strength/ambiguity controls if attribution is implicated.

Do not run all boundaries by default.

---

# Phase 3 — Natural interactive validation

Take the winning bottleneck/completion into a natural error-recovery setting:
- tool execution errors;
- repeated-action trajectories;
- public Fission-GRPO-compatible or equivalent tasks.

Ask whether the controlled diagnosis predicts natural repetition and whether the same completion repairs it.

---

# Outcome routes

- retention wins → consolidation/interference;
- attribution wins → action–outcome binding;
- policy formation wins → episodic fact → executable replacement;
- behavioral inhibition wins → knowledge/action dissociation;
- negative-specification wins → connect to prohibition mechanisms without collapsing into them;
- matched design erases gap → reconstruct around what the parent inhibition score measures, if broad/consequential.

---

# Kill / reconstruct

RECONSTRUCT when another stage/boundary wins.

KILL when data do not identify the stages, effects reduce to known negative-instruction behavior, no completion moves actual action, natural validation breaks the controlled explanation, or new literature compresses the full chain.

---

# Main-level requirement

Before paper-mainline approval require:

> established phenomenon → stage-wise localization → targeted causal repair → meaningful boundary → natural validation → consequence for experience/memory design.

Do not promote a four-bar diagnostic funnel by itself.
