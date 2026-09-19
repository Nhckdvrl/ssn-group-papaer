# Industry Source Ledger — 2026-09-19

> **Purpose:** provenance and evidence-quality control for the industry research track.
>
> Window: primarily June–September 2026.
>
> This ledger is not a ranking of companies and not a list of candidate topics.
>
> For every industry artifact we record:
>
> - **Artifact type**
> - **Evidence tier**
> - **Deep-read status**
> - **What it actually establishes**
> - **What it does NOT establish**
> - **Research-taste value**
> - **Execution transferability**
>
> Ratings:
>
> - Research-taste value: A / B / C
> - Execution transferability: A / B / C / D / F
>
> These ratings are internal project-management judgments, not quality rankings of the papers/models.

---

# Evidence tiers

## Tier I — production telemetry / real traces
Strongest for:
- workload distribution;
- operational bottlenecks;
- reuse patterns;
- real intervention structure.

Weak for:
- causal mechanisms.

## Tier II — technical report / model card with controlled evidence
Strongest for:
- architecture/training regime;
- changed premise;
- expensive controlled evidence.

Weak for:
- recipe disentanglement.

## Tier III — engineering report / production systems paper
Strongest for:
- proxy-vs-real-bottleneck;
- deployment constraints;
- end-to-end resource accounting.

## Tier IV — launch/product/partner material
Useful only for:
- frontier direction discovery;
- product knobs;
- finding better primary material.

Not sufficient for mechanism claims.

---

# A. OpenAI

## OA-01 — GPT-5.6 frontier intelligence / efficiency engineering
Date: 2026-07-29  
Type: engineering report  
Tier: III  
URL: https://openai.com/index/gpt-5-6-frontier-intelligence-efficiency/

Deep-read: **YES**

Actually establishes:
- end-to-end agent cost is model × serving × harness;
- repeated per-call overhead compounds over multi-request agent loops;
- prompt prefix stability / tool layout / caching matter operationally;
- AI agents are used to search serving configurations, kernels, and speculative decoding experiments.

Does NOT establish:
- a universal law for all agent systems;
- that any one harness choice improves model-intrinsic reasoning.

Taste value: **A**  
Execution transfer: **B/C**

Core pressure:
> semantic-equivalent context layouts can have very different execution economics.

---

## OA-02 — GPT-Live System Card
Date: 2026-07-08  
Type: system card  
Tier: II  
URL: https://deploymentsafety.openai.com/gpt-live

Deep-read: **YES**

Actually establishes:
- new voice models are full duplex;
- model continuously decides whether to listen/respond;
- complex work may be delegated to deeper models.

Does NOT establish:
- detailed training architecture;
- causal reason for every latency/interaction improvement.

Taste value: **A**  
Execution transfer: **C**

Core pressure:
> turn boundary is no longer a prerequisite for inference.

---

## OA-03 — Continuous Voice Interaction engineering
Date: 2026-08-03  
Type: production engineering  
Tier: III  
URL: https://openai.com/index/continuous-voice-interaction-with-gpt-live/

Deep-read: **YES**

Actually establishes:
- external turn detector removed from live audio path;
- separate low-latency media path and asynchronous deep-reasoning path;
- prefilled/affinitized frontier sessions reduce delegation latency;
- context compaction invalidates KV and requires seamless state handoff;
- continuous internal stream still requires downstream discrete message reconstruction.

Does NOT establish:
- one universal architecture for all full-duplex systems.

Taste value: **A**  
Execution transfer: **B/C**

Core pressure:
> control-time representation and downstream logging representation can legitimately use different event boundaries.

---

## OA-04 — GPT-Live-1 API
Date: 2026-09-10  
Type: product/system release  
Tier: III/IV  
URL: https://openai.com/index/introducing-gpt-live-1-in-the-api/

Deep-read: **YES**

