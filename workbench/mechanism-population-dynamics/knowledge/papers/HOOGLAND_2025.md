# Hoogland, Wang, Farrugia-Roberts, Carroll, Wei, Murfet (TMLR 2025) — Loss Landscape Degeneracy and Stagewise Development in Transformers

**原文**：[arXiv 2402.02364 v3](https://arxiv.org/html/2402.02364v3)。**阅读范围**：正文；附录 B.4（种子）与 F（设置）被截断未读。

## 问题
训练是否分阶段？阶段能否由损失地形的几何（退化程度，用局部学习系数 LLC 估计）识别，并与内部结构 / 行为变化对应？

## 设计与结果
- 约 3M 参数、2 层纯注意力 LM（Pile 子集）；另有 in-context 线性回归小模型。
- 用 SGLD 估计 LLC 曲线，平台期为阶段边界。LM 阶段：LM1（0–900 步）二元组统计；LM2（900–6.5k）位置嵌入有用、常见 n-gram、首层头开始组合；LM3（6.5k–8.5k，LLC 下降）首层 previous-token 匹配上升；LM4（8.5k–17k）第二层 induction 前缀匹配上升；LM5 无显著变化。
- LLC 下降段被解释为计算结构的“简化”，但作者承认机制不清。
- 作者明说：induction 回路的基础在输出 / 注意力出现可测变化之前就已奠定；**不解释哪个头为何专业化**；只研究了两个小设置；退化变化与结构变化的因果联系未建立。

## 与我们的距离
发育阶段 + 头分化的主线（Timaeus / SLT）目前只在极小模型上；自然大规模预训练中的阶段与组件分化、跨种子的一致性尚缺。我们的 E89 / E90 数据（正常 410M 种子在 1k 步定下 previous-token 枢纽、之后不换）可放进这个框架理解，但 LLC 估计在 410M 上成本高、可靠性未知。
