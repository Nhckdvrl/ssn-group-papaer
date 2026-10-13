# 开源资产的真实对象与复现入口｜2026-10-13 第二轮

已从摘要/README 继续到指定正文/附录与代码。**没有任何完整模型 baseline 被本地复现。** E01 只检查两份源码的指标/声明契约；它不等于安装游戏、调用模型或达到论文数字。

## 不用一个“可执行”标签混掉所有任务

| 资产及官方入口 | 实际能支持什么 | 本轮核查后的边界 | 当前用途 |
|---|---|---|---|
| [KNUDGE](https://github.com/nweir127/KNUDGE) / EMNLP 2024 | 真实 RPG 背景下的作者侧对话图与知识使用 | 抽取简化部分游戏状态条件；图结构合法不等于完整任务引擎；原文也评价文本游戏效果 | 自然语料/知识与任务对话测量，不冒充在线 world |
| [CDT](https://github.com/KomeijiForce/Codified_Decision_Tree) / ACL 2026 | 情境化角色规则与行动文本预测，另有新情境多轮评价 | 条件依赖语义判断；树提供 grounding，动作未在该 benchmark 中改变独立世界状态 | 强角色逻辑方法/表示对照，构树/API 与本地推理分开记成本 |
| [NCP-Bench](https://github.com/NLP2CT/NCP-Bench) / ICML 2026 | narrator 的长期事实/承诺/玩家输入审核 | 状态更新与审核含 LLM；原文已有同审核器 memory 对照和审计验证 | 长程测量近邻，不能替代独立 NPC execution ground truth |
| [PCSP](https://github.com/yoosunghong/pcsp) / 2026 预印本 | persona 条件共享 RL、不同研究环境及 UE 接口 | 作者已做独立行为 probe；不能冒领其内外指标差异；未确认我们节点的完整复现 | 真实行为近邻，先核查研究层资产，不要求先装全 UE |
| [CPDC 官方任务](https://www.aicrowd.com/challenges/commonsense-persona-grounded-dialogue-challenge-2025) / [公开参赛实现](https://github.com/MahammadNuriyev62/CPDC-challenge-2025-solution) | 人物/背景/工具 schema/参考调用，适合离线调用决策分析 | 指定公开 sell/equip 是 pass；sample executor 是 gold matching，不代表私有官方 evaluator | **当前优先审计的数据候选**，还不是最终研究数据或在线游戏 |
| [Collab-Overcooked](https://github.com/YusaeMeow/Collab-Overcooked) / EMNLP 2025 | 必要协作、游戏动作与过程读数 | 料理伙伴与剧情 NPC 不等价；参考轨迹覆盖需审计；旧依赖尚未安装 | 后续真实协作底座候选，本轮未新增运行证据 |
| [TALES](https://github.com/microsoft/tale-suite) | 多种文本游戏中的玩家 agent | 主体是玩家，不是世界内独立 NPC；部分环境有 Java/数据许可依赖 | 执行接口与能力门槛的可迁移近邻 |
| [FAIRGAMER](https://github.com/BingkangShi/FairGamer) / ACL 2026 | 角色条件下的游戏决策评价 | 其指标与任务/角色影响的定义仍需深查 | 保留近邻，不能用初始 README 阅读假定已复现 |

逐篇证据：[CORE_NOTES](knowledge/CORE_NOTES.md)；实际文件/版本：[SOURCE_AUDIT](knowledge/SOURCE_AUDIT_2026-10-13.md)。

## 准入分层，而不是一律要求大型引擎

**离线决策研究：** 核对角色/任务信息、参考历史、可接受动作、标签歧义与数据切分；可以不建完整引擎，但结论只能及于给定历史条件下的决策。**在线能力研究：** 需要策略自己的动作改变状态、其错误传导到后续观测、独立执行反馈与可重放轨迹。两者均可有价值，不能混写。

完整复现应固定上游 Git/模型/数据/评价版本，并先跑作者强 baseline；使用本地替代 API 需要明确是改造条件。CPDC 现成多专家方法、Talk Less/Deflanderization 等应进入近邻/基线考虑，不能给新方法不公平额外预算。

E00 的数据、环境与成本门槛仍未全部通过。E01 证明两份指定源文件能按合约检查；E02 先做自然数据 census/lineage，再决定模型实验。数据不够支持问题就改变入口，不自动靠新引擎/全面合成补齐。

## 单节点资源与资产纪律

模型/数据先节点本地缓存；先实测显存、CPU RAM、输入输出长度、p50/p95 延迟、I/O、wall-time，再铺开独立场景/模型/种子。不把 A100、PRO6000、H20 当作统一高速集群，也不承诺未实测的 GPUh 或训练规模。

大数据、权重及原始长轨迹不进 Git；仓库保留可复算的小结果、脚本与 manifest。每项记录 source SHA、模型 revision、数据 hash、配置、seed、硬件和失败。实习的权限、模型、数据和网络边界单独核实，不上传私有资产或凭证。
