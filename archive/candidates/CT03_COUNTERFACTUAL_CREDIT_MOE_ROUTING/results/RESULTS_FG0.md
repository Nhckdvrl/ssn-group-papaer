# CT03 FG0.1 — Counterfactual routing credit is decision-local, not state-persistent

**Run:** 2026-09-20, `fvcrc20:0,1` · Qwen3-30B-A3B fp32, L44 · 6 problems ×
{high, low} tokens × {base, proxy-best, exact-best}, locked dev pool (hendrycks
MATH **train**, disjoint from MATH-500). `src/fg0_diag.py`.

**Status: closed.** FG0.1 is retained as a causal characterisation and as the
motivation for CPD — **not** as the validation of kill-bar condition 3. That
condition is now tested by CPD itself (see `docs/CPD_V1_DESIGN.md`).

## What was measured

The first smoke run showed the greedy continuation never changed under
intervention. That is ambiguous between "the hook is broken" and "the hook works
but has no decision consequence", so the diagnostic measured the decision level
directly, plus how long the perturbation survives along a shared continuation.

The hook is not broken: gold logprob moved from −18.106 to −16.812 on one
example, so the intervention does reach the KV cache and propagate.

## 1. The selector works — `H_proxy` finds decision-relevant positions

| token | next KL | **next TV** | greedy flip | gold p base→arm | base entropy | top1−top2 margin |
|---|---|---|---|---|---|---|
| **high** | 7.7e−3 | **0.0434** | 0/6 | 1.88e−3 → 4.74e−3 | 0.655 | 0.734 |
| **low** | 3.7e−7 | 0.0000 | 0/6 | 0.996 → 0.996 | 0.023 | 0.993 |

A ~400× separation in total-variation response, with high tokens also carrying
an order of magnitude more base entropy. Counterfactual headroom identifies
positions where the route choice has a **substantially larger causal effect on
the model's next-token distribution** — it is not generic perturbation
sensitivity, and not teacher-forcing arithmetic with no behavioural referent.

## 2. But one swap cannot cross the decoding margin

Greedy never flipped, and the reason is quantitative rather than mysterious:
the base top1−top2 probability margin is **0.734** while the intervention moves
the distribution by **TV = 0.043**. A single equal-compute expert swap changes
the distribution but is an order of magnitude too weak to cross an already-large
decoding margin.

## 3. And the perturbation does not ride the cache forward

Teacher-forcing the *same* base continuation through each arm's
intervention-specific cache (median TV):

| token | arm | s1 | s2 | s4 | s8 | s16 | s32 |
|---|---|---|---|---|---|---|---|
| high | proxy_best | 0.002 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

From 0.043 at the intervened token to 0.002 one step later and ~0 thereafter.
The causal channel is

```
route change -> next-token distribution changes -> if the sampled token
changes, the trajectory branches
```

**not** a persistent latent-state drift that later outcomes inherit.

## Why this closes FG0 rather than extending it

Two follow-ups were considered and both are rejected **by this measurement**,
not by preference:

- **Paired sampling on single interventions.** TV = 0.043 means ~4% of samples
  branch. Detecting a ~2% shift in final accuracy through a 4% branching rate
  needs far more seeds than the effect is worth.
- **Intervening at every high-headroom prefix token, then generating.** With
  persistence ≈ 0, earlier interventions have washed out by the time generation
  starts; the final cache would remember only the last one or two. The intuition
  that "many weak interventions accumulate" is false in this system — it would
  only hold if each intervention were allowed to change an emitted token
  immediately, which is a sequential on-policy design, i.e. a hand-built
  gold-conditioned oracle routing policy.

And that is precisely what CPD already is, learned rather than hand-built. So
the right test of the free-generation question is the method itself.

## The statement this licenses

> A one-off counterfactual rerouting changes the local decision distribution but
> dissipates within one or two tokens unless it changes the emitted token. This
> motivates distilling counterfactual credit **into the router**, so that the
> correction is applied repeatedly throughout autoregressive generation rather
> than used as a one-shot intervention.

FG0 began as a kill-bar probe and ends as CPD's motivation. The kill-bar question
is unchanged and now sits with CPD-v1 + free generation on these same 120 locked
problems.
