# 2026-09-13 — Live Search After L32 II

Continuation of `2026-09-13_LIVE_SEARCH_AFTER_L32.md`. Keep this file compact; seriously investigated dead hooks are persisted immediately.

**Rule:** only a fully selected `PILOT-AUTHORIZED — E01 ONLY` topic is user-facing.

---

## Hook E — Why can deleting training data improve factual memorization?

**Status:** `DROP / MOTHER PAPER OWNS THE EXPLANATION`

### Origin

Ye, Feldman & Talwar, ICML 2026, *Cram Less to Fit More: Training Data Pruning Improves Memorization of Facts*, reports a striking effect: under finite model knowledge capacity and strongly skewed fact frequencies, loss-based data selection can make a model memorize **more** facts by training on **less** data. On an annotated Wikipedia setup, GPT-2 small memorizes about 1.3× more entity facts after pruning and can match a much larger model trained on the full data.

Source: https://arxiv.org/abs/2604.08519

### Why it dies

The attractive title-level question — `why can less data produce more remembered facts?` — is already the paper's scientific center. The authors explicitly model finite knowledge capacity together with the long-tailed frequency distribution of facts. When repeated/high-frequency material consumes training budget and representational capacity, selection simultaneously limits the number of competing facts and flattens their exposure distribution; the semisynthetic experiments push factual accuracy toward the derived capacity limit.

A follow-up that merely decomposes which examples are removed, measures gradient competition, or reframes the result as interference would therefore refine a mechanism the mother already states rather than supply the missing sentence.

### Reviewer compression

> `Finite per-model knowledge capacity + power-law fact frequency + loss-based selection reallocates scarce capacity toward underlearned facts = why pruning can increase memorized-fact count.`

### Anti-resurrection

Do not reopen as `why less data memorizes more`, `data pruning frees knowledge capacity`, or `long-tail facts compete for parameters` unless a future same-quantity result violates the capacity/frequency account.

---

## Hook F — Why does doubling parameter precision barely increase memorization capacity?

**Status:** `DROP / DIRECT PREDECESSOR OWNS PRECISION-INSENSITIVITY`

### Origin

ICML 2026 Honorable Mention *How Much Can Language Models Memorize?* estimates a GPT-style memorization capacity of roughly 3.6 bits per parameter and reports only a small increase from BF16 to FP32 despite twice the physical storage precision.

This first looked like a clean architecture/computation anomaly: where did the extra numerical bits go?

### Why it dies

The phenomenon predates the ICML paper. Allen-Zhu & Li, ICLR 2025, *Physics of Language Models: Part 3.3, Knowledge Capacity Scaling Laws*, already argues that factual/knowledge capacity is approximately a small constant number of useful bits per parameter and reports little or no benefit from 16→32-bit parameter precision (with additional quantization experiments). Thus `why don't raw parameter bits translate linearly into stored knowledge bits?` is already an explicit capacity-scaling object, not an unexplained side anomaly newly exposed in 2026.

The remaining mechanism question quickly reviewer-compresses to familiar finite-precision/optimization/function-space redundancy arguments unless a new intervention reveals a quantity not predicted by that predecessor.

### Anti-resurrection

Do not reopen as `why FP32 stores only slightly more than BF16`, `unused parameter bits`, or generic `bits-per-parameter vs numerical precision` without a qualitatively new contradiction to existing knowledge-capacity scaling work.

---

## Hook G — Why did modern MT become robust to character noise without explicit robustness training?

**Status:** `DROP FOR CURRENT PROJECT / TRAINING-DATA CAUSE IS ESTABLISHED, SELECTIVE MECHANISM REQUIRES EXPENSIVE RE-TRAINING`

### Origin

Peters & Martins, ACL 2025 Main, *Did Translation Models Get More Robust Without Anyone Even Noticing?*, revisits the classic fragility of NMT to character corruption. Modern multilingual MT systems and LLMs are dramatically more robust to swaps, drops, duplication, and keyboard noise than older NMT systems, even when clean translation quality is comparable and none was explicitly trained for these perturbations.

Source: https://aclanthology.org/2025.acl-long.295/

### Owner / identification audit

The paper already rules out the easiest explanations. It compares similarly sized multilingual models with sharply different robustness and trains a decoder-only 1.3B translation LM on the older OPUS/Tatoeba-style data; the newly trained decoder-only model remains roughly as vulnerable as the old OPUS system. The authors therefore conclude that **training data**, rather than model size or decoder-only architecture, is the dominant source of the modern robustness shift. Tokenization stability is correlated with some cases but does not provide one cross-language explanation.

That leaves a scientifically attractive question — *what property of modern pretraining/multilingual data creates the robustness?* — but no L32-like cheap selective intervention was found. Natural candidates (orthographic-noise exposure, web/social-media text, broader language diversity, tokenizer co-adaptation) are entangled in already-trained checkpoints. Correlating them across model zoos is not causal; faithfully separating them requires controlled continued/pretraining data interventions at a scale where the mother robustness phenotype is known to hold.

A tiny synthetic MT reproduction would show that one ingredient *can* confer robustness, not identify the cause of the natural ACL-2025 mother. This is a cost/bridge failure, not a claim that the scientific gap is unimportant.

### Reviewer compression / stop rule

> `ACL 2025 already localizes the regime change to training data; a cheap follow-up can only correlate candidate corpus properties, while a causal answer requires controlled data training.`

### Anti-resurrection

Do not shrink this into a tokenizer audit, model-zoo robustness survey, or toy character-noise augmentation paper. Reopen only if a public checkpoint/data intervention or naturally matched training experiment makes the modern training-data cause selectively identifiable at bounded cost.
