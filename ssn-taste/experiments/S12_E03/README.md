# S12 E03 — frozen scope-identification experiment

## Purpose

Can the same quoted biconditional be restricted to World A, or does its bare universal form act as a global rule despite a World A report container? E03 is a validity and identification test, not a prompt search or a new benchmark. E01/E02 are immutable discovery and diagnosis records. Their raw outputs, exact scores, and logs were checked against committed item IDs before E03, and `origin/main` was current.

## Frozen design

- Model and parser: cached `Qwen/Qwen2.5-14B-Instruct` at the same revision as E01/E02, bfloat16, chat template, greedy generation, maximum four new tokens; inherited exact parser accepts only `A`, `B`, `A = Yes`, or `B = No` (optional final period). Any other output is invalid and counted wrong. No LLM judge or item exclusion.
- Resource fallback: if GPUs are occupied, `--gpu-cap-gib 2 --batch-size 16` limits placement on each visible GPU and leaves activation space; remaining weights are offloaded while using the same bfloat16 model. Record this runtime setting in every raw row and use it identically for controls and main. This does not change prompts, labels, decoding, or weights. Excluded resource trials are archived separately: an initial OOM before any output; four interrupted CPU controls; a cap-6 run (216 controls and 24 main answers before OOM); four cap-4/batch-4 controls; and 96 cap-4/batch-16 controls before another shared-GPU OOM. All final control and main prompts must be rerun from the beginning with cap-2/batch-16. If shared resources prevent that, leave E03 incomplete rather than pool runtime variants.
- New main seed `3092603`: 60 bases × 3 discourse containers × 2 E02 scope-clean readouts = **360** independent chats. New controls seed `3092699`: 24 separate bases × 3 roles × 3 applicable controls = **216** independent chats. The 20 nonce nouns, six colors, four shapes, and 12 object names are disjoint from E01/E02 vocabularies; every E03 color–shape combination is new.
- Common introduction: World A and World B are separate places speaking the same language. In each base, the **quoted relation sentence is byte-identical** across all three containers: `"An object is a {word} if and only if it has color {color} and shape {shape}."` World A has two positive and two negative objects, identical in all containers.
- `definition`: `The glossary for this language contains the following line:`
- `fact_natural`: `The survey report describing World A contains the following line:`
- `fact_explicit`: the exact `fact_natural` container followed by `This report describes World A only and makes no claim about any other world.` The same quoted relation follows. This is **only a scope diagnostic**.
- Positive readout: the E02-clean World B matching new object and `Does it follow that ...?` / `Is it undetermined whether ...?`; no `Nothing states whether` clause.
- Exception readout: the E02-clean World B off-property noun and the question whether that observation is impossible / whether the two descriptions can both be true given the earlier sentence's stated scope.
- Polarity is balanced 30/30 in each role × readout cell. Definition expected answers assert cross-world membership/conflict; both fact conditions expect non-entailment/coexistence. Ground truth is determined by the generator, not model output.

## Validity controls and interpretation gate

`a_world_a`: known positive/negative membership in World A (24 per role). `b_world_change`: the same object can have different colors in separate worlds (24 per role). `c_definition`: unseen World A membership from the glossary (24 definition). `d_world_local`: an explicitly World-A-only survey report does not establish a World B noun (24 for each fact role). Every applicable control cell must score at least 20/24; invalid responses must be at most 2% in main and controls; definition must score at least 51/60 on each main readout. If any fail, report the outputs and treat the scope contrast as uninterpretable. These are interpretation gates, not post hoc exclusions.

## Primary table and frozen reading rules

Report exact correct counts and transfer-assertion counts for each of the six role × readout cells, each polarity, and matched definition-minus-fact assertion differences. **Do not average positive and exception readouts.** Treat a fact readout as localized at ≥48/60 correct and globalized at ≤12/60 correct. Intermediate values remain unresolved.

| Pattern | Predeclared interpretation |
|---|---|
| A: both fact containers localized on both readouts | E02 failure may be due to its old framing; S12 can continue only to one tiny natural-framing replication. |
| B: natural fact globalized, explicit fact localized on both readouts | World scope is usable when explicit, but natural discourse role is insufficient; stop the original natural-role claim. The global-reading observation is only a candidate pending novelty check. |
| C: explicit fact globalized on both readouts | Current construct cannot reliably manipulate a world-local relation; KILL the current S12 design rather than strengthening wording again. |
| D: either fact container differs by ≥18/60 correct between the two readouts | Analyze positive entailment and exception coexistence separately; record at least two explanations and do not force A/B/C by averaging. |

Patterns may be mixed or intermediate. Describe the exact cells before a verdict. E03 can reveal a new hypothesis, but its own items cannot independently confirm one invented after reading E03.

## Freeze and run

Commit `e03.py`, tests, this design, `main.jsonl`, and `controls.jsonl` **before any E03 model output**. Tests and human spot checks must verify pairing, quoted-relation identity, World A extension, World B colors, balanced polarity, labels, parser, and disjoint item vocabulary. Run controls first, then main. Any instrument bug requires a new committed version and rerun of affected outputs; never pool versions.
