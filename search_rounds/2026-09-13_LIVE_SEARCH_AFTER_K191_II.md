# 2026-09-13 — Live Search After K191 II

**Purpose:** continuation of `2026-09-13_LIVE_SEARCH_AFTER_K191.md`. Keep newly assassinated hooks in a separate compact file to reduce risk from large-file updates under unstable network conditions.

**Rule:** only a fully selected `PILOT-AUTHORIZED` topic is actionable. Everything below is dead / non-actionable unless a qualitatively different scientific contradiction appears.

---

## Hook G — Early SFT dynamics predict final performance

**Status:** `DROP / NON-INDEPENDENT OPTIMIZATION SIGNAL`

### Hook

Recent SFT studies report that runs with smaller early gradient norms / slower early loss reduction can end with better downstream performance. The tempting RQ is whether successful SFT deliberately avoids rapid early adaptation and preserves a more general pretrained basin.

### Why it dies

The reported pattern is tightly coupled to ordinary optimization controls such as lower learning rate and larger batch size. Nearby 2025–2026 work already makes small-update / low-learning-rate fine-tuning a direct strategy for reducing pretrained-capability degradation while retaining target-domain gains. Consequently, `small early gradient -> better final model` is not an independent stable mother phenomenon with a clearly separate mechanism; it is largely a diagnostic shadow of known update-size / over-adaptation dynamics.

A mechanism project would therefore reviewer-compress to `lower effective update magnitude preserves pretrained features`, unless a future paper shows the gradient-norm relation after matching effective parameter displacement / optimizer trajectory.

### Verdict

**DROP.** Do not reopen as `why is slower SFT better?`, `early gradient norm predicts generalization`, or `high initial loss is beneficial` without a same-quantity residual effect after optimization controls.

---

## Hook H — Massive activations / activation outliers as an unexplained architectural anomaly

**Status:** `DROP / PARENT SATURATED`

### Hook

Massive activations and attention sinks are visually striking, stable across many modern LMs, and initially look like an ideal `stable anomaly -> unresolved why` source.

### Owner assassination

The natural mechanism space is already heavily centralized:

- Sun et al. (2024), *Massive Activations in Large Language Models*, show rare huge activations act like implicit bias terms; explicit attention biases can remove the need for them.
- ICLR 2026 *Attention Sinks and Compression Valleys in LLMs are Two Sides of the Same Coin* connects sinks / massive activations to a depth-wise compression mechanism and Mix–Compress–Refine organization.
- 2026 follow-ups separately study the pre-norm origin, gradient sinks, FFN/RMSNorm emergence, and hybrid/linear-attention morphology.
- MoE-specific 2026 work also gives direct super-expert / massive-activation mechanisms.

The obvious questions — why massive activations emerge, whether they are required for sinks, which block creates them, and what they do functionally — are therefore already an active mechanistic line rather than an unnamed gap.

### Verdict

**DROP.** Do not spend new-search budget on generic activation-outlier / massive-activation mechanisms unless a new strong result contradicts the existing sink/bias/compression explanations on the same quantity.

---

## Hook I — Attention-output modifications preserve LM loss but destroy downstream capability

**Status:** `DROP / PARENT ITSELF EXPLAINS MAIN FAILURE + STRONG PRIOR THEORY`

### Origin

arXiv 2605.20798 / EMNLP-2026 submission, *Most Transformer Modifications Still Do Not Transfer at 1-3B*, performs a controlled 20-modification study at 1.2B and partial 3B scale. Two attention-side failures are striking:

- Sigmoid Attention: validation loss only ~2.4% worse than baseline but CLIMB average drops ~16 points; LAMBADA falls from ~0.42 to near zero.
- SSMax: validation loss only ~3% worse but CLIMB average drops ~6 points.

This looks at first like a strong `same pretraining loss, radically different capability` anomaly.

Primary source: https://arxiv.org/abs/2605.20798

### Why the obvious mechanism question is already mostly owned

The paper's Appendix E directly diagnoses the strongest Sigmoid failure. Without softmax row normalization, learned attention is more diffuse and fails to concentrate on a single retrieval-relevant key; LAMBADA is therefore catastrophically affected while generic next-token modeling remains usable. The same appendix finds SSMax has a smaller uniform drift because its learned per-head temperature does not stabilize near softmax's effective value, and at 3B exhibits known softmax-replacement logit blowup.

This is not merely author speculation sitting alone. Ramapuram et al. (2024/2025), *Theory, Analysis, and Best Practices for Sigmoid Self-Attention*, already shows that properly normalized/stabilized sigmoid attention can match softmax across language, vision, and speech, identifying attention-norm stabilization as load-bearing. Associative-memory theory further explains softmax / QK normalization in terms of competitive precise retrieval.

Nearby 2026 linear-attention work explicitly describes softmax's missing ingredient as `global competition` needed for robust retrieval under distractors.

### Strongest reviewer compression

> `The new architecture survey shows near-loss attention failures; its appendix already attributes the largest failure to diffuse key selection; sigmoid-attention work already shows normalization/stabilization fixes it; associative-memory theory already explains why competitive normalization supports retrieval.`

A project asking `why can attention changes preserve perplexity but hurt LAMBADA?` would therefore mostly mechanize an explanation already stated and independently supported. SSMax also has a different, more uniform failure signature, so there is not yet one clean shared hidden quantity across the two methods.

### Verdict

**DROP.** Do not revive as `perplexity misses retrieval ability`, `softmax is needed for selection`, or `attention concentration is a hidden capability axis` unless a separate repeated anomaly survives after matching normalization/selectivity and cannot be explained by existing associative-memory theory.
