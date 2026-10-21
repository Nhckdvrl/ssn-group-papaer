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

## 5. 首个具体焦点 I01：角色修订的语义作用范围（2026-10-21）

用户选择进入实际研究，焦点为 [I01 Scope-Aware Character Editing](ideas/I01-scope-aware-character-editing.md)，但其他 A–H 保留开放。此处新近邻只核查官方摘要/元数据与仓库既有论文卡，**未冒充全文复现**。

- [The Persona Hierarchy Model（2026-10-07 预印本）](https://arxiv.org/abs/2610.09384) 已讨论微调中的局部/全局 persona 影响传播与 PPR；不能重做 context locality 就声称新颖。
- [BalancEdit（ICML 2025）](https://proceedings.mlr.press/v267/guo25e.html) 已讨论 generality-locality，范围辨认并非本线发明。
- [FinePE（Applied Soft Computing, 2026）](https://www.sciencedirect.com/science/article/pii/S1568494626003911) 与 [PERSONA（ICLR 2026）](https://proceedings.iclr.cc/paper_files/paper/2026/hash/f66ce276436c4cd151535b03841ac713-Abstract-Conference.html) 也在研究细粒度人格/激活编辑。

可辨认的增量必须是 **作者意图在人际关系、条件行为、叙事动作与语言表现之间的语义作用范围**，与一般事实编辑及 Prompt 上下文范围不同；具体困难存在与否待强普通基线与真实创作材料确认。[ORIBA](https://arxiv.org/abs/2512.12630) 有作者试演修改的人类需求证据，[CDT](https://aclanthology.org/2026.acl-long.568/) 是不可忽略的条件逻辑近邻。

初始 [scope_edit_pilot](experiments/scope_edit_pilot/README.md) 的四个人造角色、16 受控情境只能验证程序；明显存在显式条件阅读理解的天花板，**不是已建立的 Role-playing 能力缺陷**。

## 6. E01 v1.1 近邻实质审查补充（2026-10-21）

1. **CDT 不等于狭义手工规则树。** [正式 ACL 2026 论文](https://aclanthology.org/2026.acl-long.568/) 已通过故事场景/行动数据归纳、验证、逐层细化人物规则，并允许更新；作者仓库已有构建/评价实现。它是否会出现 Action–Style 耦合，只能通过同等输入与实际表现检验，不可先验断言。
2. **The Persona Hierarchy Model 不是作者 RPG 人物属性节点结构。** [2026-10-07 预印本](https://arxiv.org/abs/2610.09384) 研究特定 system prompt 下的**微调行为**向其它 Persona context 的局部/全局传播与 PPR，不能说它只测静态属性问答；也不能直接从其结论推出角色创作中的语义编辑范围。
3. **[Test-Time-Matching](https://arxiv.org/abs/2507.16799)** 已将人格、记忆与语言风格组织为独立测试时要素；「将 Action 和 Style 分开」作为设计常识而非新贡献。
4. **[Behavior Editing](https://arxiv.org/abs/2506.20606)** 与 **[Personalization Editing](https://arxiv.org/abs/2512.13676)** 已分别讨论 agent 行为和用户偏好的编辑/局部性；仅借用 ROME/MEMIT/IKE 的 efficacy/generalization/locality 并改为 role play 不足以立项。
5. **ORIBA 的证据边界：** [原文](https://arxiv.org/html/2512.12630) 中 14 位艺术家、其中 8 位在研究期间修改了 OC 配置；并没有对「仅凭单次 in-situ critique 推断潜在行为规则」提供系统性泛化检验。

**修订后的增量问题：** 从一幕创作反馈中恢复**不完整、可能多解的作者意图**，区分哪类行为变化受反馈支持、哪类必须澄清；仅在语义证据足够时检验跨人物/剧情动作的正确泛化与表达保持。它比「风格/行为完全分开」更明确，也比「隐藏金标的 if–then 文本分类」更不易制造伪失败。详见 [I01](ideas/I01-scope-aware-character-editing.md) 与 [E01](experiments/E01-scope-aware-character-edit-baseline-gate.md)。

## 7. 对「模型问作者澄清」的新近邻限制（2026-10-21）

- [Modeling Future Conversation Turns to Teach LLMs to Ask Clarifying Questions（ICLR 2025）](https://mlanthology.org/iclr/2025/zhang2025iclr-modeling/) 已通过模拟未来对话使模型学会在模糊请求下澄清；「能够问问题」本身不新。
- [Uncertainty-Aware Clarification in LLM Agents with Information Gain（ICML 2026）](https://proceedings.mlr.press/v306/deng26l.html) 已通过信息增益奖励训练 agent 澄清欠确定意图；不能把 entropy-based question selection 当未被研究的方法。
- 可能真正需要研究的是**原创人物的行为规则修改边界**：从一幕表演纠偏里决定哪些未知场景确实需要作者确认，是否能用少量针对性确认减少后续多场景返工，以及确认后是否在 NPC 决策/台词两类通道正确保持角色。强澄清策略、规则重写、完整作者人物卡都是直接近邻。
