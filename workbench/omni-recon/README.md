# Omni Reconnaissance — multi-lane pressure map (not an admitted workbench)

## 当前进度（中文，2026-09-30）

**状态：RECONNAISSANCE（三路侦察，C1 → A1 → B1 → 统一比较）。candidates = 0。**

这不是第三个 Omni workbench。它只承载：资产清单、三路（C / A / B）侦察记录、压力图、导航决定。
两个旧工作区（`realtime-agent-capability-transition`、`realtime-computation-boundaries`）的结论全部继承，不复跑、不复活：
- 语音 vs 文本的通用能力差距、电话式措辞、实体捕获 —— 已关闭；
- "该不该交接 / 委托" 的通用路由 —— 已被前作占据；
- 全双工破坏诚实性 / 弃答 —— 一句指令即可恢复，已降级关闭；
- 可复用线索（仅线索，不是论文）：**语言指令能大幅改变口头策略，但结构化动作 token 不跟着变**（Venus delegate 1/21、0/11）。

| 路线 | 问题 | 状态 |
|---|---|---|
| C 后训练能力再分配 | 语音 / 全双工后训练到底改变了哪些"功能/策略"，哪些不变？每个变化是"默认值移动"还是"能力丢失"？ | C1 运行中 |
| A 原生语音-语言-动作策略 | 原生动作通道（VoiceChat）里，说出来的话 / agent 文本 / 结构化调用 三者何时一致、何时分叉？（先排除 ASR / 实体） | VoiceChat 权重下载中，NeMo 环境搭建中 |
| B 回合内语义吸收 | 生成已经开始后，新信息如何进入当前计算？ | 待 A1 后 |

---

## 1. Asset inventory (local, not in git; `/home/xiang/rt_ext`)

**Models (`rt_ext/models`, or HF cache `~/.cache/huggingface/hub`)**

| lineage | parent (text) | intervention(s) | notes |
|---|---|---|---|
| MiniCPM-o | Qwen3-8B (cache) | MiniCPM-o 4.5 (speech/omni post-training) → same weights ordinary vs full-duplex mode → Realtime-Venus-Audio / -Omni (further 2.8M-sample realtime post-training, adapted *from MiniCPM-o 4.5*, confirmed in Venus report §4) | same-weight mode contrast + parent→child chain |
| GLM | GLM-4-9B (base; `glm-4-9b-chat-hf` sibling is local) | GLM-4-Voice-9B (speech pretrain+align, turn-based) → BayLing-Duplex (400K duplex SFT + light DPO, 4 special tokens, *from the public GLM-4-Voice checkpoint*) | cleanest post-training pair; GLM-4-Voice tokenizer re-pulled 2026-09-30 |
| Qwen2 | Qwen2-7B-Instruct (cache) | Freeze-Omni (LLM **frozen**, speech in/out + duplex state predictor) | frozen-backbone control |
| Qwen2.5 | Qwen2.5-7B-Instruct (cache) | Qwen2.5-Omni-7B (turn-based omni; text or speech input) | speech-input control without duplex |
| MiniCPM text-duplex | MiniCPM-2B-sft-bf16 | MiniCPM-duplex (THUNLP time-sliced text duplex; ordinary vs duplex session on same weights) | duplex training with **no speech at all** |
| Nemotron | Nemotron-Nano-9B-v2-Base (cache) | NemotronLabs VoiceChat 11B (CPT+SFT, parallel agent-text / function-call heads, RNN-T user transcript) | downloading (44 GB) |
| other | — | Lychee-FD (12 MB: adapters only), DuplexCascade (gated, not accepted) | |

Judge/backends: Qwen3-32B, Qwen3-30B-A3B, Qwen3.5-*, Qwen2.5-32B-Instruct in HF cache; vLLM 0.11 in `verl-clean`.

**Data / harness**: τ-Voice public trajectories (~20 GB, `rt_ext/data`), FDB-v3 real-human audio + mock tools (`rt_ext/Full-Duplex-Bench/v3`), edge-tts probe audio (`rt_ext/runs/epi_audio`, `rt_ext/runs/battery_audio`), Venus FDB driver + forced-delegation + slow backend, all epistemic probe drivers (now env-configurable: `AUD`, `LANGS`, `NOJUDGE`) in `../realtime-computation-boundaries/experiments/`.

**Code clones**: BayLing-Duplex, GLM-4-Voice, Freeze-Omni, duplex-model (MiniCPM-duplex), Realtime-Venus, Lychee-FD, DuplexCascade, Full-Duplex-Bench, tau2-bench, qwen-audio-agent, nemo-speech-voicechat (offline FC inference: `examples/speechlm2/offline_voicechat_fc_infer.py`; docker not usable — no daemon permission).

