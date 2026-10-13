# Game NPC Agents｜从游戏角色的真实问题出发

**状态：PROPOSED；用户已授权持续研究，其他 ACTIVE 分配不变。**
**2026-10-13 第三轮：按用户纠正重新整理。CPDC不再牵引选题；默认核心研究闭环零付费API、全链路本地。**

## 当前判断

前轮过早从易于检查的竞赛工具接口，收敛到“角色信息是否干扰调用”，尚未充分证明它是值得深入的NPC研究问题。这一执行入口已撤回；[E02](experiments/E02-role-relevance.md)标为VOID/superseded，未运行、不是实验否定。既有论文笔记和[E01源码结果](results/E01_source_contracts.json)保留，不再拿它们支持该选题优先级。

现在以独立的学术与行业需求确定研究空间：**制作可控且有自身目标的角色；适应真实玩家的协同行为；共同经历产生的长期连贯；有用而及时的主动性。** 这不是四个已经找到的创新点。具体主张仍须从自然任务、强基线及有区分力的实验中形成。

**首先核查的研究底座：LIGHT/goal-driven角色任务。** 其身份、动机、对话和真实状态行动更接近NPC本体；不是因为旧/免费就选为论文数据。旧接口、短轨迹、数据/权重许可、当前模型能力均需确认。伙伴适应的MeltingPot/Overcooked谱系为备选，不自动转成泛用MARL项目。

## 工作入口：先读这几份

| 入口 | 解决的问题 |
|---|---|
| [领域问题谱系](knowledge/PROBLEM_GENEALOGY.md) | 重要性从哪里来，前人研究到哪，哪些还只是待调查判断 |
| [顶会尺度与研究动作](knowledge/RESEARCH_CALIBRATION.md) | LIGHT/Dragon、ICML行为控制、NeurIPS GAMMA、ICLR Hypothetical Minds、ICML Proact-VL的具体校准 |
| [游戏界一手证据](knowledge/INDUSTRY_EVIDENCE.md) | Ubisoft/KRAFTON的制作压力；研发说明与科学证据分开 |
| [全链路本地规范](LOCAL_FIRST.md) | NPC、伙伴、教师、记忆、裁判都计成本；不暗含大批外部API |
| [资产与代码核查](BASELINES.md) | 已读文件/版本、资源是否已发布、依赖和数据许可的债 |
| [下一步探索入口](EXPLORATION_ENTRY.md) | 从真实角色任务进入，不预先冻结论文故事 |
| [知识库索引](knowledge/README.md) / [文献账本](knowledge/PAPER_LEDGER.md) | 当前定向阅读与历史初筛分开，旧阅读卡继续可查 |
| [定位表](knowledge/POSITIONING.md) | 不能重新冒领的认识及如何证明真正增量 |
| [本地Agent指南](AGENTS.md) / [数据与测量](knowledge/MEASUREMENT.md) | 自主探索、负结果、构念效度和反漂移 |
| [实验索引](experiments/README.md) / [主张](CLAIMS.md) / [痛点](PAIN_LOG.md) | 没有NPC模型发现；不把源码测试当科研结果 |

## 哪些不再默认做

不按CPDC竞赛目标定义科研价值；不从免费toy函数开始自行证明重要性；不将“NPC+记忆/RAG/ToM/行为树”当独创；不把所有问题约化为工具调用、personality judge或单一总分。

不要求所有NPC论文都有符号引擎：叙事/人类体验可以是严肃问题，但必须有支持相应结论的证据。优先独立引擎是因为我们要降低执行反馈和API耦合，不是把其他研究一概排除。

不以最新会议标签代替全文阅读。NeurIPS 2026标题目录已筛查，但未完成每篇track/正文/资产核实；尚未完成全领域综述或确定论文新颖性。

## 实际进度与资源

本轮完成定向原文阅读、行业需求核对、若干官方源码入口核查和研究文档重整。**新模型运行0、GPU使用0、新行为结论0。** E01的8/8为前轮CPU源码合约结果，不是NPC实验。没有接入用户服务器，也没有声称本轮跑通LIGHT或复现任何主表。

研究室十余张A100、8张PRO6000，实习方16张H20；弱互联/弱I/O，单节点任务与独立实验优先。是否能跑由实际模型、KV cache、CPU与磁盘测量决定，不以总卡数估算。目标会议按真实贡献选择ICML/ICLR/NeurIPS或ACL/EMNLP/NAACL主会，不按周倒排。

本轮依据见[整理日志](logs/2026-10-13-reorientation.md)。旧版本及被替换计划可从Git历史追溯；未改其他工作台、全局配额或已删除项目。
