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


---

# L. Failure provenance, open development trees, continual learning, structured science — added 2026-09-19

## ST-21 — Vinci Technical Report No. 1: Transferring Character Post-Training to Mistral 7B
Date: 2026-08-13  
Type: internal technical report + experimental checkpoint  
Tier: II/negative-evidence source  
Primary: SimpleDirect / Vinci Research No. 1

Deep-read: **YES**

Actually establishes within its development-tier protocol:
- a frozen SFT+DPO behavior recipe substantially moved the model-judged unsupported/fabrication metric on Mistral 7B;
- reticence increased;
- GSM8K regressed by ~5.6 points;
- a deterministic evaluator misranked checkpoints.

Does NOT establish:
- improved factual knowledge;
- production readiness;
- general recipe portability.

Taste value: **A for failure provenance**  
Execution transfer: **A/B**  
Instrument value: **B**  
Peer review: **NO**

Core lesson:
> target behavior movement and useful behavior change are different quantities.

---

## ST-22 — Vinci Technical Report No. 2: Character Transfer Across Three Model Families
Date: 2026-09-01  
Type: controlled multi-family negative/boundary report  
Tier: II  
Primary: SimpleDirect / Vinci Research No. 2

Deep-read: **YES**

Actually establishes in the declared validation setting:
- one frozen recipe moved unsupported-assertion rate in the desired direction on Qwen3, Ministral and OLMo;
- no family met the pre-registered grounded-answer preservation bar;
- trade-off differed by family;
- judge repeatability/provenance became a measurement issue.

Does NOT establish:
- universal character-training failure;
- final primary-holdout result;
- production safety or truthfulness.

Taste value: **A+ for boundary-result discipline**  
Execution transfer: **A/B**  
Instrument value: **B**  
Peer review: **NO**

Core lesson:
> directional transfer ≠ utility-preserving transfer.

---

## ST-23 — Vinci Technical Report No. 3: Runtime Pass Is Not Correctness
Date: 2026-09-01  
Type: failed post-training study + evaluator audit  
Tier: II  
Primary: SimpleDirect / Vinci Research No. 3

Deep-read: **YES**

Actually establishes in its audit:
- the configured reasoning-efficiency intervention missed its positive bar;
- the original executable evaluator accepted 24/24 deliberately wrong adversarial non-solutions;
- runtime/visible-test success did not certify semantic correctness;
- evaluator repair required fresh mutation/adversarial qualification;
- denominator/censoring choices materially affected measured quantities.

Does NOT establish:
- a universal weakness of executable evaluation;
- a peer-reviewed general theorem.

Taste value: **A+**  
Execution transfer: **A**  
Instrument value: **A as protocol pattern / low as model artifact**  
Peer review: **NO**

Core lesson:
> evaluator is an experimental instrument that needs independent qualification.

---

## ST-24 — IFM K2 Horizon fleet
Date: 2026-09-03  
Type: open model fleet / development-tree artifact  
Tier: II/IV depending claim  
Primary:
- IFM K2 Horizon release
- Hugging Face K2-Horizon family

Deep-read: **YES at blog/model-card/artifact level**

Actually establishes:
- six public size classes from 0.9B to 375B;
- public weights and at least some intermediate branches/checkpoints/logs;
- common family methodology/interfaces, with nontrivial architecture/vocabulary differences across sizes;
- 0.9B card exposes multi-teacher post-training and stage branches;
- release materials document an unintended benchmark-answer acquisition episode in development.

Does NOT yet establish:
- a perfectly controlled same-recipe scaling law;
- proxy-fidelity of 0.9B results for 375B;
- full reproducibility until promised report/code/data artifacts are verified as released.

Taste value: **A**  
Execution transfer: **A at 0.9B / lower at large scales**  
Instrument value: **A+**  
Proxy-fidelity evidence: **B-/unknown until full tree analysis**

Core lesson:
> an open development tree can be more scientifically useful than final weights, but family membership is not causal control.

---

## ST-25 — Base Labs: Can a Language Model Learn Facts Continually in Its Weights?
Date: 2026-07  
Type: open post-training science / continual-learning negative study  
Tier: II  
Primary:
- Base Labs article
- arXiv:2607.11020

Deep-read: **YES**

Actually establishes:
- broad restatement/study data creates more usable written knowledge than bare statements;
- later sequential writes can make earlier facts behaviorally unreachable while preserving much of their local write signal;
- prompt re-supply can recover many "forgotten" facts;
- tested local interventions did not robustly preserve reachability under continued writes.

Does NOT establish:
- that all weight-based continual learning is impossible;
- that the information is fully intact in a mechanistic sense.

Taste value: **A+**  
Execution transfer: **A**  
Instrument value: **A/B**

