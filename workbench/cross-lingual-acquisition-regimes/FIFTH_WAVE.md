# Fifth Wave: Context Dependence And Joint Error Structure

Status: exploratory; no candidate, no training. Started 2026-09-30, recorded 2026-10-01 JST.

## Completed Context Gate

Six additional Macaroni frozen runs cover noswitch/code-switch x seeds 42/43/44 under the already fixed unrelated-story donor assignment. Original endings and semantic gold labels are unchanged. All 36,264 new rows completed; actual prompt hashes, complete semantic keys, finite scores and identical original/control checkpoint manifests verified.

Chinese context -> English ending, three-seed means:

| Readout | Original mono / CS | Shuffled mono / CS | Original CS effect | Shuffled CS effect | Context DiD [fixed-seed item 95% CI] |
| --- | --- | --- | --- | --- | --- |
| Raw accuracy (%) | 48.07 / 50.14 | 48.38 / 47.80 | +2.07 pp | -0.57 pp | +2.65 [1.39, 3.93] pp |
| Token-normalized accuracy (%) | 51.73 / 53.28 | 52.20 / 51.91 | +1.54 pp | -0.29 pp | +1.83 [0.29, 3.35] pp |
| Character-normalized accuracy (%) | 53.45 / 55.26 | 53.45 / 53.89 | +1.81 pp | +0.44 pp | +1.37 [-0.02, 2.76] pp |
| Prior-adjusted accuracy (%) | 51.60 / 54.62 | 50.17 / 51.47 | +3.02 pp | +1.30 pp | +1.72 [-0.88, 4.28] pp |

Raw context DiD is positive at each seed (+1.85/+3.18/+2.91 pp). Prior-adjusted accuracy DiD is not (-0.60/+2.12/+3.64 pp). Raw gold-versus-foil margin DiD is +0.361 nats [0.180, 0.539], positive at all seeds; the prior-adjusted margin DiD is algebraically the same because the ending prior cancels between original and shuffled contexts. Those two margins are NOT independent corroboration.

There is useful original-context gain, so this is not solely a damaged-control artifact. However, unrelated context also changes topical/lexical compatibility; near-chance frozen continuation is not proof of improved reasoning. One donor assignment, three released seeds, exploratory uncorrected item intervals, no training-population inference. English->Chinese prior-adjusted DiD (+3.99 pp) has only +0.38 pp original gain and -3.62 pp shuffled decline; do not promote that larger interaction. Native Chinese prior-adjusted DiD is positive despite worse original useful accuracy; also not a capability gain.

Decision: retain a bounded functional-context signal, not a paper identity. Further donor permutations on this same benchmark would only refine this local result; they are not the next research-scale advance. Independent semantic intervention/task support and acquisition/content controls remain necessary.

## Field-Scale Branch Before New Analysis

Question: can bilingual coupling alter the *joint correctness structure* across equivalent language views even when mean native accuracy changes little? This could distinguish access redundancy from additional competence, but generic cross-language consistency is already owned. This is a falsification/triage analysis, not a novel-metric proposal.

Read primary Factual Consistency of Multilingual Pretrained Language Models (Findings ACL 2022), methods and results: consistency must be accompanied by correctness; repeated wrong answers can inflate agreement. https://aclanthology.org/2022.findings-acl.240.pdf

CLiKA (NAACL 2024) already defines performance, consistency and conductivity, and reports shallow alignment. Initial PDF route failed; the alternate Anthology route succeeded. Primary Sections 3-6 now read: correct prediction overlap, artificial translated entity names with English-only relation learning, LoRA conductivity tests, German and reverse-translation controls. Generic performance/consistency/transfer separation is owned. Its public-model comparisons do not content/compute-match all pretraining interventions. https://aclanthology.org/2024.naacl-long.339/

