# WALL-AQ — Model editing: parameter locality vs rational belief revision

Date: 2026-09-15
Status: EXHAUSTED / DIRECTLY OWNED

## Mother question
Knowledge editing methods often seek a local parameter/behavioral change: alter one fact while preserving unrelated outputs. Classical belief revision instead asks how a knowledge state should change coherently after new evidence, including propagation to logical/probabilistic consequences. Is a locally minimal parameter edit semantically the wrong notion of minimal change?

## Direct-owner assassination
Hase et al. (2024), *Fundamental Problems With Model Editing: How Should Rational Belief Revision Work in LLMs?*, frames model editing explicitly as the longstanding philosophical/statistical problem of belief revision. It critiques the standard editing formulation, enumerates conceptual problems including far-reaching consequences and probabilistic entailment, and evaluates models against an idealized Bayesian-agent standard.

This is surrounded by a direct ripple-effect program:
- Findings EMNLP 2023 evaluates specificity and implication awareness under factual edits;
- TACL 2024 RippleEdits defines downstream facts that must change after an edit and shows existing editors fail to propagate them;
- ACL 2025 ChainEdit explicitly propagates logical-rule-guided edit chains;
- 2026 work continues logical-consequence benchmarking and reasoning-aware editing.

## Verdict
No L-series. The apparent conflict between local model edits and globally coherent semantic revision is already the conceptual foundation of an active model-editing program.

## Anti-resurrection
Do not revive as:
- AGM/belief revision applied to LLM editing;
- locality versus logical ripple effects;
- edit one fact and test entailed consequences;
- Bayesian ideal-agent editing benchmark;
- logical-consistency-aware knowledge editing without a distinct independent question.