Core lesson:
> behavioral forgetting can be retrieval/reachability drift rather than literal erasure.

---

## ST-26 — Falcon: Fast Weight Attention for Continual Learning
Date: arXiv 2026-08-27 (project metadata also references earlier technical-report work)  
Type: theory/architecture continual-learning study  
Tier: II  
Primary: arXiv:2608.27763 / project page

Deep-read: **YES at abstract/project/theory-object level**

Actually establishes:
- recurrent/fast-weight state transitions can be interpreted as online learning rules;
- prefix-aligned vs same-step writes optimize different internal objectives;
- normalized updates separate plasticity, forgetting and bounded rehearsal.

Taste value: **A**  
Execution transfer: **B**  
Instrument value: **B**

Core lesson:
> online memory update semantics are an optimization objective, not only architecture plumbing.

---

## ST-27 — Macaron-V1
Date: 2026-07/08  
Type: open large agent-model family / continual-learning architecture  
Tier: II/III  
Primary:
- Macaron-V1 report/repo

Deep-read: **YES at architecture/harness level**

Actually establishes:
- frozen base + four persistent LoRA specialists;
- one specialist selected per user turn;
- same Mixture-of-LoRA design on Venti and smaller Tall families;
- adapter registration provides a modular substrate for continued specialization.

Does NOT establish:
- robust cumulative continual learning over unbounded experience;
- compositional consistency across arbitrary specialists.

Taste value: **A-**  
Execution transfer: **D for flagship / C for Tall**  
Instrument value: **B**

Core lesson:
> persistent modular adapters are a different knowledge location from base-weight rewriting.

---

## ST-28 — Infinite-Parameter LLMs
Date: 2026-09-16  
Type: very recent conceptual architecture paper  
Tier: II/early proposal  
Primary: arXiv:2609.18842

Deep-read: **YES at abstract/problem/formulation level**

Actually proposes:
- a frozen shared base;
- hypernetwork-generated low-rank FFN modulations from live data;
- an online-updated Bayesian belief over latent code;
- re-derived effective weights as interaction proceeds;
- an evaluation protocol against ICL/retrieval.

Does NOT yet establish:
- practical large-scale performance;
- superiority over retrieval/adapters;
- stable continual learning in deployment.

Taste value: **A- as new storage-location thesis**  
Execution transfer: **C/D**  
Instrument value: **F until code/checkpoints appear**

Core lesson:
> live data can in principle be compiled into generated weights, creating a distinct persistence/amortization point between context and permanent parameters.

---

## ST-29 — Monroe
Date: 2026-08-19  
Type: molecular foundation-model study  
Tier: II  
Primary: arXiv:2608.18982

Deep-read: **YES at problem/ablation/transfer-result level**

Actually establishes:
- molecular representation improvements plus a PFN downstream predictor;
- PFN-based downstream inference also improves external molecular representations (MiniMol/CheMeleon);
- downstream consumer choice can be transferable across representation families.

Taste value: **A**  
Execution transfer: **B**  
Instrument value: **B**

Core lesson:
> representation quality and downstream inference algorithm are distinct, interacting contributors.

---

## ST-30 — Molexar Base / Omni
Date: 2026-06-24  
Type: tiny molecular FM + matched conditional SFT pair  
Tier: II  
Primary:
- arXiv:2606.25865
- fairydance/molexar-10m-base
- fairydance/molexar-10m-omni

Deep-read: **YES**

Actually establishes:
- Fragment-SELFIES / BRICS-fragment molecular language;
- 10M base model for unconditional/fragment continuation;
- matched Omni model initialized from Base and SFT'd across scalar/property, pharmacophore, protein-sequence and pocket conditions;
- one AR decoder supports multiple condition types.

Taste value: **A-**  
Execution transfer: **A+**  
Instrument value: **A+**

Core lesson:
> a chemically meaningful basic unit plus matched base/conditional pair can be a better small scientific instrument than a giant domain model.

---

## ST-31 — Self-Geometry
Date: 2026-08-11  
Type: 3D VFM test-time adaptation paper  
Tier: II  
Primary: arXiv:2608.10708 / project page

Deep-read: **YES**

Actually establishes:
- explicit multi-view geometry is expensive to impose during foundation pretraining;
- test-time QKV-LoRA can impose epipolar/multi-view constraints;
- reported improvements span six VFMs and four benchmarks;
- adaptation is lightweight enough for per-scene use on a high-end single GPU.

Artifact caveat:
- official repository/project page still indicated code release was forthcoming at the checked version.

Taste value: **A**  
Execution transfer: **A/B if code becomes available**  
Instrument value: **B currently**

Core lesson:
> known physical structure can be placed at test time rather than inside pretraining.

---

