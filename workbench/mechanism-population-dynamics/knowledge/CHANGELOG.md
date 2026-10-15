# 知识库维护日志

## 2026-10-15 — 首轮历史研究重评（已有）

- 首次在当前workbench内部建立 knowledge 目录，而非外围library。
- 建立 [研究重评](2026-10-15-reassessment.md)、[文献地图](2026-10-15-literature-map.md)、简要入口。
- 发现E81/v3对carriers和迁移度量存在源码—正文不一致；没有修改原实验或启动训练。

## 2026-10-15 — 本轮大规模知识整理

**结构化增补**：
- [领域问题地图](FIELD_GUIDE.md)，区分参数编号、统计角色、局部因果、协作关系与训练形成；
- [15篇一手论文卡](papers/)及[PAPER_CATALOG](PAPER_CATALOG.md)，逐篇保留领域背景、实验思路、idea来源证据/逆向重建、novelty边界与可迁移方法；
- [实验全景](heritage/EXPERIMENT_ATLAS.md)：把原77张历史实验卡按研究问题重排，链接回原始证据；
- [证据账本](heritage/EVIDENCE_LEDGER.md)：支持、有限支持、撤回、未完成分别归档；
- [测量审计](heritage/MEASUREMENT_AUDIT.md)：DLA与ablation、additive与joint、source-only与target-aided的合同；
- [失败手册](heritage/FAILURE_MODES.md)：来自P01/P03/P04/P05/P06/P08/P09/P10/P11/P12/P13等实证事故；
- [四版论文叙事演化](heritage/PAPER_VERSIONS.md)；
- [对称性](syntheses/SYMMETRY_ALIGNMENT.md)、[训练动力学](syntheses/TRAINING_DYNAMICS.md)、[因果等价](syntheses/CAUSAL_EQUIVALENCE.md)、[竞争解释地图](syntheses/CONFLICT_MAP.md)；
- [候选问题](research/OPEN_QUESTIONS.md)、[最小区分性实验](research/PILOT_DESIGNS.md)、[idea过程案例](research/IDEA_ORIGIN_CASES.md)、[本地Agent指南](AGENT_GUIDE.md)。

**纠错**：
- 旧文献地图误把MDA多头重配指向附录K；一手arXiv v2确认正确位置是附录F.2.2。Merullo附录K确实是Colored Objects问题来源，与MDA的K不可混淆。
- E81/v3的指标口径问题保留在知识审计中，不把尚未修复的代码结果“偷偷当成修复完毕”。
- 为旧论文、脚本、结果保留历史状态，并标明E87未完成、E88代码部分有问题、v3 raw NPZ缺失。

**没有做的事**：没有运行新实验、没有重训任何模型、没有修复旧论文/图表代码、没有确认所有Git结果数值可独立重算、没有把研究问题宣布为新论文idea、没有改变根项目的CLOSED状态。

## 持续维护标准

每次增加文献：版本、阅读深度、核心证据、重要反例和直接近邻；每次提出主张：明确估计对象、测试条件、竞争解释与新信息；每次讨论实验：优先保留原样结果与负例，避免重复全量复制。
