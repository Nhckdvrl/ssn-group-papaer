**当前执行（2026-10-22人类决定）：** B/I01暂停，优先在本工作台现有矿区D研究长期人物状态演化，C/NCP-Bench为备选。以下为保留的矿区知识地图，旧优先级不覆盖本次决定。

**实测更新（2026-10-24）：** D-E01–D-E13、三条标准SFT参照及本批审计已收尾，失败与缺失全部保留于[矿区D登记](mine-d-affect-relationships/experiments/README.md)。本页的早期未运行设计属于知识建图历史，不能据其自动重启任务。

# 四个新矿区：角色扮演、叙事、情绪与玩家体验

知识建图日期：2026-10-21。2026-10-19 用户要求深入四个兴趣方向，据此建立 B–E 知识/问题矿区，当时四区尚未独立启动实验。**2026-10-21 用户进一步指定将新的 Role-playing Agent 主研究线直接登记在同一 `game-npc-agents` 根目录（ACTIVE-MAIN），见 [研究议程](RESEARCH_AGENDA.md) 与 [研究定位](POSITIONING.md)。** 矿区 A 仍终止，历史主张不迁入新线；当前实测状态以上述D登记为准。

## 1. 四个矿区各自承担什么问题

| 矿区 | 核心问题 | 有意义的角色/玩法能力 | 首要判断对象 |
|---|---|---|---|
| [B：可塑造、可延展的角色扮演](mine-b-character-enactment/README.md) | 作者怎样塑造、修订并逐渐理解具体人物，人物怎样承接玩家的新处境？ | 角色有独特的表达、习惯、例外和主见，能合理变化；作者可试演、修改并发现新解释 | 具体人物、作者创作与可辨认的表演 |
| [C：可共同改写的角色叙事](mine-c-shared-narrative/README.md) | 玩家、人物与作者怎样共同改变故事，谁能改什么，变化怎样服务作品？ | 秘密可被争取或误解，冲突可转向，失败能续演，作者能保留意外并理解修改影响 | 可参与的故事、创作权限与作者作品 |
| [D：可理解的情绪与关系演变](mine-d-affect-relationships/README.md) | 共同经历及新证据怎样改变人物的事件解释、情绪、关系和表达？ | 人物可以仍愤怒却恢复信任，可以尊重对手却继续敌对；玩家能回应这些区别 | 事件意义、人物情感过程、关系与玩家体验 |
| [E：玩家可理解的互动自由](mine-e-player-agency/README.md) | 玩家怎样发现、表达、判断并驾驭NPC互动可能，哪些自由值得使用？ | 玩家能以自己的身份、措辞和社会策略参与，理解抵抗与意外，并从交互故障中恢复 | 玩家实际活动、解释、学习、体验与负担 |

这些是宽问题空间，不是四篇已经选定的论文。2026-10-21 新增的四学术中心与 A–H 八个假说见 [RESEARCH_AGENDA](RESEARCH_AGENDA.md)，它们跨 B–E，不等于八个已立项项目；当前具体候选与执行以矿区D登记为准。每区均有README、RESEARCH_MAP和POSITIONING，分别提供入口、问题谱系、最近邻与强参照。E有独立的设计与解释性问题，也帮助其他矿区检查人的价值；D的情绪不是给B加一个数值模块，C也不是给所有角色套统一导演。

## 2. 这批阅读真正改变了哪些认识

### 人物“保持不变”不是角色扮演的终点

经典Oz/Bates已经把人物内部过程、外显表演和观众解释分开。现代角色数据和训练能支持可配置人物，ArcANE进一步研究人物在已给定发展阶段的表现；这与玩家新经历如何形成尚未预写的未来不同。ORIBA的原创角色作者会通过试演修改设定并发现人物：最初设定遵循与作者后来认可的延展，应分别记录。[Bates](../../library/themes/game-npc-social/papers/BATES_BELIEVABLE_EMOTION_1994.md) · [Oz](../../library/themes/game-npc-social/papers/OZ_CENTRIC_REVIEW_1997.md) · [Crab](../../library/themes/game-npc-social/papers/CRAB_2025.md) · [ArcANE](../../library/themes/game-npc-social/papers/ARCANE_2026.md) · [ORIBA](../../library/themes/game-npc-social/papers/ORIBA_2025.md)

由此得到的候选认识是：角色质量应同时容纳**辨认、变化与作者再理解**。这不是证明了某个记忆或心理机制必需。MDRP对强Qwen3-Max的提示增量近乎零，ArcANE的短ArcHint对两个基础模型接近完整发展弧；完整普通模型必须是认真参照。[MDRP](../../library/themes/game-npc-social/papers/MEMORY_DRIVEN_ROLEPLAY_2026.md) · [B定位](mine-b-character-enactment/POSITIONING.md)

### 互动叙事要容纳意图的形成和改变

