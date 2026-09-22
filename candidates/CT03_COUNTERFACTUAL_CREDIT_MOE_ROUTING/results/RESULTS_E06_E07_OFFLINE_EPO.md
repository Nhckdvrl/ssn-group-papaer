# CT03 E06/E07 — offline exact-EPO gate at non-final layers

**Run:** 2026-09-22, Qwen3-30B-A3B fp32 · 119 problems (79 train / 40 held-out,
problem-disjoint) × 8 hard tokens × L36/L44 = 1,902 cells with exact downstream
CE. Only the 128×2048 gate matrix trains, from the **pretrained** gate, on cached
`x_t`. `src/e06_offline_epo.py`, `src/e07_score_picks.py`.

## The question

CPD's failure was established against two action mechanisms we invented. The
parent's own — EPO, which uses **exact** CE to pick `r+/r-` and a
reference-anchored, gap-weighted preference update — was never tried at a
non-final layer. So: given the best possible (exact) counterfactual preference,
can a standard linear router absorb it and generalise across problems?

`log pi(S|x) = sum_{e in S} log p(e|x)` is **my** surrogate for the route
likelihood; the parent's exact form was not available to me. Stated because it
matters for reproduction.

## Result: route value improves, but not via the claimed mechanism

Exact value of the route the trained router actually picks, held-out problems:

| layer | n | V_trained | V_base | paired diff | 95% CI | win rate | experts changed |
|---|---|---|---|---|---|---|---|
| **L36** | 328 | −0.0673 | 0.0000 | −0.0673 | **[−0.137, −0.007]** | 0.470 | 3.16 |
| L44 | 328 | −0.0727 | −0.0000 | −0.0727 | [−0.151, +0.002] | 0.540 | 3.36 |

Negative is better. **L36 is significant; L44 is not.** Preference accuracy on
held-out problems rises from a *structural* floor of 0.000 — `r-` is the
router's own top-8, which maximises `sum log p` over 8-subsets by construction —
to 0.637 (L36) and 0.822 (L44).

Three things must be read together with that:

1. **Win rate is 0.47–0.54.** L36 is significant in the mean while winning on
   *fewer than half* the tokens: a few large gains against many small losses.
   The same heavy tail E03.1 found, again.
2. **3.2–3.4 experts change per token.** EPO's objective constrains exactly one
   comparison (`r+` beats `r-`), and the router satisfies it by reordering the
   whole candidate region — not the small directed correction the method wanted.
   Different mechanism from CPD's margin collapse, same species of shortcut.
3. **`A_delta` stays ~0** (L36 −0.018, L44 +0.041). Even with exact labels and
   the parent's validated objective, the router does not acquire a token-level
   utility-aligned direction. Two entirely different objectives now agree on this.

So non-final exact supervision *can* move route value, but **not by learning the
counterfactual direction**. That is not the mechanism CT03 claimed.

## Four implementation bugs found in this round

Each would have produced or hidden a wrong number:

| bug | effect |
|---|---|
| `-torch.log(-torch.log(u).clamp_min(eps))` parses as `-(log(u).clamp_min(eps))` → NaN | one identical Gumbel route across all 60,864 draws; nearly published a false 0.934 action-space ratio |
| `mix()` called `moe.experts[e](x)` inside the per-route loop | 512 single-token matmuls per cell; 1–2% GPU utilisation (spotted by the user) |
| unfound router picks scored as `0.0` | silently reported "no change" for **93–98%** of test cells — exactly the cases of interest |
| per-sample autograd over a 128×2048 matrix | 2h15m CPU across 19 threads without reaching the first eval; 26s once vectorised |

The third is the most dangerous: a default value that happens to mean "no
effect" turns missing measurement into a null result.

## Status

CT03 remains **KILLED** (`CT-KILL-20260922-1`). This gate was run because the
parent's action mechanism had never been tested off the final layer. It does not
reverse the kill: the significant L36 effect is tail-driven, comes with wholesale
route rewriting, and arrives **without** the credit-direction alignment that was
the point. A dynamic GPU EPO run would only scale up a mechanism that is not the
one claimed.
