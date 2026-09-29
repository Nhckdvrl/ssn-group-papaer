# Realtime Computation Boundaries — Workbench

## 当前进度（中文，2026-09-30）

**状态：** P0（领域理解 + 谱系重建 + 代码级架构审计）完成第一轮；P1 基线驻留开始（下载 Realtime-Venus 权重、做可运行性检查）。**尚无 paper identity，candidates = 0。**

**P0 最重要的结论（详见下方 §P0）：**
1. 全双工领域在"统一/原生"和"模块/分离"之间来回摆动，但每次摆动保护的是同一对东西：**文本 LLM 的智能**（脆弱、昂贵）和**密集时间上的交互策略**（需要低延迟）。Lychee-FD 是唯一先测量瓶颈（深层梯度冲突 + 稀疏文本梯度被稠密音频稀释）再做分离的工作。
2. EMNLP 综述的 L0–L3 只刻画"轮转决策放在哪一层"，**没有覆盖"推理/工具的快慢边界"**这一维度——这正是 2026 年 9 月系统分歧最大的地方。
3. 五套快慢系统在两个维度上给出了相反答案：
   - **慢侧能看到什么**：只看当前一轮的 ASR 文本（NVIDIA）/ 请求时刻冻结的证据快照（Venus）/ 目标 + 最近 10 轮（Qwen）/ 与快侧并行接收同一输入（ConvFill）/ 周期性看完整历史（Think@5Hz、游戏 Latent Bridge）。
   - **谁来写最终内容**：慢侧写好、快侧照读（NVIDIA 的 prefill-and-repeat、Venus 的 polish）/ 快侧拿慢侧结果自己组织（Qwen、ConvFill、Latent Bridge）。
4. 目前只知道设计空间存在分歧，**不知道哪个变量真正决定能力**。下一步：选一个开放基线，先看懂它的真实轨迹。

---

**Lane:** our-taste  
**Stage:** ACTIVE EXPLORATORY WORKBENCH — **not a candidate**  
**Target ceiling:** ICML / ICLR / NeurIPS / ACL / CVPR main-track scale.  
**Core discipline:** understand the design space and let the load-bearing boundary emerge from strong baselines. Do not pre-register delegation, latent bridge, stale state, or any specific fix as the paper.

---

## 0. Territory

Realtime interactive agents face a structural tension:

- perception / conversational feedback / control may need to run on tens-to-hundreds of milliseconds;
- planning, long reasoning, retrieval, tool use, and complex environment actions may take seconds or longer;
- some information must remain available continuously while other computation can be delayed or delegated.

Recent systems increasingly respond by introducing **computational boundaries across timescales**: acoustic vs semantic pathways, Thinker vs Talker, frontend vs backend, fast reactive vs slow deliberative loops, or slow perception/reasoning vs fast action experts.

This workbench studies that **problem territory**:

> **How should computation and state be partitioned, shared, and communicated across different timescales in realtime multimodal agents?**

This is intentionally not a final RQ.

We do **not** assume:
- two-model systems are inherently better than unified models;
- separation is inherently better than sharing;
- text, latent, KV, graph, or structured state is the right bridge;
- delegation is always useful;
- stale state, routing, or result admission is the central bottleneck;
- voice is the final scientific substrate.

The goal is to inhabit strong open systems, understand where their boundaries actually are, and discover which boundary choice is load-bearing.

---

## 1. Why this territory exists: field genealogy, not gap filling

This workbench is admitted because several strong lineages independently expose the same design pressure while giving **different answers**.

### 1.1 Pipeline → native unification

**Moshi (2024)** starts from a concrete dissatisfaction with ASR → text LLM → TTS pipelines: pipeline latency, a text bottleneck that discards non-linguistic information, and explicit turn segmentation that cannot naturally represent overlap/interruption. Its answer is a speech-text foundation model with parallel user/system streams.

Reusable move: **a serving pipeline is not neutral; its interface constrains what interaction can be represented.**

### 1.2 Preserve intelligence while adding speech

**Freeze-Omni (ICML 2025)** exposes another pressure: adapting a text LLM to speech can damage intelligence already present in the text backbone. It freezes the LLM while attaching speech input/output.

Changed problem representation: making speech native is not enough; **capability preservation is an architectural constraint**.

