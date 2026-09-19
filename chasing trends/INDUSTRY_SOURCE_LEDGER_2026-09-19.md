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


---

# K. Startup / Hugging Face frontier sources — added 2026-09-19

This section extends the industry ledger beyond major frontier-model incumbents.

Additional axis:

## Instrument value
How useful is the release as a low-cost experimental contrast?

- **A**: matched checkpoints / clean intervention pairs / small enough to run.
- **B**: useful open artifact but heavier/confounded.
- **C**: mostly inspiration.
- **F**: no practical experimental access.

---

## ST-01 — Thinking Machines Inkling
Date: 2026-07-15  
Type: open-weight model + first-party technical release  
Tier: II  
Primary:
- https://thinkingmachines.ai/news/introducing-inkling/
- Hugging Face Inkling model card

Deep-read: **YES**

Actually establishes:
- 975B total / 41B active MoE;
- large-scale RL >30M rollouts;
- effort is trained via system-message conditioning + per-token cost;
- performance is evaluated as an effort/token frontier, not one score;
- RL induces more telegraphic CoT without an explicit language-style reward.

Does NOT establish:
- shorter CoT = less internal reasoning;
- a universal scalar semantics for effort.

Taste value: **A**  
Execution transfer: **F for training / C for inference analysis**  
Instrument value: **C**

Core pressure:
> reasoning-resource control can be part of policy training rather than an external decode knob.

---

## ST-02 — Thinking Machines Interaction Models
Date: 2026-05-11  
Type: research preview / architecture-system report  
Tier: II/III  
Primary:
- https://thinkingmachines.ai/blog/interaction-models/

Deep-read: **YES**

Actually establishes:
- continuous multimodal interaction is modeled using time-aligned micro-turns (~200ms);
- fast interaction path and asynchronous background reasoning are separated;
- silence, overlap and interruption remain part of model context.

Taste value: **A**  
Execution transfer: **D/F**  
Instrument value: **C**

Core pressure:
> alternating-message sequence is not the natural causal unit for realtime collaboration.

---

## ST-03 — Thinking Machines / Bridgewater expert judgment
Date: 2026-06-30  
Type: domain post-training study  
Tier: II  
Primary:
- https://thinkingmachines.ai/news/learning-to-replicate-expert-judgment-in-financial-tasks/
- Bridgewater AIA Labs version

Deep-read: **YES**

Actually establishes:
- repeated expert decisions contain trainable signal not easily expressible as prompt rules;
- disagreement-driven human verification + RL/distillation can reproduce domain-specific judgment.

Does NOT establish:
- general expert-taste transfer from all domains.

Taste value: **A-**  
Execution transfer: **B/C**  
Instrument value: **C** (data proprietary)

Core pressure:
> tacit judgment can be supervision even when it is hard to verbalize as rules.

---

## ST-04 — Thinking Machines ReViSQL
Date: 2026-08-27 release / paper arXiv 2603.20004  
Type: academic-style industrial post-training study  
Tier: II  
Primary:
- https://thinkingmachines.ai/news/putting-task-expertise-into-rl/

Deep-read: **YES**

Actually establishes:
- substantial data-label problems in the parent Text-to-SQL training set;
- execution-match reward can reward semantically wrong SQL by coincidence;
- verified data + task-specific reward shaping can replace some external pipeline complexity;
- a Kimi-K2.6 LoRA + CISPO recipe reaches strong results at lower inference cost.

Taste value: **A**  
Execution transfer: **A/B**  
Instrument value: **B**

Core move:
> external scaffold expertise can sometimes be moved into a better training signal.

---

## ST-05 — Prime Intellect Prime Agent
Date: 2026-08-05 blog / 2026-08-24 paper  
Type: open agent harness + paper  
Tier: II  
Primary:
- https://www.primeintellect.ai/blog/prime-agent
- arXiv:2608.23552
- https://github.com/PrimeIntellect-ai/prime-agent

Deep-read: **YES — paper + code concepts**

Actually establishes:
- context can be programmatically processed through an RLM-style persistent REPL;
- prompts/memory/skills/subagent specs form editable persistent harness state;
- refinement edits are explicit/reviewable/rollbackable.

Does NOT establish:
- continual refinement always improves;
- harness learning replaces weight learning.

Taste value: **A-**  
Execution transfer: **A/B**  
Instrument value: **A**

Core pressure:
> harness can be a persistent adaptive artifact rather than fixed inference infrastructure.

---

## ST-06 — Continual Harness
Date: 2026-05-11  
Type: academic/open agent adaptation system  
Tier: II  
Primary:
- arXiv:2605.09998
- https://github.com/sethkarten/continual-harness