## ST-32 — MindForge
Date: 2026-07-29  
Type: code-agent data/environment pipeline + open trajectories  
Tier: II  
Primary:
- arXiv:2607.27146
- centre-for-swe/MindForge-27B-Training-Trajectories

Deep-read: **YES**

Actually establishes:
- source-free cleanroom environments expose only compiled reference executable + sanitized docs;
- 1,001 long whole-program synthesis trajectories are public;
- 1,124 cleanroom environment entries are indexed;
- a concrete full-finetuning recipe for Qwen3.6-27B is released;
- fine-tuning improves ProgramBench and seven unseen SE benchmarks in the reported study.

Taste value: **A**  
Execution transfer: **B/C (trajectory analysis easier than full FT)**  
Instrument value: **A**

Core lesson:
> executable behavior can be a powerful interactive oracle without exposing implementation.

---

## ST-33 — SpecFirst
Date: 2026-07-29  
Type: code-agent process decomposition paper  
Tier: II  
Primary: arXiv:2607.27167

Deep-read: **YES**

Actually establishes:
- from-scratch synthesis often under-probes the behavioral oracle;
- separating behavioral specification elicitation from implementation improves the tested agents;
- early misunderstanding is treated as a process-stage failure rather than only a code-generation failure.

Taste value: **A**  
Execution transfer: **A/B**  
Instrument value: **B**

Core lesson:
> requirements/specification elicitation can be a first-class computation phase before synthesis.

---

## ST-34 — Code World Model
Date: 2026-08-26  
Type: world-model architecture preprint  
Tier: II  
Primary: arXiv:2608.25927 / project page

Deep-read: **YES at architecture/problem level**

Actually proposes/demonstrates:
- coding agent maintains executable persistent world state/rules;
- proxy representation compiles state constraints into proxy video;
- generative video model handles visual realization.

Taste value: **A**  
Execution transfer: **C/D**  
Instrument value: **B if released code/HF artifacts are used**

Core lesson:
> persistent causal dynamics and visual rendering need not be represented by the same model/state.

---

## ST-35 — STELLAR (older parent / instrument)
Date: 2026-02 / ICML 2026  
Type: spatial-semantic representation factorization  
Tier: peer-reviewed academic parent  
Primary: Microsoft Research / HF STELLAR

Deep-read: **YES**

Actually establishes:
- semantic invariance and spatial reconstruction create conflicting representation pressures;
- factorized semantic tokens + localization matrix can support both;
- B/L/H and B8/B16/B24 matched artifacts are released.

Taste value: **A**  
Recency role: **PARENT / CONTRAST, not recent-frontier evidence**  
Execution transfer: **A/B**  
Instrument value: **A**



---

# M. Latest harness-maturity, auto-research, R&D-process, and audio-proxy sources — added 2026-09-19

## ST-36 — Rethinking the Evaluation of Harness Evolution for Agents
Date: 2026-07-14  
Type: evaluation-correction / agent methodology paper  
Tier: II  
Primary:
- arXiv:2607.12227
- open code repository

Deep-read: **YES**

Actually establishes in the tested Terminal-Bench 2.1 setup:
- harness evolution repeatedly consumes task feedback and inference budget;
- under matched feedback/inference budgets, automatic harness evolution does not consistently beat simple parallel sampling / sequential refinement;
- evolved harness improvements show limited held-out generalization.

Does NOT establish:
- harness optimization is never useful;
- all self-improving harness methods overfit.

Taste value: **A+**  
Execution transfer: **B**  
Instrument value: **A/B**

Core lesson:
> when a method is itself a search process, compare it to simpler ways of spending the same search budget.

---

## ST-37 — Co-Evolving Harnesses and Models
Date: 2026-09-08  
Type: diagnosis-driven harness/weight adaptation paper  
Tier: II  
Primary: arXiv:2609.09134

Deep-read: **YES**

Actually establishes across seven tested enterprise-agent tasks:
- an expert can often exploit a harness evolved around a weaker model better than the weaker model;
- full expert-trajectory imitation under the evolved harness regresses the weaker model by 4–30 points in the reported Qwen3-Coder/Gemma 4 experiments;
- analysis attributes this to model–harness fit / strategy-competence mismatch;
- localized expert correction on the weaker model's own on-policy rollout restores compatibility better.

Taste value: **A+**  
Execution transfer: **B**  
Instrument value: **B**

Core lesson:
> harness quality is relational to the policy/competence it was evolved around.

---

## ST-38 — ModularRSI
Date: 2026-09-14  
Type: benchmark-disjoint modular harness evolution  
Tier: II  
Primary:
- arXiv:2609.14857
- Hugging Face paper page / GitHub

Deep-read: **YES at abstract/problem/method level**

Actually proposes/tests:
- evolution on an external 2,000-task set disjoint from downstream benchmarks;
- successful-vs-failed trajectory contrast;
- decomposition into five functional harness modules;
- independent evolution followed by integration;
- transfer to unseen tasks/models in reported experiments.

