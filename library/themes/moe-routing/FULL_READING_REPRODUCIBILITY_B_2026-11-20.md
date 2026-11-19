# 全文精读 B：跨种子可复现性的三篇近邻 + PRISM 核查（2026-11-20）

服务的候选问题（division 11-20，不是主线）：独立训练的 MoE 语言模型在单个路由决定上大多不一致，但在固定词形内、扣除"同一隐状态上随机路由器"零假设、按完全重跑上限归一后，**分区**可能可复现；自训小模型上这一可复现度随专家数上升（16 → .13，64 → ~.5，256 → .81）。要问：独立运行之间的分歧是**嵌套在共享的粗专家组内部**，还是**横穿**这些组；它如何随专家数和规模移动。

阅读方式：arXiv HTML 全文下载到本地，转成纯文本（公式保留 LaTeX alttext）后逐节读。图只能读图注，图内像素数值读不到；表格数值从 HTML 表格读出。

**一句话结论**
- Tran et al.（LMC of MoE）：对象是参数空间的损失地形，不是路由分区。一对一 Hungarian 匹配（按门控权重或专家权重 Gram 矩阵）后，线性插值的损失壁垒降到朴素插值的约 4–14%；全层替换的 GPT-2 上，残余壁垒随专家数**变大**。没有任何路由一致性或分区测量。对候选问题的认领风险低。
- Tangtartharakul & Storrs（Beyond Routing，视觉 MoE）：10 个种子 × E∈{4,8,16}，把所有专家的 readout 表征几何（强制每张图都过每个专家，不看路由）放在一起聚类，三种 E 下都分成 animate / inanimate 两族。这是"专家族"跨种子稳定，不是"输入分区"跨种子稳定；没有零假设、没有数值化的跨种子一致度。它给"多个冗余专家落进同一粗族"一个定性旁证，不能回答"分歧是否嵌套"。
- Kawata et al.（ICML 2025 理论）：哪个专家专攻哪个簇**完全由初始化决定**（Def. 4.7 / C.1）；需要 M ≳ C log C 个专家才能保证每簇至少一个（Lemma 4.8 / C.2）；专家多于簇时，多个"专业专家"共享一簇，簇之间的路由被证明是干净的（Lemma 4.10 / C.14 / C.15），**簇内谁接数据，理论明确说路由器无法决定**（§C.4 "Adaptive top-k routing"），作者因此改用阈值式 adaptive top-k 绕开。没有任何关于跨种子可复现性的命题，但它的结构直接推出：簇级分区跨种子相同（置换意义下），专家↔簇映射与每簇专家数随种子变，簇内划分无确定性。这正是"分歧嵌套在冗余专家组内"的玩具版本；但它的数据簇内是各向同性噪声、没有更细结构，所以它**预测不出**"可复现度随专家数上升"——这个上升恰好说明真实语言里多出来的专家在切分可复现的细结构，而不是任意切分。
- PRISM（2606.03444）：存在。是多教师蒸馏（DINOv2 / CLIP / SAM → ViT 学生）的条件路由 MoE 方法论文；跨种子只在附录 B 一段 + 一张图：各种子按 teacher–expert 亲和矩阵用 Hungarian 对齐到第一个种子，"qualitatively"同样的结构重现。无数值、种子数未写、路由以教师 ID 为条件（结构被条件输入强加）。与候选问题基本无关。

---

## 卡 1　Tran, Trinh, Bui, Nguyen — On Linear Mode Connectivity of Mixture-of-Experts Architectures（arXiv 2509.11348v2，2025-10-25；带 NeurIPS checklist，录用情况未核对）

**读取**：https://arxiv.org/html/2509.11348 （v2）。**全文已读**：Abstract；§1 Introduction；§2 Preliminaries（2.1 LMC、2.2 MoE）；§3 Group Action（3.1、3.2，Prop. 3.1、3.2，Remark 3.3）；§4 Symmetries and Functional Equivalence（Thm 4.1、4.2，Remark 4.3，§4.2 假设的必要性，k=1 情形）；§5 LMC（5.1 置换充分性，5.2 对齐算法，5.3 Algorithm 1）；§6 Experiments（6.1–6.4）；§7 Conclusion；Table of Notation；附录 A（A.1、A.2，Prop. A.1–A.4，Remark A.5）；附录 B（B.1 ReLU 分片仿射、B.2 Lemma B.3、B.3 Thm B.5 证明 5 步——证明步骤略读、Remark B.6 全读）；附录 C（Def. C.1、Example C.2、Prop. C.3、Thm C.4、Remarks C.5–C.9 全读，证明略读）；附录 D（D.1–D.3）；附录 E（FFN 重初始化）；附录 F（超参）；附录 G（G.1–G.5 的正文与表 5–13，图 5–96 只读图注）；附录 H；NeurIPS checklist。**不可得**：图内曲线数值（只有图注）。

