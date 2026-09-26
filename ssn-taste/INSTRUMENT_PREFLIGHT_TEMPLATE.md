# Instrument Preflight Template — REQUIRED BEFORE ANY NEW Sxx

Last reset: 2026-09-26

Purpose:

> Prevent another S11/S12 failure where a conceptually attractive question is registered before the manipulation/readout is known to measure the intended construct.

This file is a template. Copy the sections into a candidate-specific preflight record **only after an Observation Card has been reproduced and an RQ has been formed**.

No Sxx number may be assigned before this preflight passes.

---

# Candidate RQ

**Anchor observation:** OXX  
**One-sentence RQ:**  
**Why the RQ follows from the reproduced finding:**  

If the RQ can be stated without reference to the anchor finding, explain why it is not drifting back into abstract-question generation.

---

# P0 — Prerequisite capability

What simpler capability must the model possess for the main readout to be interpretable?

Test that capability directly.

**Pass condition:** frozen before inference.

If the prerequisite fails, stop. Do not reinterpret the failure as the target phenomenon.

---

# P1 — Manipulation validity

Scientific variable:

What exactly differs between conditions?

List every other dimension that could differ:
- wording;
- length;
- difficulty;
- tokenization;
- answer distribution;
- information amount;
- discourse framing;
- model state;
- compute.

Show why these are held fixed or irrelevant.

**Pass condition:** predeclared.

---

# P2 — Readout validity

Explain why the readout answers the RQ rather than a prerequisite skill.

Include:
- exact ground truth if possible;
- scorer;
- parser;
- invalid-output handling.

If a learned judge is required for the primary result, justify why an analytic/existing label is impossible.

---

# P3 — Symmetry / equivalent-form stability

Before measuring the target effect, test logically/semantically equivalent forms:

Examples:
- positive vs negative polarity;
- greater-than vs less-than;
- answer order permutation;
- equivalent entailment vs consistency wording;
- equivalent notation.

**Hard failure signal:** large directional flips among forms that should be equivalent.

If this happens, the instrument fails. Do not “pick the better wording”.

---

# P4 — Positive and negative controls

Positive control:
The readout must detect an unambiguous case where the target distinction should matter.

Negative control:
The readout must remain invariant where the distinction should not matter.

Both thresholds are frozen before inference.

---

# P5 — No prompt search

List all templates before inference.

A template may be changed only for a documented bug or ambiguity.

If output has been seen:
- old batch becomes discovery/debug data;
- corrected design uses a new held-out batch.

Never search many prompts and retain the one with the desired effect.

---

# P6 — Control-budget test

Count how many auxiliary controls are necessary just to make the main manipulation interpretable.

If the experiment requires stacked repairs to:
- establish the construct;
- establish the scope;
- teach prerequisite logic;
- stabilize the question;
- remove wording effects;

then the construct is probably not natural enough.

Default verdict: KILL.

---

# P7 — Synthetic-assay dependence

Ask:

> If this custom assay disappeared, would the anchor finding and RQ still independently matter?

If no: KILL.

Synthetic data may diagnose a real observation; it may not create the scientific object.

---

# P8 — Frozen preflight verdict

Record before the main pilot:

- prerequisite: PASS / FAIL
- manipulation: PASS / FAIL
- readout: PASS / FAIL
- symmetry: PASS / FAIL
- controls: PASS / FAIL
- no-prompt-search: PASS / FAIL
- control budget: PASS / FAIL
- synthetic dependence: PASS / FAIL

Only all PASS permits:

> **CREATE Sxx + add to SELECTED_TOPICS.md**

Otherwise:

> **KILL before registration.**

---

# Important distinction

Preflight data are for validating the instrument, not for claiming the scientific effect.

If preflight accidentally reveals the main effect, freeze a fresh held-out batch for the actual pilot.