### 1.3 Push back toward one standalone model

**SALMONN-omni (NeurIPS 2025)** argues that modular full-duplex systems accumulate errors and struggle with context-dependent interaction. It also observes that Moshi-style codec injection can degrade speech-vs-text capability. Its answer is a standalone codec-free speech LLM with dynamic thinking.

### 1.4 Modularity comes back

**FlexDuo (2025)** and **DuplexCascade (2026)** move in the other direction. FlexDuo decouples duplex control from the dialogue model to avoid tightly coupled optimization and contextual noise. DuplexCascade shows that a VAD-free streaming ASR–LLM–TTS cascade can achieve strong full-duplex behavior while retaining a capable text LLM.

The 2026 EMNLP Main full-duplex survey therefore treats architectural levels as **not a progress ladder**: external/modular control remains competitive, L1 has become an industrial attractor, and token-level native systems remain heterogeneous.

Pressure: **interaction capability and model unification are not the same axis.**

### 1.5 Sharing itself can become the bottleneck

**Hierarchical Acoustic-Semantic Modeling / Lychee-FD (ACL 2026 Outstanding)** analyzes optimization dynamics and identifies severe acoustic–semantic gradient conflict when deeply shared parameters are forced to model both. The method follows from the measured bottleneck: hierarchical parameter separation plus semantic alignment.

This is a canonical Paper-Rewind exemplar:

> **successful unified baseline → analyze optimization dynamics → localize conflict → separate only where evidence demands it.**

### 1.6 But separation is not a general law

**Scaling Laws for Native Multimodal Models (ICCV 2025)** trains 457 models and finds no inherent advantage for late fusion over early fusion; early fusion can be stronger at smaller scales, while MoE develops modality-specialized weights.

**Audex (2026)** uses a simple unified audio-text decoder and, with very large-scale multimodal/text training plus RL/distillation, reports strong audio capability with little text regression.

Therefore this workbench must **not** turn into a campaign for modularity. Sufficient scale/data/training can change the answer.

### 1.7 2026 realtime systems converge on explicit fast/slow division

By September 2026 several independent systems separate realtime interaction from slower reasoning/action:

- **GPT-Live-1:** full-duplex conversation model + independently chosen backend reasoning/tool model;
- **NVIDIA frontend-backend architecture:** streaming duplex frontend emits a delegation token and streams transcript to a text backend; backend results are reinjected;
- **Qwen-Audio-Agent:** Frontend Agent + Orchestration Runtime + Backend Agent; mixed direct/delegated execution outperforms direct-only and all-delegated on its cockpit benchmark;
- **Realtime-Venus:** full-duplex 9B frontend + asynchronous Harness; foreground interaction continues while background work runs;
- **ConvFill / Thinking While Speaking:** small fast Talker continues interacting while a slower Reasoner supplies knowledge asynchronously.

These systems agree that different timescales matter, but they do **not** agree on what the frontend should own, what information crosses the boundary, what representation is transmitted, what state is shared vs isolated, when slow results become valid for the fast loop, or how much slow computation should remain in the live causal state.

That unresolved design space is the workbench object.

### 1.8 The same pressure appears outside voice

- **The Latent Bridge: A Continuous Slow-Fast Channel for Real-Time Game Agents (2026)** freezes a fast reactive VLM and slow reasoning VLM and studies the communication channel itself; text and latent bridges behave differently and using both can interfere.
- **Latent Bridge for dual-system VLA inference (2026)** predicts intermediate VLM features so slow VLM computation need not run at every control step.
- **Think at 5 Hz, Act at 20 Hz (2026)** separates slow VLM reasoning from a faster action expert and trains the expert under stale-cache conditions.

Shared pressure: **high-quality foundation-model computation and realtime closed-loop interaction often operate at incompatible timescales.**

---

## 2. Top-conference ceiling contract

Authorized scope ladder:

> **strong realtime systems increasingly create computational boundaries across timescales**  
> → **baseline exploration identifies which boundary variables actually control capability / latency / robustness and why**  
> → **a transferable principle, mechanism, or minimal intervention for multi-timescale interactive intelligence**

A strong candidate may eventually concern computation ownership, shared vs isolated state, boundary representation, update cadence, freshness/staleness, admission of slow results, capability–latency allocation, or another object discovered from baseline traces. None is pre-selected.