作者结局、人物意图、玩家介入之间的关系已有IPOCL、Sabre和戏剧管理的长谱系。自然语言storylet、普通剧情反思和可编辑可能性空间也已有直接研究。Bonsai甚至已经支持持久保存玩家产生的分支、作者修剪和从编辑积累意图；“我们也做一个导演/编辑器”距离新贡献很远。[IPOCL](../../library/themes/game-npc-social/papers/IPOCL_2010.md) · [GME](../../library/themes/game-npc-social/papers/GAMEPLAY_MEDIATION_2014.md) · [Dramamancer](../../library/themes/game-npc-social/papers/DRAMAMANCER_2025.md) · [Bonsai](../../library/themes/game-npc-social/papers/BONSAI_2026.md)

本库据此保留的问题是：作者尚未完整表述或后来改变的意图，怎样与玩家的新解释相处？一次编辑是例外、规则还是新的创作方向？修改是否使下一批玩家得到更有意义的参与？Bonsai的主要定量条件直接读取完整模拟偏好，不能替代这一真实作者过程；已有正面结果同时要求对完整普通商业系统认真比较。[Bonsai证据边界](../../library/themes/game-npc-social/papers/BONSAI_2026.md) · [ACL 2025互动戏剧](../../library/themes/game-npc-social/papers/IMMERSION_AGENCY_DRAMA_2025.md) · [C定位](mine-c-shared-narrative/POSITIONING.md)

### 情绪关系的目标远比“更积极、更喜欢玩家”丰富

OSSE在2009年已区分触发、当前、表达情绪与非对称关系；自然语言appraisal也已有真人短时证据。关系代理在非游戏场景中通过脚本和历史引用，就能在一个月交互里改善部分关系感受。游戏研究记录友谊、保护、认同和欣赏等多种关系意义。不能把增加好感、情绪向正转或持续互动意愿当所有作品的目标。[OSSE](../../library/themes/game-npc-social/papers/OSSE_SOCIOEMOTION_2009.md) · [Chain-of-Emotion](../../library/themes/game-npc-social/papers/CHAIN_EMOTION_2024.md) · [Bickmore–Picard](../../library/themes/game-npc-social/papers/RELATIONAL_AGENTS_2005.md) · [角色依恋](../../library/themes/game-npc-social/papers/CHARACTER_ATTACHMENT_2019.md)

当前有价值的候选是事件如何被重新解释、关系怎样分化、表达是否承载了这种变化，以及玩家能做什么回应。CPM-MultiAgent在GPT-5.4主干上的均分增量很小，真人判断更偏向评价理由；这不能证明复杂情绪架构带来更好的游戏关系。CoRE也提醒情绪类别的确定性不等于心理有效性，合理多解需要保留。[CPM](../../library/themes/game-npc-social/papers/CPM_MULTIAGENT_2026.md) · [CoRE](../../library/themes/game-npc-social/papers/CORE_EMOTION_CONCEPTS_2026.md) · [D定位](mine-d-affect-relationships/POSITIONING.md)

### 自由、能动性和更长游玩时间不能互相代替

自由措辞、扮演不同身份、提出社会策略、改写故事和改变游戏机制是不同能力。能动性理论与表达性选择研究允许结局不变但表达有意义；VRST、CoG等短研究则表明自由输入与引导各有取舍。时间增加可能包括输入、等待和修复；未显著不同也不证明两种体验等价。[Agency Reconsidered](../../library/themes/game-npc-social/papers/AGENCY_RECONSIDERED_2009.md) · [叙事选择](../../library/themes/game-npc-social/papers/NARRATIVE_CHOICE2022.md) · [VRST 2024](../../library/themes/game-npc-social/papers/PRESENCE_VRST_2024.md) · [CoG 2025](../../library/themes/game-npc-social/papers/OPEN_ENDED_DIALOGUE_2025.md)

玩家是否发现、理解、愿意使用一种能力，应与系统是否能完成分开。玩家不使用不自动表示不需要；引导可能同时改变玩家表达和模型意图识别。PXI适合部分体验构念，不能把所有分量表合成总体验，也不能替代角色关系与叙事理解；关于AI创作来源的态度和推测还需与实际游玩、标签因果分开。[PXI](../../library/themes/game-npc-social/papers/PXI_2020.md) · [独立验证](../../library/themes/game-npc-social/papers/PXI_VALIDATION_2024.md) · [Imitation Game](../../library/themes/game-npc-social/papers/IMITATION_GAME_2026.md) · [E定位](mine-e-player-agency/POSITIONING.md)

## 3. 当前最值得继续深挖的交叉问题

以下优先级是基于目前阅读的**选题建议**，不是研究状态变更，也不排除单区的设计、理论或方法工作。