Deep-read: **YES — paper + repo**

Actually establishes:
- reset-free online CRUD updates to prompt/subagents/skills/memory;
- explicit minimal vs expert vs evolving harness baselines;
- capability-dependent gains;
- strong capability floor: Pro improves, Flash variable, Flash-Lite can degrade.

Taste value: **A**  
Execution transfer: **B**  
Instrument value: **A**

Most important boundary:
> self-improvement loops can fail below a base-capability threshold.

---

## ST-07 — Sakana Recursive Harness Self-Improvement
Date: 2026-07-17  
Type: research paper  
Tier: II  
Primary:
- arXiv:2607.15524

Deep-read: **YES**

Actually establishes:
- prompt-level harness refinement can improve low-effort agents on synthetic ML-R&D tasks;
- authors attribute gains mainly to information flow/context management rather than longer reasoning;
- few update iterations can matter.

Does NOT establish:
- universal self-improvement;
- stability across models/tasks.

Taste value: **A-**  
Execution transfer: **A/B**  
Instrument value: **B**

Cluster warning:
> harness self-improvement is already a crowded conceptual surface.

---

## ST-08 — Kyutai Kairos temporal pretraining
Date: 2026-05-21 / released 2026-05-26  
Type: controlled pretraining study + open matched checkpoints  
Tier: II  
Primary:
- arXiv:2605.22769
- https://huggingface.co/kyutai/Sequential_Helium_6B
- KairosQA

Deep-read: **YES**

Actually establishes:
- 6B sequential chronological vs shuffled Common-Crawl training;
- sequential training improves recency/temporal precision while preserving broad general performance;
- multiple yearly sequential checkpoints;
- token-matched shuffled controls;
- selected non-cooldown variants.

Taste value: **A+**  
Execution transfer: **A for analysis / F for re-pretraining**  
Instrument value: **A+**

Why unusually useful:
> one public repo already contains a near-natural experiment over pretraining order.

---

## ST-09 — Kyutai MoshiRAG
Date: 2026-04/05  
Type: open full-duplex model + paper  
Tier: II  
Primary:
- arXiv:2604.12928
- https://github.com/kyutai-labs/moshi-rag
- HF checkpoints

Deep-read: **YES**

Actually establishes:
- asynchronous selective retrieval can run while conversation continues;
- pre-RAG acknowledgements/coarse speech hide retrieval latency;
- factual augmentation is injected back into the ongoing speech stream;
- retrieval backend is modular.

Taste value: **A**  
Execution transfer: **B/C**  
Instrument value: **B**

Core pressure:
> realtime interaction exposes natural latency slack that can be used for asynchronous cognition.

---

## ST-10 — Lychee-FD
Date: 2026-07-07  
Type: open full-duplex SpeechLM + diagnosis paper  
Tier: II  
Primary:
- arXiv:2607.06540
- https://huggingface.co/HIT-TMG/Lychee-FD

Deep-read: **YES**

Actually establishes:
- full-duplex semantic degradation is analyzed as acoustic-semantic gradient conflict;
- hierarchical parameter separation is derived from the diagnosis;
- reported gains improve both spoken QA and duplex interaction.

Taste value: **A+**  
Execution transfer: **B/C**  
Instrument value: **B**

One of the strongest recent diagnosis→mechanism→method examples outside LLM reasoning.

---

## ST-11 — DuplexSLA
Date: 2026-05/06  
Type: full-duplex Speech-Language-Action research system  
Tier: II  
Primary:
- arXiv:2605.20755

Deep-read: **YES**

Actually establishes:
- a shared ~160ms timeline for user audio, assistant audio and textual action;
- planning/tool calls can occur without stopping speech;
- turn-taking/control is handled inside one duplex backbone.

Taste value: **A**  
Execution transfer: **C/D**  
Instrument value: **B**

Core pressure:
> duplex speech alone does not solve duplex planning/action.

---

## ST-12 — KRAFTON Raon-Speech / SpeechChat
Date: 2026-04 report, weights updated through July  
Type: open 9B SpeechLM + full-duplex extension  
Tier: II  
Primary:
- arXiv:2605.23912
- HF Raon-Speech-9B / Raon-SpeechChat-9B

Deep-read: **YES at report/model-card level**

Actually establishes:
- a staged conversion of text LLM → SpeechLM → full-duplex model;
- 1.38M hours speech/text for SpeechLM;
- 119K hours time-aligned dialogue continual training for duplex behavior;
- checkpoints/training/inference are open.

Taste value: **A-**  
Execution transfer: **C**  
Instrument value: **A/B**

Core pressure:
> strong speech intelligence and full-duplex interaction are separable training problems.

