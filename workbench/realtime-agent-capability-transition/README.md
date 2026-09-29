# Realtime Agent Capability Transition — Workbench

## 当前进度（中文，2026-09-30）— 已关闭（DRAINING 完成）

**状态：** 本工作区的母假设“实时/语音交互普遍削弱 agent 能力”已被证据削弱，按用户决定停止扩展，研究转入 `../realtime-computation-boundaries/`。本页仅保留结论与资产。

**资产（可复用）：** τ-bench 排行榜 20 个系统的完整公开轨迹（本地 `/home/xiang/rt_ext/data`，约 20GB；脚本 `experiments/s3_fetch.py`、`fetch_all.sh`）；逐 sim 索引 `results/sim_index.json`；分析脚本 E01–E04。

**结论：**
1. **E01**：2026 年 9 月的前沿“双系统”语音 agent（gpt-live-1、Pine）在真实噪声下已与文本前沿持平（零售/航空/电信 79/82/84 vs GPT-5.2 82/83/90）。
2. **认证分解**：单体实时模型与弱级联的差距主要来自口语实体捕获（零售：级联 GPT-4.1 认证失败 42%、gpt-realtime-2 34%、gpt-live-1 3%），该对象已由 τ-Elicitation（2026-09）拥有。
3. **E02/E03**：“先说后做”不是主要失败源（0–8% 对话）；gpt-realtime-2 有 21% 的邮编参数是用户从未说过的，仍属实体捕获问题。
4. **E04（本地严格对照，已完成）**：同一 agent（Qwen3-32B）、同一用户模拟器（Qwen3-30B-A3B）、纯文本、无转写误差，只把用户说话方式换成 τ-Voice 电话口语风格：零售 47.8%→43.5%（配对 p=0.79），航空 40%→44%（p=0.77）。**口语化/信息碎片化本身不造成可测损失。** 注：本地用户模拟器不发结束标记会陷入道别循环，两组均按同一规则改判（`experiments/e04_rescore.py`，NL 断言裁判改用 Qwen3-30B-A3B）。

**一句话结论：** 在 τ-Voice 上，去掉“听不准实体”和“底座能力”之后，实时/口语交互契约本身几乎不造成能力损失；母假设不成立，不再扩展。

---

**Lane:** our-taste  
**Stage:** ACTIVE EXPLORATORY WORKBENCH — **not a candidate**  
**Target ceiling:** ICML / ICLR / NeurIPS / ACL / CVPR main-track scale.  
**Core discipline:** inhabit the realtime-agent regime, reproduce strong baselines, and let the actual bottleneck emerge. Do not turn a convenient failure slice into a paper story.

---

## 0. Territory

Modern agents are moving from a sequential interaction contract

> observe a complete user turn → reason → call tools → wait → answer

toward systems in which several processes can overlap:

> partial / streaming observation + ongoing generation + tool execution + background tasks + new user input + memory / environment events.

The scientific territory is the **capability transition from turn-based / offline agents to realtime / streaming / asynchronous agents**.

The workbench does **not** register a specific failure such as self-correction, rollback, interruption, stale state, proactive speaking, or user-stream routing. Those are possible diagnostic axes only.

The entry pressure is already objective and does not depend on our hoped-for phenomenon:

- **τ-Voice (ICML 2026)** shows a large gap between strong text agents and full-duplex voice agents on the same grounded task family; even under clean conditions voice agents lag substantially, and qualitative analysis attributes most failures to agent behavior rather than benchmark artifacts.
- **Full-Duplex-Bench v3 (2026)** evaluates tool-using voice agents with real human disfluency and reports self-correction handling and hard multi-step reasoning as recurring weaknesses across systems.
- **OmniInteract (2026)** finds that strong offline capability does not reliably transfer to native online streaming interaction over audiovisual streams.
- **STAR (2026)** shows a turn-based vs real-time strategy-execution gap: strong reasoning models can lose their advantage when action must be timely.
- **Real-Time Deadlines Reveal Temporal Awareness Failures (2026)** finds large differences between turn-count and wall-clock deadline settings even when strategic competence is otherwise present.
- Meanwhile **Stream RAG**, **NemotronLabs VoiceChat**, and **Qwen-Audio-Agent** move the architecture itself toward streaming tool calls, parallel function streams, foreground/background agents, and asynchronous task execution.

