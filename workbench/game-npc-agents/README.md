# Game NPC Agents：领域工作台

**持续研究中的源纠正：** D-E03的Monte Summary误把14原生叙事单元改为117文学章号；六作品S相关比较暂撤回，其他V/A与D-E02/04–06保留。[纠正与修复](mine-d-affect-relationships/results/D-SOURCE-CORRECTION-2026-10-22.md)；D-E06连续更新仍在运行，D-E07按正确来源继续。

**状态：ACTIVE-MAIN。2026-10-22用户明确暂停B/I01，优先转入本工作台现有矿区D：动态角色认知与长期人物演化；矿区C/NCP-Bench保留为备选。** 当前是公开资产上的研究驻留，优先ArcANE、PHASE-Tree/LongEvoRoleBench，不提前锁定方法或预设失败。B的E01–E03及历史矿区A资产保留；A仍CLOSED／TERMINATED。

本工作台维护游戏NPC的行为控制、人物表现、人机互动、叙事、社会、玩家体验、作者工具与运行部署知识。先理解不同角色在游戏中承担什么功能，再比较方法、证据和仍然存在的问题。具体研究项目各自保留进展与主张，外围知识库按整个领域组织。

## 当前主线：矿区D（2026-10-22）

核心问题：Role-playing Agent如何利用截至当前可获得的经历，形成、更新并表现人物状态，同时保留仍成立的身份特征？优先进入[矿区D](mine-d-affect-relationships/README.md)，先复现强官方基线，再从真实现象探索；[矿区C](mine-c-shared-narrative/README.md)为叙事方向备选。

首夜[D-E01–D-E05实测及科研报告](mine-d-affect-relationships/results/D-OVERNIGHT-REPORT-2026-10-22.md)已完成：1,481条角色回复、256条本地状态更新、Step5 65次Plan请求得到64状态，另有章节教师/完整内容评分/原句预测。ArcANE专用8B在原生Arc下APF/PTF78.05/83.48，通用8B65.93/60.92；PHASE文本状态对普通卡重写Sem+0.234、NLL−0.318。现有方法有效；强Step修复主要主体错配，但三模型都将已收回金表记成送出，评委也可能漏核最终事实。当前无新机制/算法主张，继续围绕有据状态形成及其后续人物行为，不做局部坏例调参。完整范围/不确定性见报告与[资产表](mine-d-affect-relationships/ASSETS.md)。

**持续推进：** [D-E06](mine-d-affect-relationships/experiments/D-E06-closed-loop-state-enactment.md)连接29人物的8轮状态更新与后续表演；[D-E07/08案例](mine-d-affect-relationships/results/D-E07-CASEBOOK.md)区分摘要源错配、人物整理错配与实际行为，Step同信息82次Plan请求已得到81卡，修复部分归属并保留材料不足，完整下游评分继续。[D-E09](mine-d-affect-relationships/experiments/D-E09-full-prefix-character-memory.md)已冻结6人物/15probe/47phase的完整来源前缀普通记忆参照，排入前序测量后的空闲卡。主问题始终是经历怎样形成这个人物的状态，并影响多个情境中的实际表演；不是累计调用数或预设新RL。

## B/I01历史实测（已暂停；2026-10-21）

- **E01：** Qwen3-8B、Llama-3.1-8B-Instruct、Step5各60请求，Step另1次截断恢复。Original / Situated / Explicit合成规则一致分别为 **75/75/100%、60/90/100%、90/85/95%（预算恢复后100%）**。Step只用Token Plan入口；严格格式与围栏恢复另报。
- **E02：** 64次Qwen调用；Situated原15/20，一句提示16/20，去原卡16/20，完整卡重写18/20；重写Preserve 7/12→11/12，但Change 8/8→7/8。
- **科研判断：** 完整规则动作执行已足够好；仍欠确定的作者边界不能判能力失败。优先核查旧规则与新例外如何整合，以及动作—台词联合约束；不提前训练RL。Decision-identifiable Accuracy分母0，四故事不能作245独立样本。
- **证据入口：** [E01完整报告](results/e01/REPORT.md) · [E02报告](results/e02/REPORT.md) · [全量台词](results/e01/CASEBOOK.md) · [CLAIMS](CLAIMS.md) · [PAIN_LOG](PAIN_LOG.md)。
- **资产位置：** `results/e01/`、`results/e02/`存任务/配置/评分及无损压缩raw（245条合计约110KB）；[哈希索引](results/raw_manifest.json)。本地解压raw同目录git-ignore；权重在`/home/xiang/.cache/huggingface/hub/models--*/snapshots/<revision>`，不入Git。版本与复算见[工具说明](experiments/scope_edit_pilot/README.md)。

