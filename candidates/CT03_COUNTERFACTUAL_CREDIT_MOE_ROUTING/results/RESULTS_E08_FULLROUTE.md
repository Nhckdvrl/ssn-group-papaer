# E08 — Screening curve in EPO's own action space

Design frozen before the run: `docs/E08_DESIGN.md`. Nothing here trains anything.
159 MATH-train problems (the locked `cpd_trainpool.json`, disjoint from the FG0
dev pool), 8 high-CE tokens each, layers {28, 36, 44}, **3813 token-layer cells**,
32 parent-style Gumbel top-8 routes per cell over the top-32 expert pool.
Two workers x 2 cards (fvcrc20, GPUs 0-3), ~40 min wall-clock.

## Result: the pre-registered gate PASSES

> **Threshold (frozen): there exists `m <= 8` with mean `R_m >= 0.90` at BOTH
> L36 and L44.**
> **PASS at m = 2** (L36 0.938, L44 0.976). L44 already passes at **m = 1**.

`R_m` = retained oracle gain, mean over cells with a beneficial route, 95% CI
from a paired bootstrap over problems.

| m | L36 `R_m` | 95% CI | L44 `R_m` | 95% CI | exact reruns saved |
|---|---|---|---|---|---|
| 1 | 0.881 | [0.867, 0.895] | **0.952** | [0.944, 0.959] | 97% |
| 2 | **0.938** | [0.927, 0.948] | **0.976** | [0.970, 0.982] | 94% |
| 4 | 0.969 | [0.961, 0.977] | 0.990 | [0.986, 0.993] | 87% |
| 8 | 0.988 | [0.983, 0.992] | 0.996 | [0.993, 0.998] | 75% |
| 16 | 0.997 | [0.995, 0.999] | 0.999 | [0.998, 1.000] | 50% |

L28 (boundary, does not vote): 0.748 / 0.848 / 0.922 / 0.966 at m = 1/2/4/8 —
it clears 0.90 only at m = 4, consistent with every earlier depth result.

Secondary, at m = 4: exact-best recall 0.761 / 0.887 / 0.961 (L28/L36/L44),
mean regret 0.019 / 0.007 / 0.003 against a median oracle gain of 0.24 / 0.28 /
0.32. Per-cell Spearman `rho(u_hat, u)` median **0.794 / 0.937 / 0.979**.

Measured cost: proxy 52.8s vs exact 1068.0s for 1893 cells (shard A; shard B
53.0s vs 1112.7s) — **~20x**, and the proxy figure already carries its share of
the one shared backward per problem.

## This is a different action space from E05, and now that is quantified

E05 measured screening on the one-swap space and got 0.937 / 0.962 at m = 4.
Those numbers could not be quoted as "we cut EPO's reruns by 8x", because:

| | L28 | L36 | L44 |
|---|---|---|---|
| mean experts changed vs base route | 4.40 | 4.25 | 4.03 |
| **share of sampled routes that are one-swap** | **0.4%** | **0.7%** | **1.1%** |

So ~99% of what EPO actually evaluates was outside the space E05 measured. The
curve had to be re-measured there, and it holds up — at L36/L44 it is in fact
*better* than the one-swap curve (0.969 / 0.990 vs 0.937 / 0.962 at m = 4).

I will not dress that up as the proxy being more accurate on full routes. The
likelier reading is that full routes are spread further apart in utility
(median oracle gain 0.28-0.32 against a median `|u|` of 0.11), and ranking is
easier when the candidates are further apart. Fidelity and rankability are not
the same quantity; E08 measures the second, which is the one screening needs.

## Measurement precision

`u` is a sum of per-position CE over the whole suffix, so fp32 replay error
accumulates. Two checks (`docs/E08_DESIGN.md` 6-7) bound it:

* null row per cell (base route through the patch path, true `u` = 0): median
  **1e-5**, p90 1e-4, against a `u` IQR of 0.16-0.20;
* replicate of 48 cells under a different row-batch composition: per-route
  `|du|` mean 2.0e-3 / max 3.2e-2, **0/48 exact-argmax flips**, `R_m`
  reproducible to **1e-4**.

The null control alone would have been self-flattering — a null patch keeps the
trajectory glued to the baseline, so its errors cancel. The replicate is the
operating case: individual `u` values wobble at ~6% of the best-vs-2nd gap, and
neither the argmax nor `R_m` moves.

## What this does NOT establish

1. **Screening is measured at the pretrained router.** During EPO training the
   router moves, and the proxy's fidelity at a moved router is untested. E04's
   `A_delta ~ 0` is a standing reason not to assume it transfers.
2. `u` is teacher-forced suffix CE on a gold solution, not generation quality.
3. Tokens are sampled from the top-CE quartile, as in every CT03 stage. 49-51%
   of sampled routes beat the base route on these tokens; on easy tokens that
   fraction would be far lower and the oracle gain smaller. The curve is a
   statement about the tokens EPO would actually spend its reruns on, not about
   all tokens.
4. **This says nothing about whether exact EPO at L36 trains to a better
   router.** That is the next gate, and E08 does not open it by itself.

## Status

CT03 remains **KILLED** as originally scoped (`CT-KILL-20260922-1`). This is the
narrow reopening path: the estimator as a *screening* mechanism for the parent's
own validated action mechanism. E08 clears its own gate. The next question —
第二关 — is reproducing parent EPO at L47 with this implementation, so that a
later L36 result can be attributed to science rather than to a bug.