Taste value: **A-**  
Execution transfer: **B/C**  
Instrument value: **B**

Core lesson:
> once benchmark overfitting becomes a known confound, evolution data and evaluation data must be structurally separated.

---

## ST-39 — SoL-Pi
Date: 2026-09-17  
Type: open auto-research + harness-efficiency paper  
Tier: II/III  
Primary:
- arXiv:2609.20519
- NVlabs/SoL-Pi

Deep-read: **YES — full arXiv text + repo**

Actually establishes:
- explicit capability and efficiency metrics are frozen before search;
- held-out EdgeBench never feeds back into optimization;
- broad-to-deep search covers 152 proposal directions, 535 development environments, >3,000 runs and >60,000 agent-environment interactions;
- only four reusable mechanisms survive;
- reported EdgeBench performance is comparable to base Pi while token traffic drops 44.7–49.0% and API cost roughly one third.

Important caveat:
- authors explicitly state search counts do not establish a scaling law.

Taste value: **A+ for research-process design**  
Execution transfer: **A for individual mechanisms / F for full discovery process**  
Instrument value: **A**

Core lesson:
> auto-research needs frozen objectives, capability gates, development/held-out isolation, and evidence-preserving efficiency constraints.

---

## ST-40 — Atria Dawn Preview
Date: 2026-09-14  
Type: open agentic model + R&D-process study  
Tier: II/I-like internal task-record analysis  
Primary:
- arXiv:2609.15818
- atria-asi/Atria-Dawn-Preview

Deep-read: **YES — paper text + repo/model release**

Actually establishes:
- 744B-MoE-based Atria model is trained through a Verifiable Experience Pipeline linking task, trajectory, artifacts and externally checked outcomes;
- failure categories feed later task/environment refinement;
- development-process study covers 769 task records from 56 participants plus agent logs;
- agents frequently propose methods and execute revisions, while humans retain most final selection/judgment/steering in the reported project;
- roughly one third of completed AI-assisted tasks were rated by participants as infeasible without AI under comparable constraints.

Does NOT establish:
- autonomous research taste;
- a general productivity multiplier across labs;
- benchmark scores independent of harness/resource conditions.

Taste value: **A**  
Execution transfer: **F for training / C for process abstraction**  
Instrument value: **C**

Core lesson:
> project-level AI R&D should separate proposal, execution, interpretation, selection and steering rather than compress them into one “AI scientist” score.

---

## ST-41 — X-AuT
Date: 2026-09-10  
Type: speech-LLM compression study  
Tier: II  
Primary: arXiv:2609.11412

Deep-read: **YES**

Actually establishes:
- short behavioral probes are used to select encoder-layer combinations before expensive repair;
- removing encoder depth can cause decoder-level deletion/premature-EOS failures;
- progressive 18→16→14 compression beats direct 18→14 in the reported matched setting (5.75 vs 6.73 mean error);
- larger teacher distillation outperforms self-distillation in the reported setting;
- results are explicitly single-run and vary across benchmarks.

Taste value: **A for proxy/trajectory discipline**  
Execution transfer: **A/B**  
Instrument value: **B/A if code/checkpoints available**

Core lesson:
> a cheap proxy should predict task behavior, and the compression path can matter even when the endpoint architecture is identical.

---

## ST-42 — Qwen-Audio-VAE
Date: 2026-07-13  
Type: industrial audio-representation technical report  
Tier: II  
Primary: arXiv:2607.11738

Deep-read: **YES at problem/architecture/evidence level**

Actually establishes:
- audio VAE design is optimized jointly for reconstruction, bitrate and encoding throughput;
- causal/windowed/asymmetric encoder-decoder design plus latency-aware encoder pruning;
- trained on ~5M hours;
- reported encoding throughput is high enough to make large-scale downstream text-to-audio latent production a first-class design objective.

Taste value: **A-**  
Execution transfer: **C/D for training / B for representation profiling**  
Instrument value: **B**

Core lesson:
> a representation producer should be evaluated against the cost profile of the downstream consumer/training pipeline, not reconstruction alone.



---

# N. Long-horizon provenance/state/correction sources — added 2026-09-19

## ST-43 — Agora: Git as Shared Memory for Collective AutoResearch
Date: 2026-09-16  
Type: multi-agent research-memory / coordination technical report  
Tier: II/I-like sustained-run evidence  
Primary:
- arXiv:2609.18094
- yifanzhang-pro/Agora

Deep-read: **YES — full arXiv text + repo**

