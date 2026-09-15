# 2026-09-14 — WALL-C / IP03 Grokking Addendum

**Parent report:** `search_rounds/2026-09-14_WALL_C_EXPRESSIVITY_LEARNABILITY_EXHAUSTION.md`  
**Purpose:** close the last anti-miss branch: post-fit algorithm replacement / grokking.  
**Outcome:** **NO REOPENING — NO L — NO PILOT**

## Question audited

After a network has already fit the training set, what determines whether it later moves from a memorizing / heuristic solution to an OOD-generalizing computation?

This was the last plausible IP03 descendant because it directly concerns selection among training-equivalent computations rather than mere expressivity.

## Why a single trigger quantity is not currently a viable scientific parent

The current grokking literature already supports a multi-factor competing-solution picture rather than a universal scalar trigger:

1. **Property-specific regularization.** ICML 2025, *Grokking Beyond the Euclidean Norm of Model Parameters*, shows that if a generalizing model has a property P (e.g. sparse or low-rank), small non-zero regularization toward P can induce grokking. L2 norm is not universal. Overparameterization and data selection can also induce grokking / ungrokking.

2. **Solution volume / entropy.** NeurIPS 2025 work studies grokking through the volume / Boltzmann entropy of memorizing and generalizing solution regions rather than a single complexity scalar.

3. **Competing-basin geometry.** 2026 Singular Learning Theory work explicitly models grokking as a phase transition between competing near-zero-loss basins, characterized through local learning coefficients / degeneracy / posterior mass.

4. **Multiple dynamic predictors.** 2025–2026 work studies weight norm, spectral structure, rate–distortion complexity, data fraction, width, regularization and other phase variables. This is already an active theory program; another scalar or early-warning statistic would be metric-first unless it overturns a mature causal account.

5. **Algorithm-replacement story itself is unstable.** Findings ACL 2026, *Is Grokking Worthwhile? Functional Analysis and Transferability of Generalization Circuits in Transformers*, reports that grokked and non-grokked models can use the same inference paths for in-distribution compositional queries, and that unseen-case accuracy and formation of a particular reasoning path can dissociate. Thus `grokking = sudden acquisition of a new algorithm` cannot be assumed as the mother phenomenon.

## Reviewer compression

> “Another grokking trigger / complexity proxy / phase indicator.”

or

> “Another mechanistic description of memorization-to-generalization transition inside the already active competing-basin / regularization program.”

## Final consequence for IP03

This closes the last major natural branch omitted from the parent exhaustion report. The current accessible IP03 space is occupied at all obvious levels: representational succinctness, parameter geometry / function prior, restricted learnable program classes, scratchpad/interface representations, data-induced algorithm selection, initialization / optimizer bias, pretraining-modified architectural bias, feature competition, and late-training grokking dynamics.

Reopen only if a future result creates a **same-computation contradiction** among mature selection theories under matched architecture/data/objective/optimizer, or introduces a genuinely new identifying operation rather than another complexity statistic.
