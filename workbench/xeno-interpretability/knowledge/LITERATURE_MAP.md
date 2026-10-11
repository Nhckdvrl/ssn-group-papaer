# 初步领域地图：表征与解释之间究竟隔着什么？

**状态：FIRST-PASS MAP（2026-10-12）**。这是选定阅读谱系的起点，不是基于全面精读做出的缺口定论。

## 起点与范畴
Xeno 原论文问：神经网络可能使用当前人类概念本体无法充分覆盖的内部区别吗？回答前必须拆开四种不同尺度：
1. **识别/解码**：从激活统计预测某个人类标签；
2. **描述/覆盖**：解释（自然语言、组合程序、结构约束）能跨数据预测该内部结构的激活条件；
3. **因果/机制**：实验控制的内部变量是否解释真实模型行为，干预及替代抽象在 holdout 上成立；
4. **模型本体/认识论**：若解释失败，究竟由于人类概念不完备，还是实验仪器、描述语言、数据与统计不足？

不能将“解释器失败”升格为“模型具有超人类语义”，也不能把离线聚类与天然计算变量直接等同。

## 五条并行且需要相互对照的邻域
### A. 语言描述的可靠性
- Parent: 给 neuron / SAE feature 做 language labeling；从激活样本生成解释。
- Pressure: 自然语言解释可能过宽、未在相似负样本和 out-of-distribution 分布下经受考验；语言流畅不等于功能准确。
- 关键文献：Feldhus & Kopf 2025 综述；Ma et al. NeurIPS 2025。
- 开放问题：组合/程序描述能在多大程度上消除看似 xeno 的残差？如何避免因为“描述的词汇受限”人为制造 gap？

### B. 分解是否唯一、可复现、跨训练成立
- Parent: SAE/其他稀疏分解把激活空间转换为特征字典。
- Pressure: seed/字典大小/重建权衡改变发现，模型空间的对称性让某种坐标分解不是天然本体。
- 邻域：ICLR 2026 SAE trained on same data...；ACL 2026 feature consistency；NeurIPS 2026 Bypassing PC1...（**只核对标题/作者信息**）。
- 开放问题：一个 candidate 是真实跨方法计算对象还是字典构造伪影？允许何种等价类？

### C. 干预的真实性与解释有效性
- Parent: causal abstraction, MIB, activation patching / steering / DAS。
- Pressure: flexible alignment 能人为拟合解释，干预可能 off-manifold；因果控制不等于自然机制。
- 邻域：JMLR 2025 Causal Abstraction；NeurIPS 2025 Non-Linear Representation Dilemma；ICML 2025 MIB / SAEBench。
- 开放问题：在哪种干预族内，“这种解释足够好了”才具有可证伪性？怎样与便宜行为/logit baselines 比较？

### D. 概念本体本身是否不完整
- Parent: concept bottlenecks / supervised interpretable concepts。
- Pressure: 少一个潜变量可能使已知概念关系发生不一致。
- 邻域：Parisini et al. 2026 `Concept frustration`（公开摘要已有形式化与实证，**不能宣称没人做过**）；Concept-Based MI Needs a Concrete Evaluation Paradigm（全文待读）；NeurIPS 2026 level-of-description 工作（标题待全文）。
- 开放问题：什么具体的实验结果可以区别 ontology incomplete、concept classifier weak、task geometry distorted 与 causal mechanism mismatch？

### E. 多模型、多智能体的迁移与通信（非必需分支）
- Parent: representation alignment / learned communication。
- Pressure: 协作训练的内部状态和消息可能逐渐共同适配而失去人类词汇可读性。
- 开放问题：如何区别隐藏信息、压缩协议、纯训练捷径，与新的任务相关的内部功能区分？优先先看真实通信文献，而不是从概念论文直接脑补集体 xeno。

## 三种以上竞争解释（不要预设 H3 成立）
- **H1 描述不足：** 扩大解释语言（组合规则、描述长度、程序）与训练数据，拟合缺口消失。
- **H2 仪器伪影：** 误差来自 SAE/probe/geometry 的不稳定、不同坐标或采样与 off-manifold 干预。
- **H3 真实但普通的计算对象：** 存在稳定因果结构，不过它是多种已知机制组合、任务压缩或计算 shortcut。
- **H4 更强的本体缺失：** 在合理的描述类、强对照及跨分布因果检验后仍有显著、稳定、可泛化的功能区分无法被当前概念体系充分覆盖。

H4 只能是逐步升级的经验假设；任何有限实验证据都不能证明“原则上永不可描述”。

## 先弄清楚的重叠与 ownership risk
- `Concept frustration` 已经研究缺失概念与 task-aligned geometry；
- feature description falsification 已是实证 program；
- non-canonical SAE / cross-method explanations 已形成拥挤近邻；
- NeurIPS 2026 公开名单出现直接同邻域工作（见 [READING_QUEUE.md](READING_QUEUE.md)）。
因此真正可挖的是**他们在哪种假设和证据层级尚未达成一致**，而不是声称“以前没人考虑模型原生概念”。

## 当前欠账
- 综述和最近邻尚未逐篇 FULL_TEXT 核验；
- NeurIPS 2026 没完成 systematic scan，也没正式给每篇验 Track；
- 未从开源模型复现标准基线；未有可报告的异常/证据；
- 尚未选择论文唯一中心 RQ。
