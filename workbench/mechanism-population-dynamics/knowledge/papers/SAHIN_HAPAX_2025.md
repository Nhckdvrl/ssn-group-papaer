# Şahin, Feucht, Belfki, Wendler, Bau, Brinkmann, Mueller — In-Context Learning Without Copying（arXiv 2511.05743 v2，2026-02）

**原文**：[arXiv HTML](https://arxiv.org/html/2511.05743)。**阅读范围**：正文；附录 F 之后未读。

## 设计
Hapax：训练时把“可由 induction 预测”的位置（某个更早位置有相同的前一 token 与当前 token，即重复二元组）从损失中去掉（仍留在上下文里）；严格版按嵌入余弦 >0.3 扩展。1B、GPT-NeoX、Pythia 超参、Pile 20k 步约 40B token；Hapax 去掉 31.7% 的 token，严格版 52.5%。

## 结果
- 随机重复准确率下降 66%（严格版 89%）；前 10 个前缀匹配头均值 61% → 40% / 36%（仍有一个 ~100% 的头）。
- 抽取式 ICL：24 个显著差异中 23 个变差。
- 抽象 ICL（Todd 26 任务 + 8 个翻译）：Hapax 在 21 个显著任务中 13 个更好；控制标签重叠后 25 个中 24 个更好；严格版多数变差但翻译更好。
- 未分析 FV 头。

## 对我们的意义
“抽象 ICL 是否依赖 induction 作为脚手架”已基本被回答（不依赖，甚至有替代 / 竞争关系）；我们不再追此题。但 Hapax 是“在真实规模预训练里删除一种学习信号、看机制与能力怎么变”的可行范例。
