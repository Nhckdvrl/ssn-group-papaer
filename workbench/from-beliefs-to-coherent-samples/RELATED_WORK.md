# Related Work｜Generative In-Context Learning: From Beliefs to Coherent Samples

更新：2026-10-27。配套：[研究方案](./RESEARCH_PLAN.md) · [本地 Agent Handoff](./AGENT_HANDOFF.md)

## 0. 阅读这份文献图谱的方式

我们的目标不是寻找一篇“已经做过相近关键词”的论文来否定方向，而是看清四条研究线如何连接、已经解释到哪一步、还有什么重要问题值得系统研究：

1. **Bayesian / generative ICL**：有限示例确定的是后验预测分布，而非唯一任务/点预测。
2. **Mechanistic ICL（尤其 Hakaze Cho）**：示例信息如何进入 Transformer、形成任务相关表示、经历选择与信息消除。
3. **联合生成与随机过程**：同一 Episode 中多个 Query / 一张结构化图像须共享潜在任务，联合分布不能由边缘分布直接替代。
4. **Diffusion dynamics / uncertainty**：Score、Denoiser Jacobian、协同耦合与采样时间如何影响模式实现。

**核心研究缺口**：预训练生成式 Transformer 怎样从示例推断概率性任务知识，在内部保留联合预测所需的信息，并通过扩散把它实现为分布校准、跨位置/跨 Query 一致的样本？论文目标是研究完整的 Inference → Representation → Realization，而不是单独宣称新的 Head、通用压缩或一个新恒等式。

下述“差异/切入点”是我们的研究定位，不等于宣称相应论文完全未触及该问题；正式写作需仔细核对原文实验、假设与版本。

## 1. 最直接的两大源头（优先精读）

### [R1] Fu et al., Diffusion Transformers are Provably Optimal In-context Generators (2026, arXiv:2610.05333)
- 原文：https://arxiv.org/abs/2610.05333
- 研究贡献：把有限示例条件生成的理想目标形式化为 **posterior predictive distribution**；证明特殊 DiT 构造能通过上下文 Score Learning 学到该目标，在规定 Hölder 任务族上达到提示长度的最优速率。
- 我们应继承：上下文后验和模型训练/采样误差的区别；混合 Score 的正确计算；允许多峰不确定性而不牺牲单样本可用性；解析 Bayes Oracle + 分布级评测。
- 原文 Appendix J 的真实模型/实验（不要与理论 4-block 构造混为一谈）：每个 Context Pair 编码为 **4 个空间 Token**，Query 为 **256 个 Patch Token**；12 个 DiT blocks，Query Self-Attention + Context Cross-Attention + MLP，约 80.27M 参数；以 x0-prediction 训练，200 步确定性 DDIM 评估。Context 对应二元潜在方向，主要检测**单个 Query**的模式权重与图像质量。
- 我们的延伸：从单 Query posterior predictive 扩展到**共享潜在任务的多个 Query / 一个全局结构化输出**；研究联合分布、跨 Query 协同、内部信息路径与干预，而非仅重做单点生成。
- 阅读优先章节：§2–3、Appendix J.1.1–J.1.2；特别避免把构造性近似网络当成真实训练网络的证据。

### [R2] Cho et al., Mechanism of Task-oriented Information Removal in In-context Learning (ICLR 2026)
- 原文：https://arxiv.org/abs/2509.21012
- 贡献：把 ICL 解释为对非选择性 Hidden Representation 进行任务导向的信息消除，讨论低秩过滤、Denoising Heads 与因果消融。
- 我们应继承：Task-relevant / nuisance information 的区分、跨层表示与受控因果干预。
- 重要口径：Eccentricity 和 Covariance Flux 是在**样本集合的表示协方差**上定义的指标，不能直接把单条上下文向量半径解释成 Shannon 后验熵。
- 我们的延伸：信息消除要同时接受**单 Query 与联合 Query 的预测充分性**检验。对一个 Query 可删除的任务信息，对共享任务的多 Query 生成可能是必要的。关注这种取舍的功能后果，而非预设一定存在某个特定 Head。

## 2. Hakaze Cho 研究脉络（机制方法工具箱）

### [C1] Cho et al., Revisiting In-context Learning Inference Circuit in Large Language Models (ICLR 2025)
- https://proceedings.iclr.cc/paper_files/paper/2025/hash/22d4f952efa13970f0b1ffb22170d416-Abstract-Conference.html
- Input Text Encode → Semantics Merge → Feature Retrieval / Copy 的 ICL 推断电路；有干预与旁路机制讨论。
- 对我们：设计 Context Evidence Aggregation、Feature Retrieval 的可证伪机制实验；不直接认定同一电路会在 DiT 中复现。

