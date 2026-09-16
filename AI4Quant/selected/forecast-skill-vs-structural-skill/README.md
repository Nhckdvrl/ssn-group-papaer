# P2 — Forecast Skill ≠ Structural Skill

## Working title

**Do Multivariate Foundation Models Actually Learn Error-Correcting Structure?**

## Status

**PILOT-AUTHORIZED**

This folder is the canonical registration for this topic. Do not reduce it to “can TimesFM predict a cointegrated spread?”

---

## 1. Mother question

A multivariate foundation model can achieve strong ordinary forecast loss while still failing to acquire the structural mechanism that generated the data.

Cointegration gives an unusually clean test case. Let

\[
z_t=\beta^\top x_t
\]

be the deviation from a long-run equilibrium relation. In a VECM-style world,

\[
\Delta x_{t+1}=\alpha z_t + \text{short-run dynamics}+\epsilon_{t+1}.
\]

The defining structural skill is not merely predicting the next vector accurately; it is learning that an intervention on the equilibrium gap `z_t` should induce a restoring drift with the correct direction and magnitude.

The scientific question is:

> **Does exposure to a mechanism in multivariate pretraining lead foundation models to acquire that mechanism, when standard forecast objectives provide only weak pressure to represent it explicitly?**

This is intentionally broader than cointegration. Cointegration is the first controlled mechanism because it gives a known, testable restoring law.

---

## 2. Core distinction

### Forecast skill

Low MSE / MASE / CRPS / quantile loss on ordinary trajectories.

### Structural skill

Correct response to controlled perturbations of the mechanism-relevant state.

For cointegration, define

\[
R(z)=\beta^\top \mathbb E[\Delta \hat x_{t+1}\mid z_t=z].
\]

A structurally correct model should exhibit a restoring relationship consistent with the true error-correction law, approximately tracking

\[
\beta^\top\alpha z.
\]

A model can therefore be good at the ordinary forecasting objective while wrong about the mechanism.

The target result is a region where:

> **ordinary forecast scores are nearly indistinguishable, but structural response is sharply different.**

---

## 3. Why this is not “old VECM beats deep learning”

Do not make the paper about:

- pairs trading performance;
- whether VECM beats a Transformer on MSE;
- adding an ECM layer to a neural network;
- enforcing cointegration as a regularizer;
- discovering cointegrated pairs;
- generic long-horizon consistency.

The paper is about **mechanism acquisition under modern foundation-model pretraining/evaluation**.

A particularly important modern lever is that recent multivariate TSFM pretraining pipelines can explicitly include synthetic cointegration processes, yet standard evaluations may still use generic forecasting metrics rather than directly testing the restoring mechanism.

This creates the stronger question:

> **Exposure to mechanism ≠ acquisition of mechanism.**

If a model has actually seen cointegrated generators during pretraining but fails the controlled restoring-law test, the failure cannot be dismissed as merely “the model never saw this data family.”

---

## 4. Owner boundary

Important nearby work that does not directly own this question:

- classical cointegration / VECM / ECM;
- neural networks that explicitly include error-correction terms;
- work predicting cointegrated equity spreads with TSFMs;
- generic forecast reconciliation;
- ICML 2026 work on correcting autoregressive rollout prediction errors, which is conceptually distinct from learning a cross-series cointegrating equilibrium relation;
- standard synthetic-pretraining papers that include cointegration but evaluate with ordinary forecast metrics.

The project must be reconsidered if a direct paper is found that already evaluates modern multivariate foundation models by intervening on cointegration gaps and measuring whether their predicted drift follows the correct restoring law.

---

## 5. Competing scientific accounts

### Account A — predictive training implicitly acquires the mechanism

If the mechanism materially improves prediction, a sufficiently capable multivariate FM should internalize it even without a special structural loss.

Then as ordinary forecast quality/model scale improves, structural response should converge toward the true restoring law.

### Account B — ordinary loss leaves the mechanism weakly identified

A model can fit local predictive statistics or exploit shortcuts while failing to encode the restoring relation itself.

Then:

- MSE may improve substantially;
- yet intervention-on-gap response remains wrong, weak, asymmetric, or unstable;
- explicit exposure to cointegrated data does not guarantee acquisition of error correction.

### Account C — mechanism acquisition is regime dependent

Models may acquire the restoring law only when:

- equilibrium deviations are sufficiently large/frequent;
- correction speed is high enough;
- short-run dynamics do not mask the long-run signal;
- context/horizon is long enough;
- multivariate coupling is sufficiently visible.

A phase diagram over these conditions is preferable to a binary pass/fail result.

---

## 6. E01 — controlled zero-training structural diagnostic

### Synthetic world

Generate VECM / cointegrated systems with known parameters:

\[
\Delta x_{t+1}=\alpha \beta^\top x_t + \Gamma\Delta x_t + \epsilon_{t+1}.
\]

Control:

- cointegrating vector `β`;
- correction vector/rate `α`;
- short-run dynamics `Γ`;
- innovation covariance;
- dimensionality;
- equilibrium-gap distribution;
- signal-to-noise ratio;
- horizon.

### Matched intervention

Construct contexts that are identical or tightly matched except for a controlled equilibrium gap

\[
z_t=\beta^\top x_t.
\]

Sweep positive and negative `z` values.

For each model, measure

\[
R(z)=\beta^\top\mathbb E[\Delta \hat x_{t+1}\mid z_t=z].
\]

Compare:

- sign of restoring response;
- slope relative to the true `βᵀα`;
- symmetry for positive/negative gaps;
- response across horizons;
- response stability across context lengths/scales.

### Models

Start zero-shot with public multivariate-capable models where possible, prioritizing:

- TiRex-2;
- Chronos-2;
- TimesFM-3.

No fine-tuning initially.

---

## 7. Ordinary forecasting control

Always report ordinary metrics on the same systems:

- MSE / MAE;
- MASE where appropriate;
- probabilistic score if available.

The decisive evidence is not merely low structural score; it is **decoupling** between ordinary forecast skill and restoring-law skill.

Search specifically for regimes where:

\[
\Delta \text{MSE} \approx 0
\]

but

\[
\Delta \text{StructuralError}
\]

is large.

This directly supports the title **Forecast Skill ≠ Structural Skill**.

---

## 8. Strong E02 extensions

Only after E01 shows a real phenomenon.

Potential directions:

### Mechanism exposure

Compare models/pretraining settings known to include vs omit synthetic cointegration families.

Question:

> Does explicit pretraining exposure improve structural response independently of ordinary forecast score?

### Mechanism frequency

Control how frequently equilibrium deviations requiring correction appear in training data.

Question:

> How much learning pressure is required before a mechanism becomes structurally represented?

### Scale

If multiple model sizes exist, test whether structural skill scales with parameter/data size at the same rate as ordinary loss.

### Mechanism transfer

Train/evaluate on one family of `β, α` and intervene on unseen equilibrium geometries.

This tests whether the model learned a reusable error-correction principle rather than memorized a narrow synthetic family.

---

## 9. Evidence that would count as success

Strong outcomes include:

1. **Forecast–structure dissociation:** similar ordinary loss, very different restoring-law behavior.
2. **Exposure–acquisition gap:** a model pretrained on cointegrated generators still fails structural intervention tests.
3. **Mechanism threshold:** structural skill emerges only beyond a measurable frequency/strength/context regime.
4. **Different scaling laws:** ordinary forecast loss improves smoothly with scale while structural skill saturates or emerges at a different rate.
5. **Positive result:** some FMs genuinely recover the restoring law, allowing us to identify what objective/data conditions are sufficient for structural acquisition.

A clean positive result is scientifically valid; the project is not based on betting that models must fail.

---

## 10. Kill / downgrade criteria

Downgrade or kill if:

- the experiment reduces to “VECM has lower error than FM”;
- structural response is trivially implied by ordinary one-step MSE in all relevant regimes;
- no regime produces a meaningful separation between forecast and structural skill;
- closest work already performs the same intervention-on-gap diagnostic;
- the only contribution becomes adding a cointegration loss/regularizer;
- real-model failures disappear once a trivial API/normalization issue is corrected;
- results depend on an arbitrary synthetic construction rather than the mechanism itself.

---

## 11. Conference identity

The first-order contribution must be about **what predictive foundation models learn from mechanisms present in their data**, not about financial pairs trading.

Finance is load-bearing because cointegration/error correction provides:

- a known latent structural relation;
- a manipulable deviation variable;
- a precise predicted response;
- a clean separation between observational forecast quality and mechanism-level competence.

A good opening sentence would resemble:

> Foundation models are usually evaluated by predictive loss, but low loss need not imply that the model has acquired the mechanisms that govern its data.

Not:

> Cointegration is widely used in finance...

---

## 12. First local-agent task

1. Re-run one final owner search focused specifically on intervention-on-cointegration-gap diagnostics for foundation models.
2. Implement a minimal 2D VECM generator with known `α, β`.
3. Build matched contexts with controlled positive/negative equilibrium gaps.
4. Query one public multivariate FM zero-shot.
5. Compute both ordinary forecast loss and restoring-response curve `R(z)`.
6. Verify whether structural response remains identifiable after accounting for normalization/API behavior.
7. Add a second model only after the diagnostic pipeline is correct.
8. If no forecast/structure dissociation exists across a reasonable parameter sweep, downgrade honestly rather than adding a method to manufacture a gap.