**问题与主张（原文）**
- Abstract："we systematically investigate this phenomenon [LMC] within Mixture-of-Experts (MoE) architectures"；"the symmetries inherent to MoE architectures are fully characterized by permutations acting on both the expert components and the gating function"；"we propose a matching algorithm that enables alignment between independently trained MoEs, thereby facilitating the discovery of LMC"。
- §4.1："The central result of this section is that the symmetries of the gating mechanism are fully characterized by the group action of G(n)"（G(n) = ℝ^d × ℝ × S_n：门控权重/偏置的平移 + 专家置换）。
- §5.1：平移不影响壁垒（Prop. D.1），"only the permutation component τ influences LMC behavior"。
- §7："functional equivalence via permutation symmetries is sufficient to construct low-loss linear paths–when they exist"；"our method does not provide theoretical bounds on the loss barrier"。

**理论部分**
- Thm 4.1（稠密门控）：若两个 MoE 函数相同，且（1）专家函数两两不同、（2）门控权重差 {W_i − W_j} 两两不同，则 n = n′，且存在 (c_W, c_b, τ) 使门控与专家一一对应。Thm 4.2（稀疏 top-k，k>1）：需"strongly distinct"专家（不等集合在 ℝ^d 稠密）与 {W_{i−1} − W_i} 线性无关，结论只在专家被选中的区域成立。
- Remark B.6 / C.8 给反例：违反假设时存在不属于 G(n) 的"spurious / singular symmetries"（例如两个专家永远不被同时选中时的门控缩放）。§4.2 与 Remark C.9：k = 1 时多出正标量缩放对称 ℝ_{>0}，作者"do not consider k = 1 in our primary results"。
- 注意：理论刻画的是**函数完全相同**时的参数关系，不涉及训练是否收敛到同一函数；所以它对"独立训练是否学到同一分区"没有预测。

**设置**
- 预训练 Transformer（ViT：MNIST/CIFAR-10/100/ImageNet-1k/ImageNet-21k→CIFAR；GPT-2 12 层 768 维：WikiText103、One Billion Word），把第一层 / 最后一层 / 全部层的 FFN 换成**随机初始化**的 MoE，**冻结其余所有参数，只训练 MoE 层**（§6.1，附录 F）。
- 变体：稠密 MoE；SMoE top-2；DeepSeekMoE（top-2 + 1 共享专家）。专家数 2/4/6/8/16。专家为单隐层 MLP。
- 独立运行数：§6.2 每配置 3 个模型（3 对）；Table 7 为 4 个 checkpoint（6 对）；Table 2/8/9 为 10 对（"repeated five times"）；Table 10 为 3 对；Table 12/13 为 5 个模型 10 对。
- 不一致之处：§6.2 写 "three independently initialized models"，附录 G.1 写 "All models were fine-tuned from identical random initializations"，G.1 末段又说 LMC 成立 "when alignment in initialization and architecture is preserved"。"独立"指不同初始化还是只是不同数据顺序，原文自相矛盾，**未能核对**（代码库未看）。

**测量与对齐**
- 壁垒（Eq. 1）：B(θ_A, θ_B) = sup_t [L(tθ_A + (1−t)θ_B) − (tL(θ_A) + (1−t)L(θ_B))]，25 个等距插值点；另报 loss / accuracy 的 AUC（相对端点连线）。
- 对齐（Algorithm 1，**只在权重上，不用数据、不用路由**）：第一步，专家顺序的一对一置换，用 LAP / Hungarian 求解，代价两种：（Method 1）去中心化门控权重与偏置的欧氏距离（Eq. 10）；（Method 2）专家权重的 Gram 矩阵差 ‖Ã_iᵀÃ_i − Ã′_jᵀÃ′_j‖_F 与 ‖B̃_iB̃_iᵀ − B̃′_jB̃′_jᵀ‖_F（Eq. 11，对隐单元置换不变，Prop. D.2）。第二步，对每对匹配的专家做 Git Re-Basin 的 weight matching 对齐隐单元。**严格一对一**，没有多对一或软匹配。
- 匹配质量（§6.3）：4 专家时枚举全部 24 个置换，报所选置换的 Rank 与 L̂ = (L_method − L_top1)/(L_naive − L_top1)×100。

**基线 / 零假设**：朴素插值（不对齐）；"Skipping-Expert-Order Matching"（只做专家内对齐、不重排专家，Table 10）；24 个置换的穷举（Table 2）。没有"随机置换"或"随机初始化"类零假设。

