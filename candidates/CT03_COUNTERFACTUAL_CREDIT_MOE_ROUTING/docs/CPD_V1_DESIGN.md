# CT03 CPD v1 — Counterfactual Potential Distillation

**Status:** FROZEN 2026-09-20, before any training step.
**Predecessors:** E01/E01.5/E02 (estimator), C0 (binary CCD failure),
E03.1/.5/.6/.7 (evaluation repair + structure), FG0.1 (motivation).

---

## 1. Method

At a calibrated layer, for the routed set `S` and boundary candidates `C`:

```
u_hat_ij = -g^T dh_ij                      cheap credit, one shared backward
z_hat    = argmin_z sum_ij [(z_j - z_i) - u_hat_ij]^2       expert potential
q*(e|x)  ∝ p_0(e|x) exp(beta * z_hat_e)    KL-regularised policy improvement
L_CPD    = KL( q* || p_theta )
```

`q*` is the closed-form solution of
`max_q E_{e~q}[z_e] - (1/beta) KL(q || p_0)`, so the trust region is **part of
the objective**, not an anchor bolted on. Since `p_0 = softmax(s_0)`, the target
is simply `softmax(s_0 + beta*z)`: **counterfactual potential is a task-grounded
advantage correction to the pretrained router logits.**

### Why this and not the two things it replaces

- Against C0's binary pairwise loss: `softplus(-y(s_j - s_i))` has a degenerate
  optimum at `s_i = s_j`. Random labels fit it slightly *faster* than real ones,
  and it collapsed the selection margin ~45%. A full-distribution target has no
  such shortcut.
- Against `q_j ∝ exp(-ΔL̂_j/τ)`: `ΔL̂_j` is not well defined — only `ΔL(i→j)`
  exists, so "the utility of j" silently requires picking `min_i`, `E_i`, or the
  rank-k `i`. The least-squares projection **is** the principled answer.

E03.5/E03.6 licensed this: exact utilities are near-additive at calibrated
layers (R² 0.969/0.999 at L36/L44) and the proxy potential tracks the exact one
(ρ 0.902/0.979). Projection is **not** claimed to denoise — E03.6 measured that
at −0.003.

### Heavy tail is exploited, not removed

E03.1 found gains concentrated in a token tail. `q* ∝ p_0 exp(beta z)` means
`|z| ≈ 0` leaves routing essentially untouched while large `|z|` moves it
materially. **Do not per-token normalise `z`** — that would delete the very
magnitude structure the form exists to use.

## 2. Target — exact mass-preserving reallocation on `U = S ∪ C`

**Amended 2026-09-21, before any training step.** The first version used the
gauge `sum_{e∈U} p_0(e|U) z_e = 0` with `z = 0` outside. That is wrong in a way
that would have been hard to detect afterwards: `exp` is convex, so by Jensen

```
sum_{e∈U} p_0(e) exp(beta z_e) = P_U * E_{p_0(·|U)}[exp(beta z)] >= P_U
```

with strict inequality unless `z` is constant. The target would therefore have
**systematically raised the whole candidate neighbourhood's mass**, which the
credit never licensed — it only ranks experts *within* `U`. C0 was already
fooled once by a generic mass/margin effect; this closes that route at the
formulation level rather than relying on a control to catch it.

The target is instead exactly mass-preserving. With `P_U = sum_{e∈U} p_0(e)`:

```
q*(e) = P_U * p_0(e) exp(beta z_e) / sum_{k∈U} p_0(k) exp(beta z_k)     e ∈ U
q*(e) = p_0(e)                                                          e ∉ U
```

Three properties, all exact rather than approximate:

1. **Gauge invariant.** `z_e -> z_e + c` leaves `q*` identical, so the
   potential's undetermined zero point disappears and no gauge has to be imposed.
2. **Outside experts are untouched**, `q*(e) = p_0(e)`, and
   `sum_{e∈U} q*(e) = sum_{e∈U} p_0(e)` exactly.
3. The method becomes what its name claims: probability is **reallocated within
   the evidence-supported neighbourhood**, never created for it.

Equivalently in logit form, `s*_e = s_0,e + beta(z_e + c)` on `U` and
`s*_e = s_0,e` outside, with
`c = (1/beta)[log P_U - log sum_{e∈U} p_0(e) exp(beta z_e)]`; substituting it
returns the normaliser to its base value, which is how the two forms are
checked against each other. The implementation uses the probability form.

The claim this licenses:

> CPD performs **evidence-local policy improvement**: it preserves the
> pretrained router's probability mass outside and into the candidate
> neighbourhood exactly, and redistributes mass only according to counterfactual
> advantage. Gains cannot come from globally flattening the router or from
> indiscriminately increasing candidate mass.

