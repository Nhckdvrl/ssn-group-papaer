# 2026-09-15 — WALL-Q / Mechanistic Degeneracy and Universality

**Mode:** multiple-realization ancestry → convergent-learning lineage → mechanistic-universality program → owner audit  
**Outcome:** **EXHAUSTED AS A CURRENT TOPIC GENERATOR — NO NEW L-SERIES — NO PILOT**

# 1. Mother problem

> **When multiple learned systems exhibit the same behavior, which aspects of their internal causal organization are forced by the task/learning problem and which are contingent realizations of optimization history?**

This is older than mechanistic interpretability. Neuroscience and complex-systems work uses `degeneracy` / multiple realization for cases in which structurally distinct mechanisms produce the same function. Neural-network research has asked since at least the mid-2010s whether independent training runs converge to common representations.

Li et al. (2015), *Convergent Learning*, already find a mixed picture: some features recur across runs, common low-dimensional subspaces can emerge while particular basis vectors differ, and other features remain idiosyncratic.

Source: https://proceedings.mlr.press/v44/li15convergent.html

# 2. Modern mechanistic interpretability directly owns the parent

Chughtai, Chan & Nanda (ICML 2023), *A Toy Model of Universality*, explicitly name universality as a central mechanistic-interpretability hypothesis: models trained on similar tasks may learn similar features/circuits. Their controlled group-composition setting gives exactly the relevant mixed result: models can be characterized by a common family of algorithms, while the precise circuit and order of development for an individual run remain arbitrary.

Source: https://proceedings.mlr.press/v202/chughtai23a.html

Anthropic's 2023 *Interpretability Dreams* likewise treats universality as a load-bearing question for whether studying one model teaches us about others.

Source: https://transformer-circuits.pub/2023/interpretability-dreams/index.html

# 3. Current owner density

The program has expanded rather than leaving the parent open:

- universal neurons across independently trained GPT-2 seeds;
- ICLR 2025 comparison of mechanistic similarity across Transformer and Mamba architectures;
- 2026 circuit-stability studies across refits/seeds;
- 2026 cross-architecture numerical-comparison circuits showing within-family convergence but qualitatively different implementations across families;
- 2026 work on representation-similarity calibration revisiting the Platonic Representation Hypothesis.

Representative sources:
- https://arxiv.org/abs/2401.12181
- https://openreview.net/forum?id=2J18i8T0oI
- https://arxiv.org/abs/2602.16740
- https://arxiv.org/abs/2602.14486

The parent question `what is universal versus contingent?` is therefore itself an active research program.

# 4. Why no descendant survives

The most attractive restatement was:

> **What causal organization is invariant across functionally equivalent independently trained models, after quotienting out coordinate/basis symmetries?**

But this is not a residual outside the program. It is precisely the sharpened universality/identifiability question current work is pursuing.

Natural descendants all compress:

- another task/behavior across seeds → universality case study;
- larger LLMs → scale extension;
- causal instead of representational comparison → stronger universality metric;
- architecture comparison → already direct current work;
- align coordinate systems before comparison → representation-identifiability/alignment program;
- ask why some circuits converge → learning-dynamics/implicit-bias program, overlapping IP03.

# 5. Decision

**WALL-Q exhausted as current generator.**

Keep the evidence-standard lesson:

> **A mechanism found in one trained instance should not automatically be described as `the` mechanism of the task/model class.**

But do not generate another cross-seed/cross-model circuit universality study without a substantive scientific parent outside universality itself.

No L-series is created.