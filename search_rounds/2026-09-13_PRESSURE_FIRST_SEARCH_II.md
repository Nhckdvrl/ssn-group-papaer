# 2026-09-13 — Pressure-First Search II

Continuation of `2026-09-13_PRESSURE_FIRST_SEARCH.md`. Keep this compact and persist serious dead routes immediately.

Only a fully selected `PILOT-AUTHORIZED — E01 ONLY` topic is user-facing.

---

## Hook P6 — Why can near-zero-loss “hyperfitting” improve free-running generation?

**Status:** `DROP / DIRECT ICML-2026 MECHANISM SUCCESSOR`

### Pressure

ICLR 2025 *The Hyperfitting Phenomenon* challenges the ordinary overfitting/early-stopping intuition for pretrained autoregressive models. Fine-tuning on a tiny dataset all the way to near-zero training loss can substantially improve long free-running generation under greedy decoding, across model sizes/domains and even autoregressive image generation. The effect is not explained by copying the tiny training set, and hyperfitted models become extremely low-entropy.

The natural next question would be why severe fitting stabilizes generation rather than merely memorizing the small dataset.

### Why it dies

ICML 2026 *Beyond Temperature: Hyperfitting as a Late-Stage Geometric Expansion* directly takes this mechanism question. It entropy-matches the base model and shows temperature sharpening cannot reproduce the generation gain; it rules out static vocabulary reweighting, identifies context-dependent token-rank reordering, localizes the largest representational change to the terminal transformer block, and shows that adapting only the last few layers can reproduce the useful behavior. This is a direct mechanism successor rather than a loose neighboring paper.

A follow-up asking whether low entropy, static logit bias, or generic last-layer specialization explains hyperfitting is therefore already owned. A deeper causal intervention on the reported terminal expansion would be a refinement of the ICML-2026 mechanism, not a fresh Main-level parent under the current bar.

### Reviewer compression

> `ICLR 2025 establishes the hyperfitting anomaly + ICML 2026 falsifies temperature/static-bias accounts, localizes dynamic rank reordering to late layers, and reproduces it with late-stage adaptation = the mechanism program.`

### Anti-resurrection

Do not reopen as `why hyperfitting improves generation`, `low entropy but high diversity`, `hyperfitting is learned temperature`, `deep-tail promotion`, or `terminal expansion causes hyperfitting` unless a qualitatively new contradiction appears that the ICML-2026 account cannot predict.
