# Selected Topics — Sasano-Taste Search

Started: 2026-09-16

Purpose: record only questions that survive real nearest-prior novelty checking, fit Sasano/Main scientific taste, and whose **actual experiment is itself scientific rather than mainly an evaluation exercise**.

## Admission rule

A topic enters this file only when it has survived the **importance → knowledge delta → direct attack → execution** audit.

1. **Worth knowing:** an average reviewer can understand in ~30 seconds why the answer matters, and the major possible worlds would change a real understanding of learning/reasoning/generation/representation—not merely reveal a local architectural difference.
2. **Real scientific pressure:** the question grows from an actual contradiction, unexplained component, questionable premise, changed regime, or newly attackable old problem—not a literature blank or future-work cell.
3. **Main-level knowledge delta:** nearest prior does not already answer the same decisive unknown. Normal conceptual overlap is expected; new model/data/language/condition alone is insufficient.
4. **Direct attack exists now:** a small first experiment can distinguish the main scientific worlds. The pilot should primarily answer the science, not first invent/validate a probe, evaluator, latent construct, or benchmark.
5. **Execution stays subordinate:** data, training recipe, scale, and mechanism do not naturally explode. Prefer existing ground truth, small programmatic instruments, within-run/same-state interventions, and minimal robustness checks.
6. **Outcome significance, not story flexibility:** opposite/null outcomes count only when they alter a live belief, rule out a real explanation, or revise an important assumption. Merely being able to narrate every outcome is not enough.
7. **Mechanism is optional depth:** mechanistic work is welcome when it explains an independently important puzzle. A head/vector/circuit or “A and B use different internal states” is not sufficient significance by itself.

Selected topics are **not positive taste exemplars**. Selection only means the topic is currently worth spending real time on its first decisive experiment.

---

## Current selections

**None. Current selected topic count = 0.**

2026-09-26 pool-level reset: S04 / S06 / S07 / S10 were cancelled without execution because the selection process that admitted them was itself found unreliable after S11/S12 failed at construct/identification time. They are not retained as “maybe good later” candidates in this folder.

---

## Explicitly cancelled registrations

- **S04 — How Do Language Models Update Situation Models Across Event Boundaries?**: **KILL in 2026-09-26 pool-level postmortem.** The question is conceptually attractive, but the registered first attack depends on an intervention whose causal meaning is not validated independently of the transformer access pattern it modifies. The admission process treated a plausible mechanistic contrast as if it were already an identifiable natural phenomenon. Do not revive by adding probes, history-access masks, or more elaborate narratives.

- **S06 — What Does Deliberation Do to Evidence?**: **KILL in 2026-09-26 pool-level postmortem.** “Evidence influence over reasoning depth” was promoted before establishing a natural, stable observable independent of forced reasoning-prefix interventions. The registered estimand risks being defined by the measurement procedure itself. Do not revive by adding more fork points, attribution estimators, or evidence skins.

- **S07 — Where Does Surprise Go?**: **KILL in 2026-09-26 pool-level postmortem.** State/source/rule revision is a neat hierarchical decomposition, but the three loci were chosen as a theoretical taxonomy before a natural LM behavior forced that taxonomy. The trusted-reset diagnostic is an engineered identification system, not evidence that the model naturally exhibits a surprising revision-allocation phenomenon. Do not revive by elaborating POMDP worlds or diagnostic fingerprints.

- **S10 — Does the Language We Plan to Speak Change Event Construal?**: **KILL in 2026-09-26 pool-level postmortem.** This was admitted mainly because LLM/VLMs create a cleaner within-agent intervention for an old human debate. That is still old debate + new artificial subject unless a natural model behavior or conflict first creates independent pressure. The motion-triad task is a constructed psycholinguistic assay rather than a model-native phenomenon. Do not revive by adding languages, VLMs, motion clips, or hidden-state analysis.


- **S11 — Same Number, Different Information: Value vs Measurement Precision**: registration cancelled after E01–E03 execution (final E03 commit `9de6d60`). Pure mathematical value invariance and nuisance-notation invariance were strong, but the registered measurement-threshold instrument failed its own construct-validity requirement. Even when the compatible true-value interval was supplied explicitly, the model remained unstable for greater-than certification (16/40 correct coarse cases; 24/40 Yes/Yes pairs), while less-than interval judgments were 40/40. Thus the readout itself does not cleanly identify whether reported measurement precision is preserved as epistemic information. Do not rescue S11 by further prompt repair, CoT, model families, or mechanism work on this threshold route. Any revival requires a new independently motivated instrument, not another variant of interval-threshold certification.


