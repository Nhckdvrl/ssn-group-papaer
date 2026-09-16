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
