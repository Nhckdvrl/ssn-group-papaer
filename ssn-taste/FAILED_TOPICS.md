# Failed Topics — Sasano-Taste Search

Started: 2026-09-16

Purpose: keep a durable record of questions that were seriously considered but rejected, so later search rounds do not accidentally repackage and revive them.

## Logging rule

For every rejected topic, record:

1. **Question** — the scientific question in plain language.
2. **Why it initially looked promising** — the evidence or research pressure that made it worth checking.
3. **Nearest prior work** — the papers most directly overlapping the question.
4. **Failure reason** — especially whether the nearest-prior difference is too small, the question is already answered, the framing is benchmark-centric, the required data is impractical, or the experiment cannot cleanly answer the question.
5. **What would be required to revive it** — only concrete new evidence can reopen a topic.

Do **not** reject a topic merely because the answer is uncertain, the first hypothesis may be false, the method is simple, or the work is not mechanism-heavy.

---

## Current-round failures

### F01 — Is post-training uncertainty lost, or merely unreadable?

**Question.** After instruction/alignment/reasoning post-training makes an LLM overconfident, is uncertainty information actually erased from the model, or does it remain internally represented but fail to reach the model's explicit confidence/readout?

**Why it initially looked promising.** This has a very Sasano-compatible structure: a clear empirical paradox (post-trained models become overconfident) followed by source/readout separation. It is easy to explain, requires no difficult dataset construction, and could in principle be tested with base-vs-post-trained checkpoints, probes, and controlled interventions.

**Nearest prior work.**
- Miao & Ungar (2026), *Closing the Confidence-Faithfulness Gap in Large Language Models* (arXiv:2603.25052): explicitly shows that internal accuracy/calibration and verbalized confidence are separable/roughly orthogonal signals, describes the problem as a readout failure, and uses activation probing/steering.
- Tan et al. (ACL 2026), *BaseCal: Unsupervised Confidence Calibration via Base Model Signals*: shows base models can retain better calibration than their post-trained counterparts and learns a projection from post-trained hidden states back into the base-model representation space to recover calibrated confidence.
- Slobodkin et al. (EMNLP 2023), *The Curious Case of Hallucinatory (Un)answerability*: already shows that hidden states can encode answerability even when the model produces overconfident hallucinations.

**Failure reason.** The central distinction — uncertainty/correctness information remaining internally available while the surface confidence/readout is wrong — is already directly demonstrated. Re-running it on newer reasoning models or another alignment recipe would be exactly the kind of “old question + newer models” novelty that Sasano has warned against. The remaining space would need a substantially different causal question, not a new model family or benchmark.

**What would be required to revive it.** Only a genuinely different premise that makes existing explanations diverge, e.g. a specific post-training operation predicted to destroy the latent signal rather than merely alter readout, with evidence that existing work did not test that distinction. Otherwise do not revive.

### F02 — Are message/turn boundaries semantically neutral?

**Question.** If the lexical information and order are held fixed, does presenting the same content as one context block versus multiple native chat turns systematically change what an LLM infers or does? If so, are message/role boundaries themselves part of the learned computation rather than mere serialization metadata?

**Why it initially looked promising.** The question is unusually clean and Sato-like: chat models are ultimately fed token sequences, yet semantically equivalent histories can be segmented into different role/message structures. A matched-content intervention is cheap, easy to explain, and could isolate an overlooked source of behavior.

**Nearest prior work.**
- Liu et al. (ICML 2026), *On Effectiveness and Efficiency of Agentic Tool-calling and RL Training*: directly compares native multi-turn serialization against putting the full interaction history into one context and reports material tool-use differences, while also analyzing system prompts and retained thinking history.
- *ChatInject: Abusing Chat Templates for Prompt Injection in LLM Agents* (ICLR 2026): demonstrates that native role/template delimiters materially change how models interpret authority and instructions.
- Existing chat-template analyses already show that the exact serialization/control-token scheme can materially affect downstream behavior.

**Failure reason.** The broad scientific parent — message/role serialization is not behaviorally neutral — is already empirically established. A new reasoning task, model family, or a cleaner same-token-count control would be a refinement, not the clear nearest-prior difference Sasano expects.

**What would be required to revive it.** A qualitatively different quantity beyond generic performance/authority sensitivity, with a theory predicting a specific boundary-dependent computation not tested by existing multi-turn/chat-template work. Otherwise do not revive.

