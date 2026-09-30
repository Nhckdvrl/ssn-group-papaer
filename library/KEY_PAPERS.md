# Key Papers — Curated Anchors

**Last verified:** 2026-09-29

This is not a comprehensive bibliography. These are papers worth rereading because they define a primitive, change an assumption, expose a failure, or provide a reusable open baseline.

**Read these genealogically, not as an idea menu.** For each important anchor, reconstruct the parent baseline/belief, pressure, changed premise, earliest revealing analysis, and why the final contribution is distinct from adjacent related work. See `README.md` for the genesis template.

---

## Research craft / baseline discipline

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| RC01 | **ResNet strikes back: An improved training procedure in timm** (2021) | ANCHOR / CRAFT | A strong reminder that weak/old baseline recipes can manufacture “novel method” gains. | https://arxiv.org/abs/2110.00476 |

---

## Post-training / RL / alignment

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| PT01 | **Training language models to follow instructions with human feedback** (InstructGPT, 2022) | ANCHOR | Canonical SFT→RM→PPO pipeline; useful for remembering what later methods are changing. | https://arxiv.org/abs/2203.02155 |
| PT02 | **Direct Preference Optimization** (2023) | ANCHOR | Reparameterizes RLHF into a direct preference objective; classic example of changing the optimization object rather than adding machinery. | https://arxiv.org/abs/2305.18290 |
| PT03 | **DeepSeekMath** (2024) | ANCHOR / ARTIFACT | Introduces GRPO in a real open training stack; baseline for modern reasoning RL. | https://arxiv.org/abs/2402.03300 |
| PT04 | **Tulu 3: Pushing Frontiers in Open Language Model Post-Training** (2024) | ANCHOR / ARTIFACT | One of the best open end-to-end recipes; includes methods that failed as well as those that worked. | https://arxiv.org/abs/2411.15124 |
| PT05 | **DeepSeek-R1** (2025) | BRIDGE / ARTIFACT | Changed the premise around large-scale RL and reasoning emergence; important training-regime anchor. | https://arxiv.org/abs/2501.12948 |
| PT06 | **DAPO: An Open-Source LLM Reinforcement Learning System at Scale** (2025) | BRIDGE / ARTIFACT | Decomposes large-scale RL instability into concrete algorithm/system choices; strong reproducibility reference. | https://arxiv.org/abs/2503.14476 |
| PT07 | **Group Sequence Policy Optimization (GSPO)** (2025) | BRIDGE | Makes sequence vs token optimization unit itself the object. | https://arxiv.org/abs/2507.18071 |
| PT08 | **Beyond the 80/20 Rule: High-Entropy Minority Tokens Drive Effective RL for LLM Reasoning** (NeurIPS 2025) | BRIDGE | Good example of turning “RL works” into a learning-signal decomposition at token level. | https://arxiv.org/abs/2506.01939 |
| PT09 | **The Surprising Effectiveness of Negative Reinforcement in LLM Reasoning** (NeurIPS 2025) | BRIDGE | Correct and incorrect rollouts are not symmetric; a clean example of decomposition → mechanism → small method. | https://arxiv.org/abs/2506.01347 |

---

## Reasoning / test-time compute

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| RS01 | **Self-Consistency Improves Chain of Thought Reasoning** (2022) | ANCHOR | Moves inference from one greedy reasoning path to marginalizing multiple paths. | https://arxiv.org/abs/2203.11171 |
| RS02 | **Tree of Thoughts** (2023) | ANCHOR | Makes explicit search state / branching part of inference rather than only sampling. | https://arxiv.org/abs/2305.10601 |
| RS03 | **Let's Verify Step by Step** (2023/ICLR 2024) | ANCHOR | Final-answer supervision can be too late; step-level supervision becomes the object. | https://arxiv.org/abs/2305.20050 |
| RS04 | **Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters** (2024) | BRIDGE | Key move from “more test-time compute” to **compute allocation conditioned on problem difficulty**. | https://arxiv.org/abs/2408.03314 |

---

## Architecture / recurrence / memory

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| AR01 | **Mamba: Linear-Time Sequence Modeling with Selective State Spaces** (2023) | ANCHOR / ARTIFACT | Makes input-dependent selection the key repair for SSMs on discrete language. | https://arxiv.org/abs/2312.00752 |
| AR02 | **Transformers are SSMs / Mamba-2** (ICML 2024) | ANCHOR / ARTIFACT | Unifies recurrence and attention through structured state-space duality; useful antidote to surface-level architecture taxonomy. | https://arxiv.org/abs/2405.21060 |
| AR03 | **RecurrentGemma** (2024) | ANCHOR / ARTIFACT | Open recurrent/local-attention language models; useful strong public architecture baseline. | https://arxiv.org/abs/2404.07839 |
| AR04 | **Leave No Context Behind: Infini-attention** (2024) | ANCHOR | Clean attention + compressive-memory hybrid and a useful reference for “exact vs compressed history”. | https://arxiv.org/abs/2404.07143 |
| AR05 | **Titans: Learning to Memorize at Test Time** (2025) | BRIDGE | Reframes long-term memory as test-time learning in a neural memory rather than a fixed recurrent vector. | https://arxiv.org/abs/2501.00663 |
| AR06 | **Scaling up Test-Time Compute with Latent Reasoning: A Recurrent Depth Approach (Huginn)** (2025) | ANCHOR / ARTIFACT | Open depth-recurrent model where extra test-time depth reuses a small recurrent core; direct baseline for recurrent-depth science. | https://arxiv.org/abs/2502.05171 |
| AR07 | **Scaling Latent Reasoning via Looped Language Models (Ouro)** (2025) | FRONTIER / ARTIFACT | Open looped-LM family; makes iterative latent computation a pretraining primitive. | https://arxiv.org/abs/2510.25741 |
| AR08 | **Mamba-3: Improved Sequence Modeling using State Space Principles** (2026) | FRONTIER / ARTIFACT | Current SSM lineage update; reread before making claims about what “modern Mamba” can/cannot do. | https://arxiv.org/abs/2603.15569 |
| AR09 | **Latent Chain-of-Thought? Decoding the Depth-Recurrent Transformer** (2025) | BRIDGE / NEGATIVE | Huginn-specific negative/diagnostic reference: latent-CoT readouts are probe-sensitive and additional recurrence gives limited gains in the tested arithmetic setting. | https://arxiv.org/abs/2507.02199 |

---

## MoE / routing

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| MOE01 | **Switch Transformers** (2021) | ANCHOR | Simplified top-1 sparse routing; canonical scale/training-stability baseline. | https://arxiv.org/abs/2101.03961 |
| MOE02 | **Mixture-of-Experts with Expert Choice Routing** (2022) | ANCHOR | Reverses token→expert allocation into expert→token selection; useful reminder that routing primitive itself is a design choice. | https://arxiv.org/abs/2202.09368 |
| MOE03 | **DeepSeekMoE: Towards Ultimate Expert Specialization** (ACL 2024) | ANCHOR | Shared vs routed experts and fine-grained expert segmentation; important specialization reference. | https://aclanthology.org/2024.acl-long.70/ |

---

## Mechanistic interpretability / model science

