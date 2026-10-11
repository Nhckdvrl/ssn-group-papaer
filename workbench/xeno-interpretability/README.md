# Xeno-Interpretability — 模型原生表征与解释的边界

**状态：PROPOSED**（2026-10-12 创建；研究 workbench 已注册，但**不占 ACTIVE-MAIN / ACTIVE-EXPLORE**。是否升级由用户另行决定）
**主题：** LLM 内部计算、概念本体与人类解释之间是否存在结构性错配？  
**来源：** Pierucci et al., [Xeno-Interpretability: Investigating the Alien Minds of LLMs](https://arxiv.org/abs/2609.20408)（2026 arXiv；概念论文，非已验证现象）  
**目标会议：** 暂未选定（以之后的证据形态与官方征稿决定）  
**上次人审：** —（由用户后续在选线决策点确认）

## 一句话（探索目标，非已成立主张）
从成熟的 interpretability / representation 研究谱系中找**真实、重要、尚未解释透彻**的问题，不要求“零人研究”，也不做“找一个神秘的向量来证明外星语义”的自证题。通过强 baseline、可证伪的竞争解释、行为与因果实验，争取获得比现有解释更一般、更深刻的认识。

## 当前优先级
1. **先理解领域而非锁定论文题目。** 从综述 → NeurIPS 2026 / ICML 2026 / ICLR 2026 / ACL/EMNLP 2026 及以往主会优秀工作 → arXiv 新进展；审查近邻的 claim、技术尺度、证据强度。NeurIPS 2026 当前部分论文可见，仍需完整筛选。
2. **读懂「为什么能想到」而不是只学最终方法。** 对关键论文重建 parent、压力、改变的前提、最早能揭示问题的实验、相对最近邻的实质 delta；作者自述与我们的合理重建必须分开。
3. **先确定有研究压力的具体问题范围。** 它必须能用可承担的开源模型和强 baselines 反复测试，且至少存在两个需要实验区分的解释。
4. **获批准推进到实验阶段后**：复现强 baseline → 系统测量 → 从不一致 / 正负结果选择最具信息量的实验 → 更新竞争假设 → 进一步追加对照、因果干预及跨模型外推。
5. **每一步为自己留下知识资产。** 所有本方向的文献、读书卡、工具、压力与探索笔记放在 **本 workbench 的 `knowledge/` 内**，供后续研究 agent 连续复用，不再把本方向的专属知识库分散到公共 library。

## 工作区入口
- [knowledge/README.md](knowledge/README.md) — **项目内部知识库唯一入口**：证据级别、索引与阅读导航。
- [knowledge/LITERATURE_MAP.md](knowledge/LITERATURE_MAP.md) — 研究版图、竞争解释、核心不确定性。
- [knowledge/READING_QUEUE.md](knowledge/READING_QUEUE.md) — 已核查索引和待精读队列，按证据等级区分。
- [knowledge/papers/PIERUCCI_2026_XENO.md](knowledge/papers/PIERUCCI_2026_XENO.md) — 起点论文卡（记录阅读深度）。
- [knowledge/RESEARCH_CRAFT.md](knowledge/RESEARCH_CRAFT.md) — 如何从谱系读出 idea 并设计强实验。
- [knowledge/EXPERIMENT_DESIGN.md](knowledge/EXPERIMENT_DESIGN.md) — 准实验诊断、竞争假设及阳性/阴性对照（**非已批准运行计划**）。
- [CLAIMS.md](CLAIMS.md) — 主张账本：全部未验证。
- [PAIN_LOG.md](PAIN_LOG.md) — baseline 复现之后才填写真实痛点。
- `experiments/`、`ideas/`、`results/`、`logs/` — 与既有流程兼容。

## 当前认识的边界
- **未知:** 模型是否存在严格意义的、原则上不可翻译成人类概念的 xeno-representations。
- **重要但已有人做:** 语言解释与模型表征错配、SAE 一致性、因果解释、概念本体缺失；不能把 Xeno 新术语当作 0 近邻。
- **最可能的实际问题:** 人类概念标签能否准确预测模型真实的计算作用？不同解释方法的差异来自模型还是分析工具？何种实验可以鉴别。
- **禁止倒置因果:** 未建立自然行为现象/高质量测量前，不因 SAE、probe 或工具可用而硬造任务和叙事。

## 论文形态卡与 idea
尚无已确认的论文主旨或具体 idea；文献阅读与准实验设计不自动构成 I##，实验发现与因果主张必须在正式 E## 卡上形成证据后才升级。

## 决策记录
- 2026-10-12 · 用户明确要求新建独立 `xeno-interpretability` workbench，并在其**内部**建立、维护该领域知识库；本次登记为 **PROPOSED**。没有改变任何既有正式研究线或运行资源。

## 算力与资产位置
现阶段无新运行任务、无实验结果/权重。后续默认单节点可负担的公开模型和工具；环境、数据、checkpoint 位置待实测登记。
