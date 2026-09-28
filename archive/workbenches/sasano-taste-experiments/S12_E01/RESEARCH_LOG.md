# E01 research log — discovery data

## Observation

Qwen2.5-14B-Instruct, 120 matched bases, three fixed framing pairs. All 144 controls are correct, and all 480 main answers parse exactly. Positive transfer: definition 39/120, fact 1/120; paired transfer-assertion difference +38/120 (38 positive, 82 tied, 0 negative). Exception conflict: definition 120/120, fact 120/120; paired difference 0/120. Thus the model mostly refuses to infer a new World B noun from a definition, yet treats *every* off-property World B noun as conflicting even after a World-A field report. The exception pattern is identical across all three role framings. In the positive readout, the question-polarity split is material: definition 39/60 correct for “Does it follow?”, 0/60 correct for “Is it undetermined?”.

## Validity

Pair equality, extension, label logic, balance, and exact parsing were checked before model output. The first control-only run exposed answer-key echoing (`A = Yes` / `B = No.`); its outputs are archived separately and excluded. A strict grammar was frozen, then the whole control batch was rerun before the main batch. Final controls: World A 48/48, world change 48/48, definition following 24/24, explicitly local fact 24/24. There are no invalid final responses. However, two E01 wordings have serious construct risk: “Nothing states whether [object] is a [noun]” can pragmatically cue uncertainty despite the definition, and “conflict with the earlier information” can invite a textual rather than scope-sensitive consistency judgment. Controls do not rule out those readout artifacts. E01 cannot establish a general behavioral law yet.

## Interpretation candidates

1. **Directional rule use:** the relation is deployed as a prohibition on exceptions even when introduced as a local fact, but a definition only weakly licenses positive inference. This would make the original typed/untyped split too coarse.
2. **Readout wording:** the positive “Nothing states” clause and the exception's “earlier information” phrase separately drive opposite heuristic answers. The strong asymmetry may disappear when the questions specify the intended logical scope without adding new role facts.
3. **Bare-universal scope:** the identical, unqualified biconditional sounds globally quantified; the World A field-report frame may not sufficiently localize it for a contradiction judgment, despite explicit world-local control success.

## Knowledge consequence

If the directional pattern survives a clean held-out readout, definition versus fact status alone does not determine cross-world use; the direction and kind of query must be part of the scientific question. If it disappears, E01 mainly diagnoses an instrument ambiguity and the original S12 question remains open.

## Next decisive experiment

Freeze E02 on a new seed before inference. Cross the unchanged E01 wording with one scope-clean wording for each readout: omit “Nothing states whether” from positive transfer; ask whether both worlds' descriptions can be true under the stated scope for exceptions. Keep each core relation and role pair matched. The E01 and E02 item batches are separate; E01 is discovery data, never used as independent validation of this wording hypothesis.

## Current verdict

**continue original RQ** through the one targeted E02 readout diagnosis. Do not promote typed or directional claims from E01 alone.
