# Xeno 初步实验入口 · 给本地研究 agent（未运行）

**选择的空间（不是预定结论）**：**“概念先验是否扭曲我们对模型内部计算组织的发现？”** 重点研究 semantic accessibility 与结构/因果有效性之间的关系，不转向多智能体通信、单纯 SAE 提点、steering benchmark 或华丽的无标签聚类。

## 0. 入场时必须带着的科学问题
- 原论文提出的 *Fermi paradox of distributional semantics*：为何解释研究反复发现人类熟悉的类别？
- **Q1**：human-concept-seeded、activation-first、effect/causal-first 三种发现渠道在同一模型和同一自然数据分布下，实际上揭示了哪些计算对象？相同强度/复杂度下，是否有系统差异？
- **Q2**：当单个对象难以命名时，是解释太弱、仪器造假、纯上下文操作，还是确实有**模型原生关系**可预测未见过的干预？
- 终点优先是**新的认识、解释机制或边界条件**，不是“自动命名率低”或“发现了一个古怪维度”。

## 1. 优先复现的仪器（可根据研究发现主动调整）
- [FEGA / Gemma-2-2B + SAEBench SAEs](https://github.com/UKPLab/FEGA)：先重建 reconstruction-relative ablation、paired logit change、matched activation-prevalence random controls 和自然 context 分布；**不可**将 `original vs SAE-ablated` 直接相减混入 SAE 重建误差。
- [MIB](https://github.com/aaronmueller/MIB) 与 [Causal Differentiating Concepts](https://proceedings.neurips.cc/paper_files/paper/2025/hash/5faf0f518f39e4d6b2b595e3ca2fe0c4-Abstract-Conference.html)：分别提供有因果标的的阳性对照和较少人工概念先验的发现入口。严格检查论文真实的“无监督”所依赖的**行为分组/稀疏改变假设**。
- [Ma et al. NeurIPS25](https://papers.neurips.cc/paper_files/paper/2025/hash/5b6ce2529a79862a2d8ac57ac0e01d90-Abstract-Conference.html)、[Gur-Arieh ACL25](https://aclanthology.org/2025.acl-long.288/) 的 hard negatives / output-centric 描述，作为**强语义解释**对照；不能只和一词标签比。
- [Aristotelian calibrated similarity](https://github.com/mlbio-epfl/Aristotelian)：若跨模型/跨层比较，校正维数、max-layer-selection 假阳性，随机网络及同数据统计控制。
- 算力：从可单卡复现的开源基线起步，必要时用其它独立卡并行 context / model / seed；不可假定跨节点高速互联或 GPU 空闲。

## 2. 第一批**高信息量**测量（研究动作，不是机械清单）
**A · Baseline sanity + 自然条件下的异象地图**：在现成模型与若干自然语言输入类型（事实、语境依赖的指代/关系、一般文字变换等；开放式 corpus 与严格正对照均要有）测同一批内部对象的：重现性、输入触发、**重构误差匹配的干预效果**、下游输出分布变化、上下文相关性。以统一的探索集选对象，留出**未触碰的反证集**。匹配激活频次/幅度/效应强度，不“只报漂亮 feature”。

**B · 三种发现/解释方式相撞**：控制信息预算和参数复杂度，比较 (i) 人类概念先验定位与复合/程序语义解释，(ii) 不先贴标签的 activation/geometry 发现，(iii) 不贴标签、从**行为差异或因果效果**出发的候选结构。检验解释对 **held-out 干预结果**的预测——不仅是 activation simulation、分类 probe、SAE reconstruction、CKA 或某个 LLM 给标签的评分。记录语义覆盖与**真正的功能解释价值**的二维关系，而不是一个混合“解释好坏”总分。

**C · 主动选最大分歧的自然输入来判别机制**：依据 [Golan et al. 2026](https://www.nature.com/articles/s41583-026-01070-0) 的 controversial stimuli / optimal experiment design，从未使用的数据池挑**概念模型预测**与**关系/条件操作模型预测**有明显分歧的输入，在**先固定预测及分析方案后**执行介入并比较结果。同时留出随机抽样自然输入作外推控制。

## 3. 准实验的读数、竞争假设、出结果后该怎么办

| 分歧结果 | 我们应该学到什么，而不是硬保 idea |
|---|---|
| 强概念/组合解释追上匿名关系预测 | 过去的“不可表达”来自解释器能力，而非证据支持 Xeno；查清最重要的表达能力/样本复杂度 |
| 关系描述比概念解释更预测未见过的 causal outcomes，且可跨条件重复 | 可以提出**指定解释类下的语义充分性缺口**，但还要排除容量差、预训练语料统计、等价描述及其它普通机制；绝不立刻宣称人类无法理解 |
| 两边都好，但不同上下文交替胜出 | 找 conditioning variable 与有效范围；可能发现更有意义的组合规律 |
| SAE feature 不复现/随机模型同样显著/真干预无效 | 下降为**分析器和测量问题**，不归因于潜在神秘概念；更换有根据的分析单位和对照 |
| 两种解释对不同测试没有显著分歧 | 此次实验信息增益不足；寻找更具判别力的真实问题或新近邻，不靠追加大样本和漂亮图硬耗资源 |

**核心统计**：paired held-out intervention-effect predictivity（向量夹角/幅度、top-logit rank、指定 task outcome）、reliability across contexts/seed、随机 & 错任务 controls、CI、noise floor、预先选定的最小科学上有意义效应；多重搜索记录并在独立评测集校对。只有看到第一轮真实读数后才确定最有价值的 effect metric 与解释抽象粒度。

## 4. Agent 必须保持主动科学判断
入场先重新读此 workbench 内 [知识库](knowledge/README.md)、原论文和最新顶会，并继续 web search 近邻，特别是 FEGA / PolySAE / Aristotelian / 2026 NeurIPS；**不准机械把 A→B→C 当成命令流水线**。如果发现更自然的对象、更强的实验、明显混杂或者本预案已经被发表工作覆盖，可以立即提出并改写实验设计；实验前依 [workbench EXECUTION](../EXECUTION.md) 填实验卡与分支预测。每轮反过来问：哪项观察改变了我们对“模型如何组织意义”的理解？为什么值得兴奋？重要负结果同样保留。不能用目前的任何猜想自动判死 xeno territory。
