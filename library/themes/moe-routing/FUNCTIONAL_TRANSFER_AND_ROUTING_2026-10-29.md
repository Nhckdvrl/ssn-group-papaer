# 功能迁移与实际使用：全文核对及下一问题（2026-10-29）

新增完整PDF五篇共100页，含可取得的附录；AAAI出版PDF未附补充；后续从arXiv v1源包取得并完整读了补充LaTeX及12张表源码，不称独立出版的camera-ready附录。版本/PDF SHA/逐页覆盖及关键图在[阅读凭证](../../../workbench/mechanism-population-dynamics/moe/notes/PRIMARY_READING_TRANSFER_2026-10-29.json)。Multi-Way v2随后在E164冻结运行期间补完22页，不改变已注册干预或读数。

## Transferring Linear Features Across Language Models With Model Stitching（NeurIPS 2025，33页）

1. 形态：迁移方法与功能特征研究。[正式全文](https://papers.neurips.cc/paper_files/paper/2025/file/4569a868e7aa891248832ec08445d071-Paper-Conference.pdf)。
2. 压力：不同规模模型的SAE/探针需重复训练。
3. 前提变化：用双向仿射映射及MSE/逆映射约束迁移特征。
4. 来源DOCUMENTED：model stitching、弱universality、SAE；不是只做相关性。
5. 距离：同家族Pythia/GPT2/Gemma，跨规模残差空间。
6. 实证：SAE初始化省算力、真实探针/语言steering、功能特征路径消融；部分语言/格式任务转移弱。
7. 界限：next-token CE未完全恢复；逆映射接近identity不保证单向完整品质，训练stitch约200M缓存token。
8. 可借动作：把有用特征、完整品质和实际使用分开评估；保留失败任务。
9. 对我们：一般线性特征迁移已有实证。当前同S_P的权重和写入基底都固定，学到修复映射不能单独命名自然分工机制。

## How Not to Stitch Representations to Measure Similarity（AAAI 2025，9页出版PDF）

1. 形态：测量失效与直接匹配基线。[正式全文](https://ojs.aaai.org/index.php/AAAI/article/download/33698/35853)。
2. 压力：task-loss stitch可以把远层判得比自身还相似。
3. 改变前提：比较任务损失优化与不读标签的直接表示匹配。
4. 来源DOCUMENTED：既有stitching与表示相似性检验。
5. 距离：ResNet/ViT图像分类，非成熟MoE历史。
6. 实证：真实精度、OOD检测、层身份/低rank检验；不是只有几何推测。
7. 界限：图像范围；DM/Procrustes也依赖目标与评价，不提供普遍相同计算的oracle。
8. 可借动作：修复性能和识别原计算分开，不把新任务训练当原职责恢复。
9. 对我们：不因此放弃重用问题；优先做无需学习修复器的运行路径干预。arXiv v1补充源码已读，含同空间尺寸控制和逐层完整统计；作者README也已核对。

## Grounding Functional Similarity by Invariance-Aware Model Stitching（ICML 2026，arXiv v2，22页）

1. 形态：相似性框架与反例/修正。[实际版本全文](https://arxiv.org/pdf/2505.20142v2)、[正式接收记录](https://openreview.net/forum?id=yUEFOa32CG)。
2. 压力：依赖不同信息cue的模型也可成功stitch。
3. 改变前提：加入源模型表示不变输入的前像约束。
4. 来源DOCUMENTED：Smith等stitch失效、共享invariance、feature distillation。
5. 距离：forward–backward compatibility不是变换的round-trip inverse。
6. 实证：真实shortcut/稳健性任务，多架构及完整附录；比较HLM/SLM/DM/FuLA。
7. 界限：近似IRIs、优化协议与相似性直觉仍有限，作者未声称oracle。
8. 可借动作：特征可用、可对齐与原生使用不是同一读数。
9. 对我们：保留任务干预价值，避免从adapter成功直接声称功能身份/共同语义单位。

## Routers Learn the Geometry of Their Experts（2026预印本v1，14页）

1. 形态：梯度分析、训练实证与centroid router。[全文](https://arxiv.org/pdf/2605.12476v1)。
2. 压力：路由塌缩与均衡损失如何改变专家组织。
3. 改变前提：把router/expert看作共同输入历史的累积者。
4. 来源DOCUMENTED：SwiGLU梯度、loss-free均衡、在线K-Means。
5. 距离：9层1B/64R+2S/50B训练；训练几何与本题成熟终点的运行通路不同。
6. 实证：激活–score关系、真实训练/PPL/负载对照；不简化为相关性。
7. 前提：masked routing的未选行零梯度不能照搬native full127分母；共有输入方向的观察不因此取消。
8. 可借动作：把训练耦合与推理时某条通路对预测性质的作用分开检验。
9. 对我们：一般router–expert共同演化已有ownership；需要识别R_B迁移收益究竟经专家响应还是后续实际gate输出实现。

## Multi-Way Representation Alignment（2026预印本v2，22页）

1. 形态：共同坐标对齐方法与多任务验证。[实际全文](https://arxiv.org/pdf/2602.06205v2)。
2. 压力：成对映射的数量和组合不一致。
3. 改变前提：GPA共同正交参考，加共享非线性方向修正GCPA。
4. 来源DOCUMENTED：经典GPA、GCCA、共享latent spaces。
5. 距离：多编码器/语言/模态；分类“stitching”读数是线性probe迁移，并非固定原生LM整段替换。
6. 实证：真实分类、聚类、跨语言/相机/模态检索、增量与噪声对照，非只给恒等式。
7. 界限：GCPA修正不保留严格正交cycle保证；理论约束在retained/orthonormal子空间内，不能当神经计算等价保证。
8. 可借动作：几何保留、组合一致与下游效用分别验证，保留弱consensus下的失败。
9. 对我们：共同参考/一般兼容与质量–跨模型效用分离已有先例；C14增量仍是成熟MoE的参数来源、必要伙伴与实际使用通路干预。

## 从三条结果到下一项：本轮自主推理

C14已经有相近成功的分担差异、R_B性质迁移、同函数/消息的条件使用。下一项不需要再证明任意方向替换能破坏网络。更有信息的缺口是：**一个参数包能带走某种预测性质，是否意味着这种性质通过它的局部响应实现？** 固定gate参数没有固定后续实际路由，因此原参数来源干预未分开这两条通路。

选择交叉R_P/R_B函数来源和两背景产生的真实gate轨迹，保持P骨干、S_P及gate参数不变；用实际路由通路干预区分专家响应、诱导的后续路由变化与来源配合。这里是前向层间通路，不是层内循环或训练动力学。增加此前未使用的55个MMLU学科作预锁主分析，旧两科作严格guard和次分析，避免把旧128题上的一个loss解释不断细化。

学可训练对齐仍有科学用途；本轮暂不选它，理由是同S_P写入基底已被固定，修复器的成功本身不会定位原收益如何实现。新路由干预不依赖拟合成功，竞争解释会给出不同结果，额外成本仅是已有P/B的前向与选择器校准，无新模型训练。完整设计见工作台下一实验卡；本说明不登记新科学结果或提高证据等级。