**主要结果（含数字）**
- §6.2 / Table 1 / Fig. 1：第一层替换，所有数据集与变体上曲线"consistent low-loss"；最后一层"less pronounced"；作者归因于浅层"strongly shape the solution basin"。Table 1 只列配置，数值在图里。
- Table 2（ViT 12 层，4 专家）：Expert Weight Matching 的 Rank 2.1–4.6（24 个中），L̂ 0.07–3.42；Gate Weight Matching Rank 2.6–4.2，L̂ 0.09–3.42。替换层越深 L̂ 越小（CIFAR-10：层 1 2.12 → 层 12 0.13）。即所选置换通常不是最优的那一个，但接近最优。
- Table 10（One Billion Word，12 层，全量匹配 vs 跳过专家重排）：壁垒 0.0044–0.0066 vs 0.14–0.86 nats；中点 loss ≈ 3.44。
- Table 7（**全部层**替换）：WM 壁垒 vs 朴素壁垒（×10²）。ViT 上 WM 约为朴素的 10–12%（例：CIFAR-10 6 层 4 专家 5.42 vs 47.47）。GPT-2 One Billion Word：稠密 MoE 2/4/6/8 专家的 WM 壁垒 56.82 / 68.76 / 78.44 / 93.23（即 0.57→0.93 nats，单调增），朴素 400–477；SMoE 4/8/16：72.31 / 79.86 / 98.68（朴素 492–618）；DeepSeekMoE 4/8/16：64.06 / 117.42 / 72.94。**全层设置下残余壁垒远非零（约 0.6–1.2 nats），且稠密与 SMoE 随专家数上升。**
- Table 3 / 11（CIFAR-10，2/4/6 层，替换每个位置）：WM / 朴素的壁垒比 2.4%–14.4%；没有清晰的随层位置单调趋势。
- 附录 E / Table 4：只重初始化一层 FFN 再微调，在 IMDB / AGNEWS / DBPedia / EnWik8 / PTB 上，两个不同种子微调模型之间的**朴素**壁垒已经只有 0.0003–0.045——作者自己指出这可能只反映"the reinitialized state is already highly functional and located within the same ... basin"。

**作者陈述的局限**：没有壁垒的理论界（§7）；k = 1 留待以后（§4.2）；理论只处理门控对称、把专家当黑箱（Remark 4.3、A.5）。

**我的评估**
- 结论范围窄：只训练一层（或全部 MoE 层）而 backbone 冻结、专家数 ≤ 16、主要是首层替换。冻结 backbone 意味着 MoE 输入分布在不同运行间完全相同，这是"独立训练模型"里最有利于对齐的情形。
- G.1 "identical random initializations" 的说法若属实，则多数实验根本不是独立初始化，LMC 的含义大幅缩水。
- 全层 GPT-2 的残余壁垒 0.6–1.2 nats 并不小（中点 loss ≈ 3.4–3.5），而作者在正文用 "LMC persists in all cases" 概括；壁垒随专家数增大与"更多专家更难一对一对齐"一致。
- 没有任何关于路由的测量：不比较两模型在同一 token 上选哪个专家，也不比较分区。

**与候选问题的关系**
- 他们拥有：MoE 的门控对称群刻画（k>1）；按权重一对一匹配专家后的 LMC 现象（小专家数、冻结 backbone）。
- 他们没碰：路由层面的一致性、分区可复现性、多对一 / 嵌套结构、随机路由零假设、上限归一化、专家数 > 16。
- 对"可复现度随专家数上升"：**间接相反的信号**——在他们的权重一对一匹配框架里，专家越多，对齐后的残余壁垒越大（Table 7 GPT-2）。这与我们的结论不冲突（对象不同：一对一权重身份 vs 置换不变的输入分区），反而可以当对照叙述："按专家身份一对一对齐随专家数变差，而分区可复现度随专家数变好"——前提是我们自己测出前者。
- 对"分歧嵌套在冗余专家组内"：无证据。一对一 Hungarian 在构造上无法表达多对一，所以他们的框架看不见嵌套。
- 压缩风险（compression risk）：低。审稿人可能说"LMC 已经说明独立 MoE 等价到置换"，回应是：他们的结果只在冻结 backbone + ≤16 专家下成立、全层时残余壁垒非零且随专家数增大，并且从未测量路由。

---

## 卡 2　Tangtartharakul & Storrs — Beyond Routing: Characterising Expert Tuning and Representation in Vision Mixture-of-Experts（arXiv 2605.20610，2026）

**读取**：https://arxiv.org/html/2605.20610 。**全文已读**：Abstract；§1 Introduction（含 3 条贡献）；§2 Related Work（三小节）；§3 Sparse Contrastive MoE-CNN（Model Architecture、Gating Network、Losses、Training、Inference Dataset: THINGS）；§4 Results（Probing Specialisation Through Routing、Expert-Level Tuning + Table 1、Separability Analysis、Representational Stability Across Instantiations）；§5 Discussion（含 Limitations、Future Avenues）；附录 A.1–A.4；附录 B.1；附录 C（Fig. S1–S4 图注、Table S1 全部数值）。**不可得**：图 2/3/5/6、S3（silhouette 曲线）、S4 的图内数值——silhouette 分数没有在正文或表中给出数字。

**问题与主张（原文）**
- Abstract："routing alone does not reveal what each expert actually encodes"；"we use tuning and representational similarity analysis to assess the stability of expertise-allocation across independent initialisations. We find that an animate–inanimate distinction dominates expert partitioning, apparent from gating through to expert readout, and is stable across independently trained models."
- §1 贡献 3："Across independently trained models (E ∈ {4,8,16}, 10 seeds each), we identify representational motifs that re-emerge reliably using second-order RSA and silhouette-based cluster selection."
- §4 末："This suggests that the partition is stable both across model configurations and across independent instantiations."

