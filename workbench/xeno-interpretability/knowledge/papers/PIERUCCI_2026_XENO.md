# Pierucci et al. (2026) — Xeno-Interpretability: Investigating the Alien Minds of LLMs

[arXiv:2609.20408](https://arxiv.org/abs/2609.20408) · **概念论文；核查：用户提供首页/摘要 + 可得引文线索；正文未完整重新核对**。

**问题**：解释者先以 truthfulness、refusal 等已有人类概念寻找模型内部结构，是否可能错过模型本身使用的别的区分？

**改变的前提**：将“可实验识别”（复现、几何、介入、预测行为）与“可找到人类语义名称”分开。这是**研究动机**，不是 Xeno-representation 存在的实验证据。

**原文能够支持的**：提出 `human-interpretable H` 与 `xeno X` 的概念区分、设想无标签先识别结构再尝试命名，以及 agent 之间可能的 xeno 传播。摘要提及的可能区分空间大，仅是宽泛的理论可能性，不证明有限模型真实训练出了人类无法概念化的变量。

**RECONSTRUCTED idea 来源**：固定 human label 可能限制 observation → 开放特征寻找并接受未知解释 → 再以几何和因果测试“有功能但不好翻译”。并无证据表明作者确实沿此个人思路完成论文。

**致命未解**：`我们现在解释不了` 与 `原则上无法以任何人类概念解释` 之间没有可实验的边界；可控制的任意向量可能是 off-manifold 干预；若用它同样“不能描述”来证明概念的存在，逻辑循环。

**最近邻现在已确认并非空白**：
- [Concept Frustration 2026](CORE_READS.md#6-parisini-等-2026-预印本) 已有本体漏项几何与任务实验；
- [Ma NeurIPS 2025](CORE_READS.md#3-ma-等-neurips-2025) 已设计强反例改进概念描述；
- [Ma ICML 2026](CORE_READS.md#4-ma-等-icml-2026) 把高层语义错认归因于低维混杂；
- [Torop NeurIPS 2026](CORE_READS.md#5-torop-等-neurips-2026) 已发现检测方向和控制效果可系统反号；
- [Song ACL 2026](CORE_READS.md#7-song-等-acl-2026) 针对可重复的解释对象提出一致性衡量。

**当前用法**：保留 Xeno 作为**选问题的提醒**，不将“找到一个陌生 feature”作为先验论文目标；先阅读 [领域地图](../LITERATURE_MAP.md) 的可检验 competing explanations。尚无作者之外的独立复现。
