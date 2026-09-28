# Route-Preference Objective vs Executed Top-K Decision

**Status: OBSERVATION — NOT A PAPER CANDIDATE**

This observation emerged from the killed CT03 MoE-routing lineage.

## Empirical fact

With the same frozen preferred routes, same linear router gate, and same data, parent-style preference training could satisfy the stated route preference while moving the deployed Top-K decision away from the preferred route.

Frozen-target probe:
- preference accuracy: **0.947**;
- preferred-route overlap: **3.77/8 → 1.05/8**;
- exact preferred-route adoption: **0.000**;
- executed-slot decomposition after training: **80.8%** of selected experts belonged to neither the preferred nor rejected route.

A target-directed execution-aligned control could move overlap toward the preferred route, so "the gate simply cannot move" is not a sufficient explanation.

## Why this is scientifically interesting

The factorized pairwise route preference constrains relative scores of the compared sets. Deterministic Top-K execution additionally requires preferred experts to outrank all outside competitors. Those are different decision objects.

The observation explains why better counterfactual supervision need not become better executed routing.

## Why this is not automatically a new paper

Top-K surrogate consistency/calibration and top-K preference/ranking literature already own the broad idea that a surrogate preference need not be decision-consistent.

Therefore the current status is deliberately **Observation**, not "CT04".

A future candidate would need an independently important MoE-specific consequence that cannot be reviewer-compressed to known top-K surrogate inconsistency. Do not start by searching hinge/listwise/Plackett-Luce/soft-top-k losses until one works.

Canonical underlying evidence remains in:
- `candidates/CT03_COUNTERFACTUAL_CREDIT_MOE_ROUTING/`

The old `candidates/CT04_ROUTE_PREFERENCE_DECISION_CONSISTENCY/` candidate wrapper was removed to avoid duplicate CT numbering and premature paper identity.
