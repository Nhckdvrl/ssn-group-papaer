# WALL-AW — Pretraining prior strength vs resistance to contradictory learning

Date: 2026-09-15
Status: EXHAUSTED / DIRECT MECHANISM PROGRAM EXISTS

## Mother question
When post-training evidence contradicts a strongly encoded pretrained belief, what determines how much evidence/update is required to change behavior? A Bayesian account suggests resistance should track prior odds; an optimization/geometry account allows equally probable behaviors to differ in update difficulty because of parameter/gradient geometry.

## Direct-owner audit
The modern knowledge-conflict literature already studies this axis directly.

- 2026 *The Override Gap: A Magnitude Account of Knowledge Conflict Failure in Hypernetwork-Based Instant LLM Adaptation* measures base-model log-probability as prior strength and finds a strong monotonic relation between pretrained margin and failure to internalize conflicting facts. It proposes an explicit competition condition between pretrained margin and adapter/update magnitude, and causally rescues strong-prior conflicts by selectively amplifying the update.
- Findings ACL 2025 KaFT stratifies fine-tuning examples by degree of conflict with internal knowledge and finds conflict strength materially changes SFT outcomes.
- ICML 2025 Spotlight *Taming Knowledge Conflicts in Language Models* provides a direct mechanistic program for parametric-memory versus contextual-evidence conflict.
- 2024–2026 work already studies counterfactual/contradictory knowledge under prompting, SFT, editing, and multilingual conditions.

## Verdict
No L-series. Prior strength versus override resistance and its relation to update magnitude is already a directly measured mechanism, not an unowned Bayesian-vs-optimization fork.

## Anti-resurrection
Do not revive as:
- stronger pretrained facts require more SFT examples;
- prior log-probability predicts resistance to counterfactual updates;
- Bayesian prior strength vs gradient magnitude on factual knowledge;
- multilingual/domain versions of the same conflict curve;
- larger-model replication of the override-gap account.