### [C2] Yang, Cho et al., Unifying Attention Heads and Task Vectors via Hidden State Geometry in In-Context Learning (NeurIPS 2025)
- https://papers.neurips.cc/paper_files/paper/2025/hash/1f3e9dddea1df5b3049192172f2e163f-Abstract-Conference.html
- 分类式 ICL 中分离 query representation 的 separability 与 alignment，研究各层动态以及与 Heads / Task Vectors 的关系。
- 对我们：可以测不同层中信念/联合预测能力的可解码性与几何，但是 Probe 关联不等于模型因果使用。

### [C3] Yang, Cho, Inoue, Localizing Task Recognition and Task Learning in In-Context Learning via Attention Head Analysis (ICLR 2026)
- https://proceedings.iclr.cc/paper_files/paper/2026/hash/974726d56a6ddfac48486e57d5e798e4-Abstract-Conference.html
- TR/TL 分解、Task Subspace Logit Attribution（TSLA）、任务子空间的几何对齐/旋转与 Head-level 干预。
- 对我们：从“识别规则、利用规则”走向“保留规则的不确定性、实现联合分布”；TR/TL 类比可研究，但不能先验宣称 DiT 存在同名的两个电路。

### [C4] Yang, Cho et al., Task Vectors, Learned Not Extracted: Performance Gains and Mechanistic Insights (ICLR 2026)
- https://proceedings.iclr.cc/paper_files/paper/2026/hash/79ada0f9bc4e41192ad5a80d13c8ca7e-Abstract-Conference.html
- 学习式 Task Vectors 与 OV Circuits、跨层旋转/缩放机制。
- 对我们：Task Vector 是候选表示解释之一；不预设“信念必须在弯曲流形或凸包内以线性方式编码”。

## 3. Bayesian ICL、Belief Representation 与统计理论

### [B1] Wakayama & Suzuki, In-Context Learning Is Provably Bayesian Inference: A Generalization Theory for Meta-Learning (ICML 2026)
- https://proceedings.mlr.press/v306/wakayama26b.html
- 分解 Bayes Gap 和 Posterior Variance，提出有限预训练下的 ICL 贝叶斯泛化理论。
- 对我们：连接统计误差与模型行为；不可把经典风险分解当成未经验证的新定理。

### [B2] Kang, Lee & Cheng, Transformers Can Learn Posterior Predictive Distributions In-Context (ICML 2026)
- https://proceedings.mlr.press/v306/kang26h.html
- GP 回归中 Transformer 构造性近似后验预测均值、方差与分箱概率。
- 对我们：分布预测与 Transformer 连接已有基础；我们的特殊对象是**多模态、联合、共享任务的扩散生成及其机制**。

### [B3] Balcells et al., Large Language Models Develop Belief State Geometry In-Context (2026)
- https://arxiv.org/abs/2609.17376
- HMM 情形下 LLM Hidden States 可解码 posterior belief，并作表示干预。
- 对我们：不能只做 Belief Linear Probe 就宣称创新；要对 Score / 联合生成给出因果功能检验。

### [B4] Bigelow et al., Belief Dynamics Reveal the Dual Nature of In-Context Learning and Activation Steering (ICML 2026)
- https://proceedings.mlr.press/v306/bigelow26a.html
- 将上下文证据累积与 Activation Steering 置于贝叶斯 Belief Dynamics 框架。
- 对我们：研究信念更新与干预，区别于直接只分析内部信念几何。

### [B5] Wang et al., How Few-Shot Examples Add Up: A Causal Decomposition of Function Vectors in In-Context Learning (ICML 2026)
- https://proceedings.mlr.press/v306/wang26hp.html
- Function Vector 的示例加性、上下文重加权及 QK / Value 因果作用。
- 对我们：注意 Context Token Attention 的证据聚合与潜在任务后验不是同一个空间；不要把 Token Attention Map 直接解释成任务权重。

### [B6] Tikhonov et al., One Task Vector is not Enough: A Large-Scale Study for In-Context Learning (ACL SRW 2026)
- https://aclanthology.org/2026.acl-srw.127/
- 复杂任务可能依赖多个子任务向量。
- 对我们：多个子任务向量的组合 ≠ 对互斥潜在任务的概率混合；比较两种机制即可，不必回避。

## 4. 联合函数分布与视觉生成（必须认真对照的强基线）

### [J1] Garnelo et al., Neural Processes (2018)
- https://arxiv.org/abs/1807.01622
- 通过共享潜在变量建模函数分布、少样本适配与不确定性。
- 对我们：**共享任务隐变量 / 联合预测不是新的发明**；创新应体现为预训练 DiT 在 ICL 中如何实现、保留、诊断和改进此能力。

