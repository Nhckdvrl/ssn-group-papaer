# E09 — Reproduce the parent's final-layer (L47) Exact-EPO

**Frozen 2026-09-22, before any E09 run.**

## Why this exists

E08 cleared its gate, so the next question is whether exact counterfactual
supervision trains a better router. Before touching a non-final layer, this
reproduces the parent's simplest setting with OUR implementation of the EPO
objective, route likelihood, reference anchoring, CE-gap weighting, Gumbel
sampling and exact replay. If L36 later fails, this is what lets us say whether
it failed as science or as a bug.

Nothing here is novel and nothing here uses the proxy. The proxy enters only at
第四关.

## A structural fact that makes L47 cheap

Layer 47 is the last decoder layer. After it come only the final RMSNorm and
`lm_head`, both position-wise. So patching the MoE output at position `t`
changes the CE at position `t` **and nowhere else** — there is no downstream
sequence to replay.

Two consequences, both stated up front:

1. Exact utility at L47 is `u_r = CE_t(base) - CE_t(r)`, a single-position
   quantity. That is why the parent's final-layer EPO is cheap, and it is
   exactly the property CT03 loses at non-final layers.
2. `x_t` (the L47 MoE input) does not depend on the L47 gate, because the gate
   only affects layer 47's own output. So `x_t`, the residual stream entering
   the block, and every expert's output `E_e(x_t)` can be cached ONCE and the
   whole training run needs only the cached tensors, the final norm and
   `lm_head` — a 1.2GB slice of the model, not the 30B backbone.

The run is therefore genuinely dynamic (routes are resampled from the CURRENT
router at every step, and the exact CE is recomputed for them) while costing
one collection pass plus arithmetic. No approximation is bought with this.

All 128 experts are cached per token, not just the base top-32, so the pool may
move anywhere during training without the cache silently constraining it.

## Objective (the parent's form)

Per token, sample `n_g = 32` Gumbel top-K routes over the CURRENT router's
top-32 pool. Let `r+` be the sampled route with the lowest exact CE and `r-` the
one with the highest.

    delta   = CE(r-) - CE(r+)                                    >= 0
    margin  = [logpi_theta(r+) - logpi_ref(r+)]
            - [logpi_theta(r-) - logpi_ref(r-)]
    loss    = -delta * log sigmoid(beta * margin)

`logpi(S|x) = sum_{e in S} log p(e|x)` is MY surrogate for a set's likelihood,
not a reproduction of the parent's definition. It is the same surrogate E06
used, so the two are comparable; it is stated rather than implied.

**This differs from E06 on purpose.** E06 set `r- = S0`, the router's own route,
which made preference accuracy structurally 0 at init (the router's own top-8
maximises `sum log p` over 8-subsets by construction). Here both `r+` and `r-`
are sampled, so the init value is a real quantity and the metric is informative.
That divergence is one of the things this reproduction exists to expose.

Only the L47 gate matrix trains. The reference router is the pretrained gate,
frozen.

## Evaluation (held-out problems, disjoint from training)

1. **Preference accuracy** on a FIXED candidate support drawn once from the
   REFERENCE router, so the evaluation set does not move with training.
2. **Route value** `V = CE_t(base route) - CE_t(trained router's route)`, exact,
   paired bootstrap over held-out problems.
3. **Free generation** on the 120 locked FG0 dev problems, base vs trained,
   identical greedy decoding.

## Reproduction criterion (pre-registered)

> The implementation is treated as unbiased iff, at L47, held-out route value
> improves with a 95% CI excluding 0, AND preference accuracy rises above its
> measured init value, AND free generation does not degrade significantly.

If L47 fails, **第三关 (dynamic exact-EPO at L36) does not run** — the chain has
a defect and a non-final result would be uninterpretable.

## Validity checks — gate the run

1. **Route reconstruction.** `mix(bank, S0, p0)` equals the block's own `h_0` to
   rel. 1e-4, and `lm_head(norm(resid + h_0))` reproduces the full forward's CE
   at `t` to 1e-4. This is what makes the cached path exact.
2. **Locality.** Patching at `t` leaves CE at every other position bit-identical.
   Asserted once against a full replay, since the whole cheap-cache argument
   rests on it.
3. **Gumbel diversity.** >= 8 distinct routes among 32 draws (the E06 NaN tell).
4. **Pool coverage.** The current router's top-32 is always inside the cached
   bank — trivially true at 128 experts, asserted so it stays true if the cache
   is ever narrowed.
5. **Train/test problem disjointness**, asserted, and the FG0 dev pool disjoint
   from both.

## Scale

150 problems for training, 60 held out, 6 high-CE tokens each, from the locked
`cpd_trainpool.json`. Collection: full model over 2 cards, one pass. Training
and route-value evaluation: one card. Free generation: full model.
