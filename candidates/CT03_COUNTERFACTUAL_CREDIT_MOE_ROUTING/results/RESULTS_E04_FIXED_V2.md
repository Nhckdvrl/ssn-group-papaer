# CT03 Fixed-Support v2 — did the router learn the counterfactual direction?

**Run:** 2026-09-21/22, `fvcrc20:0,1`, Qwen3-30B-A3B fp32 · 24 problems from the
locked FG0 pool × 8 hard tokens × 3 layers × 4 checkpoints = 2,304 rows, one
frozen support (base tokens, base hidden states, base candidate universe, exact
utilities computed once). No training. `src/e04_fixed_v2.py`.

## Why the metric changed

`CPD_V1_DESIGN` named `A_fixed = rho(s_theta_j - s_theta_i, u_exact)` as the
mechanism judge. **That was mis-specified.** CPD learns `s_theta ~= s_0 + beta*z`,
and `s_0`'s own pairwise differences are uncorrelated with utility (base
`A_fixed ~ 0`). With a small trust region the large, utility-irrelevant `s_0`
term dominates, so `A_fixed` can sit near zero even if the correction is
perfectly aligned. The mechanism lives in the **correction**:

```
A_delta = rho( (s_theta_j - s_theta_i) - (s_0_j - s_0_i),  u_exact_ij )
A_z     = rho( gauge-centred (s_theta_e - s_0_e) on U,     z*_exact_e )
```

since the target literally is `delta_s_e ~ beta * z_e`.

## Result: nothing is significant. This is the bad branch.

Paired bootstrap, 10k resamples, 192 tokens per cell:

| metric | layer | router_ce | shuffled | **cpd** | cpd − shuffled |
|---|---|---|---|---|---|
| A_delta | L36 | +0.034 ns | +0.008 ns | **+0.008 ns** | −0.000 ns |
| A_delta | L44 | +0.025 ns | −0.023 ns | **+0.030 ns** | +0.053 ns |
| A_z | L36 | +0.038 ns | +0.019 ns | **+0.027 ns** | +0.008 ns |
| A_z | L44 | +0.008 ns | −0.004 ns | **+0.036 ns** | +0.040 ns |

Every confidence interval contains zero. CPD's best cell, `A_delta` at L44, is
+0.0296 with CI [−0.019, +0.077].

The per-token **median** at that cell is +0.071 and looks like a signal; the mean
is +0.030 and the interval crosses zero. The distribution is heavy-tailed and the
median misleads — the same lesson E03.1 taught, applied against our own
preferred reading this time.

## Route quality: CPD is not better than ordinary CE tuning

| arm | V_route L36 | V_route L44 | realized KL | experts changed |
|---|---|---|---|---|
| router_ce | −0.0370 | **−0.0698** | 0.245 | 0.97 |
| **cpd** | −0.0291 | −0.0374 | 0.198 | 0.89 |
| shuffled | −0.0112 | +0.0098 | 0.044 | 0.81 |

Paired: `cpd − router_ce` is **positive** (i.e. CPD worse) at both trained layers,
+0.008 and +0.032, ns. CPD does beat shuffled numerically (−0.018, −0.047) but ns.

This also retires a reading from the previous write-up. "CPD achieves more with
half the displacement" came from comparing free-generation shared-prefix KL
(0.0168 vs 0.0348). On fixed support the router-level displacements are 0.198 vs
0.245 — 1.24x, not 2x — and those are different quantities (router distribution
KL vs next-token LM KL). They should not have been narrated as one.

## The control layer failed

L28 was included as an untrained control to give a noise floor. It returns all
NaN: an untrained layer has `delta_s = 0` exactly, so the correlation is
undefined. It reports only the tautology "untrained means unchanged" and supplies
no floor. The question "is A_delta = 0.03 a signal?" is therefore answered only by
the bootstrap CI, which says no. A usable floor would need e.g. a random-direction
correction of matched magnitude.

## What this means

Three independent lines now fail to support the credit-specific claim:

1. free generation — CPD vs shuffled and vs router_ce both ns (`RESULTS_CPD_V1.md`);
2. mechanism — `A_delta` and `A_z` indistinguishable from zero for every arm;
3. route quality — CPD no better than ordinary CE tuning, numerically worse.

CPD's **+5.8 points over base in real free generation is real and significant**.
But the most parsimonious account is that it comes from router-only adaptation
as such, not from the counterfactual potential this project spent its effort
recovering. Under the pre-registered tree this is the branch where the response
is *not* to add baselines or a second model family, but to ask whether CPD needs
to exist.

**The estimator half is untouched by this.** E01/E01.5/E02 (proxy fidelity,
cross-family replication, cost), E03.5/.6 (integrability, proxy-vs-exact
potential) and E03.7 (interaction vs estimation) stand on their own evidence and
say nothing about distillation. What has failed is the step from *credit* to
*router policy*.

## Power caveat, stated without using it as an excuse

192 tokens per cell with per-token Spearman over 32 pairs gives CI half-widths of
about ±0.045. An effect of 0.03–0.07 sits at the resolution limit, so this run
cannot exclude a small true alignment — it simply provides no support for one.
Anything that claims otherwise needs more tokens, not a softer reading.