---

## ST-13 — InclusionAI Ling-3.0
Date: 2026 recent release; WSM parent arXiv:2507.17634  
Type: open training-stage model family  
Tier: II  
Primary:
- HF inclusionAI/Ling-3.0-*
- Warmup-Stable-Merge

Deep-read: **YES**

Actually establishes:
- pretrain/midtrain/WSM-merged checkpoint ladder;
- tiny and flash share training recipe;
- WSM replaces conventional decay with weighted checkpoint merging;
- goal includes continual pretraining / dynamic data expansion.

Taste value: **A**  
Execution transfer: **A/B**  
Instrument value: **A+**

Core pressure:
> training schedule can be partially transformed from online trajectory commitment into offline checkpoint-combination search.

---

## ST-14 — OpenBMB MiniCPM5-2B
Date: 2026  
Type: open small model family + staged post-training  
Tier: II  
Primary:
- HF OpenBMB MiniCPM5 family

Deep-read: **YES at model-card level**

Actually establishes:
- base/midtrain/SFT/final RL+OPD stages;
- 2B scale;
- critic-style RL;
- 16 expert models consolidated with OPD;
- open data/checkpoints.

Taste value: **A-**  
Execution transfer: **A**  
Instrument value: **A+**

Why valuable:
> small enough to train, modern enough to study current post-training rather than legacy SFT only.

---

## ST-15 — Cohere Tiny Aya Thinker pair
Date: 2026  
Type: matched multilingual reasoning models  
Tier: II  
Primary:
- CohereLabs/tiny-aya-en-thinker
- tiny-aya-l2-thinker

Deep-read: **YES at model-card level**

Actually establishes:
- En-Thinker reasons in English and answers in user language;
- L2-Thinker reasons in prompt language;
- same family, ~3.35B.

Taste value: **A-**  
Execution transfer: **A**  
Instrument value: **A+**

Core value:
> matched public instrument for reasoning-language vs answer-language effects.

---

## ST-16 — Meituan LongCat Sparse Attention
Date: 2026-08-03  
Type: technical report + open smaller sparse model  
Tier: II  
Primary:
- arXiv:2608.01662
- meituan-longcat/LongCat-Flash-Lite-Sparse

Deep-read: **YES**

Actually establishes:
- DeepSeek-style sparse indexing exposes index-scoring and fragmented-memory bottlenecks;
- streaming-aware, cross-layer and hierarchical indexing address distinct system costs;
- smaller 69B-A3B mechanism-faithful checkpoint is open.

Taste value: **A**  
Execution transfer: **C**  
Instrument value: **B**

Core move:
> theoretical sparsity solves one bottleneck and exposes indexer/memory-access as the next one.

---

## ST-17 — Kyutai FID Lottery
Date: 2026-06-18  
Type: controlled evaluation/measurement study  
Tier: II  
Primary:
- arXiv:2606.20536
- https://kyutai.org/fid-lottery/

Deep-read: **YES**

Actually establishes:
- training-seed variation dominates generation-seed variation in their panel;
- initialization, data order and flow-matching noise all contribute;
- scale/compute do not collapse the relative variance floor;
- small FID gains can fall under recipe randomness.

Taste value: **A**  
Execution transfer: **B/C**  
Instrument value: **B**

Core pressure:
> a "trained model" is a random draw from a training recipe, not a deterministic artifact.

---

## ST-18 — Surflo
Date: 2026-06  
Type: 3D generative/reconstruction research  
Tier: II  
Primary:
- arXiv:2606.13644

Deep-read: **YES**

Actually establishes:
- variable-view images → fixed 128-token global state;
- arbitrary-resolution output is decoupled from latent size;
- independent point decoding needs shared rendering guidance for coherence.

Taste value: **A**  
Execution transfer: **C**  
Instrument value: **B/C**

Core pressure:
> physical invariance can define the representation unit more strongly than input tokenization.

---

## ST-19 — ACE Robotics Kairos
Date: 2026-06 report / July open weights  
Type: 4B world-action model + robotics variants  
Tier: II  
Primary:
- arXiv:2606.16533
- HF ACERobotics/Kairos3.1-4B-robot-480P and action variants

Deep-read: **YES**

Actually establishes:
- cross-embodiment data curriculum;
- hybrid local/mid/global temporal memory;
- unified understanding/generation/action prediction;
- open robot-action checkpoints;
- deployment-aware server/consumer rollout.

Taste value: **A**  
Execution transfer: **B/C**  
Instrument value: **A/B**

---

