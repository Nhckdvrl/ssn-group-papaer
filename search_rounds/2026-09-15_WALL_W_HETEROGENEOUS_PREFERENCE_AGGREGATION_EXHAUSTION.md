# WALL-W — Heterogeneous preference aggregation / scalar reward rationalizability

Date: 2026-09-15
Status: EXHAUSTED AS STANDALONE GENERATOR

## Mother question
If each individual annotator has a transitive, scalar-rationalizable preference, does pooling heterogeneous annotators preserve representability by a single scalar reward? If not, what does RLHF/DPO learn when the aggregate preference itself is non-rationalizable?

## Why this looked promising
This has a genuine old intellectual lineage in utility theory, social choice, Bradley–Terry/random-utility modeling, and population preference aggregation. The modern alignment stack makes scalar reward a load-bearing modeling assumption rather than a minor statistical convenience.

## Direct-owner assassination
Nash Learning from Human Feedback (ICML 2024) already contains the decisive construction: even when every individual human has a totally ordered/transitive scalar scoring function, averaging across humans can produce a cyclic aggregate pairwise preference. This exact individual-rationalizable -> aggregate-nontransitive residual is therefore directly owned, not merely adjacent.

The same paper explicitly uses this limitation to motivate pairwise preference models and Nash optimization rather than a scalar reward. MaxMin-RLHF (ICML 2024) independently establishes an impossibility result for single-reward alignment under diverse human preferences. Subsequent NLHF/EGPO/MNPO/MCHF work has already developed alternative objectives, algorithms, and quantitative decompositions of the non-transitive residual.

## Verdict
KILL as a new L-series source. The core theorem, failure mode, and alternative objective family already exist.

## Anti-resurrection
Do not revive as:
- annotator heterogeneity causes cycles;
- Condorcet paradox in RLHF;
- scalar reward cannot represent population preference;
- transitive individuals but intransitive aggregate;
- DPO/RLHF under cyclic preference;
- new dataset/model demonstrating the same phenomenon;
- replacing reward model with pairwise game as the main novelty.