**Commercial**: a StepFun API key is available (stored outside the repo). StepFun authored DuplexSLA; usable as a frontier closed reference if a lane needs one.

## 2. Frontier patch (read 2026-09-30; what each already owns)

| paper | owns | implication |
|---|---|---|
| AdaptDuplex (2609.29217, Qwen3-Omni) | adaptive window duration; every behavioural decision an explicit token; logits-bias runtime control; non-blocking memory consolidation; ≤4 in-flight external requests; Thinker curriculum + Talker SFT + GRPO | adaptive compute / fast-slow / behaviour-token steering are **not** novelty |
| DuplexSLA (2605.20755, StepFun; weights not released) | user-audio / assistant-audio / rate-limited action channel on a 160 ms clock; planning + tool calls in-stream; DuplexSLA-Bench | reported: native action acc 85.6% vs ASR+LLM cascade 91.3%, **multi-action 75.0% vs 89.3%**, single 85.7 vs 89.3, backchannel-triggered 96 vs 95; 4× lower delay. The native-vs-cascade gap concentrates on multi-action composition (their own table; not analysed by them) |
| NemotronLabs VoiceChat (2609.21967) | open 11B FD model; parallel agent-text head + function head (fusion weights 1/1/2), RNN-T transcript branch from the shared encoder (not fed to the LLM); FDB-v3 tool-sel F1 82.5 / arg acc 42.2 / pass 33.0 | the arg-vs-selection gap is their headline, not ours. Limitations section: answers from internal knowledge when a tool should be called; invented arguments; ≤5 tools |
| Duplex Cue (2609.13117) | continue / adapt / yield taxonomy; 300 human-confirmed cues; PersonaPlex adapts 34.8% vs humans 68.2% on collaborative cues | corpus requires authorised access ("requires authorized artifacts"); benchmark expansion is an obvious follow-up (forbidden) |
| EchoChain (2604.16456) | state-update under mid-speech interruption; contextual inertia / interruption amnesia / objective displacement; half-duplex control flips 40% of failures | closed models only; generic stale-state is owned |
| State Inertia (2606.11386, MIT) | logit-lens: FD-SLM hidden states switch between "generative" and "perceptive" prediction; lag at interruption = state inertia; Zero-Buffer Benchmark; perception-vector steering (PersonaPlex 28→45%) | the obvious mechanism story for Lane B ("model is deaf while speaking") is owned |
| DuplexPO (2607.07148) | RL on dynamic-critical windows; timing optimised without QA/IF/reasoning loss | timing and semantics are separable by training |
| BayLing-Duplex (2606.14528) | duplex vs **turn-based SFT on the same data** → no broad quality loss (Llama Q 44.3 vs 45.3; Web Q 18.0 vs 15.9) | NB: it never compares against the GLM-4-Voice **checkpoint itself**; the same-data control isolates "duplex format", not "post-training" |
| Decoupling turn-taking from semantics (2609.03321), Same Words Different Actions (2609.17360), When Patients Cut In (2608.29241) | FSM decoupled data; paired turn-taking contexts; clinical interruption safety | turn-taking evaluation is saturated |

## 3. C1 — post-training redistribution (interim, 2026-09-30 17:10)

Battery: `probes/battery.json`, 122 English items over 9 axes (know, math, format, rule, premise, syco, clarify, harm,
benign); math / premise / syco / clarify each have a variant with a one-sentence spoken instruction in the request
itself (`*_i`), so "default moved" vs "capability lost" can be separated without touching system prompts. Spoken
versions via edge-tts (2 voices = 2 seeds). Generations with `NOJUDGE=1`, labels by `experiments/battery_judge.py`
(Qwen3-32B). Raw labelled runs: `results/c1/`.

Good-label counts (out of 20 unless noted; know 24, rule 16, harm/benign 12):

