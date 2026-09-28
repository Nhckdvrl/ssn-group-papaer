# CT03 E03.6 / E03.7 — proxy-vs-exact potential, and which gap actually limits it

Zero-to-low cost analyses. E03.6 adds the proxy for the same 32 base pairs
already measured exactly in C0 (one forward+backward, no replays). E03.7a is
pure CPU on those two files. Sources: `src/e036_potential.py`,
`src/e037_gaps.py`.

## E03.6 — the substitution is licensed in the deep layers, but projection does not denoise

Training never sees exact utilities, only the proxy. Substituting one for the
other in `z*` was an untested assumption.

| layer | ρ(pairwise) | ρ(z_proxy, z_exact) | best-cand recall | top-4 overlap |
|---|---|---|---|---|
| 28 | 0.707 | 0.703 | 0.703 | 0.660 |
| 36 | 0.905 | 0.902 | 0.852 | 0.791 |
| 44 | 0.984 | 0.979 | 0.914 | 0.902 |

Fidelity is high at L36/L44 and marginal at L28. **But `gain = ρ_z − ρ_pair` is
−0.004 / −0.003 / −0.005: projection is an identity transport, not a denoiser.**
The hoped-for "projection cleans up pairwise credit" is not available and must
not be written.

`z*` keeps exactly two justifications, and they are enough:
1. it converts `K × m` pairwise replacement utilities into an expert-level
   target a standard scalar router can represent;
2. fitting it has no `s_i ≈ s_j` collapse solution, unlike
   `softplus(−y(s_j − s_i))`.

Wording correction: `z*` makes the target **dense in expert space**. It does
**not** remove the heavy tail across tokens — and it should not, since that tail
is what the policy-improvement form is designed to exploit.

### The proxy is additive by construction, so its own R² carries no news

Proxy R² is 0.9998 / 0.9998 / 0.9999. That is algebra, not a property of the
model: with `Z' = Z − p_i + p_j ≈ Z` when `p_i, p_j ≪ Z`,

```
g^T dh_ij  ->  z_j - z_i   with   z_e = p_e (g^T E_e)/Z
```

So the empirical content of E03.5 is the **exact** utility's integrability
(0.867 / 0.969 / 0.999), not the proxy's.

## E03.7a — interaction is NOT what limits the shallow layer

Split the exact utility as `u = u_par + u_perp`, with `u_par = A z*_exact` the
expressible part. Two gaps had been conflated:

| layer | 1−R² (interaction) | ceiling √R² | ρ(û, u) | ρ(û, u_par) | lift | est. gap |
|---|---|---|---|---|---|---|
| 28 | 0.133 | 0.931 | 0.707 | **0.755** | **+0.048** | **0.245** |
| 36 | 0.031 | 0.985 | 0.905 | 0.936 | +0.031 | 0.064 |
| 44 | 0.001 | 0.999 | 0.984 | 0.985 | +0.001 | 0.015 |

**Removing the non-additive component entirely lifts L28 only from 0.707 to
0.755.** The estimation gap on the *representable* component is 0.245 — roughly
five times the interaction contribution.

**Correction.** An earlier reading of E03.6 claimed L28 is limited because "the
exact utility is pair-dependent and a first-order proxy structurally cannot see
it". That is withdrawn. The first-order estimator is mis-estimating the additive
component itself.

A second claim is also withdrawn: that a second-order term could not capture pair
interaction. `½ Δh_ij^T H Δh_ij` is a quadratic form in a pair-specific
perturbation and is pair-specific by construction. The reason not to add it is
that its available lift here is 0.048, not that it is impossible.

### This links up with E01.5

E01.5 found the shallow-layer failure is finite-step linearisation error — the
full swap leaves the linear regime, and `α = 0.125` recovered OLMoE L1 from
0.257 to 0.829. E03.7a independently says the shallow gap is *estimation* of the
representable component, not interaction. Both point at the same mechanism:
**step size, not expressiveness.**

