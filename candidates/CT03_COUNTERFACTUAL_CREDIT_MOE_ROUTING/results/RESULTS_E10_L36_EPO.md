# E10 — Dynamic Exact-EPO at L36 (第三关)

Design frozen before the run: `docs/E10_DESIGN.md`. No proxy in E10 — this is the
oracle arm, 32 exact replays per token per step.

Same 209 problems and 6 high-CE tokens per problem as E09, so L36 and L47 are
compared on the same tokens: 146 train / 63 held out, disjoint and asserted; the
120-problem FG0 dev pool asserted disjoint from both. Routes resampled from the
**current** router every step; exact suffix CE recomputed by replaying layers
37-47 for every candidate.

## Training arc

| | before | ep1 | ep2 | ep3 | ep4 |
|---|---|---|---|---|---|
| held-out route value | 0.000 | +0.208 | +0.282 | +0.343 | **+0.375** [+0.231, +0.527] |
| median route value | 0 | +0.020 | +0.025 | +0.046 | +0.035 |
| win rate | — | 0.577 | 0.571 | 0.598 | 0.587 |
| **preference accuracy** | **0.442** | 0.550 | 0.508 | 0.524 | **0.505** |
| experts changed / 8 | 0 | 3.24 | 3.84 | 4.12 | 4.02 |

## Free generation, 120 locked FG0 problems

| | base | EPO-L36 | diff |
|---|---|---|---|
| accuracy | 0.475 | 0.475 | **+0.000** [−0.050, +0.050] |
| identical completions | — | — | **0.008** |

## The pre-registered rule passes on its letter

> route value improving with a 95% CI excluding 0 **AND** free generation not
> degrading significantly.

Both hold: +0.375 [+0.231, +0.527], and a free-generation difference of exactly
zero. So 第四关 is not blocked. **What the rule cannot do is make this a
positive result, and it is not one.**

## What the numbers say

1. **The oracle produced zero generation gain at a non-final layer.** With the
   full 32-route exact search, no proxy, no approximation, L36 rewrote **99.2%**
   of completions and moved accuracy by **0.000**. L47 did the same thing at
   +0.017 (ns). Two layers, same answer.
2. **Preference accuracy — the only thing the objective constrains — barely
   moved, and moved the wrong way during training.** 0.442 → 0.550 at ep1, then
   back down to 0.505 by ep4, *while route value nearly doubled over the same
   span*. The direction that raises route value is actively pulling preference
   accuracy back toward its init value. Whatever the router is learning, it is
   not the per-token route preference the loss encodes.
3. **The route-value gain is tail-driven and comes with wholesale rewriting.**
   Mean +0.375 against a median of +0.035, win rate 0.587, 4.0 of 8 experts
   changed per token. The same shape as E03.1, E07 and E09.
4. **Init preference accuracy is below chance at both layers** (0.442 at L36,
   0.402 at L47). The base router's own likelihood ordering anti-correlates with
   exact CE on these candidate pairs. That is a fact about the base model.

The honest summary is that route value is cheap to move, generation is not, and
the gap between them did not narrow by moving to a non-final layer. E09 predicted
this and said so before E10 ran; E10 confirmed it with the oracle in hand.

## Consequence for 第四关

第四关 (screened-EPO) compares screened against exact at equal routing/benchmark
gain with 75-88% fewer exact reruns. E08 established the screening half solidly
(R_2 = 0.938/0.976). E10 establishes what is being screened: **a supervision
signal that, at full oracle strength, yields no downstream generation gain.**

So the only claim 第四关 can support is an **efficiency** claim — screened-EPO
reproduces exact-EPO's route-value trajectory at a fraction of the reruns. It
cannot support a quality claim, because exact-EPO has no quality gain to
inherit. Any write-up must say that in the same breath as the cost ratio.

## Implementation notes

Three defects this round, all caught, in the order they mattered:

1. **V1 validated the wrong path** — it replayed with the live attention kwargs
   instead of kwargs rebuilt from the cached fields, i.e. a path the trainer
   never takes. Fixed first; only then did it catch anything.
2. The attention-mask precondition fired **at save time, after 104 problems**.
   A precondition belongs at the first opportunity to check it.
3. The mask was cached as `am.float()`. It is `torch.bool`, so that turns a
   causal mask into an **additive 1.0/0.0 mask — no masking at all**: CE read
   44.5 against the true 82.6, the model "improving" by seeing the future.
   Under the old V1 this would have been silent, and the entire L36 result
   would have been trained and scored on a replay that can look ahead.

V1 finally read `167.2719 vs 167.2719`, mask `(1,1,366,366) torch.bool`.

## Status

CT03 remains **KILLED** as originally scoped (`CT-KILL-20260922-1`).
第一关 (E08) passed, 第二关 (E09) passed, 第三关 (E10) passes its letter and
returns a null on the question that matters.
