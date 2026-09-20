# CT03 E03.5 — Is counterfactual routing utility expressible by a scalar router?

**Run:** 2026-09-20, zero GPU. Pure analysis of exact utilities already measured
in the C0 base-arm evaluation (`results/c0_eval_base_pairs.jsonl`, 384 tokens ×
32 one-swaps = 12,288 exact `dL`). Source: `src/e035_integrability.py`.

## The untested assumption

A standard router emits one scalar per expert. For it to represent the
counterfactual landscape there must exist expert potentials `z` with

```
u_ij = -dL(i->j)  ~=  z_j - z_i
```

Nothing in CT03 had tested this, and Qwen's `norm_topk_prob=true` gives a
concrete reason to doubt it: the swap renormalises by `Z' = Z - p_i + p_j`, so
`u_ij` depends on the pair jointly. If the landscape were not integrable, **no
scalar router could express it** and every listwise/utility target would be
misspecified from the start.

## Result: it is integrable, and increasingly so with depth

Per token, least squares for `z` minimising `sum_ij [(z_j - z_i) - u_ij]^2`
with gauge `sum z = 0`; medians over tokens.

| layer | depth | R² | Spearman | sign acc | median \|resid\| | median \|u\| |
|---|---|---|---|---|---|---|
| 28 | 58% | 0.867 | 0.908 | 0.906 | 0.0174 | 0.0579 |
| 36 | 75% | 0.969 | 0.971 | 0.969 | 0.0085 | 0.0558 |
| 44 | 92% | **0.999** | 0.996 | **1.000** | 0.0019 | 0.0635 |

The counterfactual utility landscape **is**, to a good approximation, a
per-expert scalar potential. The representation layer is therefore **not** the
bottleneck, and a utility/listwise router target is well posed.

The integrability gradient tracks the depth-calibration curve from E01.5/E02
(0.600 / 0.943 / 1.000 at these same layers). Whether that is one phenomenon or
two is not established here; it is worth stating as an observation, not a claim.

### One number not to over-read

The script also reports a 4-cycle residual
`u_i1j1 - u_i1j2 - u_i2j1 + u_i2j2`, which additivity forces to zero. At L28 it
is 0.0412 against median `|u|` 0.0579, which *looks* like 71% frustration. That
normalisation is wrong: the 4-cycle sums four fit residuals, so its natural
scale is ~2×`|resid|` = ~0.035, not `|u|`. The observed value is consistent with
the R² fit and carries no independent information. Normalising it against `|u|`
was a mistake in the script's output, kept here rather than silently reformatted.

## What this decides

1. **Soft utility distillation is well posed** — but its target should be the
   projected potential `z*`, not an ad-hoc `q_j ∝ exp(−ΔL̂_j/τ)`. The ad-hoc
   form is not even well defined, since only `ΔL(i→j)` exists and "the utility
   of j" requires an arbitrary choice of which `i`. The projection **is** the
   principled answer to that question:

   ```
   counterfactual credit  ->  expert potential z*  ->  router distillation
   ```

2. **v0's failure mode is not a representation failure.** The router could have
   expressed the target. That localises the problem in the *objective* (the
   margin-collapse shortcut), which is consistent with the shuffled-label
   control fitting the loss slightly faster than the real one.

3. It does **not** yet show that distilling `z*` works. That is v1.