New 2026 primary paper Improving Cross-Lingual Factual Recall via Consistency-Driven Reinforcement Learning directly studies parallel CPT versus factual access and consistency. Primary Sections 3-5 now read: 235.5M-token parallel CPT, OLMo/Qwen 7B, PolyFact SFT and all-languages-correct GRPO reward, free-generation KLAR and Global-MMLU transfer. CPT does not generally improve these tasks; head overlap is larger for SFT despite better functional GRPO results. Generic alignment/access, shared-head metrics or consistency-driven training are insufficiently distinct. It does not provide translated-unpaired versus explicit-paired CPT controls. https://arxiv.org/html/2606.06586v1

Predeclared cheap screen: reuse ORIGINAL native/native XStoryCloze outputs only. Macaroni EN/ ZH, noswitch/switch/par, all three released seeds; JGP ID/ZH, nominal 160K no/multi/nonadj/distributed. Report every existing readout. Compute both-correct, both-wrong, one-language-only correct, disagreement, oracle-any-correct and correctness covariance `P(both correct)-P(correct L1)P(correct L2)`. Covariance subtracts the independent-marginal baseline but is NOT a causal estimate or an item-difficulty adjustment. Binary choice agreement equals equal correctness; this assay cannot diagnose shared wrong semantic answers in multi-option QA.

No pooled cross-family average, no selected checkpoint comparison, no significance fishing. A direction that does not replicate within all three Macaroni seeds or is readout-dependent is demoted. A consistent direction would still require independent task evidence and matched-content intervention, not automatic candidate status. No additional GPU inference is needed for this screen.

## Joint-Error Screen Outcome

All 13 original runs pass actual input-hash and finite-score checks. Analysis is descriptive, with no uncertainty/significance claim; machine-readable joint tables are `results/p3_joint_errors.json`.

| Contrast | Raw covariance change, per seed | Prior-adjusted covariance change, per seed | Token-normalized covariance change, per seed |
| --- | --- | --- | --- |
| Macaroni CS - mono | +.00435 / +.00148 / +.00180 | +.00335 / +.01603 / +.02012 | +.01015 / -.00618 / -.00466 |
| Macaroni par - mono | +.00024 / +.00528 / +.00552 | +.00611 / +.01552 / +.01054 | -.00810 / +.00086 / -.00585 |
| JGP distributed - nonadj, 160K | +.00186 | +.01130 | +.00055 |

Prior-adjusted Macaroni CS has more both-wrong items at every seed (+0.40/+2.98/+4.77 pp) and oracle-any-correct falls by the same amounts. Native Chinese accuracy falls under that readout. Token-normalized changes tell a different story; hence this cannot identify shared harmful knowledge or a stable competence-versus-redundancy mechanism. The contrast is also binary-choice, not general shared-error identity. JGP positive covariance alone does not rescue the inconsistent independent-family result.

Decision: **demote this joint-error branch** under the predeclared readout/seed stability gate. Do not develop a consistency metric or paper narrative from it. The result closes a cheap field-scale possibility instead of adding another local tuning loop.

## Next Research-Scale Gate

The retained question is narrower and functional: does bilingual coupling help use externally supplied semantics across languages, rather than merely make equivalent text/predictions align? Novelty is NOT established; CLiKA owns artificial knowledge conductivity and MONOWEB owns QA interface decomposition. The needed next evidence is an independent task with a semantic counterfactual that changes the correct answer while preserving topical vocabulary, plus an English/native positive control showing the task is measurable. A new template score at chance, donor permutations on XStoryCloze, or a high representation-overlap score is insufficient. Only a robust useful-performance effect beyond these owned explanations can justify opening a matched-content acquisition/coupling factorial.

Inventory: 46 completed frozen/QA runs, 179,376 item-cell rows including repeated semantic items, corrupted-context controls and invalid-format diagnostics. Not 179,376 independent questions. All six new inference handles and both analyses/inventory are terminal. Python compilation and tracked whitespace check pass. Goal remains active; no candidate registration, no training.