## 3. beta — one global trust-region budget, no sweep

Per layer, `beta_l` is set on a small frozen calibration split so that the
**median** `KL(q* || p_0)` hits one global budget `delta`. Per-layer `z` scales
differ, but only the layer median is calibrated, so within a layer a
high-magnitude token still produces a larger update.

`delta` is fixed once by a training-free ladder on the calibration split:
compute, for each candidate `delta`, the fraction of tokens whose top-8 changes,
and take the value giving a modest change rate. Recorded, then frozen. This is
not a results-table sweep.

## 4. Layers: L36 and L44 only

Potential fidelity ρ = 0.902 (L36, 75% depth) and 0.979 (L44, 92%). L28 is at
the estimator's calibration boundary (0.703) and is **excluded from v1**, to be
revisited as a `CPD-36/44` vs `CPD-28/36/44` ablation. L47 stays out: the parent
already owns final-layer adaptation, and the claim needing support is that
*non-final* routers can be improved.

Only the gate matrices train: 2 × (2048 × 128) = 524k parameters. Backbone,
experts, attention, embeddings and LM head frozen.

## 5. Three arms, no fourth

1. **Router-CE** — same data, same layers, same steps, ordinary LM cross-entropy.
   Answers the reviewer's first question: is plain router-only post-training
   enough? (RoMA, ICLR 2026, already owns "router-only post-training helps", so
   this cannot be our contribution.)
2. **Shuffled-CPD** — `z` permuted among `U`, put through the same
   mass-preserving normalisation, then a per-token scalar on `beta` chosen so
   that `KL(q_shuf || p_0) = KL(q_true || p_0)`. Under the mass-preserving
   target this control is unusually tight: true and shuffled share the total `U`
   mass, the outside probabilities, the intervention strength in KL, and the
   `|z|` multiset. The **only** difference is which expert receives the
   counterfactual advantage. Without the rescale, permutation would change the
   realised strength because `p_0(e)` differs per expert.
3. **CPD** — the real `z_hat`.

Binary CCD v0 is not rerun; its failure analysis stands.

## 6. Data

Training: MATH train / NuminaMath verified trajectories. **MATH-500 is not used
for training and is no longer described as untouched** — C0 drew its pool and
held-out set from it and E03.1/.5/.6 were developed on it.

Free-generation development: the **120 locked FG0 problems**
(`results/fg0_devpool.json`), disjoint from MATH-500, never trained on.
Confirmatory: AIME / HMMT, untouched.

## 7. Evaluation, in two layers

**Mechanistic** — the repaired fixed-support instrument: base tokens, base hidden
states, base candidate universe.

```
V_route = L(S_theta ; x_base) - L(S_base ; x_base)
```

reported as mean, median, win rate, p10/p90 and paired bootstrap CI, because
E03.1 showed the mean alone is misleading. Also `rho(s_theta, z*_exact)` on
fixed support: CPD explicitly learns the potential, so if this does not move it
is an optimisation or implementation problem, not a scientific finding.

**Free generation** — the 120 locked problems, **greedy first**. Greedy is right
here precisely because CPD is not FG0's 4%-TV single intervention: it changes
routing at every token, at two layers, from prompt to answer. If a
deployment-strength treatment cannot move a single greedy trajectory, that is
itself important information, and sampling would only hide it in variance.
Recorded: exact-match correctness, whether the completion differs from base,
first divergence position, route overlap, experts changed, sampled per-token KL.

## 8. Result tree, fixed in advance

- **A.** alignment ↑, route value ↑, trajectories diverge, accuracy ↑ →
  paper-scale benchmarks.
- **B.** alignment ↑, route value ↑, free generation flat → FG0.1 becomes the
  interpretation: the credit improves local route utility at positions the
  generation policy does not actually visit or cannot act on. *Then* an
  on-policy / actionable credit variant is motivated — by two converging
  failures, not by invention.
- **C.** CPD does not beat Shuffled-CPD on fixed-support route value → potential
  distillation did not convert credit into router action. Revisit the objective,
  not the regularisers.
- **D.** CPD helps free generation but Router-CE helps equally → the novelty
  burden moves to sample efficiency / generalisation / route quality, and
  stronger baselines (EPO, RoMA) are required.

**Not to be done now:** entropy / margin / gold-probability gating of the credit.
FG0.1 showed high-`H_proxy` tokens often sit at `p_gold ≈ 2e−3`, which makes such
a filter tempting. But C0 already showed credit-specific gains (−0.056 nats) even
at those positions, and CPD is a stronger objective than binary CCD. Adding
actionability now would be inventing the method ahead of the evidence; it is the
natural v2 **iff** outcome B occurs.