Actually establishes:
- research contributions are stored as immutable Git DAG nodes with parent lineage, typed claim tags and independent verification;
- 13 model workers operated for nearly 12 days with no assigned roles/central planner;
- 1,703 contributions, including 1,124 scored results and 165 verifications;
- best no-training weight-transfer score improves frozen 119.6M target from 3.3923 to 1.899 bpb;
- search rapidly concentrates into a dominant lineage and parallel rediscovery is common;
- one human intervention exposing the search monoculture redirects exploration;
- paper explicitly states a matched-compute controlled comparison is still needed to establish discovery-efficiency benefit of shared research state.

Does NOT establish:
- that Git-DAG memory causally beats all alternatives under matched compute;
- autonomous scientific taste;
- elimination of monoculture.

Taste value: **A+**  
Execution transfer: **B/C**  
Instrument value: **B/C at checked repo**

Core lesson:
> research memory should preserve claim/artifact/provenance/verification status, but shared memory can itself reshape attention and create monoculture.

---

## ST-44 — SURE-Map
Date: 2026-09-14  
Type: streaming geometry / self-correction study  
Tier: II  
Primary:
- arXiv:2609.15795
- RCL-Robotics/SURE-map

Deep-read: **YES — paper/abstract + open repo/training/eval**

Actually establishes:
- conventional single-view confidence is insufficient for streaming geometry;
- cross-view geometric uncertainty targets pose-depth correspondence consistency;
- local uncertainty-weighted correction addresses short-term pose/geometry errors;
- sparse keyframe-window inference addresses slow accumulated scale drift;
- open code, uncertainty checkpoint, frozen backbone path, training/evaluation configs are provided.

Taste value: **A+**  
Execution transfer: **A/B**  
Instrument value: **A**

Core lesson:
> self-correction should match empirically distinct error time constants rather than add generic local/global modules.

---

## ST-45 — AlayaVista
Date: 2026-09-13  
Type: streaming video world-model architecture  
Tier: II  
Primary:
- arXiv:2609.14462
- AlayaLab/AlayaVista

Deep-read: **YES at problem/architecture/artifact boundary**

Actually establishes/proposes:
- perspective-only world models face off-screen persistence burden under camera motion;
- system factorizes persistent 360° panoramic latent world evolution from perspective viewport rendering/refinement;
- chunk-autoregressive generation and few-step distillation recover streaming efficiency;
- MUGEN contains 1,318h ≥4K panoramic video with semantic/geometric annotations.

Artifact caveat:
- checked repo roadmap still marks inference code and pretrained weights unreleased.

Taste value: **A**  
Execution transfer: **D/F**  
Instrument value: **C currently**

Core lesson:
> persistent world state and high-fidelity local observation need not use the same representation.

---

## ST-46 — Taming Long-form Text-to-Speech / LACI
Date: 2026-09-15  
Type: inference-only diagnosis/repair study  
Tier: II  
Primary: arXiv:2609.16989

Deep-read: **YES at mechanism/result/boundary level**

Actually establishes:
- strong short-form AR TTS models can enter catastrophic skip/hallucination regimes on long prompts/references;
- alignment dynamics can detect failure onset in near realtime;
- method rolls back only to onset, temporarily imposes attention constraints, then removes them;
- Qwen3-TTS-0.6B worst-of-10 WER above 1500 words reported 35.2%→3.4%;
- catastrophic >30% WER rate under long-reference condition reported 26%→<1%;
- localized wSIM metric exposes speaker-similarity failures hidden by global SIM;
- very extreme VoxCPM2 regimes remain less fully repaired.

Taste value: **A+**  
Execution transfer: **A+**  
Instrument value: **A**

Core lesson:
> when damage is long but causal onset is local, rollback/temporary intervention can dominate global constraints or full restart.



---

# O. Final frontier-wave sources — added 2026-09-19

## ST-47 — Figure Helix 2.5
Date: 2026-09-17  
Type: frontier robotics deployment/pretraining report  
Tier: II/III  
Primary:
- https://www.figure.ai/news/helix-2-5-zero-shot-30-home-generalization
- https://www.figure.ai/news/introducing-index

Deep-read: **YES — official result + pretraining ablation + Index data pipeline**

Actually establishes/reports:
- same task-specification data, architecture, optimization and evaluation are compared with vs without Index pretraining;
- reported strict zero-shot full-task success across 30 unseen homes: 9% from-scratch vs 56% Index-pretrained;
- no evaluation-home data or adaptation;
- three behaviors are still specified through task-specific data collected elsewhere;
- action-prediction loss scales smoothly with Index pretraining data and is reported as forecasting the largest run;
- Index is a human-behavior data pipeline rather than robot-only demonstration collection.

Does NOT establish:
- arbitrary unseen-task ICL;
- universal household-robot reliability;
- that action-prediction loss is a sufficient predictor of downstream task success;
- independent validation.