These works establish a regime transition and multiple pressures. They do **not** yet identify one universal mechanism, and this workbench must not assume one exists.

---

## 1. Top-conference ceiling contract

The authorized scope ladder is:

> **strong agent succeeds under a sequential / fully specified contract but changes under a realtime or asynchronous interaction contract**  
> → **identify which temporal / concurrency interface changes the effective capability and why**  
> → **a general principle, mechanism, or intervention for agents that must observe, reason, communicate, and act while the world continues to change**

The first substrate is voice because the current artifacts make physical time unavoidable and measurable. The scientific object must not remain “voice benchmark errors”.

This workbench keeps authorization only if exploration can plausibly reach beyond one provider, one speech model, or one benchmark.

### Demote / kill if

- the remaining story is only ASR quality, accent robustness, VAD tuning, TTS latency, or another speech-component issue;
- the strongest result is “model X loses Y points on τ-Voice/FDB-v3” with no broader agent implication;
- an apparent realtime effect disappears under a fair text/half-duplex or latency-matched control;
- the object collapses to a slice already owned by Evolving Intent, Cordon, Stream RAG, τ-Voice, FDB-v3, OmniInteract, or the proactive-speaking / user-stream-routing papers;
- progress requires building a new giant benchmark rather than understanding existing strong baselines;
- the workbench keeps narrowing conditions to rescue one hoped-for anomaly;
- only proprietary frontier systems expose the effect and no reproducible open foothold remains.

---

## 2. Nearest-prior ownership map

Overlap is expected. Do not claim what these works already own.

### τ-Voice — already owns

- a direct text-vs-full-duplex-voice comparison on grounded real-world tasks;
- the large voice/text task-completion gap in its evaluated systems;
- acoustic realism / accent / turn-taking ablations;
- interaction metrics such as response latency, responsiveness, yielding, interruption, and selectivity;
- qualitative failure attribution showing many failures are agent-behavior failures.

We cannot write a paper whose contribution is merely “voice agents are worse than text agents” or “realistic speech hurts agents”.

### Full-Duplex-Bench v3 — already owns

- real human disfluency + multi-step tool-use evaluation;
- six model configurations;
- recurring weakness on self-correction and difficult multi-step reasoning.

We cannot claim discovery that self-correction is hard for voice agents.

### Evolving Intent — already owns

- controlled user-intent reveal, revision, and task switching in multi-turn agents;
- the finding that strong static-task performance degrades as intent evolves.

We cannot repackage intent revision as a realtime phenomenon without new temporal / concurrency evidence.

### Stream RAG — already owns

- predicting and issuing retrieval/tool queries before the user finishes speaking;
- latency gains from overlapping tool preparation with ongoing speech.

We cannot claim speculative streaming tool use itself.

### Cordon — already owns

- semantic transactions for multi-step tool agents;
- commit / rollback / staged effects / recovery as a runtime containment abstraction.

We cannot claim transactionality or rollback as our general solution.

### Qwen-Audio-Agent — already owns as a system design

- foreground conversation + background delegated agents;
- asynchronous task execution;
- explicit separation of speech interruption from task cancellation;
- task completion from result delivery;
- task status, cancellation, modification, and persistent memory.

Its architecture is a strong artifact / pressure source, not evidence that a particular coordination failure exists.

### NemotronLabs VoiceChat — already owns as a model design

- an open 11B full-duplex speech-to-speech model;
- native parallel function-call output stream;
- open weights and inference code;
- tool-calling evaluation on FDB 3.0.

### Proactive-speaking paper — already owns

- the finding that current full-duplex models respond more reliably to being addressed / silence than to semantic reasons such as false claims or hazards.

### User-stream-routing paper — already owns

- channel-fusion vs cross-attention routing as a full-duplex design axis;
- the grounding vs context-corruption trade-off under overlapping speech.

### Lychee-FD — already owns

- acoustic/semantic gradient conflict in native full-duplex SLM training;
- hierarchical parameter separation as its solution.

The workbench must continuously search for new prior that further compresses our remaining space.

---

## 3. Why this is a workbench rather than a candidate

We do **not** yet know what the paper is.

Possible outcomes of baseline residency include, among many others:

