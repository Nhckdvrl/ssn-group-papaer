# Game NPC Agents｜游戏世界中的交互式角色智能体

**状态：PROPOSED。** 用户已批准创建并继续研究；现有 ACTIVE 分配不变。
**最新更新：2026-10-13 第二轮，已进入正文/源码核查与 CPU 测量合约检查；尚无模型行为发现。**

## 当前科学问题与优先级

长期领域中心仍是：NPC 怎样依据自己的经历、知识、角色目标行动，并与玩家及游戏世界发生可信的交互？六个开放方向见 [RESEARCH_TERRITORIES](RESEARCH_TERRITORIES.md)。

本轮更具体的**优先测量问题**：**角色信息何时应该改变 NPC 的选择，何时不应干扰本来明确的任务行动？** 不是预定“persona 越强越好”或“删 persona 就好”，也没有宣称这是一片无人研究的空间。

[EXPLORATION_ENTRY.md](EXPLORATION_ENTRY.md) 解释为何现在问、自然数据需要什么、哪些结果会改变判断；[POSITIONING](knowledge/POSITIONING.md) 列出已有工作占据的认识。当前优先做 CPDC 等自然角色工具任务的数据/许可/lineage 审计，再决定是否进行单节点冻结模型的配对诊断。

## 这次实际推进了什么

- 新增 KNUDGE、CDT、NCP、PCSP、CPDC 五份逐篇研究笔记，记录方法/数据/对照、idea 起源重建和阅读范围；不是把 36 条初始索引全部称为精读。
- 修正底座分类：KNUDGE 是作者侧图生成；CDT 的语义条件树主要支持行动文本预测，但也有多轮交互实验；NCP 的 narrator 审核不等于独立游戏引擎；CPDC 指定公开 sample 有动作 schema/gold replay，不是完整交易世界。
- 修正对 NCP 的遗漏：原文已有匹配审核器的 HiAgent 对照、多审核器/人审和自然玩家输入实验，不能当成我们的新想法。
- **E01 实际执行：8/8 源码合约检查通过，0 模型调用，0 GPU·时。** 检查的是纯指标函数与动作声明，不是 NPC 能力；没有重算原论文主表/图。

## 研究与复现入口

| 文件 | 用途 |
|---|---|
| [knowledge/CORE_NOTES.md](knowledge/CORE_NOTES.md) | 最新逐篇深读入口及初稿修正 |
| [knowledge/README.md](knowledge/README.md)、[领域地图](knowledge/LITERATURE_MAP.md)、[初始文献总账](knowledge/PAPER_LEDGER.md) | 本 workbench 内部知识库；初始扫描与本轮阅读范围分开 |
| [knowledge/POSITIONING.md](knowledge/POSITIONING.md) | 最近邻已占主张与我们的认识债 |
| [knowledge/SOURCE_AUDIT_2026-10-13.md](knowledge/SOURCE_AUDIT_2026-10-13.md) | 核查代码路径、版本 blob 与证据范围 |
| [EXPLORATION_ENTRY.md](EXPLORATION_ENTRY.md) | 当前问题、竞争解释和自适应实验入口 |
| [BASELINES.md](BASELINES.md) | 修正后的资产分类与资源边界 |
| [knowledge/MEASUREMENT.md](knowledge/MEASUREMENT.md) | 数据、行动轨迹、对照和统计原则 |
| [AGENTS.md](AGENTS.md) | 本地 agent 自主研究与反漂移规范 |
| [E00](experiments/E00-baseline-feasibility.md) / [E01](experiments/E01-source-contracts.md) / [E02](experiments/E02-role-relevance.md) | E00 完整准入未完成；E01 CPU 检查 DONE；E02 数据/行为探索 PLANNED |
| [审计脚本](scripts/audit_source_contracts.py)、[实际结果](results/E01_source_contracts.json) | 可复算的源码合约，不是模型 benchmark |
| [CLAIMS.md](CLAIMS.md)、[PAIN_LOG.md](PAIN_LOG.md)、[本轮日志](logs/2026-10-13-deep-read.md) | 无本地 NPC 科学主张；明确哪些做了/没做 |

## 范围与科研尺度

不把 roleplay chatbot、玩家 agent、narrator、NPC policy 混为同一任务。**离线角色决策/作者侧生成本身可以有研究价值**；只是不能用它们的结果直接支持未测过的游戏内闭环能力或玩家体验。

不预定方法名、训练配方或贡献数量。不凭源码常识宣布论文级发现，不把“内外指标不同”“角色妨碍工具调用”等已有认识冒领为 novelty。若自然数据支持不了当前问题，可以主动重新选问题/资产，而不是全面合成来制造现象。

## 资源与实际状态

研究室十余张 A100、8 张 RTX PRO 6000；实习方 16 张 H20。网络/I/O/互联弱，单卡/单节点起步，多 GPU 用于真正独立的实验；不默认所有卡同时可用或跨机构资产可共享。

**正式 baseline 复现 0；自然 NPC 模型 episode 0；L1+ 科学主张 0；模型调用/GPU 0。** E01 仅在当前工作容器运行，未接入用户服务器。没有完整新数据集或模型权重下载；没有运行全仓库 process checker。

目标会议随最终贡献形态考虑 ICML/ICLR/NeurIPS 或 ACL/EMNLP/NAACL 主会；不填推测截止日、不按周倒排。只更新本 workbench，不恢复已删除的旧 NPC 工作台。

规则：[根 AGENTS](../../AGENTS.md)、[EXECUTION](../EXECUTION.md)、[IDEA_EXPLORATION](../IDEA_EXPLORATION.md)。初始授权与历史状态见 [初始化日志](logs/2026-10-13.md)；当前以本页及第二轮日志为准。
