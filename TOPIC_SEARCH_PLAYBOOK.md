# Topic Search Playbook — Generator Library

Updated: 2026-09-12.

This file answers only:

> **Where might a strong research question come from?**

It does not approve candidates. Selection belongs to [RESEARCH_TOPIC_SELECTION.md](RESEARCH_TOPIC_SELECTION.md).

The generators are intentionally **not equal priority**. Current project taste strongly favors model-computation and mechanism questions; data/evaluation/workflow generators are retained only as secondary possibilities so we do not lose useful intellectual tools.

---

# PRIMARY GENERATORS

## A. Stable anomaly → unresolved mechanism

This is the highest-priority generator.

Look for a phenomenon already established by a strong paper and preferably supported by another model/setup/replication:

- a restriction helps instead of hurts;
- stronger reasoning improves one behavior while degrading another;
- a capability survives but its normal readout disappears;
- a training stage changes behavior in a way the reported explanation does not predict;
- two model families with similar accuracy fail in structurally different ways;
- an ablation has a large asymmetric effect with no satisfying computational explanation.

Question shape:

> **Why does this stable phenomenon occur? Which computation or stage is load-bearing?**

Healthy development:

> established phenotype → competing accounts → discriminating intervention → localization/boundary → prediction or consequence

Failure modes:

- treating a single unexplained table cell as stable;
- reproducing the parent on more models and calling that mechanism;
- probe-only evidence;
- inventing the mechanism after seeing each result.

---

## B. Training-stage transition → what actually changed?

Look at pretraining, SFT, preference optimization, RL/RLVR, distillation, reasoning training, continued pretraining, model editing, or unlearning.

Strong hooks include:

- behavior appears/disappears sharply between stages;
- final output changes while latent capability may remain;
- post-training improves task accuracy but changes revision, uncertainty, exploration, or use of evidence;
- two checkpoints share competence but differ in how information controls action.

Question shape:

> **Did training create new information/computation, reweight an existing strategy, suppress a route, or change readout/policy control?**

Useful evidence:

- matched checkpoints;
- same-weight mode changes when scientifically meaningful;
- controlled retraining;
- trajectory/state comparisons tied to behavior;
- targeted interventions that distinguish creation from selection/suppression.

Failure mode: calling two unrelated model families a training intervention.

---

## C. Representation present → is it causally used?

Start from a meaningful behavior where evidence suggests the model “knows” more than it outputs.

Useful decompositions:

- absent vs represented;
- represented vs accessible;
- accessible vs selected;
- selected vs read out;
- policy knowledge vs action;
- local computation vs autoregressive accumulation;
- decision formed vs answer verbalized.

Question shape:

> **Where does the behavior first diverge, and which represented quantity actually controls the decision?**

Good operations:

- causal tracing / activation patching with active controls;
- steering tied to a specific account;
- teacher-forcing/free-running comparisons;
- controlled restoration/corruption;
- checkpoint trajectories;
- matched answer-preserving interventions.

Failure mode: “linear probe finds X, therefore X explains behavior.”

---

## D. Two strong papers disagree → hidden condition

Find apparently incompatible conclusions only after passing the SAME-QUANTITY check.

Question shape:

> **What structural condition makes both results true?**

Promising hidden conditions:

- base vs instruct/reasoning;
- pretraining vs post-training;
- local vs autoregressive computation;
- controlled vs free-running inference;
- strategy availability / exploration regime;
- task structure that changes which computation is required.

The third paper must do more than decide who wins. It should predict **when each regime occurs**.

Failure mode: manufacturing a contradiction from different golds, interfaces, or estimands.

---

## E. Old empirical law / challenge taxonomy → modern model regime

Search 2018–2023 work that explicitly claimed:

- “main bottleneck”;
- “major challenge”;
- “dominant error source”;
- “critical component”;
- a named curse/paradox/tradeoff;
- a multi-item challenge taxonomy that guided subsequent methods.

Then ask whether modern foundation-model training changes the **premise**, not merely the score.

Question shape:

> **Does the old law still govern the modern regime? If not, what replaced it and why?**

Best outcomes:

- old bottleneck remains but for a different mechanistic reason;
- bottleneck migrates to another stage;
- an old law becomes conditional on training/model regime;
- an apparent reversal is explained by a changed computation.

Failure mode: “LLM is better than BERT on an old benchmark.”

---

## F. Strong mechanistic claim → weak direct evidence

Look for claims repeatedly used to explain methods or model behavior:

> “X happens because Y.”

