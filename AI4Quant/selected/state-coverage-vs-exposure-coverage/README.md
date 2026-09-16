# P1 — State Coverage ≠ Exposure Coverage

## Working title

**The Geometry of Data in Multivariate Foundation Models**

## Status

**PILOT-AUTHORIZED**

This folder is the canonical registration for this topic. Do not replace the question with a generic “more assets vs longer history” ablation.

---

## 1. Mother question

Existing neural/time-series scaling work usually compresses data size into a scalar, e.g.

\[
D = \text{number of observations/tokens}.
\]

For a multivariate panel,

\[
x_{i,t}=\lambda_i^\top f_t+\epsilon_{i,t},
\]

however the two axes carry different information.

- Increasing **N** adds more cross-sectional views/exposures of the same latent market state `f_t`.
- Increasing **T** adds new realizations and transitions of the latent environment `f_t -> f_{t+1}`.

Therefore equal total observation count

\[
N_1T_1=N_2T_2
\]

does not imply equal information geometry or equal learnability.

The scientific question is:

> **When can breadth and depth be treated as interchangeable data, and when must multivariate foundation-model scaling be intrinsically two-dimensional?**

---

## 2. Why this is not “data diversity matters”

Do not sell the paper as any of the following:

- more assets are useful;
- longer context is useful;
- correlated samples contain less information;
- diverse training data improve transfer;
- choose the best `N:T` hyperparameter under a token budget.

Those are too generic and heavily owned.

The intended scientific object is the decomposition of **data geometry** into:

- **state coverage**: how many genuinely new latent-environment realizations/transitions are observed;
- **exposure coverage**: how many distinct views/loadings of each latent state are observed.

The target outcome is a theory/empirical law of the form

\[
L = L(N,T;\text{factor strength},\text{persistence},\text{noise},\text{loading diversity},\ldots),
\]

not merely `L(D)`.

---

## 3. Why now / owner boundary

The strongest current TSFM scaling papers intentionally study **univariate** forecasting to avoid the confounding introduced by variable interactions/correlations, and explicitly leave multivariate scaling as future work.

At the same time, newly released multivariate foundation models such as **TimesFM-3** expose a genuinely two-dimensional temporal × variate context, making the question experimentally accessible without training a large model from scratch.

Near owners that do **not** by themselves kill the topic:

- generic data-diversity scaling;
- repeated-data scaling;
- task-count vs samples-per-task meta-learning;
- robot environment diversity scaling;
- classical large-N, large-T panel asymptotics.

The novelty must come from **shared latent environment realizations**: `N` views reuse the same state while `T` creates new states/transitions.

If a direct paper is found that already derives/empirically demonstrates multivariate FM scaling as a function of cross-sectional breadth × temporal depth under shared latent factors, reassess immediately.

---

## 4. Competing scientific accounts

### Account A — scalar data scaling is approximately sufficient

A sufficiently capable multivariate model may efficiently combine both axes such that

\[
L(N,T) \approx \tilde L(NT)
\]

after the right normalization/effective-data correction.

If curves collapse, that is scientifically meaningful.

### Account B — data geometry is irreducibly two-dimensional

Different `(N,T)` pairs with identical `NT` can produce systematically different capability because breadth and depth identify different latent quantities.

Expected structured interactions include:

- stronger common factors -> larger value of breadth for current-state inference;
- greater idiosyncratic noise -> larger cross-sectional sample needed to recover the shared state;
- richer loading diversity -> more value from breadth for new-exposure generalization;
- greater regime/state diversity -> larger value of temporal coverage;
- different targets may prefer different aspect ratios.

The paper is strong only if it explains **when** each regime occurs, not if it merely shows a significant N/T effect.

---

## 5. E01 — decisive synthetic pilot

### Generative world

Start with a controlled dynamic-factor model:

\[
f_{t+1}=Af_t+\eta_t,
\]

