# Interpretability at Scale: Identifying Causal Mechanisms in Alpaca（NeurIPS 2023）[证据：正文§3、§4.5核对]

原文：https://arxiv.org/html/2305.08809v3

1. **形态：** 方法＋大型冻结模型的因果抽象。
2. **压力：** DAS需要手设子空间尺寸，变量可能分布在不同规模的表示内。
3. **改变前提：** 同时训练orthogonal rotation与可退火soft边界，评估时snap成binary masks；主模型冻结。
4. **idea来源：** DOCUMENTED为手设dimensions的搜索难度，非作者原始过程复盘。
5. **最近邻距离：** DAS分布式对齐→边界也可学习，继承IIA判据。
6. **实验对象：** Alpaca价格区间判断，比较两个Boolean边界、mid-point distance、bracket identity解释。结果不能将高max IIA当独立原生组件。
7. **证据审计：** 在固定价格区间学rotation后，换区间不重训；另加入20个prefix、改instruction，检验alignment而非只比性能。有正确/错误子集分析。表的IIA_max来自位置/层搜索，与我们的固定接口不同。
8. **可迁移动作：** 冻结发现对齐后改变任务具体参数与无关上下文，测同一因果变量是否仍可运输。
9. **ICES：** 可用于criterion/private polarity的子空间分解，但要先用实际有效接口判定在运输什么。避免在任意槽位不断训练更强控制再把分数称原生机制。