**设置**
- ResNet 式 CNN，5 个卷积块 + 3 层 MLP readout；前 3 块共享，后 2 块 + readout 复制成 E 个专家；**E ∈ {4,8,16}，top-k = 2**；门控 = 3×3 conv + GAP + FC，noisy top-k（Shazeer）；重要度 CV² 负载损失（权重 0.1）。
- **总参数固定约 46M**：专家通道宽度按 1/√E 缩放（128 / 90 / 64），所以 E 增大时每个专家更窄（§3、A.1）。这与常见 MoE（加专家 = 加参数）不同，作者在 Limitations 里承认。
- 自监督 SimCLR（NT-Xent，τ = 0.5），STL-10 unlabeled 100k 张 96×96，100 epoch，batch 256，Adam 3e-4，cosine。
- 推断：STL-10 test（8k）与 THINGS（26,107 张 / 1,854 概念；THINGS Similarity 的 66 维人类行为维度，每概念一张代表图）。
- 独立运行：每个 E 训练 10 个不同种子（A.1：3 个示例配置 + 每配置 10 个独立实例，约 115.5 GPU 小时）。变化的只有随机种子。

**测量**
- 路由：每个专家接收的 STL-10 各类比例热图（Fig. 2b，每个 E 只展示一个模型）；最大门控 logit 的样本。
- MEI：强制每张图通过每个专家（绕开路由器），以 readout 的 ‖z_i‖₂ 排序。
- 维度回归（A.2）：66 维 THINGS 嵌入 → 每个专家的门控 logit 或 readout 范数，非负 Lasso，嵌套 5×5 交叉验证，报 r²。
- 类别可分性（A.3）：每个专家 readout 上的两两逻辑回归，5 折 balanced accuracy。
- **跨种子稳定性（§4 最后一节，A.4）**：对每个专家（强制通过，不看路由）在 1,854 张 THINGS 代表图上算一阶 RDM（欧氏距离，1854×1854）；所有 (模型 × 专家) 的 RDM 上三角两两 Spearman 相关 → 二阶相似矩阵；平均连接层次聚类，簇数 2–15 网格搜索取 silhouette 最大。**没有专家之间的一对一匹配**：是把 10 个模型的全部专家一起聚类，属于多对一 / 族归属的读法。
- 路由一致性（B.1）：同一张图两个增强视图选中同一对专家的比例（模型内，不是跨种子）。

**基线 / 零假设**：只有 B.1 的偶遇基线 1/C(E,2)。跨种子 RSA 聚类**没有任何零假设**（没有未训练 / 随机初始化专家的 RDM、没有打乱、没有同模型内专家间相似度作为参照），silhouette 数值未报。

**主要结果**
- 路由（Fig. 2）：E=4 时出现"pairs of experts with similar routing proportions"；E 增大时成对不明显，但专家倾向接收以 animate 或 inanimate 为主的输入。
- 门控 vs readout：Table 1（E=4）门控 r² .416–.538，readout r² .125–.200；Table S1：E=8 门控均值 .467（.374–.545），readout .159（.085–.283）；E=16 门控 .387（.253–.553），readout .224（.097–.350）。门控 logit 与 readout 范数无线性关系（Fig. 4、S1）。readout 的主导维度是形状 / 颜色 / 纹理（"fine-grained pattern"、"repetitive/spiky"、"long/thin"），门控的主导维度更接近类别（animal-related、house/furnishing、electronics）。
- 可分性（Fig. 5）：所有专家都能分 animate / inanimate，同一 animacy 内也能分但较弱；"representational geometries were strikingly similar across experts despite their divergent MEIs"。
- **跨种子**（Fig. 6，E=4；Fig. S4，E=8/16；Fig. S3 silhouette）：silhouette 选出 2 簇，一簇 animate / organic / 不规则纹理，一簇 inanimate / artificial / 几何结构；"the same split also predominates in the eight- and sixteen-expert configurations ... even though top-k = 2 does not consistently select the same pair of experts"。
- B.1：两增强视图同对专家比例 79.27%（±2%）/ 58.32%（±4%）/ 45.30%（±2%），对应 E = 4/8/16；偶遇 16.66% / 3.57% / 0.83%。**原始一致率随 E 下降，相对偶遇的倍数随 E 上升（约 4.8× / 16× / 55×）。**

**作者陈述的局限**（§5 Limitations）：专门化依赖训练集图像统计（STL-10 小、类别预定义）；目标函数可能改变专门化；固定总参数、随 E 缩窄专家"atypical in MoE practice"，可能不推广到大规模工业 MoE。

**我的评估**
- 标题里的"partition stable across instantiations"其实是**专家表征族**稳定：RDM 是强制所有图片通过每个专家算出来的，与路由器把哪些输入分到一起无关。跨种子的输入分区（哪些图片被分到同一组）从未比较。
- 两簇结论没有零假设：同一模型内各专家几何已"strikingly similar"，而 animacy 是 THINGS 上任何视觉表征的最大方差轴（作者自己这么解释）。若随机初始化的专家、或共享 backbone 本身的 RDM 也给出同样的两簇，结论就只是"数据的主轴"。silhouette 值未报，无法判断两簇是否明显优于一簇或多簇。
- 只有一层门控、单一 CNN、单一数据集；k=2 且专家随 E 变窄，E 的效应与专家容量的效应纠缠。
- B.1 是一个干净的小观察：原始一致率与偶遇归一后的一致率随 E 的方向相反。这提醒我们：任何"随专家数上升"的结论都必须说清用的是哪种归一。