## 领域入口

| 想了解什么 | 入口 |
|---|---|
| NPC类型、17个交叉方向、已有路径与覆盖空白 | [领域地图](knowledge/DOMAIN_ATLAS.md) |
| 全部专题与文献导航 | [通用知识库](knowledge/README.md) |
| 两批138项独立工作、版本、阅读范围与未读欠账 | [阅读总账](knowledge/READING_CATALOG.md) · [机器记录](knowledge/READING_CATALOG.json) |
| 身体动作、游戏控制、队友适应、对手与难度 | [学习、控制与人类合作](knowledge/LEARNING_CONTROL_AND_HUMAN_COOPERATION.md) |
| 人物知识、表达、原创角色、角色训练与评价 | [角色学习与评价](knowledge/ROLE_LEARNING_AND_EVALUATION.md) |
| 叙事规划、情绪、社会推理、群体与制度 | [叙事、社会与制度](knowledge/SOCIAL_SIMULATION_AND_NARRATIVE.md) |
| 玩家价值、开放交互、作者工具与创作控制 | [玩家体验与作者工具](knowledge/PLAYER_EXPERIENCE_AND_AUTHORING.md) |
| 模型、接口和系统对照；评价与主张是否匹配 | [强基线](knowledge/STRONG_BASELINES.md) · [测量规范](knowledge/MEASUREMENT.md) |
| 通用系统、开源候选资产与适用边界 | [BASELINES](BASELINES.md) |

2026-10-18的外围扩展登记96项独立工作；2026-10-19围绕四个兴趣方向新增42项及42张规范卡。正文、附录、理论/报告/书章、demo与正式长文分别登记，旧卡不随更新日期自动升级。更早31项经典系统与开放合作阅读保留为[定向专题](knowledge/FIELD_REVIEW_2026-10-18.md)，不与两批不同范围简单相加为“全文总数”。

## 当前主线：Role-playing Agent 研究驻留（2026-10-21）

**核心问题：** 一个角色如何从设定、行为示例、人生经历与玩家互动中形成自己独特的认知与行为规律；如何合理改变，并通过人物表演使玩家理解、参与故事？聚焦单角色 Role-playing Agent，不研究通用游戏操控、多智能体社会模拟或博弈胜率；允许轻量叙事状态/动作验证真实后果。

| 新线文件 | 内容 |
|---|---|
| [RESEARCH_AGENDA](RESEARCH_AGENDA.md) | 四个学术中心、A–H 八个开放假说与交叉问题；**并非 8 个已立项项目** |
| [POSITIONING](POSITIONING.md) | 正式近邻、强普通系统、方法与评测的风险边界 |
| [CLAIMS](CLAIMS.md) · [PAIN_LOG](PAIN_LOG.md) | 新驻留独立的主张和痛点账本，注册时都为空 |
| [ideas](ideas/README.md) · [experiments](experiments/README.md) · [日志](logs/2026-10-21.md) | 后续研究资产与决定记录，注册时无实验 |

**历史隔离：** [矿区 A 的终止结论](mine-a-persona-strategy/CLOSEOUT.md)与旧 C01–C06/E01–E85 全部保留原位，不继承为本研究证据；B–E 的知识与论文卡继续复用，不复制第二套。新研究没有自动承继旧研究的算力、API 或外部资源授权。

## 首个具体研究焦点（2026-10-21运行前历史；最新结果见上节）

