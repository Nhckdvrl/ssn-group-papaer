# L12 — Minimum Decisive Pilot Card

**Status:** PILOT-AUTHORIZED  
**Purpose:** establish a clean training-induced invariance transition and determine whether there is enough leverage to separate competing mechanisms.

> This is the current cheapest route, not a fixed full-paper protocol.

---

## Pilot question

> In a same-family open model trajectory, does reasoning-oriented training reduce framing sensitivity in a reproducible way, and does the framing information itself disappear or remain internally available after behavior becomes invariant?

---

## Minimal setup

Prefer:
- one public same-family checkpoint lineage;
- pre-/post-reasoning-SFT comparison;
- 1–3 strong matched decision manipulations from the ACL 2026 parent;
- enough repeated runs to establish stable choice differences.

Candidate axes:
- gain/loss;
- description/history;
- option order.

No need to run all of them if one gives a clean transition.

---

## First behavioral requirement

Confirm:
> post-training changes **sensitivity to equivalent presentation**, not merely overall accuracy or answer style.

If no usable transition appears, do not jump to mechanistic tooling.

---

## First mechanism split

A cheap first distinction can ask:

### Does framing identity remain recoverable after behavioral invariance appears?

If no:
- canonicalization becomes more plausible.

If yes:
- policy/readout override or deliberation becomes more plausible.

This alone is **not** the final evidence. It only chooses the next causal experiment.

---

## Stronger follow-up

Use the simplest causal operation that can answer:
> is the surviving/disappearing framing signal actually relevant to the final choice?

Possible tools include patching, ablation, steering, cross-checkpoint intervention, or reasoning-mode intervention.

The agent may choose another method if it is cleaner.

---

## Informative branches

### A — frame information collapses
Pursue representational canonicalization.

### B — frame information survives but no longer controls choice
Pursue policy/readout suppression.

### C — invariance depends on reasoning mode
Pursue deliberation-mediated invariance.

### D — effect only holds for arithmetic-transparent tasks
Pursue boundary/specialization.

### E — another mechanism emerges
Reconstruct around it.

---

## Pilot kill conditions

Kill/demote if:
- no reproducible training-stage behavioral transition exists;
- same-family checkpoint differences are too confounded;
- only probe correlations remain with no path to decisive evidence;
- the project reduces to another cognitive-bias benchmark.

Do not kill because canonicalization specifically fails.

---

## Promotion criterion

Keep/promote only if there is a credible route to:

> **established behavioral anomaly  
> → independent mechanism question  
> → decisive evidence  
> → meaningful boundary/consequence  
> → paper identity comparable to strong ACL/EMNLP/NAACL Main work.**
