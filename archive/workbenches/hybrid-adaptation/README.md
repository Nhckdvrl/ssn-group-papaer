# Hybrid Adaptation State Dynamics — Workbench

**Status: DEMOTED / NOT ACTIVE (2026-09-29 top-conference ceiling audit).**

This directory is retained as a literature/search asset, not an authorized execution line.

**Ceiling audit:** the current object is too broad and too close to already-owned 2026 work. S0 Tuning already establishes recurrent-state adaptation as a PEFT surface across Qwen3.5/Falcon-H1 and compares state tuning/state offsets with LoRA; *What Attention Recalls and Recurrence Controls in Hybrid Language Models* independently gives causal KV-vs-recurrent-state functional interventions. The current workbench has no stronger empirical pressure or broader changed premise beyond those parents.

**Reopen only if:** a new, independently important phenomenon appears that is not compressible to “which hybrid component should we tune?” or “KV and recurrent state play different roles,” and its best-case consequence is broader than one hybrid family/PEFT recipe.

This workbench studies how adaptation changes hybrid recurrent–attention language models.

The motivating literature contains real but not yet unified pressure:
- recurrent-only LoRA can behave differently across sequential and parallel hybrid topologies;
- direct state/state-offset tuning can be effective while recurrent weight adaptation can be brittle;
- attention KV and recurrent state can carry different functional roles;
- some post-training stages can damage long-range or routing behavior.

These facts justify studying the object. They do **not** establish a single paper question.

Start from matched checkpoints, strong baselines, stage comparisons, and simple state/KV interventions. First establish a reproducible effect in our regime. Let the eventual scientific question emerge from what actually moves, fails, or remains invariant.

Avoid creating a method before a bottleneck exists or using model-zoo breadth to search for a desired sign.
