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


## Every Expert Matters: Towards Effective Knowledge Distillation for Mixture-of-Experts Language Models `[证据：摘要/§1、§4入口，非全文]`
[arXiv v1，2025-02-18](https://arxiv.org/html/2502.12947)
1. 形态：MoE→dense蒸馏方法。
2. 压力：稀疏教师原路由没有暴露全部专家知识。
3. 前提：非选中专家也可能提供有用监督。
4. 来源（DOCUMENTED）：教师路由与学生学习过程的诊断。
5. 近邻：常规KD、MoEBERT、B-Distill；MoE教师不是新设置。
6. KA多次采样专家；SAR用全部专家并调router；正文用dense学生。
7. 限制：本次未复核全部实验；其教师目标可被改变。
8. 动作：区分忠实拟合原函数与提取更多潜在知识。
9. 对我们：E135明确只固定native H→Y，不用KA/SAR改教师，也不认领KD方法。

## Balanced Knowledge Distillation for Large Language Models with Mix-of-Experts `[证据：AAAI正式摘要，非全文]`
[AAAI 2026，2026-03-14](https://ojs.aaai.org/index.php/AAAI/article/view/39543)
1. 形态：MoE→MoE蒸馏方法。
2. 压力：教师覆盖不足与学生router负载失衡。
3. 前提：师生MoE仍需专门的转移/均衡约束。
4. 来源（DOCUMENTED，摘要）：专家覆盖与router失衡观察。
5. 近邻：Every Expert Matters、常规KD、MoEBERT。
6. Monte Carlo专家探索与entropy-aware教师路由监督。
7. 限制：这里只读官方摘要，不作精确实现/实验覆盖判断。
8. 动作：将函数监督与组织监督分开。
9. 对我们：MoE→MoE已有ownership；E135不监督教师gate/专家编号，避免用强制组织对齐再声称自发恢复。

## Soft-to-Hard Routing in Sparse Mixture-of-Experts Models `[证据：v2摘要/§1/§2与§5范围，非证明复核]`
[arXiv v2，2026-05-23](https://arxiv.org/html/2605.02124)
1. 形态：总体平方损失MoE回归的边界层理论。
2. 压力：softmax低温近似在router ties附近奇异。
3. 前提：控制边界概率质量，而不只温度数值。
4. 来源（DOCUMENTED）：soft→hard极限及额外假设下的landscape转移。
5. 近邻：经典MoE可识别性、统计MoE框架、路由几何。
6. 归一化dense softmax→hard top1，条件性teacher recovery/对称破缺诊断。
7. 限制：不是有限预算神经Top8 no-renorm联合训练定理；未复核长证明。检索旧标题Boundary Mass不可当作v2题名。
8. 动作：把可识别性假设与经验优化结果分开。
9. 对我们：E135拟合/不拟合都不自动证明唯一/不可能，不直接援引其条件定理解释原生OLMoE。

## MoEBERT: from BERT to Mixture-of-Experts via Importance-Guided Adaptation `[证据：正式摘要＋§3.3检索片段]`
[NAACL 2022](https://aclanthology.org/2022.naacl-main.116/)
1. 形态：压缩/适配方法。
2. 压力：小dense学生容量损失与推理成本。
3. 前提：将原FFN适配为专家，保留部分预训练表示。
4. 来源（DOCUMENTED）：重要性适配与逐层蒸馏。
5. 近邻：Patient KD、Every Expert Matters、B-Distill。
6. 有中间层MSE与最终预测分布蒸馏；非本项目同容量原生单块重学。
7. 限制：未读全文，不能据摘要判断跨训练职责实验。
8. 动作：层函数监督是已有工具。
9. 对我们：E135用MSE作为科学控制，不认领逐层蒸馏首创。
