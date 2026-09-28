# Hybrid Adaptation State Dynamics

**Status: TERRITORY — NOT A CANDIDATE**

This territory asks how adaptation changes hybrid recurrent–attention language models.

The motivating literature contains real but not yet unified pressure:
- recurrent-only LoRA can behave differently across sequential and parallel hybrid topologies;
- direct state/state-offset tuning can be effective while recurrent weight adaptation can be brittle;
- attention KV and recurrent state can carry different functional roles;
- some post-training stages can damage long-range or routing behavior.

These facts justify studying the object. They do **not** yet establish a single paper question.

## What we need before candidateization

First establish a strong, reproducible observation in our regime, for example a stable adaptation-induced change that:
- is not generic representation drift;
- survives a reasonable seed/recipe check;
- differs from a pure-Transformer control in an interpretable way;
- can be localized to state, transition, or channel allocation without an explosion of interventions.

Until such an observation exists, "what moves during adaptation?" remains exploratory identification.

## Discovery priorities

Prefer:
- matched base/adapted checkpoints;
- strong task baselines;
- simple state/KV causal interventions;
- stage comparisons where the underlying checkpoint family is genuinely comparable;
- early tests for generic drift and recipe sensitivity.

Avoid:
- creating a method before the bottleneck exists;
- model-zoo breadth to search for a desired sign;
- declaring topology-specific mechanisms from incomparable training recipes.

A future candidate must be born from an observed stable effect, not from this territory description.
