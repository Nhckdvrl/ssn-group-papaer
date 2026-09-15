# WALL-Z — Conditional compatibility in masked language models

Date: 2026-09-15
Status: EXHAUSTED AS STANDALONE GENERATOR

## Mother question
Masked/pseudolikelihood training learns many bidirectional conditional distributions. Do these conditionals correspond to any common joint distribution? If not, what global distribution is induced when they are iteratively used for generation?

## Why this is scientifically real
Conditional compatibility is an old statistics / dependency-network / Gibbs-sampling problem. Unlike a left-to-right autoregressive factorization, an unrestricted collection of full conditionals need not be compatible with any joint distribution. Modern masked generative models make this a load-bearing issue rather than a philosophical detail.

## Direct-owner chain
- Earlier work on deriving language models from MLMs explicitly formulates MLM conditionals as dependency networks and distinguishes compatible from incompatible conditionals, including near-compatible joint recovery.
- EMNLP 2024 CONTESTS directly notes that MLM training contains no mechanism guaranteeing a unique/common joint and empirically tests probability consistency under alternative completion/conditioning orders.
- ICML 2024 Promises and Pitfalls of Generative Masked Language Modeling explicitly asks how well fitting conditionals recovers a joint distribution and analyzes Markov-chain generation.
- 2026 Mixing Times of Glauber Dynamics on Masked Language Models directly proves/diagnoses incompatibility with a rectangle test and studies the global Markov chain induced by those conditionals, including fast-mixing and metastable regimes and an empirical temperature-dependent phase transition.

## Verdict
The strongest residual—conditional incompatibility -> stationary/mixing distortion—is directly occupied. No new L-series.

## Anti-resurrection
Do not revive as:
- 'MLM conditionals may be inconsistent';
- alternative order consistency tests;
- compatibility score/metric on larger models;
- Gibbs sampling from incompatible MLMs;
- temperature/mixing phase-transition replication;
- masked/diffusion LM generation framed around this same incompatibility without a genuinely new old-theory question.
