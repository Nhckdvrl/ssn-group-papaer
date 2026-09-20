# CT03 Stage C0 (E03) — Counterfactual Credit Distillation v0

**Run:** 2026-09-20, `fvcrc20:0,1` · Qwen3-30B-A3B fp32, routers at L28/36/44 only
(786k trainable params) · 300 steps × 768 pairs, MATH-500 train / 16 held-out.
**Design:** `docs/E03_C0_DESIGN.md` + its 2026-09-20 amendment (exploration tree).

## Headline: a real but modest credit-specific effect, and one dead metric

Two controls were run that were not in the original design. Both were necessary,
and both changed the conclusion.

| arm | held-out CE | Δ vs base |
|---|---|---|
| base | 1.2197 | — |
| **temperature** (flatten base logits, zero training) | 1.2165 | −0.0032 |
| **shuffled labels** (identical pipeline, credit content destroyed) | 1.1767 | −0.0430 |
| cf_only | **1.1209** | **−0.0987** |
| cf_anchor | 1.1288 | −0.0909 |

- **Credit-specific gain = −0.0557 nats** (cf_only vs shuffled).
- **43.5% of the raw gain is non-specific** — reproduced by random labels.

So CCD v0 does something real, and less than it first appeared.

## Control 1 rejected my own leading hypothesis

The CF loss has a degenerate optimum at `s_i == s_j`, and training compressed the
selection margin ~45%. I proposed that the CE gain was that flattening. It is not:
scaling the base router's logits to reproduce the margin exactly (T = 1.59 / 1.75
/ 2.39) moves CE by only **−0.003** of the −0.099.

Why: scaling gate weights is order-preserving, so the top-8 membership is
**unchanged** (overlap 1.000). The control isolates flatter mixing over the same
experts, and that is worth almost nothing. The gain therefore comes from
**changed route membership**, not from flatter weights.

## Control 2 killed metric B

| arm | B regret L28 | L36 | L44 |
|---|---|---|---|
| base | 0.1943 | 0.2009 | 0.3032 |
| shuffled | 0.1854 | 0.1691 | 0.2278 |
| cf_only | 0.1876 | 0.1648 | 0.2067 |

**Random labels reduce route regret as much as real credit does.** B was the
design's load-bearing metric — §5 said "B is what distinguishes those cases" —
and it does not distinguish anything.

The reason is a defect in how B was defined, not in the method: regret is measured
over *the model's own current* top-(k+4) neighbourhood, which moves when the
router moves. Any perturbation relocates the route to a neighbourhood with less
measurable headroom. **Regret measured on a moving neighbourhood is not a valid
before/after quantity.** A corrected version must fix the candidate set (e.g.
always the base router's ranks k+1..k+m) or score against a fixed oracle.

Without the shuffled control I would have reported "B fell, the method works".
That conclusion would have been wrong.

## What the other metrics say

- **A (score ↔ exact utility) never moved**: ~0 in every arm including shuffled.
  Partly expected — after the good experts move into the top-8, ranks 9–12 are
  leftovers — but it means C0 produced no evidence of a utility-aligned router.
- **D crossings helped ≈ 0.50 in every arm** (cf_only 0.516/0.520/0.508,
  shuffled 0.520/0.531/0.477). Realised crossings are a coin flip by count in
  both. `dL_revert` mean is positive (+0.016/+0.033/+0.039), so the helpful
  crossings are larger in magnitude — a noisy, positively-biased signal.
- **Routing changed massively, capability did not degrade**: overlap 0.41–0.64
  (3–5 of 8 experts change per token) yet held-out CE improved. Not collapse,
  but not the "small, directed change" the design hoped for.
- **The anchor arm was inert.** λ=0.02 gave an anchor term of 0.00144 against a
  CF term of 0.74 (0.2%), and its drift matched cf_only. It is a second seed of
  the same configuration, not a trust-region arm. The "effective but destructive"
  branch therefore has **no tested arm**.

## `L_CF` is not a valid progress signal

Loss fell 0.769 → 0.723 over 300 steps — and the **shuffled-label run fell
slightly faster** (0.7202 vs 0.7275 at steps 151–200), with a near-identical drift
trajectory. The pairwise objective has a shortcut (margin compression) that lowers
the loss without improving routing, and both arms took it. Any future version must
not use `L_CF` as its progress metric.

## Diagnosis against the amendment's tree

Closest row: **"A≈ B≈ — pairwise supervision did not write the information into
the router"**, with the qualification that a credit-specific CE effect of −0.056
nats does exist. The information is getting in, but weakly and not as a
utility-aligned ordering.

This is consistent with the amendment's own argument: `u_ij ≈ −ΔL(i→j)` is
continuous and the pairwise reduction `u_j > u_i` discards its magnitude. The
evidence now says that discarded magnitude is where the signal was.

## What C0 does not license

- No benchmark claim. Nothing here says AIME will move.
- Nothing about free generation. Every number is teacher-forced, which is kill-bar
  condition 3 in the amendment and still entirely uninstrumented.
- No conclusion about trust-region / selective update, because no such arm ran.

## Proposed v1, in evidence order

1. **Soft utility distillation** — `q_j ∝ exp(−ΔL̂_j/τ)`, fit the router's
   candidate distribution to `q` by KL. Directly restores the magnitude the
   pairwise form throws away, which is the one thing the data points at.
2. **Fix metric B** before trusting any of it: fixed candidate neighbourhood, and
   keep the shuffled-label control as a standing arm in every future run.
3. Only then: set-aware targets, or a real trust region with a λ chosen from the
   measured KL scale rather than guessed.
