# L42 — E01 Selection Amendment

**Status:** candidate remains `PILOT-AUTHORIZED — E01 ONLY; NOT MAINLINE`.  
**Purpose:** refine the registered E01 after deeper closest-owner and instrument audits.  
**Relation to README:** this file supersedes the README only where explicitly stated below; it does not authorize E02 or a paper-level scaling claim.

---

# 1. Closest-owner update: ACL 2023 makes the depth axis more scientifically specific

Mueller & Linzen, ACL 2023, **How to Plant Trees in Language Models: Data and Architectural Effects on the Emergence of Syntactic Inductive Biases**, is a closer owner than the original L42 audit recognized.

Their question is:

> Which architectural and data properties cause a Transformer to **spontaneously acquire** a hierarchical syntactic inductive bias through pretraining?

Key findings relevant to L42:

- parameter count alone does not monotonically predict hierarchical generalization;
- depth has a much stronger effect than width / feed-forward size;
- in a controlled scratch-pretraining experiment they vary depth over `2 / 4 / 8 / 16` while keeping hidden size and heads fixed;
- on CHILDES, main-auxiliary generalization for the fixed-width family is approximately `0.49 / 0.58 / 0.73 / 0.70` for `2 / 4 / 8 / 16` layers;
- on Wikipedia the corresponding values are approximately `0.08 / 0.35 / 0.46 / 0.48`.

Paper: https://aclanthology.org/2023.acl-long.629/

This does **not** directly own L42. Mueller & Linzen manipulate the architecture and ask when a hierarchical preference **emerges naturally**. They do not compare a model with and without an externally supplied matched syntactic prior at each depth, and they do not ask how the **marginal value of that prior** changes with depth.

Instead, their result creates a sharper competing prediction for L42:

### Crowding-out hypothesis

> If greater depth already causes the baseline learner to acquire a stronger hierarchical bias, an explicit matched syntactic prior should become less valuable as depth increases.

### Complementarity / scale-amplification hypothesis

> If a matched prior changes the effective learning problem / optimization geometry rather than merely compensating for a shallow model's missing syntax, its marginal benefit may stay constant or grow with depth.

The latter possibility is independently motivated by ICLR 2026 **Scaling Laws and Symmetry**, where a matched architectural prior changes scaling behavior rather than being washed out.

Therefore the preferred short RQ for E01 is now:

> **Does depth crowd out an explicit syntactic prior, or make that prior more valuable?**

This is lower-description-length and better grounded than a generic `bigger models vs syntax` framing.

---

# 2. Additional closest owner: model-size × linguistic-prior interaction is not unprecedented

McCoy et al., Nature Communications 2025, **Modeling rapid language learning by distilling Bayesian priors into artificial neural networks**, factorially vary LSTM hidden size and CHILDES data quantity after distilling a linguistic Bayesian prior. They find a non-trivial model-size × data-size interaction: the prior's perplexity benefit forms a rough diagonal band rather than simply helping the smallest / lowest-data models.

Paper: https://www.nature.com/articles/s41467-025-59957-y

This means L42 must **not** claim:

> `first evidence that linguistic inductive bias interacts with model size`.

What remains unowned is narrower and stronger:

> **depth × matched structural prior × syntactic generalization**, with an explicit mismatched-structure control and a predeclared distinction between prior benefit and random-constraint harm.

---

# 3. Primary scientific estimands — amendment

The README currently centers

`A(d) = TRUE(d) - RANDOM(d)`

and the depth interaction

`I = A(16) - A(4)`.

After the deeper identification audit, `TRUE-RANDOM` should **not be the sole primary quantity**, because an increasing gap can be generated entirely by RANDOM becoming more harmful at larger depth.

For the refined question `crowding out vs complementarity`, define:

### Matched-prior marginal benefit

`B(d) = TRUE(d) - BASE(d)`

and the primary depth interaction

> `J = B(16) - B(4)`.

`J` directly asks whether the *marginal value of an explicit matched syntax prior* changes with depth.

### Structural-specificity contrast

Keep

`A(d) = TRUE(d) - RANDOM(d)`

and define

> `K = A(16) - A(4)`.

`K` asks whether the depth interaction is specific to matched structure rather than merely to applying the TreeReg machinery.

Also retain

`C(d) = RANDOM(d) - BASE(d)`.

### Interpretation matrix

#### Strongest promotion pattern

- `|J| >= 5 pp`;
- `J` is robust across seeds;
- `K` has the same sign and is materially non-zero;
- no scale-dependent instrument pathology.

Interpretation: depth changes the marginal value of a **matched** syntactic prior, and the interaction cannot be reduced to a generic TreeReg effect.

#### `K` large but `J ~ 0`

The TRUE-RANDOM gap changes mainly because RANDOM becomes more helpful/harmful.

Interpretation: depth changes sensitivity to the random structural constraint. **Do not promote this as `scale rewards syntax`.** Return to Selection and require a stronger shape-matched misalignment control.

#### `J` large but `K ~ 0`

TRUE changes relative to BASE, but RANDOM changes similarly.

Interpretation: likely a scale interaction with TreeReg / auxiliary optimization broadly, not a matched-syntax-specific effect. **HOLD the syntax claim.**

