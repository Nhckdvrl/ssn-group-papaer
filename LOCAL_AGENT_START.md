# Local Agent Start — Current Execution Handoff

**Date:** 2026-09-09  
**Target:** NAACL Main  
**Mode:** RESEARCH EXECUTION  
**Approved paper mainline:** NONE

# Current priority

1. **L10 — From Failure to Action**  
   `good/L10_FROM_FAILURE_TO_ACTION/`
2. **L12 — Reasoning-Induced Invariance**  
   `good/L12_REASONING_DECISION_INVARIANCE/`
3. **L08 — strong backup only**  
   `candidates/L08_READOUT_DIMENSION/`

**L11 is KILL / K181. Do not resume it.**

Do not generate new topics unless the user explicitly reopens search.

---

# Mandatory reading before experiments

1. **RESEARCH_EXECUTION.md**
2. the selected candidate's canonical package:
   - README.md
   - DATA_AND_GOLD.md
   - RELATED_WORK_AND_NOVELTY.md
   - RESEARCH_PLAN.md
   - PILOT_CARD.md
3. existing execution artifacts/code/results inside that candidate directory.

Keep: claim → experiment → config/code → data → raw output → evidence → claim update.

---

# L10 immediate instruction

The first experiment is:

> **one untouched experience history H → independent branches for outcome recall, causal attribution, policy knowledge, and actual first action.**

Never ask diagnostics and then continue that same conversation into the action test.

After localization, fork again from H and add only one matched completion:
- outcome reminder;
- action–outcome causal binding;
- negative prohibition;
- positive replacement.

Measure which completion changes the **actual first action**.

Start with one strong open instruct model. Add a second family only after the design has leverage.

---

# L12 immediate instruction

The sibling behavioral contrast is already established locally. Do not rerun it at scale.

Next:
1. **E07 — relevant-vs-irrelevant context boundary**;
2. **E08 — conclusion-free causal decision-state substitution**, only after E07 is stable.

The goal is not “find a layer.” Distinguish selective semantic abstraction, context flattening/causal disengagement, deliberative reconstruction, or a stronger account.

---

# Stop / reconstruct rule

A preferred hypothesis losing does not kill the RQ.

Stop/reconstruct when data do not identify the claim, the parent is not robust enough, reviewer compression wins, why-space collapses to a technical corner, or the surviving result is below Main scale.
