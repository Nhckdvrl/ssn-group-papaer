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

---

## VLA / robotics

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| VLA01 | **Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware (ACT)** (2023) | ANCHOR / ARTIFACT | Action chunking grows directly from compounding-error / high-precision control pressure. | https://arxiv.org/abs/2304.13705 |
| VLA02 | **RT-2** (2023) | ANCHOR | Converts actions to language-like tokens to unify web semantics and robot control. | https://arxiv.org/abs/2307.15818 |
| VLA03 | **OpenVLA** (2024) | ANCHOR / ARTIFACT | Strong open VLA baseline and fine-tuning substrate. | https://arxiv.org/abs/2406.09246 |
| VLA04 | **π0: A Vision-Language-Action Flow Model for General Robot Control** (2024) | ANCHOR | Useful contrast to purely autoregressive action tokenization; flow-matching action decoder. | https://arxiv.org/abs/2410.24164 |
| VLA05 | **FAST: Efficient Action Tokenization for Vision-Language-Action Models** (2025) | BRIDGE / ARTIFACT | Excellent example of a successful abstraction (“actions as tokens”) becoming the next bottleneck. | https://arxiv.org/abs/2501.09747 |

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