## ST-20 — NVIDIA Nemotron-Labs-Diffusion
Date: 2026-07-07  
Type: open 3B/8B/14B tri-mode LM family  
Tier: II  
Primary:
- arXiv:2607.05722
- HF nvidia/Nemotron-Labs-Diffusion-3B etc.

Deep-read: **YES**

Actually establishes:
- one model jointly supports AR, diffusion and self-speculation;
- diffusion drafts + AR verifies;
- decoding mode can be workload-conditioned;
- small open 3B instrument exists.

Taste value: **A**  
Execution transfer: **A/B**  
Instrument value: **A**

Core pressure:
> generation operator can be a controllable mode of one trained model rather than an architecture family choice.

---

# Startup/HF ledger rule

For future scanning, any new release should record both:

1. **technical-thesis value**
2. **instrument value**

A very strong closed model with no matched artifacts may have:
> thesis A / instrument F.

A modest 2B–6B model with clean stage/control pairs may have:
> thesis B / instrument A+.

For our research process, the second case can be more useful.


---

# L. Additional startup / open-lab sources — deep-read pass 2

Added after expanding beyond the first Startup+HF sweep.

---

## ST-21 — Sakana Fugu / Fugu Max / Fugu Ultra v2
Date: Jun–Sep 2026  
Type: orchestrator LM technical report + productized research release  
Tier: II/III  
Primary:
- arXiv:2606.21228
- https://github.com/SakanaAI/fugu
- https://sakana.ai/fugu-max-release/

Deep-read: **YES**

Actually establishes:
- orchestration is trained as a language-model policy rather than fixed workflow code;
- low-latency Fugu deliberately restricts orchestration to worker selection;
- Ultra tracks multi-agent identities, communication topology, tool-call ownership and subtask state;
- September release explicitly separates cost-efficient and maximum-capability orchestration regimes.

Does NOT establish:
- that learned routing is universally superior to fixed routing;
- that one routing state representation is sufficient across model pools.

Taste value: **A**  
Execution transfer: **B/C**  
Instrument value: **B**

Core pressure:
> model selection / workflow topology becomes a learnable cognition-allocation policy.

---

## ST-22 — Runway Solaris
Date: Sep 2026  
Type: world-model research paper  
Tier: II  
Primary:
- arXiv:2609.00776

Deep-read: **YES**

Actually establishes:
- interactive UI can be modeled directly as visual-state transitions conditioned on user actions;
- code/DOM/state-machine representation is not required as the immediate generated object;
- long autoregressive interaction requires training on model-generated states and managing compounding error.

Does NOT establish:
- that direct visual generation should replace programmatic UI systems generally.

Taste value: **A**  
Execution transfer: **D/F**  
Instrument value: **F**

Core pressure:
> executable interface behavior can be modeled as world dynamics rather than generated source code.

---

## ST-23 — Skild S1
Date: Aug 2026  
Type: company research report / deployment-derived foundation-model study  
Tier: II/III  
Primary:
- https://skild.ai/blogs/s1

Deep-read: **YES**

Actually establishes / company reports:
- dense downstream data can erase part of the peak gap between scratch specialists and pretrained policies;
- S1 is trained so a video demonstration specifies a task in context without weight updates;
- evaluation explicitly separates seen/unseen tasks and short/long horizons;
- long-horizon unseen tasks run up to roughly ten minutes;
- deployment friction motivated redefining the value of pretraining as a new adaptation mode.

Does NOT establish:
- an independent, universally validated scaling law for robot ICL;
- that one-shot video ICL always dominates post-training.

Taste value: **A**  
Execution transfer: **D**  
Instrument value: **C**

Core changed premise:
> foundation pretraining should be judged by the adaptation mode it creates, not only by fine-tuning sample efficiency.

---

## ST-24 — Physical Intelligence RL Token / MEM / π0.7
Date: Mar–Apr 2026  
Type: robotics research papers / company reports  
Tier: II  
Primary:
- arXiv:2604.23073
- arXiv:2603.03596
- https://www.pi.website/

Deep-read: **YES at paper/official-report level**

Actually establishes:
- RL Token exposes a compact VLA representation for small actor-critic online RL;
- MEM separates short-term visual memory from long-term abstract/text memory;
- π0.7 explores policy steering/compositional conditioning.

Taste value: **A**  
Execution transfer: **C/D**  
Instrument value: **C**

Core lesson:
> "fast robot adaptation" already decomposes into different channels: in-context task induction, memory, online RL, and steering.

---

## ST-25 — Zyphra ZONOS2
Date: Jun 2026  
Type: open TTS technical report + weights/code  
Tier: II  
Primary:
- arXiv:2606.24320

Deep-read: **YES**

