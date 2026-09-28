# CT03 E01 — Results and adjudication

**Run:** 2026-09-20 · `allenai/OLMoE-1B-7B-0924-Instruct`, float32, one RTX PRO 6000
(host `fvcrc20`, card 0) · MATH-500 solutions, teacher-forced.
**Scale:** 32 problems × 8 tokens × 6 layers × 16 candidates = **24,576 records**.
**Design:** `docs/E01_DESIGN.md`, frozen at commit `0eef144` before any number existed.

## Verdict: CONTINUE

The §9 bar was: per-token median Spearman of `px_shared` vs `dL_seq` on
**hard | boundary**, averaged over non-final layers, `>= 0.5`; top-3 clearly
above chance; beats every baseline; not confined to the last layers.

| predictor | rho_med | top-1 | top-3 | norm. regret |
|---|---|---|---|---|
| **px_shared** | **0.698** | **0.548** | **0.816** | **0.195** |
| px_tok | 0.562 | 0.419 | 0.706 | 0.277 |
| router_gap | −0.019 | 0.178 | 0.442 | 0.497 |
| neg_dh_norm | −0.019 | 0.186 | 0.483 | 0.507 |
| dh_norm | 0.019 | 0.109 | 0.281 | 0.500 |
| random | 0.000 | 0.147 | 0.394 | 0.491 |

All four conditions pass. The baselines are the load-bearing part: **the router's
own score gap carries no information about which swap helps** (rho ≈ −0.02,
top-1 at the random floor). That is the parent's blind spot reproduced as a
measurement, and it means the proxy is not laundering the router's opinion.
Beneficial rate sits at ~0.50 in every cell, so the sign task is not degenerate.

## The estimand is real, and each gradient predicts its own

Cross-pairing the two proxies against the two exact quantities (rho_med, hard |
boundary | non-final; easy in parentheses):

| | vs `dL_tok` | vs `dL_seq` |
|---|---|---|
| `px_tok` | **0.876** (0.815) | 0.562 (−0.010) |
| `px_shared` | 0.652 (−0.036) | **0.698** (0.695) |

The diagonal is sharp. The gradient you back-propagate determines which loss you
can predict, and the off-diagonal collapses to zero on easy tokens — where the
token's own CE is near zero, so `dL_seq` is *entirely* downstream effect and has
nothing to do with `dL_tok`. Keeping these apart was the right call: had the
design measured only `px_tok` against only `dL_seq`, the method would have looked
dead (rho −0.01 on easy) when in fact both halves work against their own target.

For CT03 the relevant cell is `px_shared` → `dL_seq` = 0.698, because one shared
backward is what makes the method cheap and total sequence loss is what router
training actually moves.

The first-order term itself is *very* faithful: `px_tok` → `dL_tok` reaches
0.876 hard / 0.815 easy, top-1 0.72. Taylor is not the weak link.

## The real limitation: a steep depth gradient

`px_shared` → `dL_seq`, hard | boundary, per layer:

| layer | 1 | 4 | 7 | 10 | 13 | 15 |
|---|---|---|---|---|---|---|
| rho_med | 0.286 | 0.524 | 0.762 | 0.929 | 0.988 | 1.000 |
| top-1 | 0.273 | 0.352 | 0.492 | 0.727 | 0.898 | 0.984 |
| median \|dL_seq\| | 1.1e−1 | 1.3e−1 | 1.3e−1 | 8.2e−2 | 4.4e−2 | 2.9e−2 |

This passes the "not confined to the final layer" condition — layer 7 already
sits at 0.762 and layer 10 at 0.929 — but the honest reading is that **the
average is carried by the deep half**. Layer 1 alone (0.286) falls in the
design's explicit "in between" band, above the 0.25 kill line and below the 0.5
continue line.

That is an uncomfortable shape rather than a convenient one, and it should be
stated plainly in any paper: the approximation degrades exactly where the
perturbation has the most remaining network to propagate through, which is also
**where exact rerouting is most expensive**. Early layers are the costly ones to
supervise and the ones the surrogate serves worst. This is the opposite of a
free lunch, and it is the first thing a reviewer will find.

## Cost

Measured exact replay, and analytic FLOPs per candidate:

| layer | exact GFLOP | proxy GFLOP | ratio | measured exact s/cand |
|---|---|---|---|---|
| 1 | 274.7 | 2.10 | **131×** | 0.0391 |
| 7 | 168.4 | 2.10 | 80× | 0.0230 |
| 13 | 62.1 | 2.10 | 30× | 0.0067 |
| 15 | 26.7 | 2.10 | 13× | 0.0014 |

**The advantage must be quoted as ~131×, not ~22,000×.** The local expert MLP is
only 12.6 MFLOP, but the shared backward costs 1599 GFLOP per sequence, and at
the 768 candidates/sequence harvested here that amortises to 2.08 GFLOP per
candidate — i.e. the backward, not the expert forward, dominates the proxy.
Reporting the expert forward alone would overstate the gain by ~170×.

Two consequences. First, the amortisation improves as more candidates are
harvested per backward, which is a genuine argument *for* CT03's multi-layer
pitch rather than a rhetorical one: the shared backward is a fixed cost that
multi-layer, multi-token credit spreads thinner. Second, the last-layer ratio of
13× is modest, which is consistent with the registration's concern that
final-layer rerouting is already cheap — the surrogate earns its keep in depth.

## Measurement integrity

`src/e01_validity.py` passed all three checks before the run (log:
`results/logs/e01_validity.log`): replay identity to 1.6e−5 CE, route algebra to
fp32 roundoff (3e−9 … 1e−7), and replay `dL_seq` matching a genuine full forward
with a routing-override hook to 1.6e−5 / 3.3e−5 / 6.0e−5 at layers 1 / 7 / 15.

That third figure drove a design change. The full-forward-vs-replay gap (~3e−5)
is negligible against layer-1 effects (1.1e−1) but is ~15% of a layer-15 effect
(2.9e−2 median, with a long tail toward 1e−4). Taking the baseline from the full
forward and the patched CE from the replay would have injected that path
difference into every deep-layer `dL` — precisely the regime the final-layer kill
condition turns on. Each batch therefore carries a **zero-patch row through the
identical replay**, and `dL` is measured against it, so the paths cancel.
`replay_base_drift` is logged per record so the residual stays visible.

## What E01 does not establish

- One model, one family, one task. OLMoE was chosen partly because
  `norm_topk_prob=false` makes the swap exact; a renormalising router adds a
  term this measurement never had to face.
- Faithful ranking is not a trained router. Nothing here shows that distilling
  these utilities improves a benchmark.
- Single-expert swaps only. The registration's own HOPE-inspired caution — that
  first-order credit may degrade for simultaneous multi-expert changes — is
  untested and remains a live risk.
- Tokens are CE-quartile strata on teacher-forced gold solutions, not the
  parent's fragile *reasoning* tokens under the model's own generations.

## Next gate, per registration §7

Stage B is authorised in principle but the depth gradient should be understood
first, since it bounds what multi-layer supervision can buy. Do **not** reach for
the §7 refinements (second-order correction, per-layer temperature, uncertainty
filter) — those are gated behind evidence, and "layer 1 is weak" is not yet
evidence about *why*.
