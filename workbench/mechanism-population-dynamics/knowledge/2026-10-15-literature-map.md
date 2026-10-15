# 文献地图：角色、因果分工、跨模型对应与训练形成

更新：2026-10-15。与[研究重评](2026-10-15-reassessment.md)配套。

本页不是按关键词堆砌 bibliography。每项记录研究问题、实际证据范围、对本 workbench 的限制以及可迁移的研究方法。读到的正文/附录不等于审计了作者全部代码或重证数学定理。没有直接过程材料时，关于 idea 来源的说明只是根据文献关系作的研究重建。

## 0. 全局画像

这个领域至少有四个不同的对象：

- **表征/注意力相似性**：输出或注意力图是否可匹配；不直接回答因果作用。
- **任务因果承担**：改变哪些部件会改变某个任务的输出；依赖输入条件与干预定义。
- **关系和组织**：哪些计算被同一部件复用，哪些部件通过什么路径协作。
- **形成过程**：这些分工如何由数据、初始化和早期学习共同形成。

共识不是“所有头都相同”或“所有头都随机”，而是不同粒度可能有不同程度的可复现性。应避免从局部相似度直接推断完整算法，也避免从一个离散 circuit 图不一致直接推断算法不同。

本次最值得继续查的解释空白：**跨训练的功能对应在何种因果粒度上成立；若单个任务的功能都能找到，为什么它们的共用与协作关系仍可能不同？**

## A. 对应与普适性：已有工作实际做到哪里

### A1. Tigges et al. — LLM Circuit Analyses Are Consistent Across Training and Scale

