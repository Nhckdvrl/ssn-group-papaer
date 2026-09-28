# MoE Route Preference vs Executed Top-K — Workbench

**Status: stable local observation / knowledge asset — not a paper candidate.**

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
