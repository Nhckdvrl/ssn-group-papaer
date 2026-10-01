# Fourth Wave: Independent Small-Model Intervention Family

Status: exploratory, P3 substrate test; not a replication claim or candidate. Previous goal turn made progress by completing four QA runs and demoting the proposed dissociation. P4 remains closed.

## Before Scoring

Use official Macaroni final checkpoints for `noswitch`, `switch`, and `par`, each at the three publicly released seeds 42/43/44. The paper reports eight seeds; the public weights do not cover all eight. No controlled paired intermediate trajectory is publicly available. Do not train missing states.

Primary repository and model card confirm common GPT-2 architecture, 16,384-token byte-BPE vocabulary, 1,024-token context, and nominal 100M byte-premium-adjusted-word budget. All three selected conditions use shuffled ordering and one 10-epoch run, not the three-stage curriculum. Verify actual tokenizer hashes before interpreting differences. Source: https://github.com/drooryck/multilingual-macaroni and https://huggingface.co/drooryck/multilingual-macaroni-models.

The intervention is not pure explicit pairing: `par` appends translations to one third of source documents, then discards documents to maintain the word budget. `switch` replaces parts of the same monolingual sources with translations. Thus unique semantic coverage, token counts and language exposure can differ even at the same adjusted-word budget. Do not infer that an effect is caused by correspondence alone.

Fixed assay: all 1,511 XStoryCloze evaluation examples, English/Chinese context x English/Chinese endings, zero demonstrations, two original endings, no prompt search. Use the previously pinned dataset and scoring boundary checks. Report raw, length-normalized and choice-prior-adjusted results together; do not select a winning calibration. Keep FP32 checkpoint weights and FP32 compute for this small family. Confirm zero context overflow rather than silently truncate. Same semantic item and actual prompt hashes across all nine models.

Primary comparisons: par-minus-noswitch and switch-minus-noswitch, and cross-minus-monolingual treatment interaction. Average per-item changes across the three matched seed labels; inspect every seed separately. Matching seed numbers is only a label match until common initialization is verified. Item bootstrap does not establish variability across training seeds; three seeds are insufficient for a precise population claim. No inference that a small-model failure on a readout means lack of all reasoning.

## Why This Is Not Yet An Idea

Macaroni already owns coherence controls, curriculum alignment persistence and grammatical/downstream evaluation. This assay seeks independent evidence about frozen cross-language continuation, not novelty from applying an existing benchmark. A scientifically useful next step requires a consistent functional effect that can be distinguished from priors, lexical cues, native-language competence and changed data coverage. The prior waves did not establish an interaction to replicate; this is exploratory triangulation, not a confirmatory P3 success.

## Outcomes

All nine frozen runs completed. Each contains 6,044 rows (1,511 stories x four language cells), for 54,396 new item-cell rows. Standard HF cache, existing conda environment, fvcrc20 GPUs 0/1/3; GPU 2 was occupied and untouched. No training.

Artifact audit verifies nine distinct actual weight hashes, all stored tensors FP32, identical architecture fields and one shared tokenizer hash `764e12dd3f5f2d753998848d8cd5876f935a8e9621530644eda80c9efc922a87`. All 18,132 original English/Chinese sentence fields encode/decode losslessly. Maximum full prompt+ending length is 108 tokens, safely below 1,024. Actual item hashes match across all nine runs; complete unique keys and finite likelihoods checked.

### Functional Results

Three-seed mean accuracy (%); raw and prior-adjusted both retained. These are low absolute scores, not established strong commonsense competence.

| Readout | Context -> ending | Monolingual | Code-switch | Document-parallel |
| --- | --- | --- | --- | --- |
| Raw | en -> en | 50.89 | 51.00 | 51.29 |
| Raw | en -> zh | 46.44 | 47.74 | 47.14 |
| Raw | zh -> en | 48.07 | 50.14 | 49.04 |
| Raw | zh -> zh | 47.61 | 48.05 | 48.03 |
| Prior-adjusted | en -> en | 54.71 | 54.34 | 54.09 |
| Prior-adjusted | en -> zh | 52.15 | 52.53 | 52.28 |
| Prior-adjusted | zh -> en | 51.60 | 54.62 | 51.42 |
| Prior-adjusted | zh -> zh | 56.06 | 53.34 | 54.20 |

Code-switch minus monolingual cross-minus-mono interactions are +1.41 pp raw, +1.64 token-normalized, +1.47 character-normalized and +3.24 prior-adjusted. Each is positive in all three seed-label comparisons. Fixed-seed item-bootstrap intervals exclude zero, but they do **not** establish training-population significance. The corresponding document-parallel interactions are +0.43, +0.51, +1.03 and +1.21 pp, with all item intervals spanning zero and inconsistent seed signs in some readouts.

There is a useful-performance component worth checking: zh->en code-switch changes +2.07 pp raw [0.75, 3.40] and +3.02 pp prior-adjusted [0.46, 5.54], with positive changes in every seed under both readouts. But the larger prior-adjusted interaction also contains a native zh->zh decline of -2.71 pp [-4.63, -0.77], negative in every seed. Token normalization instead gives a +2.25 pp native-Chinese increase. Thus a scalar claim of improved/degraded Chinese reasoning would be readout-dependent and unjustified.

Machine-readable estimates: `results/p3_macaroni_xstory.json`; release audit: `results/p3_macaroni_artifact_audit.json`. Bootstrap intervals are exploratory, conditional on the three released seeds, without multiplicity correction. They are not a confirmation of the initial acquisition-regime hypothesis.

### Scientific Decision

Retain **one** follow-up: test whether the positive zh->en code-switch effect depends on correct story context, using the already fixed context-control assay and retaining both absolute useful scores and control scores. This probes external semantic conditioning versus changed continuation priors. Because original useful performance rises in all three seeds, this signal warrants that bounded check; it is not selected solely from a positive difference-in-differences.

Do not promote a paper idea yet. The Macaroni paper already owns code-switch alignment, and the broader literature owns alignment-versus-functional-transfer dissociations. A valid mechanism requires correct-context dependence, independent task/family support, and a separation from changed native exposure and translated content coverage. Context shuffling also changes lexical/topic compatibility, so even a successful check is only an intermediate gate, not causal proof of reasoning.

Overall frozen/QA inventory is now 40 runs and 143,112 item-cell rows, including prior corrupted-context and invalid-format diagnostics. These are repeated semantic items, not that many independent questions. Independent text-loss measurements remain separately counted.

Native-FP32 scorer verification passed four padding/boundary cases against direct cross entropy, maximum batch/reference discrepancy 7.63e-6 nats. All inference, artifact-audit and analysis handles are terminal. Python compilation and whitespace checks passed. No unrelated worktree changes were reverted.
