# Good Candidates

> **good/ means pilot-authorized, not paper-mainline-approved.**

**Approved paper mainline:** NONE

## Active

| ID | Candidate | Canonical package | Status |
|---|---|---|---|
| **L03** | **Table Value ≠ Observation Status** | [L03_TYPED_OBSERVATION/](L03_TYPED_OBSERVATION/) | **PILOT-AUTHORIZED** |
| **L11** | **Task Gradient ≠ Learning Pressure** | [L11_TASK_GRADIENT_PRESSURE/](L11_TASK_GRADIENT_PRESSURE/) | **PILOT-AUTHORIZED** |
| **L12** | **Reasoning Training: Canonicalization or Policy Override?** | [L12_REASONING_DECISION_INVARIANCE/](L12_REASONING_DECISION_INVARIANCE/) | **PILOT-AUTHORIZED** |

Historical L02/L04 experiment packages may remain in this directory for reproducibility, but they are **not active**:
- L02 → NO-GO / K175
- L04 → NO-GO / K180

Use **failed/KILLED_LEDGER.md** for actual closure reasons.

---

# Meaning of promotion

A candidate enters good/ only after the pre-pilot gates in **RESEARCH_TOPIC_SELECTION.md** are materially satisfied:

- natural/important RQ;
- genuine scientific tension;
- credible data/evidence identification;
- surviving paper-level novelty;
- outcome robustness / scientific depth;
- Main-level calibration.

Promotion means only:

# **PILOT-AUTHORIZED**

It does not mean:
- paper mainline approved;
- novelty permanently safe;
- expected mechanism must occur;
- exact methods are frozen;
- candidate should be rescued after a bad pilot.

After the minimum decisive pilot, re-audit:
- data validity;
- interpretation;
- novelty/reviewer compression;
- Main-level scale;
- remaining paper depth.

---

# Canonical package

Each active pilot-authorized candidate keeps the smallest useful five-document package:
- **README.md** — current RQ, scientific accounts, paper identity, verdict;
- **DATA_AND_GOLD.md** — evidence/measurement contract;
- **RELATED_WORK_AND_NOVELTY.md** — closest ownership/collisions;
- **RESEARCH_PLAN.md** — open but disciplined research routes;
- **PILOT_CARD.md** — current smallest decisive starting experiment.

Execution artifacts such as claims, code, configs, data and results stay inside the concrete candidate directory.

Do not create extra root-level candidate cards.

---

# Important flexibility rule

A candidate package should **constrain the science, not pre-write the answer**.

Keep firm:
- RQ;
- evidence standard;
- novelty boundary;
- Main-level identity;
- kill/reconstruct logic.

Keep flexible:
- exact method;
- exact mechanistic account;
- exact model/checkpoint after feasibility checks;
- exact paper section order;
- whether the final paper is mechanism-, measurement-, or boundary-centered.

When the data reveal a stronger explanation, reconstruct around it rather than forcing the original hypothesis.

---

# L11 warning

Do not reduce L11 to:
> “Can we balance task gradients better?”

Its identity must remain:
> **what makes LLM tasks optimization-loud, whether raw parameter-gradient norm is a valid cross-task pressure measure, and what scientific/training consequence follows.**

---

# L12 warning

Do not reduce L12 to:
> “Can we probe framing information in a reasoning model?”

Its identity must remain:
> **what reasoning post-training changes when behavioral decision invariance emerges: representation, policy/readout, deliberation, or a meaningful boundary.**

---

# L03 warning

Do not reduce L03 to:
> “Can an LLM understand Census sentinel codes?”

Its scientific identity must remain about whether provider-defined observation status is a load-bearing semantic representation for modern table understanding.

The local survivor is not the quality ceiling. Continue judging every active candidate against strong ACL/EMNLP/NAACL Main work during execution.