**与候选问题的关系**
- 他们拥有：视觉 MoE 中"专家跨种子落入少数几个稳定的表征族（animate / inanimate）"的定性观察，在 E = 4/8/16 下都成立；路由统计与专家编码不一致。
- 他们没碰：语言 / token 级路由；跨种子的输入分区比较；固定 token 身份；零假设与上限归一化；分歧是否嵌套于族内；大专家数（>16）。
- 对"可复现度随专家数上升"：没有直接测量。B.1 的偶遇归一一致率随 E 上升，与我们的方向同向，但那是模型内两视图，不是跨种子。
- 对"分歧嵌套在冗余专家组内"：**定性旁证**——E 增大时每个模型有更多专家，但跨种子仍只聚成两族，意味着每族内有多个可互换的专家，"哪个专家"随种子变而"哪一族"不变。这与嵌套图景一致，但他们的证据是专家表征相似，不是输入分配；不能代替我们的测量。
- 压缩风险：中等偏低。审稿人可能说"粗分区跨种子稳定已有人报过"；回应：他们是视觉 CNN 单门控、表征族而非输入分区、无零假设无数值；我们是语言模型 token 级、词形固定、随机路由器零假设、上限归一、并且问的是分歧的**位置**（族内还是跨族）及其随专家数的移动。应在定位表中把它列为"粗族稳定"的视觉近邻并引用。

---

## 卡 3　Kawata, Matsutani, Kinoshita, Nishikawa, Suzuki — Mixture of Experts Provably Detect and Learn the Latent Cluster Structure in Gradient-Based Learning（arXiv 2506.01656，ICML 2025）

**读取**：https://arxiv.org/html/2506.01656 。**全文已读**：Abstract；§1（Contributions、Notation）；§2 Related Works；§3 Problem Setting（3.1 Def. 3.1、Assumption 3.2、3.3；3.2 MoE 结构、Assumption 3.4；3.3 Algorithm 1 四阶段）；§4 Main Results（4.1 Example 4.1、Remark 4.2、Thm 4.3、Lemma 4.4、4.5；4.2 Thm 4.6、Experiments、Def. 4.7、Lemma 4.8、4.9、4.10、Remarks 4.11、4.12、Phase III/IV 叙述）；§5 Conclusion（含 Implications and Future Directions）；附录 A（A.1 Hermite、A.2 不等式、A.3 激活函数 Lemma A.5、A.6）；附录 B（Def. B.1、Remark B.2、Assumption B.3、证明大纲、B.1–B.4 的引理陈述；证明推导略读）；附录 C（总大纲与常数次序；C.1 Def. C.1、Lemma C.2 及其证明全读、Cor. C.3、Remarks C.4、C.5；C.2 Lemma C.6–C.13 陈述，证明略读；C.3 Lemma C.14–C.16 及证明的文字部分；C.4 Re-initialization、Lemma C.17、Def. C.18、Remark C.19、Adaptive top-k 段落与 Lemma C.20 全读、Lemma C.21–C.26 陈述；C.5 Lemma C.27–C.29 及 C.28 证明）。**不可得**：Fig. 1/2 的图内数值（只有图注）。长代数推导（C.2、C.3、C.4 中的上下界逐项估计）只核对了结构没有逐行验算。

**问题与主张（原文）**
- Abstract："we prove that a vanilla neural network fails in detecting such a latent organization as it can only process the problem as a whole ... we show that a MoE succeeds in dividing this problem into easier subproblems by leveraging the ability of each expert to weakly recover the simpler function corresponding to an individual cluster."
- §1："while the mechanism of the initialization, the optimization procedure and the behavior of the router are essentially the same for each expert, it has been repeatedly reported that each expert ultimately specializes in its own way ... It is still unclear why such phenomenon happens and why the router can learn to fairly distribute an input to appropriate experts without collapsing to a single expert."

**设置（数据与模型）**
- 数据（Assumption 3.2）：C = O(1) 个簇，c ~ Unif[C]；x_c ~ N(ρ v_c, I_d)，ρ ≃ polylog d（簇均值范数远小于噪声范数 √d，Remark 4.11）；y_c = f*_c(w*_cᵀx) + s_c g*(w*_gᵀx) + ν。f*_c 是簇局部单指标任务，g* 是全局任务，Σ_c s_c = 0（制造簇间梯度抵消）；信息指数 k* > 2 且为偶数，所有 f*_c 与 g* 同信息指数、首个 Hermite 系数绝对值相同。Assumption 3.3：特征方向近似正交（Õ(d^{-1/2})），v_c 与所有 w* 正交。
- **簇内没有更细结构**：簇内输入就是各向同性高斯噪声加均值。
- MoE（§3.2）：M 个专家，每个是宽 J 的两层网络；线性门控 h(x) = Θᵀx，**初始化为 0**。Phase I/II 用加 softmax 权重的 top-1（F_1），Phase III/IV 用阈值式 adaptive top-k：F̂_M(x) = Σ_m 1[h_m(x) ≥ 0] f_m(x)。
- 训练（Algorithm 1）：Phase I 归一化 SGD 只训专家第一层（路由均匀，每个专家以 1/M 概率收到任一数据）；Phase II 一步大批量（n = Θ̃(d)）只训门控；Phase III **重初始化专家**后再训第一层；Phase IV 第二层岭回归。
- 实验（§4.2 "Experiments"）：C = 2，f*_1 = He₃ + He₅，f*_2 = He₃ + He₄，g* = He₃，d = 200，**M = 8 个专家**（冗余），隐宽 500，lr 1，T₁ = 3.5×10⁶，T₂ = 300，T₃ = 10⁷。只有对齐度图（Fig. 1/2），没有数值表，没有多种子。

