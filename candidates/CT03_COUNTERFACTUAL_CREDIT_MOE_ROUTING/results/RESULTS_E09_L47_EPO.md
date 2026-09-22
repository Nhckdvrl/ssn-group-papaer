# E09 — Dynamic Exact-EPO at L47 (第二关, implementation reproduction)

Design frozen before the run: `docs/E09_DESIGN.md`. No proxy anywhere in E09.

Setup: Qwen3-30B-A3B, L47 gate only. 209 MATH-train problems from the locked
`cpd_trainpool.json`, 6 high-CE tokens each, 1254 tokens; 146 problems train /
63 held out, disjoint and asserted; the 120-problem FG0 dev pool asserted
disjoint from both. Routes are resampled from the **current** router at every
step (32 Gumbel top-8 draws over its top-32 pool) and their exact CE is
recomputed — genuinely dynamic, not offline.

## Pre-registered reproduction criterion: MET

> held-out route value improves with a 95% CI excluding 0, AND preference
> accuracy rises above its measured init value, AND free generation does not
> degrade significantly.

| leg | before | after (ep8) | verdict |
|---|---|---|---|
| held-out route value | 0.000 | **+0.946** [+0.710, +1.194] | PASS |
| preference accuracy (fixed support) | 0.402 | 0.550 | PASS |
| free-gen accuracy, 120 FG0 problems | 0.475 | 0.492, diff **+0.017** [−0.033, +0.067] | PASS (not degraded) |

Win rate on route value 0.688; experts changed per token 4.43 of 8; identical
completions between the two arms **0.008**.

So the chain — EPO objective, route likelihood surrogate, reference anchoring,
CE-gap weighting, Gumbel sampling, exact replay, gate update — is functional
end to end. **第三关 (dynamic Exact-EPO at L36) may run.**

## What this does NOT say, stated plainly

1. **This is not a replication of the parent's benchmark result.** The criterion
   asked free generation not to *degrade*; it did not ask for a gain, and the
   +0.017 it produced is not significant at n=120. E09 validates the
   implementation, not the parent's headline.
2. **99.2% of completions changed and accuracy did not.** A route-value gain of
   +0.95 nats per scored token at the final layer rewrote essentially every
   generation and moved accuracy by an amount indistinguishable from zero. That
   is a real caution to carry into 第三关: route value and generation quality
   are not the same currency, and the first is much easier to move.
3. **Preference accuracy moved far less than route value.** 0.402 → 0.550,
   against a route-value gain that is large and significant. If the router had
   absorbed the per-token *preference* the objective encodes, that number should
   have moved more. The likelier reading is that it found a direction that
   lowers CE broadly on hard tokens rather than a per-token route ordering —
   the same shape as E06/E07's wholesale route rewriting (3.2–3.4 experts
   changed there, 4.4 here).
4. Init preference accuracy is **0.402, below chance**: the base router's own
   likelihood ordering anti-correlates with exact CE on these candidate pairs.
   That is a fact about the base model worth keeping, not an artefact of
   training.

## Implementation notes that cost something

* L47 is the last decoder layer, so only the position-wise final norm and
  `lm_head` follow it: patching the MoE output at `t` moves the CE at `t` and
  nowhere else, and `x_t` does not depend on the L47 gate. A fully dynamic run
  therefore needs one collection pass plus arithmetic on cached tensors — no 30B
  backbone in the training loop. **This is exactly the property CT03 loses at a
  non-final layer, and the reason 第三关 costs real compute.**
* All 128 expert outputs are cached per token, not the base top-32, so the pool
  may move anywhere during training without the cache silently constraining the
  action space.
* E09 uses the parent's `r+`/`r-` form (best vs worst sampled route). E06 used
  `r- = S0`, the router's own route, which made preference accuracy
  *structurally* 0 at init because the router's own top-8 maximises
  `sum log p` over 8-subsets by construction. Surfacing that divergence is part
  of what this reproduction was for.

## Status

CT03 remains **KILLED** as originally scoped (`CT-KILL-20260922-1`). E08 cleared
第一关 and E09 clears 第二关. Next: 第三关, dynamic Exact-EPO at L36, where the
exact utility is no longer a single-position quantity.