### Demote / kill if

- it becomes voice frontend + stronger backend improves task success;
- it becomes another router / delegate-or-not classifier;
- it becomes text-vs-latent handoff after existing bridge papers already own that comparison;
- it becomes generic multi-agent context compression;
- it becomes generic stale-context detection already owned by TicToc / Concord;
- it becomes orchestration engineering with no scientific quantity;
- evidence remains specific to one proprietary provider;
- apparent principles disappear when controlling for frontend/backend model capability;
- the only contribution is a benchmark or hand-authored schema;
- generality is asserted rhetorically rather than demonstrated on an independent realtime substrate.

---

## 3. Nearest-prior ownership map

### Full-duplex survey (EMNLP 2026 Main)
Already owns the L0–L3 hierarchy, T×I×R ontology, decision FSM, realization gap, and the cross-system audit. Do not claim a new full-duplex taxonomy.

### Lychee-FD
Already owns acoustic–semantic gradient conflict in deeply shared full-duplex SLM parameters and hierarchical separation as its solution.

### Qwen-Audio-Agent
Already owns foreground/background architecture, direct vs all-delegated vs mixed execution comparison on its cockpit benchmark, and its runtime task lifecycle. Do not claim mixed delegation is better.

### NVIDIA frontend-backend full-duplex agent
Already owns delegation-token speech frontend, streaming ASR transcript to a text backend, result reinjection, and its tool-call results.

### Realtime-Venus
Already owns a dual-loop realtime + asynchronous Harness system, request-time context capture, work lifecycle, cancellation/freshness checks, and result delivery.

### GPT-Live
Already owns as a deployed design independent realtime voice and backend delegation. Use as convergence evidence, not a reproducible baseline.

### The Latent Bridge — realtime games
Already owns frozen fast+slow VLM coupling, text vs learned latent bridge, the relation between slow-model usefulness and bridge gain, and destructive interference from combining channels.

### Latent Bridge — VLA
Already owns feature/KV delta prediction to reduce slow VLM frequency in dual-system VLA.

### Think at 5 Hz, Act at 20 Hz
Already owns slow VLM / fast action-expert driving with fresh per-tick observation and randomized-staleness training.

### Routed Graph Handoff
Already owns adaptive natural-language vs graph delegation in multi-agent LLM systems.

### Temporal Blindness / TicToc
Already owns elapsed-time-induced staleness in multi-turn tool-use decisions.

### Concord
Already owns provenance-indexed stale tool observations and runtime repair/drop/refresh for mutable external sources.

### Streaming/adaptive reasoning papers
Think-as-You-See, AdaSR, Think-While-Listening and related work already study when/how much to reason while input is streaming. Do not reduce this workbench to adaptive reasoning-budget allocation.

---

## 4. Why this is a workbench, not a candidate

We know only that the field has a real design tension. We do **not** know whether one boundary variable dominates, whether voice and embodied agents share a bottleneck, whether representation matters more than timing, whether current systems are already near the correct decomposition, or whether a method is needed.

Possible outcomes include: no general principle survives; strong current systems already solve the important issues; one interface variable creates a large reproducible change; a current best practice is unnecessary under a strong baseline; different regimes require different boundaries; or a new bottleneck appears that is not named here.

---

## 5. Baseline residency: open artifacts first

### A. Realtime-Venus — primary model/runtime foothold

Use the released 9B models and open Harness. Map the shared causal timeline, request capture/evidence cutoff, dispatch, private feedback, playback-aware delivery, state ownership, freshness rules, and representative trajectories before changing anything.

### B. Qwen-Audio-Agent — configurable runtime foothold

Use primarily as an orchestration/design baseline. Frontend and backend are independently selectable; frontend-only mode exists; a fully local Hugging Face speech-to-speech frontend is supported; custom realtime providers and backend adapters are explicit interfaces.

Do not depend on a proprietary Qwen realtime model for the scientific object.

### C. DuplexCascade — modular full-duplex control

Use as a practical counterexample to native = necessary. It offers a VAD-free streaming cascade with open code and a capable text LLM at the center.

### D. Lychee-FD — native/separated model baseline

Use for understanding an internally unified but hierarchically separated model. Training/serving code and weights are open. Do not immediately retrain it.

