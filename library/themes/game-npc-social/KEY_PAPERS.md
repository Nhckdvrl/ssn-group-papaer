# Key Papers — 游戏 NPC 与社会智能体（Game NPCs / social agents）

从 `library/KEY_PAPERS.md` 按题材拆出（2026-09-30），保留历史ID；后续核查只修正对应摘要与入口。标签含义见 `../../KEY_PAPERS.md`。

**2026-10-18维护：** 当前领域认识见[全领域地图](../../../workbench/game-npc-agents/knowledge/DOMAIN_ATLAS.md)，逐篇正式身份、版本、实际阅读范围与唯一规范卡见[阅读总账](../../../workbench/game-npc-agents/knowledge/READING_CATALOG.md)。未重读条目不因本页更新而升级。

**ID 勘误（2026-10-09）**：旧增补段落把 `NPC13–NPC15` 分别用于两组不同论文，后者已更名为 `NPC19–NPC21`，各行内容未删。详见[知识库审计](../../LIBRARY_AUDIT_2026-10-09.md)。该日记录涉及的两个旧NPC工作台后来已于2026-10-11删除，当前入口为[game-npc-agents](../../../workbench/game-npc-agents/README.md)。

## Game NPCs / interactive characters

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| NPC01 | **Craft an Iron Sword: Dynamically Generating Interactive Game Characters by Prompting LMs Tuned on Code** (2022) | ANCHOR / ARTIFACT | Early clean bridge from NPC language to executable game actions; public Minecraft prototype. | https://github.com/microsoft/interactive-minecraft-npcs |
| NPC02 | **Generative Agents: Interactive Simulacra of Human Behavior** (UIST 2023) | ANCHOR / ARTIFACT | Memory→reflection→planning lineage; foundational reference before proposing “long-term NPC memory”. | https://arxiv.org/abs/2304.03442 |
| NPC03 | **Collaborative Quest Completion with LLM-Driven NPCs in Minecraft** (2024) | BRIDGE / ARTIFACT | Moves from chatbot/action demos to human–NPC co-play; public interaction logs. | https://arxiv.org/abs/2407.03460 |
| NPC04 | **KNUDGE: Ontologically Faithful Generation of NPC Dialogues** (EMNLP 2024) | ANCHOR / AUTHORING | 基于《The Outer Worlds》任务与对话结构的作者工具。专家判断的game effect属于文本质量评价，不是引擎动作执行；完整知识ICL是重要参照。 | [规范卡](../../../workbench/game-npc-agents/knowledge/papers/KNUDGE_2024.md) · [正式原文](https://aclanthology.org/2024.emnlp-main.520/) |
| NPC05 | **Slice of Life: A Hybrid Social Simulation with LLM Dialogue** (FDG 2025) | BRIDGE | Important boundary choice: symbolic social simulation owns state/dynamics; LLM realizes language. | https://dl.acm.org/doi/proceedings/10.1145/3723498 |
| NPC06 | **PersonaEval** (2025) | NEGATIVE / MEASUREMENT | Shows role-play LLM judges are not automatically reliable proxies for human character identification. | https://arxiv.org/abs/2507.22087 |
| NPC07 | **Can LLM Agents Stick to the Script? / NCP-Bench** (2026) | FRONTIER / ARTIFACT | 多人物叙事承诺与约束；实际任务、调度器权限、模型对照及读取范围见规范卡，不由题名推断引擎能力。 | [规范卡](../../../workbench/game-npc-agents/knowledge/papers/NCP_2026.md) · [原文](https://arxiv.org/abs/2608.12195) |
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

## Role-playing / NPC boundary evidence

| ID | Paper | Role | Why reread | Link |
|---|---|---|---|---|
| NPC19 | **Beyond Static Persona Consistency: Dynamic Persona Coherence in LLM Role-Playing** (ACL 2026) | PARENT / DYNAMIC PERSONA | 区分稳定人物设定与变化的心理状态。Vanilla无历史，不能据其差距排除普通记忆的解释；PCC定义与部分表格存在待澄清不一致。 | [规范卡](../../../workbench/game-npc-agents/knowledge/papers/DYNAMIC_PERSONA_COHERENCE_2026.md) · [正式原文](https://aclanthology.org/2026.acl-long.1336/) |
| NPC20 | **Beyond Fixed Psychological Personas: State Beats Trait, but Language Models are State-Blind** (Findings ACL 2026) | PARENT / HUMAN-GROUNDED | Human data places much variation within-person state rather than fixed traits; useful pressure against evaluating agents only by static persona consistency. | https://aclanthology.org/2026.findings-acl.1316/ |
| NPC21 | **ArcANE: Do Role-Playing Language Agents Stay in Character at the Right Time?** (2026) | FRONTIER / DYNAMIC CHARACTER | Evaluates the same character across changing story phases, pushing persona evaluation toward context-dependent character arcs; strong ownership boundary for generic dynamic-persona proposals. | https://arxiv.org/abs/2606.05553 |