**与问题直接相关的定理 / 定义（逐条）**

(a) **哪个专家专攻哪个簇，由什么决定**
- Def. 4.7 = Def. C.1："(j*_m, c*_m) := argmax_{j,c} w⁰_{m,j}ᵀ w*_c，M_c := {m | c = c*_m}"。原文称之为 "a definition of the set of professional experts that depends on initialization"（§C.1 开头）。即：专家 m 的命运由其 J 个神经元在**初始化时**与各簇特征方向 w*_c 的最大内积决定。
- §4.2.2："At the initial state, experts are divided based on the task of the cluster with which they exhibit the highest alignment." "At the initialization, the inner products only differ by a constant. However, when two sequences have initial values that differ by a constant factor, this can cause differences in their growth rates, ultimately placing them in different asymptotic orders."
- Lemma 4.9 / C.6（formal）："Consider the expert m ∈ M_c"——**M_c 中每一个专家**都弱恢复 w*_c（κ ≥ a₂），其余神经元与方向保持 Õ(d^{-1/2})。Phase I 中路由是均匀的（θ = 0），所以分工完全来自初始化的不对称被梯度流放大，而不是来自路由器的竞争。
- Lemma 4.10 / C.15：Phase II 一步之后，对 m ∉ M_c，θ_mᵀv_c ≤ −Ω̃(1)；m*_c := argmax_m h_m(v_c) ∈ M_c 且 θ_{m*_c}ᵀv_c ≥ Ω̃(1)。证明用到 Lemma C.16：Σ_m θ_m = 0（门控初始为零 + softmax 梯度和为零）。路由器"读"的是专家的弱恢复差异："the router leverages these differences in recovery, which are reflected in the gradients, as a signal"（§4.2 Experiments）。
- Lemma C.14："any m ∉ M_c satisfies h_m(x_c) − max_{m′} h_{m′}(x_c) < 0 with high probability"。

(b) **需要多少专家**
- Lemma 4.8："If M ≳ C log C, it holds that P[|M_c| ≥ 1, ∀c] ≥ 0.999"；并要求 √log d ≳ J ≳ C⁻¹ log M。
- Lemma C.2（精确版）：M ≃ C log(C/δ) 时，以概率 ≥ 1−δ 每簇至少一个专业专家。证明（Eq. 104–105）："By the symmetry, P[|M_c| ≥ 1] ≥ 1 − (1 − C⁻¹)^M"，并对 c 取并集界——即**每个专家独立、等概率（1/C）落入某一簇**，这是优惠券收集问题，所以需要 C log C。
- §5："the number of experts is typically chosen heuristically in practice"——没有给出"多于 C log C 是否有益"的结论。

(c) **专家多于簇时（冗余专家）**
- 多个专家共享一簇：|M_c| 是随机的（按上面的对称性，近似多项分布 Multinomial(M, 1/C)），M_c 两两不交（§4.2.2 Phase III："M_c ∩ M_{c′} = ∅"）。
- **簇内谁接数据，理论不决定**。§3.2："After Phase II with top-1 routing, a data point x_c is no longer routed to experts outside the set of professional experts ... however, competition among the professional experts may still occur. In general, this can result in issues related to load imbalance or the emergence of redundant experts"。§C.4 "Adaptive top-k routing"："the router does not route data to experts where m ∉ M_c; however, it cannot definitively determine which expert among those where m ∈ M_c should receive the data. Therefore, resolving conflicts within m ∈ M_c without knowing M_c or v_c requires an alternative approach."
- Remark 4.12：固定 k 的 top-k 会出错——k > |M_c| 时会把 x_c 送进别的簇的专家，k < |M_c| 时可能没有一个 M_c 中的专家被稳定选中；因此改用阈值 h_m ≥ 0。
- Lemma C.20："There is at least one m ∈ M_c such that f_m is correctly routed with high probability"；"f_{m′} is never chosen for all m′ ∉ M_c"。只保证**至少一个**，并不说 M_c 中哪些、多少个满足 h_m ≥ 0。
- Lemma C.28 证明："we may have superfluous experts m′ ∈ M_c \ {m}. However, we only need to put a*_{m′j} = 0"——多余专家在可行解构造中被直接置零，理论不刻画它们最终学到什么。
- §5 Implications："to prevent competition among professional experts, we employed top-k routing to reduce potential load imbalance"；"freezing or pruning redundant experts may further alleviate competition"。
- Phase III 重初始化专家（§3.3、§C.4）："While not strictly necessary, this reinitialization helps ensure that the early learning of w*_c does not interfere with ... w*_g"。