Actually establishes:
- LLM-style MoE routing is substantially less stable on delayed audio-token streams in their setup;
- MHA was more stable/higher quality than GQA in early tests, but GQA was selected for inference speed;
- high-bandwidth speaker embeddings leak lexical/duration/noise/pause information and create shortcut failures;
- LDA + cropping/loss masking + augmentation + staged annealing reduce that leakage;
- phonemization helps at lower capability but becomes a silent preprocessing failure source at sufficient scale, where byte input can catch up/surpass it.

Taste value: **A+**  
Execution transfer: **B/C**  
Instrument value: **A/B**

Core pressure:
> domain transfer of an architecture/conditioning channel can fail because the new token/statistical process violates assumptions that were benign in text.

Failure-provenance value: **A+**

---

## ST-26 — Inworld Realtime TTS-2
Date: Aug 31 2026  
Type: production voice-model release  
Tier: III/IV  
Primary:
- https://inworld.ai/blog/realtime-tts-2

Deep-read: **YES**

Actually establishes / product claim:
- prior conversational audio, not only transcript, conditions subsequent TTS;
- natural-language voice direction replaces part of fixed categorical style control;
- cross-lingual voice identity and persistent realtime session are explicit product requirements;
- their production stack keeps modular STT/router/TTS boundaries but passes richer state across them.

Does NOT establish:
- architecture/training mechanism in enough detail for causal claims.

Taste value: **A- pressure / C mechanism**  
Execution transfer: **C**  
Instrument value: **F**

Core pressure:
> utterance-local TTS is an incomplete abstraction when acoustic conversational state persists across turns.

---

## ST-27 — NVIDIA NemotronLabs VoiceChat-11B
Date: Aug 3 2026  
Type: open full-duplex model card + weights/config  
Tier: II  
Primary:
- https://huggingface.co/nvidia/NVIDIA-NemotronLabs-VoiceChat-11B

Deep-read: **YES**

Actually establishes:
- end-to-end realtime full-duplex speech understanding/generation;
- separate output channel for tool-call scripts;
- conversational "on-hold" speech can continue while external tool execution is pending;
- ~11B open checkpoint, full-duplex/tool protocol, config and broad training-data description;
- reported training uses ~550k hours of real/synthetic speech.

Does NOT establish:
- that a separate tool channel is uniquely optimal;
- causal mechanism for all turn-taking improvements.

Taste value: **A**  
Execution transfer: **B/C**  
Instrument value: **A/B**

Core pressure:
> realtime assistants have multiple output clocks: conversational speech and structured external action.

---

## ST-28 — Odyssey Starchild-1
Date: May 2026  
Type: technical report / closed world model  
Tier: II  
Primary:
- Starchild-1 technical report
- https://odyssey.ml/introducing-starchild-1

Deep-read: **YES**

Actually establishes:
- causal realtime joint audio-video rollout is not a straightforward extension of video-only causal generation;
- audio/video have different temporal frequency, information density and error propagation;
- standard video-only causal-distillation strategies are insufficient in their setting;
- asynchronous KV state and rollout adaptation are designed for multirate modalities;
- short offline generation metrics are insufficient for interactive long-horizon multimodal rollout.

Taste value: **A+**  
Execution transfer: **F**  
Instrument value: **F**

Core pressure:
> multimodal realtime generation is a coupled multirate dynamical system.

Failure-provenance value: **A**

---

## ST-29 — Odyssey PROWL-1
Date: May 2026  
Type: RL-driven world-model data generation / technical research  
Tier: II/III  
Primary:
- https://odyssey.ml/introducing-prowl-1

Deep-read: **YES at first-party technical-report level**

Actually establishes:
- an RL explorer is rewarded for finding world-model failure trajectories;
- exploration is constrained toward realistic behavior to avoid meaningless adversarial exploits;
- a prioritized adversarial trajectory buffer shifts training toward unresolved failures;
- world model and data-discovery policy co-evolve.

Taste value: **A**  
Execution transfer: **C/D**  
Instrument value: **C**

Core pressure:
> data collection can optimize model regret rather than passively sample the environment distribution.

---

## ST-30 — MIRA (General Intuition × Kyutai × Epic)
Date: Jul 2026  
Type: open world-model technical report + code + dataset  
Tier: II  
Primary:
- https://mira-wm.com/
- https://github.com/mira-wm/mira

Deep-read: **YES**

Actually establishes:
- a 5B latent diffusion world model generates synchronized 2v2 Rocket League views at realtime rates;
- training data includes synchronized per-player views/actions and game state;
- code, dataset and model/training configuration are public;
- multiplayer interaction imposes one shared hidden world that must remain consistent across multiple observers/actions.

