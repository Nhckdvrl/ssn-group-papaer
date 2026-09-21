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

### S04 — How Do Language Models Update Situation Models Across Event Boundaries?

**Status:** SELECTED — PILOT-AUTHORIZED  
**Registered:** 2026-09-18  
**Detailed registration:** `S04_EVENT_BOUNDARY_SITUATION_MODEL_UPDATING.md`

**Parent question.** When a narrative shifts from one event to the next, how does an autoregressive language model update its internal representation of the current situation: by locally editing only what changed, by reconstructing a broader active situation state, or by selectively reactivating/rebinding relevant past information?

**Scientific width.** S04 is intentionally broader than the binary claim `global updating vs incremental updating`. Those are competing mechanistic explanations, not the entire novelty claim. The central object is **native situation-model updating in LMs across event transitions**.

**Nearest-prior ownership boundary.** Existing work owns neighboring objects such as event-boundary detection/behavior, externally engineered situation working memory, discourse circuits, and temporal feature extraction. S04 does not require zero overlap with these literatures. Its contribution must instead explain **what internal situation information is transformed at a boundary and how that transformation causally supports later narrative understanding**.

**Mechanistic path.** Representation → update computation/transformation → implementing pathway/component → causal intervention. Do not reduce the project to a boundary probe, SAE feature, or head-discovery paper.

---

### S06 — What Does Deliberation Do to Evidence?

**Status:** SELECTED — PILOT-AUTHORIZED  
**Registered:** 2026-09-18  
**Detailed registration:** `S06_DELIBERATION_EVIDENCE_REWEIGHTING.md`

**Parent question.** When a model is given a fixed set of external evidence and then deliberates, does reasoning merely compute with a stable evidential state, or does deliberation itself change which pieces of evidence can still causally influence the decision?

**Scientific pressure.** Nearby work separately finds prior-belief effects on CoT, resistance to incongruent updates, choice-supportive persistence, and even overweighting of opposing advice. These do not collapse to a single static “confirmation bias” account. S06 studies the missing dynamic quantity: the **time evolution of evidence influence under fixed external evidence**.

**Minimum identification.** Randomize the directions of several matched evidence items and track their causal effects at multiple pre-commitment reasoning depths. Stable effects support approximately stable integration; uniform shrinkage supports generic dilution; sign-selective divergence supports endogenous reweighting/coherence formation.

**Claim boundary.** Do not turn S06 into another confirmation-bias benchmark, CoT-faithfulness paper, attribution metric, or generic “longer reasoning is worse” result.

---

### S07 — Where Does Surprise Go?

**Status:** SELECTED — PILOT-AUTHORIZED  
**Registered:** 2026-09-18  
**Detailed registration:** `S07_WHERE_DOES_SURPRISE_GO.md`

**Parent question.** When an anomalous observation conflicts with what a model expected, which explanatory layer absorbs the prediction error: current-state belief, observation/source reliability, or transition/rule belief?

**Scientific pressure.** Recent work separately demonstrates strong latent-state inference, weak source discernment, and adaptation to regime changes. What remains unowned is the **revision-allocation problem** when one anomaly can be explained by more than one of those layers.

**Minimum identification.** Hold the anomalous report fixed, vary only the prior history, then use a trusted state reset followed by future same-source weighting and next-transition prediction to identify whether the anomaly changed state, source model, or dynamics.

**Claim boundary.** Do not turn S07 into a source-trust benchmark, changepoint benchmark, POMDP benchmark, or generic “LLMs are Bayesian” paper.

---

## Explicitly cancelled registrations

- **S05 — When Does Reading Become Learning?**: registration cancelled after the 2026-09-21 importance-first re-audit. The broad conditioning-vs-learning question is attractive, but the clean experiment mainly isolates an exact causal cell: whether response-relevant prompt fields leave stronger persistent traces than matched irrelevant fields. The most likely result is easy to explain from target-relevant gradient pressure; the surprising opposite direction (input-only write-through) and training-time memorization are already strongly occupied by nearby work. The honest knowledge delta is therefore too small relative to the broad mother question. Do not revive by adding dose/model sweeps, privacy framing, or post-hoc mechanism.



- **S08 — Is Metacognitive Control Shared?**: registration cancelled after a significance/Sasano-taste re-audit. Even a clean shared-vs-dissociated causal result compresses mainly to an internal architectural distinction: shared confidence readout versus policy-specific control. Nearby work already separates confidence deficits, termination delay, and post-commitment reasoning, weakening the surprise. Broadening to many metadecisions would cause experiment explosion. Do not revive via more behaviors, models, steering methods, or component hunting.


- **S03 — From Document End to Task Done: How Does Post-Training Acquire Goal-Relative Stopping?**: registration cancelled after actual pilot execution. The developmental interpretation was unstable across training budgets and model families; plausible causal stories changed with recipe, while follow-up tests failed to reveal a family-stable mechanism. The remaining robust state-vs-readout fact is too narrow / partly structural to support the original Main-sized parent. Do not revive via more SFT budgets, model families, or base→SFT→DPO/RL trajectory reconstruction. Final adjudication 2026-09-19 (`K195`, `failed/KILLED_LEDGER_CONTINUATION.md`): E04 gave one clean fact — decoupling the goal destroys goal-relative stopping while leaving generic boundary competence intact — but no resolution on which supervision carries the binding. Archived; do not reopen under a new name.


- **S09 — Same Recall, Different Stability? Does Learning History Determine What Can Be Changed?**: registration cancelled after the final S03-informed recipe-dependence audit. The mother question is scientifically interesting, but the manipulated variable (“memory age / learning history”) is itself an optimizer-path construct: acquisition time, intervening gradients, spacing, recency, dose and parameter state are inseparable. A positive result would require a recipe matrix to distinguish a law from path dependence; a null in one recipe is weak. Do not revive via larger optimizer/model sweeps or a generic consolidation framing.




- **S01 — Omission ≠ Neutrality / effective default semantics in tool calls:** cancelled/demoted. It is already recorded as F06 in `FAILED_TOPICS.md`; the Main-level parent compresses to underspecified tool intent / argument completion, leaving only an exact API-default subcase.
- **S02 / C2 — AI Rewrite ≠ Semantic Change:** registration cancelled. The high-level framing looked scientific, but the actual experimental object collapses into synthetic rewrite-data construction + semantic-preservation validation + comparison of LSC methods/metrics/robustness. Real post-LLM corpora lack clean semantic-change ground truth; synthetic paired rewrites provide ground truth only by making the central data artificial. This is precisely the evaluation/benchmark/metric-validity direction the search should avoid.

Do **not** revive either topic by adding more models, more datasets, more metrics, or broader rhetoric.

---

**Current selected topic count = 3.**