### E. Cross-domain baselines — only after an object emerges

The game-agent Latent Bridge and VLA fast/slow systems are independent evidence sources, not day-1 reproduction requirements.

---

## 6. Exploration map — axes, not hypotheses

Trace where existing systems place boundaries:

- perception → semantic state;
- live dialogue → deliberate reasoning;
- reasoning → tool/action;
- slow model → fast model;
- backend result → live causal state;
- semantic content → acoustic realization;
- persistent context → per-tick observation.

Useful quantities may include task success, interaction latency, reasoning/tool latency, foreground interruption behavior, backend utilization, payload information/size, state age/update cadence, result usefulness on return, downstream sensitivity to boundary interventions, compute cost, and model-capability controls.

Look for **large gradients produced by small, interpretable boundary changes**. Do not assume which gradient exists.

---

## 7. Paper-Rewind discipline

Before inventing a method, reconstruct at least three lineages in depth.

### Rewind A — Moshi → SALMONN / Freeze-Omni → DuplexCascade
Ask what each paper believed the prior architecture was losing, which failure was model-level vs system-level, which assumption the next paper rejected, and what earliest experiment would distinguish pipeline from speech-model failure.

### Rewind B — unified full-duplex → Lychee-FD
Hide the final hierarchical method first. Reconstruct which measurements rule out simple data/scale explanations, what layer/stage analyses localize the conflict, and why separation becomes justified only after that evidence.

### Rewind C — single-loop → frontend/backend systems
Compare Qwen-Audio-Agent, NVIDIA, Realtime-Venus, GPT-Live and ConvFill. Map fast/slow responsibilities, state visibility, request representation, result reintegration, user-facing timing and external-effect ownership. Do not infer one best architecture from the comparison.

---

## 8. Anti-local-optimization rule

After every meaningful block answer:

1. What did the baseline teach us about the boundary itself?
2. Which architecture assumption became less plausible?
3. Is the effect model capability or interface?
4. What strongest current prior can compress this finding?
5. Are we rediscovering delegation/routing/staleness/handoff compression?
6. Does the current object still have a path beyond voice?
7. What experiment has highest information gain now?
8. CONTINUE / PIVOT / FREEZE / KILL?

Forbidden loops:

> delegation error → tune router → tune router → bigger routing dataset

> stale result → invent version IDs → build transactional runtime

> text handoff weak → train latent bridge immediately

> native model worse → conclude modularity is better

> modular model worse → conclude unified is better

---

## 9. Training policy

**No foundation-model training at entry.**

Early work uses released models, frozen inference, runtime instrumentation, matched boundary interventions, controlled frontend/backend substitutions, and valid offline replay.

Small training is allowed only after a stable bottleneck appears: LoRA/adapter, small bridge, lightweight controller, or localized post-training.

Any trained component must satisfy:

> **measured boundary failure → localized bottleneck → controllable interface → minimal intervention → robust outcome**

---

## 10. Compute / feasibility

One node at a time: up to 4×A100 80GB or 4×RTX PRO 6000 96GB; no cross-node assumption.

This is sufficient for 9B–11B open realtime/speech models, local cascaded frontends, frozen fast/slow experiments, and small bridge/LoRA training if eventually justified.

Audex-scale pretraining or a new Omni foundation model is neither feasible nor required. Big-lab unified-model results are scientific counterexamples, not reproduction targets.

---

## 11. Relationship to the previous realtime-agent workbench

The previous realtime-agent-capability-transition workbench produced useful baseline assets but its original mother pressure weakened: September-2026 public trajectories show dual-system voice agents can largely close the earlier voice-vs-text task-success gap; much residual failure was explained by spoken entity capture, now directly studied by τ-Elicitation; several initially suspected realtime failure slices were weak or already owned.

Do not discard its downloaded trajectories or analysis code. Reuse them as baseline knowledge when relevant.

This workbench does **not** inherit the hypothesis that realtime interaction generally degrades capability.

---

## 12. Candidate promotion contract

**Current paper identity: none.**

Create a candidate only after experiments produce: a simple scientific question; an empirical boundary effect/bottleneck surviving strong controls; evidence separating interface effects from model-capability effects; defensible nearest-prior ownership; a plausible path beyond one voice stack if generality is claimed; feasible confirmation; and a story that gets simpler as evidence accumulates.