### F03 — API backward compatibility ≠ agent behavioral compatibility

**Question.** If an API/tool evolves only by adding an optional parameter while preserving all old calls, does an LLM agent nevertheless change its behavior on old tasks because the new schema itself changes the model input?

**Why it initially looked promising.** This is a clean changed-regime question. In ordinary software engineering, adding a defaulted optional parameter is normally treated as backward-compatible. An LLM caller is unusual because it re-reads the interface description at inference time; therefore a software-compatible change could still alter planning. The experiment would be cheap: hold backend, task, model, and old call semantics fixed, and change only the additive optional field.

**Nearest prior work.**
- Liu et al. (2026), *MCPEvol-Bench: Benchmarking LLM Agent Performance Across Dynamic Evolutions of MCP Servers* (arXiv:2607.14642): explicitly studies evolving MCP interfaces with 11 mutation operators. Its PARAM-level **Flexible Expansion** operator adds optional parameters, requires existing calls to remain backward-compatible, and updates implementations to handle the new parameters gracefully, including via defaults. The benchmark then measures agent task-solving performance across evolved server versions.
- Faghih et al. (EMNLP 2025 Main), *Tool Preferences in Agentic LLMs are Unreliable*: controlled edits to exposed tool descriptions substantially alter tool selection, establishing that tool-interface metadata itself can change agent behavior.
- 2026 schema/tool-drift work further treats interface evolution as an explicit robustness object.

**Failure reason.** The proposed core intervention — a backward-compatible extension of a tool interface with optional parameters — is already an explicit evolution operator in MCPEvol-Bench, and interface metadata sensitivity is independently established. Isolating just this operator more cleanly would improve causal attribution but would still be reviewer-compressible to a controlled subcase of an already occupied schema-evolution problem. That is too close to the “cleaner experiment on an existing parent” pattern Sasano rejected in prior topic discussions.

**What would be required to revive it.** A different scientific quantity that is not generic robustness to schema evolution — for example, an independently motivated semantic law about omitted arguments versus resolved runtime actions that yields predictions not captured by interface-drift performance. Merely adding defaults, changing model families, or using better controls is insufficient.

### F04 — Same timeout, different action semantics

**Question.** Does an LLM agent change its recovery decision after an ambiguous timeout according to whether the preceding action was idempotent/read-only versus externally effectful or non-idempotent, where blind retry can duplicate a real-world action?

**Why it initially looked promising.** The observation is simple and operationally important: the same missing response can imply radically different safe continuations depending on action semantics. It allows a matched intervention with no large dataset and seemed more scientific than generic error-recovery benchmarking because the target quantity is the semantics of the action, not error frequency.

**Nearest prior work.**
- Wang (2026), *Callability Is Not Operability: Controlled Interface Interventions for LLM Agents* (arXiv:2608.23628): directly studies operational uncertainty where an external effect may commit but its response is lost, making committed and uncommitted states observationally indistinguishable even though they require different continuation actions. It evaluates interface mechanisms including execution lifecycle/recovery, explicit external-effect semantics, and postcondition verification while holding task/backend/state/failure/agent/model fixed.
- Adjacent 2026 agent-safety/reliability work explicitly distinguishes action classes such as idempotent, reversible, compensable, and irreversible, and studies when agents should abstain or verify before acting/retrying.

**Failure reason.** The load-bearing scenario — lost response after a potentially committed external effect and the need for different safe recovery — is already the motivating example and controlled object of a 2026 study. Rephrasing it as “does the model understand idempotency?” would mainly move responsibility from the interface to the model while retaining the same operational parent. That is too close for a Sasano-style novelty bar.

**What would be required to revive it.** A distinct action-semantic computation whose predictions cannot be reduced to operability/recovery under ambiguous external effects, and that has an independently motivated reason to be studied inside the model rather than at the interface layer.

### F05 — Does standard SFT secretly weight examples by response length?

**Question.** Because standard SFT aggregates token-level cross-entropy, does a demonstration with a longer assistant response exert systematically more influence than a shorter demonstration even when the dataset treats them as one example each? In other words, is response length an implicit sample weight?