| ID | Paper / project | Role | Why reread | Link |
|---|---|---|---|---|
| MI01 | **In-context Learning and Induction Heads** (2022) | ANCHOR | Classic capability↔mechanism emergence argument; useful for causal-evidence standards. | https://arxiv.org/abs/2209.11895 |
| MI02 | **Function Vectors in Large Language Models** (ICLR 2024) | ANCHOR / ARTIFACT | Compact causal task representations; good example of moving from correlation to intervention. | https://arxiv.org/abs/2310.15213 |
| MI03 | **Towards Monosemanticity** (Anthropic, 2023) | ANCHOR | Changes unit of analysis from neurons to learned features. | https://www.anthropic.com/research/towards-monosemanticity-decomposing-language-models-with-dictionary-learning |
| MI04 | **Tracing the thoughts of a large language model** (Anthropic, 2025) | BRIDGE | Moves from feature discovery toward computational/attribution graphs. | https://www.anthropic.com/research/tracing-thoughts-language-model |
| MI05 | **A global workspace in language models** (Anthropic, 2026) | FRONTIER | Current example of posing a broad functional question, then attacking it with multiple causal properties rather than one probe. | https://www.anthropic.com/research/global-workspace |
| MI06 | **MIB: A Mechanistic Interpretability Benchmark** (ICML 2025) | BASELINE / ARTIFACT | Standardized circuit-localization and causal-variable tracks; essential before claiming a new MI method improves real mechanistic recovery. | https://proceedings.mlr.press/v267/mueller25a.html |
| MI07 | **SAEBench** (ICML 2025) | BASELINE / ARTIFACT | Shows proxy/reconstruction gains do not reliably imply practical SAE utility; provides 200+ released SAEs and multiple evaluation axes. | https://proceedings.mlr.press/v267/karvonen25a.html |
| MI08 | **Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability** (JMLR 2025) | FOUNDATION | Unifies patching, circuits, SAE/DAS/steering under explicit intervention-preserving abstractions; useful language for separating readability from causal explanation. | https://www.jmlr.org/papers/v26/23-0058.html |
| MI09 | **The Non-Linear Representation Dilemma** (NeurIPS 2025) | NEGATIVE / FOUNDATION | Unrestricted nonlinear alignment can map random/non-solving networks to algorithms with perfect IIA; makes mediator complexity/falsifiability a first-class issue. | https://proceedings.neurips.cc/paper_files/paper/2025/hash/dbb98528c9870377f3f0d133aae6050b-Abstract-Conference.html |
| MI10 | **Sparse Autoencoders Trained on the Same Data Learn Different Features** (ICLR 2026) | NEGATIVE / MEASUREMENT | Same model/data, different seeds can yield markedly different SAE dictionaries; strong warning against treating one dictionary as canonical truth. | https://proceedings.iclr.cc/paper_files/paper/2026/hash/3c1fe56b043848b211030c202764c6a7-Abstract-Conference.html |
| MI11 | **Mechanistic Interpretability Should Prioritize Feature Consistency in SAEs** (ACL 2026) | MEASUREMENT | Turns run-to-run consistency into an explicit evaluation axis and shows architecture choices can materially change reproducibility. | https://aclanthology.org/2026.acl-long.99/ |
| MI12 | **Narrow Finetuning Leaves Clearly Readable Traces in Activation Differences** (ICLR 2026) | BASELINE / NEGATIVE / ARTIFACT | Simple activation differences strongly reveal narrow finetune objectives and expose model-organism external-validity problems; strong baseline-first paper. | https://proceedings.iclr.cc/paper_files/paper/2026/hash/3b939edfdf9c1211fb764a888078f13d-Abstract-Conference.html |
| MI13 | **Crosscoding Through Time** (ACL 2026) | FRONTIER / ARTIFACT | Uses crosscoders to make representation development across checkpoints the object; useful example of a tool opening a new scientific question rather than merely visualizing a behavior. | https://aclanthology.org/2026.acl-long.60/ |
| MI14 | **Many Circuits, One Mechanism** (TMLR 2026 Featured) | NEGATIVE / MEASUREMENT | Structurally distinct circuits can be functionally equivalent; cross-condition transfer and edge-level tests change the evidential standard. | https://arxiv.org/abs/2606.06267 |
| MI15 | **Interpretability Can Be Actionable** (ICML 2026 Position) | CRAFT / EVALUATION | Argues interpretation should be judged by concrete, validated downstream decisions/interventions rather than elegance alone. | https://arxiv.org/abs/2605.11161 |
| MI16 | **Diff Mining: Logit Differences Reveal Finetuning Objectives** (2026 preprint) | FRONTIER / SIMPLE BASELINE | Cheap output-logit differences can outperform state-of-the-art internal model-diffing methods on finetune-objective discovery; critical comparative baseline for future model-diff work. | https://arxiv.org/abs/2608.26462 |
| MI17 | **Automated Interpretability Metrics Do Not Distinguish Trained and Random Transformers** (ICLR 2026) | NEGATIVE / MEASUREMENT | Strong construct-validity warning: multiple automated interpretability metrics can look good even on random transformers, so score improvement need not reflect learned computation. | https://proceedings.iclr.cc/ |
| MI18 | **Simple LLM Baselines are Competitive for Model Diffing** (2026) | NEGATIVE / BASELINE | Direct ownership boundary for model diffing: defines generalization/interestingness/abstraction desiderata and finds a simple LLM baseline competitive with SAE diffing. | https://arxiv.org/abs/2602.10371 |
| MI19 | **From Shortcut to Induction Head: How Data Diversity Shapes Algorithm Selection in Transformers** (NeurIPS 2025) | FOUNDATION / MODEL SCIENCE | Shows training-data diversity can select between a brittle positional shortcut and a generalizable induction-head algorithm; a strong example of MI explaining mechanism selection rather than a behavioral anomaly. | https://proceedings.neurips.cc/paper_files/paper/2025/hash/6499b639e8a4b5c9a780d9b88c09722f-Abstract-Conference.html |
| MI20 | **Capability Emergence Can Be Forecast** (2026 preprint) | FRONTIER / DEVELOPMENTAL | Turns mechanistic precursor claims into actual forecasts with lead time, calibration, blind gates and negative controls; important ownership boundary for developmental-interpretability ideas. | https://arxiv.org/abs/2609.19000 |
| MI21 | **LLM Circuit Analyses Are Consistent Across Training and Scale** (NeurIPS 2024) | FOUNDATION / DEVELOPMENTAL | Tracks circuit formation across Pythia checkpoints and scale; exact heads can turn over while higher-level algorithms persist. Parent for asking what level of mechanism is stable. | https://proceedings.neurips.cc/paper_files/paper/2024/hash/47c7edadfee365b394b2a3bd416048da-Abstract-Conference.html |
| MI22 | **PolyPythias: Stability and Outliers across Fifty Language Model Pre-Training Runs** (ICLR 2025) | FOUNDATION / ARTIFACT / POPULATION | 50 pretraining runs, 10 seeds per size, ~7k checkpoints. Makes training stability a population object; behavior/representation/training-map analyses provide the substrate for population-level mechanism studies. | https://proceedings.iclr.cc/paper_files/paper/2025/hash/d611d06e3207330555fbc10810e70163-Abstract-Conference.html |
| MI23 | **Which Attention Heads Matter for In-Context Learning?** (ICML 2025) | FOUNDATION / DEVELOPMENTAL | Reconciles induction-head and function-vector explanations under matched causal comparison and finds a developmental transition from induction to FV roles. Exemplary dense-lineage idea growth. | https://proceedings.mlr.press/v267/yin25e.html |
| MI24 | **A Training-Time Sign Flip During the Formation of an IOI Circuit** (ICML 2026 MI Workshop) | BASELINE / ARTIFACT / DEVELOPMENTAL | Replicates one training-time causal reversal across Pythia scales and PolyPythia variants; useful strong baseline showing developmental mechanism measurements can be population-replicated. | https://github.com/Tejas7007/ICML_2026_MIW_IOI_Sign_Flip |