The final candidate may be architecture, model science, agent systems, or something else. It does not have to preserve the phrase realtime computation boundaries.

---

## 13. Immediate first research block

### P0 — deep artifact + genealogy audit

Before proposing experiments:

1. reproduce architecture/dataflow diagrams from code for Realtime-Venus, Qwen-Audio-Agent, DuplexCascade, and Lychee-FD;
2. reconstruct the three Paper-Rewind lineages in §7;
3. verify current versions, checkpoints, licenses, and single-node inference requirements;
4. write a compact table of fast-loop responsibility, slow-loop responsibility, boundary representation, state ownership, update cadence, result reintegration, and already-evaluated failure modes.

### P1 — one strong open system, deeply understood

Choose **one** open, configurable baseline first. Default preference: Realtime-Venus + Harness, unless code audit gives a stronger reason to use Qwen-Audio-Agent with a local frontend.

Become able to explain representative successful and failed trajectories end-to-end. Do not scale breadth before this.

### P2 — let the baseline expose the first pressure

Only after P1, choose a small number of interventions that separate plausible explanations. Do not start from test stale state, compare text vs latent, train a router, or prove delegation helps.

The first useful experiment should emerge from what the strong baseline actually relies on.

### Decision

- **CONTINUE** — a consequential boundary variable is emerging;
- **PIVOT** — a simpler/better object emerged inside the territory;
- **FREEZE** — good field knowledge but no tractable scientific object;
- **KILL** — nearest prior or baseline strength removes the research space.

---

## 14. Primary starting references

- Moshi — 2024
- Freeze-Omni — ICML 2025
- SALMONN-omni — NeurIPS 2025
- Scaling Laws for Native Multimodal Models — ICCV 2025
- FlexDuo — 2025
- DuplexCascade — 2026
- Hierarchical Acoustic-Semantic Modeling / Lychee-FD — ACL 2026 Outstanding
- Speaking While Listening: Full-Duplex Survey and Empirical Audit — EMNLP 2026 Main
- Unified Audio Intelligence Without Regressing on Text Intelligence / Audex — 2026
- The Latent Bridge: A Continuous Slow-Fast Channel for Real-Time Game Agents — 2026
- Latent Bridge: Feature Delta Prediction for Efficient Dual-System VLA Inference — 2026
- Think at 5 Hz, Act at 20 Hz — 2026
- Realtime-Venus — 2026
- Qwen-Audio-Agent — 2026
- A frontend-backend architecture for tool calls in full-duplex speech models — 2026
- GPT-Live-1 delegation documentation — 2026
- Routed Graph Handoff — 2026
- Your LLM Agents are Temporally Blind — ACL Findings 2026
- Concord / When Agent Context Goes Stale — AgenticOS @ SOSP 2026

Re-verify frontier papers before making any latest-state claim.
---

## P0 — Field understanding, Paper Rewind, code-level boundary audit (2026-09-30)

Sources read (full text, local copies under `/home/xiang/rt_ext/papers`): Moshi 2410.00037, Freeze-Omni 2411.00774, SALMONN-omni 2505.17060, FlexDuo 2502.13472, DuplexCascade 2603.09180, Lychee-FD 2607.06540, FD survey 2606.19453, Scaling Laws NMM 2504.07951, Audex 2607.05196, Realtime-Venus 2609.13814 (+ code `inclusionAI/Realtime-Venus@e53ae8d`), Qwen-Audio-Agent 2609.25195 (+ code `f6dd0e3`), NVIDIA frontend-backend 2609.19334, ConvFill 2511.07397, Never Stop Thinking 2609.17416, game Latent Bridge 2606.24470, VLA Latent Bridge 2605.02739, Think@5Hz 2607.15621.

### Rewind A — Moshi → Freeze-Omni / SALMONN-omni → FlexDuo / DuplexCascade

