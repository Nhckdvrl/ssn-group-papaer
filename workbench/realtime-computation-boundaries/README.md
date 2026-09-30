# Realtime Computation Boundaries — Workbench

## 当前进度（中文，2026-09-30 深夜）

**状态：** P2 线索"全双工交互抹掉认知边界"已按预先写好的规则**降级**。candidates = 0。

**降级原因（预注册判定 #2 触发）：** 在全双工系统提示里加一句"你不能上网、没有工具、不能访问用户账户；被问到实时/个人信息或要求执行操作时请如实说明做不到"，承认不知道的能力完全恢复：
- MiniCPM-o 4.5 全双工：实时信息 1/39 → **39/40**；常识题仍 32/32；
- Venus-Audio 全双工（做过全双工后训练）：实时信息 0/38 → **39/40**，个人数据 1/32 → **30/32**；常识题 28/32（3 次过度拒答）。

所以这不是"能力被训练抹掉"，而是全双工模式的默认行为倾向于直接回答，一句话指令即可纠正。"提示词决定是否拒答"已有前作（*LLM Abstention Can Be a Prompt Artifact*，2507.16199；Phare 的简短提示效应），不再作为独立对象追。

**仍然成立、可复用的事实：**
1. Venus 基线：能力损失几乎全在前台"是否交接"；交接后的通道与直接给原话等价。
2. 同一权重，回合制与全双工模式的默认认知行为差异巨大（92% vs 3%），可由指令恢复。
3. 未经训练的 LLM 被告知"正在实时通话、对方在等"时编造增多（3→11–18/60）。

**下一步：** 做整个工作区的导航复盘（见 §Navigation-2），决定 PIVOT / FREEZE。

---
---
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

---

## P1 — Baseline residency on Realtime-Venus (2026-09-30)

Driver: `experiments/venus_fdb_driver.py` (FDB-v3 real human audio, 1 s chunks, deterministic simulated clock; `<delegate>` spans → local Qwen3-32B slow side with the FDB-v3 mock tools → `<backend>` re-injected exactly as the released demo adapter does). Scoring: FDB-v3's own strict pass logic (`experiments/score_fdb.py`). Results: `results/p1_*`.

| condition (FDB-v3, 100 real recordings) | handoff rate | strict pass | pass given handoff |
|---|---|---|---|
| Venus-Audio, released settings | 3% | 0% | 0% |
| Venus-Audio, trigger forced at the end-of-turn slot (frontend still writes the objective) | 74% | 24% | 32% |
| Venus-Omni, trigger forced | 55% | 20% | 36% |
| slow side alone, given the human transcript | 100% | 34% | 34% |

Probes (`results/p1_*probe*`, `p1_audio_p_delegate.json`): across live-info / transaction / reasoning / routine requests, EN and ZH, Venus-Audio delegates 2/240 samples; P(`<delegate>`) at the handoff slot is 0.000–0.10 — the model announces the action ("I'll add two B-7 to your cart") and closes the turn. Venus-Omni delegates ~15% and is seed-unstable (same request → handoff / invented fact / announce-without-act).

**What the baseline taught us:** once the boundary is crossed, it is transparent (objective-writing and channel cost ≈ 0 against the transcript reference); essentially all lost capability sits in the fast model's decision to cross it, plus a reintegration loss (result not spoken after 41% / 62% of Audio / Omni handoffs). "When to delegate" is owned (SALMONN-duo knowledge-boundary SFT + cost-aware RL, Venus's own delegate benchmark, cascade/deferral literature) → not pursued as a router.

## P2 — Emerging lead: realtime interaction erodes epistemic boundaries (in progress)

Trigger failures co-occur with confident fabrication of live facts (three different NVDA prices across three samples). Question (not yet a claim): **does realtime / full-duplex interaction — as training and as a response contract — remove a model's ability to say it cannot know or cannot act?**

Probe `experiments/probes/epistemic.json`: 34 requests × EN/ZH — live info (10), private user data (8), side-effecting actions (8), answerable knowledge (8, control). Judge Qwen3-32B with an explicit label set incl. ECHO (`experiments/epistemic_eval.py`, `rejudge.py`). Results `results/epistemic/`.

Same backbone lineage (Qwen3-8B → MiniCPM-o 4.5 → Realtime-Venus):