---

## Omni / speech

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| VO01 | **Moshi: a speech-text foundation model for real-time dialogue** (2024) | ANCHOR / ARTIFACT | Full duplex as a modeling problem; parallel user/system streams and physical-time constraints. | https://arxiv.org/abs/2410.00037 |
| VO02 | **Qwen2.5-Omni Technical Report** (2025) | ANCHOR / ARTIFACT | Thinker–Talker separation, streaming multimodal input, text/speech co-generation; useful architecture reference. | https://arxiv.org/abs/2503.20215 |
| VO03 | **τ-Voice: Benchmarking Full-Duplex Voice Agents on Real-World Domains** (ICML 2026) | PARENT / BENCHMARK / ARTIFACT | Direct grounded-task comparison between strong text/half-duplex agents and full-duplex voice agents; establishes a substantial capability transition rather than a pure ASR problem. | https://arxiv.org/abs/2603.13686 |
| VO04 | **Stream RAG: Instant and Accurate Spoken Dialogue Systems with Streaming Tool Usage** (ICML 2026) | PARENT / METHOD | Starts retrieval/tool preparation before the user finishes speaking; important parent for overlapping perception and action. | https://arxiv.org/abs/2510.02044 |
| VO05 | **Hierarchical Acoustic-Semantic Modeling / Lychee-FD** (ACL 2026 Outstanding) | PARENT / ARTIFACT | Finds acoustic–semantic gradient conflict in native full-duplex SpeechLM training and separates parameters hierarchically. | https://aclanthology.org/2026.acl-long.419/ |
| VO06 | **Full-Duplex-Bench v3** (2026) | FRONTIER / BENCHMARK / ARTIFACT | Real-human disfluency plus multi-step tool use; useful diagnostic substrate for interaction failures without requiring us to invent a new benchmark. | https://arxiv.org/abs/2604.04847 |
| VO07 | **Speech-Hands** (ACL 2026) | PARENT / ROUTING | Shows naive integration of noisy speech hypotheses can hurt and studies when an Omni model should rely on specialist audio perception. | https://aclanthology.org/2026.acl-long.1997/ |
| VO08 | **OmniInteract** (2026) | FRONTIER / BENCHMARK | Tests native online audiovisual interaction and exposes a gap between offline capability and streaming interaction. | https://arxiv.org/abs/2605.26485 |
| VO09 | **NemotronLabs VoiceChat** (2026) | FRONTIER / ARTIFACT | Open 11B full-duplex speech-to-speech model with a parallel structured function-call stream; practical model-level foothold. | https://arxiv.org/abs/2609.21967 |
| VO10 | **Qwen-Audio-Agent Technical Report** (2026) | FRONTIER / ARTIFACT | Foreground dialogue plus background delegated agents, explicit task state, cancellation/modification, result delivery, and persistent memory; practical asynchronous-runtime foothold. | https://arxiv.org/abs/2609.25195 |
| VO11 | **How Should LLMs Listen While Speaking?** (2026) | FRONTIER / ARCHITECTURE | Contrasts direct channel fusion with cross-attention routing and exposes grounding-vs-context-corruption pressure under overlapping speech. | https://arxiv.org/abs/2605.10199 |
| VO12 | **Full-Duplex Speech Models Take the Floor When Asked, Not When Needed** (2026) | FRONTIER / BEHAVIOR | Separates turn opportunity from semantic need to intervene; important ownership boundary for proactive-speaking research. | https://arxiv.org/abs/2609.19596 |
| VO13 | **Speaking While Listening: Full-Duplex Survey and Empirical Audit** (EMNLP 2026 Main) | SURVEY / FIELD MAP | L0–L3 architecture hierarchy, T×I×R ontology, state machine, and the crucial empirical result that architecture levels are not a progress ladder; use before making any full-duplex frontier claim. | https://arxiv.org/abs/2606.19453 |
| VO14 | **DuplexCascade** (2026) | PARENT / ARTIFACT | Important counterexample to “native end-to-end is necessary”: VAD-free cascaded ASR–LLM–TTS with micro-turns preserves strong text-LLM intelligence while supporting duplex interaction. | https://arxiv.org/abs/2603.09180 |
| VO15 | **Realtime-Venus** (2026) | FRONTIER / ARTIFACT | Open 9B full-duplex frontend plus asynchronous Harness; request-time context capture, background work, private feedback, freshness and playback-aware delivery make computational boundaries directly instrumentable. | https://arxiv.org/abs/2609.13814 |
| VO16 | **A frontend-backend architecture for tool calls in full-duplex speech models** (2026) | FRONTIER / ARCHITECTURE | NVIDIA design: streaming duplex frontend delegates transcript to a text backend and reinjects results; strong evidence for 2026 foreground/backend convergence. | https://arxiv.org/abs/2609.19334 |
| VO17 | **Unified Audio Intelligence Without Regressing on Text Intelligence (Audex)** (2026) | COUNTEREXAMPLE / FRONTIER | Large-scale unified audio-text decoder reports strong audio capability with little text regression; prevents overclaiming that separation/modularity is inherently necessary. | https://arxiv.org/abs/2607.05196 |
| VO18 | **The Latent Bridge: A Continuous Slow-Fast Channel for Real-Time Game Agents** (2026) | CROSS-DOMAIN / ARTIFACT | Fast reactive + slow reasoning models with communication as the load-bearing variable; text/latent bridge results and channel interference are a direct cross-domain ownership boundary. | https://arxiv.org/abs/2606.24470 |

---

## VLA / robotics

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| VLA01 | **Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware (ACT)** (2023) | ANCHOR / ARTIFACT | Action chunking grows directly from compounding-error / high-precision control pressure. | https://arxiv.org/abs/2304.13705 |
| VLA02 | **RT-2** (2023) | ANCHOR | Converts actions to language-like tokens to unify web semantics and robot control. | https://arxiv.org/abs/2307.15818 |
| VLA03 | **OpenVLA** (2024) | ANCHOR / ARTIFACT | Strong open VLA baseline and fine-tuning substrate. | https://arxiv.org/abs/2406.09246 |
| VLA04 | **π0: A Vision-Language-Action Flow Model for General Robot Control** (2024) | ANCHOR | Useful contrast to purely autoregressive action tokenization; flow-matching action decoder. | https://arxiv.org/abs/2410.24164 |
| VLA05 | **FAST: Efficient Action Tokenization for Vision-Language-Action Models** (2025) | BRIDGE / ARTIFACT | Excellent example of a successful abstraction (“actions as tokens”) becoming the next bottleneck. | https://arxiv.org/abs/2501.09747 |
| VLA06 | **Latent Bridge: Feature Delta Prediction for Efficient Dual-System VLA Inference** (2026) | FRONTIER / ARTIFACT | Reduces slow VLM calls by predicting feature/KV deltas between timesteps; useful cross-timescale interface prior rather than a voice-specific analogy. | https://arxiv.org/abs/2605.02739 |
| VLA07 | **Think at 5 Hz, Act at 20 Hz** (2026) | FRONTIER / FAST-SLOW | Separates slow VLM reasoning from a fast action expert and explicitly trains under stale-cache conditions; strong cross-domain evidence that timescale boundaries are structural. | https://arxiv.org/abs/2607.15621 |

