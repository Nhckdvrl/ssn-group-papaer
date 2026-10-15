# Trott (arXiv:2509.22831) — Toward a Theory of Generalizability in LLM Mechanistic Interpretability

**原文**：[arXiv全文](https://arxiv.org/html/2509.22831)｜**阅读范围**：框架定义与1-back head实证；并非作者所有引用工作全文审计。

## 为什么重要

Mechanistic interpretability谈“universality”时，不同作者可能在问完全不同的问题：行为是否相同、同一元件是否出现、不同元件之间关系是否保持、配置如何分布。这导致表面矛盾被误读为反例。

## 文中的五个维度

- Functional generalizability：某类组件的计算功能是否广泛存在。
- Developmental：训练中如何形成，是否有相似轨迹。
- Positional：坐标/深度/具体位置是否保持。
- Relational：组件与组件的关系是否对应。
- Configurational：某类实现和部件组合的分布规律。

实证以previous-token / 1-back head为重点，多个Pythia尺度和训练阶段。**这是分类框架加局部验证，不是已证明LLM所有电路都遵循一个完整普适定律。**

## 对本workbench两种重要约束

1. 不能把“relational universality”这个词当我们的新理论发明。
2. 也不必被框架吓得不敢研究：分类并不自动告诉我们，当IOI与CO同时成立时，一个**统一的对应能否预测两任务之间的联合干预后果**。

## Idea来源/实验设计能学什么

它改变的不是某一个小技巧，而是把常被混淆的“同一机制”拆成多个可分别观测的命题。对此类研究，应先决定要比较的对象，再写出指标，而不是让一个相似度数字同时替代功能、发展和关系的答案。

**我们的下一步**要用真正可操作的干预测量把relational/configurational落实，不能停在重新罗列五种名称。