Taste value: **A+**  
Execution transfer: **F for reproduction / B for conceptual proxy studies**  
Instrument value: **F/C**

Core lesson:
> robot pretraining value should be decomposed into environment transfer, task ICL, sample efficiency, adaptation speed and peak finetuned performance.

---

## ST-48 — Odyssey-3
Date: 2026-09-15  
Type: foundation world-model / physical-agent release  
Tier: II/IV  
Primary:
- https://odyssey.systems/introducing-odyssey-3

Deep-read: **YES — official architecture/use-case narrative and downstream adaptation claims**

Actually establishes/reports:
- one pretrained autoregressive diffusion world model is used as a foundation across robot arms, humanoids, driving, drones and games;
- downstream action/policy heads can be trained while keeping the pretrained representation frozen in several settings;
- reported downstream adaptation often uses tens of hours or less of experiential data;
- 20h simulated driving policy reaches ~77% of the real-data policy's reported distance between safety interventions;
- the model is also used as an interactive environment for agent training.

Does NOT establish:
- one universal transferable physical representation;
- a controlled decomposition of which pretraining data/property causes transfer;
- small-team reproducibility.

Taste value: **A**  
Execution transfer: **D/F**  
Instrument value: **D currently**

Core lesson:
> a world model can be treated as a reusable physical representation layer, not only a simulator.

---

## ST-49 — Decart Oasis 3
Date: 2026-06-10, active current product in final scan  
Type: interactive world-model infrastructure  
Tier: III/IV  
Primary:
- https://decart.ai/oasis

Deep-read: **YES at product/technical-contract level**

Actually establishes/reports:
- action-conditioned closed-loop world generation;
- synchronized multi-camera views;
- geometry-aware physical-AI target;
- reported <200ms end-to-end / 22 FPS at the stated configuration;
- API integration for robot/AV policy training.

Does NOT establish:
- open model internals;
- consumer policy transfer fidelity relative to real environments;
- a universal simulator-quality metric.

Taste value: **A-**  
Execution transfer: **C/D via API / F for model training**  
Instrument value: **C**

Core lesson:
> world-model usefulness may require fidelity under realtime control, not offline visual fidelity alone.

---

## ST-50 — A.X K2 ALM
Date: technical/model-card update active in Aug–Sep 2026  
Type: speech-model technical report / HF model card  
Tier: II  
Primary:
- https://huggingface.co/skt/A.X-K2-ALM

Deep-read: **YES — detailed model card/training design**

Actually establishes/reports:
- speech modality is added around a fully frozen 20B-A2.7B LLM backbone;
- trainable speech encoder/adapter/VAD/decoder carry the modality extension;
- two-stage alignment + frozen-LLM-in-the-loop self-distillation preserves text-input behavior by construction;
- context-aware VAD uses adapter/LLM representations;
- all paths are streaming.

Artifact caveat:
- current model card says model weights are planned for release / coming soon.

Taste value: **A**  
Execution transfer: **B conceptually / D currently**  
Instrument value: **D/C until weights are actually available**

Core lesson:
> multimodal extension can be formulated as an interface-learning problem around an immutable foundation model.

---

## ST-51 — Tencent SAS: Simple Attention Sparsification
Date: 2026-09-11 paper / Sep 2026 HF+code release  
Type: sparse-attention mechanism + open checkpoint/code  
Tier: II  
Primary:
- arXiv:2609.13141
- https://huggingface.co/tencent/Simple-Attention-Sparsification
- https://github.com/Tencent-Hunyuan/Simple-Attention-Sparsification

Deep-read: **YES — objective, mechanism, released artifact**

Actually establishes:
- dense-attention-score distillation is not directly aligned with context utility under a fixed sparse budget;
- continuous gates inside attention logits restore gradient flow from LM loss to selector ranking;
- improvements are strongest under tighter context budgets;
- Qwen3-based checkpoints and code are public.

Taste value: **A+**  
Execution transfer: **A/B**  
Instrument value: **A**

Core lesson:
> a convenient teacher/proxy target should be replaced when it does not preserve downstream ranking under the constrained regime.

---

## ST-52 — Tencent WeVisDoc
Date: 2026-09-17  
Type: end-to-end document parsing / residual-error-guided data construction  
Tier: II  
Primary:
- arXiv:2609.20423
- https://huggingface.co/tencent/WeVisDoc-2B
- https://huggingface.co/tencent/WeVisDoc-4B
- https://github.com/Tencent/WeVisDoc

Deep-read: **YES — two-stage training logic + open 2B/4B artifacts**

Actually establishes:
- Stage I expands semantic/structural/appearance coverage;
- Stage II uses a held-out probe to measure residual errors in fixed visual-structural clusters;
- diagnostics guide targeted data construction and target-token-budget reallocation;
- 2B and 4B open checkpoints are released.

