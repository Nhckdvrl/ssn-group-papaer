# WALL-AD — Generative vs discriminative sample complexity after pretraining

Date: 2026-09-15
Status: EXHAUSTED / DIRECTLY OWNED

## Mother question
Classical Ng–Jordan/Efron analyses compare learning a joint/generative model with learning a conditional/discriminative model from labeled data, producing the familiar two-regime tradeoff: generative classifiers can learn faster at small n but have worse asymptotic error. Does this law survive when both approaches inherit massive pretrained knowledge rather than estimating their models from scratch?

## Why this looked promising
Pretraining changes the statistical problem: neither model starts from an uninformative estimator, so the original sample-complexity intuition may cease to apply. This looked like a clean old-theorem -> modern-regime premise break.

## Direct-owner assassination
Kasa et al., EMNLP 2025 Outstanding Paper, *Generative or Discriminative? Revisiting Text Classification in the Era of Transformers*, already studies the classical two-regime question across modern transformer architectures. Crucially, the paper contains an explicit pretrained experiment using BERT-base and GPT-2-base under the same sample-size protocol. It reports that with pretrained weights the classical two-regime phenomenon no longer holds: the discriminative encoder generally outperforms the generative autoregressive classifier across data regimes, and connects this to prior vision findings that pretraining can eliminate the two-regime effect.

Therefore the tempting regime-change question is already part of the awarded paper itself, not an unowned sibling problem.

## Verdict
No L-series. Asking why the observed pretrained regime changes would be a direct mechanistic follow-up to Kasa et al. rather than an independently inherited scientific question.

## Anti-resurrection
Do not revive as:
- Ng–Jordan with BERT/GPT;
- 'does pretraining remove the generative low-data advantage?';
- larger pretrained models / more datasets / LoRA versions of the same comparison;
- mechanistic explanation of the specific EMNLP-2025 finding unless an independent older theory first supplies a decisive rival prediction.
