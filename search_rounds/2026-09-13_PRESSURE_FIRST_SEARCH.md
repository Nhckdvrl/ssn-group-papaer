# 2026-09-13 — Pressure-First Search

This rolling log follows the corrected provenance doctrine:

> **scientific pressure first → matched/stress test → phenomenon second**

Do not default to mining already-published anomalies. Search old laws, widely used assumptions, evaluation/deployment mismatches, and causal explanations whose evidence is weaker than their influence.

Only a fully selected `PILOT-AUTHORIZED — E01 ONLY` topic is user-facing.

---

## Hook P1 — Is the benefit of easy→hard curriculum really ordering, or learning-rate timing?

**Status:** `DROP / DIRECT CAUSAL SUCCESSORS`

### Pressure

Curriculum learning is commonly motivated as an ordering effect: presenting easier examples before harder ones is supposed to improve optimization or learning. In modern LLM training, however, data order is mechanically coupled to optimizer time; under learning-rate decay, later hard/high-quality examples receive smaller updates.

A clean pressure-first question was therefore:

> **After matching effective update opportunity, does easy→hard order itself still help, or is part of the modern curriculum effect just where examples land on the LR schedule?**

### Why it dies

This is already too directly occupied. A 2025 study, *How Learning Rate Decay Wastes Your Best Data in Curriculum-Based LLM Pretraining*, explicitly identifies the incompatibility between ascending-quality curricula and decaying LR and shows that constant/matched LR can restore gains. A 2026 successor, *Understanding Curriculum Learning in LLMs via Cross-Difficulty Optimization Dynamics*, further analyzes curriculum schedules through transfer across difficulty levels and develops a schedule around that dynamics.

ACL 2026 work on mathematical-reasoning curricula also finds no universal forward/reverse ordering rule, reinforcing that the simple curriculum-order premise is already under active re-identification.

### Reviewer compression

> `Curriculum order is confounded with optimizer time + existing LLM studies already manipulate LR/data-order coupling and cross-difficulty transfer = our matched test.`

### Anti-resurrection

Do not reopen as `easy→hard only works because examples occur at high LR`, `match LR across curriculum stages`, or generic forward-vs-reverse curriculum unless a qualitatively new same-quantity contradiction emerges.

---

## Hook P2 — Does post-training create the LLM “hivemind,” or is common error structure inherited from pretraining?

**Status:** `DROP / PUBLIC DIRECT DECOMPOSITION ALREADY EXISTS`

### Pressure

ICML 2025 *Correlated Errors in Large Language Models* challenges a widely used assumption: diversity of providers, architectures, and training should yield meaningfully diverse mistakes. It finds high error correlation across hundreds of models. NeurIPS 2025 Best Paper *Artificial Hivemind* further establishes broad model-output homogeneity.

A natural matched-stage question was:

> **Is this convergence already present in base models, or does instruction/post-training make independently pretrained models converge toward the same behavior?**

The attractive E01 would compare matched base↔instruct checkpoints and then separate weight changes from chat-format effects.

### Why it dies

A public August-2026 study, *Where the Hivemind Comes From: Geometry, Tuning and Format, Separated on Open Weights*, already performs almost exactly this decomposition on six matched open-weight base/instruct pairs. It reports that base models do not reproduce the high homogeneity regime, instruction tuning contributes some increase, and applying the model's trained chat template to the same instruct weights produces a much larger shift; in their reported decomposition the format effect is roughly 4.6× the tuning effect.

The source is a public research article rather than a flagship-conference paper, but this project explicitly treats strong public work/blogs as novelty evidence. We should not pretend the direct experiment is open merely because it has not yet appeared in ACL/ICML.

### Reviewer compression

> `ICML/NeurIPS establish LLM homogeneity + the August-2026 open-weight study already separates base, instruction-tuned raw prompting, and chat-template prompting = proposed stage-localization study.`

### Anti-resurrection

Do not reopen as `does RLHF/SFT homogenize models`, `base vs instruct error correlation`, or `chat templates cause hivemind` without a different scientific quantity that the existing decomposition cannot answer.