## Consequences for v1

- Deploy on **L36/L44**. L28 is a calibration-boundary layer (potential fidelity
  0.703), held out for a later `CPD-36/44` vs `CPD-28/36/44` ablation. The reason
  is measured fidelity, not a claim that L28 is inexpressible.
- Do not claim projection denoising.
- Do not add curvature in v1.

## E03.7b — OLMoE, six layers: the same decomposition, cross-model

`e01_records.jsonl` could not be reused: E01 recorded a single `i` per token, so
there is no `K × m` grid to project. `src/e037_olmoe.py` produced one (16
problems × 8 tokens × 6 layers × 32 pairs = 24,576 exact + 24,576 proxy).

| model | layer | depth | 1−R² | lift | est. gap | est/lift |
|---|---|---|---|---|---|---|
| OLMoE | 1 | 6% | 0.257 | +0.065 | 0.579 | 9.0× |
| OLMoE | 4 | 25% | 0.146 | +0.092 | 0.343 | 3.7× |
| OLMoE | 7 | 44% | 0.059 | +0.039 | 0.167 | 4.2× |
| OLMoE | 10 | 62% | 0.013 | +0.018 | 0.078 | 4.4× |
| OLMoE | 13 | 81% | 0.005 | +0.012 | 0.045 | 3.7× |
| OLMoE | 15 | 94% | 0.000 | −0.003 | 0.015 | — |
| Qwen | 28 | 58% | 0.133 | +0.048 | 0.245 | 5.1× |
| Qwen | 36 | 75% | 0.031 | +0.031 | 0.064 | 2.1× |
| Qwen | 44 | 92% | 0.001 | +0.001 | 0.015 | 13.8× |

**Both halves of the picture are confirmed, and they say different things.**

1. The structural observation **is** real and cross-model: non-additivity rises
   monotonically toward shallow layers — 0.000 → 0.257 in OLMoE, 0.001 → 0.133
   in Qwen — and `spearman(1−R², est_gap) = 0.983` over the nine layer-points.
   So "shallower route utilities become increasingly interaction-dependent" is
   a supportable statement.
2. It is nevertheless **not the limiting factor anywhere**. The estimation gap
   exceeds the interaction lift at every single layer in both models, by a
   median of **4.3×** (minimum 2.1×).

   *Units caveat:* `lift` is a change in rank correlation while `1−R²` is a
   variance share, so these are not commensurable. The ratio is reported as a
   descriptive comparison only — **this is not a variance decomposition**, and
   the claim to make is simply "the estimation gap is consistently much larger
   than the gain from removing the interaction residual", not "interaction
   accounts for N% of the deficit".

So the two quantities co-vary with depth — which is why conflating them was easy
— but the decomposition assigns the shallow-layer failure to **estimation of the
representable component**, not to expressiveness, in both architectures.

`spearman(1−R², est_gap) = 0.983` must **not** be read as "interaction causes the
estimation failure". Both are driven by depth, so the high correlation is
confounding; the decomposition is precisely what shows correlation is not cause
here.

The residual error is **consistent with finite-intervention linearisation
error** — E01.5 recovered OLMoE L1 from 0.257 to 0.829 at α=0.125 — but no
specific nonlinear mechanism is claimed. The simple "long-suffix accumulation"
account was already falsified in E01.5 (direction drift first breaks at absolute
layer 13–14 regardless of source layer, and never breaks for L1), and it is not
being quietly reinstated.

Note the two models do not align on relative depth: Qwen at 58% has a larger
estimation gap (0.245) than OLMoE at 44% (0.167), consistent with E02's finding
that Qwen's calibration curve sits materially later.

**Analysis stops here.** Next is FG0 (the free-generation bridge, attacking the
one kill-bar condition with no instrument) and the frozen CPD v1 design — not
further mechanism digging.
