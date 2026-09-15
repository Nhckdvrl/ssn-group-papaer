# WALL-Z — Learned Inductive Bias from Prior Tasks

Date: 2026-09-15
Status: EXHAUSTED AS A CURRENT GENERATOR; IP02 REMAINS IMPORTANT

## Mother question
Can inductive bias itself be learned from prior experience, and what properties of source tasks reshape the learner's effective hypothesis space for later tasks?

## Old lineage
- Caruana (ICML 1993) framed multitask supervision as a source of inductive bias.
- Baxter (JAIR 2000), *A Model of Inductive Bias Learning*, formalized learning a hypothesis-space bias from an environment of related tasks.
- Learning-to-learn / meta-learning and hierarchical Bayes continue this program.

## Modern direct ownership
ACL 2025 Outstanding Paper *Between Circuits and Chomsky* directly asks which properties of formal-language pre-pretraining impart useful inductive biases to later natural-language learning. It gives both structural hypotheses (dependency structure and compatibility with architectural computational limits) and mechanistic evidence of transferred components.

## Why no new candidate
The broad question and the modern Transformer instantiation are both occupied. Further grids over source formal languages, source-task similarity, or transferred heads/circuits would be descendants of this active program. A sharper future reopening of IP02 needs a distinct theoretical contradiction, not another demonstration that prior tasks reshape later generalization.

## Anti-resurrection
Do not revive as learned inductive bias, formal-language pre-pretraining, source-task structure predicts transfer, transferred attention heads, or learning-to-learn for linguistic generalization without a new theory-level contradiction.