Actually establishes:
- full-duplex model can be paired with different backend models/tools/harnesses;
- realtime controller and deep-reasoning backend can be independently selected;
- explicit turn boundaries remain optionally supported.

Does NOT establish:
- that multi-model delegation is always optimal;
- causal reason for benchmark differences.

Taste value: **B+**  
Execution transfer: **B**

---

## OA-05 — GPT-6 Astra System Card
Date: 2026-09-03  
Type: system card / controlled evaluation  
Tier: II  
URL: https://deploymentsafety.openai.com/gpt-6-astra

Deep-read: **YES**

Actually establishes:
- substantially greater controllability of CoT properties than earlier reasoning models;
- CoT-only monitorability can worsen even as capabilities increase;
- CoT controllability increases during RL;
- evaluation awareness / metagaming is behaviorally measurable.

Does NOT establish:
- a complete mechanistic cause;
- that architecture has no role in all settings.

Taste value: **A**  
Execution transfer: **B**

Core pressure:
> stronger reasoning and more observable/monitorable reasoning are not monotonic.

---

## OA-06 — Internal research acceleration
Date: 2026-09-06  
Type: internal-usage telemetry / research-process report  
Tier: I/III  
URL: https://openai.com/index/research-acceleration-view-inside-openai/

Deep-read: **YES**

Actually establishes:
- agent use is uneven across research stages;
- implementation/running can automate faster than prioritization/judgment;
- long tasks still receive interventions.

Does NOT establish:
- general productivity multiplier across labs;
- autonomous scientific taste.

Taste value: **A**  
Execution transfer: **C**

---

## OA-07 — GPT-Rosalind capabilities
Date: 2026-06-03  
Type: research/product evaluation report  
Tier: II/III  
URL: https://openai.com/index/introducing-new-capabilities-to-gpt-rosalind/

Deep-read: **YES (workflow-level)**

Actually establishes:
- scientific-agent evaluation increasingly uses executed workflows, protocols, tools, and efficiency jointly.

Does NOT establish:
- model-intrinsic scientific capability independent of harness.

Taste value: **B+**  
Execution transfer: **C**

---

# B. Anthropic

## AN-01 — Claude Sonnet 5 launch + methodology correction
Date: 2026-06-30  
Type: model release / evaluation methodology  
Tier: II/IV  
URL: official Anthropic Sonnet 5 release

Deep-read: **YES**

Actually establishes:
- Anthropic's standard agentic BrowseComp methodology used a 10M-token total budget, context compaction, and programmatic tool calling;
- a simpler methodology initially produced a comparison Anthropic later corrected.

Does NOT establish:
- model-intrinsic performance independent of the harness.

Taste value: **A-**  
Execution transfer: **A/B**

Core pressure:
> agent benchmark score is a model × budget × context policy × tool-interface quantity.

---

## AN-02 — Claude Fable 5.1 / Mythos 5.1
Date: 2026-09-01  
Type: model/system release  
Tier: II/IV  
URL: https://www.anthropic.com/claude-fable-and-mythos-5-1

Deep-read: **YES**

Actually establishes:
- cache reads repriced 75% lower;
- four weeks of actual August usage show cache reads form enough of cost that highly agentic/context-heavy workloads benefit much more;
- same underlying model can be deployed under different safeguard/access configurations.

Does NOT establish:
- a causal law of cache reuse;
- general performance effect of different safeguards.

Taste value: **A- for systems economics / B for model science**  
Execution transfer: **B**

Core pressure:
> reused/persistent context is an economically separate resource class.

---

## AN-03 — September 2026 frontier-lab measurement report
Date: 2026-09-17  
Type: internal telemetry / methodology report  
Tier: I  
URL: https://www.anthropic.com/institute/measuring-pace-of-ai-development

Deep-read: **YES**