### [J2] Garnelo et al., Conditional Neural Processes (ICML 2018)
- https://proceedings.mlr.press/v80/garnelo18a.html
- 上下文聚合与 query-conditioned function prediction 的经典框架；部分设定更侧重条件边缘预测。
- 对我们：显式上下文聚合的强基线；不能把“Context Encoder”当作新方法。

### [J3] Dutordoir et al., Neural Diffusion Processes (ICML 2023)
- https://proceedings.mlr.press/v202/dutordoir23a.html
- 用 Diffusion 对函数的有限维联合边缘分布建模，强调 exchangeability / stochastic-process consistency。
- **最重要的邻近基线之一**：我们的论文要与之在联合生成质量、Q 泛化、校准、机制可诊断性、条件压缩与计算成本上认真对照，而不是说它没有考虑联合预测。

### [J4] Wang et al., In-Context Learning Unlocked for Diffusion Models / Prompt Diffusion (NeurIPS 2023)
- https://proceedings.neurips.cc/paper_files/paper/2023/hash/1b3750390ca8b931fb9ca988647940cb-Abstract-Conference.html
- 用示例图像对和文字提示进行视觉 ICL 与条件扩散生成。
- 对我们：视觉 Demo-to-Generation 的实践前史；区别在显式后验、联合一致性与理论可观测的机制。

## 5. Diffusion 时间动力学、Jacobian、信息与算法

### [D1] Biroli et al., Dynamical Regimes of Diffusion Models (Nature Communications 2024)
- https://www.nature.com/articles/s41467-024-54281-3
- 高维极限下 Speciation / Collapse 机制及不同时间尺度。
- 对我们：可研究模式专业化与时间窗口，但有限维/有限模型不应预设尖锐相变。

### [D2] Guo, Shamai & Verdú, Mutual Information and Minimum Mean-Square Error in Gaussian Channels (IEEE TIT 2005)
- https://doi.org/10.1109/TIT.2005.844072
- I-MMSE 关系；可将带噪输出的信息增长与条件后验协方差连接。数学工具，不是我们的独立新定理。

### [D3] Kong, Brekelmans & Ver Steeg, Information-Theoretic Diffusion (2023)
- https://arxiv.org/abs/2302.03792
- I-MMSE 用于扩散建模/概率估计。
- 对我们：说明“信息论 + Diffusion”早有前史；我们应展示它对生成式 ICL **共享任务与联合协同**的专门解释。

### [D4] Lin et al., Token Pruning for In-Context Generation in Diffusion Transformers / ToPi (2026)
- https://arxiv.org/abs/2602.01609
- 无训练 Token Pruning、Layer Sensitivity 与 Diffusion-time Adaptation。
- 对我们：JVP / Coherence-preserving 压缩若成为方法，要比其针对**联合分布、模式概率、跨位置耦合**提出清楚差异并做强基线比较。

### [D5] Zhang, Li & Xiao, In-Context Learning as Rate–Distortion Optimization (ICML 2026)
- https://proceedings.mlr.press/v306/zhang26cu.html
- 示例选择与 Token Budget 下的 ICL 率失真优化。
- 对我们：上下文压缩有前史；我们更关心 shared-latent **joint posterior-predictive distortion**，不是普通的提示删减。

### [D6] Gao et al., Opening the Black Box of Classifier-Free Guidance via Information Bottleneck (2026)
- https://arxiv.org/abs/2610.13369
- 条件扩散的信息瓶颈与动态 CFG。
- 对我们：动态采样校准必须比“某个时间段增强条件”更具体，考察联合结构与概率自洽性。

## 6. 最优先复读顺序与文献审视标准

**第一轮必须认真读**：R1 → R2 → C2/C3 → J3 → B2/B3 → D1/D3 → D4。随后补 C1/C4、B1/B4/B5、J1/J4、D5/D6。

每篇阅读只回答四个问题即可：
1. 它真正研究的随机对象、给定信息、输出单位是什么（单 Query / 联合 Query / 图像整体 / 独立 Batch）？
2. 它证明了什么，实际模型又只验证了什么？哪些是假设，哪些是观察？
3. 它对我们完整 Inference → Representation → Realization 主线提供什么有用工具或重要对照？
4. 哪个区别应该通过实验/理论直接检验，而不是停留在“词语距离”上？

**研究判断原则**：相近论文做了某个组件，不等于整体主问题已被解决；使用经典工具分析新的、重要的研究对象可以完全有创新。既不忽略强相关工作，也不以“不是全新定理/有人涉及局部问题”为理由收缩目标。
