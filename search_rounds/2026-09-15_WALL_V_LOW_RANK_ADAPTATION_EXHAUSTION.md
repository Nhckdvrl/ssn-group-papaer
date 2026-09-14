# 2026-09-15 — WALL-V / Why Does Low-Rank Adaptation Work?

**Mode:** intrinsic-dimension ancestry → LoRA load-bearing claim → full-FT spectral challenge → theory/owner audit  
**Outcome:** **EXHAUSTED AS A CURRENT TOPIC GENERATOR — NO NEW L-SERIES — NO PILOT**

# 1. Mother problem

> Why can an enormous pretrained network be adapted to a new task through a tiny constrained parameterization, and what notion of low-dimensionality is actually relevant?

Aghajanyan et al. (ACL 2021) argue that pretrained language models have low **intrinsic fine-tuning dimension**: a task can often be solved by optimizing in a low-dimensional random parameter subspace.

LoRA operationalizes a different notion: each adapted weight matrix receives a low-**matrix-rank** update.

These notions are not logically equivalent.

# 2. The folk explanation is already under direct attack

The common story that LoRA succeeds because full fine-tuning itself learns low-rank updates is not generally supported.

Biderman et al. (2024), *LoRA Learns Less and Forgets Less*, find that full-fine-tuning perturbations can require ranks 10–100× larger than standard LoRA ranks, while LoRA often learns less of the target domain and preserves more base behavior.

Shuttleworth et al., NeurIPS 2025, *LoRA vs Full Fine-tuning: An Illusion of Equivalence*, show qualitatively different spectral structure: LoRA introduces high-ranking `intruder dimensions` absent from full FT and these directions causally mediate forgetting.

ICLR 2026 work on gradient intrinsic dimensionality further measures >100× mismatch between vanilla LoRA rank and effective FFT gradient dimensions in some settings.

Representative sources:
- https://arxiv.org/abs/2405.09673
- https://www.microsoft.com/en-us/research/publication/lora-vs-full-fine-tuning-an-illusion-of-equivalence/
- https://proceedings.iclr.cc/paper_files/paper/2026/hash/5b4b967d4222d87fa5b28b6ec7144058-Abstract-Conference.html

# 3. The explanation space is already a dense theory program

Current theory directly studies:

- expressivity of low-rank adaptation;
- existence of low-rank global solutions in NTK regimes;
- absence/presence of spurious minima;
- implicit bias from zero initialization / weight decay;
- singular-space alignment between pretrained and target models;
- spectral strength and alignment as distinct from rank;
- full-rank parameter-efficient adaptation using pretrained spectral bases.

Representative sources:
- ICML 2024: https://proceedings.mlr.press/v235/jang24d.html
- ICLR 2024: https://proceedings.iclr.cc/paper_files/paper/2024/hash/154926e0b66e2b2a8c1120852f31a12d-Abstract-Conference.html
- AISTATS 2025: https://proceedings.mlr.press/v258/xu25h.html
- ICML 2025: https://proceedings.mlr.press/v267/kim25n.html

# 4. Reviewer compression

Any attractive residual currently compresses to an active program:

- `intrinsic dimension ≠ matrix rank` → already exposed by full-FT spectral analyses;
- `LoRA is regularization, not approximation` → learning/forgetting and spectral studies;
- `which pretrained directions make adaptation easy?` → spectral-alignment theory;
- `when does LoRA fail?` → domain-shift/rank/gradient-dimension studies;
- `full-rank PEFT can work` → current full-rank spectral-preconditioning methods.

# 5. Decision

**WALL-V exhausted as current generator.**

Keep the conceptual lesson:

> low task intrinsic dimension, low gradient dimension, and low matrix rank are distinct scientific quantities; success of one constrained parameterization does not establish that full fine-tuning naturally follows the same geometry.

But this distinction and its consequences are already direct prior work.

No L-series is created.