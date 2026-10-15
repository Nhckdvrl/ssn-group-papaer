# Baherwani, Chen, Qiu, Wilson, Izmailov（arXiv 2606.25010，2026）— Emergent Capabilities Arise Randomly from Learning Sparse Attention Patterns

**原文**：[arXiv HTML](https://arxiv.org/html/2606.25010)。**阅读范围**：正文中 Pythia 部分与摘要。

## 结论与证据
- Pythia 14M–410M 各 10 组检查点（不同初始化）：重复 / 复制、模式补全、IOI 等**初级**能力在训练中随机时间点突然出现，大模型平均更早；160M / 410M 上复制任务 10 个模型都学会。
- 机制：把出现后的注意力分数修补进出现前模型，取 top-16 头即可恢复复制任务的差距；IOI 只可视化了一个类 name mover 头的注意力变化。
- 合成线性映射 / 元胞自动机：上下文越长、模式越稀疏越难学；更多头提高效率；MLP-Mixer 在复杂注意力模式上可胜过 Transformer。
- 作者明说：只到 1B 以下、能力较初级；依赖上下文的模式（如 induction）可能性质不同；**假设学会后不回退**（并称经验上验证过），不分析失败种子。

## 与我们的距离
他们回答“初级能力何时、为何突然出现”；E92 显示较复杂的 few-shot 能力在正常种子间出现时间很一致（160M / 410M 多数任务落在同一网格区间），而 31M 存在“学会后丢失”，与“不回退”的假设不同（小模型、粗网格，待核实）。