Taste value: **A**  
Execution transfer: **C/D**  
Instrument value: **A/B**

Core pressure:
> multi-agent world models require shared latent state consistency, not four independent video predictions.

---

## ST-31 — World Labs Functional Taxonomy / R2S2R / Atlas
Date: Jun–Sep 2026  
Type: industrial research framework + robotics simulation report + model release  
Tier: II/III  
Primary:
- https://www.worldlabs.ai/blog/taxonomy-of-world-models
- https://www.worldlabs.ai/blog/real-to-sim-to-real
- https://www.worldlabs.ai/blog/atlas

Deep-read: **YES**

Actually establishes / frames:
- renderer, simulator and planner have different output contracts;
- R2S2R evaluates simulation partly by whether it preserves policy ranking, training progress and failure regions in reality;
- simulation usefulness can therefore be defined by decision fidelity rather than exact scalar success-rate matching;
- Atlas is a multimodal autoregressive diffusion model grounded in shared spatial context, but is closed/early-access.

Does NOT establish:
- general causal laws for every world-model family;
- independent verification of all company R2S2R claims.

Taste value: **A**  
Execution transfer: **D/F**  
Instrument value: **F**

Core pressure:
> the fidelity metric for a learned world should be determined by the downstream consumer's decision contract.

---

## ST-32 — Audio8 TTS Preview 0.6B
Date: Sep 2026  
Type: open compact TTS checkpoint + codec + INT4 deployment pair  
Tier: II/III  
Primary:
- https://huggingface.co/Audio8/Audio8-TTS-Preview-0.6b
- CPU INT4 ONNX release

Deep-read: **YES at model-card/code level**

Actually establishes:
- compact DualAR TTS with separate slow semantic and fast codebook prediction;
- complete 44.1kHz codec and 0.6B model are public;
- a matched CPU-oriented INT4 ONNX deployment exists with roughly 1GB runtime footprint in the team's reported setup.

Does NOT establish:
- a new DualAR scientific thesis (the card explicitly cites Fish Audio S2 Pro inspiration);
- controlled evidence that the architecture itself is novel.

Taste value: **C+/B-**  
Execution transfer: **A**  
Instrument value: **A**

Core value:
> unusually cheap open speech research instrument, not a primary research-taste anchor.

---

## ST-33 — DeepGrove Maple Preview
Date: Sep 2026  
Type: open on-device reasoning model  
Tier: II/IV  
Primary:
- https://huggingface.co/deepgrove/maple-preview
- deepgrove-ai MLX fork

Deep-read: **YES at model-card/runtime level**

Actually establishes:
- 20B total / ~1B active MoE;
- ternary weights;
- 256 experts with 8 active;
- 3:1 512-token sliding-window vs global attention;
- explicit design target of local/on-device inference.

Does NOT establish:
- enough training ablations or failure diagnosis to identify why each architectural component is load-bearing.

Taste value: **B-**  
Execution transfer: **B/C**  
Instrument value: **B**

Status:
> monitor as deployment-native architecture; not yet a positive genealogy anchor.

---

## ST-34 — Syzygy Mach-1 Additive
Date: Sep 2026  
Type: ultra-low-bit compression artifact / custom codec runtime  
Tier: III  
Primary:
- https://huggingface.co/SyzygyResearch/Mach-1-Additive-35B

Deep-read: **YES at release-format/code level**

Actually establishes:
- highly compressed additive/trellis-coded Qwen-family MoE representation;
- standalone decode implementation and explicit compression manifest;
- benchmark-retention measurements against full precision;
- custom local runtime / GGUF-style distribution.

Does NOT establish:
- a sufficiently documented scientific derivation of the codec;
- why this coding structure is the unique consequence of a diagnosed model failure.

Taste value: **C+/B-**  
Execution transfer: **B**  
Instrument value: **B/A- for compression engineering**

Status:
> compression artifact and contrast case, not a current taste source.

---

# M. Recency discipline for HF/startup scanning

New hard rule:

> **Current HF attention is not publication recency.**

Example:
- Motif 2.6B was resurfacing in 2026 HF discussion, but its technical report dates to Aug 2025.

Therefore every source must record:
1. original technical-report/model-card date;
2. latest checkpoint update date;
3. whether a recent update changed the scientific thesis or only packaging/runtime;
4. whether "trending now" reflects a genuinely new research result.

Do not let current likes/downloads rewrite genealogy chronology.

---

# N. Convergence is not novelty

Another hard rule strengthened by Solar Open 2:

Solar Open 2 (Jul 2026) includes:
- ~1M context;
- hybrid global/linear attention;
- 12 domain specialists;
- MOPD consolidation.

