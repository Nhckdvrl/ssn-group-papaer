# L34 E01 — G1 verdict: **INSTRUMENT FAILS**

**Date:** 2026-09-14
**Gate:** `E01_PREREGISTRATION.md` §6 G1 — first-stage access specialization on OLD facts,
measured at the post-Phase-1 checkpoint.
**Anchor:** Llama-3.2-3B base, shared trunk (OLD-bio loss 0.117), 3 seeds per causal arm.
**Verdict:** **G1 FAILS.** Per the frozen rule, the NEW phase is **not** interpretable.
No account (A / B / C) is supported or rejected by this run.

---

## 1. The gate quantity

```
CROSSOVER_postP1(OLD) = PREF(PIT_A) - PREF(PIT_B),   PREF(arm) = S_famA - S_famB,   S = -NLL/token
```

G1 required this to be **positive** with a bootstrap CI excluding 0.

| template set | CROSSOVER_postP1(OLD) | 95% CI | required |
|---|---|---|---|
| held-in | **−0.1554** | [−0.1853, −0.1266] | > 0 |
| held-out | **−0.0844** | [−0.1136, −0.0552] | > 0 |

The crossover is large, tight, and **reversed**. This is not a null — it is a significant
effect in the direction opposite to the manipulation.

## 2. Why it is a construct failure and not a finding

The diagnostic is the per-arm, per-attribute change in OLD-fact gold-answer NLL relative to
the balanced arm (positive = the curriculum made that attribute **worse**):

| arm | trained family | Δ on its **own trained** family (held-in) | Δ (held-out) |
|---|---|---|---|
| `PIT_A` | birth_date, university, work_city | **+0.383** [+0.376, +0.391] | **+0.290** [+0.280, +0.301] |
| `PIT_B` | birth_city, company, major | **+0.413** [+0.397, +0.430] | **+0.361** [+0.344, +0.379] |

> **Neither arm improved the family it was trained on. Both degraded it.**
> 10 of 12 arm × attribute cells degrade, on held-in and held-out alike.

There is therefore no access specialization for the gate to measure. The observed crossover is
differential *damage*, not differential *preference*.

Per-attribute deltas vs `PIT_BAL` (held-in):

| arm | birth_date | university | work_city | birth_city | company | major |
|---|---|---|---|---|---|---|
| `PIT_A` | +0.110 | +0.758 | +0.282 | **+1.835** | +0.264 | **−0.958** |
| `PIT_B` | +0.634 | −0.157 | +0.307 | +0.285 | +0.747 | +0.208 |

Two cells dominate, and both are **untrained** attributes for the arm in question — the signal is
not organised by the trained/untrained split at all:

- `PIT_A` / `birth_city` **+1.835**. `PIT_A` trains `work_city`. Because the preregistration gave
  `birth_city` and `work_city` **disjoint city pools**, `PIT_A` learns "city-shaped answers come
  from the *work-city* pool", which makes the gold `birth_city` value of every OLD person sharply
  less likely. The control introduced to prevent cross-family leakage became the largest single
  source of cross-family interference.
- `PIT_A` / `major` **−0.958**. `major` is the one attribute `PIT_A` never trains, while the
  `PIT_BAL` reference does train it. The "improvement" is the reference arm being damaged, not
  `PIT_A` gaining anything.

## 3. Root cause

Phase 1 trains QA about `PIT` persons whose biographies are **never shown** (prereg §3), so those
answers are permanently ungrounded. The curriculum therefore cannot teach *"this is how family-A
knowledge will be queried"*; it can only teach *"family-A questions take answers of this surface
shape, with arbitrary content"*. What it installs is an answer-format prior plus across-the-board
interference with already-encoded facts — which is exactly what the numbers show.

This was a deliberate design choice, made to satisfy the hard constraint that the access curriculum
must not contain the NEW facts (`SELECTION.md` §5.2). Jiang et al.'s PIT does **not** have this
property: its pre-instruction QA concerns the very documents that arrive later, so its answers are
grounded by the subsequent document phase. The clean-NEW-facts constraint and the grounded-access-
curriculum requirement are in direct tension, and E01 as frozen resolved that tension in a way that
destroys the manipulation.

## 4. Consequence under the frozen rule

`E01_PREREGISTRATION.md` §6 G1: *"If the manipulation cannot produce mirrored specialization on
knowledge the model already has, the access curriculum has no leverage → **STOP**, do not interpret
the NEW phase."*

That rule fires. Specifically:

- the `PROSPECTIVE` estimand from this run must **not** be reported as evidence for or against
  accounts A, B or C;
- this is **not** a null result for L34's scientific question — the question was not tested;
- no prompt/template search, no attribute-partition search, no seed extension may be used to turn
  this into a positive (prereg §6 G3, §9).

The remaining runs still produce the **G0** mother check (`NO_PIT` vs `PIT_BAL` on NEW facts), which
is diagnostic for any redesign: it measures whether an ungrounded access curriculum is net-harmful
to subsequent knowledge acquisition in this substrate.

## 5. What a corrected instrument would have to do

Not authorized — recorded so the fault is not rediscovered:

The access curriculum must be **grounded** (answerable) while still containing none of the NEW
facts. Candidate resolutions, all requiring a fresh authorization and a fresh preregistration:

1. Ground the curriculum on a **third** fact set whose biographies *are* shown before Phase 1, so
   family-A access is taught on facts the model can actually retrieve.
2. Make the curriculum *structural* rather than QA-on-unknowns — e.g. access training on FORMAT
   persons, restricted to one family.
3. Drop the disjoint-pool control and instead equate answer pools across the two families, so
   answer-format priors cannot masquerade as family specialization.

Any of these changes the identity of the manipulation and therefore requires re-deriving the gates,
not editing them after seeing this sign.
