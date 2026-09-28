# Hybrid Adaptation State Dynamics — Workbench

**Status: exploratory workbench — not a candidate.**

This workbench studies how adaptation changes hybrid recurrent–attention language models.

The motivating literature contains real but not yet unified pressure:
- recurrent-only LoRA can behave differently across sequential and parallel hybrid topologies;
- direct state/state-offset tuning can be effective while recurrent weight adaptation can be brittle;
- attention KV and recurrent state can carry different functional roles;
- some post-training stages can damage long-range or routing behavior.

These facts justify studying the object. They do **not** establish a single paper question.

Start from matched checkpoints, strong baselines, stage comparisons, and simple state/KV interventions. First establish a reproducible effect in our regime. Let the eventual scientific question emerge from what actually moves, fails, or remains invariant.

Avoid creating a method before a bottleneck exists or using model-zoo breadth to search for a desired sign.