| config | know | math | math_i | format | rule | premise | syco | clarify | clarify_i | harm | benign |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Qwen3-8B text | 24 | 20 | 12* | 20 | 16 | 20 | 20 | 19 | 19 | 12 | 12 |
| MiniCPM-o 4.5 offline, speech in | 24 | 20 | 20 | 20 | 16 | 20 | 20 | 20 | 20 | 12 | 12 |
| MiniCPM-o 4.5 **duplex**, speech in (same weights) | 24 | 12 | 13 | 15 | 13 | 20 | 20 | **4** | **18** | 11 | 11 |
| Realtime-Venus-Audio duplex | 24 | 11 (7 no-answer) | 11 | 14 | 14 | 20 | 20 | **6** | **19** | 11 | 12 |
| Qwen2-7B-Instruct text | 24 | 19 | 17 | 18 | 14 | 20 | 20 | 15 | 19 | 12 | 12 |
| Qwen2.5-Omni text in | 24 | 12 | 14 | 9 | 14 | 20 | 20 | 20 | 20 | 12 | 12 |
| Qwen2.5-Omni speech in | 24 | 12 | 10 | 9 | 15 | 19 | 20 | 18 | 19 | 12 | 12 |

\* Qwen3-8B `math_i` losses are truncation at 256 tokens when asked to reason aloud.

First reading (pressure map, not claims):
- **Ceiling axes** (know, premise, syco, harm): no model/mode moves; the battery is too easy there to see redistribution.
- **Clarification collapses in full-duplex mode on the same weights** (MiniCPM-o 20/20 → 4/20; Venus 6/20; the
  model invents a referent and answers), and **one spoken sentence restores it** (18/20, 19/20). Same shape as the
  demoted abstention lead → default-policy class, not a capability loss. Control running: system prompts swapped
  between modes (duplex's default prompt is "Streaming Omni Conversation.", offline's "You are a helpful assistant.").
- **Math / format drop in duplex mode and are *not* restored by instruction** (math 12→13); but Qwen2.5-Omni shows the
  same math/format drop with **text** input, so part of this is Omni post-training, not duplexity. Decoding differs
  (duplex = sampled 20-token chunks; offline = greedy) — confound to control before reading anything into it.
- Venus's math "no-answer" cases are announce-then-silence ("Let me calculate it step by step." then nothing, no
  `<delegate>`) — the verbal-promise-without-action pattern from P3 again.

### C1 controls (2026-09-30 17:40) — the clarification lead dies

| MiniCPM-o 4.5 | clarify | clarify_i | math | format |
|---|---|---|---|---|
| duplex, default prompt "Streaming Omni Conversation." | 4 | 18 | 12 | 15 |
| duplex, prompt "You are a helpful assistant." | **18** | 16 | **16** | 14 |
| offline, prompt "Streaming Omni Conversation." | 18 | 19 | 20 | 20 |
| offline, sampled decoding (T=0.7) | 19 | 20 | 20 | 20 |

- The duplex "clarification collapse" is a **system-prompt artifact** (default duplex prompt). Killed. Second consecutive
  demotion of a default-policy lead in this family (abstention → clarification) ⇒ two-demotion reset for this axis.
- Sampling does not explain the math drop; the remaining duplex math/format gap (16/20, 14/20) is small.
- Other lineages: BayLing-Duplex collapses on math (0/20), rule games (2/16), format (5/20); Freeze-Omni (frozen LLM)
  keeps math (19/20). These are properties of individual checkpoints, not of an intervention; GLM-4-Voice parent pending.

**Navigation (user correction, 2026-09-30):** C1 as run is a per-model capability/default probe — exactly the kind of
object that is model-specific and prompt-fragile. Lane C is demoted to dormant. Remaining recon must look for
properties of the *formulation / design space* that hold across systems (e.g. how a streaming model commits to
content before evidence is complete; native action head vs serialized action channel vs cascade), not quirks of one
checkpoint, and must widen beyond the three pre-planned lanes before any deep dive.

## 4. Field-level scan (desk, 2026-09-30 evening) — widening beyond A/B/C

Question asked of each strand: *is there a property of the formulation that holds across systems, with open
artifacts, that strong 2026 work has not already compressed?*

