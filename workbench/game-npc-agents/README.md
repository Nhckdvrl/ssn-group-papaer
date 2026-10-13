# Game NPC Agents｜游戏内自主角色的学习、可控制行为与实际部署

**PROPOSED；2026-10-13 用户再次明确限定为游戏 NPC Agent，撤回旧“目标保持 vs 旧计划”主切口。** 本次是用户驱动的科学入口修改，不改变其他 workbench 的 ACTIVE 状态。尚无新模型/环境训练结果。

## 我们研究的是谁
游戏世界中的 **非玩家控制角色（Non-Player Characters）**：RPG/开放世界居民、互动社会 NPC、队友、敌人、战斗与剧情角色。他们从游戏真实状态和有限感知得到信息，通过可执行动作/言语影响游戏；可以拥有身份/设计者给定意图/可学习策略，与真实或模拟玩家共处。
- **不是：** 训练一个 agent 通关游戏/刷新游戏最高分，或单纯在聊天界面模仿动漫角色。
- **可以借鉴：** Game-playing RL/模仿学习、角色扮演 LLM 的后训练和多智能体学习，但只有返回 **NPC 本身的行为控制、设计制作或真实互动**，才成为本工作台实验。
- **不预设：** NPC 每帧必须用 LLM；底层行为树/小政策可与本地 LLM 的高层感知、对话、策略生成协作。

## 2026-10-13 新领域锚点
我们关心：**怎样以可负担的训练与设计成本，获得在真实游戏中可执行、可修改、可复用而且符合创作意图的 NPC 行为？**
EA 的 [Augmenting Game AI with Deep RL](https://arxiv.org/html/2606.20210v1) 针对 FC25 守门员/Battlefield 6 兵种列七项生产要求（可信、可控、快速训练、模块化、易维护、可纠错、运行时约束），这属于直接 NPC 研究，不是游戏通关 benchmark。KRAFTON [PUBG Ally](https://developer.nvidia.com/blog/how-krafton-built-pubg-ally-a-co-playable-character-powered-by-nvidia-ace/) 展示本地小模型高层交互与实时行为树双层架构；它自称 CPC，是紧邻但不代表传统所有 NPC。
**这些是问题的重要性锚点，不是证明我们的 idea 新颖或“游戏 NPC 只能 RL”。**

## 研究空间（不是四个已经选定的论文方案）
| 子方向 | 真正的科学压力 | 最直接的参照 |
|---|---|---|
| **学习可控的角色行为**（优先驻留） | 从有限设计师反馈/示范/行为约束训练，既不只是获胜也不只是性格句子 | EA 2026、Direct Behavior Specification、PCSP、UBCL、MultiGAIL |
| **快速修改与迁移已学 NPC** | 更新一个角色动作/游戏规则后不毁掉旧能力；多角色可复用而不每人从零训练 | EA 2026、continual RL、共享条件策略、NeurIPS2026 Event-triggered diversity |
| **玩家/伙伴交互中的适应** | 面对不同真实玩家的策略、需求、合作关系执行有用的行动 | KRAFTON Ally、GAMMA、Hypothetical Minds（角色/玩家映射须明确） |
| **LLM↔游戏策略↔引擎分工** | 语言理解/意图如何成为合法动作；什么必须快执行，怎样评估完整行动成本 | PUBG Ally、LIGHT/Dragon、ReactiveGWM（视频世界模型分支） |

**优先调查的广义 territory：** Trainable and Designer-Controllable Game NPC Behavior。尚未冻结某个损失函数、benchmark、新 architecture 或论文故事。选“小问题”前先复现真实 NPC 行为学习底座，读透近邻方法与评估，再从实际现象形成 idea。此前 E03/E04 特定实验被用户否决为主线，仅保留历史。

## 入口
| 任务 | 文件 |
|---|---|
| 最重要：原生游戏 NPC 论文、审稿尺度、竞争近邻 | [knowledge/NATIVE_GAME_NPC_FRONTIER.md](knowledge/NATIVE_GAME_NPC_FRONTIER.md) |
| 领域问题与训练方案的探索地图 | [knowledge/METHOD_TERRITORIES.md](knowledge/METHOD_TERRITORIES.md) |
| 开放研究入口、真实可证伪 pilot | [EXPLORATION_ENTRY.md](EXPLORATION_ENTRY.md) |
| 公开代码和无需云 API 的可执行性 | [BASELINES.md](BASELINES.md)、[LOCAL_FIRST.md](LOCAL_FIRST.md) |
| 原生基线的运行前准入与实测 | [experiments/E05-native-npc-baseline-gate.md](experiments/E05-native-npc-baseline-gate.md) |
| 研究者自主行为与独立知识库 | [AGENTS.md](AGENTS.md)、[knowledge/README.md](knowledge/README.md) |
| 历史：目标 vs 计划假说、LLM 对话/竞赛 | [knowledge/GOAL_CONTROL_REVIEW.md](knowledge/GOAL_CONTROL_REVIEW.md)、[experiments/README.md](experiments/README.md) |

## 执行/证据状态
本轮**仅公开论文/代码核验和 workbench 研究方向重整**；未复现新模型、未跑游戏 episode、未投入 GPU；L1+ 科学主张数为 0。所有论文按已读原文/摘要/源码区分；arXiv≠ICML/NeurIPS 录用。核心闭环 **0 付费推理 API**；研究室十余张 A100、8 张 PRO6000、实习单位16张 H20，弱互联/弱I/O：单卡/单节点独立训练与多种子/多环境并行，先以实际 CPU 环境步速、磁盘和模型时延定预算。

用户已否决上一轮切口优先级，但**没有否决“目标与计划”问题本身**；它现为众多可能行为失败之一，不再锁死工作台。旧结果 E01 仅 CPU 源码合约检查（不是 NPC 行为结论），E02/E03/E04 未有科学结果。
