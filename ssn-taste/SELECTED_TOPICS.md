# Selected Topics — Sasano-Taste Search

Started: 2026-09-16

Purpose: record only questions that survive real nearest-prior novelty checking, fit Sasano/Main scientific taste, and whose **actual experiment is itself scientific rather than mainly an evaluation exercise**.

## Admission rule

A topic can enter this file only when all of the following are true:

1. **Worth asking:** the question is understandable without elaborate framing and there is a natural reason a reviewer would want to know the answer.
2. **Real difference:** nearest prior work does not already answer the same parent question; the difference is not merely a new model, dataset, language, condition, or exact experimental cell. Normal overlap with neighboring literatures is expected; novelty does **not** require zero conceptual overlap.
3. **Correct scientific width:** the parent RQ, claim scope, and Related Work neighborhood are calibrated against real ACL / EMNLP / NAACL Main papers and Sasano-approved work. Do not over-narrow merely to manufacture a perfectly isolated novelty cell.
4. **Scientific experiment, not evaluation disguised as science:** after stripping away the Introduction rhetoric, the main experiment must study a phenomenon, learning/representation/behavioral law, causal relation, trade-off, or natural process. If the work reduces to constructing a dataset and comparing methods/metrics/robustness/leaderboards, do not select it.
5. **Data path is natural and realistic:** do not require large synthetic benchmark construction, hard-to-obtain ground truth, or an artificial dataset merely to make the question measurable. Small controlled stimuli are allowed as identification instruments.
6. **Exploratory rather than anomaly gambling:** several plausible outcomes should remain scientifically interpretable, but this alone is not sufficient for selection.
7. **Feasible:** there is a cheap initial experiment that directly reduces uncertainty without large pretraining or a massive annotation campaign.

Mechanistic depth, surprising results, large model sweeps, and complex methods are not admission requirements. For mechanistic-interpretability topics, prefer a Zhao/Cho-style chain from representation to computation/transformation to causal mechanism rather than head/probe hunting.

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

### S05 — When Does Reading Become Learning?

**Status:** SELECTED — PILOT-AUTHORIZED  
**Registered:** 2026-09-18  
**Detailed registration:** `S05_WHEN_DOES_READING_BECOME_LEARNING.md`

**Parent question.** Under ordinary response-only SFT, prompt/context information is available to the model but receives no direct token loss. What determines whether that information remains transient conditioning, is compressed into only the task-sufficient information needed to predict the response, or becomes persistent parameter memory?

**Scientific pressure.** EACL 2026 establishes that input-only, target-absent information can be unintentionally memorized and explicitly suggests downstream-task utility matters, but does not causally match exposure while changing only response relevance. S05 targets that missing quantity.

**Minimum identification.** Match prompt-side exposure within one SFT run while changing only whether the information is causally necessary for predicting the response; use a small dose ladder and direct-supervision positive control.

**Claim boundary.** Do not turn S05 into privacy extraction, prompt-loss tuning, or an overfitting study. If the relevance effect appears only under extreme repetition or changes qualitative direction across modest doses, kill.

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

### S08 — Is Metacognitive Control Shared?

**Status:** SELECTED — PILOT-AUTHORIZED  
**Registered:** 2026-09-18  
**Detailed registration:** `S08_SHARED_METACOGNITIVE_CONTROL.md`

**Parent question.** Is internal confidence a reusable metacognitive control variable shared across behaviours, or do answer/abstain and reasoning continue/terminate decisions rely on separable monitor/control states?

**Scientific pressure.** Confidence has been causally shown to control abstention, while reasoning work independently finds termination delay and manipulable thinking-budget/reflection states. The unresolved object is the functional architecture linking confidence to distinct metadecisions.

**Minimum identification.** Fork identical native reasoning prefixes into forced-answer and continue-reasoning branches to label confidence and native termination at the same state; then perform confidence→termination and termination→confidence cross-steering. Shared, hierarchical, and double-dissociated architectures make different predictions.

**Claim boundary.** Do not turn S08 into confidence calibration, another early-stop method, a “when to think” benchmark, or a stopping-vector catalog.

---

## Explicitly cancelled registrations

- **S03 — From Document End to Task Done: How Does Post-Training Acquire Goal-Relative Stopping?**: registration cancelled after actual pilot execution. The developmental interpretation was unstable across training budgets and model families; plausible causal stories changed with recipe, while follow-up tests failed to reveal a family-stable mechanism. The remaining robust state-vs-readout fact is too narrow / partly structural to support the original Main-sized parent. Do not revive via more SFT budgets, model families, or base→SFT→DPO/RL trajectory reconstruction.


- **S09 — Same Recall, Different Stability? Does Learning History Determine What Can Be Changed?**: registration cancelled after the final S03-informed recipe-dependence audit. The mother question is scientifically interesting, but the manipulated variable (“memory age / learning history”) is itself an optimizer-path construct: acquisition time, intervening gradients, spacing, recency, dose and parameter state are inseparable. A positive result would require a recipe matrix to distinguish a law from path dependence; a null in one recipe is weak. Do not revive via larger optimizer/model sweeps or a generic consolidation framing.




- **S01 — Omission ≠ Neutrality / effective default semantics in tool calls:** cancelled/demoted. It is already recorded as F06 in `FAILED_TOPICS.md`; the Main-level parent compresses to underspecified tool intent / argument completion, leaving only an exact API-default subcase.
- **S02 / C2 — AI Rewrite ≠ Semantic Change:** registration cancelled. The high-level framing looked scientific, but the actual experimental object collapses into synthetic rewrite-data construction + semantic-preservation validation + comparison of LSC methods/metrics/robustness. Real post-LLM corpora lack clean semantic-change ground truth; synthetic paired rewrites provide ground truth only by making the central data artificial. This is precisely the evaluation/benchmark/metric-validity direction the search should avoid.

Do **not** revive either topic by adding more models, more datasets, more metrics, or broader rhetoric.

---

**Current selected topic count = 5.**
