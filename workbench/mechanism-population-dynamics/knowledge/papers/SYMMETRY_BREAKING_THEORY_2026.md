# 头专业化的对称性破缺理论（2026）：Sagitova, Duranthon, Zdeborová；Incremental Learning of Sparse Attention Patterns

**原文**：[arXiv 2603.03993](https://arxiv.org/html/2603.03993v2)（Specialization of softmax attention heads: insights from the high-dimensional single-location model）；[arXiv 2602.19143](https://www.alphaxiv.org/abs/2602.19143)（Incremental Learning of Sparse Attention Patterns in Transformers）。**阅读范围：只读了检索摘要与少量正文片段，未精读。**

## 要点
- 单层多头 softmax 注意力、单个相关 token 藏在噪声中的合成任务，SGD 训练：先是未专业化阶段，再是多阶段专业化，各头依次对齐不同的潜在信号方向；**未专业化状态是梯度流的不变集，专业化只能由初始化或 SGD 引入的不对称触发**；专业化开始时间 Θ(log D)。
- 2602.19143：简化回归设置中，头的初始化只要有微小不对称，梯度流最终会把某个头推离、出现对称性破缺（增量地学习稀疏注意力模式）。

## 与我们的关系
理论在简化模型里说“谁专业化由微小初始不对称被放大决定”。E96 在真实预训练语言模型（Pythia-160M step100k）的训练期损伤中观察到：功能受损后流向**原本就有弱倾向的头**（3.0；清零备份后 3.4 / 3.1 / 2.8），受损头即使保留一半参数、位置空缺也不原位再生——与“已有不对称被放大”的图景一致。E97 用事先预测检验这条规则是否跨功能成立。若成立，它把“初始化决定哪个头”（工作台早期的 C05 统计）与可干预的训练期机制连起来。