(d) **对跨随机初始化可复现性的预测**
- 论文**没有任何**关于不同种子之间比较的命题或实验。以下是从定理结构直接推出、作者未写的含义（标为我们的推论）：
  1. 簇级的输入分区在成功事件下跨种子相同（置换意义下）：x_c 只去 M_c，M_c 两两不交，而簇本身由数据决定（v_c）。
  2. 专家↔簇映射跨种子任意：每个专家以 1/C 等概率落入某簇（Lemma C.2 证明的对称性）。
  3. 每簇专家数 |M_c| 跨种子随机变化。
  4. 簇内划分无确定性：理论上路由器无法区分 M_c 中的专家；若用固定 top-1，簇内分配由 θ_mᵀz（噪声方向）和负载决定，因为数据在簇内没有结构可分。adaptive top-k 下，簇内哪些专家激活也未被刻画。
  → 在这个模型里，**跨种子的专家级分歧全部嵌套在簇级组内，不会横穿簇**；这是"嵌套"图景的玩具证明，但前提是数据簇内无结构。

**基线**：理论对照是普通两层网（单专家，Thm 4.3：在 Example 4.1 下对 w*_g 的对齐度 sup_t |wᵀw*_g| ≲ Õ(d^{-1/2})，即学不到全局任务）；复杂度对照：单指标模型 Õ(d^{k*−1})（Arous et al.）、核岭回归 Õ(d^{p*})。

**主要结果**：Thm 4.6：J = O(ε⁻¹)、T₁ = Θ̃(d^{k*−1})、T₂ = 1 且 n = Θ̃(d)、T₃ = Θ̃(d^{k*−1} ∨ dε⁻² ∨ ε⁻³)、T₄ = Θ̃(ε⁻²) 时，以概率 ≥ 0.99，E|F̂_M − f*_c − s_c g*| ≤ ε；总样本复杂度 Õ(d^{k*−1})，与学单个单指标模型相同。实验图：Phase I 后 "differences among experts arise due to initialization"，Phase II 路由按簇分发，Phase III 每个专家学到局部 + 全局任务。没有专家数、宽度、层、训练时长的扫描。

**作者陈述的局限 / 开放问题**（§5）：是否达到信息论极限未知；专家数在实践中是启发式选的；建议梯度感知路由、按 token 自适应 k、冻结或剪掉冗余专家、上循环（upcycling）。

**我的评估**
- 分阶段算法（分层训练、门控一步、专家重初始化、阈值路由）离真实 MoE 训练很远；"专业专家由初始化决定"是在**路由先冻结为均匀、专家先独立探索**的设定下成立的。真实训练里路由与专家同时更新，负载均衡损失会改变"谁专攻谁"，这一点理论未覆盖。
- 冗余专家的处理是绕开而非解决：adaptive top-k 让 M_c 内所有 h_m ≥ 0 的专家同时激活，所以"簇内划分"在其模型里根本没被定义为一个结果。
- 关键的建模选择——簇内是各向同性噪声——使"冗余专家如何切分一个簇"必然是任意的。真实语言数据是层级的（词形内部还有语境 / 用法结构），因此这一理论不能拿来预测真实 MoE 中冗余专家的切分是否可复现。

**与候选问题的关系**
- 他们拥有：MoE 专家专门化由初始化不对称 + 梯度放大决定的理论机制；C log C 的专家数门槛；冗余专家共享一簇、簇内路由不确定。
- 他们没碰：跨种子比较；专家数超过门槛后的效应；簇内有结构的数据；真实语言模型。
- 对"可复现度随专家数上升"：理论只给出一个随专家数变化的量——覆盖概率 1 − M(1 − 1/C)^M（M < C log C 时有簇没有专家，簇级分区就不可复现）。超过门槛后，按其模型，额外专家只会增加簇内任意切分；若我们的测量对簇内切分敏感，它预测可复现度**不升反降**或持平。我们看到的 .13 → .5 → .81 因此是与该玩具模型不同的现象，正好构成一个可检验的分叉：(i) 低专家数时处在"覆盖不足"区（类似 M < C log C，粗组都没被稳定占据）；(ii) 高专家数时多出来的专家切分的是数据中可复现的细结构，而不是任意切分。两者在嵌套分析中给出不同签名：(i) 下分歧横穿粗组，(ii) 下分歧被嵌套且残余随专家数下降。
- 对"分歧嵌套在冗余专家组内"：**直接的理论支持（玩具模型）**——专家级分歧全部来自冗余专家组内部，簇之间路由干净。可在论文里作为先验预测引用："Kawata et al. 的模型预测分歧只在冗余组内；我们问真实模型是否如此、组内残余是否任意。"
- 压缩风险：低。它是理论文，不测量任何真实模型；但"专业专家由初始化决定、冗余专家竞争"这一表述需要在相关工作中认领给他们（以及其依据 Chen et al. 2022）。

---