| step | strongest parent / field belief | pressure the authors could not accept | premise rejected | earliest revealing experiment (reconstructed) |
|---|---|---|---|---|
| Moshi | ASR→LLM→TTS is the default | latency; text bottleneck drops paralinguistics; turn segmentation cannot represent overlap | "the pipeline interface is neutral" | measure overlap/interrupt behaviour a VAD-segmented cascade *cannot express*, independent of model quality |
| Freeze-Omni | native speech-text training (Moshi-like) | speech adaptation erodes the text LLM's intelligence (Moshi reports −12.7 LlamaQ after duplex alignment) | "making speech native is enough" | same backbone, spoken-QA vs text-QA before/after speech adaptation |
| SALMONN-omni | modular FD (VAD / interrupter / multiple LLMs) or codec-injected single LLM | error accumulation across modules; codec tokens in the LLM space still degrade speech-vs-text | "duplex needs extra modules" and "one LLM needs codec tokens" | module-wise error attribution on barge-in / echo cases; speech-vs-text gap with and without codec injection |
| FlexDuo / DuplexCascade | tightly coupled native FD models | coupled optimization; contextual noise; hard to keep text-LLM intelligence | "native = necessary for full duplex" | VAD-free micro-turn cascade with the *same* text LLM vs native FD on FDB + VoiceBench |

Why the field oscillates: every step protects the same two assets placed differently — **(i) the text LLM's intelligence, fragile under joint training, and (ii) a dense-time interaction policy that needs low latency** — and each architecture pays for one with the other. The survey confirms the levels are *not a progress ladder* (L0 competitive, L1 an attractor, L2 heterogeneous, L3 unrealized); Audex (unified, 30B-A3B, 157B audio + 320B text tokens + RL/distillation) shows sufficient scale can shrink the trade-off, so "separate" is not a law.

### Rewind B — unified full-duplex SLM → Lychee-FD

- Parent: native end-to-end FD SLM loses knowledge; Thinker–Talker keeps knowledge but costs latency/inference.
- Moves that rule out "too small / too little data / weak recipe": (1) **layer-wise cosine between semantic-loss and acoustic-loss gradients** on the *same* model and data — synergistic in shallow layers, orthogonal→negative in deep layers; (2) **gradient-magnitude ratio** — sparse text (~3 Hz) aligned to dense audio (~25 Hz) via padding suppresses semantic gradients in every layer.
- Each measurement maps to one component: conflict in deep layers → split only deep layers into acoustic/semantic heads (keeps depth, keeps latency); dilution → a semantic alignment channel (continuous text supervision).
- Prior already had MOSS-Speech's representation-motivated layer split; Lychee's contribution is the **optimization-level diagnosis** that makes the split necessary and localized.
- Reusable move: *baseline works → measure a training/inference quantity that is invisible in end metrics → localize → separate only where the measurement says*.

### Rewind C — single loop → fast/slow systems (code + papers)

| | Realtime-Venus (+Harness) | NVIDIA FE-BE | Qwen-Audio-Agent | ConvFill | Game Latent Bridge | Think@5Hz (VLA) |
|---|---|---|---|---|---|---|
| fast loop | 9B native FD model (MiniCPM-o 4.5 based): listen/speak/yield, direct answers, emits `<delegate>` span | duplex STT frontend; emits delegation token; silent/filler while waiting | realtime model (cloud or local S2S): dialogue, identity + read-only lookups, `spawn_thinking` | tiny Talker (135M–1.7B) | 9B reactive VLM @15 Hz | light action expert every 50 ms tick |
| slow loop | Harness: router → capability (Codex agent / multimodal / skill) → **polish** | LangGraph ReAct text LLM | backend agent via A2A (writes, money, composite tasks) | frontier Reasoner + tools | 8B thinking VLM @~1 Hz | frozen 7B VLM at low frequency |
| trigger | fast decides (in-stream token) | fast decides | fast decides (tool call) | always, in parallel | continuous | periodic |
| what slow sees | NL objective + **evidence snapshot frozen at the opening tag** (look-back Δ; playback-confirmed assistant speech only) | **only the current user ASR transcript** per delegated turn + its own thread memory of past delegated turns | objective + ≤10 recent turns + verified IDs/lookups; backend keeps ≤50 task turns | the same transcribed user utterance as the Talker | full visual history at its own rate | instruction + visual history |
| slow → fast payload | polished spoken-form text in private `<backend>` span | NL text **prefilled; frontend trained to repeat it exactly** | task result / status / input-request records | streamed knowledge text | text suffix **or** learned latent tokens | per-layer KV cache |
| who authors user-facing content | slow (Harness decides content & wording; fast decides only *when*) | slow (verbatim repeat) | fast (presents result in current context) | fast (infills + integrates) | fast (acts) | fast (acts) |
| freshness / staleness | freshness deadline + TTL; stale results dropped; delivery gated on playback ack | none explicit | results held until user stops speaking; revision checks for memory | none explicit | implicit (1 s lag) | trained with randomized staleness |
| evaluated failure modes | delegation-decision accuracy only (Venus-Audio over-delegates routine requests: specificity 39%); **end-to-end delegated execution not evaluated** | single-turn tool recall; FDB-v3; EVA-Bench | cockpit 134 cases: direct 72%, all-delegated 81%, mixed 91%; τ airline text-IO: frontend-only 74 / harness 78 / backend-only 76; EVA airline 44 / 62 / 68 | accuracy within 6.3% of Reasoner; user study | bridge gain iff slow>fast (r=0.93); text+latent together interfere | per-tick freshness 82→94 route completion |

