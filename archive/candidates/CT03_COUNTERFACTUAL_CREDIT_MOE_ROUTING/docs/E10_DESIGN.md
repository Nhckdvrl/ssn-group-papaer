# E10 — Dynamic Exact-EPO at L36 (第三关)

**Frozen 2026-09-22, before any E10 run.** No proxy anywhere in E10. The proxy
enters only at 第四关; E10 is the oracle/reference arm it will be measured
against.

## The question

> Does exact counterfactual supervision improve a genuinely **non-final** MoE
> router — and does that reach deployed generation?

L44 is deliberately skipped: it is close enough to the final layer that a
reviewer can read it as the parent's final-layer EPO moved back a few layers.
L36 cannot be read that way.

## Why L36 costs real compute and L47 did not

At L47 only the position-wise final norm and `lm_head` follow the block, so
patching the MoE output at `t` moved the CE at `t` **and nowhere else**. At L36
the patch propagates through layers 37-47 via attention, so the exact utility is
a sum over the whole suffix and every candidate route needs a real replay.

What is still cacheable: layers 0-36 do not depend on the L36 gate, so the
layer-36 residual stream, `x_t`, and all 128 expert outputs `E_e(x_t)` are
constant across training and are cached once. What is not: layers 37-47.

## Objective — identical to E09, only the layer changes

    delta   = CE(r-) - CE(r+)                                    >= 0
    margin  = [logpi_theta(r+) - logpi_ref(r+)]
            - [logpi_theta(r-) - logpi_ref(r-)]
    loss    = -delta * log sigmoid(beta * margin)

`r+`/`r-` are the lowest/highest exact-CE routes among 32 Gumbel top-K draws
from the **current** router's top-32 pool, resampled every step. CE is the exact
suffix CE from the replay. `logpi(S|x) = sum_{e in S} log p(e|x)` is the same
stated surrogate E09 used. Only the L36 gate trains; the reference is the
pretrained gate.

Keeping the objective bit-identical to E09 is the point: E09 established that
this chain works at L47, so a difference at L36 is a difference in the layer,
not in the code.

## Evaluation — the same three legs, and the same order of authority

1. **Held-out route value** `V = CE(base route) - CE(trained router's route)`,
   exact, paired bootstrap over held-out problems.
2. **Preference accuracy** on a FIXED candidate support drawn once from the
   REFERENCE router (so the eval set does not move with training), with its
   measured init value as the baseline — not an assumed 0.5.
3. **Free generation** on the 120 locked FG0 dev problems, greedy, base vs
   trained.

E09 is the standing reason to rank these in the opposite order from how easy
they are to move: there, +0.95 nats of route value rewrote 99.2% of completions
and moved accuracy by an amount indistinguishable from zero. **Route value is
the cheapest of the three to move and the least informative.**

## Pre-registered outcome rule

> **Leg 1 alone does not carry the topic.** For 第四关 (screened-EPO) to be
> worth running, L36 must show held-out route value improving with a 95% CI
> excluding 0 **and** free generation not degrading significantly.
>
> If route value improves and free generation *degrades* significantly, that is
> a negative result for non-final EPO and 第四关 does not run: screening a
> supervision signal that makes generation worse is not worth making cheap.

An accuracy *gain* is not required, for the same reason it was not required at
L47: n=120 cannot resolve a few points. What is required is that the mechanism
does not cost generation quality.

## Validity checks — gate the run

1. **Cached-replay identity.** Replaying the BASE route from the cache must
   reproduce the full forward's suffix CE to 1e-4. This single check validates
   the entire cached path at once — rotary embeddings, attention mask, residual
   reconstruction and layer walk — and the run does not start without it.
2. **Route reconstruction.** `mix(bank, S0, p0)` equals the block's own `h_0` to
   rel. 1e-4.
3. **Gumbel diversity.** >= 8 distinct routes among 32 draws (the E06 NaN tell).
4. **Train/test problem disjointness**, asserted, and the FG0 dev pool asserted
   disjoint from both.
5. **Batch-composition replicate.** As in E08: the per-route `u` wobble under
   fp32 must not move the argmax. Carried over rather than re-derived, since
   E10 uses the same replay code at the same layer.

## Scale

Same 209 problems and 6 high-CE tokens per problem as E09, 146 train / 63 held
out, so the two layers are compared on the same tokens. Full model over 2 cards
(only layers 37-47 are exercised in the loop). Estimated ~3.5s per problem-step
from the E08 measurement, ~45 min for 4 epochs plus evaluation.