These are relevant current industrial evidence.

But similar conceptual moves already appear across:
- Kimi;
- MiniCPM;
- Instella;
- DeepSeek;
- other agent-specialist/post-training pipelines.

Therefore a new report can be:
> strong confirmation that a design pattern is industrially important

without being:
> a new conceptual seed.

Log convergence separately from changed-premise discoveries.


---

# O. Structured/scientific/open-model sources — deep-read pass 3

## ST-35 — Prior Labs TabPFN-3 / TabPFN-3.5
Date: May 2026 / Sep 2026  
Type: open tabular foundation model + hosted fit-time compute extensions  
Tier: II  
Primary:
- arXiv:2605.13986
- arXiv:2609.17895
- https://github.com/PriorLabs/TabPFN

Deep-read: **YES**

Actually establishes:
- synthetic task prior is used to pretrain an in-context predictor;
- TabPFN-3 can perform downstream fitting/inference in one forward pass;
- 3.5 public architecture uses distribution embedding, row-wise and cross-row attention;
- public base and Fast variants exist;
- "Thinking" spends more fit-time compute to construct/configure a reusable predictor rather than generating longer CoT.

Does NOT establish:
- that every TabPFN Thinking implementation detail is public;
- that product word "thinking" corresponds to language-style reasoning.

Taste value: **A+**  
Execution transfer: **A**  
Instrument value: **A+**

Core pressure:
> test-time compute can mean amortized predictor construction, not deliberative token generation.

---

## ST-36 — τ₀-VLA
Date: Jul/Aug 2026  
Type: hierarchical VLA + world-model-guided test-time computation  
Tier: II  
Primary:
- arXiv:2608.16885
- https://github.com/sii-research/tau-0-vla

Deep-read: **YES**

Actually establishes:
- high-level policy can route uncertain decisions into proposal/world-model/value/beam-search/reflection before physical commitment;
- low-level policy is an open Qwen3.5-2B + MoT action expert with conditional flow matching;
- execution memory and hypothetical branch state are distinct;
- open low-level post-training/data adapters are usable.

Does NOT establish:
- that the full high-level TTC stack is currently as open/reproducible as the low-level VLA;
- universal value of world-model search on all robot tasks.

Taste value: **A+**  
Execution transfer: **B/C for low-level; D for full thesis**  
Instrument value: **A/B low-level; C full TTC**

Core pressure:
> extra inference compute is justified by the asymmetric cost of wrong irreversible action.

---

## ST-37 — Google TimesFM-3
Date: Aug 2026  
Type: open 330M time-series foundation model  
Tier: II  
Primary:
- https://github.com/google-research/timesfm
- google/timesfm-3.0-pytorch

Deep-read: **YES**

Actually establishes:
- native multivariate forecasting and past/future covariates;
- official evaluation enables cross-variate attention;
- one-forward-pass prediction remains the deployment object;
- PyTorch/MLX and benchmark runners are public.

Taste value: **A**  
Execution transfer: **A**  
Instrument value: **A+**

Core pressure:
> richer cross-variable inference does not necessarily require iterative/test-time reasoning; it can belong in the base computation graph.

---

## ST-38 — Tencent AuK / AuK-Flash
Date: Sep 2026  
Type: open foundational speech generation/editing model + fast distilled variant  
Tier: II  
Primary:
- arXiv:2609.08936
- https://github.com/Tencent-Hunyuan/AuK

Deep-read: **YES**

Actually establishes:
- generation/editing/enhancement/paralinguistic/acoustic editing share a natural-language+audio interface;
- training moves generation-only warmup → joint generation/editing;
- different task families retain different post-training signals;
- AuK-Flash uses task-routed fast-sampling distillation;
- base and Flash weights, fine-tuning code, intermediate snapshots, EMA and per-t validation curves are public;
- fine-tuning freezes semantic encoder/VAE and updates generation/fusion.

Taste value: **A**  
Execution transfer: **A/B**  
Instrument value: **A+**

Core pressure:
> unified interface does not imply uniform optimization or uniform distillation dynamics.

---

## ST-39 — StepAudio 3 Gen
Date: Sep 2026  
Type: general-audio technical report  
Tier: II  
Primary:
- arXiv:2609.12945

Deep-read: **YES**

Actually establishes:
- general audio is modeled through low-rate discrete RVQ autoregression rather than a diffusion-only formulation;
- time-axis coarse/first-codebook prediction is separated from residual codebook completion;
- progressive training explicitly targets interference between new audio-generation learning and existing language/reasoning capability;
- detached/gradual integration is used before deeper multimodal coupling.

