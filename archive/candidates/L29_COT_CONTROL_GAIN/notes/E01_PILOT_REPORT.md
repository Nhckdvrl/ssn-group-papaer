# L29 E01 bounded pilot report — 2026-09-13

## Decision

**RECONSTRUCT.** The bounded pilot did not identify a usable local-control-gain
instrument. It therefore does not establish either a training-induced decline or
stability of local gain. No larger question sweep, hidden-state analysis, steering,
patching, or new training is warranted from these results.

## Causal design actually run

The same three public checkpoints from one `allenai/Olmo-3.1-7B-RL-Zero-Math`
trajectory were used: step 100, 1400, and 2800. Immutable revisions and shard hashes
are in `configs/models.json`; all downloaded shards matched those hashes. Every run
used bfloat16, temperature 0.6, top-p 0.95, no top-k, and recorded raw token IDs,
seeds, software versions, code hashes, and exact suffix text.

The retained constraint was exact-word suppression. Each question initially told the
model not to use one question-specific word in its reasoning. A fork was selected from
the checkpoint's pretreatment natural trajectory at the latest true sentence/newline
boundary before the first completed use of that word, provided the use was at most 32
tokens away. Selection never used intervention outcomes. The outcome was whether the
forbidden word appeared as a complete word in the next 32 reasoning tokens. Answer and
EOS incidence were reported separately.

E01A evaluated identical token histories under all checkpoints. Admission required
both prefix mean NLL and maximum local-window NLL to be no larger than a checkpoint's
length-matched natural-reference quantile. At the primary 0.95 threshold, 12 of 20
candidate states survived, spanning six questions and sources early/middle/late =
4/3/5. The stricter 0.90 sensitivity retained seven states, five questions, and all
three source stages. Each threshold used 11–12 natural references per checkpoint at
the exact candidate length. This is reasonable for an audit but remains a small
empirical support sample.

E01B used only each checkpoint's own naturally visited states. It retained 6/12,
7/12, and 7/12 questions at steps 100, 1400, and 2800. Thus neither leg failed because
there were no measurable risk-enriched states.

## What the control audit found

The first neutral suffix mentioned that the target word had appeared in prior
instructions. It produced an apparently positive early gain and a 6.25 percentage
point late-minus-early decline in both legs. This was not trustworthy: neutral-arm
meta-discussion rose with training, and raw continuations showed that the neutral text
often retrieved the original prohibition. Those exact raw results are preserved as
`results/raw/*_rollout_instruction_cue_control.json`; their summary is
`results/audit_effects_summary_instruction_cue_control.json`.

The corrected factual neutral mentioned the identical target word but said only that
it occurred in the problem statement/answer choices. It was exactly token-length
matched to the active prohibition. Under this cleaner contrast, the apparent decline
disappeared:

| leg | step 100 gain | step 1400 gain | step 2800 gain | late − early (95% cluster bootstrap CI) |
|---|---:|---:|---:|---:|
| E01A common support | -2.1 pp | +6.3 pp | +7.6 pp | +9.7 pp [-5.6, +29.2] |
| E01B natural states | +4.2 pp | +10.7 pp | +3.6 pp | +6.3 pp [-12.5, +25.0] |

Gain is neutral 32-token violation risk minus active violation risk, aggregated within
question before averaging. There were no Answer or EOS events in these continuations.
The common-support 0.90 sensitivity also moved upward rather than downward (+10 pp),
but with only five questions it is not independently decisive.

A third, equal-length structural arm omitted the target word. It showed that merely
placing the forbidden word in the suffix increased its subsequent use. For E01A at
step 100, question-weighted risks were 41.7% structural, 52.1% factual target cue, and
54.2% explicit prohibition. Thus the target cue changed risk by -10.4 pp in the
compliance-gain direction, while adding explicit prohibition semantics contributed
-2.1 pp. The same lexical effect remained at later checkpoints. Exact factorial
results are in `results/audit_factorial_control_summary.json`.

Finally, a target-free anaphoric pair compared “Keep following the forbidden-word
requirement stated earlier” with an equal-token “Keep reasoning with the relevant
information stated earlier.” The active reminder again did not supply positive early
control gain:

| leg | step 100 gain | step 1400 gain | step 2800 gain | late − early (95% cluster bootstrap CI) |
|---|---:|---:|---:|---:|
| E01A common support | -5.6 pp | -13.2 pp | -9.0 pp | -3.5 pp [-24.3, +13.9] |
| E01B natural states | -4.2 pp | -21.4 pp | -7.1 pp | +6.3 pp [-18.8, +37.5] |

Raw inspection showed ordinary task continuations repeatedly using the indispensable
problem term; a few active continuations explicitly discussed the prohibition. The
anaphoric result is consistent with a reminder that fails to redirect the local policy,
but the audit cannot distinguish a genuinely nonpositive controller response from
word-suppression-specific intervention conflict and finite-rollout noise.

## Scientific conclusion

This pilot cannot answer whether reasoning RL makes the current-state policy harder to
steer or merely lengthens the trajectory. The shared-history and natural-state legs
were both technically feasible, common support did not collapse, and stopping did not
confound the outcome. The load-bearing failure occurred earlier: exact-word suppression
did not have positive, robust early-checkpoint causal leverage under controls that did
not themselves retrieve or prime the rule. A training trend in this quantity is
therefore not an interpretable loss of steering gain.

The pilot does rule out the initially attractive 6.25 pp decline as evidence for L29:
that number depended on a neutral reminder that was not neutral. It also shows why
simply adding questions or stochastic rollouts would be scientifically wasteful. More
samples would resolve wording and lexical effects rather than the intended controller
change.

The next valid move, only after renewed design review, is to reconstruct E01 around a
constraint with rule-diagnostic local behavior, a neutral arm that neither retrieves
the rule nor injects the checked surface event, and a clearly positive early-checkpoint
effect on a held-out instrument-development split. That is a design change, not an
authorized mechanism phase. Current status remains **RECONSTRUCT; E01 gate not passed**.

## Artifact chain

- Model/data manifest: `configs/models.json`
- Frozen audit configuration: `configs/audit.json`
- Exact current and archived suffixes: `configs/suffixes.json` and
  `configs/suffixes_instruction_cue_control.json`
- Natural histories: `results/raw/step_*_natural.json`
- Cross-checkpoint scores: `results/raw/step_*_score.json`
- Support summary and rollout plan: `results/audit_support_summary.json` and
  `configs/audit_rollout_states.json`
- Factual target-cue rollouts: `results/raw/step_*_rollout.json`
- Structural rollouts: `results/raw/step_*_rollout_structural.json`
- Anaphoric rollouts: `results/raw/step_*_rollout_anaphoric.json`
- Question-level summaries: `results/audit_effects_summary.json`,
  `results/audit_factorial_control_summary.json`, and
  `results/audit_anaphoric_summary.json`
- Analysis code: `src/summarize_audit.py`, `src/summarize_factorial.py`, and
  `src/summarize_anaphoric.py`