**Where strong systems disagree (candidate exploration surface, not hypotheses):**
1. *Visibility asymmetry* — the slow side sees anything from "only the delegated utterance" to "the whole stream".
2. *Authorship* — whether the fast model re-authors the slow result (Qwen, ConvFill, game) or is reduced to a timing/voicing device for slow-authored text (NVIDIA, Venus).
3. *Trigger* — fast-decided sparse delegation (voice systems) vs always-on slow computation (ConvFill, game, VLA).
4. *Freshness policy* — drop (Venus), hold (Qwen), train-to-tolerate (Think@5Hz), ignore (NVIDIA, ConvFill).

### Nearest-prior ownership update (additions to §3)

- **Never Stop Thinking (2609.17416, Pine AI)**: one persistent reasoning stream with interrupt-and-resume in an *unmodified* text model; ReactiveBench; LLM judges reward visible reasoning (sign flips under an independent judge); verifiable RL for continuous-time thinking. Owns "single-stream continuous-time agent" as the unified counterpoint to fast/slow splits.
- **ConvFill (2511.07397)**: small Talker + frontier Reasoner, Talker integrates streamed knowledge; owns talker-infill as a method.
- **Think@5Hz (2607.15621)**: owns KV-cache as the slow→fast payload + randomized-staleness training + per-tick freshness gains in driving.
- **VLA Latent Bridge (2605.02739)**: owns predicting slow-model feature/KV deltas to call the slow model less often.
- **Qwen-Audio-Agent text-IO τ results**: already show harness ≈ backend-only on τ airline and harness < backend-only on EVA airline — a composite-vs-slow-alone comparison exists, but without decomposition of *why*.

### Baseline choice (tentative) and feasibility

Default **Realtime-Venus-Audio + Harness** kept, because it is the only open system whose fast model is itself a trained 9B native FD model with an in-stream delegation token, an explicit snapshot boundary, and slow-authored replies — i.e. every disagreement axis above is concretely instantiated and instrumentable (`harness/core/delegate_parser.py`, `bridge/boundary.py`, `core/delivery.py`, `jobs/models.py`).
Feasibility facts: weights 20 GB per model (download running); released code integrates **Omni** with the Harness, Audio is inference-only; demo pins torch 2.4 / transformers 4.51.3 (torch 2.4 does not support Blackwell) — existing env `pvlm` (torch 2.11 cu130, transformers 4.51.3) is the first candidate runtime; Harness backends default to Codex/Gemini but `DelegateBackend` (`plan/execute/oralize`) can be implemented with local vLLM models.
Fallback if Venus cannot be made to run in an existing env within a bounded effort: Qwen-Audio-Agent with the local HF speech-to-speech frontend and its existing τ-bench text runner.

### Current explanations worth distinguishing (to be tested only after trace residency)

For a fast/slow composite on tasks the slow model can solve alone, the composite's capability could be governed mainly by:
1. **slow capability** (boundary transparent: composite ≈ slow-alone on delegated work);
2. **visibility at the boundary** (loss comes from what the slow side is not shown);
3. **authorship** (loss/gain comes from the fast model re-expressing, dropping, or mistiming slow content);
4. **age** (the conversation has moved on by the time the result is admitted).
The first residency experiment is descriptive: run the baseline on a small set of multi-turn tasks, and for each failure locate which of these four links broke, before any intervention.
