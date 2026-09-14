# WALL-AB — Bayesian in-context learning and coherence constraints

Date: 2026-09-15
Status: EXHAUSTED AS STANDALONE GENERATOR

## Mother question
If in-context learning is Bayesian posterior updating over latent tasks/concepts, which classical coherence constraints must the model satisfy, and can these distinguish Bayesian inference from pattern matching or implicit optimization?

## Direct-owner audit
The Bayesian-ICL program is already mature:
- Xie et al. and subsequent work formalize ICL as implicit Bayesian inference / latent concept inference.
- ICLR 2024 work studies ICL through the Bayesian prism and compares empirical transformers with Bayesian predictors.
- ICML 2025 shows transformers can be trained to perform full Bayesian inference in context for nontrivial statistical models.
- A martingale-perspective line explicitly identifies exchangeability/order invariance as a structural Bayesian implication.
- 2026 work directly addresses the objection that real LLM predictions depend on serialization order ('Bayesian in expectation, not in realization').

Thus the attractive recipe 'choose a Bayesian coherence axiom and test a real LLM' is already the standard program rather than a new scientific question.

## Verdict
No new L-series. In particular do not revive this through demonstration-order effects.

## Anti-resurrection
No:
- permutation/order invariance as a new Bayesian test;
- duplicate-evidence/order tests without a new old-theory quantity;
- real-LLM replication of Bayesian-vs-gradient-descent toy analyses;
- another task family showing approximate posterior updating.
