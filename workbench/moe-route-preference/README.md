# MoE Route Preference vs Executed Top-K — Workbench

**Status: CLOSED AS ACTIVE PAPER LINE / KNOWLEDGE ASSET (2026-09-29 ceiling audit).**

This workbench inherits the strongest observation from the killed CT03 MoE-routing lineage.

Frozen-target probe:
- preference accuracy: **0.947**;
- preferred-route overlap: **3.77/8 → 1.05/8**;
- exact preferred-route adoption: **0.000**;
- **80.8%** of executed slots belonged to neither the preferred nor rejected route.

The current interpretation is that satisfying a factorized pairwise route preference is not the same decision object as controlling deterministic Top-K execution in the presence of outside competitors.

This is scientifically useful, but broad top-k surrogate consistency/calibration literature may already own the general phenomenon. Therefore this stays in the workbench.

Do **not** turn it into “try a different ranking loss until one works.” A paper candidate would require an independently important MoE-specific consequence or bottleneck.

Canonical historical evidence:
`../../archive/candidates/CT03_COUNTERFACTUAL_CREDIT_MOE_ROUTING/`


## Ceiling audit

The local observation remains valid, but its broader ceiling has been overtaken by *When Are Experts Misrouted? Counterfactual Routing Analysis in Mixture-of-Experts Language Models* (2026), which directly compares executed routes against equal-compute counterfactual alternatives across multiple modern MoEs, identifies routing failures on fragile reasoning tokens, and demonstrates a router-only intervention with downstream reasoning effects.

Therefore the current line should **not** be revived as a routing-loss/ranking-consistency paper. Reopen only if a distinct MoE-specific consequence appears that the counterfactual-routing literature does not already explain.
