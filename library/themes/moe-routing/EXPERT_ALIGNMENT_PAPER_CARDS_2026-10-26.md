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


## On Least Square Estimation in Softmax Gating Mixture of Experts `[证据：引言、§2–3；未复核附录证明]`
[arXiv v2, 2024-06-24](https://arxiv.org/html/2402.02952v2)
1. 形态：确定性dense softmax加权回归的统计估计理论。
2. 问题：总回归函数估计何时约束expert函数/参数，以及速率为何依赖函数族。
3. 来源（DOCUMENTED）：概率Gaussian MoE与确定性回归之间的理论缺口。
4. 方法：紧参数域/有界输入；定义包含参数导数线性独立的strong identifiability，推导函数误差与参数误差联系。
5. 最近邻距离：它已拥有“总函数估计与expert恢复不同、函数类决定可恢复性”这个理论问题；不能声称只有sum监督就必然不可识别。
6. 阅读边界：核对setup及§3定义/定理陈述；非任意SwiGLU/top8有限优化的无条件保证。尤其非线性输入变换条件不能省略。
7. 对本题：E138共有偏差与cohort variance需分开；近似误差不能直接升级为结构自由度，固定gate解析充分条件也不自动给稳定性界。

## Statistical Perspective of Top-K Sparse Softmax Gating Mixture of Experts `[证据：引言、setup及universal assumptions；未复核证明]`
[arXiv v2, 2024-02-23](https://arxiv.org/html/2309.13850v2)
1. 形态：top-K sparse softmax **条件混合密度**的MLE/参数估计理论。
2. 问题：top-K分区与模型过设定如何改变密度及参数估计。
3. 来源（DOCUMENTED）：稀疏门控分区使经典MoE统计分析更复杂。
4. 方法：Gaussian expert密度、紧参数域/有界输入、分区相关损失；其gate先TopK再Softmax，激活专家权重归一。
5. 最近邻距离：稀疏MoE的可识别性/恢复速率不是空白；本项目对象是确定性vector加权和，不能直接套条件密度可识别性。
6. 阅读边界：仅核对主setup、假设与结果陈述，不认领已验证其全部扩展。
7. 对本题：区分条件密度、加权均值与神经块函数；OLMoE no-renorm actual BF16程序与其统计模型不同，须明确映射而非引用标题作保证。

## RRD: Routing-and-Residual Distillation for Efficient MoE Recovery in Large Language Models `[证据：作者实验室/主页及公开代码README；论文全文未核对]`

- **核对时间：** 2026-10-26。作者实验室[出版页](https://mlai.yonsei.ac.kr/publications)实读，将此题名列为**ICML 2026 Workshop**；作者为 Hoyoon Byun, Kangjun Noh, SoMin Kim, Heedong Kim, Jaeyoon Shim, Sungjun Lim, Youngjun Choi, Kyungwoo Song。[Sungjun Lim主页](https://sungjun98.github.io/)另将 **RRD: Routing-and-Residual Distillation for Recovery after Dense-to-MoE Conversion** 列为Under-Review，未给可读新稿链接。具体版本/投稿修订日期未核对；**没有确认后续正式主会/期刊接收版**。搜索引擎出现的NeurIPS Downloads命中未能在其可读官方页核实，不当接收依据。
- **读取边界：** 原[hash PDF](https://openreview.net/pdf/30dff17a034b9e0643e0845fb5265d98d06b447b.pdf)、[note PDF](https://openreview.net/pdf?id=liG5bLSb7m)、forum及api/api2在本机web/curl和另节点均403/浏览器校验。搜索缓存中的匿名摘要/日期不是全文实读。以下方法事实只归于已读的[作者公开代码README](https://github.com/MLAI-Yonsei/routing_and_residual_distillation)，不冒称论文公式/表格逐项核对；未复现实验。
1. **形态：** dense→carved sparse MoE恢复方法；非本项目跨初始化职责研究的直接复刻判定。
2. **痛点：** README目标为让稀疏学生恢复dense教师MLP行为；仅task监督不给明确路由目标。
3. **前提：** 从dense参数拆出routed/shared专家，另用teacher侧信号指导router；不是随机同容量原生MoE学生的自然组织恢复。
4. **idea来源（DOCUMENTED，代码说明）：** 把总输出恢复与专家选择监督结合，利用shared专家及teacher magnitude top-K profile。
5. **已读方法：** 代码说明joint task CE、中间输出RMSE与router KL；routed top-K门控加always-active shared专家，并提供all-active MoE与dense MLP一致的sanity probe。KL方向/共享残差的实际公式尚未查源码，不能只凭README当论文精确定义。
6. **证据范围：** README给Llama-2-7B/Qwen2.5-7B入口、C4/WikiText-2数据与PIQA/WinoGrande/ARC/HellaSwag评测命令；具体论文数字、随机种子数量、置信区间、所报性能提升和版本变动均未核对。已读primary未呈现跨seed实际component重现读数，但不能据此断言全文没有。
7. **与E135–139距离：** E135固定原生public OLMoE自身H→Y、随机同容量单块学生，总函数监督无逐expert/router监督；E136/138精确提供并冻结原生teacher gate；E139配对expert初值比较free/fixed协议，以cal-only actual-component映射和held有限cohort偏差/变异/covariance及自然预测/A为对象。RRD的dense拆分初始化、shared恢复与路由KD是方法构造；我们的这些控制不是效率/恢复方法创新。
8. **ownership/compression risk：** “总函数/任务监督不足以明确路由、teacher路由信息有助恢复”已有直接近邻，不能把E136/E139写成首次teacher-guided routing发现。中间MSE/函数恢复工具也不新。可保留的增量是固定原生函数目标、配对初始化下组织协议对跨训练实际计算分解的作用及teacher共同偏差与学生间变异分离；是否全文还有更近证据不确定。
9. **动作：** 标为强相关待全文复核的定位项，**不是精确撞车、关线或新实验指令**；不推迟已登记E139，不增匹配/训练条件、不改claim状态。
