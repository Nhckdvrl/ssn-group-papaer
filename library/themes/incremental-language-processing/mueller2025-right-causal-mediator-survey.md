# The Quest for the Right Mediator: Surveying Mechanistic Interpretability Through the Lens of Causal Mediation Analysis

`[证据级别：主文§1–8及附录A–D]`，2025 CL作者接收稿/arXiv2408.01416v3；最终MIT排版稿、review/score未核对。[原文](https://arxiv.org/abs/2408.01416)。PDF与主文135483字符外置reassessment-2026-10-07缓存，SHA见ledger。

1. **形态：** 因果单位与目标匹配的综述/领域框架。
2. **背景与压力：** 方法繁多、评估ad hoc，研究常未说明“机制”中的节点是什么，因而不能公平比较进展。
3. **改变的前提：** 不先按方法归类，而先按中介类型与解释/验证假说/编辑三个科学目标归类。
4. **idea来源：** RECONSTRUCTED——从“怎样测到一个有效组件”转到“它对当前目标能解释什么”。不是作者实际发现顺序的声明。
5. **近邻距离：** Belinkov/Glass与Belinkov的probe综述；Ferrando/Rai方法指南；Bereska/Gavves领域图；MIB/AxBench评估。共同工具之外的增量是中介粒度与目标的显式对应。
6. **方法/数据/基线：** 层/子模块、neurons/heads、非基方向/子空间、非线性中介；穷举、probe/DAS、SAE/聚类；对比faithfulness、sparsity、generality、selectivity、counterfactual faithfulness/IIA。附录区分输入依赖、类依赖及输入/类独立干预；成本表不包含训练时间。没有新的统一效果实验或新数据集，引用工作不是本综述复现实验。
7. **证据边界：** 优缺点多为领域归纳，不是每个模型/任务都成立的定理。全层替换是因果瓶颈，容易产生有效而不选择性的解释；input-dependent patch只找到对指定对比敏感的组件。优化出的方向可能不忠实；非线性/冗余/Hydra效应使单组件null不具完整排除力。
8. **可迁移动作：** 分开“控制输出”“高层变量反事实正确”“解释模型自然行为”；先设计可被反驳的关系对象，再选择中介。模型泛化和保持未干预概念，需要独立测量而非自动由稀疏/忠实推出。
9. **对我们：** 作者已把语法处理区域是否用于QA作为跨任务范例；I03的跨用途criterion不单独认证novelty。E55粗源residual替换是机制入口，之后要靠具体新预测与自然关系后果建立增量，不因正效应就称parse、不因null就称从未构建。