Actually establishes:
- bottom-up task taxonomy (~15k sampled granular tasks; 542-node hierarchy);
- Claude leads 26% of measured internal AI R&D tasks as of Aug 2026; >90% at least collaborates;
- ~30k agents active at a time on a major internal platform;
- online/offline oversight coverage and escalation rates;
- persistent agent identity and open inter-agent communication are operational design variables.

Does NOT establish:
- autonomous AI R&D;
- cross-lab comparable productivity without common methodology.

Taste value: **A**  
Execution transfer: **C/D**

Core pressure:
> as experiment production scales, selection/oversight/interpretation become scarce resources.

---

## AN-04 — Anthropic system-card archive
Date: continuously updated through Sep 2026  
Type: system-card lineage  
Tier: II  
URL: https://www.anthropic.com/system-cards

Deep-read: **PARTIAL / INDEXED**

Value:
- enables longitudinal comparison of evaluation categories and deployment assumptions.

Taste value: **B**  
Execution transfer: **B**

---

# C. Google DeepMind

## GD-01 — Gemini 3.8 Flash model card
Date: 2026-09-02  
Type: model card  
Tier: II  
URL: https://deepmind.google/models/model-cards/gemini-3-8-flash/

Deep-read: **YES**

Actually establishes:
- customizable effort is a first-class quality/cost/latency control.

Does NOT establish:
- implementation semantics of effort;
- exact internal computation controlled.

Taste value: **B+**  
Execution transfer: **B**

---

## GD-02 — Gemini 3.8 Audio model card
Date: 2026-09-15  
Type: model card  
Tier: II  
URL: https://deepmind.google/models/model-cards/gemini-3-8-audio/

Deep-read: **YES**

Actually establishes:
- separate Live and Live Extended Thinking variants;
- continuous audio/image/video/text inputs;
- realtime interaction and deeper thinking coexist as explicit modes.

Does NOT establish:
- detailed architecture for the split;
- general fast/slow control law.

Taste value: **A-**  
Execution transfer: **C**

---

## GD-03 — Agentic video in Gemini
Date: 2026-09-01  
Type: research/product report  
Tier: III  
URL: first-party Google/DeepMind agentic-video release

Deep-read: **YES**

Actually establishes:
- model can actively request frames/audio/transcript/time regions instead of consuming a fixed stream;
- reported reduction in token/cost with quality gains.

Does NOT establish:
- novelty of active perception as a scientific concept;
- universality across tasks.

Taste value: **A**  
Execution transfer: **A/B**

Core pressure:
> video understanding can be an information-acquisition policy, not only encoding.

---

## GD-04 — Gemini Robotics On-Device 2 model card
Date: 2026-07-30  
Type: model card  
Tier: II  
URL: https://deepmind.google/models/model-cards/gemini-robotics-on-device-2/

Deep-read: **YES**

Actually establishes:
- on-device VLA across multiple robot types;
- post-training on novel embodiments shows much better learning curves than previous version;
- outputs numerical robot actions;
- OOD/high-DOF limitations remain;
- layered safety architecture separates high-level semantic reasoning from low-level control.

Does NOT establish:
- the exact representation/mechanism enabling faster embodiment adaptation.

Taste value: **A-**  
Execution transfer: **C/D**

Core pressure:
> embodiment adaptation speed is becoming a first-class capability, not just final success.

---

# D. DeepSeek

## DS-01 — DeepSeek-V4.1-Flash technical report
Date: 2026-09-17  
Type: technical report  
Tier: II  
URL: https://arxiv.org/abs/2609.19969

Deep-read: **YES**

Actually establishes:
- long-horizon agent workload is increasingly input-heavy;
- CED uses asymmetric input/output active compute;
- cache compression operates across entry/sequence/layer axes;
- global/local cache components have different lifetimes;
- bounded approximate replay is explicitly post-trained;
- post-training reportedly adds no new RL algorithm but scales environment/data generation and heterogeneous scaffolds;
- massive async sandbox infrastructure is a frontier constraint.

Does NOT establish:
- causal attribution of overall model quality to one component;
- feasibility at small academic scale.

