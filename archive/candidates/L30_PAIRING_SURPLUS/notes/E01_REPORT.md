# L30 E01 — Pilot Report

**Date:** 2026-09-13. **Verdict: `HOLD — PILOT UNDER-RESOLVED`** for the project's
own novel quantity, with two large decisive effects that prior work already owns.

Design and outcome map were frozen in `notes/E01_DESIGN.md` before any arm was
evaluated. Nothing below departs from that pre-registration.

---

## 1. What ran

12 matched runs: 4 arms x 3 training seeds, Gemma-2-2B base + Alpaca-Cleaned
(51,758 pairs), LoRA r=64 on a bf16 backbone, constant LR 1e-4, effective batch
64, 3 epochs, loss on response tokens only in every arm. Training on 4 Blackwell
cards; **all** evaluation on A100 nodes (see §5). IFEval, 541 prompts, greedy,
scored with the unmodified Google Research verifier.

## 2. Result — IFEval strict prompt-level, epoch 3 (pre-registered primary)

| arm | mean | 95% CI | seeds 0 / 1 / 2 |
|---|---|---|---|
| P (correct pairing) | 23.29 | [19.96, 26.80] | 23.11 / 24.21 / 22.55 |
| D_mask (no correspondence, budget-matched) | 21.44 | [17.93, 25.20] | 19.78 / 23.48 / 21.07 |
| D_rt (Response Tuning) | 19.53 | [15.90, 23.48] | 17.19 / 21.81 / 19.59 |
| S (wrong correspondence) | 8.32 | [5.55, 11.40] | 7.21 / 7.02 / 10.72 |

| contrast | pp | 95% CI | excludes 0 |
|---|---|---|---|
| `Delta_corr` P − S | **+14.97** | [+10.66, +19.29] | **yes** |
| `Delta_wrong` D_mask − S | **+13.12** | [+8.81, +17.44] | **yes** |
| `Delta_pair` P − D_mask | +1.85 | [−1.79, +5.42] | no |
| `Delta_pair_rt` P − D_rt | +3.76 | [−0.25, +7.58] | no |
| construct D_mask − D_rt | +1.91 | [−1.66, +5.42] | no |

Intervals are prompt-clustered and seed-resampled, 10,000 bootstrap draws, arms
sharing one prompt draw. Constraints attached to the same prompt are never
treated as independent.

Trajectory: `Delta_pair` was +2.31 [−1.11, +5.73] at epoch 1 and +1.85
[−1.79, +5.42] at epoch 3 — small and under-resolved at both training lengths.
Tripling training did not grow it.

## 3. Verdict against the frozen rules

**`Delta_pair` is the project's own quantity** — the marginal value of correct
correspondence over *no* correspondence at matched prompt pool, response pool,
token budget, positions, loss-token count and step schedule. It comes out at
+1.85 pp with an interval that still admits a real +5.4 pp effect. The frozen
rule for exactly this case reads: *"≤2 pp with intervals that still admit a real
~3–4 pp effect → `HOLD — PILOT UNDER-RESOLVED`, not 'pairing does not matter'."*

So: **HOLD.** We cannot claim `P ≈ D_mask`, and we equally cannot claim a pairing
surplus exists.

**`Delta_corr` and `Delta_wrong` are decisive and large** — but `Delta_corr` is
the "shuffling answers drops IFEval by N points" result that the candidate README
explicitly rules insufficient for Main, because MAIN / FedDQC / Hindsight already
own the parent claim that instruction–response alignment matters.

The uncomfortable summary: **the effect we can measure is the one prior work owns,
and the effect we own is the one we cannot measure.**

## 4. The one finding that is not resolution-limited

S collapses to a near-constant policy, in **every seed**:

| arm | distinct responses / 541 | median response chars |
|---|---|---|
| P | 534–537 | 579–696 |
| D_mask | 537–539 | 441–585 |
| D_rt | 537–539 | 358–539 |
| **S** | **6–11** | **62–241** |

D_mask has *no* correspondence at all and does not collapse; S, which has a
*wrong* correspondence, collapses every time. So the collapse tracks actively
decorrelated supervision, not absent supervision.

This is expected in hindsight — under `P_X (x) P_Y` the optimal conditional is
the response marginal, and greedy decoding from a marginal is degenerate — but
the *contrast with D_mask* is the informative part, and it is qualitative (a
~50x difference in output diversity), not a few percentage points.

**It also means `Delta_corr` must not be reported as a graded capability gap.**
A large part of those 15 pp is "collapsed vs did not collapse", not "worse at
following constraints".

## 5. Method notes worth keeping

- **D_mask passed its construct check.** With positions held fixed by swapping in
  a different instruction *of the same token length*, D_mask response logits move
  by exactly 0.0 (also 0.0 with random tokens behind the mask), while the same
  swap moves P by 26.6. The mask is verifiably applied (26.0 vs unmasked).
  Against D_rt it is +1.91 [−1.66, +5.42] — not distinguishable, so D is not
  obviously a serialisation artifact, though the interval is too wide to claim
  the two are equivalent.
- **Evaluation hardware matters at this scale.** The same adapter scored 10.91
  vs 10.54 strict-prompt on Blackwell vs A100 under identical greedy decoding.
  That drift is the same order as `Delta_pair`, so every arm was evaluated on one
  device class.
- **Trainer bug caught by a parameter count.** Wrapping only the target Linears
  left `embed_tokens` (590M, tied to `lm_head`) trainable. Fixed before any run.

## 6. Why more compute does not fix this

The `Delta_pair` interval is **evaluation-limited, not seed-limited**:

| resampling | `Delta_pair` CI width |
|---|---|
| prompts + seeds | 7.58 pp |
| prompts only (seeds fixed) | 6.01 pp |

Only ~1.6 pp of the width comes from training seeds; ~6 pp is the 541-prompt
IFEval sample itself. A fourth, fifth or tenth seed cannot push this below the
~3 pp needed. Pairing the bootstrap across arms helps little, because P and
D_mask are different models whose per-prompt outcomes are weakly correlated.

Resolving `Delta_pair` to ±1.5 pp would need roughly an order of magnitude more
deterministic evaluation items than IFEval contains. This is the L19 failure
mode the candidate was authorised to avoid — arriving here via the evaluation
side rather than the training side.

## 7. Recommendation

Per `RESEARCH_EXECUTION.md` §13, **HOLD** with one named blocker and one bounded
way to resolve it:

> **Blocker:** the marginal value of correct correspondence over none
> (`Delta_pair`) is below the resolution of any deterministic instruction-following
> evaluation we can currently afford.

Do **not** rescue this by reporting `Delta_corr` as the headline. That is the
prior-owned claim, and the S collapse makes it partly an artifact of degenerate
decoding.

The one object that survives and is *not* resolution-limited is the
**collapse asymmetry in §4**: wrong correspondence destroys prompt-conditional
behaviour entirely while absent correspondence does not. That is a qualitative,
seed-robust, mechanism-shaped phenomenon, and it is a different scientific claim
from "aligned pairs are better data".

Whether it is worth a paper is a **selection decision, not an execution
decision**. Under §8 of the workflow this is a claim mutation — the identity
would move from *what pairing teaches* to *what wrong pairing destroys* — so
authorisation has expired and the candidate must re-enter selection with a Claim
Novelty Delta before any further compute.

**C2 remains unauthorised, and E01 does not authorise it.**