经用户授权从开放议程中选一条直接开始，当前选择 **B：Scope-Aware Character Editing（角色行为修订的语义作用范围）** 为第一条研究 idea [I01](ideas/I01-scope-aware-character-editing.md)。对照基线与定位见 [E01](experiments/E01-scope-aware-character-edit-baseline-gate.md) · [PAPER_SHAPE 草稿](PAPER_SHAPE.md)。已建立最小 [scope_edit_pilot](experiments/scope_edit_pilot/README.md) 评分骨架，当前仅有本地协议自检，**没有任何模型/玩家实验结果**。

问题是：作者修改角色的一项行为原则，哪些陌生场景中的**选择**应该改变，哪些社会关系、行为及语气应该保持？作者意图的变化可能是例外、条件原则或人物整体重塑；不能预设所有编辑必须局部。**其他 A–H 仍在 RESEARCH_AGENDA 内开放，不代表已经开八个项目。**

**I01 近邻审查后更新（2026-10-21）：** 首个焦点进一步改为 **Learning the Scope of Character Revisions from Situated Creative Feedback**。区分作者已明确概括的原则与仅针对一次试演的现场批注；后者可能无法唯一决定相关情境与通道边界，允许澄清，而不是强迫猜测隐藏规则。见 [I01](ideas/I01-scope-aware-character-editing.md)、[E01 v1.1](experiments/E01-scope-aware-character-edit-baseline-gate.md) 与 [研究评测 V1.1](experiments/scope_edit_pilot/README.md)。仍未运行新模型实验。

**I01 第三轮研究校准（2026-10-21）：** 纳入 [Persona-guided scope induction](ideas/I01-scope-aware-character-editing.md)，但区分先验偏好、当前动作可辨识与真正作者意图；首次 60 条请求保持不变。开发者标记的 `situated_scope=supported` 不再冒充严格可判对错的金标，见 [E01 V1.2](experiments/E01-scope-aware-character-edit-baseline-gate.md)。尚无任何模型推理结果。

## 新矿区

先读[四矿区总图与当前选题判断](MINES.md)，再进入对应研究地图和近邻定位。

| 矿区 | 核心问题 | 入口 |
|---|---|---|
| B：可塑造、可延展的角色扮演 | 作者塑造/修订人物，人物承接玩家的新处境与合理变化 | [矿区B](mine-b-character-enactment/README.md) |
| C：可共同改写的角色叙事 | 人物、玩家与作者怎样共同改变故事，谁能改什么 | [矿区C](mine-c-shared-narrative/README.md) |
| D：可理解的情绪与关系演变 | 经历与新证据如何改变人物解释、情绪、关系和表达 | [矿区D](mine-d-affect-relationships/README.md) |
| E：玩家可理解的互动自由 | 玩家怎样发现、表达、判断并使用互动可能 | [矿区E](mine-e-player-agency/README.md) |

四个矿区各有完整问题空间、强近邻、普通系统参照、可能贡献与未运行的进入设计；目前未锁定新方法或论文。人物表达、情感立场、戏剧意义与创作价值可以独立成立，声称改变游戏机制时才需相应执行后果。

## 历史研究与工作规则

| 内容 | 入口 |
|---|---|
| 矿区A：人物设定、自身目标与战略行为 | [矿区A](mine-a-persona-strategy/README.md) |
| 矿区A为何失败、全过程、教训与资产 | [终止总结](mine-a-persona-strategy/CLOSEOUT.md) |
| 矿区A独立研究价值审查 | [独立审查](mine-a-persona-strategy/results/audits/INDEPENDENT_RESEARCH_VALUE_REVIEW_2026-10-18.md) |
| 领域规则、资源与维护边界 | [AGENTS](AGENTS.md) |

一篇研究保留一张规范论文卡，跨目录引用；知识、实验卡、结果和主张各在原有目录维护。原始轨迹、世界及权重的入口见[数据说明](mine-a-persona-strategy/data/README.md)。

**仅历史矿区A的 I01–I04 及其论文推进终止，不代表本 Game NPC Agents 工作台的新 Role-playing 驻留已关闭。** C01–C06原证据等级作为历史保留。矿区 A 目录里的旧“下一步”、脚本、原资源授权与设计不构成启动授权；**A 的商业模型验证与论文推进不恢复**。新 Role-playing 驻留按其独立账本和根执行协议推进。