- most of the gap is modality/perception and the broader realtime story is weak → demote;
- timing pressure rather than speech explains a large portion of the loss;
- partial observability during streaming changes reasoning or tool behavior;
- overlap between observation and generation is load-bearing;
- asynchronous tools/background work introduces a distinct failure class;
- reasoning quality is intact but action timing / scheduling is not;
- the gap decomposes differently across model architectures;
- no common abstraction exists and the territory should be killed;
- a different, simpler bottleneck appears that is not named in this README.

None of these is the registered hypothesis.

---

## 4. Baseline residency

The local agent must first become competent in **existing strong systems and evaluation harnesses**.

### A. τ-bench / τ-Voice — primary task substrate

Use the released repository and current version, not numbers copied from the original paper.

Understand and reproduce:
- text half-duplex agent evaluation;
- audio-native full-duplex evaluation;
- exact task/environment/tool semantics;
- tick-based orchestration;
- trajectory format and interaction metrics;
- current task fixes / versioning;
- how voice complexity conditions are produced;
- which provider adapters are open and what can be replaced by local systems.

The most useful property is that the same grounded domains support text and voice/full-duplex evaluation.

Do not immediately run all 278 tasks or expensive providers. Start with a small auditable subset.

### B. Full-Duplex-Bench v3 — secondary diagnostic substrate

Use its released real-human audio, disfluency annotations, mock APIs, inference/evaluation pipeline, and latency analysis.

The purpose is not to make a new FDB-v4. Use it to learn which temporal / tool-use events are already observable.

### C. Open model foothold: NemotronLabs VoiceChat 11B

Audit the exact released checkpoint and NVIDIA Speech runtime.

Reasons to prefer it as the first model-level foothold:
- open 11B weights;
- open inference stack;
- full-duplex streaming;
- native tool-call channel;
- research-oriented release;
- fits a single 80–96GB GPU in principle, and comfortably within the available one-node budget.

Do not fine-tune it at entry.

### D. Open runtime foothold: Qwen-Audio-Agent

Audit the foreground/background/orchestration implementation, event logs, task state, cancellation, result delivery, and local frontend support.

It is useful because concurrency is explicit in the runtime and backend agents/tools are replaceable.

Treat the default cloud frontend as optional; the repository supports alternative/local speech-to-speech frontends.

### E. Independent streaming substrate — only if earned

OmniInteract / StreamArena / STAR may later serve as independent evidence that a discovered temporal principle is not speech-specific.

Do **not** start by reproducing all of them.

---

## 5. What to measure before asking why

First build trustworthy instrumentation.

For every trajectory where the harness allows it, preserve:
- wall-clock / simulated timestamps;
- user audio or text event boundaries;
- partial vs finalized observations when available;
- model text / speech events;
- tool-call issue time, arguments, result time, and result consumption time;
- foreground/background task events;
- interruption / yield / resume events;
- final environment state and task success;
- latency and interaction metrics;
- model/runtime/version/config.

Do not invent a new scalar “realtime intelligence score” at the beginning.

Use existing task success and interaction metrics first; add diagnostics only when they answer a concrete question.

---

## 6. Exploration space — axes, not hypotheses

The agent should use the reproduced baseline to discover which transition is load-bearing.

Potential axes include:

- **modality:** text vs speech while holding task/tool semantics fixed as far as possible;
- **interaction contract:** turn-based / half-duplex vs full-duplex;
- **observation completeness:** complete user turn vs partial / streaming input;
- **wall-clock pressure:** unlimited thinking vs real-time response/action deadlines;
- **overlap:** user input arriving during agent generation;
- **tool timing:** tool starts/returns before, during, or after ongoing generation;
- **execution contract:** synchronous tool call vs asynchronous/background execution;
- **task concurrency:** foreground-only vs simultaneous delegated work;
- **environment change:** new information arriving while a task is already in flight;
- **reasoning budget / latency:** deeper reasoning with slower action vs shallower/faster behavior;
- **interaction events:** interruption, backchannel, hesitation, self-correction, clarification;
- **state lifetime:** what remains active across user turns, tool returns, task completion, or session memory;
- **architecture:** cascaded vs native full-duplex; single-stream vs separated/parallel streams.

These axes are a map for exploration. The agent must not run a Cartesian-product benchmark mechanically.

Choose comparisons because they distinguish plausible explanations revealed by the baseline.

---

## 7. Earliest exploration philosophy

