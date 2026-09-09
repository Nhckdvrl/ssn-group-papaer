# L10 — Minimum Decisive Pilot Card

**Experiment:** L10-E01 + gated L10-E02  
**Status:** PILOT-AUTHORIZED  
**Purpose:** determine whether the failure→future-action chain has a stable, causally addressable bottleneck.

---

# Load-bearing question

> **Can the same model know what happened, know what action caused it, know what it should do next, yet still repeat the failed action? If not, which earlier stage is missing?**

---

# Data

Start with the **20 released ImplicitMemBench tool-like instances** from:
- Conditioned API Aversion;
- Tool Use with Side-Effects.

Before model evaluation audit each item for:
- explicit failed/problematic B;
- explicit viable/safer A;
- objective system outcome;
- unambiguous next-request action truth.

Freeze exclusions and source hashes before seeing model behavior.

---

# Model

Use **one strong open instruct model** already feasible locally.

Freeze model ID/revision, template, decoding config, and parser.

A second family is confirmation, not part of the first route-selection run.

---

# E01 — untouched-history forks

For each canonical history H, independently run:

1. **M — outcome memory**
2. **C — action–outcome attribution**
3. **P — executable policy**
4. **A — actual first action**

**Hard rule:** M/C/P outputs never appear in A.

Record stage correctness, first action, invalid outputs, and policy-correct/action-wrong dissociation.

Use item-level bootstrap or paired exact/permutation tests where applicable. Do not pseudo-replicate generations.

---

# E02 — causal completion

From the same untouched H create action branches:

- A0 raw;
- A1 outcome reminder;
- A2 causal binding;
- A3 “do not B”;
- A4 “use A instead”.

Primary outcome:
> paired change in actual avoid-failure / correct-first-action rate.

The experiment is decisive through **behavior**, not more verbal diagnostics.

---

# Informative outcomes

- **M weak:** retention bottleneck.
- **M good, C weak:** attribution bottleneck.
- **M/C good, P weak:** executable-policy formation bottleneck.
- **M/C/P good, A weak:** behavioral inhibition / knowledge-action dissociation.
- **A4 ≫ A3:** positive-replacement boundary.
- **No raw gap but intervention pattern remains:** reconstruct.
- **No stable gap and no causal action effect:** demote/kill rather than scale.

# Continue criterion

Continue when at least one interpretable stage dissociation motivates a matched completion and/or one preregistered completion clearly changes actual action.

Do not require Stage 4 specifically.

# Stop criterion

Stop/reconstruct if item truth is ambiguous, the action protocol/parser is invalid, results reduce to wording artifacts, or no stage/completion has causal leverage.

No model zoo, hidden-state probing, or natural-agent expansion before this card is resolved.
