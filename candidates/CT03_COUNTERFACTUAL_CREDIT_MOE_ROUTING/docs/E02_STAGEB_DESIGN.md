# CT03 Stage B (E02) — Cross-family calibration on Qwen3-30B-A3B

**Status:** FROZEN 2026-09-20, before any run. Nothing is trained.
**Predecessors:** `results/RESULTS.md` (E01), `results/RESULTS_E015.md` (E01.5).
**Question:** is the local counterfactual credit estimator a property of MoE
LMs, or an artefact of OLMoE's routing geometry?

---

## 1. Why this is now the largest remaining risk

E01/E01.5 established, on one model, that first-order local credit predicts
exact equal-compute route regret (rho 0.698 overall, and 0.771/0.929/0.988/1.000
at layers 7/10/13/15 of 16 at full swap), that the router's own score carries no
such information, and that the shallow-layer failure is tail dispersion at full
swap rather than curvature or depth accumulation.

Every one of those numbers comes from a model with **64 experts, top-8, 16
layers, and `norm_topk_prob=false`**. The last of those is not incidental: it
made the swap algebra exact with no renormalisation term. Qwen3-30B-A3B has
**48 layers, 128 experts, top-8, `norm_topk_prob=true`** — it stresses depth,
expert-pool size, and precisely the architectural caveat E01 flagged.

## 2. Renormalised swap — the new exact quantity

With `norm_topk_prob=true`, raw softmax probabilities `p_e` are renormalised over
the selected set. For route `S`:

```
Z_S = sum_{e in S} p_e ,    h = sum_{e in S} (p_e / Z_S) E_e(x)
```

Replacing `i` by `j` gives `S' = S \ {i} u {j}` and `Z_S' = Z_S - p_i + p_j`, so

```
h' = (1/Z_S') [ Z_S * h  -  p_i E_i(x)  +  p_j E_j(x) ]

dh = h' - h = (Z_S/Z_S' - 1) * h  +  (p_j E_j(x) - p_i E_i(x)) / Z_S'
```

The first term is the **rescaling of the seven surviving experts**, which OLMoE
never exercised. It is exact and needs no extra expert forwards: the block's own
output `h` already contains `sum_{e in S} p_e E_e(x)` up to the factor `Z_S`.

So the per-candidate local cost is unchanged in kind: one forward of the
candidate expert `E_j`, one of the replaced expert `E_i`, and arithmetic. **No
extra downstream forward.** If the estimator survives here, CT03's efficiency
claim is not a consequence of OLMoE's unnormalised routing.

## 3. Relative depth, not absolute layer

OLMoE's "layers >= 7" is 44% depth and does not transfer to a 48-layer model.
Sampled layers and their relative depth:

| layer | 4 | 12 | 20 | 28 | 36 | 44 | 47 |
|---|---|---|---|---|---|---|---|
| depth | 8% | 25% | 42% | 58% | 75% | 92% | 98% |

`L4/L12` are failure controls. **`L20` is the boundary point that matters.**
`L28/L36` decide whether a genuinely multi-layer method exists. `L44/L47` check
the deep regime where rerouting is cheap anyway.

## 4. Primary endpoint is alpha = 1, and only alpha = 1

E01.5 showed the alpha=0.125 threshold answers "is the local linearisation
correct", not "can we predict the credit of an executable route replacement".
Routing is a discrete swap. Therefore:

> **Primary:** `rho(px_shared, dL_seq)`, hard tokens, boundary candidates,
> **alpha = 1**, renormalised swap, at L20/L28/L36/L44.

A small `alpha = 0.125` arm is retained **for debugging only** and is barred from
the survival decision. It is recorded so that a failure can be diagnosed as
"gradient wrong" vs "step too large" without another run.

## 5. Pre-registered adjudication

**CONTINUE to Stage C (router training)** requires all of:

1. `median{rho @ L20, L28, L36, L44} >= 0.60`
2. at least one layer at `<= 60%` depth (L20 or L28) with `rho >= 0.55`
3. median top-3 recall `>= 0.70` over those four layers
4. clearly beats `router_gap` on the same cells
5. beneficial rate not degenerate (within ~0.3-0.7)
6. proxy cost still clearly favourable at a realistic candidate workload

Condition 2 is the one that protects the paper. If only L44/L47 work, CT03
collapses back into the late-layer regime EPO already handles cheaply.

**KILL or fundamental reframe** if L20/L28 are near random and only the last
~20% of the network is reliable. In that case the first question is *not* how to
add a robust loss — it is whether a late-layer-only method still has enough
efficiency and benchmark upside over EPO. If not, kill before Stage C.

No shallow-layer rescue is attempted in E02 regardless of outcome. Whether
shallow credit needs saving is not yet known, and may never matter: if reliability
turns out to be a stable function of relative depth, the natural method is to
adapt only calibrated layers, which adds no module at all.

## 6. Scale — deliberately small

This is cross-family validation, not precision estimation. 24 problems, 6 tokens
each (4 hard / 2 easy), 7 layers, 6 boundary + 4 random candidates, 2 alphas.
The target is the **shape of `rho` against relative depth**, not three-digit
values. Single cells will be coarse and must not be over-read.

## 7. Numerics

float32, sharded over 2 cards. bf16 is not acceptable here: at deep layers the
exact effects reach 1e-4, and bf16 hidden states can round two near-identical
routes to the *same* value, silently producing `dL = 0`. Two zero-patch rows per
batch measure the floor, as in E01.5.

Validity checks (`--validate`) must pass first, and now include the
renormalisation algebra: `h` rebuilt from the router's own weights, and the
swapped route's output recomputed independently and compared against `h + dh`.