---

## Cross-domain research-move anchors

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| XD01 | **Elucidating the Design Space of Diffusion-Based Generative Models** (2022) | ANCHOR / CRAFT | Turns a convoluted method zoo into explicit independent design axes, then improves several at once. | https://arxiv.org/abs/2206.00364 |
| XD02 | **Sharpness-Aware Minimization (SAM)** (2020/ICLR 2021) | ANCHOR | Creates a new optimization object: neighborhood sharpness, not only endpoint loss. | https://arxiv.org/abs/2010.01412 |
| XD03 | **SAM operates far from home** (2023) | BRIDGE | Re-attribution example: accepted endpoint/minimum explanation is insufficient; training dynamics matter throughout the trajectory. | https://arxiv.org/abs/2302.08692 |


---

## Game NPCs / interactive characters

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| NPC00a | **AI for Games in the Foundation Model Era** (2026) | SURVEY / FIELD MAP | Cross-lifecycle map organized by what AI outputs are used for. The reusable NPC lesson is boundary + transfer + evidence: downstream game claims must be revalidated where the character actually acts. | https://arxiv.org/abs/2609.16679 |
| NPC00b | **A Survey on Large Language Model-Based Game Agents** (ACM CSUR 2026) | SURVEY | Component map across perception/action, memory, reasoning, role-play and learning; useful warning against optimizing one NPC component while silently relying on another. | https://arxiv.org/abs/2404.02039 |
| NPC00c | **AI-Native Games: A Survey and Roadmap** (2026) | SURVEY / DESIGN MAP | Useful counterfactual definition of AI-native play and emphasis on goals/rules/state/feedback/pacing/agency; open-ended generation is not gameplay by itself. | https://arxiv.org/abs/2607.00527 |
| NPC00d | **Narrative and Dialogue Generation for Video-Games: A Systematic Mapping** (2026) | SURVEY / NEGATIVE MAP | Maps 55 empirical studies; coherence, memory, repetition and latency are recurring generic problems, so those labels alone are not fresh NPC territories. | https://doi.org/10.1016/j.engappai.2026.115041 |
| NPC01 | **Craft an Iron Sword: Dynamically Generating Interactive Game Characters by Prompting LMs Tuned on Code** (2022) | ANCHOR / ARTIFACT | Early clean bridge from NPC language to executable game actions; public Minecraft prototype. | https://github.com/microsoft/interactive-minecraft-npcs |
| NPC02 | **Generative Agents: Interactive Simulacra of Human Behavior** (UIST 2023) | ANCHOR / ARTIFACT | Memory→reflection→planning lineage; foundational reference before proposing “long-term NPC memory”. | https://arxiv.org/abs/2304.03442 |
| NPC03 | **Collaborative Quest Completion with LLM-Driven NPCs in Minecraft** (2024) | BRIDGE / ARTIFACT | Moves from chatbot/action demos to human–NPC co-play; public interaction logs. | https://arxiv.org/abs/2407.03460 |
| NPC04 | **KNUDGE: Ontologically Faithful Generation of NPC Dialogues** (EMNLP 2024) | ANCHOR | Strong authored-world grounding baseline using real quest/dialogue structure from *The Outer Worlds*. | https://aclanthology.org/2024.emnlp-main.520/ |
| NPC05 | **Slice of Life: A Hybrid Social Simulation with LLM Dialogue** (FDG 2025) | BRIDGE | Important boundary choice: symbolic social simulation owns state/dynamics; LLM realizes language. | https://dl.acm.org/doi/proceedings/10.1145/3723498 |
| NPC06 | **PersonaEval** (2025) | NEGATIVE / MEASUREMENT | Shows role-play LLM judges are not automatically reliable proxies for human character identification. | https://arxiv.org/abs/2507.22087 |
| NPC07 | **Can LLM Agents Stick to the Script? / NCP-Bench** (2026) | FRONTIER / ARTIFACT | Long-horizon narrative commitment preservation; raises the bar beyond isolated response consistency. | https://arxiv.org/abs/2608.12195 |
| NPC08 | **One Policy, Infinite NPCs: Persona-Traceable Shared RL Policies for Scalable Game Agents** (2026) | FRONTIER / ARTIFACT / NEGATIVE-AUDIT | Strong open persona-conditioned RL baseline. Crucial current-repo audit: InfoNCE strongly helps the model-internal trajectory/persona metric, but an independent action/state Big-Five evaluator does not show a behavioral advantage. Treat metric↔behavior validity as unresolved. | https://arxiv.org/abs/2605.23652 |
| NPC09 | **ReactiveGWM: Steering NPC in Reactive Game World Models** (2026) | FRONTIER / ARTIFACT | Decouples player control and NPC strategy inside a game world model; unusually complete code/model/data release. | https://arxiv.org/abs/2605.15256 |
| NPC10 | **WorldMind: Decoupled Game World Model for State-Aware NPC Behavior** (2026) | FRONTIER | Successor pressure on ReactiveGWM: externally provided strategy is not state-aware autonomous decision making. Re-check artifact status. | https://arxiv.org/abs/2608.21439 |
| NPC11 | **Lies We Can See: Joint Verbal and Non-Verbal Deception by VLM Agents in Embodied Social Interactions** (2026) | FRONTIER / ARTIFACT | Public Minecraft social sandbox showing behavior/action channels can dominate verbal social signals; strong ablation harness. | https://arxiv.org/abs/2608.30428 |
| NPC12 | **The Double-Edged Sword of Open-Ended Interaction: How LLM-Driven NPCs Affect Players** (2026) | BRIDGE / NEGATIVE | Strong antidote to “more open-ended = better”: autonomy, cognitive load, usability/trust and experience can move differently. | https://arxiv.org/abs/2604.10107 |
| NPC17 | **Reinforcement Learning Methods for Emulating Personality in a Game Environment** (2025) | ANCHOR / BEHAVIORAL CONTROL | Explicit OCEAN-to-game-behavior reward shaping. Less semantically flexible than text personas, but useful because the trait→behavior contract is inspectable and task/personality trade-offs are exposed directly. | https://doi.org/10.3390/app15147894 |
| NPC18 | **Stack More Levels: How to Get General and Human-like Mario Playing** (IEEE CoG 2026) | ARTIFACT / BEHAVIORAL PERSONA | Open PPO/DRAIL baseline with runner/killer/collector playstyles, PCG levels, human demos and checkpoints. Useful contrast to PCSP because persona preservation is measured in concrete game behavior such as kill/coin outcomes. | https://github.com/carrotoxic/mario-personas |
| NPC13 | **ClueGen: An Exploration of Procedural Storytelling in the Format of Murder Mystery Games** (AIIDE 2016) | ANCHOR | Old but unusually relevant: NPC lies are generated by altering remembered events, so deception stays coupled to the procedural world and can be challenged by the player. | https://doi.org/10.1609/aiide.v12i2.12896 |
| NPC14 | **Lies, Deceit, and Hallucinations: Player Perception and Expectations Regarding Trust and Deception in Games** (CHI 2024) | ANCHOR / MEASUREMENT | Establishes that falsehood is not one error class in games: perceived intentional lies can carry narrative/gameplay meaning, while accidental falsehoods can break players’ mental models. | https://doi.org/10.1145/3613904.3642253 |
| NPC15 | **Enforcing Narrative Reliability and Epistemic Pacing in LLM-Driven Detective Games via Structured Knowledge Trees** (AIIDE 2026) | FRONTIER / NEGATIVE | Strong current pressure point: free LLM deception creates untraceable false alibis and fabricated entities; SKT restores reliability by pre-authoring allowed truth/lie nodes, exposing a rigidity–improvisation boundary. | https://arxiv.org/abs/2609.23043 |
| NPC16 | **Strategically Misleading the User: Building a Deceptive Virtual Suspect** (AAMAS 2017) | ANCHOR / OWNERSHIP | Critical old prior: runtime lie generation from structured event/entity memory and an explicit model of what the interviewer may know. Prevents falsely claiming that dynamic NPC deception itself is new. | https://dl.acm.org/doi/10.5555/3091282.3091419 |

