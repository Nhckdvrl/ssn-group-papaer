# Positioning：现有能力、最近邻与真实增量（初始版）

**2026-10-21；状态：研究入口定位，非完整最新近邻扫描。** 证据身份、完整论文阅读范围和局限以原 [文献总账](knowledge/READING_CATALOG.md) 与规范卡为准；本页不冒充逐篇重新全文阅读或已运行强模型。后续按根目录 R6 更新正式接收、预印本版本与 claim ownership。

## 1. 近邻已经占据的空间

| 研究谱系 | 关键近邻 | 已有能力；不能再声称什么 | 还值得询问的增量 |
|---|---|---|---|
| 人物化推理与训练 | [Thinking in Character](../../library/themes/game-npc-social/papers/THINKING_IN_CHARACTER_2025.md) · [HER](../../library/themes/game-npc-social/papers/HER_2026.md) · [CRPO](https://proceedings.mlr.press/v306/tang26c.html) | 已有 role-aware reasoning、场景化奖励、角色相关 RL；“让 NPC 先内心思考”不是新主张 | 推理是否决定了未见互动中的行为，而不只输出风格 |
| 人物条件规则与认知 | [CDT](knowledge/papers/CDT_2026.md) · [ThinkPersona](https://aclanthology.org/2026.acl-long.449/) · [RoleCDE](https://aclanthology.org/2026.findings-acl.106/) | 条件决策树、经历驱动推理、角色价值冲突已有直接研究 | 从稀疏修订/行为中学习非显式逻辑并跨情境泛化 |
| 人物状态、成长与记忆 | [ArcANE](../../library/themes/game-npc-social/papers/ARCANE_2026.md) · [MDRP](../../library/themes/game-npc-social/papers/MEMORY_DRIVEN_ROLEPLAY_2026.md) · [Dynamic Persona Coherence](knowledge/papers/DYNAMIC_PERSONA_COHERENCE_2026.md) | 已知文学人物阶段、记忆分面与身份—状态分离已有成果 | 玩家新增经历带来的选择性更新、回溯重评、后续策略作用范围 |
| 情绪、关系与可解释更新 | [OSSE](../../library/themes/game-npc-social/papers/OSSE_SOCIOEMOTION_2009.md) · [FAtiMA](../../library/themes/game-npc-social/papers/FATIMA_MODULAR_2014.md) · [Chain-of-Emotion](../../library/themes/game-npc-social/papers/CHAIN_EMOTION_2024.md) | 情绪评价、非对称关系、情绪来源、自然语言 appraisal 不是新模块 | 新证据如何改变旧解释并影响后续行为，而非只提升情绪文本分 |
| 原创人物作者编辑 | [ORIBA](../../library/themes/game-npc-social/papers/ORIBA_2025.md) · [Bonsai](../../library/themes/game-npc-social/papers/BONSAI_2026.md) · [WhatELSE](../../library/themes/game-npc-social/papers/WHATELSE2025.md) | 作者试演/修订、持久分支与编辑提规则已有工作 | 修订的语义范围、跨场景泛化、作者对意外接受与拒绝的区分 |
| 可读性与角色表演 | [Bates/Oz](../../library/themes/game-npc-social/papers/BATES_BELIEVABLE_EMOTION_1994.md) · [PersonaEval](https://arxiv.org/abs/2508.10014) · [HRI Legibility](https://doi.org/10.15607/RSS.2013.IX.061) | 可信人物与通过行为推断意图/身份有经典和近期研究 | 玩家在未见情境预测与互动中是否获得可使用的人物理解 |
| 叙事与玩家能动性 | [IPOCL](../../library/themes/game-npc-social/papers/IPOCL_2010.md) · [DiaryPlay](../../library/themes/game-npc-social/papers/DIARYPLAY2026.md) · [Bonsai](../../library/themes/game-npc-social/papers/BONSAI_2026.md) | 人物动机、剧情管理、作者/玩家可编辑互动已有谱系 | 人物外显行为作为玩家可察觉、可利用的叙事机会 |
| 强训练新近邻审查债 | [Persona Circuit](https://proceedings.mlr.press/v306/qin26h.html) · [DynSess 预印本](https://arxiv.org/abs/2605.29256) | 激活空间人格控制、会话级角色策略训练已有工作；具体接收身份/评测范围须补核 | 新表征/轨迹目标相对近期方法的严格额外价值 |

## 2. 重要非贡献与数学边界

- “2×2 角色 × 干预符合写在角色卡上的偏好”可能只是阅读理解；结果必须区分显式规则遵循与未显式条件的行为归纳。
- “隐藏一个心理锁 + 满足逻辑条件就给奖励”是可验证游戏机制，不自动是人物认知学习；线性效用 `wᵀφ` 只是可选受控模型。
- 相同历史下的 NPC 不同行为优势，不能用不同玩家输入的回报差直接替代；跨分支 KL 也不会自动带来策略免疫。
- 对前一轮自己的动作分布使用 stop-gradient KL，不保证 Martingale/时间自洽；前一轮本身可能不正确，玩家施压也可能是关系事件。
- 盲态 Observer 识别人设或未来动作，可被口头禅与死板策略投机；高可预测不等于丰富、可玩的角色。
- 最大化 player empowerment / mutual information 不能替代叙事质量；更高可控性与合理的不可逆结局有时相冲突。
- 不能从新模型/新术语自动推断顶会 novelty；精确撞车、强近邻压缩风险和证据范围逐项判断。

## 3. 强普通系统原则

目标不是故意使强模型失败，而是确认可研究能力与方法需要的尺度：

1. 合理角色卡、人物示例与反例、完整相关历史、明确事实和主观知识边界，合适的推理空间、普通记忆/反思与角色必要的行动反馈。
2. 单独检查 persona 条件本来是否充分显式；原始经历归纳、条件优先级、人物编辑及长程更新不应被简化成明显规则填空。
3. 严肃考虑同信息的规则提示/条件树、SFT/Role-aware 方法、记忆方案、角色专用后训练；比较真正的行为与玩家可理解后果。
4. 区分原作事实、角色误信、作者边界、叙事许可与玩家意图；不让手写唯一正确情绪/选择覆盖合法多解。
5. 数据/模型/玩家独立性，以及工具和裁判的偏差，应与新方法自身收益分开判断。

## 4. 尚未建立的证据

- **0 个本线已运行实验；0 条实验支持的角色新机制主张。**
- 尚未确定某一个 A–H 研究切口是最优；还没有本线新的人类玩家/作者数据、训练集或复现曲线。
- B–E 的已有知识库可提供历史事实与警示，但不能凭其文献数量宣称强基线已经复现。
- 具体实验条件、首批模型与研究问题的取舍，要在定位和人审时独立确定；不得从本文直接自动执行。
