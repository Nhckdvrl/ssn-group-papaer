# 2026-10-14｜仓库清理与用户选定矿区 A

## 用户选择与整理目的
用户认为 NPC workbench 因多次研究转向而混乱，明确选择**先从矿区 A（Persona vs Strategic Utility）** 挖掘。保留领域全景、安全/经济/人格动态等资产，不把 A 变成整个人生长期唯一方向。

## 清理事实
- 审计到多份冲突的旧入口：根 `LOCAL_AGENT_START` 仍指向已撤销的 E03/E04，`RESEARCH_TERRITORIES` 属于第三轮旧优先级，`configs/entry_manifest.json` 针对旧目标/计划世界，E00/E02–E05 从未实际运行。
- 将这些七个过时文件从当前HEAD清除，完整字节可以通过上一快照 37f4e9ba4152c3a21c36c73830897221a186924b 访问；不删除真实 E01 源码合约实验、其结果与原始代码，不删除领域地图和任何纸面精读。
- 精简根 README、当前探索入口、本地 Agent 入口、实验目录与 Idea/KG导航；新建矿区 A 的独立3份知识文件和 E06（PLANNED）。
- 未新建另一套 `npc-agent-workbench/kb/exp_engine`，避免与整个仓库工作流重复。
- 其他 workbench 与 ACTIVE 配额未改，仓库登记中 PROPOSED 不变。

## 新的最近邻更正
已核 PMLR ICML2026 《The Personality Illusion》正式录用/摘要，作者仓库/数据；2026《Rethinking Psychometric Evaluation》作者报告NeurIPS接受而本轮官方proceedings未独立核实，已读 README 和执行源码中 TPB Likert nudge/seed fallback；2026《The Story Shapes the Agent》预印本正文摘要发现 narrative priors 在同构行动实验中强于persona，属于非常近的claim owner；2026《Persona Vectors in Games》已报 activation steering/策略与修辞差异；PCSP 本身已有独立行为检查。不能冒称这些结果为我们的新发现。
定点检查 PCSP Mini-Inzoi v3 的风格奖励会基于 preferred_actions 和与 BigFive 构造的style_profile 明确奖励行动；ccb agent-sandbox 的 NPC 决策受动作合法性/反思/脚本兜底影响。均是源码事实，尚无本地复算。
**GPU/模型/实际游戏：0 新运行，0 新科学结果。** E06尚未开始。下一个行动是本地Agent读取一套入口并真正恢复自然NPC行为基线，先验证测量再做决定性实验。