Deep genealogy and broader survey map: `deep/academic/GAME_NPC_LANDSCAPE.md`.

---

## Notes

- “FRONTIER” means **re-check before making a latest-state claim**.
- For deep parent→successor reconstruction, use `deep/academic/GENEALOGY_LIBRARY_INDEX.md`.
- Candidate-specific nearest prior does **not** belong here; put it in the candidate/workbench package.


---

## Frontier additions — 2026-09-30

> **Status note:** these are research-navigation / lineage assets discovered in the 2026-09-30 cross-venue scan. Inclusion here does **not** authorize a workbench or imply a paper idea. Venue/release labels should be re-verified from the primary source before any novelty claim.

### Interactive agents / evolving task state

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| AG19 | **LLMs Get Lost In Multi-Turn Conversation** (ICLR 2026) | PARENT / BEHAVIOR | Strong parent showing that competence under a fully specified task can collapse when the same information arrives interactively; useful baseline for separating static capability from state maintenance/recovery across turns. | https://proceedings.iclr.cc/paper_files/paper/2026/hash/59f6421e64707225fdf5b28840679a07-Abstract-Conference.html |
| AG20 | **LLMs Get Lost in Evolving User Intent** (2026) | FRONTIER / ARTIFACT | Extends multi-turn pressure from incremental disclosure to revisions and goal/function changes; useful ownership boundary for any work on persistent task-state revision. | https://arxiv.org/abs/2607.20734 |
| AG21 | **U-Fold: Dynamic Intent-Aware Context Folding for User-Centric Agents** (Findings ACL 2026) | SUCCESSOR / METHOD | Treats changing user intent as a context-management problem rather than ordinary summarization; important evidence that state revision is already becoming an explicit systems object. | https://aclanthology.org/2026.findings-acl.897/ |
| AG22 | **Uncertainty-Aware Clarification in LLM Agents with Information Gain** (ICML 2026) | PARENT / METHOD | Strong clarification parent: turns underspecification into a decision problem over whether asking is worth the interaction cost; useful boundary against rediscovering generic clarification. | https://proceedings.mlr.press/v306/deng26l.html |
| AG23 | **When and What to Ask: AskBench and Rubric-Guided RLVR for LLM Clarification** (Findings ACL 2026) | PARENT / BENCHMARK / ARTIFACT | Separates intent-deficiency and false-premise clarification and supplies a current strong baseline; important evidence that “agents should ask clarifying questions” is already crowded. | https://aclanthology.org/2026.findings-acl.845/ |
| AG24 | **Ask Early, Ask Late, Ask Right: When Does Clarification Timing Matter for Long-Horizon Agents?** (2026 preprint) | FRONTIER / DIAGNOSTIC | Controlled timing intervention suggests clarification value depends on where the agent is in a trajectory; useful research-move example even if the exact claim remains preprint-level. | https://arxiv.org/abs/2605.07937 |
| AG25 | **When2Tool: Tool Necessity Is Linearly Decodable Before Generation** (2026) | FRONTIER / REPRESENTATION→ACTION | Shows that tool-need information can be strongly decodable before generation while natural action selection still fails to use it reliably; useful ownership boundary for generic “the model knows but does not act” stories. | https://arxiv.org/abs/2605.09252 |
| AG26 | **Done, But Not Sure: Disentangling World Completion from Self-Termination in Embodied Agents** (2026) | FRONTIER / CONTROL | Separates completing the external task from committing to termination; useful example of decomposing a single benchmark success into distinct control decisions. | https://arxiv.org/abs/2605.08747 |
| AG27 | **Calibration Is Not Control: Intervention Advantage for LLM-Agent Oversight** (2026) | FRONTIER / CONTROL OBJECT | Changed-object lesson: predicting failure risk is not the same as estimating whether an intervention improves the continuation. Useful beyond the specific oversight setting. | https://arxiv.org/abs/2606.21399 |
| AG28 | **AgentLens: Revealing the Lucky Pass Problem in SWE-Agent Evaluation** (2026) | FRONTIER / MEASUREMENT | Process-level audit showing that terminal success can hide poor recovery/verification trajectories; useful measurement warning for long-horizon agents. | https://arxiv.org/abs/2605.12925 |

### Reasoning / planning utilization

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| RS05 | **Extracting Search Trees from LLM Reasoning Traces Reveals Myopic Planning** (2026) | FRONTIER / DIAGNOSTIC | Reconstructs search structure from reasoning traces and asks whether deeper explored nodes actually control the final decision; useful pressure on “more visible reasoning = more used reasoning”. | https://arxiv.org/abs/2605.06840 |
| RS06 | **Reasoning Traces Shape Outputs but Models Won’t Say So** (ACL 2026) | PARENT / CAUSAL | Uses causal thought intervention to distinguish trace influence from models’ self-reports of that influence; important parent for reasoning-use/faithfulness claims. | https://aclanthology.org/2026.acl-long.1986/ |
| RS07 | **FaithCoT-Bench: Benchmarking Instance-Level Faithfulness of Chain-of-Thought Reasoning** (ICLR 2026) | PARENT / EVALUATION | Strong current faithfulness parent; prevents reframing generic CoT faithfulness as a new territory. | https://proceedings.iclr.cc/paper_files/paper/2026/hash/6c7154e394e24c69409256ccf8bf0804-Abstract-Conference.html |