- 一手来源：[NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/47c7edadfee365b394b2a3bd416048da-Abstract-Conference.html)，[论文 PDF](https://proceedings.neurips.cc/paper_files/paper/2024/file/47c7edadfee365b394b2a3bd416048da-Paper-Conference.pdf)。核读：核心实验、训练/尺度比较及图示。
- 问题与证据：对公开训练检查点和不同规模的模型做电路分析，区分较稳定的高层计算与会变化的具体部件。
- 与本项目距离：“算法相近、头会换”已有直接前例。但是不能把这篇的跨时间/尺度结果说成已经完成固定架构下的初始化 × 语料因子分解。
- 可学的尺度：把同一个解释沿明确变化轴反复检验，而不是只在一个模型上展示电路。

### A2. Bali et al. — Quantifying LLM Attention-Head Stability: Implications for Circuit Universality

- 一手来源：[arXiv:2602.16740](https://arxiv.org/html/2602.16740v1)。核读：方法、优化器比较与功能重要性分析。本文以预印本标记，不沿用旧卡片中未经本次核实的会议信息。
- 方法事实：按注意力矩阵余弦相似度为来源头寻找最佳目标头，研究多次重训；并考察消融后的功能重要性和 Adam/AdamW 差异。
- 关键边界：最佳匹配不是全局一一对应；注意力匹配也不等于任务因果角色对应。另一方面，不能误述为它完全没有功能/消融实验。
- 对我们：重复“中层头不稳定”或“考虑对齐”没有足够新意。更具体的关系结构及预测性干预才可能形成增量。

### A3. Trott — Toward a Theory of Generalizability in LLM Mechanistic Interpretability Research

- 一手来源：[arXiv:2509.22831](https://arxiv.org/html/2509.22831)。核读：五个对应轴及 1-back head 的跨 seed/训练分析。
- 内容：区分 functional、developmental、positional、relational、configurational 五种普遍化；实证集中于 previous-token/1-back 注意力的发展与位置。
- 对我们：**关系普适性不是本次新发明的概念。** 可做的是把它落实为具体、可区分的因果预测，而不是再次提出术语分类。
- 思维迁移：先确定“哪一种相同”，再选择统计量，避免用一张相关图同时回答五个问题。

### A4. Merullo, Eickhoff & Pavlick — Circuit Component Reuse Across Tasks in Transformer Language Models

- 一手来源：[全文](https://arxiv.org/html/2310.08744)，[作者发表页](https://jmerullo.github.io/publications/circuit_reuse/)。ICLR 2024。核读：正文、路径干预、附录 I/J/K。
- 正文：研究 IOI 与 Colored Objects 的部件复用；干预不仅改变任务结果，还按 IOI 解释预测的方式改变下游 mover heads。
- **重要附录边界**：GPT-2 Large 的两任务 top-10 有五个重合，XL 没有，但部分功能仍重合。作者已知道重要头重合率与功能复用不是一回事。
- **真实过程材料**：附录 K 解释，Colored Objects 来自之前正在研究的任务，研究者察觉它与 IOI 都涉及从候选中选择并复制，再开展电路比较。不能把最终章节顺序假装成发现顺序。
- 可学的核心不是百分比，而是：由一个已理解机制推导另一个任务中的具体干预后果。

### A5. Shao et al. — Differentiable Faithfulness Alignment for Cross-Model Circuit Transfer (DFA)

- 一手来源：[arXiv:2604.24302](https://arxiv.org/html/2604.24302)。核读：目标函数、数据划分、留一任务测试、消融与跨规模附录。
- 方法事实：学习把源模型节点重要性映射到目标模型的矩阵，用目标 faithfulness 训练；已包含留一任务设置，不能说只在一个任务内拟合。
- 控制事实：包括随机矩阵、推理时打乱来源分数、置换已训练矩阵的列、深度启发式。
- 我们的评析：训练时使用目标信息本身并不无效。要衡量来源电路的额外价值，需要信息预算匹配的 target-only / source-free 训练对照；推理时破坏正常输入并不等价于这个对照。这是待检验问题，不是已发现 DFA 失效。
- 距离：仅做“跨任务对齐”已经不新。必须进一步预测具体因果关系、协作路径或修复后果，而非只恢复稀疏电路的总行为。

## B. 为什么电路/排名差异不能直接解释为算法差异

### B1. Méloux, Portet & Peyrard — Mechanistic Interpretability as Statistical Estimation: A Variance Analysis

- 一手来源：[全文 v4](https://arxiv.org/html/2510.00845)，[ICML 2026](https://proceedings.mlr.press/v306/meloux26a.html)。核读：CMA/EAP 分解、重采样和反事实敏感性。
- 证据范围：因果分数随输入而异，快速近似和后续离散选择可能进一步放大不稳定性。
- 对我们：E81 中大量近零头的排名信度低，属于应认真处理的测量问题。不能把信度修正当成自动得到真机制，也不能将真实的输入条件依赖全部归为噪声。
- 可迁移方法：把估计对象和统计处理分开；考察条件化效应、连续分数及未参与选择的验证证据。

### B2. Chen et al. — All Circuits Lead to Rome: Rethinking Functional Anisotropy in Circuit and Sheaf Discovery for LLMs

- 一手来源：[全文](https://arxiv.org/html/2605.12671)，[ICML 2026](https://proceedings.mlr.press/v306/chen26bb.html)。核读：多电路发现方法及理论/实验主张的范围。
- 内容：同一任务可以存在多个低重合却有行为忠实性的稀疏电路，挑战从一个抽取图推断唯一实现。
- 边界：主要关心同模型内的电路非唯一性；不能用它直接断言独立训练中的所有关系都不普适。
- 对我们：图重合度不是完整机制等价性的判据。新问题应问所提出的解释能否预测独立的干预后果。

### B3. Bayat Makou et al. — Many Circuits, One Mechanism: Input Variation and Evaluation Granularity in Circuit Discovery

- 一手来源：[arXiv:2606.06267v1](https://arxiv.org/html/2606.06267v1)。核读：多输入组电路、评价粒度及 interchange 分析。会议状态未在本次可靠核实，标为预印本。
- 内容：输入组改变时，抽取的具体电路可不同；更粗粒度的共同结构能保留大量行为。
- 我们的评析：较晚/最终残差的 interchange 成功，本身不等于已经证明所有上游因果过程相同。高层行为可操纵性与内部算法同一性需要分开。
- 对我们：不要把“换个粒度相似”直接当新机制解释；必须说明哪些因果预测因此变得更准确。

## C. 数据和训练如何形成部件

### C1. Chen, Luo & Pan — Mechanistic Data Attribution: Tracing the Training Origins of Interpretable LLM Units

- 一手来源：[arXiv v2 全文与附录 F.2.2](https://arxiv.org/html/2601.21996)，[作者新闻](https://liangmingpan.bio/news/)。作者材料确认 ICML 2026 Oral；本次已按公开 arXiv v2 核对附录 F.2.2；尚未逐函数审计作者代码。
- 内容：用训练数据 influence 追踪可解释单元；删减/增加相关样本改变形成过程，结构性重复数据尤其重要。
- **近邻边界**：附录 F.2.2 已观察 160M 模型中一些 induction heads 变弱或失去特征、另一些增强；“换承担头”不是新的空白现象。
- 方法来源的重建：把训练数据归因用于具体机制，再用重新训练检验；不只是给数据贴类别标签。
- 对我们：单头追踪应与角色群体、行为及原样重跑一起读。若想做训练机制，应区分改变计算本身和改变承担者，不能仅报告 argmax 更换。

### C2. Singh et al. — What needs to go right for an induction head? A mechanistic study of in-context learning circuits and their formation

- 一手来源：[全文](https://arxiv.org/html/2404.07129)，[ICML 2024](https://proceedings.mlr.press/v235/singh24c.html)。核读：形成过程及训练期钳制/子电路干预。
- 内容：用训练过程中的干预拆分 induction 形成所需的子计算，而不只画相关曲线。
- 对我们：“多个部件协作形成 induction”已有机制性研究。更好的借鉴是干预具体中介，把“同时出现”转成可区分的形成路径。
- 可迁移方法：只恢复或阻断某一子计算，观察后续发展，而不是同时改变一大片数据和全部网络后用叙述解释。

### C3. Dong, Noci, Khodak & Li — Is Random Attention Sufficient for Sequence Modeling? Disentangling Trainable Components in the Transformer

- 一手来源：[arXiv:2506.01115](https://arxiv.org/html/2506.01115)。旧题名包括 Attention Retrieves, MLP Memorizes。核读：Frozen-QK/MixiT 区分及相关实验；不声称重证理论附录。
- 关键事实：固定 Q/K 参数仍可形成 induction 模式，因为输入表示仍能学习。固定 Q/K 与固定、输入无关的注意力矩阵不是同一个实验。
- 对我们：某头表现出角色，不表示该角色只由它自己的权重形成；但“上下游参与”也已经不是新结论。
- 可迁移方法：把参数块和其输入表示分开干预，以反事实定位角色倾向由何处承载。

### C4. Sagitova, Duranthon & Zdeborová — Specialization of softmax attention heads: insights from the high-dimensional single-location model

- 一手来源：[arXiv:2603.03993](https://arxiv.org/html/2603.03993)。核读：设定、专业化阶段和解释范围；未重证全部推导。
- 内容：在可分析的高维模型中研究头如何沿数据结构逐步专业化及受到初始条件影响。
- 边界：这不是自然语料多层 LLM 的因果分工实证；也不能由它自动解释我们的特定头。
- 对我们：研究概率性的专业化有正当科学价值，但“发生对称性破缺”这个标签本身不是解释。需要找到数据结构、交互和发展轨迹的可检验联系。

### C5. Aoyama, Wilcox & Schneider — Predicting the Emergence of Induction Heads in Language Model Pretraining

- 一手来源：[ICML 2026](https://proceedings.mlr.press/v306/aoyama26a.html)，[arXiv:2511.16893](https://arxiv.org/abs/2511.16893)。本次深度：官方摘要和问题范围筛选，非全文精读。
- 内容范围：把 batch/context、重复统计等与 induction 形成联系，给出形成预测。
- 对我们：不能把“重复数据影响 induction 出现时间”当新发现。下一轮需要深入对照它的边界条件，才能宣称某种新发展规律。

### C6. Silverstein, Kunin & Shyam — Symmetry Breaking in Transformers for Efficient and Interpretable Training

- 一手来源：[arXiv:2601.22257](https://arxiv.org/html/2601.22257)。核读：研究的对称群及优化器关系。
- 必须澄清：主要讨论的旋转/参数化对称性，不等于离散的头置换，也不自动证明“头之间的竞争决定职责”。
- 对我们：E41 引用涉及 symmetry breaking 的文章时，需要对准具体对象；不能因为标题相似就拿来支撑未实测的集体形成解释。

## D. 继续训练与部件沿袭

### D1. Prakash et al. — Fine-Tuning Enhances Existing Mechanisms: A Case Study on Entity Tracking

- 一手来源：[全文](https://arxiv.org/html/2402.14811)，[ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/hash/2082273791021571c410f41d565d0b45-Abstract-Conference.html)。核读：机制复用主张、定位与跨模型干预方法。
- 内容：在实体追踪案例中，微调增强已有机制，而非必然建立完全不同的实现。
- 对我们：E81 后代中的部件延续有强相关前例。不同任务、模型谱系或变化尺度下的边界仍可研究，但不能从少量 lineage 推出所有 SFT/DPO 都保存电路。

### D2. Wang et al. — Towards Understanding Fine-Tuning Mechanisms of LLMs via Circuit Analysis

- 一手来源：[arXiv:2502.11812](https://arxiv.org/html/2502.11812)。核读：任务设定、节点/边变化和与早期微调工作的比较。
- 内容：已有节点的重用与连接重要性的变化可以同时出现；并讨论基座原有任务能力与更难任务的差异。
- 对我们：不能把“简单任务强化已有部件、难任务改写连接”重新当成尚无人提出的解释。还要区分真实信息路径变化与离散抽图方式引起的边变化。

## E. 数据资产与最新论文筛选，不冒充精读

### E1. PolyPythias — Stability and Outliers across Fifty Language Models

- 一手来源：[ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/d611d06e3207330555fbc10810e70163-Abstract-Conference.html)。深度：官方摘要与资产范围。
- 用途：跨 seed 和训练检查点比较的候选资产。具体 checkpoint 关系必须使用本 workbench 的权重审计，不只信标签。

### E2. Can Circuit Alignment Predict OOD Generalization?

- 一手入口：[arXiv:2609.31996](https://arxiv.org/abs/2609.31996)，[作者项目页](https://ayanban011.github.io/cas.html)。深度：检索到的一手摘要/项目简介；本次未成功取得可核读全文或 PDF。
- 检索范围：2026-09 新近工作，把电路对应与 OOD 预测联系。不能依据摘要断言其理论无条件成立，也不能把它的视觉模型结果直接套到 LLM。
- 对我们：有用的 taste 参照是“相似度能带来新的预测”；不把它当本次候选问题已解决或未解决的决定证据。

### E3. NeurIPS 2026 检索记录的边界

检索了当届列表和相关论文入口。列表中出现题目或第三方声称录用，不等于已经获得论文全文。未核实的题目不被用作“相关工作已经封死”或“这是全新空白”的依据。核心判断优先依赖上面取得的一手全文及已审计实验。

## F. 矛盾地图与具体机会

| 看似冲突的观察 | 不能直接做出的结论 | 值得做的区分 |
|---|---|---|
| E72 角色对齐高，E75 IOI 原编号或通用映射差 | 前者假，或算法一定不同 | 通用统计轴、任务主要承担和协作路径是不同对象 |
| Merullo 正文有复用，附录 J 的 GPT-2 XL 重要头不重合 | 复用消失 | 头仍执行相同操作但份额不同，还是任务确实使用不同路径？ |
| E81 DLA 排名信度低，主力头数值贡献稳定 | 测量全部无效 | 近零单位排名与主要因果效应分开 |
| 数据干预后 head 变弱，另一个变强 | 数据不影响机制，或算法被替代 | 形成速度、总能力与承担者分配分别测量 |
| 不同 faithful circuits 重合低 | 真实模型有任意互不相干算法 | 用未参与抽取的具体中介/干预预测检验解释 |

## G. 阅读资产如何继续维护

关键论文必须保留：确切实验设定、该结果排除的解释、仍可成立的解释、与当前主张的距离。准备声称新颖性时，应优先重读对应近邻的附录和控制，而不是再搜大量同名关键词。

特别优先的原文段落：Merullo 附录 J/K；MDA 附录 F.2.2；DFA §4.1/4.3；Bali §3.2 与功能重要性分析；Tigges 的算法/部件定义。它们直接决定下一轮实验是否只是在重做已有内容。