#### both near zero

Current paper identity is NO-GO: explicit syntax behaves approximately as a constant offset over this depth range.

This amendment therefore turns the RANDOM arm into a **specificity control** rather than allowing RANDOM-harm alone to manufacture the headline effect.

---

# 4. Pilot statistical gate — amendment

Four training seeds are suitable for a **large-effect go/no-go pilot**, not for publication-grade inference about a scaling law.

A hierarchical bootstrap over SyntaxGym items cannot create additional independent training runs. Therefore the README requirement

> `95% hierarchical bootstrap CI excludes 0`

should no longer be treated as a hard promotion criterion with only four seeds.

### E01 primary pilot evidence

Use:

1. **effect magnitude:** `|mean J| >= 5 pp` for the matched-prior interaction;
2. **replication direction:** seed-paired `J` has the same sign for at least `3/4` predeclared seed indices;
3. **specificity:** `K` has the same sign and is materially non-zero; the exact magnitude is reported rather than rescued with a post-hoc threshold;
4. **instrument validity:** no floor/saturation/recipe/layer-placement/gradient-clipping pathology explains the interaction.

Report item/seed bootstrap intervals as **descriptive uncertainty summaries**, not as a claim that four training runs establish a publication-grade confidence interval.

If E01 is promoted, the next Selection stage must budget additional independent training runs and scale points before statistical/exponent claims.

Do not lower the `5 pp` material-effect threshold merely because a smaller effect attains a narrow item-level CI.

---

# 5. 4L layer-placement robustness gate — bounded implementation

The parent 16L BLLIP study sweeps TreeReg placement and finds layer 12 best. The parent's separate 4-layer synthetic experiments use layer 2, whereas the registered L42 E01 uses layer 3 by the predeclared fractional-depth rule (`12/16 = 3/4`).

This can manufacture a false depth interaction if 4L is unusually sensitive to layer placement.

A cost-bounded resolution is possible without turning placement into a hyperparameter search.

### If Phase A (16L replication) passes

For the **first two predeclared 4L seeds only**:

- run formal `TRUE@layer3` and `RANDOM@layer3` as already required by E01;
- additionally run `TRUE@layer2` and `RANDOM@layer2`.

Thus layer 3 runs count toward the eventual formal 4L endpoint. The robustness gate adds only **4 extra training runs maximum**, not 8.

### Decision

- If the layer-2 vs layer-3 TRUE-RANDOM contrast differs in sign or by an amount comparable to the planned `5 pp` depth interaction, mark `HOLD — LOW-DEPTH INSTRUMENT PLACEMENT-SENSITIVE` and do not complete the remaining 4L sweep.
- If the contrast is reasonably stable, retain the **predeclared layer-3 fractional-depth rule** for the remaining formal 4L runs. Do not switch to whichever placement produced the nicer final SG value.

Maximum total authorized run count under this amended path is therefore:

- 12 runs at 16L;
- 12 formal runs at 4L;
- up to 4 additional 4L placement-diagnostic runs;
- **28 total runs maximum**, with sequential stopping.

This extra budget is solely an instrument-validity gate; it does not expand the scientific study.

---

# 6. Scale terminology — tightened

ACL 2023 gives an additional reason to describe E01 as a **depth interaction**, not generic parameter scaling: depth itself is a scientifically special architectural variable for hierarchical generalization.

The TreeReg code also has a potentially large fixed tied embedding matrix, so 4L→16L need not imply a fourfold change in total parameter count.

Until the actual reconstructed vocabulary and models are available, report:

- exact depth ratio;
- exact parameter counts measured from instantiated models;
- tokens seen;
- realized FLOPs / throughput.

Preferred E01 language:

> **fixed-data computational-depth × syntactic-prior interaction**

Do not write `4× model scale` or claim a parameter-scaling exponent.

---

# 7. Updated E01 verdict

The deeper audit **does not revoke L42**. It strengthens the scientific question but narrows what E01 can claim.

### Topic identity

**PASS.** ACL 2023 supplies a direct crowding-out prediction from the syntax literature; ICLR 2026 supplies a credible complementarity/amplification alternative. The question is genuinely uncertain.

### Ownership

**PASS WITH HIGHER NEAR-OWNER RISK.** ACL 2023 already owns `depth changes emergent syntactic bias`; Nature Communications 2025 owns a model-size × linguistic-prior interaction in another learner/metric. Neither owns the marginal effect of a matched structural prior on autoregressive syntactic generalization as depth changes.

### Identification

**PASS CONDITIONAL ON E00.** Use `J=Δ_depth(TRUE-BASE)` as the main crowding-out/complementarity quantity and `K=Δ_depth(TRUE-RANDOM)` as structural-specificity evidence. RANDOM-harm alone is not sufficient.

### Statistics

**PASS FOR LARGE-EFFECT PILOT ONLY.** Four seeds support a bounded promotion decision, not final inference. Remove `CI excludes 0` as a hard E01 gate.

### Execution

**E01 REMAINS AUTHORIZED, but full sweep is execution-HOLD until E00 recipe/data/gradient/layer-placement checks are satisfied.**

No E02 or paper-level scaling claim is authorized by this amendment.