The first new experiments should be **matched regime transitions**, not anomaly traps.

A healthy pattern is:

> reproduce a task successfully in a simpler regime  
> → change one interaction contract while preserving the task as much as possible  
> → inspect the trajectory and downstream consequence  
> → test the simplest alternative explanation  
> → update the problem representation.

Examples of useful matched transitions may include:
- same grounded task, text half-duplex vs audio full-duplex;
- same agent/tool task, synchronous execution vs asynchronous return;
- same utterance content, finalized input vs streamed chunks;
- same event sequence, no overlap vs overlap;
- same reasoning/model, turn-count budget vs wall-clock budget.

These examples do not prescribe a desired failure sign.

A null result is useful: it removes one suspected transition from the search space.

---

## 8. Anti-local-optimization rule

This rule is mandatory.

The local agent's objective is **not** to maximize τ-Voice, FDB-v3, VoiceChat tool F1, or any one slice.

After every meaningful research block, stop and answer:

1. What changed in our understanding of the realtime transition?
2. Which explanation became less plausible?
3. Did the important object get broader/simpler, or did it collapse into a local speech issue?
4. What does the strongest nearest prior now already own?
5. Can a reviewer compress the current story into “τ-Voice/FDB-v3 + one more slice”?
6. What next comparison has the highest information gain?
7. Should the agent continue, pivot inside the territory, freeze, or kill?

Do not:
- tune prompts until one desired gap appears;
- keep adding cases around self-correction because FDB-v3 mentioned it;
- optimize a rollback protocol because Cordon exists;
- train a routing gate because user-stream routing exists;
- build a new benchmark because existing tasks are inconvenient;
- add ten models before understanding one trajectory;
- turn latency engineering into a scientific claim;
- protect “realtime coordination” terminology if experiments point elsewhere.

---

## 9. Research blocks and freedom to explore

The agent should work autonomously in blocks, not ask for approval after each small experiment.

A typical block should contain:
1. one ownership / literature update;
2. one baseline or matched-regime experiment;
3. manual inspection of representative trajectories;
4. at least one simple alternative-explanation check;
5. an integrated interpretation;
6. an explicit **CONTINUE / PIVOT / FREEZE / KILL** decision;
7. the next highest-information action.

The agent is encouraged to:
- abandon an uninformative benchmark;
- switch from voice to a text/asynchronous control if that isolates the object better;
- instrument runtime state or event traces;
- use a surprising negative result as a gradient;
- follow a newly exposed bottleneck even if it is not named here;
- search related fields such as streaming systems, control, HCI, distributed systems, robotics, or realtime games for useful experimental abstractions.

The agent is not required to preserve the initial framing.

---

## 10. Training policy

**No model training is authorized at entry.**

First establish:
- a strong reproducible baseline;
- a meaningful regime transition;
- a bottleneck or changed premise that survives simple controls.

Only then may the workbench consider:
- small LoRA / adapter tuning;
- a lightweight controller/router;
- post-training on a narrow interaction behavior;
- runtime / orchestration changes;
- a model-side architectural intervention.

Any trained method must satisfy:

> **measured failure → diagnosed bottleneck → controllable action → robust downstream effect**

Do not train merely because the available GPUs make training possible.

---

## 11. Compute and practicality

Available practical boundary:
- one node at a time;
- up to 4×A100 80GB or 4×RTX PRO 6000 96GB;
- no cross-node assumption.

Early work should usually need:
- CPU + API calls for τ-bench inspection, or
- 1 GPU for an 11B-class open voice model,
- not 8-GPU foundation-model pretraining.

The expensive resource is research attention, not GPU hours.

---

## 12. Candidate promotion contract

Do **not** create anything under `candidates/` until this workbench has actually produced evidence satisfying the repository contract:

- the scientific question is clear;
- the question is important independently of the hoped-for result;
- the core finding / bottleneck is empirical rather than invented in advance;
- nearest-prior ownership is defensible;
- confirmation is feasible;
- the story is getting simpler as evidence accumulates.

A candidate may emerge around timing, concurrency, state, routing, reasoning, tool semantics, or something not anticipated here.

The directory name and initial framing do not own the future paper.

---

## 13. Immediate first block

### P0 — artifact / ownership audit