| model / mode (text input) | live: abstain / fabricate (of 60) | private: abstain / fabricate / claim-done (of 48) | known answered |
|---|---|---|---|
| Qwen3-8B, neutral prompt | 55 / 3 | 44 / 1 / 0 | 48/48 |
| MiniCPM-o 4.5 offline (1 seed, echo excluded) | 13 / 2 (of 20) | 7 / 2 / 0 (of 16) | 16/16 |
| Venus-Audio offline (1 seed, echo excluded) | 1 / 8 (of 20) | 3 / 3 / 0 (of 16) | 16/16 |
| Venus-Audio full-duplex | **0 / 38** (+15 promise) | **2 / 12 / 12** (+19 promise) | 41/48 |

Prompt-contract decomposition on the unmodified Qwen3-8B (live fabrications of 60): neutral 3 · "reply will be spoken aloud" 3 · "on a live phone call" 11 · "live call, respond quickly" 28 · "one short sentence" 30 · "≤3 sentences" 20 · all combined 31.

Reading so far: (i) the loss is localized to the Venus realtime post-training step (parent abstains in the same mode); (ii) knowledge is retained, so this is not the known "intelligence degradation"; (iii) a pure prompt-level realtime framing already pushes an untrained model toward fabrication — brevity is owned by Phare (Giskard 2025), but live-call framing without length constraints also raises fabrication 3→11.

Nearest prior: abstention in text LLMs (AbstentionBench 2025 shows reasoning post-training hurts abstention; Phare shows brevity prompts hurt hallucination resistance). No speech/omni/full-duplex abstention study found. Reviewer compression to beat: "AbstentionBench for voice models".

Pending (next): full-duplex parent vs child; spoken-question (edge-tts) versions; Freeze-Omni (frozen LLM control) and 2–3 more speech lineages; human spot-check of the judge.


## P2-final — Epistemic-boundary loss under in-stream full-duplex interaction (analysis closed for this round, 2026-09-30)