Taste value: **A- question-forming / C for our preferred execution style**  
Execution transfer: **A/B**  
Instrument value: **A**

Core lesson:
> after generic coverage expansion, data value can become learner-relative and residual-error-conditioned.

---

## ST-53 — General Intuition final-scan status
Date: checked 2026-09-19  
Type: startup research program / world+action model thesis  
Tier: II/IV depending artifact  
Primary:
- https://www.generalintuition.com/
- MIRA technical report/code
- prior IRIS / Delta-IRIS / DIAMOND / GAIA-2 lineage

Deep-read: **YES at program-lineage level; NO new Sep 18–19 matched artifact found**

Actually establishes:
- coherent world-model/action-model research lineage;
- action-labeled gameplay data as a major training resource;
- MIRA as an open realtime multiplayer world-model artifact.

Final-scan decision:
> retain as a strong ongoing monitor and lineage source, but do not manufacture a new "September model" claim from company visibility alone.

Taste value: **A lineage / C for new-current artifact**  
Execution transfer: **B/C via MIRA, lower for unreleased frontier work**  
Instrument value: **B for existing artifacts**

Core lesson:
> company research thesis and currently released experimental artifact must be scored separately.


---

# FINAL ADDENDUM SOURCES — Sep 17–19 2026

These entries close the broad source ledger. They are not a new weekly-watch list.

---

## FINAL-01 — Infinite-Parameter LLMs
Date: 2026-09-16  
Type: architecture / continual-live-learning preprint  
Tier: II  
Primary: arXiv:2609.18842

Deep-read: **YES — paper thesis**

Actually establishes:
- live data can condition a compact hypernetwork that generates low-rank modulation of a shared base network;
- a Bayesian belief over latent code is updated online during a session;
- effective weights are re-derived as that belief changes;
- paper explicitly compares the intended memory location against in-context/retrieval-style use.

Does NOT establish:
- that runtime-generated weights dominate RAG/ICL universally;
- low-cost practical deployability on current open frontier models.

Taste value: **A**  
Execution transfer: **B/C conceptually, current artifact must be re-verified before pilot**  
Instrument value: **C until runnable checkpoint/code is confirmed**

Core pressure:
> knowledge supplied at runtime need not remain in the context; it can become generated effective parameters.

---

## FINAL-02 — ProgramDistill
Date: 2026-09-16  
Type: software-engineering benchmark / executable-specification study  
Tier: II  
Primary: arXiv:2609.18805

Deep-read: **YES — full paper sections**

Actually establishes:
- desired software behavior can be elicited from a working reference whose source is hidden;
- 1,975 replay-verified behaviors across 26 applications are factorized into 4,063 tasks;
- prerequisite lineages create a controlled restoration-depth axis;
- replay traces serve as behavioral specifications/verifiers;
- agent observation effort becomes increasingly important as reconstruction burden rises.

Does NOT establish:
- executable behavior as complete semantic correctness for all software;
- that one verifier has universal certification authority.

Taste value: **A**  
Execution transfer: **B/C**  
Instrument value: **B pending exact release/runtime audit**

Core pressure:
> specification source and verifier role are separable design objects.

---

## FINAL-03 — ComposeCL
Date: 2026-09-07  
Type: continual-learning mechanism-composition study  
Tier: II  
Primary:
- arXiv:2609.06986
- https://github.com/cozheyuanzhangde/compose-cl

Deep-read: **YES — paper/project/code summary**

Actually establishes:
- 100 sequential QA tasks × 3 datasets × 3 seeds;
- no individual continual-learning mechanism remains strong across the full horizon;
- full 2^4 factorial over replay, self-distillation, weight anchor and merged LoRA;
- best composition raises average final retention 1.2% → 34.9%;
- replay + merged LoRA interact super-additively across all three datasets;
- task-level successive halving reduces a 90-configuration search over longer horizons;
- official code/datasets are open; checkpoints/generated outputs are not included.

Does NOT establish:
- catastrophic forgetting as solved (34.9% remains far from perfect);
- generalization to paraphrased/new formulations from memorization alone;
- preservation of all general model capabilities.

Taste value: **A+**  
Execution transfer: **A/B**  
Instrument value: **A**

Core pressure:
> mechanism composition is scientific when complementary failure sources and interaction effects are explicitly identified.

---

## FINAL-04 — ActObs / Don't Mask the Environment
Date: 2026-09-17  
Type: agent SFT→RL mechanism study  
Tier: II  
Primary: arXiv:2609.20715

Deep-read: **YES — mechanism/result chain**

