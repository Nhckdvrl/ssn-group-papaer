# 专家对应与组合：补充论文卡（2026-10-26）

只记录已核对正文的范围；以下成熟思路作为E133强基线来源，不作新颖性自动裁决。

## REAP the Experts: Why Pruning Prevails for One-Shot MoE Compression `[证据：相关正文]`
[arXiv v3，2026-05-13](https://arxiv.org/html/2510.13999)
1. 形态：重建误差分析＋压缩方法。
2. 压力：参数冗余与专家合并的函数失真。
3. 前提：区分删除函数与丢失独立门控自由度。
4. 来源（DOCUMENTED）：从替代误差中的门值和输出幅度构造剪枝重要性。
5. 近邻：M-SMoE、HC-SMoE、REAM；输出/路由权重不是本项目首创。
6. 核对§3–4；以激活时的门加权输出范数评价专家。
7. 限制：理论使用归一化active gates及简化合并模型；不直接当作本项目no-renorm情形的通用定理。未复核全部证明/实验。
8. 动作：从真实算子误差定义组件重要性。
9. 对我们：E133用同类重建思想作强基线，单独给出适用自身算子的Cauchy界，不宣称新理论。

## REAM: Merging Improves Pruning of Experts in LLMs `[证据：相关正文]`
[arXiv v1，2026-04-06](https://arxiv.org/html/2604.04356)
1. 形态：专家压缩方法。
2. 压力：剪枝损失知识，合并依赖分组质量。
3. 前提：同时看调度与输出，而非单一相似度。
4. 来源（DOCUMENTED）：结合REAP重要性及门加权输出相似。
5. 近邻：REAP、M-SMoE、HC-SMoE。
6. 核对§3–4：聚合gate-logit与门加权输出相似，结合权重/激活对齐和逐层合并。
7. 限制：单模型内压缩与校准分布；未独立重跑结果。
8. 动作：把接口支持纳入函数比较。
9. 对我们：不能把路由加权输出匹配包装为首创；E133只检验其跨独立训练整库移植中的可用性。

## Retraining-Free Merging of Sparse MoE via Hierarchical Clustering `[证据：相关正文]`
[arXiv v4，2025-10-26](https://arxiv.org/html/2410.08589)
1. 形态：无重训压缩方法。
2. 压力：router/权重空间相似未必保留函数。
3. 前提：以校准输入上的专家输出作代表。
4. 来源（DOCUMENTED）：均值输出向量＋层次聚类。
5. 近邻：M-SMoE、REAP、REAM。
6. 核对§3.2.1–3.2.3：先平均输出，再分组/合并参数。
7. 限制：平均向量与逐输入函数距离不同；未复核全部附录。
8. 动作：用实际计算而非参数坐标定义邻近。
9. 对我们：E133是逐输入MSE，不冒称原HC-SMoE复现；仍需held组合后果，不能把输出近自动称语言职责同。

## Collective Model Intelligence Requires Compatible Specialization `[证据：相关正文]`
[arXiv v1，2024-11-04](https://arxiv.org/html/2411.02207)
1. 形态：失败模式＋构念测量。
2. 压力：专化模型的特征组合可能失效。
3. 前提：专化能力与表示兼容性须分开。
4. 来源（DOCUMENTED）：微调过程中的合并退化与CKA变化。
5. 近邻：LMC-MoE、Expert Merging、FLEx。
6. 核对引言/§2–3：冻结attention、微调多层MLP；在代码/数学域训练后组合，并比较不同路由方式。
7. 限制：输入/下游表示仍随其它MLP变化，与本项目单层冻结接口不同；未审所有实验。
8. 动作：把专化和实际组合共同评估。
9. 对我们：不能认领一般“共同任务好不等于兼容”；可增加固定接口、同目标独立训练的控制与历史干预。

## Routing Divergence Is Not Evidence of Behavioral Influence in Same-Weight MoE Self-Distillation `[证据：相关正文]`
[arXiv v1，2026-08-16](https://arxiv.org/html/2608.15787)
1. 形态：精确分解＋直接行为干预。
2. 压力：gate距离不等于下游影响。
3. 前提：同权重、不同条件下分开gate与content变化。
4. 来源（DOCUMENTED）：自蒸馏条件差异及其残差流暴露。
5. 近邻：StableMoE、RouterInterp、统计MoE框架；一般代理警告已有主张所有权。
6. 核对§1–2及结果概述：固定内容的路由项、固定路由的内容项与输出patch。
7. 限制：不是跨不同权重的训练历史，未独立重跑；不移用其经验范围为门槛。
8. 动作：代数分解后仍须直接行为验证。
9. 对我们：C06仅支持性测量；E131问权重轨迹，E134为单次原生输出均匀中心化，估计对象不同，不冒称分解首创。

## Towards a Statistical Understanding of Mixture-of-Experts `[证据：相关正文]`
[arXiv v1，2026-09-03](https://arxiv.org/html/2609.03501)
1. 形态：统计理论＋模拟。
2. 压力：局部聚合、稀疏与共享成分的统计作用。
3. 前提：可预测专家轨迹与plug-in路由学习，而非全联合优化动力学。
4. 来源（DOCUMENTED）：局部预测结构与近年的shared-expert架构。
5. 近邻：DeepSeekMoE、共享专家统计理论、经典MoE可识别性。
6. 核对引言、§6：固定Top1两区域/学习规则，比较显式共享加局部残差的学习问题。
7. 限制：收益依赖函数类/学习规则；未复核长附录证明。
8. 动作：分离统计对象和具体优化轨迹。
9. 对我们：E134均匀均值不等于其统计共享函数；E131的联合非凸历史后果不由该理论直接推出。


## Rethinking Routing Exploration in Modern Mixture-of-Experts `[证据：§1–2与C.1，非全文复核]`
[arXiv v1，2026-10-15](https://arxiv.org/html/2610.22353)
1. 形态：训练失败模式＋MirrorMoE方法。
2. 压力：细粒度组合空间变大，共享专家却削弱路由探索。
3. 前提：共享/路由专家的影响不对称，组合容量不自动被优化利用。
4. 来源（DOCUMENTED）：单专家消融、随机路由及输出变异诊断。
5. 近邻：DeepSeekMoE、Routers Learn Geometry、Routing Divergence；均提示路由变化与预测价值须分开。
6. 核对共享/非共享对照、逐层随机路由；C.1界依赖非负归一化组合，不能直接用于本项目no-renorm门值。
7. 限制：没有独立复核全实验；其显式共享模块不同于E134事后逐输入均值。
8. 动作：检验可探索差异是否真的能影响输出。
9. 对我们：共有计算占优、路由影响弱及随机路由检查已有ownership；E134仅增加特定均匀分量干预，不认领一般冗余结论。

## Beyond Geometric Complementarity: Coherent Overlap in Sparse Mixture-of-Experts Routing `[证据：§1–2/5–6/S6，非全文复核]`
[arXiv v1，2026-07-30](https://arxiv.org/html/2607.28308)
1. 形态：几何构念＋factorial与功能干预。
2. 压力：共路由几何重叠不能判定专家有无预测价值。
3. 前提：分离候选质量、共选上下文与交互。
4. 来源（DOCUMENTED）：固定prefix的2×2对照，再检验增添/替换专家的NLL后果。
5. 近邻：Routers Learn Geometry、When Are Experts Misrouted、RouterInterp；功能价值不能由几何标签代替。
6. 核对多架构调查及OLMoE/Mixtral/DeepSeek冻结路由功能检查，另有小型等活跃容量Top1/2训练。
7. 限制：几何是指定秩线性输入子空间，功能检查不是跨训练可对应性；未复核完整附录。
8. 动作：把重叠与可替代性作为两个命题分别干预。
9. 对我们：E134的均值可保任务得分不等于“其它专家无用”；不能认领几何与功能不等价这一一般结论。
