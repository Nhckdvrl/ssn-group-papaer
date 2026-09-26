# E03 research log — scope identification

## Validity

The new main seed `3092603` supplied 60 matched bases, yielding **360** complete main prompts. A separate control seed `3092699` supplied **216** complete controls. New nonce terms, color–shape combinations, and object names are disjoint from E01/E02. The quoted biconditional, World A inventory, and World B event are byte-identical within each definition / fact-natural / fact-explicit triple. Three roles × two readouts each have 60 items and 30/30 question polarity. Tests and manual spot checks passed before inference. The final model revision is `cf98f3b3bbb457ad9e2bb7baf9a0125b6b88caa8`; every final output used bfloat16, greedy decoding, `gpu_cap_gib=2`, and batch size 16. The final controls were **216/216 correct**; all 576 final answers parsed exactly. Resource-failed and throughput-trial fragments are archived with `excluded` filenames and are not pooled.

## Main table

Counts are exact correct / 60; the two readouts are never averaged.

| Discourse container | Positive transfer | Exception / coexistence |
|---|---:|---:|
| Definition | 60/60 | 60/60 |
| Fact-natural | 1/60 | 0/60 |
| Fact-explicit | 60/60 | 26/60 |

For fact-explicit exception judgments, the polarity split is decisive: **26/30** correct when asked whether the World B observation is impossible, but **0/30** correct when asked whether the World A and B descriptions can both be true. Definition was 30/30 on both phrasings; fact-natural was 0/30 on both. Fact-explicit positive transfer was 30/30 on both phrasings. Representative matched triples and exact per-row answers are in `main_scored.jsonl`.

## Observation

The natural World A survey container did not localize the bare biconditional on either readout. Adding one explicit sentence that the report describes World A only made positive-transfer reasoning perfectly world-local, while exception/coexistence judgments remained unstable and changed sharply with question polarity. This is the predeclared **Pattern D**, with one part of Pattern B limited to the positive readout. The explicit-scope condition is diagnostic; it is not a viable natural-role main condition.

## Interpretation candidates

1. **Bare-rule scope dominance with explicit repair:** the universal-looking `iff` sentence wins over a weak survey container, but an explicit World-A-only statement can bound its positive use. On this view, natural definition-versus-fact role is too weak to identify the intended construct.
2. **Question-form heuristic:** the model treats “impossible” and “can both be true” differently even when they are logically complementary under the stated scope. The 26/30 versus 0/30 split in the same fact-explicit condition supports a readout-level contribution; it does not establish a representation-level directionality.
3. **Joint account:** scope wording determines positive transfer, while apparent exception conflict also depends on the question's linguistic form. E03 cannot partition those contributions further without a new hypothesis and independent validation.

No generator, pairing, label, or parser bug was found. The final E03 comparison is within one offloaded runtime; do not interpret E01/E02 versus E03 rate changes as pure prompt effects because placement differed under shared-GPU pressure.

## Knowledge consequence and novelty check

E03 shows that this model *can* use explicit world scope for positive entailment, so a simple blanket claim that it cannot distinguish language from world updates is unsupported. But natural report framing does not reliably create a world-local relation, and the exception readout does not give a stable answer even with explicit scope. Therefore the current S12 instrument cannot establish a robust typed contextual update.

Related primary work already studies [definition following](https://arxiv.org/abs/2311.08704), [flexible use of in-context representations](https://aclanthology.org/2026.acl-long.676/), [generic statements and exceptions](https://direct.mit.edu/coli/article/50/4/1211/123791/Exceptions-Instantiations-and-Overgeneralization), and [question-answering faithfulness under semantically relevant input changes](https://direct.mit.edu/coli/article/50/1/119/118135/Analyzing-Semantic-Faithfulness-of-Language-Models). This focused check did not find a paper with E03's exact triple, but generic overgeneralization or polarity sensitivity alone is not a defensible new mother question. E03 is discovery data for the polarity split and cannot independently validate a new hypothesis about it.

## Verdict

**KILL current S12 design.** Do not add stronger prompts, new model families, or mechanism work to rescue its natural-role claim. The broader language-versus-world question remains unadjudicated; a future reformulation would need a new scientific rationale and a newly frozen independent experiment.
