# WALL-AY — Prompt-invariant probability / confidence under semantic equivalence

Date: 2026-09-15
Status: EXHAUSTED / DIRECT PROGRAM EXISTS

## Mother question
Can answer probabilities be compared as a model-intrinsic belief/confidence scale across semantically equivalent prompts? If two prompts encode the same proposition and decision problem, should a meaningful epistemic confidence remain invariant, or can p(y|x) change arbitrarily with wording/template while preserving the underlying task?

## Direct-owner audit
This exact invariance question is already central to prompt-sensitivity and confidence-robustness research.

- Liu & Chu, ACL 2026, *Understanding the Prompt Sensitivity*, directly studies meaning-preserving prompt pairs and differences in next-token log probabilities. It derives a first-order/Taylor upper bound on log-probability change and attributes sensitivity to dispersion of similar inputs through model layers; prompt templates can influence logits more strongly than the questions themselves.
- Hua et al., EMNLP 2025, *Flaw or Artifact? Rethinking Prompt Sensitivity in Evaluating LLMs*, shows that substantial apparent prompt sensitivity can arise from evaluation artifacts including log-likelihood scoring and rigid answer matching that fail to respect semantically equivalent output realizations.
- 2026 confidence-robustness work directly studies protocol/language variation and semantic-equivalence/coherence constraints rather than pointwise confidence alone.
- ACL 2026 *Illusions of Confidence? Diagnosing LLM Truthfulness via Neighborhood Consistency* explicitly argues that pointwise confidence/self-consistency can hide brittle belief and evaluates coherence under mild contextual perturbations.
- Earlier prompt-probing work already documents strong paraphrase/template dependence of factual probabilities and uses prompt marginalization/ensembling/calibration to mitigate it.

## Verdict
No L-series. The core scientific statement—token probability is not automatically a prompt-invariant belief-strength scale—is already directly studied. A new semantic-equivalence set or prompt-invariant confidence metric would collapse into evaluation/calibration work.

## Anti-resurrection
Do not revive as:
- paraphrase probability invariance;
- semantically equivalent prompts with different confidence;
- prompt-invariant probability calibration;
- confidence robustness under wording/template changes;
- semantic-equivalence confidence metric;
- prompt marginalization as a scientific mechanism.
