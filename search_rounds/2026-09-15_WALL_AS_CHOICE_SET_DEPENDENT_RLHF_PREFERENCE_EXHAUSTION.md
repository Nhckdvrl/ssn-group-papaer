# WALL-AS — Choice-set dependent preferences / IIA in RLHF

Date: 2026-09-15
Status: EXHAUSTED / DIRECTLY OWNED

## Mother question
Standard pairwise reward models such as Bradley–Terry treat the preference between responses A and B as independent of what other alternatives are present. Classical choice theory shows attraction/decoy/menu effects in which adding an irrelevant or dominated option C changes the relative preference between A and B. If human feedback for language models has the same property, the choice set is itself a causal variable and a context-independent scalar reward can be misspecified.

## Direct-owner assassination
Xu et al. (2023/ICML 2024 workshop), *RLHF and IIA: Perverse Incentives*, addresses exactly this premise. It argues that existing RLHF algorithms rely on preference models satisfying Independence of Irrelevant Alternatives (IIA), demonstrates violations of IIA in human preferences for text content, and shows that the assumption can generate perverse incentives and obstruct richer query formats/learning algorithms.

The statistical-identification layer is also directly occupied. Cherapanamjeri et al. (2025), *Learning Correlated Reward Models: Statistical Barriers and Opportunities*, studies non-IIA correlated random-utility models and proves that ordinary pairwise preference data is fundamentally insufficient to identify correlational structure, while best-of-three feedback can recover it efficiently.

Classical Tversky–Simonson context-dependent choice supplies the older intellectual ancestry, but the exact bridge into RLHF has already been made.

## Stronger residual considered and rejected
One could ask whether policy optimization changes the candidate/menu distribution and therefore changes the preference target itself (a performative-preference effect). However, without an independently inherited unresolved theory this reviewer-compresses to `RLHF-and-IIA + performative prediction`, i.e. prohibited A+B recombination.

## Verdict
No L-series.

## Anti-resurrection
Do not revive as:
- decoy/attraction effects in RLHF annotation;
- IIA violations in human preferences over LLM responses;
- pairwise feedback cannot recover context-dependent preferences;
- best-of-three/listwise feedback as the solution;
- contextual Bradley–Terry for RLHF as novelty;
- policy-induced choice-set shift framed as new unless an independent old theory yields a nontrivial same-quantity prediction.