Does NOT establish:
- cheap public reproduction unless complete weights/code are available;
- that discrete AR universally dominates flow/diffusion.

Taste value: **A+**  
Execution transfer: **C/D pending artifact availability**  
Instrument value: **C pending release**

Core pressure:
> adding a modality can damage a pretrained backbone; representation/generative operator and training schedule jointly determine interference.

---

## ST-40 — Hugging Face Carbon
Date: Sep 2026  
Type: fully open genomic causal-LM family  
Tier: II  
Primary:
- https://github.com/huggingface/carbon
- HuggingFaceBio/Carbon-500M, 3B, 8B

Deep-read: **YES**

Actually establishes:
- DNA uses non-overlapping 6-mer tokens while text uses BPE;
- coarse 6-mer tokenization improves sequence economics but reduces direct nucleotide-resolution supervision;
- Factorized Nucleotide Supervision restores base-pair-level supervision;
- 500M model has an explicit draft-model role for speculative decoding of larger Carbon models;
- biological counterfactual evals and long-context DNA tasks are public.

Taste value: **A+**  
Execution transfer: **A/B**  
Instrument value: **A+**

Core pressure:
> an efficiency-oriented tokenizer can create a known information-resolution loss that the learning objective must repair.

---

## ST-41 — NVIDIA JEPA-DNA
Date: Feb 2026  
Type: matched-backbone genomic objective study  
Tier: II  
Primary:
- arXiv:2602.17162
- https://github.com/NVIDIA-BioNeMo/JEPA-DNA

Deep-read: **YES**

Actually establishes:
- token reconstruction is augmented with latent masked-region prediction intended to capture broader functional structure;
- matched JEPA continual-pretraining checkpoints are released for DNABERT-2, NTv3 and HyenaDNA;
- reproduction configs/code and benchmark driver are public;
- effects are not uniform across every task/backbone.

Taste value: **A**  
Execution transfer: **A/B**  
Instrument value: **A+**

Core pressure:
> local token recovery and region-level functional abstraction are distinct supervision targets.

Recency note:
> direct scientific parent/source, not a Sep-2026 release.

---

## ST-42 — NASA–IBM Lunar Foundation Model
Date: Sep 2026  
Type: open remote-sensing foundation model  
Tier: II  
Primary:
- NASA/IBM model card and NASA-IMPACT repo

Deep-read: **YES**

Actually establishes:
- lunar appearance depends strongly on known acquisition/illumination geometry;
- acquisition geometry is explicitly conditioned instead of being left for pixel inference;
- high-resolution NAC and low-resolution WAC imagery are jointly pretrained;
- modality-specific tokenizers and flexible scale handling are public.

Taste value: **A+**  
Execution transfer: **A/B**  
Instrument value: **A**

Core pressure:
> do not force a model to re-infer a nuisance variable that the measurement process already records accurately.

---

## ST-43 — BGI Genos-m
Date: May 2026  
Type: open microbial-genomics foundation model  
Tier: II  
Primary:
- BGI-HangzhouAI/Genos-m
- project technical report

Deep-read: **YES**

Actually establishes:
- human-associated microbial ecology is explicitly emphasized in the pretraining distribution;
- single-nucleotide representation contrasts with Carbon's coarse k-mer design;
- sparse MoE enables large total capacity with ~330M active parameters;
- SAE features are aligned to external genomic annotations such as ORF/intergenic/tRNA/rRNA/strand direction;
- chunk representations are aggregated for whole-genome phenotype tasks.

Taste value: **A**  
Execution transfer: **B/C**  
Instrument value: **B**

Core pressure:
> domain specialization can act through the prior/training distribution while external scientific annotations make representation semantics directly testable.

---

## ST-44 — Botanic1
Date: Sep 2026  
Type: open plant-genomics foundation-model family  
Tier: II  
Primary:
- Botanic1 Hugging Face collection / technical report

Deep-read: **PARTIAL-TO-SOLID**

Actually establishes:
- bidirectional Mamba-2 masked modeling;
- single-nucleotide representation;
- hundreds of plant species;
- multiple sizes/adaptation modes.

Taste value: **A-**  
Execution transfer: **A/B**  
Instrument value: **A/B**

Core pressure:
> architecture/tokenization can be chosen around the sequence process and mutation resolution rather than around dominant language-model conventions.

---

# P. New model-card reading fields

For every future open/startup/scientific model, the ledger should additionally record:

- **Minimum Scale of Causal Visibility**
- **Proxy Fidelity Evidence**
- **Failure-Provenance Value**
- **Operator Identity**
- **Domain Structure Placement**
- **Instrument Value**

This prevents one large SOTA score from dominating research-taste calibration.
