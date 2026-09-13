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

---

## Hook H — Is one-step proto-token reconstruction a learned language capability or random-Transformer programmability?

**Status:** `DROP / ANTI-RESURRECTION + REVIEWER COMPRESSION`

### Origin

Mezentsev & Oseledets, EMNLP 2025 Main, *Exploring the Hidden Capacity of LLMs for One-Step Text Generation*, shows that a frozen causal LM can reconstruct hundreds of target tokens in a single parallel forward pass from only two optimized continuous proto-token embeddings. A 2026 successor analyzes semantic/syntactic content and stability of these proto-tokens.

Sources:
- https://aclanthology.org/2025.emnlp-main.1165/
- https://arxiv.org/abs/2602.18301

The initially attractive missing sentence was:

> Is this hundreds-token one-step reconstruction created by language pretraining, or is it largely an architectural property of a Transformer that two continuous vectors can program?

Pythia makes a cheap experiment possible because the exact same architecture/tokenizer is released from `step0` initialization through 154 checkpoints.

### Why it dies

First, this violates the current round's anti-resurrection intent. The user explicitly marked **token cramming / parallel token reconstruction** as a route not to rediscover after 2026 mechanistic work showed brittle steering rather than transferable semantic compression and localized causal interactions to early layers. The one-step paper is directly descended from that family: its official repository states that data and loaders are borrowed from Kuratov et al.'s token-cramming repository. Reframing the axis as `architecture vs pretraining` does not create a sufficiently independent scientific object.

Second, the proposed distinction is already strongly reviewer-compressible from adjacent prompt-expressivity work. NeurIPS 2025 *Prompt Tuning Transformers for Data Memorization* explicitly uses randomly initialized frozen Transformers to separate architectural expressivity from pretraining and shows that learned continuous prompts can memorize finite datasets. An August-2026 theory paper, *Training-Free Universal Approximation by Prompting Random Transformers*, goes further and proves that appropriate soft prompts can make random softmax-attention networks approximate broad function classes without pretraining.

Those priors do not perform the exact two-vector parallel reconstruction experiment, but they make the strongest positive result — `a random frozen Transformer can be programmed by continuous vectors` — substantially predictable. The remaining exact operating point is too close to an already-banned reconstruction family to clear the Main-level ownership bar.

### Strongest reviewer compression

> `Parallel reconstruction is already a cramming-descended capacity phenomenon + random frozen Transformers are already known to be highly expressive under learned soft prompts = test the same fact in the two-proto-token setup.`

### Anti-resurrection

Do not reopen as `pretraining is unnecessary for proto-token reconstruction`, `step0 Pythia already reconstructs`, `when during pretraining does parallel reconstruction emerge`, or `architecture vs language knowledge in two-vector reconstruction` unless a qualitatively new contradiction appears that is independent of the cramming/reconstruction parent.
