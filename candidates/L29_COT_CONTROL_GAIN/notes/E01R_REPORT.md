# E01R final instrument audit report — 2026-09-13

## Decision

**KILL L29. No further reconstruction.** Both predeclared balanced-binary families
failed the frozen step-100 instrument gate. No E01R outcome was generated for step
1400, step 2800, or any of the 240 untouched confirmation questions.

## What was tested

Step 100 first generated unconstrained reasoning. All 48 previously unseen instrument-
development questions reached a natural sentence/newline boundary between tokens 32
and 56 (median 38), with no Answer marker by token 128. The same natural prefix was
then forked into two valid opposite instructions.

Each arm contained the complete codebook. Case arms selected lowercase versus
uppercase for the next reasoning sentence; tag arms selected `[amber]` versus
`[violet]` at the beginning of that sentence. Within each template and mapping, the
two arms were exactly token-length matched and differed only in the selected Rule 1/2
label. Two templates and swapped/identity label mappings contributed 12 questions per
cell. There was no earlier constraint and no neutral arm.

Four paired continuations per semantic action yielded 768 complete raw records. The
question, not the rollout or token, was the inference unit.

## Frozen-gate results

| family | directional gain | question-bootstrap 95% CI | gate |
|---|---:|---:|---|
| case | 0.00 pp | [0.00, 0.00] pp | FAIL |
| tag | +1.30 pp | [+0.26, +2.60] pp | FAIL |

The required gain was at least 15 pp, with both semantic directions, both templates,
and both mappings each at least +5 pp.

Case produced no strictly lowercase or strictly uppercase completed sentence in any of
384 continuations. The lowercase-character fraction was 96.36% when lowercase was
selected and 95.13% when uppercase was selected, a diagnostic shift of only +1.23 pp.
Both semantic components, templates, and mappings therefore had zero strict gain.
Sentence completion was 98.70%.

Tag behavior was also too weak and asymmetric. Across 192 amber-selected continuations,
six were valid amber successes; across 192 violet-selected continuations, no valid
violet success occurred. One amber success also appeared when violet was selected.
The symmetric gain was therefore +1.30 pp, entirely driven by the amber direction.
Template gains were +2.08 and +0.52 pp; mapping gains were +1.56 and +1.04 pp, all far
below the frozen threshold. Meaningful continuation rate was 99.22%.

Answer/EOS rates were low and balanced: 0.52% versus 2.08% for the two case actions,
and 3.65% versus 2.08% for the tag actions. Instrument failure was therefore not caused
by truncated, empty, or prematurely finalized outputs.

Raw inspection confirmed that mappings and checkers behaved as specified. For example,
under a swapped case codebook, selecting lowercase correctly executed Rule 2, yet the
model continued with ordinary mixed-case text beginning “Okay”. Tag successes began
with the expected literal bracketed tag; almost all continuations instead began normal
task reasoning. The observed null/near-null is not a label-decoding implementation bug.

## Scientific interpretation

E01R answered only the instrument-development question. Even at the earliest released
RL checkpoint, a fresh, local, lexically balanced control pulse did not produce material
instantaneous control over the next reasoning sentence. Consequently there is no valid
positive early gain whose change across training can identify local-controller weakening.

This does not prove that opportunity accumulation explains the published global
controllability collapse, nor does it prove that the model has no elicitable control
under few-shot examples, repeated rules, system prompts, or further prompt search.
Redwood Research's 2026-09-11 results keep those stronger elicitation possibilities
alive. Pursuing them here would turn the project into an evaluator/prompt-optimization
study and violate the one-final-reconstruction gate.

The audit did rule out the remaining simple identification rescue for L29. Failure was
not attributable to old-rule retrieval, asymmetric target-word priming, Rule 1/2 bias,
one prompt template, absence of natural fork states, or EOS/Answer competition. Both
independent control families failed, with the tag effect only about one percentage point.

Under the locked decision rule, **L29 is killed as a paper candidate**. The technically
working common-support and natural-state infrastructure remains reusable elsewhere,
but it supplies no positive scientific result for this candidate. Hidden-state probing,
activation steering, mechanism localization, larger checkpoint sweeps, and further
instrument wording search are not authorized.

## Artifact chain

- Frozen design: `notes/E01R_DESIGN.md`
- Config and gate: `configs/e01r.json`
- Frozen question split: `configs/e01r_questions.json`
- Pre-outcome hashes: `configs/e01r_freeze_hashes.json`
- Natural prefixes: `results/raw/e01r_dev_step_0100_natural.json`
- Raw interventions and continuations: `results/raw/e01r_dev_step_0100_rollout.json`
- Gate summary: `results/e01r_dev_gate_summary.json`
- Intervention/checker code: `src/e01r_instruments.py`
- Runner and analysis: `src/run_e01r.py`, `src/summarize_e01r_dev.py`
