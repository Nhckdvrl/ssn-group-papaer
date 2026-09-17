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

The detailed file contains the ACL/EMNLP scope calibration, competing hypotheses, controlled/natural data strategy, initial pilot, causal follow-up, feasibility, and kill conditions.

---

## Explicitly cancelled registrations

- **S01 — Omission ≠ Neutrality / effective default semantics in tool calls:** cancelled/demoted. It is already recorded as F06 in `FAILED_TOPICS.md`; the Main-level parent compresses to underspecified tool intent / argument completion, leaving only an exact API-default subcase.
- **S02 / C2 — AI Rewrite ≠ Semantic Change:** registration cancelled. The high-level framing looked scientific, but the actual experimental object collapses into synthetic rewrite-data construction + semantic-preservation validation + comparison of LSC methods/metrics/robustness. Real post-LLM corpora lack clean semantic-change ground truth; synthetic paired rewrites provide ground truth only by making the central data artificial. This is precisely the evaluation/benchmark/metric-validity direction the search should avoid.

Do **not** revive either topic by adding more models, more datasets, more metrics, or broader rhetoric.

---

**Current selected topic count = 2.**