\[
x_{i,t}=\lambda_i^\top f_t+\epsilon_{i,t}.
\]

Optional later extensions:

- nonlinear observation map;
- stochastic volatility;
- regime switching;
- multiple factors with heterogeneous persistence;
- sparse vs dense loadings.

### Experimental control

Hold total observation budget approximately fixed:

\[
D=NT.
\]

Sweep aspect ratios across a wide range, e.g. many-short panels vs few-long panels.

Independently vary:

- factor strength / signal-to-idiosyncratic-noise ratio;
- factor dimensionality;
- persistence / mixing time;
- loading diversity;
- regime diversity;
- observation noise.

### Two orthogonal evaluation targets

**A. Future-state generalization**

Evaluate prediction on future latent-state realizations for known series/loadings.

**B. New-exposure / new-series generalization**

Evaluate on previously unseen loadings/series drawn from the same structural family.

Do not collapse these into one MSE number.

### Desired scientific product

A **breadth–depth phase diagram** showing what structural conditions make one axis more valuable than the other.

Potential stronger result: derive an effective information quantity or asymptotic expression that predicts the crossover.

---

## 6. E02 — zero-shot real-foundation-model validation

Only do this after E01 reveals a clean structural prediction.

Preferred setup:

- synchronized finance panel such as Finance1K;
- TimesFM-3 or another native multivariate zero-shot FM;
- no expensive model retraining initially.

For a fixed input/context budget, vary:

- number of contemporaneous variables/series;
- temporal history per series.

Test whether the E01 phase-diagram predictions carry to a real FM:

- does breadth become more valuable when cross-sectional commonality is stronger?
- does depth become more valuable when latent dynamics/regimes require more temporal coverage?
- do future-time and held-out-series generalization prefer different geometries?

Do not interpret a plain best-context-length result as success.

---

## 7. Evidence that would count as success

Any of the following can support the project:

1. **Irreducible 2D scaling:** equal `NT` produces stable, predictable performance differences explained by latent structure.
2. **Task-dependent geometry:** future-state and new-exposure generalization have systematically different optimal scaling directions.
3. **A collapse law:** raw `NT` fails, but a theoretically motivated effective-information quantity collapses the curves.
4. **A boundary/phase transition:** identify where additional breadth stops substituting for depth, or vice versa.

A null result is acceptable if it strongly demonstrates that an appropriate scalar effective-data law actually exists.

---

## 8. Kill / downgrade criteria

Downgrade or kill if:

- the only conclusion is “both N and T matter”;
- effects disappear under trivial rescaling and yield no explanatory law;
- there is no stable relation to factor strength/persistence/loading diversity;
- E01 requires arbitrary architecture tricks to produce the phenomenon;
- closest prior work already gives the same `L(N,T)` scientific conclusion;
- the real-FM part degenerates into context-window hyperparameter tuning.

---

## 9. Conference identity

The paper must read first as an **AI/ML scaling and multivariate representation question**, not as a stock-forecasting paper.

The finance panel is load-bearing because it supplies a natural shared-latent-environment geometry in which cross-sectional breadth and temporal depth have distinct statistical meanings.

A valid first sentence should resemble:

> Scaling laws typically summarize data with a scalar count, but multivariate foundation models observe data on multiple structural axes whose information content need not be interchangeable.

Not:

> Financial forecasting is important...

---

## 10. First local-agent task

1. Re-check the closest multivariate TSFM/scaling owners one final time.
2. Implement the minimal linear dynamic-factor world.
3. Construct fixed-`NT` grids with at least 5–7 substantially different aspect ratios.
4. Train a deliberately small sequence/multivariate model first; do not start with a giant FM.
5. Measure future-state and new-exposure generalization separately.
6. Sweep factor strength and persistence first; only add complexity if these already give an interpretable interaction.
7. If curves show no meaningful geometry after careful control, record the negative result and downgrade rather than inventing a method.