| 候选 | 为什么有优先深入价值 | 最强反证/竞争解释 | 最需要的下一层证据 |
|---|---|---|---|
| **B×C：可修改的人物延展** | 把作者试演/修订、玩家意外、人物未来和作品意义连起来；直接对应原创角色与叙事创作 | ORIBA、Crab、ArcANE、WhatELSE、Bonsai已覆盖很多组件；完整聊天/编辑工具可能足够 | 真实作者具体如何改人物、何种意外被保留、修改影响是否可理解，以及后续玩家怎样参与 |
| **B×D×E：有来由且可回应的关系变化** | 区分愤怒/信任、亲近/依赖、敬重/敌意，让变化形成角色扮演材料 | OSSE/脚本、完整历史强LLM、普通appraisal可能解决；玩家可能更喜欢稳定角色 | 同事实下的强普通系统残差，独立角色/关系类型，以及实际玩家对变化的解释和回应 |
| **C×E：可理解的叙事参与与戏剧阻力** | 研究秘密、冲突、失败和沉默怎样支持参与，避免所有输入导向快速和解 | 明确选项、合理披露状态、普通剧情反思/重规划可能足够 | 玩家想参与什么，何时把抵抗理解为人物、何时当成系统不懂，以及作品节奏的取舍 |
| **E独立：自由的发现、表达与恢复** | 即使底层模型强，人与作品的互动安排仍可成为实质问题 | 普通说明/优质选项可能足够；“不会用”也可能是模型误解输入 | 自然玩家过程、输入→解释→后果记录，接口改善的特定作用与额外负担 |

优先沿第一、第二条补真实创作和关系活动材料；它们最贴近本次兴趣且能把四条阅读链连接起来。若实际可接触的作者/玩家及作品不足，应缩小推断范围，不能用研究者随手写的少数刁钻对话代替领域需求。当前没有证据证明我们已有这些人群或资产优势。

## 4. 怎样用一轮高信息量工作选题

本页最初列出的进入设计是当时的未运行草案，后续实际执行以实验登记为准。共同原则是**先辨认人关心的完整活动，再检查合理普通系统到底差在哪里**，不先做几十种局部提示优化。

1. **确定作品与人的目的。** 选择独立作者/人物/故事机制，记录其想表达的体验与允许改变的范围。真实作品可以很小，但换名、复述和重复采样不增加独立世界。
2. **给普通系统足够信息和能力。** 使用届时可核查的强商业模型，完整人物资料、历史、知情范围、世界状态、工具反馈与普通重规划；情绪题纳入自然语言appraisal/成熟脚本，叙事题纳入storylet和普通编辑。模型型号与预算在正式设计时核定，本轮不调用。
3. **保留人的过程。** 作者的原意符合和后来采纳分开记；玩家可以表达、拒绝推进、挑衅、保持距离。真实输入、系统解释、回应/后果及人的后续解释分别可见，允许戏剧含混和有依据的多解。
4. **一次回答有限的因果问题。** 同时增加历史、声音、引导和新模型不能证明一个情绪模块有效。支持设计组合只能证明组合效果；想归因到某一步，需要相应比较。两次体验不足以区分新奇与学习，更不代表长期关系。
5. **让结果改变投入。** 强普通系统足够，则结束复杂方法候选或转向真实存在的创作/交互问题；只有内部指标上升，则不声称玩法收益；实际人群不重视，则接受不适配；跨作品存在人重视且简单支持未解决的压力，才考虑具体机制立项。

方法增量、解释性实证和创作/交互设计都是可能的产物；它们各自需要匹配的证据。不会因为一个组成部分已有工作就排除整体贡献，也不会因为四个方向都重要就默认任意组合有价值。

## 5. 阅读建设、范围与仍需补齐的部分

本轮新增**42个规范阅读条目、42张规范卡**：B为10篇现代论文和2篇经典技术报告；C为11项论文/理论文章/作者稿与1项demo＋设计短稿合并记录；D为9篇论文和1个完整书章；E为8篇论文。包含新正文阅读、旧摘要/选读来源的正式版补读；CoG开放对话、ACL互动戏剧在旧库已有同家族材料。正文范围、关键附录、身份、样本与限制全部进入[总账](knowledge/READING_CATALOG.md#mines-2026-10-19)。并非42篇已正式发表的顶会长文，也不是42份彼此独立的实证；同一研究的新题名/版本不重复计数。

前一批96项广域阅读与本批合为138项独立工作记录；更早31项含不同阅读范围，仍单独保留。六篇广域综述继续提供外层结构，本批补Oz与共同创作历史、appraisal综述章和原始研究链。原有17方向领域地图保留，四个兴趣矿区没有取代整个NPC领域。

仍有实质阅读债：完整多模态表演与演员创作、当代互动叙事综述和choice poetics、跨文化与非亲密关系、儿童/无障碍/不同玩法、真实玩家纵向关系、专业团队的长期制作与维护。RPGAgent、Beyond Pre-Defined Scripts、部分角色表演和测量论文尚未取得全文，明确排除于正文计数。持续阅读应由这些空白和可能推翻候选的证据驱动。

矿区A最终结论仍见[CLOSEOUT](mine-a-persona-strategy/CLOSEOUT.md)。本页最初建图只包含知识、问题和未运行设计；之后矿区D的真实模型工作单独登记，不继承或恢复A。
