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

## RETRACTION (2026-09-22, same day, before 第四关 was started)

The reading below — and the sentence "E10 establishes what is being screened: a
supervision signal that, at full oracle strength, yields no downstream
generation gain" — **is withdrawn. It was not supported.** E09/E10 did not
reproduce the parent's EPO action mechanism, in three places:

1. **`r-` is wrong, and this changes the semantics of the objective.** The
   parent sets `r- =` the route the CURRENT router actually executes (its
   top-k), samples G alternatives, takes `r+ = argmin CE` among them, and
   **emits a gradient only when `CE(r+) < CE(r-)`**. That is policy improvement
   from the deployed action: *you took this route, here is a better one, move*.
   E09/E10 instead set `r+`/`r-` to the best and worst SAMPLED routes, which
   only constrains `best_sampled > worst_sampled` — a comparison the currently
   deployed route need not even participate in. A router can satisfy it by
   rearranging the whole expert-score landscape with no reason for its actual
   top-k to become the improved route. That is a much better explanation of
   4/8 experts changed, preference accuracy collapsing 0.550 -> 0.505, route
   value climbing and greedy generation not moving, than "the oracle has no
   downstream value".
2. **The recipe is far from the parent's.** Parent: 2269 verified trajectories,
   lr 3e-4, beta 0.1, batch 16, 1 epoch, hard tokens entering dynamically by
   CURRENT CE > 0.1. E10: 146 problems, six permanently fixed tokens each,
   lr 1e-3 (3.3x), beta 1.0 (10x), batch 1, 4 epochs. Wholesale rewriting under
   that regime is not surprising and cannot be attributed to EPO.
3. **The downstream metric is not the parent's either.** The parent never
   claims a greedy pass@1 gain; its headline is a pass@K shift, which it calls
   small and treats as a minimal existence check (AIME24+25 and HMMT, 160
   samples per problem, T=0.6, top-p 0.95). `0.475 -> 0.475` on greedy says this
   checkpoint did not change deterministic accuracy. With 99.2% of completions
   changed, one greedy trajectory per problem cannot say whether the generation
   distribution moved toward or away from success under sampling.

Also corrected: `logpi(S|x) = sum_{e in S} log p(e|x)` is **the parent's own
definition** of route log-probability, not a surrogate I chose. The E09/E10
design docs describing it as mine are wrong on that point.

What E10 does establish, and no more:

> Best-vs-worst sampled-route preference training, under a small-data aggressive
> recipe, raises held-out route value and does not change greedy accuracy.

第四关 is **not** blocked by a null; it is blocked because the gate that was
supposed to license it was not correctly executed. The repair is E11: a
corrected L47 gate, back at the cheap layer, with the parent's `r-`, the
parent's skip rule, a parent-ish recipe, and a sampled pass@K evaluation.

## Superseded reading (kept for the record)

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

Superseded by the retraction above. CT03 remains **KILLED** as originally scoped (`CT-KILL-20260922-1`).
第一关 (E08) passed, 第二关 (E09) passed, 第三关 (E10) passes its letter and
returns a null on the question that matters.
