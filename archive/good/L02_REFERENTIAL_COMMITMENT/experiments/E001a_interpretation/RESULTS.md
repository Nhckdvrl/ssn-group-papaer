# E001a — Interpretation likelihood diagnostic

Both models completed all 168 frozen jobs (336 records total). Each model saw
the same 42 naturally occurring omissions, balanced within 21 frame-role strata,
under sentence/full context and both A/B mappings. `analysis.json` verifies the
completion hashes and applies the frozen mean DNI-versus-INI log-odds rule.

| Model | Context | Correct / 42 | Both pair members correct / 21 | Label-order disagreements / 42 |
|---|---|---:|---:|---:|
| Qwen3-32B | Sentence | 20 | 1 | 16 |
| Qwen3-32B | Full story | 22 | 1 | 9 |
| Mistral-Small-24B-Instruct-2501 | Sentence | 23 | 4 | 42 |
| Mistral-Small-24B-Instruct-2501 | Full story | 22 | 1 | 42 |

A deterministic frame-role-only rule obtains 21/42 and 0/21 complete pairs **by
construction** on this selection. This is not a trained-model baseline result.
The selection does not control every lexical/syntactic cue: only two paired
strata have exactly identical surface predicates.

## Measurement problem

Mistral's highest-scoring output token was **A on all 168 jobs**. Thus the
prespecified order-averaged score uses small differences in a persistent A
preference. Report the numeric result, but do not treat it as a robust capability
measurement or evidence that full discourse cannot help. Qwen also exhibits
non-negligible order sensitivity. Neither model produced a non-A/B argmax token.

Full context changes Qwen from wrong to right on 3 items and right to wrong on 1;
Mistral changes 10 and 11 respectively under the averaging rule. Full-context
predictions favor DNI on 41/42 Qwen examples and 37/42 Mistral examples. These
are classification tendencies under a particular elicitation, not generated
specific-filler commitments.

The separately frozen **E001b** checks direct native-label generation on the same
items to investigate the A/B measurement failure. It is explicitly exploratory
and does not replace or retroactively modify this protocol/result.

## Execution and scope

BF16, Transformers SDPA, no truncation, Qwen thinking disabled. Full prompts were
11,191–11,333 Qwen tokens and 11,419–11,565 Mistral tokens. Frozen prompts, actual
chat-template renderings, pinned model revisions, software versions, raw log
probabilities, runtime and completion hashes are in the corresponding `runs/`
directories. Shared-filesystem weight loading dominated startup, not inference.

This is one training story and a gold-balanced challenge selection. No population
interval, genre generalization, hallucination rate, filler-support judgment,
architectural necessity, or equivalence claim is supported. DUST already owns
the broad distinction between detecting and interpreting underspecification;
see the follow-up literature alignment. H01/H02/H03 remain untested.
