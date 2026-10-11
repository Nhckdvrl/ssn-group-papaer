# CT03 Stage B (E02) — Cross-family calibration on Qwen3-30B-A3B

**Run:** 2026-09-20, 59 min on `fvcrc20:0,1` · Qwen3-30B-A3B fp32 sharded over 2 cards
· MATH-500, teacher-forced. **Scale:** 24 problems × 6 tokens × 7 layers ×
10 candidates × 2 α = **20,160 records**. **Design:** `docs/E02_STAGEB_DESIGN.md`,
frozen at `8bc4573` before the run.

## Verdict: all six pre-registered conditions PASS → Stage C

| § 5 condition | value | |
|---|---|---|
| 1. median rho over L20/28/36/44 ≥ 0.60 | **0.771** | PASS |
| 2. some layer ≤60% depth with rho ≥ 0.55 | **0.600** (L28) | PASS *(marginal)* |
| 3. median top-3 ≥ 0.70 | 0.870 | PASS |
| 4. clearly beats `router_gap` | 0.771 vs **0.057** | PASS |
| 5. beneficial rate in 0.3–0.7 | 0.518 | PASS |
| 6. cost favourable at realistic workload | 100× @ 840 cands/seq | PASS |

## Primary — α=1, hard, boundary

| layer | depth | rho_med | top-1 | top-3 | router_gap | rand top-3 |
|---|---|---|---|---|---|---|
| 4 | 8% | 0.200 | 0.292 | 0.594 | 0.029 | 0.490 |
| 12 | 25% | 0.286 | 0.240 | 0.604 | −0.086 | 0.583 |
| 20 | 42% | 0.486 | 0.375 | 0.698 | 0.029 | 0.521 |
| 28 | 58% | **0.600** | 0.531 | 0.833 | 0.143 | 0.500 |
| 36 | 75% | 0.943 | 0.750 | 0.906 | −0.086 | 0.531 |
| 44 | 92% | 1.000 | 0.896 | 0.969 | 0.086 | 0.510 |
| 47 | 98% | 1.000 | 0.958 | 1.000 | 0.029 | 0.552 |

**The estimator is not an OLMoE artefact.** On a different family — 3× the depth,
2× the expert pool, and renormalised routing — the same three facts reappear:
monotone depth calibration, `router_gap` pinned at ~0 (the parent's blind spot,
now on a second architecture), and near-perfect deep-layer credit.

The renormalisation term is exact and free: validity confirmed the rebuilt swap
to 2.4e−8 / 6.7e−8 / 5.7e−6 against `h` scales of 0.06 / 0.28 / 42.5, using only
two local expert forwards. **CT03's efficiency claim does not depend on OLMoE's
unnormalised routing.**

## The finding that constrains the method: relative depth does not transfer either

Matched on relative depth against E01/E01.5:

| rel. depth | OLMoE (16L) | Qwen3 (48L) |
|---|---|---|
| ~6–8% | 0.257 | 0.200 |
| ~25% | 0.524 | 0.286 |
| ~42–44% | 0.771 | 0.486 |
| ~58–63% | 0.929 | 0.600 |
| ~75–81% | 0.988 | 0.943 |
| ~92–94% | 1.000 | 1.000 |

Same monotone shape, but **Qwen's curve is shifted materially later**. The ~0.6
crossover sits at ~31% depth in OLMoE and ~58% in Qwen. Relative depth is a
better coordinate than absolute layer — it is what made L28 predictable at all —
but it is **not** the invariant. Do not write "counterfactual credit is reliable
past X% depth" as a law; the honest claim is that reliability is monotone in
depth with a **model-specific onset**, which is exactly why Stage C must select
layers by measured calibration rather than by a fixed depth rule.

That is not a patch. It is the same conclusion E01.5 pointed at: adapt the layers
whose estimator passes calibration, and let the cutoff be measured per model.

## Honest caveats

- **Condition 2 passed marginally and at the window edge.** L28 is 58% depth,
  just inside the ≤60% window, and scores exactly 0.600 against a 0.55 bar.
  L20 (42%) is 0.486 and fails it. Usable mid-network credit exists, but it
  begins around the middle, not before it.
- **Top-3's floor is 0.50 here, not 0.375.** The boundary pool has 6 candidates
  (E01 used 8), so condition 3's 0.70 bar is weaker than it reads. At L20 the
  margin over chance is 0.698 vs 0.500 — real but modest.
- **Per-token Spearman on 6 candidates is quantised** (0.486, 0.600, 0.771,
  0.943 … are the attainable values). 96 hard tokens per cell. Read the curve,
  not the digits.
- **The random pool beats the boundary pool at every layer** (L28: 0.800 vs
  0.600), replicating the same inversion seen in E01. The realistic training
  pool is consistently the harder one.
- α=0.125 (diagnostic, barred from the decision) recovers exactly as in E01.5:
  L4 0.200→0.486, L20 0.486→0.743, L28 0.600→0.971. The gradient is right; the
  discrete swap is the hard part. This now replicates cross-family.

## Cost — condition 6

| cands/seq | L20 | L28 | L36 | L44 | L47 |
|---|---|---|---|---|---|
| 8 | 1.0 | 0.7 | 0.5 | 0.2 | 0.2 |
| 64 | 7.7 | 5.8 | 3.9 | 2.0 | 1.3 |
| 840 (this run) | 100.6 | 75.7 | 50.7 | 25.8 | 16.4 |
| 16384 (all-token) | 1822 | 1370 | 919 | 467 | 297 |

Break-even: **8.3 candidates/sequence at L20**, rising to 50.9 at L47. Measured
exact cost per candidate falls from 0.108 s (L20) to 0.0001 s (L47) — restating
that late-layer rerouting is nearly free, so the surrogate earns its keep in the
middle of the network, which is precisely where condition 2 says the credit
first becomes usable.

## Next: Stage C

Router training on **calibration-selected mid/late layers** (here that means
roughly L28 and deeper), MATH held-out first, then AIME/HMMT. The layer set must
be chosen by measured per-layer calibration on the target model, not by porting
"L28+" or "58%+" from this run — that is the one thing E02 proved does not
transfer.
