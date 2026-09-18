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

### S03 — From Document End to Task Done: How Does Post-Training Acquire Goal-Relative Stopping?

**Status:** SELECTED — PILOT-AUTHORIZED; CLAIM FROZEN BEFORE RUNS  
**Registered:** 2026-09-17  
**Detailed registration:** `S03_FROM_DOCUMENT_END_TO_TASK_DONE.md`

**Parent question.** A pretrained language model already has a learned action for “this text/document ends here.” When it becomes an assistant, how is information about **the user's goal being complete** connected to that stopping action: was the needed information already present and post-training mainly changes the readout, or must post-training change the model's internal state/computation before goal completion can control termination?

**Claim boundary.** Do not broaden S03 to generic instruction following, goal-satisfaction representation, response-length planning, or EOS-circuit discovery. The detailed file contains the frozen novelty audit, parameter-locus intervention, pilot, and kill conditions.

---

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

**Scientific pressure.** Conditional training specifies what should be predicted *from* the input, but does not explicitly specify what *about* the input should be durably written into the model. `Read`, `needed for the supervised prediction`, and `stored in parameters` are therefore three distinct learning claims.

**Nearest-prior ownership boundary.** Prompt-loss work studies whether prompt tokens should receive direct loss; context-distillation work deliberately internalizes context into weights; memorization/extraction work shows that some completion-only prompt content can leave traces. S05 is viable only while current prior does **not** already identify the matched-exposure causal law governing which conditioning-only information becomes persistent under ordinary response-only SFT.

**Minimum identification.** Match prompt-side information exposure while changing only its causal relevance to the supervised response; track task-sufficient knowledge versus full-detail parameter traces across training checkpoints.

**Claim boundary.** Do not turn S05 into prompt-loss hyperparameter tuning, privacy extraction, `more epochs -> more memorization`, or a context-parameterization method. The target is the **conditioning → persistent learning boundary**.

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

- **S01 — Omission ≠ Neutrality / effective default semantics in tool calls:** cancelled/demoted. It is already recorded as F06 in `FAILED_TOPICS.md`; the Main-level parent compresses to underspecified tool intent / argument completion, leaving only an exact API-default subcase.
- **S02 / C2 — AI Rewrite ≠ Semantic Change:** registration cancelled. The high-level framing looked scientific, but the actual experimental object collapses into synthetic rewrite-data construction + semantic-preservation validation + comparison of LSC methods/metrics/robustness. Real post-LLM corpora lack clean semantic-change ground truth; synthetic paired rewrites provide ground truth only by making the central data artificial. This is precisely the evaluation/benchmark/metric-validity direction the search should avoid.

Do **not** revive either topic by adding more models, more datasets, more metrics, or broader rhetoric.

---

**Current selected topic count = 5.**
