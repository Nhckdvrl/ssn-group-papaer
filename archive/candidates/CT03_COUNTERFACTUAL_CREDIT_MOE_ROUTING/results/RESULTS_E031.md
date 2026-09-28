# CT03 E03.1 — Fixed-support re-evaluation of the C0 checkpoints

**Run:** 2026-09-20, `fvcrc20:0,1`, no training. Every arm scored as a *function*
on one frozen support: base-model hard tokens, base hidden states `x_l^base`,
fixed candidate universe `U = S_base ∪ C_base`, and exact utilities `u_ij`
computed once. 16 held-out problems × 8 tokens × 3 layers × (32 swaps + 2 routes
per arm). Source: `src/e031_fixed.py`.

## Why this run exists

C0's A/B/D were not matched comparisons. `eval_router` recomputed `sel, cand`
from each arm's *own* router, and re-selected hard tokens from each arm's *own*
CE quartile — so different arms could be measured at different positions, around
different routes, against different candidates. Only held-out CE survived that.

E03.1 removes all three degrees of freedom and replaces the moving-neighbourhood
regret with a quantity that cannot drift:

```
V_arm = L(S_arm ; x_base) - L(S_base ; x_base)      negative = genuinely better
```

Two variants are replayed, because "which experts" and "what weights" are
different claims: `route_armw` (arm's experts, arm's renormalised weights,
deployment-faithful) and `route_basew` (arm's experts, base weights, isolating
selection). This also repairs C0's `dL_revert`, which had mixed base expert ids
with trained weights and trained upstream state.

## Result 1 — the anticipated retraction does not happen

`A_fixed = rho(s_j^arm - s_i^arm, u_ij^exact)` on the same 32 base pairs:

| layer | base | cf_only | shuffled | cf_anchor |
|---|---|---|---|---|
| 28 | −0.011 | −0.004 | −0.008 | +0.016 |
| 36 | −0.028 | −0.011 | −0.009 | +0.021 |
| 44 | −0.024 | **+0.078** | −0.043 | +0.005 |

It was reasonable to expect that C0's `A ≈ 0` was an artefact of moving support
and that `cf_only` would separate from `shuffled` once the support was frozen.
**It does not.** On matched support the alignment is still ~0 everywhere, with
only L44 nudging up. The C0 conclusion "no utility-aligned ordering was learned"
therefore stands, now on a valid measurement.

## Result 2 — but the corrected route metric does discriminate

Paired bootstrap, `cf_only − shuffled`, 128 tokens/layer:

| layer | variant | diff | 95% CI | significant |
|---|---|---|---|---|
| 28 | route_armw | −0.0331 | [−0.084, +0.003] | no |
| 28 | route_basew | −0.0033 | [−0.024, +0.018] | no |
| 36 | route_armw | −0.0496 | [−0.112, −0.002] | **yes** |
| 36 | route_basew | −0.0157 | [−0.039, +0.004] | no |
| 44 | route_armw | −0.0970 | [−0.187, −0.025] | **yes** |
| 44 | route_basew | −0.1001 | [−0.195, −0.023] | **yes** |

At L44 with base weights — i.e. **expert selection alone** — `cf_only` reaches
−0.0845 while `shuffled` is **+0.0156**, worse than the base route. So in the
deep layers the choice of experts is credit-specific, not generic perturbation.
Unlike C0's regret, this metric separates the arms.

## Result 3 — and the effect is entirely tail-driven

| L44 route_armw | mean | median | frac < 0 | p10 | p90 |
|---|---|---|---|---|---|
| cf_only | −0.1478 | −0.0307 | 0.641 | −0.432 | +0.249 |
| shuffled | −0.0508 | −0.0076 | 0.602 | −0.305 | +0.251 |

Paired, **`cf_only` wins on only 51–57% of tokens**, with median differences of
−0.0007 to −0.0037. The significant mean difference is carried by a small tail
of large wins; the typical token is unchanged.

An earlier per-token capture ratio `V_arm / best_1swap` came out negative in most
cells, contradicting the negative aggregate means. That contradiction was the
heavy tail, not a bug, and the ratio is unstable when `best_1swap` is near zero.
It is recorded here rather than quoted as a result.

This reconciles the three C0 observations that looked unrelated: crossings helped
≈ 0.51 by count, `dL_revert` positive in mean, CE gain −0.056 nats. All three say
**a few tokens get large correct improvements and the rest is noise.**

## Diagnosis, combined with E03.5

- E03.5: the utility landscape **is** a scalar potential (R² 0.867 / 0.969 /
  0.999). The router could represent the target.
- E03.1: it did not acquire a calibrated ordering (A_fixed ≈ 0), yet its selected
  set is credit-specifically better in the deep layers, sparsely.

So the bottleneck is **the objective, not the representation**. The binary sign
target writes a sparse, heavy-tailed signal instead of a calibrated one, while
the margin-collapse shortcut dilutes it — which is why the shuffled arm fit the
loss slightly faster than the real one.

## What this changes for v1

The direction `credit → expert potential z* → router distillation` is unchanged,
but its **motivation is corrected**. It is not "restore the magnitude the
pairwise form discarded" — that claim was withdrawn in `RESULTS_E03_C0.md`.
It is:

1. `z*` gives every expert a **dense** target, addressing the sparse tail-driven
   signal that E03.1 exposes;
2. fitting `z*` has **no margin-collapse solution**, removing the shortcut both
   arms took;
3. `z*` is the principled answer to "what is the utility of expert j", which is
   otherwise undefined since only `u_ij` exists.

Standing requirements for every future run: the shuffled-label control as a
permanent arm, fixed support, per-problem CE for paired intervals, and reporting
medians and win-rates alongside means — the mean alone would have overstated
every effect in this run.