| strand | 2026 state | ownership / verdict |
|---|---|---|
| Native vs cascade — what does end-to-end buy? | Interleaved SLMs *latently transcribe* to text in mid layers (2606.22473); cascades beat open SLMs multilingually (2609.33204), DuplexCascade ≈ strong on VoiceBench, DuplexSLA cascade > native on tool accuracy; frozen-backbone S2S (PRIME-Speech 2606.30944, Freeze-Omni, training-free omni with frozen VLMs 2609.04242) preserve capability | the "listen vs read / perception-behaviour gap" is heavily owned (Do Audio LLMs Listen or Read? ICML'26; Real-Time Voice AI Hears but Does Not Listen 2606.26083; ParaBridge 2606.10581 — a one-line scaffold exposes latent paralinguistic use; Hear2Act 2608.19515). Not ours. |
| Paralinguistic behaviour | benchmarks + scaffolds + alignment | owned (and on the user's low-value list) |
| Audio-visual temporal reasoning | AVTrace 2609.19991: all open omni models below majority baseline on sync verification | benchmark-shaped; video-temporal already has its own workbench |
| Speech RL / reward models | GSRM, dual-axis RMs, DuplexPO, SteerDuplex; reward hacking via incomplete responses | method-shaped, crowded |
| **Commitment under incremental evidence** | the same pressure appears in four sub-fields that do not cite each other: full-duplex speech (speak before the user finishes; revise after barge-in: EchoChain, State Inertia, Duplex Cue), streaming video (answer before evidence → hallucination; readiness gates: Response-G1, LiveProBench 2609.12658), simultaneous translation (append-only commit rules vs re-translation: IWSLT'26, 2609.26427), realtime agents (act before arguments are complete: DuplexSLA "trigger time legal") | each sub-field owns its local version; nobody measures *when an LLM-based streaming generator stops being able to revise what it has started* as a property of the formulation across architectures. B1 is the first probe of this. Classical SiMT (wait-k etc.) is the strongest compression risk. |
| Native action formulation | parallel function head (VoiceChat) vs serialized action channel (DuplexSLA) vs cascade; DuplexSLA's own table: native loses 14 pp on multi-action vs cascade, 4 pp on single | formulation-level, open artifact (VoiceChat) — A1 |

## 5. B1 — the same correction at different phases of the model's own speech (2026-09-30 night)

`probes/update.json`: 20 "tell me about X" requests + a spoken correction "sorry, I meant Y" (edge-tts, 2 voices);
correction delivered right after the question (pre) or 1 / 3 / 6 s after the model's speech onset (detected online).
Driver `experiments/b1_update_phase.py` (MiniCPM-o-family duplex), `experiments/b1_bayling.py`; labels `b1_judge.py`.

| model | pre | +1 s | +3 s | +6 s |
|---|---|---|---|---|
| MiniCPM-o 4.5 duplex (ADAPT / 40) | 34 | 33 | 38 | 38 |
| Realtime-Venus-Audio duplex | 34 | 33 | 40 | 39 |

**Null (a success case):** in-stream full-duplex models yield and re-answer about the new topic at every phase
(85–100%); no revision window, no contextual inertia on simple topic swaps. The single-item smoke pattern
(adapt / stop / continue by phase) was noise. What EchoChain reports for closed models is therefore about
*state-dependent* updates (multi-step blueprints), not about incorporating a correction mid-speech per se.
BayLing run incomplete (its early pre-condition outputs are mostly CONFUSED, 8/12).

## 6. Latent transcription in deployed speech-LLMs (the reframed "listen vs read" strand)

`experiments/latent_transcript_minicpmo.py`: logit lens (final norm + lm_head) on the AUDIO positions only, offline
chat, 60 battery clips with known transcripts; recall@10 of the utterance's content words vs a randomly paired
utterance's words (chance).

| layer | 0 | 8 | 12 | 20 | 24 | 28 | 32 | 34 | 35 | 36 (last) |
|---|---|---|---|---|---|---|---|---|---|---|
| MiniCPM-o 4.5 recall | .10 | .29 | .48 | .41 | .59 | .75 | .89 | .91 | .92 | .72 |
| Realtime-Venus-Audio recall | .11 | .29 | .47 | .42 | .60 | .77 | .90 | .93 | .95 | .79 |
| control (other utterance) | .10 | .06 | .06 | .07 | .07 | .07 | .08 | .10 | .14 | .12 |

- Deployed continuous-encoder speech-LLMs (Whisper features → Qwen3-8B) **latently transcribe almost every content
  word** (92–95% at layers 33–35), much stronger than the 77% reported for 3B discrete-unit interleaved SLMs
  (2606.22473), and with a two-phase profile (a mid-layer bump at ~12–18, a dip at ~20, then a late rise), not a
  mid-layer peak.
- In full-duplex streaming (`latent_latency_duplex.py`, forced listening, 1 s units), 97% of content words become
  decodable, median latency 0 units after the word's acoustic end (negative = decodable before the word finishes);
  the internal transcript keeps pace with the audio. Latency is not a bottleneck here.
- Open: is behaviour a function of this internal transcript (an "implicit cascade"), and where do native errors
  come from — a wrong latent transcript (perception) or a right transcript that is not used (policy)? A1 (VoiceChat
  native tool arguments vs its latent transcript on FDB-v3 real speech) is the test bed.
