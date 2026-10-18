# NPC目标与控制：角色、作者、玩家和世界的不同职责

更新：2026-10-18。本页从NPC控制的完整谱系出发：角色选择、身体与技能执行、作者意图、戏剧组织、玩家适应和系统维护。合作中的目的／承诺只是其中一种情境。新论文的正文阅读见[总账](READING_CATALOG.md)；较早定向文献的具体范围在本页末保留。

## 1. 不同控制目标应有不同所有者

| 层次 | 谁规定目标或边界 | 典型方法 | 应检验的控制能力 |
|---|---|---|---|
| 世界规则 | 游戏设计和引擎 | 状态机、动作前提／效果、权限和资源结算 | 结果合法、状态一致、可回放；不能用人物解释修改规则 |
| 角色行为 | 作者给定身份／目标，角色按可见信息选择 | 行为树、GOAP、BDI、效用策略、模仿／RL、LLM | 跨局势完成目的、合理中断、风格和边界、适合角色的失败 |
| 身体与技能 | 运动控制、资产与任务约束 | 动作图、轨迹优化、动作先验、技能策略 | 达成任务且运动自然、响应及时、动作可控 |
| 叙事组织 | 作者／导演系统 | 叙事规划、戏剧管理、事件图、生成与检查 | 角色动机和情节可理解、玩家表达与选择得到合乎作品目标的反馈、作者能修改和调试 |
| 玩家配合 | 游戏模式与玩家共同形成 | 伙伴建模、习惯适应、交流、让位与重规划 | 任务贡献、协调劳动、玩家参与空间和角色主见 |

这些目标可以冲突：更强的战斗策略可能破坏角色风格；更紧的剧情控制可能取消玩家选择；更积极的队友可能抢走玩家想完成的动作；更稳定的人格可能抹去应发生的成长。控制研究应说明保留什么权衡，而非把任一方的满足率当全局质量。[DeepMimic](../../../library/themes/game-npc-social/papers/PENG_2018_DEEPMIMIC.md)、[HSP](../../../library/themes/game-npc-social/papers/YU_2023_HSP.md)、[同伴研究](../../../library/themes/game-npc-social/papers/COMPANIONS_DISSERTATION2019.md)和[叙事综述](../../../library/themes/game-npc-social/papers/RIEDL_BULITKO_2013.md)分别提供这些不同压力的证据。

## 2. 经典方法已经提供的能力

