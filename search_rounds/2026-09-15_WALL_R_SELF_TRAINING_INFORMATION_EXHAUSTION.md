# 2026-09-15 — WALL-R / Where Does Self-Training Improvement Come From?

**Mode:** classical pseudo-labeling ancestry → information-source audit → LLM self-rewarding frontier → theory/owner audit  
**Outcome:** **EXHAUSTED AS A CURRENT TOPIC GENERATOR — NO NEW L-SERIES — NO PILOT**

# 1. Mother problem

> **If a learner is trained on labels, preferences, or samples produced by itself or a closely related teacher, what source of information or inductive pressure can make the new learner better than the producer rather than merely reproduce its errors?**

This is older than LLM self-improvement. Pseudo-labeling, entropy minimization, self-training, knowledge distillation and born-again networks have long exhibited the apparently paradoxical phenomenon that a student trained substantially on teacher/model-generated targets can improve over the initial predictor.

# 2. Classical theory already resolves the naive paradox

The naive statement `the model trains on its own predictions, therefore no improvement is possible` is false because self-training systems normally change more than the labels:

- they expose the learner to additional unlabeled inputs;
- pseudo-label selection changes which regions of input space receive training pressure;
- regularization / augmentation can impose smoothness or low-density-boundary assumptions;
- retraining from a new initialization can change implicit regularization;
- confidence/entropy objectives can sharpen predictions;
- teacher and student may differ in capacity or optimization.

Theory work from 2020–2022 gives conditions under which self-training provably improves generalization and suppresses spurious features under distributional assumptions.

Representative sources:
- https://ai.stanford.edu/blog/understanding-self-training/
- https://proceedings.neurips.cc/paper/2020/file/f1298750ed09618717f9c10ea8d1d3b0-Paper.pdf

Thus `how can own pseudo-labels create information?` is not an unresolved information-theoretic paradox in generic form.

# 3. LLM self-rewarding is already a direct program

Yuan et al. (ICML 2024), *Self-Rewarding Language Models*, make the same model both generator and judge and iteratively optimize preferences. Meta-Rewarding, process-based self-rewarding and temporal variants explicitly modify the feedback loop to sustain or refine the learning signal.

Sources:
- https://proceedings.mlr.press/v235/yuan24d.html
- https://aclanthology.org/2025.findings-acl.930/

2026 theory work explicitly titled *Why Self-Rewarding Works* derives conditions/finite-sample guarantees for iterative alignment and emphasizes dependence on initial model quality.

Source:
- https://arxiv.org/abs/2601.22513

Failure work studies the complementary phenomenon: self-evaluation can drift or collapse, amplifying its own errors rather than improving an external target.

# 4. Why no candidate survives

The strongest scientific restatement would be:

> **Which transformation in a closed self-training loop supplies genuinely new learning pressure: new inputs, stochastic exploration, filtering/selection, evaluator–actor asymmetry, objective change, or regularization?**

But this is already the decomposition studied across classical self-training and modern self-rewarding variants. A new LLM experiment would reviewer-compress to:

> `classical self-training improvement theory + Self-Rewarding LLM dynamics`.

If all external prompts/input variation and transformations are removed and the learner simply maximum-likelihood trains on iid samples from its own unchanged distribution, the population optimum is a fixed point; demonstrating that fact is too elementary to support a Main paper.

If filtering/judging/augmentation is added, the scientific object becomes exactly which extra transformation provides the signal — an active self-training/self-rewarding program.

The tempting `self-improvement only surfaces latent capability` version also collides with the just-exhausted reachable-capability / elicitation WALL-H.

# 5. Decision

**WALL-R exhausted as current generator.**

Keep the durable correction:

> **Self-generated targets alone do not imply information creation; any improvement claim must identify the additional input distribution, selection operator, regularizer, evaluator asymmetry, or objective that changes the learning problem.**

Do not regenerate generic self-rewarding ablations, synthetic-data iteration counts, self-judge drift, or teacher/student paradox papers without a new scientific parent.

No L-series is created.