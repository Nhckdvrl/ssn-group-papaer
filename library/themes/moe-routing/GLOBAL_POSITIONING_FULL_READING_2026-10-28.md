# 从专家标签到可重用计算：八篇全文再定位（2026-10-28）

范围：本轮完整阅读8篇论文及stitching独立附录，共204页（含参考/数学证明/实验附录/图注与checklist）；关键图另查看。不是全部证明的独立审计，也未复现作者实验。版本、PDF SHA和逐页覆盖见[清单](../../../workbench/mechanism-population-dynamics/moe/notes/PRIMARY_READING_REASSESSMENT_2026-10-28.json)。当前研究判断见[论文形态](../../../workbench/mechanism-population-dynamics/moe/PAPER_SHAPE.md)。

## Monet，ICLR 2025，32页

1. 形态：可解释架构与真实知识控制。2. 压力：小expert数的多义性与SAE替换损失。3. 前提变化：端到端训练细粒度字典。4. DOCUMENTED来源：PEER、product keys、端到端字典学习。5. 距离：HD把上下投影组合，VD同时保留交叉计算；命名expert共享参数，不等于彼此独立MLP。6. 证据：三尺度100B预训练，14域删除、代码语言与毒性干预；不只有routing可视化。7. 限制：self-description仅定性；更强mask有整体损失；路由每4层复用，不能说262K完全独立函数。8. 可借动作：语义选择性需干预与旁损；分开固定参数和实际消息。9. 对我们：已有正面模块化/编辑先例；我们的对象是固定架构的成熟历史、性质载体与必要伙伴及其消息接口。[正式全文](https://proceedings.iclr.cc/paper_files/paper/2025/file/382c35d1a57c07055dfcba58dd39e012-Paper-Conference.pdf)。

## On Linear Mode Connectivity of MoE Architectures，NeurIPS 2025，v2 86页

1. 形态：对称性理论、匹配方法与实证。2. 压力：参数坐标遮蔽低损失连接。3. 前提变化：对齐expert与内部neuron。4. DOCUMENTED来源：Git Re-Basin、OT与功能等价。5. 距离：不仅首层，还含末层、全层替换及shared变体。6. 证据：冻结原骨干、训练MoE，图像/语言与多次run；all-layer LM匹配后barrier约.57–1.17 nat，并非全为零。7. 限制：定理用ReLU/全域等式及generic条件；SMoE定理selected-softmax、shared实验另用全分母；独立/相同初始化的文字口径需区分。8. 动作：置换是工具，路径连通不等于职责同一。9. 对我们：不认领冻结骨干/多init/matching/一般等函数分解；当前native历史与固定函数/消息的角色干预是不同对象。[全文](https://arxiv.org/abs/2509.11348v2)。

阅读校对：按文中式91的反例共同重标，印刷版dense定理的`i<j`差分条件会随编号改变，纯多项式交叉乘已核同。这是字面条件的局部诊断，存在`lmc_literal_condition_check.json`；不当新的研究主张、不否定实证LMC、不把退化反例当真实模型普遍不识别依据。我们不依赖该定理推出现有结论。

## Revisiting Model Stitching，NeurIPS 2021，12+5页

1. 形态：功能比较工具与系统发现。2. 压力：CKA距离不等于下游可用性。3. 前提变化：用低容量对齐后的实际预测定义兼容性。4. DOCUMENTED来源：Lenc–Vedaldi stitching与mode connectivity。5. 距离：1×1卷积/线性层+BN，不能偷换成原样拼接。6. 证据：多架构/初始化/数据/训练时长/监督方式，随机网络对照与finetune容量对照，兼容与改进均测。7. 限制：主要视觉、依赖stitch family与优化，不是所有模块原生自治。8. 动作：区分无对齐重用边界与可对齐功能，不能从raw graft失败断言算法不同。9. 对我们：一般“相同成功可有不同表示/兼容性”不属首次；下一项限制到保留两个几何见证的消息干预，不训练自由adapter。[主文](https://papers.nips.cc/paper/2021/hash/01ded4259d101feb739b06c399e9cd9c-Abstract.html)、[独立附录](https://papers.nips.cc/paper_files/paper/2021/file/01ded4259d101feb739b06c399e9cd9c-Supplemental.pdf)。

## Standing Committee，ACL 2026 main，18页

1. 形态：组织测量框架与功能案例。2. 压力：独立领域专家直觉。3. 前提变化：按跨域rank稳定性/Pareto集合看routed核心。4. DOCUMENTED来源：super experts、representation collapse、group analysis。5. 距离：committee排除架构always-shared；共用编号跨层不代表同一函数。6. 证据：三模型MMLU、C4补充，§4.4/AppendixF有真实mask/reroute后答案变化，不能称routing-only。7. 限制：作者承认缺随机/频率匹配组控制；No Answer显著增加不直接定位语义；Table8 Mean ECI量纲与全softmax定义需澄清，不复用其数值作地板。8. 动作：区分统计稳定组、预测必要性与消息内容。9. 对我们：群体/核心叙事已有先例；我们的识别改变历史与伙伴并固定函数/消息，不重新命名一般联盟。[正式全文](https://aclanthology.org/2026.acl-long.665/)。

## How Modular Is a Frontier MoE，2026 v1，实际PDF 8页

1. 形态：有阳性的因果审计。2. 压力：route family不自动等于能力模块。3. 前提变化：预注册family、随机同大小null、跨语料和指标。4. DOCUMENTED来源：因果中介/电路假说与多语路由。5. 距离：router mask后重新选择/归一化；routed shared-core不等于always-shared。6. 证据：218B Command A+，Arabic明确选择性，其他组依赖读数，含BF16重测。7. 限制：1/3与随机mean+2sd是特定规则；Qwen阳性主要是路由组分离，不能当同效应量的因果校准。8. 动作：保留真实label和KL及完整品质，不用阴性关闭母问题。9. 对我们：不认领第一次反驳routing模块化；研究正常成功实现的历史分担、性质迁移和消息配套。[全文](https://arxiv.org/abs/2606.25092v1)。

## From Observation to Intervention，ICML2026 PhilML workshop，v2 9页

1. 形态：观测代理的因果审计。2. 压力：总体expert分数越级预测单token移除作用。3. 前提变化：当前active集合high/low成对干预。4. DOCUMENTED来源：attention/saliency解释检查与因果层级。5. 距离：单expert×单token，shared不改，与全序列分支不同。6. 证据：三模型60格、逐token权重控制、渐进删除与尾部影响。7. 限制：零假设非等价；Table4控制pW=.019与多重/dual-test口径需谨慎区分，不照搬阈值裁决。8. 动作：总体统计、个体条件作用、稀疏化部署分别定义。9. 对我们：一般route不等于importance已有owner；我们需要解释已被实际干预确认的职责变化，而非再做代理否定。[全文](https://arxiv.org/abs/2606.10703v2)。

## CartesianMoE，v2 16页

1. 形态：分享结构方法。2. 压力：路由错误与expert隔离。3. 前提变化：两个串行非线性MoE子层及残差/独立router。4. DOCUMENTED来源：collective factorization与fine-grained/shared设计。5. 距离：不是简单线性矩阵乘积分解；第二router看中间H。6. 证据：100B/400B、多规模/任务、禁top1后reroute的鲁棒性。7. 限制：无shared是训练架构比较，不能等同推理shared-zero；知识分享是机制解释，未单独识别消息内容。8. 动作：区分可实现结构、训练后实际分担与替代性。9. 对我们：合作可改善部署/路由鲁棒已有方法价值；固定结构中的历史实现与跨来源功能载体仍可直接研究。[全文](https://arxiv.org/abs/2410.16077v2)。

## ExpertWeaver，2026 v1 18页

1. 形态：结构发现与转换方法。2. 压力：dense-to-MoE破坏激活结构。3. 前提变化：GLU神经元slice按激活构建shared/routed。4. DOCUMENTED来源：Moefication、downcycling与GLU稀疏性。5. 距离：CV决定比例，再按mean-absolute分配shared；持续激活不等于恒定输出。6. 证据：training-free pruning、200B CPT/SFT、真实任务和吞吐；不是只有相关。7. 限制：零训练结构剪枝采用无权重求和，CPT后改weighted router；主文42任务与附录48未解，不当自己复现。8. 动作：严格区分mean activation、计算消息和实际职责。9. 对我们：不认领普遍common/specialized分组；问题是相同结构与函数下，训练历史怎样改变消息的可用作用。[全文](https://arxiv.org/abs/2602.15521v1)。

## 本轮实际改变的判断

已有结果有正面价值：组织历史、实际依赖、性质来源与重用被直接连接起来。当前最强故事不是“又有非线性交互”或“多数专家不模块化”，而是选择部署的形成与组件自治/角色实现可以分离。最值得补的决定性识别是：对保持幅度与残差投影的消息替代，历史特有的依赖/配套是否仍在。两个标量仍依赖输入，恢复也不意味着无语义、廉价压缩或唯一单位；损伤也不自动证明语义独占。该实验若只能显示任意方向破坏模型，不能独立支撑更强故事，应回到原三条实证而非扩网格救结果。
