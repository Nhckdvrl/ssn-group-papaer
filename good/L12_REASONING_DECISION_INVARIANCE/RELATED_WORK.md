# L12 Live Related Work and Novelty Audit

**Search date:** 2026-09-09

## Direct owners

### Mind the (DH) Gap! - ACL 2026 Outstanding

<https://aclanthology.org/2026.acl-long.479/>

Owns the broad risky-choice result: reasoning models are less sensitive to order, gain/loss framing, explanation, and description/history presentation. L12 cannot claim that reasoning models are simply more rational or invariant.

### Reasoning Traces Shape Outputs but Models Won't Say So - ACL 2026

<https://aclanthology.org/2026.acl-long.1986/>

Owns generic causal evidence that injected reasoning changes outputs. Thus full-trajectory injection is substrate, not L12's paper identity.

### LLMs Faithfully and Iteratively Compute Answers During Chain-of-Thought - Findings EACL 2026

<https://aclanthology.org/2026.findings-eacl.59/>

Owns iterative answer computation during CoT in controlled arithmetic. E07 cannot be sold as the generic observation that answers form before the final token.

### Reasoning Fine-Tuning Induces Persistent Latent Policy States - COLM 2026

<https://arxiv.org/abs/2607.18532>

The closest new collision. It frames reasoning-tuned models as switching dynamical systems, identifies persistent latent policy states, and uses state swaps/transplants to argue that reasoning fine-tuning globally reorganizes latent dynamics. L12 therefore cannot claim generic latent policy states or global reorganization from reasoning fine-tuning.

### CASE: Causally Aligned Self-Explanation - 2026

<https://arxiv.org/abs/2607.18820>

Formalizes and trains an instruction-to-CoT-to-answer causal route while suppressing direct shortcuts. It is close to L12's control-route language, but it proposes a training method rather than explaining the established presentation-invariance transition.

## Evidence-depth comparators

- **Racing Thoughts** (NAACL 2025): computational hypothesis, correlational evidence, causal evidence, then intervention. <https://aclanthology.org/2025.naacl-long.155/>
- **The LLM Language Network** (NAACL 2025): localization becomes scientifically useful only after causal ablation and breadth. <https://aclanthology.org/2025.naacl-long.544/>
- **Scaling Reasoning, Losing Control** (ACL 2026): reasoning-oriented training can trade off against external instruction control, but does not identify the internal route behind framing invariance. <https://aclanthology.org/2026.acl-long.1878/>

## Strongest reviewer compression

> Mind the DH Gap + iterative CoT computation/trace injection + persistent latent policy states.

This compression wins if L12 claims only that reasoning is causal, choices emerge through a trajectory, or a late hidden state can be swapped.

It does not yet own the complete L12 identity:

> an established presentation-invariance transition
> + matched sibling post-training branches
> + terminal-stripped distributed decision control
> + pre-answer choice-state mediation
> + a direct prompt-by-trajectory factorial showing that trajectory-relative causal control rises sharply in the reasoning branch.

The unique center is not a generic latent state. It is the **mechanistic explanation of presentation invariance as a training-associated reallocation of causal control**.

## Novelty verdict after E10-E11

**Paper identity survives and now has stimulus breadth.** E09 is essential: without the control factorial, recent work compresses E07-E08. E10 shows the branch-level control reorganization on 36 independent decisions, and E11 replicates the internal state profile on a preregistered 18-decision subset. The remaining empirical vulnerability is checkpoint/model-family breadth, while the remaining conceptual vulnerability is collision with generic latent-policy-state language.