Taste value: **A**  
Execution transfer: **C–F depending subproblem**

---

# E. Alibaba / Qwen

## QW-01 — Qwen-AgentWorld technical report + official repo
Date: 2026-06-24  
Type: technical report / open model  
Tier: II  
URL: https://arxiv.org/abs/2606.24597  
Repo: https://github.com/QwenLM/Qwen-AgentWorld

Deep-read: **YES**

Actually establishes:
- environment/world modeling is trained from CPT onward;
- >10M interaction trajectories;
- seven unified agent domains;
- controllable simulation;
- fictional self-consistent worlds;
- simulation quality/control materially affects downstream RL;
- world-model warm-up transfers to agent tasks including OOD.

Does NOT establish:
- that learned world models dominate real environments universally;
- low-cost replicability.

Taste value: **A**  
Execution transfer: **C/D**

Core pressure:
> environment itself can be a learned foundation model; simulator usefulness depends on the learning pressure it induces, not only realism.

---

# F. Microsoft Research

## MS-01 — Agentic Coding in the Wild
Date: 2026-07  
Type: production telemetry  
Tier: I  
URL: Microsoft Research publication page

Deep-read: **YES**

Evidence:
- 3.2M users;
- 13M sessions;
- 761M LLM calls;
- 95T tokens;
- nearly 1:1 LLM-call/tool-execution coupling;
- ~90% cache hit within turn vs ~55% across turns;
- long-tailed session workloads;
- predictable human idle time.

Taste value: **A**  
Execution transfer: **B/C**

---

## MS-02 — Murakkab (OSDI 2026)
Date: 2026-07  
Type: systems paper  
Tier: III  
Deep-read: **YES**

Actually establishes:
- opaque model/tool sequences hide optimization structure;
- declarative workflow representation enables cross-layer resource optimization.

Taste value: **A-**  
Execution transfer: **C**

---

## MS-03 — OpScale
Date: 2026-08  
Type: systems paper  
Tier: III  
Deep-read: **YES**

Actually establishes:
- operator heterogeneity is large enough that whole-model autoscaling is overly coarse;
- finer granularity gives measurable resource gains.

Taste value: **A**  
Execution transfer: **C/D**

Core research move:
> first prove heterogeneity, then justify changing the scaling unit.

---

## MS-04 — Beyond Prediction (ICML 2026)
Date: 2026-06  
Type: academic/industry systems paper  
Tier: III  
Deep-read: **YES**

Actually establishes:
- perfect decode-length oracle still does not solve tail latency under realistic workload dynamics;
- the assumed bottleneck (prediction accuracy) is not the real bottleneck.

Taste value: **A**  
Execution transfer: **B/C**

Excellent genealogy example:
> oracle removes presumed confound → failure persists → reframe objective.

---

## MS-05 — PowerSlider
Date: 2026-08  
Type: systems paper  
Tier: III  
Deep-read: **YES (conceptual)**

Actually establishes:
- reasoning serving has physically distinct prefill/think/answer phases under power constraints.

Taste value: **A-**  
Execution transfer: **D**

---

## MS-06 — Fara-1.5
Date: 2026-06  
Type: technical research report / open agents  
Tier: II  
URL: https://arxiv.org/abs/2606.20785

Deep-read: **YES**

Actually establishes:
- scalable environment→solver→verifier data pipeline;
- live + synthetic environments;
- multiple model solvers;
- correctness/efficiency/critical-point verifiers;
- iterative data balancing around model deficiencies;
- 4B/9B/27B open models.

Does NOT establish:
- environment quantity alone as the causal factor.

Taste value: **B+/A-**  
Execution transfer: **B/C**

---

## MS-07 — Echoverse
Date: 2026-07  
Type: agent environment research  
Tier: II/III  
Deep-read: **YES**

