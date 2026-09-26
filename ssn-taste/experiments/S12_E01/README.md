# S12 E01 — frozen direct behavioral pilot

**Freeze point:** commit containing this file, `e01.py`, `test_e01.py`, `main.jsonl`, and `controls.jsonl`, before any E01 model output is inspected. The commit hash is the generator version. Any instrument or scoring bug requires a new version and fresh run of affected prompts; outputs from different versions must not be pooled.

## Question and estimand

Does the discourse role of an extensionally identical biconditional alter its persistence when the world changes while language stays fixed? E01 measures *behavior*, not an internal semantic module.

The primary estimand is, separately for positive transfer and exception judgments, the matched-base mean of `transfer_asserted(definition) - transfer_asserted(fact)`. For the positive readout, `transfer_asserted` means asserting that the new matching World B object must be a nonce noun. For the exception readout, it means asserting conflict for a World B object that is a nonce noun but lacks the defining property. Each assertion is computed from an exact A/B answer after accounting for question polarity. Report its three paired outcome counts (+1, 0, −1), the two role-specific assertion rates and accuracies, and each of the three framing-specific rates. Do not collapse the two readouts.

## Frozen materials

- Model: cached `Qwen/Qwen2.5-14B-Instruct`, bfloat16, chat template, greedy decoding, at most four new tokens. One prompt per independent chat. No examples or corrective feedback.
- Generator seed: `120925`; 120 main base worlds; three prespecified framing pairs, 40 bases per pair; 20 nonce nouns; six colors; four shapes.
- Each base has two positive and two negative named World A objects and one new World B query object. The relation sentence, World A inventory, World B event, nonce, property, and query are byte-identical across the definition/fact pair. The only paired change is one preceding discourse-role sentence.
- Main: 120 bases × 2 roles × 2 readouts = 480 prompts. Question polarity alternates within each framing to balance A/B keys in every role × readout × framing cell. Polarity wording is matched across roles.
- Controls: 24 held-apart bases (seed `121916`), 144 prompts. `a_world_a` tests known positive and negative inventory membership under both roles; `b_world_change` tests that reports of different colors in separate worlds can coexist under both roles; `c_definition` tests unseen World A application of an explicit definition; `d_world_local` tests non-transfer under an unambiguously World-A-only report.
- Output parser: strip surrounding whitespace, accept only the complete string `A` or `B`; anything else is invalid and counted wrong. No LLM judge, answer repair, hand exclusions, or prompt-specific exceptions.
- Ground truth is fixed by generator logic: in the definition role the property biconditional persists across worlds; in the fact role it is only an observed World A biconditional. A matching new B object entails noun membership only under definition; an off-property B noun conflicts only under definition. Question polarity merely inverts the A/B key.

The predeclared **validity gate** for interpreting a main null is each of the four control accuracies ≥ 0.85 and invalid answers ≤ 2% in both main and controls. If any fail, still report raw main behavior but do not infer absence of typed updating. This gate is an interpretation rule, not a post hoc exclusion of items.

## Pre-output checks and review

Run `python3 -m unittest discover -s ssn-taste/experiments/S12_E01 -p 'test_*.py'` and `python3 ssn-taste/experiments/S12_E01/e01.py check`. Tests assert pair equality outside the role sentence, same World A extension, correct B property contrast, balance of A/B labels in all primary cells, exact parser behavior, and unique IDs.

Manual spot check before model inference: inspect bases `000`, `001`, `041`, `080`, `119` in both roles and both readouts, plus controls for bases `000` and `001`. Verify the role sentence is the only paired difference, B property is correct, and expected answer inversion matches the question polarity.

## Analysis boundary

E01 is discovery data for unregistered patterns. A newly noticed asymmetry may motivate a revised question, but cannot independently validate it. Any new hypothesis gets a newly frozen held-out batch and seed. Nearest work checked at freeze: [Fonseca & Cohen 2024](https://arxiv.org/abs/2311.08704) studies following concept guidelines; [Lepori et al. 2026](https://aclanthology.org/2026.acl-long.676/) studies flexible use of in-context representations. Neither directly matches the current definition-versus-World-A-fact persistence contrast. This is a scoped literature check, not a novelty proof.