### Mechanistic interpretability — from feature detection to functional action

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| MI25 | **Weakening Neurons: An Input-Output Functionality in Transformers with Outsize Influence** (EMNLP 2026) | FRONTIER / FUNCTIONAL UNIT | Studies an MLP neuron jointly through what it reads and what it writes; weakening neurons challenge the habit of describing neurons only by activating features/concepts. | https://arxiv.org/abs/2609.18612 |
| MI26 | **Inverted Detection and Control in Steering Vectors** (NeurIPS 2026) | FRONTIER / DETECTION≠CONTROL | Highly discriminative directions can causally steer in the opposite semantic direction; useful cross-level evidence that a representation’s readout meaning need not equal its control effect. | https://arxiv.org/abs/2608.02957 |
| MI27 | **Transformer Feed-Forward Layers Are Key-Value Memories** (EMNLP 2021) | FOUNDATION / READ→WRITE | Classic functional view of FFN keys as input pattern detectors and values as output-distribution writers; essential parent for modern operator-centric neuron analysis. | https://aclanthology.org/2021.emnlp-main.446/ |
| MI28 | **Knowledge Neurons in Pretrained Transformers** (ACL 2022) | FOUNDATION / FEATURE-LOCALIZATION | Canonical neuron-localization lineage; useful contrast for asking whether “where a concept is detected” and “what a unit does to computation” are the same scientific object. | https://aclanthology.org/2022.acl-long.581/ |
| MI29 | **Transcoders Find Interpretable LLM Feature Circuits** (NeurIPS 2024) | FOUNDATION / ARTIFACT | Sparse input→output decomposition of MLP computation; important current parent for moving from activation dictionaries toward functional circuits. | https://proceedings.neurips.cc/paper_files/paper/2024/hash/2b8f4db0464cc5b6e9d5e6bea4b9f308-Abstract-Conference.html |

### VLA — semantic information versus action control

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| VLA08 | **Not All Features Are Created Equal: A Mechanistic Study of Vision-Language-Action Models** (2026) | FRONTIER / MECHANISTIC / ARTIFACT | Causal activation interventions expose modality/pathway specialization and cases where language is encoded yet ignored by action. Strong parent for semantic-to-action questions in VLA. | https://arxiv.org/abs/2603.19233 |
| VLA09 | **Restoring Linguistic Grounding in VLA Models via Train-Free Attention Recalibration** (2026) | FRONTIER / METHOD | Diagnoses “linguistic blindness” under contradictory language and proposes a train-free intervention; ownership boundary for simple language-neglect claims. | https://arxiv.org/abs/2603.06001 |
| VLA10 | **Grounded Semantic Re-Binding for Robust Instruction Generalization in VLA Models** (2026) | FRONTIER / METHOD | Finds task semantics can remain internally available while downstream action is vulnerable to joint feature shifts; directly relevant to semantic information vs policy use. | https://arxiv.org/abs/2608.02497 |
| VLA11 | **Beyond Appearance Shifts: Task-Semantic Action Calibration for VLA Models** (NeurIPS 2026) | FRONTIER / ROBUSTNESS | Separates invariance to task-preserving nuisance changes from sensitivity to task-semantic changes; strong ownership pressure on generic “robust VLA semantics” stories. | https://arxiv.org/abs/2609.23650 |
| VLA12 | **Instruction Anchor: Dissecting the Mechanistic Dynamics of Modality Arbitration** (2026) | FRONTIER / MECHANISM | Treats instruction-following as modality arbitration across depth and identifies sparse causal attention pathways; useful mechanistic parent for language-vs-vision control. | https://arxiv.org/abs/2602.03677 |

### Role-playing / NPC boundary evidence

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| NPC13 | **Beyond Static Persona Consistency: Dynamic Persona Coherence in LLM Role-Playing** (ACL 2026) | PARENT / DYNAMIC PERSONA | Explicitly separates stable identity from evolving psychological state; shows that “dynamic persona” is already an owned research object rather than an empty NPC gap. | https://aclanthology.org/2026.acl-long.1336/ |
| NPC14 | **Beyond Fixed Psychological Personas: State Beats Trait, but Language Models are State-Blind** (Findings ACL 2026) | PARENT / HUMAN-GROUNDED | Human data places much variation within-person state rather than fixed traits; useful pressure against evaluating agents only by static persona consistency. | https://aclanthology.org/2026.findings-acl.1316/ |
| NPC15 | **ArcANE: Do Role-Playing Language Agents Stay in Character at the Right Time?** (2026) | FRONTIER / DYNAMIC CHARACTER | Evaluates the same character across changing story phases, pushing persona evaluation toward context-dependent character arcs; strong ownership boundary for generic dynamic-persona proposals. | https://arxiv.org/abs/2606.05553 |


### Second-pass additions from the same 2026-09-30 scan

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| AG29 | **Beyond Single-shot Writing: Deep Research Agents are Unreliable at Multi-turn Report Revision** (ACL 2026) | PARENT / REVISION | User feedback is usually incorporated, yet 16–27% of previously covered content/citation quality regresses; strong evidence that revision locality/non-regression is distinct from “understands feedback”. | https://aclanthology.org/2026.acl-long.609/ |
| AG30 | **Action Boundary Blindness: When LLM Agents Cannot Tell Where One Action Ends and Another Begins** (ACL 2026) | PARENT / ACTION STRUCTURE | Natural cross-benchmark agent failure with an important diagnostic twist: explicit boundary cues recover part of the gap, suggesting elicitation rather than a simple capability absence. Excellent Sasano-style genealogy example; the exact object is already owned. | https://aclanthology.org/2026.acl-long.1711/ |
| AG31 | **Large Language Models Develop Belief State Geometry In-Context** (2026) | FRONTIER / MODEL SCIENCE | Controlled HMM setting shows linearly decodable and intervention-relevant posterior belief geometry in ordinary pretrained LLMs; a useful controlled parent for asking what “agent state” could mean mechanistically. | https://arxiv.org/abs/2609.17376 |
| AG32 | **AgentAbstain: Do LLM Agents Know When Not to Act?** (2026) | FRONTIER / ARTIFACT | Paired executable tasks separate task-solving from calibrated action commitment and expose post-hoc abstention after irreversible actions; important ownership boundary for generic “ask/stop/abstain” topics. | https://arxiv.org/abs/2607.10059 |
| ML01 | **The Role of Mixed-Language Documents for Multilingual Large Language Model Pretraining** (ACL 2026) | PARENT / CONTROLLED PRETRAINING | Removing only ~2% mixed-language data destroys much translation while leaving cross-lingual QA/reasoning largely unchanged; strong example of one broad “cross-lingual ability” splitting into different causal dependencies. | https://aclanthology.org/2026.acl-long.1706/ |
| ML02 | **Feeding BabyLMs Macaroni: Code-Switching Curricula Cause Cross-Lingual Convergence** (2026) | FRONTIER / ARTIFACT / SMALL-SCALE | Cheap controlled multilingual pretraining with released code/data/models finds persistent representation convergence under code-switching curricula, creating a tractable counterpoint to the expensive ACL parent. | https://arxiv.org/abs/2609.30535 |
| MI30 | **Towards Understanding Massive Activations in Attention Sink Mechanism** (ICML 2026) | PARENT / RE-ATTRIBUTION | Reframes sinks and massive activations as interacting mechanisms that limit token mixing rather than a one-way “massive activations cause sinks” story; strong re-attribution genealogy. | https://proceedings.mlr.press/v306/wang26ed.html |
| MI31 | **It's Not RoPE that Creates Sinks: The Role of Self-Concentration and Value-Non-Mixing in Attention** (EMNLP 2026) | FRONTIER / RE-ATTRIBUTION | Uses structural interventions to reject a tempting positional-encoding explanation and attribute initial-position sinks/MAs to causal self-concentration and value non-mixing; useful model-science craft exemplar. | https://arxiv.org/abs/2609.09085 |