Actually establishes:
- shallow synthetic environments can hurt live-site performance;
- deeper/learner-targeted/evolving environments improve transfer;
- environment generation becomes learner-relative.

Taste value: **A**  
Execution transfer: **B/C**

---

## MS-08 — Privileged, but Biased
Date: 2026-08-05  
Type: academic-style industrial research  
Tier: II  
URL: https://arxiv.org/abs/2608.04794

Deep-read: **YES — PDF + mechanism chain**

Actually establishes:
- self-distillation easy-regime gains do not survive harder regimes under same objective;
- PI-conditioned teacher target is biased toward one reference path;
- loss is weakly coupled to correctness;
- low-information tokens absorb much optimization;
- correct exploratory deviations are penalized.

Taste value: **A+**  
Execution transfer: **A/B**

This is currently one of the best recent industrial papers for our actual project taste:
> intellectually sharp but not frontier-scale-dependent.

---

# G. ByteDance Seed

## BD-01 — Seed2.0 Model Card
Date: 2026-06-30  
Type: model card  
Tier: II/IV  
URL: https://arxiv.org/abs/2607.00248

Deep-read: **PARTIAL**

Actually establishes / frames:
- evaluation is built around real-user needs and complex real-world scenarios;
- focus on long-tail knowledge and complex instruction following;
- hundreds-of-millions-user deployment motivates evaluation abstraction.

Does NOT establish:
- clean causal mechanism;
- whether benchmark abstractions are optimal.

Taste value: **B**  
Execution transfer: **B**

---

## BD-02 — Seed2.1 real-workflow release
Date: 2026-06-23  
Type: production/model release  
Tier: IV with internal-workflow evidence  
Deep-read: **YES**

Useful signal:
- internal/external feedback calibrates model iteration;
- evaluation emphasizes actual workflows;
- “Seed for Seed” uses agents in eval/data/training/research/infra tasks.

Taste value: **B**  
Execution transfer: **C**

---

## BD-03 — EdgeBench
Date: 2026-07-06  
Type: large empirical research benchmark/scaling study  
Tier: II/I-like long-run evidence  
URL: https://arxiv.org/abs/2607.05155

Deep-read: **YES — PDF + screenshots**

Evidence:
- ~38k hours;
- 134 tasks;
- ≥12h/task;
- mean human expert effort 57.2h;
- two feedback loops: fast local + slower authoritative judge;
- aggregate environment learning follows log-sigmoid with mean R²≈0.998;
- early 6.5h can forecast later 12h aggregate curves with high fit;
- newer frontier models show faster learning speed;
- accumulated experience matters beyond independent restarts/submission count.

Taste value: **A**  
Execution transfer: **D/F for replication, B for conceptual small proxies**

Core changed object:
> static benchmark capability → learning dynamics under endogenous interaction and feedback.

---

## BD-04 — Sample-Efficient Learning from Agent Experience
Date: 2026-07-23  
Type: academic-style industry/collaboration research  
Tier: II  
URL: https://arxiv.org/abs/2607.21051

Deep-read: **ABSTRACT/RELATED POSITIONING; NEED FULL PDF IF USED FOR CANDIDATE**

Actually establishes:
- in-context experience gains vanish when context disappears;
- context distillation can internalize interaction experience with no additional environment samples;
- reported ≥64.8% retention of ICL gains vs 3.8% direct SFT;
- ≥9.6× fewer environment samples than classical RL baselines in tested settings.

Taste value: **A-**  
Execution transfer: **A/B**

Core question-forming move:
> experience is expensive; distinguish “acquire experience” from “internalize experience.”

---

## BD-05 — SeedRealtime
Date: 2026-08-05  
Type: product/research release  
Tier: III/IV  
Deep-read: **YES**

Actually establishes:
- continuous audio/video/text;
- proactive speak/silent decision;
- event-triggered interaction.

Does NOT establish:
- detailed training mechanism.

Taste value: **A-**  
Execution transfer: **C/D**

---