- **S12 — Does In-Context Learning Distinguish Definitions from Facts?**: registration cancelled after E01–E03 execution (final E03 commit `7e04161`). The broader language-update-vs-world-update mother question remains scientifically unresolved, but the registered matched-persistence instrument failed its own direct-attack criterion. Natural World-A report framing made the bare biconditional behave like a global rule on both readouts; adding explicit World-A-only scope repaired positive transfer (60/60) but left exception/coexistence judgments sharply question-form dependent (26/30 correct for “impossible” versus 0/30 for “can both be true”). Controls were 216/216 and all final answers parsed exactly, so this is not a harness failure. Do not rescue S12 by progressively strengthening scope prompts, adding model families, or moving to mechanism analysis. A future revival requires a new independent scientific rationale and a newly frozen instrument that manipulates definition-vs-world status without relying on stronger explicit scope wording.


- **S05 — When Does Reading Become Learning?**: registration cancelled after the 2026-09-21 importance-first re-audit. The broad conditioning-vs-learning question is attractive, but the clean experiment mainly isolates an exact causal cell: whether response-relevant prompt fields leave stronger persistent traces than matched irrelevant fields. The most likely result is easy to explain from target-relevant gradient pressure; the surprising opposite direction (input-only write-through) and training-time memorization are already strongly occupied by nearby work. The honest knowledge delta is therefore too small relative to the broad mother question. Do not revive by adding dose/model sweeps, privacy framing, or post-hoc mechanism.



- **S08 — Is Metacognitive Control Shared?**: registration cancelled after a significance/Sasano-taste re-audit. Even a clean shared-vs-dissociated causal result compresses mainly to an internal architectural distinction: shared confidence readout versus policy-specific control. Nearby work already separates confidence deficits, termination delay, and post-commitment reasoning, weakening the surprise. Broadening to many metadecisions would cause experiment explosion. Do not revive via more behaviors, models, steering methods, or component hunting.


- **S03 — From Document End to Task Done: How Does Post-Training Acquire Goal-Relative Stopping?**: registration cancelled after actual pilot execution. The developmental interpretation was unstable across training budgets and model families; plausible causal stories changed with recipe, while follow-up tests failed to reveal a family-stable mechanism. The remaining robust state-vs-readout fact is too narrow / partly structural to support the original Main-sized parent. Do not revive via more SFT budgets, model families, or base→SFT→DPO/RL trajectory reconstruction. Final adjudication 2026-09-19 (`K195`, `failed/KILLED_LEDGER_CONTINUATION.md`): E04 gave one clean fact — decoupling the goal destroys goal-relative stopping while leaving generic boundary competence intact — but no resolution on which supervision carries the binding. Archived; do not reopen under a new name.


- **S09 — Same Recall, Different Stability? Does Learning History Determine What Can Be Changed?**: registration cancelled after the final S03-informed recipe-dependence audit. The mother question is scientifically interesting, but the manipulated variable (“memory age / learning history”) is itself an optimizer-path construct: acquisition time, intervening gradients, spacing, recency, dose and parameter state are inseparable. A positive result would require a recipe matrix to distinguish a law from path dependence; a null in one recipe is weak. Do not revive via larger optimizer/model sweeps or a generic consolidation framing.




- **S01 — Omission ≠ Neutrality / effective default semantics in tool calls:** cancelled/demoted. It is already recorded as F06 in `FAILED_TOPICS.md`; the Main-level parent compresses to underspecified tool intent / argument completion, leaving only an exact API-default subcase.
- **S02 / C2 — AI Rewrite ≠ Semantic Change:** registration cancelled. The high-level framing looked scientific, but the actual experimental object collapses into synthetic rewrite-data construction + semantic-preservation validation + comparison of LSC methods/metrics/robustness. Real post-LLM corpora lack clean semantic-change ground truth; synthetic paired rewrites provide ground truth only by making the central data artificial. This is precisely the evaluation/benchmark/metric-validity direction the search should avoid.

Do **not** revive either topic by adding more models, more datasets, more metrics, or broader rhetoric.

---

**Current selected topic count = 0.**