### Ownership-pressure additions — 2026-09-30 late scan

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| AG33 | **When Users Change Their Minds: Measuring and Repairing Intent Drift in LLM Agents** (2026 preprint) | FRONTIER / OWNERSHIP | Released 2026-09-26. IntentFlux makes superseded/withdrawn intent executable and StateForge explicitly maintains active requirements; this sharply narrows any generic “evolving intent” novelty claim. | https://arxiv.org/abs/2609.32520 |
| AG34 | **From Memory to Belief: A Survey of State Maintenance and Belief Revision in LLM Decision Agents** (2026 survey/preprint) | SURVEY / FIELD MAP | Released 2026-09-23. Frames agent failures as state, transition, likelihood, revision, credit and belief-action consistency rather than generic memory; mandatory ownership map before entering this territory. | https://ssrn.com/abstract=7493158 |
| MI32 | **Constructing Interpretable Features from Compositional Neuron Groups** (ACL 2026) | PARENT / UNIT OF ANALYSIS | Challenges individual-neuron and SAE-only views by deriving sparse interpretable features directly from co-activated neurons and tying them to model computation; important ownership pressure for any new operator-centric MI unit. | https://aclanthology.org/2026.acl-long.1959/ |
| MI33 | **Locate, Steer, and Improve: A Practical Survey of Actionable Mechanistic Interpretability in Large Language Models** (Findings ACL 2026) | SURVEY / ACTIONABILITY | Maps localization to causal intervention and improvement, so “make interpretability actionable” alone is already too generic; useful boundary for operator/function-focused work. | https://aclanthology.org/2026.findings-acl.502/ |


### Cross-lingual capability formation / multilingual learning dynamics

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| ML03 | **Emerging Cross-lingual Structure in Pretrained Language Models** (ACL 2020) | FOUNDATION / CHANGED PREMISE | Cross-lingual transfer can emerge without shared vocabulary or matched domains when higher parameters are shared; boundary against treating lexical overlap as necessary. | https://aclanthology.org/2020.acl-main.536/ |
| ML04 | **On the Cross-lingual Transferability of Monolingual Representations** (ACL 2020) | FOUNDATION / CHANGED PREMISE | Freezing a monolingual Transformer and relearning only target-language embeddings yields strong transfer without joint multilingual training. | https://aclanthology.org/2020.acl-main.421/ |
| ML05 | **Identifying Elements Essential for BERT’s Multilinguality** (EMNLP 2020) | FOUNDATION / CONTROLLED TRAINING | Small controlled training isolates architectural/linguistic ingredients; craft reference for cheap mechanism experiments checked at larger scale. | https://aclanthology.org/2020.emnlp-main.358/ |
| ML06 | **Analyzing the Mono- and Cross-Lingual Pretraining Dynamics of Multilingual Language Models** (EMNLP 2022) | FOUNDATION / TRAJECTORY / ARTIFACT | 39 public XLM-R-replica checkpoints show in-language and cross-lingual capabilities emerge on different schedules and knowledge moves across layers. | https://aclanthology.org/2022.emnlp-main.234/ |
| ML07 | **Cross-Lingual Consistency of Factual Knowledge in Multilingual Language Models** (EMNLP 2023) | FOUNDATION / KNOWLEDGE | Separates factual accuracy from cross-language consistency and shows model size alone does not remove inconsistency. | https://aclanthology.org/2023.emnlp-main.658/ |
| ML08 | **mOthello: When Do Cross-Lingual Representation Alignment and Cross-Lingual Transfer Emerge?** (Findings NAACL 2024) | FOUNDATION / CAUSAL SANDBOX | Anchor tokens can create strong language-neutral alignment without transfer; critical counterexample to alignment=sufficient-for-transfer. | https://aclanthology.org/2024.findings-naacl.103/ |
| ML09 | **Probing the Emergence of Cross-lingual Alignment during LLM Training** (Findings ACL 2024) | TRAJECTORY / ARTIFACT | Uses BLOOM checkpoints to connect representation/neuron alignment dynamics to zero-shot transfer across training and scale. | https://aclanthology.org/2024.findings-acl.724/ |
| ML10 | **MEXA: Multilingual Evaluation of English-Centric LLMs via Cross-Lingual Alignment** (ACL 2025) | PARENT / MEASUREMENT / ARTIFACT | Strong global evidence that English-pivot middle-layer alignment predicts multilingual task performance; supplies cheap reusable tooling. | https://arxiv.org/abs/2410.05873 |
| ML11 | **Middle-Layer Representation Alignment for Cross-Lingual Transfer in Fine-Tuned LLMs** (ACL 2025) | PARENT / METHOD / ARTIFACT | Turns middle-layer alignment from diagnostic into training objective across 1,000+ language pairs and multiple task types. | https://aclanthology.org/2025.acl-long.778/ |
| ML12 | **Separating Tongue from Thought** (ACL 2025) | PARENT / CAUSAL MI | Activation patching separates output language from concept identity and gives causal evidence for shared concept representations. | https://aclanthology.org/2025.acl-long.1536/ |
| ML13 | **False Friends Are Not Foes** (Findings EMNLP 2025) | PARENT / CONTROLLED PRETRAINING / ARTIFACT | Controlled ID-remapping shows token overlap is a meaningful accelerator without making it a necessary condition; semantic anchors help most. | https://aclanthology.org/2025.findings-emnlp.1153/ |
| ML14 | **Tracing Multilingual Factual Knowledge Acquisition in Pretraining** (Findings EMNLP 2025) | TRAJECTORY / ARTIFACT | OLMo trajectory reveals frequency-driven factual acquisition plus limited, early and asymmetric cross-lingual transfer; open scripts/data. | https://aclanthology.org/2025.findings-emnlp.113/ |
| ML15 | **When Less Language is More** (NeurIPS 2025) | PARENT / CAUSAL REASONING | Removing language-specific signal in reasoning layers improves multilingual reasoning while upper-layer language information remains useful for output fidelity. | https://proceedings.neurips.cc/paper_files/paper/2025/hash/372bd0e47f2d5bceca7e300e1446849c-Abstract-Conference.html |
| ML16 | **When Meanings Meet** (EACL 2026) | FRONTIER / TRAJECTORY / CAUSAL MI | Tracks shared concept-space emergence across pretraining; combines causal patching with manual validity audit and exposes stage/language dependence. | https://aclanthology.org/2026.eacl-long.145/ |
| ML17 | **Can you map it to English?** (EACL 2026) | FRONTIER / CAUSAL NLU / ARTIFACT | Instance-level transfer failures are less aligned; semantically equivalent English activation patching fixes a subset of non-English NLU errors. | https://aclanthology.org/2026.eacl-long.225/ |
| ML18 | **Tracing Multilingual Knowledge Acquisition Dynamics in Domain Adaptation** (EACL 2026) | FRONTIER / LEARNING DYNAMICS | Training/evaluation matched on bilingual domain corpus; studies within-language acquisition vs cross-language transfer and loss shielding. | https://aclanthology.org/2026.eacl-long.269/ |
| ML19 | **LinguaMap: Which Layers of LLMs Speak Your Language and How to Tune Them?** (ICLR 2026) | FRONTIER / LAYER DECOMPOSITION | Separates early semantic mapping, middle task reasoning and late language realization; ownership boundary for layer-specialization claims. | https://proceedings.iclr.cc/paper_files/paper/2026/hash/00295cede6e1600d344b5cd6d9fd4640-Abstract-Conference.html |
| ML20 | **Multilingual Routing in Mixture-of-Experts** (ICLR 2026) | FRONTIER / COMPUTATION ROUTING | Shows language specificity/shared computation also appears in expert-routing dynamics, with cross-lingual middle-layer routing associated with performance. | https://proceedings.iclr.cc/paper_files/paper/2026/hash/1b558190825286a3defcc78d02fa2189-Abstract-Conference.html |
| ML21 | **Beyond English-Centric Training: How Reinforcement Learning Improves Cross-Lingual Reasoning** (ICLR 2026) | FRONTIER / POST-TRAINING | RL and SFT create different cross-lingual generalization behavior; prevents assuming pretraining alignment findings transfer unchanged to reasoning post-training. | https://proceedings.iclr.cc/paper_files/paper/2026/hash/9320df227557d00ce68f1b8b07ea2d49-Abstract-Conference.html |
| ML22 | **LiveCLKTBench** (ACL 2026) | FRONTIER / MEASUREMENT | Uses time-sensitive knowledge to reduce prior-exposure confounding when measuring genuine cross-lingual knowledge transfer. | https://aclanthology.org/2026.acl-long.694/ |
| ML23 | **Data-Centric Continual Pre-training for 500+ Languages** (Findings ACL 2026) | FRONTIER / SCALE BOUNDARY | Large-scale evidence that parallel bilingual data benefits multilingual adaptation, especially lower-resource languages; useful scale/ownership boundary. | https://aclanthology.org/2026.findings-acl.937/ |