Before experiments:
- pin current versions/commits of τ-bench, FDB-v3, NemotronLabs VoiceChat, and Qwen-Audio-Agent;
- read their evaluation/runtime code sufficiently to draw the actual event/data-flow diagrams;
- verify current released checkpoints, licenses, inference requirements, and known benchmark updates;
- write a compact ownership table of what each nearest prior already proves.

### P1 — baseline residency

Choose the **smallest practical pair of strong baselines** that lets us compare a sequential/turn-based contract with a realtime/streaming contract on grounded tasks.

Preference:
- reuse τ-bench task semantics where possible;
- use an open model/runtime wherever possible;
- manually inspect tens of trajectories before scaling.

Do not begin with a full leaderboard run.

### P2 — regime map

From P1 traces, identify a **small number of matched interaction changes** that are actually supported by the harness and could explain observed behavior.

Run only those with high information value.

The goal is not to prove a named phenomenon. The goal is to discover:
- which transition matters;
- what remains invariant;
- what simple explanation is false;
- where to look next.

### Decision

After P0–P2, choose:

- **CONTINUE** — a robust, consequential realtime transition is emerging;
- **PIVOT** — a different, simpler object appeared;
- **FREEZE** — artifacts are useful but no strong scientific object yet;
- **KILL** — the gap is already explained / too provider-specific / too engineering-heavy.

No method development before this decision.

---

## 14. Starting primary references / artifacts

- **τ-Voice: Benchmarking Full-Duplex Voice Agents on Real-World Domains** — ICML 2026  
  https://arxiv.org/abs/2603.13686  
  https://github.com/sierra-research/tau2-bench

- **Full-Duplex-Bench-v3: Benchmarking Tool Use for Full-Duplex Voice Agents Under Real-World Disfluency** — 2026  
  https://arxiv.org/abs/2604.04847  
  https://github.com/DanielLin94144/Full-Duplex-Bench

- **Stream RAG: Instant and Accurate Spoken Dialogue Systems with Streaming Tool Usage** — ICML 2026  
  https://arxiv.org/abs/2510.02044

- **OmniInteract: Benchmarking Real-World Streaming Interaction for Real-Time Omnimodal Assistants** — 2026  
  https://arxiv.org/abs/2605.26485

- **Hierarchical Acoustic-Semantic Modeling / Lychee-FD** — ACL 2026 Outstanding Paper  
  https://aclanthology.org/2026.acl-long.419/  
  https://github.com/HITsz-TMG/Lychee-FD

- **How Should LLMs Listen While Speaking? A Study of User-Stream Routing in Full-Duplex Spoken Dialogue** — 2026  
  https://arxiv.org/abs/2605.10199

- **LLMs Get Lost in Evolving User Intent** — 2026  
  https://arxiv.org/abs/2607.20734  
  https://github.com/microsoft/evolving-intent

- **Cordon: Semantic Transactions for Tool-Using LLM Agents** — 2026  
  https://arxiv.org/abs/2606.17573

- **NemotronLabs VoiceChat: An Open Full-duplex Speech-to-Speech Model with Tool Calling Capabilities** — 2026  
  https://arxiv.org/abs/2609.21967  
  https://huggingface.co/nvidia/NVIDIA-NemotronLabs-VoiceChat-11B  
  https://github.com/NVIDIA-NeMo/Speech/tree/nemotron-labs-voicechat

- **Qwen-Audio-Agent Technical Report** — 2026  
  https://arxiv.org/abs/2609.25195  
  https://github.com/QwenAudio/qwen-audio-agent

- **Full-Duplex Speech Models Take the Floor When Asked, Not When Needed** — 2026  
  https://arxiv.org/abs/2609.19596

- **Beyond Scaling: Assessing Strategic Reasoning and Rapid Decision-Making Capability of LLMs in Zero-sum Environments (STAR)** — 2026  
  https://arxiv.org/abs/2603.09337

- **Real-Time Deadlines Reveal Temporal Awareness Failures in LLM Strategic Dialogues** — 2026  
  https://arxiv.org/abs/2601.13206

---

## 15. Current paper identity

**None.**

Current scientific territory:

> **how agent capability changes when interaction becomes realtime, streaming, and asynchronous rather than sequential and turn-based**

This is intentionally a territory, not an RQ.

The workbench succeeds if it discovers a simpler, empirical, defensible object with top-conference ceiling — or if it quickly proves that no such object is available and gets killed.
