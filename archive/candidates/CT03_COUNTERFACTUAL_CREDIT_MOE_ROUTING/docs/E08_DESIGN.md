# E08 — Full-route (EPO action space) screening audit

**Frozen 2026-09-22, before any E08 run.** Nothing here trains anything.

## Why this experiment exists

E05 measured the screening curve on the **one-swap** space `S' = S - {i} + {j}`
and got retained-oracle-gain 0.937 / 0.962 at m=4 (L36 / L44). E06 then showed
that one-swap is only 0.822 / 0.870 of the union oracle and, more importantly,
**is not the action space EPO searches**: parent EPO samples full Gumbel top-K
routes from a top-32 expert pool, which change several experts at once.

So the E05 numbers cannot be quoted as "we cut EPO's exact reruns by 8x". This
experiment measures the screening curve in EPO's own action space, and it is the
gate on whether a dynamic exact-EPO run is worth opening cards for.

## Object

Per (token, layer) cell:

* pool `U` = the top-32 experts by base router probability `p0` (parent's pool);
* `n_g = 32` routes `r_1..r_32`, each a Gumbel top-K draw over `log p0[U]`
  (K = 8), i.e. exactly parent EPO's sampler;
* **proxy** `u_hat_r = -g^T (h_r - h_0)`, one shared backward per problem;
* **exact** `u_r = L(r_0) - L(r)`, full downstream replay of every unique route.

With `h_r = (sum_{e in r} p_e E_e(x)) / Z_r`, `Z_r = sum_{e in r} p_e`, the proxy
for the whole candidate set costs **|U| = 32 expert forwards and 32 dot
products**, not one forward per route:

    g^T h_r = (sum_{e in r} p_e * (g^T E_e)) / Z_r

so `u_hat` for all 32 routes is arithmetic on 32 cached scalars. This is the
same scalar trick used for the one-swap grid in E03.6.

## Primary metric (fixed now)

Over the **deduplicated** candidate set `R` of a cell, ranked by `u_hat`:

    R_m = max_{r in TopM_uhat(R)} u_r  /  max_{r in R} u_r

restricted to cells where `max_r u_r > 0` (a beneficial route exists; otherwise
"retained gain" is undefined). Report the mean over cells with a paired bootstrap
CI over **problems**, plus the fraction of cells excluded.

`m in {1, 2, 4, 8, 16, 32}`.

## Continue threshold (pre-registered)

> **There exists `m <= 8` with mean `R_m >= 0.90` at BOTH L36 and L44.**

m=8 still removes >= 75% of exact reruns. If this fails, the "efficient EPO
search" story is materially weaker and no dynamic training run is opened.

L28 is reported as a depth boundary only. It does **not** enter the gate.

## Secondary (reported, not decisive)

* exact-best recall (the argmax route is inside top-m);
* Spearman `rho(u_hat, u)` over the 32 routes, per cell, median;
* beneficial-route recall (share of routes with `u_r > 0` inside top-m);
* mean regret `max_R u - max_TopM u`;
* number of unique routes per cell (duplicates are real: EPO samples with
  replacement, and a deduped pool is what a sane implementation exact-evaluates);
* wall-clock per cell for proxy vs exact.

## Validity checks — the run does not start unless all pass

Every previous stage of CT03 had a real defect caught by exactly this kind of
check, so they gate rather than decorate.

1. **Base-route reconstruction.** `mix(bank, S0, p0)` equals the block's own
   `h_0` to rel. 1e-4. Catches a wrong renormalisation or a wrong pool.
2. **Replay identity.** Row 0 of the replay is a ZERO patch through the
   identical path; its per-token CE must equal the full forward's to 1e-4.
   (The E01 fp32 lesson: the baseline must not come through a different path.)
3. **Scalar-trick identity.** Analytic `g^T (h_r - h_0)` equals a directly
   computed `g^T (mix(bank, r, p0) - h_0)` to rel. 1e-5 on sampled routes.
4. **Gumbel diversity.** >= 8 distinct routes among 32 draws on a typical token,
   and the mean number of changed experts is not an integer constant across
   layers. This is the exact tell that caught the `clamp_min` NaN sampler in
   E06, which produced ONE identical route across 60,864 draws.
5. **Gradient sanity.** `cap.mlp_out[l].grad` is not None, finite, nonzero.
6. **Null-route noise floor** (added 2026-09-22, before the full run). Every
   cell replays the BASE route through the patch path as an extra row. Its true
   utility is exactly 0, so its measured `u` is that cell's measurement noise.
   `u` is a sum of per-position CE over the whole suffix, and the fp32
   replay gap is ~3e-5 per position, so a few hundred positions can accumulate
   to ~1e-2 -- comparable to the gaps `R_m` ranks. This check turns that from an
   assumption into a reported number. It was added after the batched-replay
   rewrite changed `u` by up to 3.0e-2 (mean 1.5e-2) against the per-cell
   implementation while leaving `u_hat` bit-identical, which is the signature of
   fp32 batch-dependent reduction order, not of a logic change.
7. **Cross-composition replicate** (added 2026-09-22, before the full run). Check
   6 turned out to measure the EASY case: the null route's patch is ~0, so its
   trajectory stays numerically glued to the baseline's and the errors cancel.
   A real route diverges, and a 1e-7 rounding difference amplifies through 20-50
   layers. The honest measurement is therefore a replicate of the same cells
   under a DIFFERENT row-batch composition.

   Measured on 48 smoke cells, chunk_rows 64 vs 288:

   | quantity | result |
   |---|---|
   | `u_null` (check 6) | median 1e-5, p90 6e-5 |
   | per-route `\|du\|` across compositions | mean 2.0e-3, max 3.2e-2 |
   | median gap between best and 2nd-best route | 0.029 - 0.041 |
   | exact-argmax flips | **0 / 48** |
   | `R_m` reproducibility | **<= 1e-4 at every m** |

   So individual `u` values wobble at ~6% of the best-vs-2nd gap, but neither the
   argmax nor `R_m` moves. `u_hat` is bit-identical across compositions, as it
   must be -- it never touches the replay.

## Replay batching (efficiency, not semantics)

The layer's tokens are replayed in ONE row-batch rather than one call per token.
Rows are independent -- a row patched at `t` does not affect a row patched at
`t'` -- so this is an identity transform up to fp32 reduction order (see check
6). It exists because one call per `(token, layer)` walks the remaining decoder
layers in Python, and Qwen3Moe loops its 128 experts inside each layer, which
left the cards at 1-2% utilisation. Each chunk carries its own zero-patch row 0,
so the baseline still comes through the identical numeric path as the rows it is
subtracted from.

## Scale and resources

80 problems from the locked `results/cpd_trainpool.json` (MATH train, disjoint
from the FG0 dev pool), 8 high-CE tokens each, layers {28, 36, 44} => ~1920
cells. Two workers, each `device_map="auto"` fp32 over 2 idle cards on this host
= 4 cards total, within the 8-card-per-topic budget.

## What this experiment cannot say

It measures **screening fidelity inside EPO's action space**. It says nothing
about whether exact EPO at L36 trains to a better router — that is the next gate
(第三关), and it is not opened by this one alone.