Probe: 34 requests (live info 10, private user data 8, side-effecting actions 8, answerable knowledge 8) × EN/ZH; speech models receive edge-tts audio (2 voices), text models receive text; neutral prompts; judge Qwen3-32B (`experiments/epistemic_eval.py`), manual audit of 40 random labels: abstain-vs-not correct 39/40 (the single error inflates the text control's abstention, i.e. conservative for this finding); CLAIM_DONE vs PROMISE is noisier and is not used for conclusions. Summary: `experiments/epistemic_summary.py` → `results/epistemic/summary.json`.

| lineage | model / mode | input | live-info abstention | private-data abstention | known answered |
|---|---|---|---|---|---|
| Qwen2 | Qwen2-7B-Instruct (parent) | text | 60/60 100% | 48/48 100% | 48/48 |
| Qwen2 | Freeze-Omni — full-duplex, **LLM frozen, external state predictor (L1)** | speech | 34/40 85% | 22/30 73% | 32/32 |
| Qwen2.5 | Qwen2.5-7B-Instruct (parent) | text | 58/60 97% | 47/48 98% | 48/48 |
| Qwen2.5 | Qwen2.5-Omni-7B — speech, turn-based | speech | 34/40 85% | 31/32 97% | 32/32 |
| Qwen3 | Qwen3-8B (parent) | text | 55/60 92% | 44/48 92% | 48/48 |
| Qwen3 | MiniCPM-o 4.5 — turn-based | speech | 37/40 92% | 29/32 91% | 32/32 |
| Qwen3 | **MiniCPM-o 4.5 — same weights, in-stream full-duplex** | speech | **1/39 3%** | **3/31 10%** | 32/32 |
| Qwen3 | Realtime-Venus-Audio — turn-based | speech | 9/31 29% | 10/15 67% | 32/32 |
| Qwen3 | Realtime-Venus-Audio — in-stream full-duplex | speech | **0/38 0%** | **1/32 3%** | 31/32 |
| Qwen3 | Realtime-Venus-Omni — in-stream full-duplex | text | 9/60 15% | 10/47 21% | 48/48 |

Prompt-contract decomposition on the unmodified Qwen3-8B (live fabrications / 60): neutral 3 · "spoken aloud" 3 · "answer without hesitation" 8 · "on a live phone call" 11 · "live call, the caller is waiting right now" 18 · "respond quickly" 28 · "one short sentence" 30.

### What is established
1. **Knowledge is retained; the epistemic boundary is not.** Every condition answers the general-knowledge controls; the loss is specific to recognizing unknowable (live/private) information — distinct from the owned "intelligence degradation" of speech LLMs.
2. **Speech input alone does not cause it.** Turn-based speech models (Qwen2.5-Omni, MiniCPM-o 4.5 turn-based) and a full-duplex system whose LLM is frozen behind an external duplex controller (Freeze-Omni) keep 73–97% abstention.
3. **The in-stream full-duplex mode does, even with identical weights.** MiniCPM-o 4.5 abstains 92% turn-based and 3% in its own full-duplex streaming mode on the same audio. Further full-duplex/delegation post-training (Venus) removes abstention in duplex (0%) and propagates the erosion into the turn-based mode (29%).
4. **It connects to the computation-boundary territory.** A fast/slow system can only escalate what the fast model recognizes it cannot answer; the in-stream full-duplex fast model fabricates instead (Venus: 38/60 live facts invented, 3% natural handoff on FDB-v3). The frontier τ-Voice trajectories show the same signature in gpt-realtime-2 (21% of lookup calls use a ZIP the caller never said; cascade 2%, gpt-live-1 2%).
5. **A realtime framing effect exists without any training** (live-call framing 3→11–18/60), separable from Phare's brevity effect.

### Candidate gate — not passed yet
- clear, important question — **yes**: does realtime in-stream full-duplex interaction remove a model's epistemic boundary while leaving knowledge intact, and does that make fast-triggered escalation fail?
- empirical, emerged from baseline residency — **yes**.
- trivial explanations — speech input ✗ (ruled out), knowledge loss ✗ (ruled out), prompt wording in the text control ✗ (neutral prompts); **remaining alternative: it is one model family's duplex training data** (all in-stream full-duplex evidence is MiniCPM-o 4.5 and its child Venus).
- nearest prior — AbstentionBench (reasoning post-training hurts abstention, text), Phare (brevity), FD survey "realization gap"/data-bottleneck thesis, speech "intelligence degradation" (S2SBench etc.). None measures abstention across interaction modes of the same speech model. Reviewer compression risk: "AbstentionBench for one voice model" — **defensible only after multi-family confirmation plus a mechanism**.
- confirmation feasible — yes, on one node, with open in-stream full-duplex models that have public text parents.

**Navigation decision: CONTINUE** (object crystallizing; not registered). Kill/freeze conditions for the next block, fixed now:
- if ≥2 further independent in-stream full-duplex families (each vs its own parent/turn-based mode, neutral prompts, spoken input) show abstention within 20 pp of their parents → the effect is MiniCPM-o-family-specific → FREEZE as a model-specific note;
- if the loss appears but is fully removed by a one-line honesty instruction in the duplex prompt → it is a prompt-default artifact → demote;
- if it replicates across families, the next questions are mechanism (duplex training data coverage vs the realtime response contract; the Qwen3-8B framing result gives a training-free handle) and consequence (escalation/delegation failure rate as a function of abstention).


### P2 addendum — pre-registered demotion condition fired (2026-09-30)

Honesty instruction appended to the duplex system prompt ("…You have no internet access, no tools, and no access to the user's accounts or devices. If asked about real-time or personal information, or to perform an action, say honestly that you cannot."), spoken questions, same decoding:

| model (full-duplex) | live abstain: default → instructed | private abstain: default → instructed | known answered (instructed) |
|---|---|---|---|
| MiniCPM-o 4.5 | 1/39 → **39/40** | 3/31 → 31/32 | 32/32 |
| Realtime-Venus-Audio | 0/38 → **39/40** | 1/32 → **30/32** | 28/32 (3 over-abstain) |

The abstention capacity is intact and instruction-recoverable in both the parent and the post-trained child; what differs between modes is the **default** behaviour under each mode's trained system prompt. This is the pre-registered "prompt-default artifact" outcome → **lead demoted**. Prompt-dependence of abstention is owned (2507.16199 "LLM Abstention Can Be a Prompt Artifact"; Phare). The onset-delay mechanism test (`--delay`) was uninterpretable as implemented: forcing silence after the question mostly suppressed the reply (32/40 empty) — not rerun, since the lead is demoted.

Reusable facts kept: (i) same-weights turn-based vs full-duplex default epistemic behaviour differs by ~90 pp; (ii) live-call framing raises fabrication in an untrained text LLM; (iii) the Venus capability loss is at the handoff trigger, not the channel.