Actually establishes:
- standard agent SFT commonly supervises action tokens while masking environment observations from loss;
- ActObs also predicts existing observation tokens without adding data, sequence tokens, parameters or forward passes;
- SFT endpoints are similar, but equal downstream GRPO training diverges;
- 4B improves pass@k across tested budgets on Terminal-Bench 2.0;
- 8B trades some pass@1 for higher pass@16 / broader task coverage;
- gains transfer to unseen aider-polyglot tasks;
- action and observation gradients become nearly orthogonal;
- action-only SFT damages consequence prediction relative to base;
- joint supervision preserves entropy and changes later exploration.

Taste value: **A+**  
Execution transfer: **A/B**  
Instrument value: **B/A if training artifacts are verified**

Core pressure:
> a seemingly innocuous loss mask in SFT can determine what internal consequence model survives into RL.

---

## FINAL-05 — Agile-WAM
Date: 2026-09-17  
Type: tactile world-action model / robotics  
Tier: II  
Primary: arXiv:2609.20761

Deep-read: **YES — core design/result**

Actually establishes:
- vision and tactile streams exhibit different temporal dynamics;
- visual latent is supervised at a larger temporal offset while tactile latent uses next-frame prediction;
- shared latent supports action and future-state flow matching;
- evaluated on 9 simulation + 5 real contact-rich manipulation tasks;
- reports 29.4% relative real-world success gain with 11.9ms inference latency.

Does NOT establish:
- one universal optimal temporal horizon for all multimodal systems.

Taste value: **A**  
Execution transfer: **B/C**  
Instrument value: **B; verify runnable code/checkpoints before candidate use**

Core pressure:
> temporal alignment does not imply equal supervision horizon across modalities.

---

## FINAL-06 — FAMOS
Date: 2026-09-17  
Type: 3D articulation / structured perception  
Tier: II  
Primary: arXiv:2609.20817

Deep-read: **YES — paper/project description**

Actually establishes:
- articulation is inferred from a sparse unordered set of partial point clouds rather than one view;
- state-wise/global attention aggregates evidence across observed states;
- observed-articulation-span objective explicitly rewards use of motion evidence;
- procedural self-annotated assets scale training.

Taste value: **A**  
Execution transfer: **B/C**  
Instrument value: **B/C pending exact code/model release audit**

Core pressure:
> for articulation, observed state transitions may be a better evidence unit than category-level single-view shape prior.

---

## FINAL-07 — Panda Diplomacy
Date: 2026-09-01  
Type: scientific foundation-model pretraining across particle detectors  
Tier: II  
Primary: arXiv:2609.00611

Deep-read: **YES — abstract/results level**

Actually establishes:
- the same point-cloud self-distillation framework is pretrained with minimal changes across three qualitatively different detector modalities;
- 1,000 labeled downstream images can match/exceed specialized FM baselines that use much more supervision;
- reported label-efficiency improvements reach ~70× on one setting and up to ~1,000× on another;
- simple probes reveal latent features associated with particle causality / track curvature.

Taste value: **A-**  
Execution transfer: **B/C**  
Instrument value: **C/B depending public checkpoint/code availability**

Core pressure:
> detector-specific task architecture may be the wrong sharing unit if sensor-level physical structure is common.

---

## FINAL-08 — Pelican-Sim 1.0
Date: 2026-09-10  
Type: embodied world-model technical report  
Tier: II  
Primary: arXiv:2609.12036 / official project page

Deep-read: **YES — report/project details**

Actually establishes:
- unified 28-D action representation;
- numerical + URDF-rendered visual action conditioning;
- sparse MoE for heterogeneous dynamics;
- four-step rollout generation with reported 5.67× speedup;
- approximately one million real/sim trajectories;
- downstream consumer tests include data generation, policy evaluation, action selection and policy improvement;
- policy-evaluation correlation reported at Pearson 0.994 across five checkpoints;
- 500 generated + 50 demonstrations per task raises RoboTwin policy success 70% → 93% in the reported setting.

Artifact status:
> official project page currently says **Code / Models — Coming soon**.

Taste value: **A**  
Execution transfer: **C/D**  
Instrument value: **D/C now — do not count announced release as current access**

Core pressure:
> world-model quality should be judged by downstream policy decisions, not only video fidelity.

---

# Final provenance corrections

## General Intuition
Strong existing MIRA/world-model lineage and high frontier-pressure value.
No equally detailed new Sep 18/19 matched artifact found in the final scan.

Status:
> **monitor only; do not manufacture a new genealogy from company visibility.**

## Decart research-page resurfacing
A result newly highlighted on a September company research page may have an underlying arXiv date months earlier.

Status:
> **artifact date, not promotion-page date, determines recency.**

---

# Ledger closed

This source ledger is now closed to default broad crawling.

Future additions require one of:
- concrete CT candidate prior audit;
- new artifact that materially changes pilot feasibility;
- clear evaluation-correction / negative-result phase;
- genuinely changed premise.