### Cross-lingual capability formation — late 2026 ownership expansion

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| ML24 | **Copy First, Translate Later: Interpreting Translation Dynamics in Multilingual Pretraining** (EMNLP 2026 Main) | FRONTIER / DENSE TRAJECTORY / TRANSLATION | Pretrains a 1.7B model on nine languages with dense checkpoints and finds a two-phase translation trajectory: early copying/surface mechanisms followed by more generalizing translation mechanisms. Strong ownership boundary for “when does translation emerge?” trajectory work. | https://arxiv.org/abs/2604.17633 |
| ML25 | **Beyond Input Understanding: Diagnosing Multilingual Mathematical Reasoning with Directed Acyclic Trace Graphs** (EMNLP 2026 Main) | FRONTIER / REASONING DIAGNOSIS | Holding problem understanding in English while changing reasoning language still changes accuracy; diagnoses lower anchor coverage and dependency fidelity in non-English reasoning. Important evidence that multilingual reasoning failures are not reducible to input-language mapping. | https://arxiv.org/abs/2605.27715 |
| ML26 | **Language on Demand, Knowledge at Core: Composing LLMs with Encoder-Decoder Translation Models for Extensible Multilinguality** (ACL 2026) | PARENT / SHARED-CORE-INTERFACE / ARTIFACT | Explicitly factorizes multilingual understanding/generation into language interfaces around an English-centric LLM knowledge/reasoning core; strong baseline and ownership pressure for generic “shared core + language shell” claims. | https://aclanthology.org/2026.acl-long.955/ |
| ML27 | **Unlocking Multilingual Reasoning Capability of LLMs and LVLMs through Representation Engineering** (ACL 2026) | PARENT / REPRESENTATION INTERVENTION / ARTIFACT | Sequentially aligns non-English reasoning representations toward English space and separately restores target-language output distribution, operationalizing a reasoning-core/output-interface decomposition. | https://aclanthology.org/2026.acl-long.1138/ |
| ML28 | **Bridging the Language Gap: Uncovering and Aligning Shared Circuits for Multi-Hop Reasoning in Multilingual LLMs** (AAAI 2026) | PARENT / MECHANISTIC REASONING | Attributes some multilingual multi-hop failures to language-dependent attention routing into shared language-agnostic semantic neurons rather than missing knowledge; important circuit-level boundary for “shared knowledge, failed access” claims. | https://ojs.aaai.org/index.php/AAAI/article/view/40592 |


### Cross-lingual capability formation — proxy / stage-decomposition pressure

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| ML29 | **Translation as a Scalable Proxy for Multilingual Evaluation** (2026 preprint / CoRR) | FRONTIER / PROXY / ARTIFACT | Across 14 models and 9 benchmarks, translation quality is often strongly correlated with downstream multilingual performance. Crucial observational parent for asking whether translation measures a causal access bottleneck or only a correlated interface/resource factor. | https://arxiv.org/abs/2601.11778 |
| ML30 | **Quantifying the Impact of Translation Errors on Multilingual LLM Evaluation** (ACL 2026) | PARENT / MEASUREMENT BOUNDARY | Shows target-side translation errors in translated benchmarks cause measurable evaluation degradation after controlling English correctness/source anomalies. Important distinction: benchmark-translation quality is not the same object as a model's intrinsic translation skill as a capability proxy. | https://aclanthology.org/2026.acl-long.1916/ |
| ML31 | **Why Do Multilingual Reasoning Gaps Emerge in Reasoning Language Models?** (Findings ACL 2026) | PARENT / STAGE DECOMPOSITION / ARTIFACT | Decomposes multilingual reasoning into input understanding, dominant-language reasoning and output; selective translation of ~20% inputs approaches full-translation performance, making input→reasoning-core access a strong parent explanation. | https://aclanthology.org/2026.findings-acl.1586/ |
| ML32 | **Bringing Up a Bilingual BabyLM: Investigating Multilingual Language Acquisition Using Small-Scale Models** (2026 preprint) | CONTROLLED TRAINING / ARTIFACT | Matched 100M-word mono/bilingual corpora and GPT-2 models provide a cheap intervention substrate for exposure-regime questions; useful causal sandbox, not sufficient modern-LLM evidence alone. | https://arxiv.org/abs/2603.29552 |
| ML33 | **Semantic Pivots Enable Cross-Lingual Transfer in Large Language Models** (2025 preprint) | OWNERSHIP PRESSURE / MECHANISTIC TRANSLATION | Uses word-level translation as its cross-lingual ability readout and proposes semantic-pivot-aware pretraining, illustrating how translation is used as a model organism for broader transfer claims. | https://arxiv.org/abs/2505.16385 |


| ML34 | **Gold vs. Translation: Are We Measuring Language, Knowledge, or Locality in Translated Benchmarks?** (ACL ARR March 2026 submission) | OWNERSHIP PRESSURE / PROXY VALIDITY | Tests whether translated English-origin benchmarks proxy native benchmarks after controlling model size and language proficiency; shows strong validity for some curricular tasks but weaker/no incremental value for locality-heavy knowledge. Distinct from intrinsic MT-skill proxy validity, but important adjacent construct-validity work. | https://openreview.net/forum?id=2SI74SsSSq |