## 卡 4　PRISM — Synergizing Vision Foundation Models via Self-organized Expert Specialization（arXiv 2606.03444；Tang, Li, Zhang, Song, Yu, Yang，HUST；ICML 关键词）

**核实**：论文存在，标题如上，代码 github.com/robotyingtang/PRISM-VFM。**它不是关于跨种子 MoE 结构的论文**，而是多教师蒸馏方法论文；跨种子内容只在附录 B 一段 + Fig. 7。按任务要求，不作完整精读卡；但实际已读完全部正文文字与全部附录文字（Abstract；§1–§3.5；§4.1–4.5；§5；附录 A–G），只是表格数值未逐一抽取。

**内容**：ViT-B/16 学生，第 2/5/8/11 层把 FFN 换成"双流"块：稠密 Universal Anchor + 条件 MoE（N = 15 个专家 top-3 + 1 个内部共享专家），路由前用 FiLM 注入 context ID（Stage 1 = 教师 ID：DINOv2-L / CLIP-L / SAM-L；Stage 2 = 下游任务 ID），浅层加 locality-aware 去相关损失。ImageNet-1k Stage 1 蒸馏 30 epoch，PASCAL-Context / NYUD-v2 多任务微调；PASCAL-Context Δm = 2.29%（SAK 0.83%），ViT-L 3.16%（SAK 2.30%）。

**跨种子部分（附录 B 原文）**："Since MoE expert indices are permutation-invariant, we align non-reference seeds to the first seed with Hungarian matching before comparison. Figure 7 shows that the same qualitative teacher–expert affinity structure consistently re-emerges across random seeds." "In early and middle layers, teacher-preferred partitions are sharp ... In the deepest layer, routing becomes more mixed and shared." Fig. 7 图注："Non-reference seeds are aligned to the first seed using Hungarian matching ... the same qualitative specialization structure consistently re-emerges across seeds up to permutation."
- 对齐对象：teacher–expert 路由频率亲和矩阵（3 个教师 × 15 个专家），一对一 Hungarian。
- 种子数**未写**；没有任何数值指标、没有零假设。
- 内部不一致：附录 B 说早 / 中层分区锐利、最深层混合；附录 G 图注说第 2 层"broad and diffuse"、第 8/11 层"sharp, context-dependent specialization"。

**与候选问题的关系**：几乎无关。路由由教师 ID 条件输入，"结构"是被条件强加的（专家按教师分开本来就是训练信号的直接后果），且仅定性、单张图。可在相关工作中一句带过（"条件路由的多教师 MoE 中，Hungarian 对齐后教师–专家亲和定性重现"），不构成认领风险。

---

## 汇总：对候选问题的定位

| 论文 | 比较对象 | 对齐方式 | 零假设 / 上限 | 专家数依赖 | 对"随专家数上升" | 对"分歧嵌套" | 压缩风险 |
|---|---|---|---|---|---|---|---|
| Tran et al. 2025 | 参数插值的损失壁垒 | 权重上一对一 Hungarian（门控或 Gram） | 朴素插值、跳过重排；无随机零假设 | 全层 GPT-2：残余壁垒随专家数增大（0.57→0.93 nats，2→8） | 间接反向（一对一身份对齐随专家数变差） | 框架看不见（一对一） | 低 |
| Tangtartharakul & Storrs 2026 | 专家 readout 表征几何（强制通过） | 不匹配，全体专家二阶 RSA 聚类 | 无 | E = 4/8/16 都是两族；偶遇归一的视图一致率随 E 升 | 无直接测量 | 定性旁证（多专家落入同族） | 中偏低 |
| Kawata et al. 2025 | 理论，无跨种子 | — | — | M ≳ C log C 才覆盖所有簇 | 超过门槛后预测不升（簇内切分任意） | 玩具模型中严格嵌套 | 低（需认领"初始化决定专业专家"） |
| PRISM 2026 | 教师–专家亲和 | 一对一 Hungarian | 无 | 无 | 无 | 无 | 极低 |

**留给我们的空白（在这四篇里都没有）**：语言模型 token 级、固定词形的跨种子分区比较；随机路由器零假设 + 完全重跑上限；分歧位置的分解（粗组内 vs 跨组）；专家数从 16 到 256 的扫描；Kawata 式"冗余组内任意切分"与"细结构可复现切分"两种机制的区分。

**一个可直接用的判别式（来自卡 3 的推论，未实验）**：若高专家数下的跨种子残余分歧在粗组内部且对组内细分的上限归一可复现度随专家数上升，则与 Kawata 玩具模型的"组内任意"相反，说明多出的专家切的是数据里可复现的结构；若组内残余是任意的（接近组内随机分配零假设），则专家数带来的上升只来自粗组被更稳定地覆盖。两种结果都可报告。

**未核对 / 不确定**
- Tran et al. 的"独立训练"是否真用了不同初始化（§6.2 与 G.1 矛盾）。
- Beyond Routing 的 silhouette 数值、两簇相对一簇 / 三簇的优势大小（只在图中）。
- PRISM 的种子数。
- Kawata et al. 附录 C.2–C.4 的逐项代数估计未逐行验算，只核对了定理陈述与证明结构。
