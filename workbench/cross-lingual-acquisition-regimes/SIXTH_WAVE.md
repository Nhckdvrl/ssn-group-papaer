# Sixth Wave: Counterfactual Location Binding

Status: exploratory assay validation, not an idea. No training.

Previous turn: progress (six context controls completed, joint-error branch demoted). This next test changes semantic bindings rather than swapping unrelated topics. bAbI single-supporting-fact retrieval already owns the underlying task; this is NOT a new benchmark or a reasoning novelty claim. Primary task generator: https://github.com/facebookarchive/bAbI-tasks.

## Fixed Before Scoring

Two people occupy two distinct locations. Each counterfactual twin exchanges the locations while keeping the names, location words and total character multiset unchanged. A fixed continuation asks for one person's location. Gold changes between twins; identical options and query remain. Thus an ending-only prior cannot solve both twins. Both sentence orders and queried people are enumerated. This still permits name-local lexical copying and does not establish general inference.

Four Latin-script name pairs, all 15 pairs of six common locations, two queried people, two fact orders, two twins: 480 contexts, each in EN/ZH context x EN/ZH query-and-answer language = 1,920 rows. Names remain identical across languages to avoid entity translation ambiguity, which also supplies shared anchors. One fixed declarative template per language, no prompt search or demonstrations. Chinese is hand-authored simple text, not independently native-reviewed. Literal space before continuations follows the verified likelihood boundary convention. Shared word membership is a character-level invariant, not a claim of identical tokenization.

Stage 1: Macaroni noswitch/switch/par seed 42 ONLY, all cells, native FP32 weights/compute. Retain raw/token-normalized/character-normalized/no-context-query-adjusted readouts. Report absolute accuracy, strict both-twins-correct, and signed-margin response to the fact swap. No-context queries must be identical across twins and necessarily have zero strict-pair success.

Measurability gate: English->English raw accuracy >=65% AND strict-pair success >=35% in at least one model. If the assay is not measurable, do not interpret multilingual nulls or optimize templates until one passes. If measurable, inspect binding versus no-context and fact-order effects before expanding to seeds 43/44 or another family. Near-floor cross-language results are not evidence that bilingual data never aids reasoning.

No candidate promotion from this toy task. A role-sensitive copying gain must be separated from general language acquisition and local token matching, and replicated in a natural task before motivating a paper-scale intervention. P4 stays closed.

## Outcome And Stop Decision

All three seed-42 runs completed, 5,760 rows, maximum full input 22 tokens. Identical actual item hashes, finite scores and 240 complete counterfactual pairs per language cell verified. No-context query scores are exactly equal across each twin pair, accuracy exactly 50%, strict-pair success zero as required.

| Model | EN->EN raw accuracy / strict pair (%) | ZH->ZH raw accuracy / strict pair (%) | ZH->EN raw accuracy / strict pair (%) |
| --- | --- | --- | --- |
| Monolingual | 55.42 / 13.33 | 55.21 / 11.25 | 50.63 / 2.08 |
| Code-switch | 53.54 / 17.08 | 51.88 / 3.75 | 50.63 / 5.83 |
| Document-parallel | 57.08 / 23.75 | 52.71 / 6.67 | 49.58 / 0.42 |

Every model FAILS the predeclared native measurability gate. Query-adjusted EN accuracy is 58.33/52.08/61.25%, with strict-pair 21.67/16.67/35.00%; this does not justify switching the gate post hoc. Code-switch raw EN accuracy also has a large fact-position effect (queried fact first 64.17%, last 42.92%). These are diagnostics of limited measurement quality and position sensitivity, not evidence of a multilingual acquisition mechanism.

Machine-readable all-readout results: `results/p3_location_binding_42.json`. Do NOT expand Macaroni location probing to more seeds, tune templates/demonstrations, or use the cross-language null as a paper result. This independent semantic gate has not validated the earlier XStoryCloze signal. The binding hypothesis remains unproven, not rescued by a positive margin on a toy task.

### Research-Scale Consequence

We now have a limitation shared across multiple small-model assays: frozen measurable native capability is insufficient for some semantic interventions even when language modeling is valid. Additional cheap small-model benchmark permutations will not establish a causal paper. The next substrate must supply both usable native performance and a controlled intervention, or published matched-content evidence must identify a genuine unresolved mechanism before new training. The existing MONOWEB natural QA substrate is measurable, but its earlier binding/interface diagnostics did not establish a stable gain. That branch cannot simply be renamed as the new idea.

49 completed frozen/QA/synthetic runs total, 185,136 item-cell rows, not independent questions. No training and no candidate. All three inference handles and analysis completed; inventory verification recorded separately. Previous parent-paper audits and hypothesis demotions remain in force.
