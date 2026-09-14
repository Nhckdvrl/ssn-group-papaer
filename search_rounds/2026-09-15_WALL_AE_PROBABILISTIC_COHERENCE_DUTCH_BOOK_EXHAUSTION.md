# WALL-AE — Can LM Forecasts Belong to One Coherent Belief Distribution?

Date: 2026-09-15
Status: EXHAUSTED BY DIRECT VERY-RECENT OWNER

## Mother question
When a language model assigns probabilities to many logically related natural-language propositions under separate prompts, can those probabilities be jointly represented by any single coherent probability measure? Or are they mutually incompatible even before calibration against outcomes is considered?

## Old ancestry
This is not ordinary confidence calibration. Classical probabilistic coherence (de Finetti / Dutch-book arguments) imposes exact cross-event constraints on a set of subjective probabilities. A collection of forecasts that violates those constraints cannot all be marginals/conditionals of one coherent belief distribution and permits a guaranteed-profit betting portfolio.

## Why this looked promising
Modern LMs define token-level conditional distributions but users often interpret verbal/numerical forecasts across prompts as expressions of one underlying set of beliefs. This creates a sharp distinction:

- per-question calibration or proper-scoring-rule optimality;
- cross-question probabilistic coherence.

The latter admits a decisive quantity independent of outcome labels: maximal Dutch-book arbitrage profit / feasibility of a joint probability measure satisfying the elicited constraints.

## Direct owner
Andrews & Sarkar, *Dutch Books for Language Models* (arXiv:2609.02797, 2026-09-02) directly implements essentially this object. It elicits LLM forecasts over related events, uses linear programs motivated by de Finetti's theorem to find the largest guaranteed Dutch-book profit, requires no realized outcome labels, and reports substantial incoherence.

The surrounding uncertainty program is also active:
- ICLR 2026 *Beyond Binary Rewards* trains reasoning LMs with proper scoring rules for calibrated confidence.
- ICML 2026 *Reaching Beyond the Mode* trains models to produce distributions over multiple plausible answers.
- ICML 2026 position work explicitly argues for cross-input self-consistency rather than independent input-output evaluation.

## Verdict
The exact strongest formulation of this wall was independently occupied days before this search. It is therefore NOT a candidate. Extending the Dutch-book evaluation to another domain, more models, natural-language logical identities, or a new coherence metric would be a descendant.

## Searcher lesson
This was a healthy near-frontier derivation: old theory supplied a nontrivial invariant (coherence), modern practice supplied a regime where users implicitly interpret independent prompts as one belief system, and the theory yielded a label-free decisive test. The fact that a very recent paper independently chose the same object is evidence that this generator shape is productive.

## Anti-resurrection
Do not revive as:
- Kolmogorov consistency of LLM beliefs;
- Dutch-book incoherence of LLM forecasts;
- marginalization/conjunction identities across prompts;
- calibration-vs-coherence comparisons;
- joint-belief feasibility on a new benchmark/domain;
- training a model merely to reduce Dutch-book profit.

Reopen only if a distinct older theory introduces a qualitatively different object than probabilistic coherence itself.