Trace the evidence.

Promising cases:

- the field cites one old correlational result;
- later methods are explicitly designed around Y;
- modern models let Y be directly manipulated while preserving the rest of the computation;
- different explanations make cleanly different predictions.

Question shape:

> **Is Y really the causal bottleneck/explanation, or merely correlated with it?**

Failure mode: literature fact-checking with no decisive intervention.

---

## G. Destructive capability control → what is invariant?

Use destructive interventions as a **scientific discriminator**, not as a metric paper by default.

Examples of useful shapes:

- selectively remove a representation/circuit/strategy while preserving surface quality;
- corrupt one stage of reasoning while keeping task content fixed;
- remove access to one information route and test whether another route compensates;
- constrain/restrict computation and ask why behavior improves or remains stable.

The interesting object is the model computation that survives or fails.

Failure mode: turning the study into “our evaluator failed to notice corruption.” Metric validation is currently low priority.

---

# SECONDARY GENERATORS — USE ONLY WHEN EXCEPTIONAL

The following generators are scientifically legitimate but are **not default search directions for the current project**.

## H. Measurement / construct-validity rewrite

Question shape:

> Does a widely used output/metric actually identify the consequential target quantity?

Use only if the scientific consequence is unusually large and the paper is not merely another benchmark/metric correction.

Current search normally deprioritizes this generator.

---

## I. Real workflow / natural process data

Real revisions, decisions, version histories, reviewer comments, user actions, etc. can expose strong questions.

Use only if the workflow reveals a **pre-existing scientific uncertainty about model behavior**, not because the workflow provides convenient labels.

Do not start from “there is a nice dataset.”

---

## J. Data-first reverse search

Retained for rare cases only.

A dataset may suggest a question, but the scientific object must become compelling independently of the dataset schema.

Current project has a strong negative prior because repeated use of this generator has produced technically clean but low-interest topics.

---

## K. Intermediate representation / structured state necessity

Ask whether an explicit state remains load-bearing in an end-to-end model.

This can still be good when it becomes a **model-computation question**. It is weak when it reduces to adding a schema field or repairing an extraction pipeline.

---

# CROSS-CUTTING DISCOVERY MOVES

## 1. Award/Main paper topic provenance

Read strong papers backward:

> What older pressure caused this paper to exist before the method existed?

Transfer the discovery move, not the subject.

Especially useful origins for the current project:

- stable anomaly;
- training-stage transition;
- causal claim with weak direct evidence;
- old empirical law under a new computational regime;
- two strong mechanistic accounts in conflict.

---

## 2. Large result, small explanation

Inspect full tables, ablations, appendices, and limitations.

Ask:

> The parent owns the phenomenon. Is a consequential explanatory space still open?

Then immediately search successor work. “Future work” is not a novelty certificate.

---

## 3. Methods as discriminators, never default generators

Potential operations:

- teacher forcing vs free running;
- causal tracing / activation patching;
- steering;
- controlled post-training;
- checkpoint trajectories;
- random rotation / projection controls;
- matched corruption/restoration;
- counterfactual inputs;
- representation similarity when tied to a hypothesis.

Correct order:

> phenomenon/question → live accounts → discriminating operation

Wrong order:

> operation → find something to apply it to

---

# ANTI-PATTERN LIBRARY

Do not repeatedly generate:

- another dataset/benchmark/metric paper because gold is easy;
- another RAG/retrieval/search question;
- another annotation/adjudication/workflow correction;
- another generic Agent/memory/RL/judge failure;
- another “X ≠ Y” distinction looking for a home;
- another “does the model know linguistic concept X?” competence test;
- another one-cell anomaly whose mother phenomenon is unverified;
- another representation-vs-readout story with only a probe;
- another mechanism story that changes every time a result is null;
- another model-family comparison sold as training causality;
- another old task rerun on a stronger model;
- another paper whose identity exists only if a narrow ranking reversal appears.

Use `failed/KILLED_LEDGER.md` for exact dead parents.

---

# PLAYBOOK USE

A normal open-ended round should spend most of its effort on **A–G**, especially A–F.

A generator creates only a lead. It does not waive:

- anti-resurrection;
- SAME-QUANTITY checks;
- novelty ownership;
- causal/construct identification;
- successful-result inference;
- feasibility/resolution;
- Main-level contribution.

Those gates live in `RESEARCH_TOPIC_SELECTION.md`.

> **The playbook should widen scientific imagination without dragging the search back toward whichever topic class happens to have the cleanest dataset.**