# H. NVIDIA

## NV-01 — Nemotron 3.5 Lightning + Switchyard
Date: 2026-08-11  
Type: technical/product release  
Tier: III/IV  
Deep-read: **YES**

Actually establishes:
- role-specialized cheap execution model + frontier planner routing is a production design;
- routing logic can be separate from provider/model endpoints.

Taste value: **B+**  
Execution transfer: **B/C**

---

## NV-02 — QAD for Nemotron 3.5 Lightning NVFP4
Date: 2026-08-17  
Type: technical engineering report  
Tier: III  
URL: NVIDIA technical blog

Deep-read: **YES**

Actually establishes:
- aggressive PTQ creates accuracy loss;
- frozen BF16 teacher can restore quantized student through KL distillation;
- quantization constraints are made part of the learning problem.

Reported:
- 66GB → 22GB;
- up to ~4× throughput in NVIDIA's tested setup.

Does NOT establish:
- universal throughput gain across hardware/workloads.

Taste value: **B+/A-**  
Execution transfer: **B**

Core pressure:
> deployment representation constraint (low precision) can be treated as student mismatch rather than only numerical error.

---

# I. Mistral

## MI-01 — Robostral Navigate
Date: 2026-07  
Type: industrial technical report  
Tier: II  
URL: https://arxiv.org/abs/2607.20785

Deep-read: **YES (conceptual + reported system details)**

Actually establishes:
- monocular RGB navigation without depth/LiDAR;
- image-space pointing reduces embodiment-specific high-level output dependencies;
- whole-episode packing + causal/tree masking greatly reduces training token cost;
- heavy simulation/trajectory data remains required.

Taste value: **A-**  
Execution transfer: **C/D**

Core pressure:
> output representation can deliberately factor out embodiment-specific coordinates.

---

# J. Lower-priority / monitor-only artifacts

## X-01 — Grok 4.6
Recent frontier release with:
- ~500k context;
- configurable reasoning effort;
- long-running agents.

Evidence tier: IV  
Deep-read: product-level only  
Taste value: C/B  
Execution transfer: B

Reason:
> little public technical mechanism; useful as convergence evidence for effort/context controls, not as primary research source.

## X-02 — generic company benchmark blogs
Evidence tier: IV  
Default action:
> do not use as positive taste unless they expose a changed evaluation/deployment variable.

---

# Current source-balance audit

Deep industrial sources now cover:

### Model/system cards
- OpenAI GPT-Live
- OpenAI GPT-6 Astra
- Gemini 3.8 Flash
- Gemini 3.8 Audio
- Gemini Robotics On-Device 2
- Anthropic Sonnet/Fable/Mythos
- Seed2.0

### Production traces
- GitHub Copilot
- OpenAI internal research agents
- Anthropic internal R&D agents

### Architecture/training technical reports
- DeepSeek V4.1
- Qwen-AgentWorld
- Fara1.5
- Robostral

### Industrial academic-style mechanism papers
- Privileged, but Biased
- Beyond Prediction
- OpScale
- EdgeBench
- Sample-Efficient Agent Experience

### Real-time / multimodal systems
- GPT-Live
- Gemini Audio
- SeedRealtime
- agentic video
- on-device robotics

### Serving/system co-design
- GPT-5.6 engineering
- Murakkab
- OpScale
- PowerSlider
- NVIDIA QAD/Switchyard

This is now broad enough that future industry inspiration should not default to:
> “frontier LLM reasoning”.

---

# Hard provenance rule

Before any industry-derived formal candidate:
1. return to primary artifact;
2. if PDF, read full relevant sections, not abstract only;
3. mark which claims are:
   - direct measured evidence;
   - company's interpretation;
   - our reconstruction;
4. locate public academic nearest prior;
5. run Scale-Stripping / Cheap-Causal-Echo tests.

If the source is Tier IV only:
> it cannot be the sole origin of a formal candidate.
