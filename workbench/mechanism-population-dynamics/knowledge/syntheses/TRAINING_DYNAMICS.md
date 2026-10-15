# 学习动力学、头专业化与“初始化留下痕迹”的正确解释尺度

## 0. 现象与解释分开

观测：两次训练共享初始权重时，一些注意角色图在不同语料后仍有统计相似；训练早期扰动比晚期更容易改变这种相似。这不自动意味着“角色预刻”或“训练中存在严格不可逆的关键期”。

**真正可以研究的对象**：训练何时、通过哪些子计算或参数状态，逐渐使某些头更容易成为特定角色，以及这种路径依赖对最终真实计算是否有后果。

## 1. 证据阶梯

| 阶梯 | 原始实验 | 实际知道什么 | 竞争解释 |
|---|---|---|---|
| 初始状态 | [E35](../../experiments/E35-init-by-data-mechanism-census.md)、[E39](../../experiments/E39-init-weight-predictors-of-roles.md)、[E41](../../experiments/E41-initial-gradient-predictors.md) | step0注意模式不明显预测；几个范数和梯度范数未找到层内预测力 | 相对几何、上游输入、交互项或随机优化 |
| 训练早期共同结构 | [E37](../../experiments/E37-identity-lock-in-timing.md)、[E40](../../experiments/E40-lock-in-curves-pythia.md) | 早期checkpoint的角色倾向与末期相关 | 相同祖先与数据顺序共同影响；后期角色仍能变 |
| 分叉的有限吸引域 | [E46](../../experiments/E46-controlled-training-basin-and-critical-period.md) | 某些训练步以后大扰动恢复role map；极早期扰动大 | 学习率/优化器状态/剩余训练量/类别形成程度 |
| warm-up与优化器 | [E66](../../experiments/E66-early-window-warmup-and-optimizer.md) | 拉长warmup会让敏感窗口随之移动，重置AdamW状态未打破已形成的部分布局 | 依累积更新幅度、输入表示或路径依赖 |
| 语料距离 | [E56](../../experiments/E56-inheritance-depends-on-corpus-similarity.md)、[E60](../../experiments/E60-corpus-distance-predicts-inheritance.md) | 语料统计越近，配对角色图越像（相关） | 来源重叠、训练事件相似，而不是“语义主题独自决定” |
| SGD噪声近似 | [E62](../../experiments/E62-batch-size-sets-inheritance.md) | 在小模型c4 vs papers设置中lr/batch变化与继承强度相关 | 其他训练超参数/输入差异共同作用，尚非数学定律 |
| 任务承担发展的差别 | [E82](../../experiments/E82-when-carriers-are-fixed.md)、[E83](../../experiments/E83-carrier-chosen-at-emergence.md) | 不同训练run早期主力可能改变；首次IOI行为出现时终点主力仅3/12保留 | 候选竞争、网络重新路由、能力增长导致评价对象变化 |

## 2. 为什么“1%–2.5%的关键期”不是可推广结论

E46的特定实验用了少数初始化、短的10k步小模型和特定扰动；E66的warm-up从300变1000步就改变敏感窗口的步数位置，换语料在窗口之后还可部分改写最终角色图。

因此应写成：**早期学习形成某种受后续训练约束的角色分配倾向，形成速率受训练计划影响**。数值时间窗口不应脱离训练计划和模型/任务硬套成自然规律。

## 3. “一个head形成”的相变可能是多个子过程的合成

[Singh 2024](../papers/SINGH_2024.md)从训练期间对match/copy子电路做activation clamping，看到外观上突变的induction形成可以由多种渐进过程的交互导致。

可迁移的逻辑：不要从某个head的score跨过阈值，推断它被突然选定；要观察形成它所需的上游route、复制投影与下游读取。头间many-to-many交互本来可能比一个winner-takes-all更自然。

[Olsson 2022](../papers/OLSSON_2022.md)的induction角色定义是很好的微观起点，但不是整个ICL发展机制的终点。

## 4. 数据和初始化如何共同作用

[MDA 2026](../papers/MDA_2026.md)在数据级归因和针对性训练干预上有强进展，并在附录F.2.2看到160M多头角色变化；但它还没有证明我们所有目标任务的上游算法都因数据而变。

我们如果观察某个头从任务A变任务B，至少有三种解释：
- 训练数据促使该头本身学到新计算；
- 上游提供的表示改变，而该头的局部参数没有主要改变；
- 同一类计算在多头间重新分配贡献份额。

需要能区分的局部训练/前向因果测试，而不是继续把seed、数据标签作为全部答案。

## 5. 下一轮形成机制的最小高信息量实验

优先在**训练初始状态**而非训练后随意拼接两个模型的head，交叉某个head的完整初始参数与同层其余网络/上游的初始参数，继而在同数据流下独立训练。观察最终角色统计是否跟随局部head或所处网络；如果有差异，再挑一个具体上游路由做交互干预。

不过，[Frozen-QK](../papers/FROZEN_QK_2025.md)已经说明初始QK可以不更新而功能形成；“周围参数也重要”不是新意。实验要继续走向可预测的分工、训练状态或最终实际任务作用，否则只得到一个显而易见的多因素答案。

这是**研究备选**，不是现在可自动启动的训练列表。