**Why it initially looked promising.** The question is simple, mechanistically grounded, cheap to test, and directly relevant to modern post-training. Common implementations explicitly distinguish token-level global averaging from per-sequence/per-sample averaging, so the proposed quantity is real rather than rhetorical. A clean test could hold example count and task difficulty fixed while changing only loss aggregation.

**Nearest prior work.**
- NVIDIA (2026), *Nemotron 3 Super: Open, Efficient Mixture-of-Experts Hybrid Mamba-Transformer Model for Agentic Reasoning*: reports that single-stage SFT produced marked degradation on long-input/short-output scenarios. It explicitly contrasts a global token-average objective with a per-conversation normalized objective, states that the latter prevents long outputs from dominating the loss, and uses a two-stage SFT procedure to restore the affected behavior.
- Current large-scale training frameworks such as OpenRLHF expose token-level versus per-sample aggregation as explicit loss modes, confirming that these objectives give different weighting to variable-length responses.
- Recent SFT-objective work such as DFT/CADFT already treats token- and sample-level gradient weighting as central optimization variables, further reducing room for a generic “hidden weighting” parent.

**Failure reason.** The core scientific observation is already explicit in a 2026 large-model training report: token-global SFT makes long outputs dominate and per-conversation normalization is used specifically to counter this effect. A cleaner controlled paper could characterize the phenomenon more systematically, but its headline would compress to an already identified effect plus stronger analysis. Under the Sasano novelty requirement, that is not enough.

**What would be required to revive it.** A distinct consequence of aggregation that is not reducible to long-output dominance and is predicted by an independent scientific quantity. Merely testing more models, more length distributions, or token-vs-sample normalization more cleanly does not reopen the parent.

### F06 — Omission ≠ Neutrality / effective default semantics in tool calls

**Question.** When an LLM agent omits an optional tool argument, does it understand that omission resolves to a concrete runtime default, and will it explicitly override that default when the user's goal requires a different value?

**Why it initially looked promising.** No direct owner was found for the exact `default-consequence reasoning` contrast. The manipulation is cheap and clean, and the distinction between a surface call and the effective executed call is real. It initially appeared to offer a simple Sasano-compatible question without a large benchmark or expensive training.

**Nearest Main-level neighborhood.**
- Zhang et al. (EMNLP 2025 Main), *AskToAct: Enhancing LLMs Tool Use via Self-Correcting Clarification*: makes incomplete/ambiguous user intent in tool calling a central problem, explicitly treating tool parameters as representations of user intent and training models to recover or clarify missing critical parameters.
- Wang et al. (EMNLP 2025 Main), *Learning to Ask: When LLM Agents Meet Unclear Instruction*: studies imperfect user instructions and finds agents often arbitrarily generate missing arguments, motivating clarification rather than unsafe completion.
- Broader Main-level tool-use work already owns argument instantiation, intent interpretation, tool-schema comprehension, and clarification under underspecification.
- BFCL/MultiCAT-style evaluation additionally treats omitted optional arguments and explicit schema-default values as execution-equivalent when appropriate, so defaults already appear as an evaluation subcase even though their consequences are not the main RQ.

**Failure reason — Main-scope / Related-Work width.** The exact experiment remains relatively novel, but novelty at the exact-cell level is not enough. At the abstraction level used by nearby EMNLP Main work, a reviewer can reasonably compress this idea to **a special case of underspecified tool intent / argument completion where the missing argument has a default value**. Broadening the paper to `effective action semantics` would be rhetorical unless additional independent phenomena establish that broader parent; keeping it honest leaves an API-default corner case one level narrower than the Main scientific neighborhood. Therefore S01 fails the required width audit even though the exact contrast is not directly owned.

**What would be required to revive it.** Independent evidence for a broader, coherent scientific object in which surface actions systematically diverge from executed action semantics across multiple non-arbitrary mechanisms (not merely optional defaults), with a common prediction that is not already owned by tool clarification/schema-comprehension work. Do not revive by adding more APIs, default types, or benchmark scale.




## S09 — Same Recall, Different Stability? Does Learning History Determine What Can Be Changed? — KILL (2026-09-19)

**Failure mode:** recipe/path dependence in the causal variable itself.

