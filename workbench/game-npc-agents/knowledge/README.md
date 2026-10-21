# Game NPC Agent 通用知识库

这里维护整个游戏NPC领域的概念、方法谱系、实际系统、玩家与作者证据。NPC可以是对手、同伴、居民或剧情人物；叙述者、世界裁决器、模拟玩家和社会仿真与它们相邻，但研究目的和权限不同。知识库据此组织问题，不以任何单一矿区的任务定义筛选整个领域。

## 从地图到专题，再到原文

| 层次与问题 | 入口 |
|---|---|
| NPC功能、17个交叉方向、研究尺度与覆盖空白 | [领域地图](DOMAIN_ATLAS.md) |
| 逐篇版本、发表身份、正文／附录范围、来源与未读欠账 | [阅读总账](READING_CATALOG.md) · [JSON](READING_CATALOG.json) |
| 角色扮演、叙事、情绪、玩家体验的四个知识/问题矿区 | [B–E总图与选题判断](../MINES.md) |
| 动作风格、原生控制、学习、对手、难度和人类合作 | [学习、控制与人类合作](LEARNING_CONTROL_AND_HUMAN_COOPERATION.md) |
| 人物知识、表达、角色训练、原创人物与评价有效性 | [角色学习与评价](ROLE_LEARNING_AND_EVALUATION.md) |
| 叙事规划、情绪、群体关系、社会规范与制度 | [叙事、社会与制度](SOCIAL_SIMULATION_AND_NARRATIVE.md) |
| 玩家表达与选择、交互负担、作者工作流、可编辑性 | [玩家体验与作者工具](PLAYER_EXPERIENCE_AND_AUTHORING.md) |

四张综合页互相交叉：例如同伴自主性同时涉及合作、人物目标和玩家体验；叙事工具同时涉及作者控制、世界规则和角色表达。分组方便阅读，不表示独立学科或投入优先级。

## 跨方向的具体问题

| 问题 | 入口 |
|---|---|
| 角色目标、作者约束、规划、行为树、效用与伙伴适应 | [目标控制谱系](GOAL_CONTROL_REVIEW.md) |
| 强模型、普通记忆／规划／技能、脚本及信息权限 | [强基线原则](STRONG_BASELINES.md) |
| 评价构念、观察权限、独立样本、动作与体验证据 | [测量规范](MEASUREMENT.md) |
| 原生动作接口、训练、模块分工与部署 | [原生NPC前沿](NATIVE_GAME_NPC_FRONTIER.md) |
| 情绪、关系、记忆、人格变化与角色成长 | [人格与关系变化](PERSONA_DRIFT.md) |
| 生产、交易、资源、市场与制度 | [游戏经济](GAME_ECONOMY.md) |
| 知识权限、玩家说服、合法欺骗与越权防护 | [NPC安全](NPC_SECURITY.md) |
| 经典系统、开放合作与早期强系统的定向阅读 | [31项定向专题](FIELD_REVIEW_2026-10-18.md) |

方法研究需要公平对照与明确增量；玩家访谈、设计研究和创作实践需要与其问题相配的取样、分析和适用范围。人物表达、规则执行、玩家体验和作者劳动分别成立，不构成从“文本”到“引擎”的论文质量阶梯。

## 规范论文卡与维护方式

2026-10-18的广域批次登记96项，2026-10-19四矿区建设新增42项，合计138项独立工作记录。本批新增38项论文/理论文章/作者稿、1项demo与设计短稿合并记录、2篇技术报告和1个书章；来源身份与正文/附录范围分别保留。14张已有卡在[原论文目录](papers)维护，两批124张新卡在[游戏NPC主题文献目录](../../../library/themes/game-npc-social/papers)。更早31项含不同阅读范围，不简单相加为全文数。具体身份以[总账](READING_CATALOG.md)为准。

维护时先查现有规范卡，再补原卡。正文、附录、版本核对、代码、数据及本地复算分别记录；下载成功不等于读完，出版年份不等于实验模型年份，自动裁判不等于真人评价。发现错误时直接修改对应卡和专题，同时保留关键不确定性。未重读的旧摘要与索引继续标明历史范围。

更早的检索线索可从[主题文献入口](../../../library/themes/game-npc-social/README.md)查阅。第一方工业记录与旧玩家证据分别保留在[应用审计](../mine-a-persona-strategy/knowledge/PLAYABLE_NPC_APPLICATION_AUDIT_2026-10-16.md)和[玩家证据](../mine-a-persona-strategy/knowledge/PLAYER_VALUE_EVIDENCE_2026-10-16.md)的既有文件；新的跨方向玩家与作者综合由本目录维护。

## 与具体研究的边界

[矿区A知识库](../mine-a-persona-strategy/knowledge/README.md)及其`experiments/`、`results/`、`CLAIMS.md`保留终止前的历史证据，最终判断见[CLOSEOUT](../mine-a-persona-strategy/CLOSEOUT.md)。[B–E](../MINES.md)按用户新要求建立知识/问题目录，尚无实验项目。外围阅读直接修正知识理解，不自动改变研究状态或分配资源。

- 2026-10-21 E01后邻居发现：[Human Interventions as Labels](papers/HUMAN_INTERVENTIONS_AS_LABELS_2026.md)（官方摘要级，未全文复现；不计入此前138项阅读统计）。
