# The Router Already Knows（2026-10-20 预印本）`[证据级别：原文 §1–2、摘要中的限制；未复跑]`

来源：[arXiv v1 全文](https://arxiv.org/html/2610.27421v1)。作者 Andrew Bistras、Marty Johnson；不据未核对的接收信息评估。

1. **论文形态：** 结构引导的稀疏字典学习及匹配控制。
2. **背景与压力：** 对 MoE 求和后输出学习字典会丢掉原生路由身份；能否直接用已有 router 选择小字典？
3. **改变的前提：** 每个被调用原生专家对应一个字典，而非重新学习全局辅助路由。
4. **idea 来源（DOCUMENTED）：** 复用原模型已经计算的稀疏地址；作者同时指出 down projection 的低秩输出空间可能解释部分优势。
5. **与最近邻的距离：** 相对 Switch/Multi-expert SAE，使用原生 gate；相对 RouterInterp，解释对象由路由转向专家向量；相对直接专家神经元分析，引入学习字典。本文没有跨独立训练模型的职责对应。
6. **方法/证据：** Gemma 4 一个块，两种重构接口、三个字典训练 seed；对照控制候选数、rank 地址与随机 expert identity。报告 gate 加权分量重构。没有测预测损失、因果忠实度或下游任务。
7. **强度与短板：** 专家身份有重构价值有匹配对照；输出子空间、共享均值与实际预测用途仍要区分。字典 seed 不等于模型训练 seed。
8. **可迁移研究动作：** 先比较实际分量和合成输出，再对接完整下游；用结构匹配对照区分“知道索引”与“恢复计算”。
9. **对本工作台：** E144 不认领 expert identity 帮助重构；它拆散独立学生来源并测完整预测。其下游缺口支持直接 KL/NLL 的优先级，但不预告重组必有损，不自动构成新颖性裁决。

## 另一篇近邻的接口适配备注

[Routers Learn the Geometry §2–3](https://arxiv.org/html/2605.12476v1) 的 masked activation 及未选行梯度论证不能直接用于本项目完整 softmax 后截取、不重归一的 OLMoE。忽略量化、固定支持时，task gradient 有全行分母项；具体自主推导与 tiny HF 核对见 [当前研究说明](../../../workbench/mechanism-population-dynamics/moe/RESEARCH_DIRECTION.md) §4.1。这里只校对适用前提，没有宣称推翻其设置下的结论或识别新的历史机制。
