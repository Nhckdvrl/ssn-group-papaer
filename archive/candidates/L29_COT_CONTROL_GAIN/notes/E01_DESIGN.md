# E01 design and no-claim audit — 2026-09-12

Authorization: E01A/E01B only. Repository starting point 91fa4bb.
Question: does the causal effect of an explicit constraint on continuation change
within one RL trajectory, beyond accumulated length/opportunity?
No hidden-state extraction, probes, activation interventions, training, or family sweep.

## Before outcomes

Three pinned checkpoints, step 100 / 1400 / 2800 of
allenai/Olmo-3.1-7B-RL-Zero-Math. Revisions and model file hashes in configs/models.json.
CoT-Control source commit and dataset hash are in that manifest. Use its existing
MMLU-Pro Math/Physics/Chemistry questions and first alphabetic suppression keyword.
Seed 290912 fixes the question order; first 12 questions are an audit split and
never enter a later confirmatory pilot. Remaining questions are untouched pilot units.
Existing /home/xiang/interesting/.venv-a100 is the first runtime candidate; no
mutation of another project's environment. Only idle GPUs on user-listed hosts;
at most 8 concurrent cards, initially 3 on fvcrc13.

## Identification refinement

Both legs use an initially constrained natural prompt and the SAME refresh contrast.
E01A cross-scores identical naturally generated legal histories at all checkpoints;
E01B evaluates a checkpoint's own histories. Thus the intervention definition is
identical across legs. This replaces E01A's differing initial prompt arms, solving
the confound that the arms can change the distribution of the entire prior history.
Pretreatment histories have one conditioning prompt; two suffix arms occur AFTER
that history and cannot change its causal support. Their own likelihood is a separate
intervention-naturalness diagnostic, not proof of on-policy suffix validity.

No chat template: follow the RL-Zero completion interface documented in CoT-Control,
Appendix E (https://arxiv.org/html/2603.05706v1#A5). Adapt 'math problem' to 'problem'
for the included physics/chemistry items. Do not condition generation on gold answers.

Audit three pre-existing instruments: lowercase, uppercase, exact-word suppression
(no synonyms). Preserve all outcomes, including unusable instruments. Surface checks
are instruments for policy response, not a new format benchmark. No opaque judge.

Fork at first newline/finished sentence boundary at or after token 32, up to token 96;
require a nonempty, still-compliant reasoning prefix, no answer marker, and alphabetic
reasoning content. Bound natural generation to 128 tokens in the initial audit.
All eligibility is decided before observing either refresh continuation. Keep every
rejection and survival denominator. This audit may fail because no useful states survive.

Primary intended behavioral measure: paired difference in probability of a violation
in the next 32 generated tokens (neutral risk minus active risk). Four paired seeded
rollouts per audit state; 8/32-token horizons retained to diagnose opportunity effects.
Casing next-token violating mass is a lower-noise diagnostic, not interchangeable with
32-token risk. EOS/answer before horizon is a competing event, NOT evidence of faithful
reasoning: report separately and inspect task continuation. Do not filter post-treatment
outcomes to make obedience look better. Injected reminders are not checker-scored as
model output. Word matches across token boundaries must be handled correctly; an
unfinished final word at truncation is not a completed forbidden word.

Support audit: natural prefix mean NLL AND maximum mean over 16-token windows,
relative to each checkpoint's natural prefix distribution. Freeze thresholds before
pilot effect analysis; likelihood typicality is necessary, not a guarantee of true
semantic reachability. Report retention by source checkpoint, family, question/domain,
length, and tail surprise. Tiny/narrow common support cannot license the headline.

Statistical units: questions; aggregate states, families and rollouts WITHIN question.
For shared histories, pair checkpoints on exactly the same question/history. Natural
state comparisons retain checkpoint-specific state distributions and survival selection;
restrict to common eligible questions as a diagnostic, not a cure for state selection.
Question-cluster bootstrap, no token pseudo-replication. A single training run cannot
estimate training-seed variance or isolate reward from all co-changing training factors.

Audit exit: freeze meaningful decline/equivalence margin and attainable MDE using
state counts and question-level variance, before a substantive pilot. An insignificant
trend is not a stable-gain result. Require an effective instrument at the early checkpoint;
floor/ceiling or near-zero effects make a null uninformative. No ~1pp effect chasing.
Budget ceiling for initial audit: 3 GPU-hours and 3 checkpoints, no automatic escalation.

Locked interpretation: both legs material decline -> return to selection, no mechanism
work; both equivalently stable with a valid instrument -> kill current L29 identity,
consistent with A but not proof that A explains all global collapse; A-only -> artifact
concern/reconstruct; B-only -> visited-state story requires new candidate; poor support,
invalid intervention or insufficient resolution -> stop and document identification blocker.

## Audit refinements before any model outcomes

The final neutral suffix pool mentions only continuing reasoning with information
already in the question; it does not mention producing the final answer. Exact
pair text is frozen in configs/suffixes.json. Token counts are checked by the actual
released tokenizer, including the shared Reminder delimiters. This improves length
matching but does not make lexical/syntactic differences vanish; a successful pilot
would still need a second fixed wording control within E01, not a mechanism probe.

Short-horizon violation is checked only before an explicit Answer: marker. Termination
and answer incidence are competing events and must be shown by arm; a decrease in
violation accompanied by more stopping cannot establish policy compliance. Preserve
raw full-fragment violation as a diagnostic. An EOS-terminated last word is complete;
a word cut by the fixed horizon remains undecided until a delimiter appears.

For the later pilot, an absolute 5 percentage-point change in 32-token causal gain is
the provisional smallest meaningful difference. Freeze a final margin no smaller than
this after variance/support feasibility audit, without selecting by trend sign. A ~1pp
shift is out of scope. Report neutral/active risks separately: gain floors, risk ceilings
and lack of opportunities can make an apparent null or shrinkage uninformative.

Before natural generation started, support calibration was improved to EXACT candidate
prefix token length. Store natural token NLLs once and truncate reference trajectories
at each candidate's length; calculate mean and max 16-token-window surprise from that
length-matched slice. Require natural reference length at least the candidate length,
report each reference denominator. The earlier first-32-token reference is retained only
as a diagnostic summary and no longer used for common-support admission.

Pre-outcome implementation audit: next-token mass is reported under the SAME decoder
as rollouts (temperature .6, top-p .95, no top-k), with raw T=1 mass separately labeled.
This prevents confusing raw-model probability with the actual continuation policy.
The three downloaded config.json files were compared and are identical.

Instrument correction made after the step-100 natural-eligibility audit and before ANY
refresh outcome: the suppression neutral refresh now mentions the identical target word
and states only that it appeared earlier in the instructions. This controls differential
lexical priming while preserving the prohibition as the active content. Exact token length
remains matched. The neutral statement may still cause meta-level continuation changes;
report meta-discussion and task continuation by arm. Casing and suppression stay separate.

The step-100 natural audit found zero eligible progressed prefixes for both casing
families: all 12 questions violated each casing constraint within 32 generated tokens.
These are invalid instruments for E01B because the early checkpoint is already at the
gain floor. Preserve the result, but do not use casing nulls/trends for the A-vs-{B,C}
decision. Exact-word suppression retained 8/12 legal trajectories at 32 tokens, 5/12
eligible boundary forks, and 3/12 fully legal at 128 tokens. Continue the audit with
suppression only; this choice is based on pretreatment eligibility, not intervention sign.