The idea asked whether present accessibility underdetermines future editability because memories of different acquisition ages may have different stability. After S03 exposed how easily training-dynamics stories flip with budget/family/recipe, S09 was re-audited. “Memory age/history” is not a clean variable: it bundles parameter state at acquisition, optimizer trajectory, intervening gradients, spacing, dose and last exposure. *Fresh in Memory* also shows its motivating training-order representation is optimizer/dose dependent. Mirrored schedules and a common refresh improve within-recipe control but cannot turn generic path dependence into a recipe-stable law. A positive result would immediately require broad recipe sweeps; a null in one recipe would be weak.

**Do not revive** by adding optimizers/models, calling one trajectory consolidation, or converting it into a Fresh-in-Memory mechanism follow-up.

**General lesson:** before selecting a training-dynamics topic, ask whether the proposed scientific quantity has a plausible answer invariant enough to survive reasonable recipe perturbations. If the “cause” is itself the optimization path, the project is high risk.


## S03 — From Document End to Task Done — KILL (2026-09-19)

**Failure mode:** recipe/family-dependent developmental biography.

S03 was actually piloted. The project asked how post-training transforms pretrained document-ending behavior into goal-relative assistant stopping. Initial controlled SFT results suggested a clean readout-vs-state acquisition story, but reasonable changes in training budget changed the interpretation, and the readout contribution differed qualitatively across OLMo/Qwen/Llama-family tests. Subsequent tests of plausible explanations did not recover a stable cross-family law.

The surviving observation—that internal-state adaptation can alter goal-relative stop/continue competition with the stop row frozen, while a stop-row-only intervention has structural limitations—is narrower than the registered parent and partly follows from parameterization constraints.

**Do not revive** by adding budgets, model families, post-training stages, or optimizer sweeps.

**General lesson:** if the explanatory variable “training stage” bundles data, optimizer, budget, serialization, synthetic-data generation and preference objectives, the result may be a training-history biography rather than a reusable scientific law.


## S08 — Is Metacognitive Control Shared? — KILL (2026-09-21)

**Failure mode:** insufficient scientific consequence / mechanistic-detail trap.

S08 asked whether confidence is a shared metacognitive control variable across answer/abstain and reasoning continue/terminate, or whether these decisions use separable control states. The experiment could in principle be clean, but the strongest plausible findings remain too easy to compress into an architectural detail: shared control versus different controllers.

Nearby reasoning work already distinguishes confidence deficits from termination delay and shows that models can continue reasoning after effective commitment. Therefore a double-dissociation result risks becoming “the previously separated behaviors also have separable internal controls,” which is technically interesting but does not sufficiently change our understanding of reasoning or model cognition.

Broadening to a universal metacognitive-controller question would require many metadecisions, datasets, causal handles and cross-interventions, creating experiment explosion.

**Do not revive** by adding more behaviors, more models, better steering vectors, SAE/head/neuron searches, or an efficiency/early-exit framing.

**General lesson:** a mechanistic question of the form “do A and B share a mechanism?” must have a clear downstream scientific consequence. If shared and separate worlds mainly imply different internal architectures, without changing a larger theory of learning/reasoning/understanding, the question is too weak.


## S05 — When Does Reading Become Learning? — KILL (2026-09-21)

**Failure mode:** broad mother question, narrow consequence-bearing experiment / exact-cell novelty.

S05 asked what determines whether prompt-side information read during ordinary response-only SFT becomes persistent parameter memory. The broad conceptual distinction among transient conditioning, task-relevant use, and durable learning is real. However, the clean executable intervention only isolates one determinant: matched prompt information that is versus is not necessary for predicting the supervised response.

Under the importance-first audit, the strongest likely headline compresses to: **response-relevant prompt fields leave stronger persistent traces than equally exposed irrelevant fields.** This is causally clean, but a reviewer can naturally explain it from target-relevant gradient pressure. The opposite broad phenomenon—target-absent/input-only information becoming memorized—is already directly established in recent fine-tuning work, while memorization emergence across instruction tuning is also an active prior object.

Thus the project risks using a broad title to sell an exact matched-relevance cell. The experimental cleanliness is not enough to create the required scientific consequence.

**Do not revive** by increasing training dose, adding optimizers/model families, converting to privacy extraction, or adding mechanism after the fact.

**General lesson:** a beautiful intervention is not sufficient. The honest strongest finding produced by that intervention must itself be important, not merely a clean answer to one narrow determinant inside a much broader question.