**GOAP与ABL。** 动作前提、代价、context、执行反馈、失败替代、中断和恢复是成熟能力。ABL的joint behavior还维护协同行为的进入、暂停、成功和失败；GOAP可通过不同角色动作集合产生不同作风。不能把“有目标表”“计划失败后重新规划”当作新发现。相应2002/2005/2006原文在[前轮阅读§2](FIELD_REVIEW_2026-10-18.md#classical)保留。

**社会规则与角色动机。** CiF/Prom Week、Versu显式处理欲望、非对称关系、社会实践、接受／拒绝和历史效果。它们的困难包括规则组合和跨场景调参，以及让玩家理解、利用和改变人物的理由。解释是作者及玩家的操作界面，不只是模型输出一段自述。[经典社会系统原文与范围](FIELD_REVIEW_2026-10-18.md#classical)

**意图与冲突规划。** [CPOCL](../../../library/themes/game-npc-social/papers/CPOCL_2011.md)允许动机充分但被阻止的行动，使角色之间可以真正冲突；[Glaive](../../../library/themes/game-npc-social/papers/GLAIVE_2014.md)改善规划搜索；[Sabre](../../../library/themes/game-npc-social/papers/SABRE_2021.md)进一步建模深层信念和错误信念。它们展示“故事中的人物必须各有理由”可以成为可计算约束，但中央全知规划器不等同于各NPC自主推理。允许动机合理的失败也不保证故事有趣。

**体验管理。** [DODM](../../../library/themes/game-npc-social/papers/DODM_2006.md)把作者质量、玩家自由和干预代价放入同一优化问题。[StoryAssembler](../../../library/themes/game-npc-social/papers/STORYASSEMBLER2019.md)在选择后重新规划片段，既能连接外部小游戏，也显示组合式内容难以调试。它们说明作者不总是追求最大自主性；研究对象也可能是可控的故事空间。

## 3. 学习式控制改变了哪些前提

示范和RL可获得手写规则难以覆盖的动作细节，但任务奖励不保证风格。[DeepMimic](../../../library/themes/game-npc-social/papers/PENG_2018_DEEPMIMIC.md)的任务／示范联合目标、[AMP](../../../library/themes/game-npc-social/papers/PENG_2021_AMP.md)动作分布先验、[ASE](../../../library/themes/game-npc-social/papers/PENG_2022_ASE.md)可复用技能空间，分别把控制从指定轨迹扩展到风格和技能组合。[MultiGAIL](../../../library/themes/game-npc-social/papers/MULTIGAIL_2023.md)可混合少量示范行为模式，其persona主要是移动风格，不能解释成完整社会人格。

作者约束也不只等于奖励调权。[Direct Behavior Specification](https://proceedings.mlr.press/v162/roy22a.html)直接使用事件频率约束，分开行为边界和任务进展。原库已读§2–6及主要实验，未复现。它与条件策略、技能编辑、示教和作者反馈构成不同控制手段；应比较修改一项要求的成本、其他能力保留和新场景推广。

[Dynamic Scripting](../../../library/themes/game-npc-social/papers/SPRONCK_2006_DYNAMIC_SCRIPTING.md)在规则层在线适应，[Enemy Within](../../../library/themes/game-npc-social/papers/PFAU_2020_ENEMY_WITHIN.md)用玩家行为模型做难度适应，[MLMove](../../../library/themes/game-npc-social/papers/DURST_2024_MLMOVE.md)从职业轨迹学战术移动。它们分别优化适应、挑战和像人程度，不应被一张“最强敌人”榜单覆盖。详见[学习与控制](LEARNING_CONTROL_AND_HUMAN_COOPERATION.md)。

## 4. LLM带来的覆盖与新增负担

LLM扩展了开放表达、未枚举意图、人物知识和自然语言规范。对声称控制游戏状态或动作的系统，还需把建议落到可执行动作和作者约束。[F.A.C.U.L.](papers/FACUL_AAAI2026.md)、PUBG Ally采用高层语言理解／规划与原生快速执行；[Vox Deorum](papers/VOX_DEORUM_2025.md)也把LLM决策与游戏内部能力组合。这些是值得认真比较的整系统，不是裸模型提示。

[CDT](papers/CDT_2026.md)把人物逻辑从故事中诱导、验证后编码为决策树；同一知识线性化提示接近完整方法，说明知识质量与执行结构应分开。[NCP](papers/NCP_2026.md)研究长程互动叙事约束；[HAMLET](papers/HAMLET_2026.md)结合层次导演与角色执行；[WhatELSE](../../../library/themes/game-npc-social/papers/WHATELSE2025.md)和[Orchid-Creator](../../../library/themes/game-npc-social/papers/ORCHID_CREATOR2026.md)让作者编辑抽象结构和事件。这条线真正扩大的是作者表达空间与可检查性，同时增加规范编写、状态管理和调试负担。

普通重规划、检索和状态记忆能修复多少问题，是需要公平比较的事实问题。[ProAgent](../../../library/themes/game-npc-social/papers/ZHANG_2024_PROAGENT.md)依靠搜索控制与前置检查，[CoELA](../../../library/themes/game-npc-social/papers/ZHANG_2024_COELA.md)依靠模块化感知／通信／计划；不能把它们的表现归给一段提示或某个模型。反过来，已有模块也不证明组合后的作者成本和玩家体验已经解决。

## 5. 能形成一般认识的比较

| 要理解什么 | 应对照的解释 | 适合的结果 |
|---|---|---|
| 角色坚持或切换目标 | 信息不足、能力不足、任务规范不同、历史惯性、控制更新失败 | 同一信息与执行支持下的轨迹、合法替代与原目的达成 |
| 人物可编辑性 | 新表示确有优势，还是只是提供了更完整知识／示例 | 同知识提示／检索、显式规则、学习方法的编辑成本与保留率 |
| 叙事控制 | 降低违例，还是减少了玩家自由与角色动机 | 约束、可达分支（如适用）、作者劳动、玩家表达和理解联合报告 |
| 队友适应 | 识别玩家，还是只学会一套固定约定／代替玩家完成 | 未见伙伴、让位、玩家贡献、失败恢复和真人体验 |
| 多种控制方式组合 | 新组件收益，还是更多工具、信息和推理预算 | 信息／执行／预算匹配，以及整系统质量和维护代价 |

本页提供研究问题结构，不自动推荐一个特定模块，也不把所有任务转成目标保持试验。原生低层控制、剧情编排、角色训练与合作适应都可各自形成完整贡献。

## 6. 较早定向阅读继续有效的部分

| 来源 | 已有实际范围与重要限定 | 规范记录 |
|---|---|---|
| LIGHT / How to Motivate Your Dragon | 正文、任务／方法关键附录；7486 quests与2111示范分开，原伙伴无自身独立目标 | [Dragon原卡](papers/HOW_TO_MOTIVATE_DRAGON_2021.md)、[历史阅读](FIELD_REVIEW_2026-10-18.md) |
| Goal Drift（AIES2025谱系） | 方法、结果与历史控制定向阅读；工具性目标后切回原目标，不等于游戏长期关系 | [原文](https://arxiv.org/html/2505.02709v1) |
| Goal-Directedness | 原有§1–4及能力／上下文局限；子任务能完成不保证复合任务会运用 | [既有单篇卡](../mine-a-persona-strategy/knowledge/papers/GOAL_DIRECTEDNESS_ICML_2026.md) |
| Arghal等2026研究 | 原有§3–5／关键假设；无用钥匙、语义诱因与内部地图已研究；接收未核实 | [原文](https://arxiv.org/html/2602.08964v1) |
| Hypothetical Minds | 原有正文、§4.5成本、B.1、README；伙伴假设及其评价／修订已有比较；不是本轮新增全文数 | [正式ICLR2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/12f483f624b378f9f3058d8ecd3c7ff5-Abstract-Conference.html) |
| Bayesian Partner Modelling | 选择性重规划与周期／事件／LLM触发的比较；方法、主表与关键控制附录选读 | [原单一记录](../../../library/themes/game-npc-social/INTERACTION_PAPER_CARDS_2026-10-03.md) |
| alem / NARRA-Gym / Collab-Overcooked | 较早指定部分阅读，不升级本轮全文；作者接收公告与具体track核实程度分开 | [alem](https://arxiv.org/abs/2606.08340)、[NARRA-Gym](https://arxiv.org/abs/2605.08503)、[Collab-Overcooked](https://aclanthology.org/2025.emnlp-main.249/) |

矿区A的目标／承诺定向判断由[专属知识库](../mine-a-persona-strategy/knowledge/README.md)维护。外层保留完整控制地图，不由某一局部假设决定文献取舍。
