# WALL-AF — Process rewards: credit assignment or objective redefinition?

Date: 2026-09-15
Status: EXHAUSTED AS STANDALONE GENERATOR

## Mother question
Modern reasoning/agent RL frequently adds step-level or process rewards and describes them as denser learning signals for sparse outcome objectives. Classical reward-shaping theory says arbitrary intermediate rewards can change the optimal policy; potential-based reward shaping is the canonical policy-invariant construction. Do modern process rewards merely improve credit assignment, or do they redefine the task?

## Why this was promising
Ng, Harada & Russell's reward-shaping theorem gives a theory-first invariant rather than an anomaly-first empirical hook: potential-based shaping can preserve the original optimal-policy set, whereas arbitrary shaping need not. This creates a natural distinction between optimization assistance and objective change.

## Direct-owner chain
- Chan et al., ICML 2024, *Dense Reward for Free in Reinforcement Learning from Human Feedback*, explicitly densifies terminal RLHF reward and proves equivalence to potential-based reward shaping, preserving the optimal policy while improving learning stability/speed.
- ICLR 2026 *Linking Process to Outcome: Conditional Reward Modeling for LLM Reasoning* explicitly constructs step rewards through a potential function tied by chain rule to final outcome probability, using PBRS precisely to maintain a principled outcome connection and improve robustness.
- 2025–2026 agentic and robotic RL work likewise derives process signals as potential-based/policy-invariant shaping rewards.
- In parallel, contemporary PRM robustness work already shows that unconstrained process rewards can be reward-hacked and can drive reward upward while ground-truth accuracy stays poor.

Thus the central distinction—policy-invariant credit-assignment aid versus objective-changing process reward—is already a direct theoretical and empirical program.

## Verdict
No L-series. Measuring how far existing PRMs depart from potential-based form would collapse into a diagnostic/evaluation contribution unless a different old theory supplies a new decisive quantity.

## Anti-resurrection
No:
- 'PRMs may change the objective';
- potential-based shaping applied to generic LLM reasoning as novelty;
- testing existing PRMs for policy invariance as a benchmark;
- reward hacking as evidence for objective redefinition without a new theory;
- dense-vs-sparse reward comparisons.
