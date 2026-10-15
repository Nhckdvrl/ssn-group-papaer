# Mechanism Population Dynamics — 研究知识库

**状态**：知识库可供研究理解与阅读；所属workbench自2026-10-11起标记为 **CLOSED / TERMINATED**。此次只整理知识，不重启原始实验或论文写作。

**精简诊断**：过去的问题不是“研究过head所以都无意义”，而是从原编号role相关、跨run因果承担和完整算法一再跨越未检验的推断桥。知识库保存这些真实区别、现有文献最强认识、以及足以区分竞争解释的探索手段。

## 从哪里进入

| 你现在要做什么 | 首先读 |
|---|---|
| 初次理解领域和项目问题 | [FIELD_GUIDE：G0–G4研究对象](FIELD_GUIDE.md) |
| 了解当前项目最后为何觉得so what | [2026-10-15重评](2026-10-15-reassessment.md)、[四版论文演化](heritage/PAPER_VERSIONS.md) |
| 找到某个旧实验的目的、结果、代码入口 | [EXPERIMENT_ATLAS：完整实验导览](heritage/EXPERIMENT_ATLAS.md) |
| 防止把已经撤回的猜想当结论 | [EVIDENCE_LEDGER：可信证据和反证](heritage/EVIDENCE_LEDGER.md) |
| 核对DLA/ablation/source-target迁移口径 | [MEASUREMENT_AUDIT](heritage/MEASUREMENT_AUDIT.md) |
| 查看过去具体踩过的代码与数据坑 | [FAILURE_MODES](heritage/FAILURE_MODES.md) |
| 阅读论文时定位最强近邻 | [PAPER_CATALOG：15篇卡片及延伸目录](PAPER_CATALOG.md) |
| 寻找研究问题和竞争假设 | [CONFLICT_MAP：文献与实验矛盾](syntheses/CONFLICT_MAP.md)、[OPEN_QUESTIONS](research/OPEN_QUESTIONS.md) |
| 设计最低成本、能改变认识的实验 | [PILOT_DESIGNS](research/PILOT_DESIGNS.md) |
| 训练自己逆向作者怎样得到idea | [IDEA_ORIGIN_CASES](research/IDEA_ORIGIN_CASES.md) |
| 让本地Agent继续研究、避免局部优化 | [AGENT_GUIDE](AGENT_GUIDE.md) |

## 目录组织及真源边界

- **papers/**：逐篇理解卡，强调具体证据链、论文idea尺度、真正的related work距离。每张卡都说明读到的程度，不冒称已完成所有附录/代码复现。
- **syntheses/**：围绕科学问题整合多论文，不是按论文名复制摘要：[置换对称与对齐](syntheses/SYMMETRY_ALIGNMENT.md)、[训练动力学](syntheses/TRAINING_DYNAMICS.md)、[因果等价](syntheses/CAUSAL_EQUIVALENCE.md)、[冲突地图](syntheses/CONFLICT_MAP.md)。
- **heritage/**：实验遗产索引和批判审计。**原始事实仍在 workbench 根目录的 experiments/、results/、scripts/、CLAIMS.md、PAIN_LOG.md、logs/ 中**。
- **research/**：未授权执行的候选研究问题、最小探索设计、论文过程训练，不是已经完成的实验。
- **旧的2026-10-15文献地图**：[总览备忘录](2026-10-15-literature-map.md)，更多研究边界见新论文卡。
- **CHANGELOG**：[本次创建、纠错与未做事项](CHANGELOG.md)。

## 最值得记住的四个具体教训

1. **置换不等于没有科学问题**：同层head编号是约定，独立初始化应考虑对齐；但同祖先训练有自然历史配对。角色统计继承≠因果组件继承。
2. **不要把目标模型自己找到的电路叫source-only迁移**：E75使用target DLA做匹配，必须有同信息预算target-only基线。
3. **不要混用估计对象**：v3/E81的DLA top3、ablation top3与“单头求和vs联合消融”有真实定义不一致，详见度量审计。
4. **现有论文已很接近**：Merullo已做IOI/Colored Objects复用并指出大模型top-k不重合不代表功能不同；MDA附录F.2.2已有多头重配；Méloux、All Circuits和Many Circuits揭示离散图非唯一与信度问题。因此后续价值在解释真实分工关系并预测新干预，而不是重复绘图。

## 状态与下次维护

既有不准确的统计、未完成的 E87/E88，以及 Git 未跟踪的原始 NPZ，不会在这里被悄悄升级为成果。见[历史结项](../CLOSEOUT.md)、[资产索引](../ASSET_INDEX.md)。

这份知识库是可审计的结构化基础，**不是所有已收录论文都达到同等深度或全部旧结果都独立复核**。需要持续完善的部分是对关键文献开源代码的细读、已有结果的程序验证及真正的留出因果实验（若之后得到授权）。

更新时间：2026-10-15。
