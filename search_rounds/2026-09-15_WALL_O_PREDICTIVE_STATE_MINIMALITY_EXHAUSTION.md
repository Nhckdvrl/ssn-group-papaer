# 2026-09-15 — WALL-O / Predictive State, Generative State, and Minimality

**Mode:** system-identification / computational-mechanics lineage → transformer belief-state program → exact minimality audit → identification audit  
**Outcome:** **EXHAUSTED AS A CURRENT TOPIC GENERATOR — NO NEW L-SERIES — NO PILOT**

# 1. Mother scientific problem

> **When a learner is trained only to predict observations, what notion of state is identified by the objective: the hidden state of a particular generative model, or only a state sufficient for predicting future observations?**

This is an old problem in dynamical systems and partially observed control, not a 2026 world-model slogan.

Predictive State Representations (Littman, Sutton & Singh, NeurIPS 2001 and successors) replace latent generator variables by predictions of future observable experiments. Computational mechanics defines causal states as equivalence classes of histories that induce the same conditional distribution over the entire future; these states are unique minimal sufficient statistics for prediction.

Thus a data-generating process can have many hidden-state presentations while possessing one canonical predictive quotient.

# 2. Modern transformer evidence

Shai et al. (2024), *Transformers Represent Belief State Geometry in their Residual Stream*, explicitly distinguish the hidden generative HMM from the Mixed-State Presentation used for prediction. They acknowledge that infinitely many HMMs can generate the same stochastic process and argue that transformers should learn the canonical/minimal predictive geometry rather than arbitrary generator labels.

They also show that next-token-degenerate belief states are nevertheless distinguished when they imply different distributions over the more distant future.

2026 work on constrained grid-world trajectories further shows that apparently `world-model-like` geometry in a Transformer can be traced directly to an analytically derived prediction-sufficient statistic.

At the same time, NextLat (2025) argues that an ordinary Transformer with growing attention memory has no inherent incentive to compress history into a compact recurrent latent state; its auxiliary objective is designed to force such compression.

This creates a real conceptual tension:

> predictive sufficiency is necessary for Bayes-optimal continuation, but minimality/compression does not automatically follow from ordinary Transformer training.

# 3. Strongest attempted residual

> **Does standard next-token training spontaneously select the unique minimal predictive state, or merely some overcomplete sufficient representation containing predictively irrelevant history?**

A seemingly decisive toy construction is to create histories that differ in a latent/history bit that was once informative but becomes provably irrelevant to the distribution of every possible future token. A minimal predictive representation must merge those histories; an overcomplete representation may keep them separate.

# 4. Why this does not survive Selection

## 4.1 The one-cell phenomenon is already known publicly

A June 2026 open experiment explicitly extends Shai et al. with predictively defunct state information and reports that a toy Transformer retains it in the residual stream; the information is shed only under imposed capacity pressure.

This is not a strong peer-reviewed owner, but it removes any basis for making `Transformer retains irrelevant history` itself the scientific discovery.

## 4.2 Whole-residual-stream minimality is the wrong claim

Shai et al. do not claim that the entire residual stream equals the minimal causal state. They claim that predictive/belief geometry is represented somewhere in the computation, potentially distributed across layers.

Therefore decoding an irrelevant history bit from the residual stream does not refute their predictive-state account. It only shows that the network can carry epiphenomenal extra information alongside the predictive computation.

To test whether the *prediction-relevant state* itself is minimal, one must first identify which subspace/computation constitutes that state. That returns immediately to WALL-A's causal-abstraction/alignment problem.

## 4.3 Causal use disappears by construction

If two histories are genuinely equivalent with respect to **all future observations**, then the latent distinction cannot have a legitimate causal effect on any future predictive behavior. The cleanest observable is therefore representational retention/decodability, not causal use.

This fails the current preference for a decisive model-computation inference rather than another probe/minimality metric.

## 4.4 Adding interventions changes the scientific object to a mature one

One can strengthen the test by making two histories observationally equivalent but distinguishable under future actions/interventions. However, this is precisely the controlled predictive-state problem.

Classical PSRs define state by the outcomes of future action-observation `tests`, where actions are interventions. 2026 UAI work further proves that capable decision-making under partial observability can force recovery of predictive/belief-like state and, in fully observed settings, the interventional transition kernel.

Thus the strengthened version enters a mature control-sufficiency / interventional-predictive-state program rather than creating a new NLP parent.

## 4.5 Forcing a bottleneck is WALL-D resurrection

Imposing dimensional/capacity pressure so that the model must choose which historical information to retain would make minimality identifiable, but it converts the project into `what structure appears under a resource bottleneck`, the just-exhausted WALL-D family.

# 5. Reviewer compression

The best current paper compresses to one of:

- `Shai belief states + check whether irrelevant history is still decodable`;
- `computational-mechanics causal states + Transformer probe`;
- `PSR control sufficiency + Transformer/world-model implementation`;
- `predictive-state minimality + bottleneck regularization`.

None leaves a large prior-work-inexpressible inference.

# 6. Decision

**WALL-O exhausted as a current generator.**

Keep the durable conceptual correction:

> **Generative latent state, observation-predictive state, control/interventional state, and the full neural activation state are not interchangeable scientific objects.**

In particular, `a model linearly represents hidden generator state` is not enough to establish that the generator ontology is uniquely identified by next-token prediction.

Do not regenerate minimal-state probes, redundant-HMM tests, action-conditioned variants, or capacity-pressure variants without a genuinely new substantive scientific parent.

No L-series is created.