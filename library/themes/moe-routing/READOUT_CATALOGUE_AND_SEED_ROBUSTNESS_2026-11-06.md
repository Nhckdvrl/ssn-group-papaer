# 现成专家分析读数目录 + 专家几何度量 + 相邻领域"换 seed 什么重现"（2026-11-06）

**用途：**给 division 主会话挑下一组实验（E174 第二尺度、"已发表结论跨 seed 稳不稳"）。三张表 + Equifinality / Geometric Routing 的压缩风险精读。只写定位，不做新颖性判决（AGENTS.md R6）。
**证据标签：**`[全文]` 读了全文；`[节]` 只读了相关节（节号 / 页码写在格里）；`[摘要]` 只读了摘要；"未核对" = 没拿到原文。原话均为英文原句摘录。PDF 在会话 scratchpad，未进仓库。

**我们手里有什么（决定"能否 CPU 复算"）：**
- 路由缓存 `~/mechpop_cache/e167_analysis/routing/<run>__ckpt_<t>.npz`：每层 `S_l` = 29,551 个抽样词 × top-8 专家 id，外加配对统计 `C/B/Kh`；10 个 run 目录 × 每个 6–10 个 checkpoint（0 → 40 亿 token）。
- hidden 缓存：`H_l`（113,118 个连续词 × 768，即路由器输入）+ 路由器 `W_l, b_l`；8 个 run 的终点 + 2 个未训练 ckpt_0。可用 `H·W` 重算**全部连续 token** 的路由概率。
- UD 标注 `division/results/e167/ud_annotations.json`：逐词 UPOS / deprel / feats / 前后词类 / **genre（EWT 5 体裁）** / doc_id。
- checkpoint `.pt`（每个 1.5 GB，CPU 可载入）：专家权重、路由器、unembedding。functional 缓存：`route_fp`（12 层 × 2 × 35 类 × 64 专家）。
- **没有的：**多语数据、领域标签细于 EWT 体裁的语料、生成 rollout、专家输出向量缓存（要前向）。

## 表 1. 现成专家分析读数目录（21 种）

"CPU" 列：**能** = 只用上面的缓存 / checkpoint；**部分** = 一半能、一半要前向；**GPU** = 要模型前向（或反向）；**新数据** = 要我们没有的语料。

| # | 论文（证据） | 单位 | 定义 | 基线 | 原文结论（原话 + 位置） | CPU | 复算输入 |
|---|---|---|---|---|---|---|---|
| 1 | OLMoE 2409.02060 §5.1 `[节]` | token × top-k | 路由饱和 = (1/N)Σ\|E_i^(t)∩E_i^(T)\|/k，中间 ckpt 与终点比 | 随机 8/64 = 12.5% | "after 1% of pretraining (5000 steps or 20B tokens), up to ∼60% of routing to the top-8 activated experts has already saturated"（p.18） | **能** | `S_l` 各 ckpt；可加跨 run 版（先配对） |
| 2 | OLMoE §5.2 `[节]` | 专家对 | 共激活 N_{Ei,Ej}/N_{Ei} | 无 | "there is no strong co-activation among experts in one layer, with only few exceptions"（p.19） | **能** | `S_l` |
| 3 | OLMoE §5.3 `[节]` | 专家 × 领域 | 领域专精 N^(k)_{Ei,D}/N_D | 随机 12.5%（OLMoE）/ 25%（Mixtral） | "Mixtral-8x7B … exhibits little domain specialization across both unique and generic domains"（p.20） | **能**（领域 = EWT 5 体裁，粒度粗） | `S_l` + genre |
| 4 | OLMoE §5.4 `[节]` | 专家 × 词表项 | 词表专精 N^(k)_{x,Ei}/N_x，x = 输入 / 真实下一词 / 预测下一词 | 无（定性） | "Later layers also specialize more on predicted output token IDs rather than input token IDs"（p.22） | **部分**（预测词要前向） | `S_l` + words |
| 5 | Mixtral 2401.04088 §5 `[节]` | 领域；相邻 token | Pile 子集上的专家分布；相邻 token 同专家比例 | 1/8；随机重复 12.5% / 46% | "we do not observe obvious patterns in the assignment of experts based on the topic"；"Repetitions at the first layer are close to random, but are significantly higher at layers 15 and 31"（p.7–8, 表 5） | **能**（相邻 token 用 `H·W`，只限 hidden 所在 ckpt） | hidden + genre |
| 6 | ST-MoE 2202.08906 §7 `[节]` | token 类 | 某类 token 的路由熵（表 14，哨兵 token） | 均匀熵 ln32 = 3.5 | "encoder experts specialize, but decoder expert don't"（p.20）；"expert specialization is heavily influenced by the distribution of tokens in each group"（p.19） | **能**（换成 UPOS 各类） | `S_l` + UPOS |
| 7 | Shazeer 2017 附录 E `[节]`、BASE 2103.16716 §5.2 `[节]`、OpenMoE 2402.01739 §4.1–4.2 `[节]` | 专家 | 每专家最常见的（前一）token 表；跨中间 ckpt 的 token-ID 偏好 | 无 | BASE："the token input at timestep t is often highly indicative of the expert assigned at time t"；OpenMoE："the routing probably has been learned at the warmup stage or so"（§4.2） | **能** | `S_l` + words，各 ckpt |
| 8 | Antoine 2412.16971 §3 `[全文]` | 词类 × 层 | Spec_POS,l = top-k 专家承担该词类的比例；ΔU = Spec − 均匀期望 U；专家 POS 分布对语料的 KL；路径 MLP 探针 | 均匀 U；词形多数类基线 .91 | "SpecPOS ranging from +25.21% for Mixtral to +36.32% for OlMoE"；探针 "between 0.79 and 0.88, except OlMoE"（§4） | **能**（E172 已做） | `S_l` + UPOS |
| 9 | DeepSeekMoE 2401.06066 §4.5 `[节]` | 模型 | 屏蔽每 token 路由概率最高的一定比例专家后的 Pile loss | GShard×1.5（同 loss） | "DeepSeekMoE is more sensitive to the disabling of top routed experts. This sensitivity suggests a lower level of parameter redundancy"（p.13） | **GPU** | checkpoint + 留出集前向 |
| 10 | NLLB-200 2207.04672 §6.2.4（式 13）与 §8.5 `[节]` | 语言 | G_lang = 该语言 token 的平均门控向量；语言间余弦、UMAP | 无 | "Languages within the same family are highly similar in their choice of experts, i.e., the late decoder MoE layers are language-specific" | **新数据** | 多语语料 |
| 11 | Kudugunta 2110.03742 §5.4 `[节]` | 任务（语对） | 每任务 top 专家分布 | 无 | "the set of experts appears to be similar for related languages. For example, English-Spanish and English-Catalan … have similar expert distributions" | **新数据** | 多语翻译 |
| 12 | Do Domain-specific Experts Exist 2604.05267 §3 `[节]` | 专家 × 领域 | g(e) = P(e\|D)·[P(s∈S\|e) − P(s∈C\|e)]，S/C 由 ‖e⊙∇L‖ 分的领域词 / 普通词；取 top-K（≈1% 专家） | 无对照专家集；以下游提升（对原模型、RICE、SFT）验证 | 10 个模型 3.8B–120B，"provide empirical evidence for the existence of domain-specific experts"（§1） | **GPU**（要梯度）+ 新数据 | — |
| 13 | DBES 2605.18498 §3 `[节]` | 领域 × 层 | S_spec = KL(P_r‖均匀)；R_eff = 路由矩阵归一化有效秩；S_iso = 1 − 领域间路由矩阵余弦；RSS = 路由概率与 Rademacher 噪声的对齐；n-gram 路径持续 | 均匀；随机 Rademacher | "modular specialization with high domain isolation, while DeepSeek and GLM employ distributed"（摘要）；理论部分质量存疑 | **能**（S_spec/S_iso/R_eff 用体裁；RSS 要路由概率 → `H·W`） | `S_l`、hidden + genre |
| 14 | Multilingual Routing 2510.04694 `[节]`；2601.14050 §4.1 `[节]`；Language Routing Isolation 2604.03592 §3 `[节]` | 语言 × 层 | 与英语配对句的熵归一化 JS 散度；Sim = 1 − JSD（专家选择频率）；top-K 专家集 Jaccard | 无（对英语） | "much higher routing divergence from English in the first and last layers than in the intermediate layers"（2510.04694 Finding 1） | **新数据** | 平行语料 |
| 15 | Myth 2604.09780 §5.1 `[节]` | rollout 对 | Top-p = 0.8 专家集 Jaccard（式 19），按（题, 生成模型, 采样 seed）两两比较 | 同题同模型不同采样 seed | "Different models solving the same question … share only ∼60% of their most-used experts, on par with the same model solving different questions"（图 6）。**注意：这里的"不同模型"是 60 个生成解答的模型，喂进同一个 MoE；不是不同训练** | **能**（换成"同文本、不同 run"，先配对专家） | `S_l` + R4 配对 |
| 16 | Equifinality 2604.14419 §5 `[节]` | 专家（跨 seed best-match） | top-20 词表投影 Jaccard；W_up 余弦 | 随机：Jaccard ≈ .0003；余弦 ≈ .116（极值理论） | "Expert weights show no cross-seed alignment … However, vocabulary projections show moderate functional alignment" | **GPU**（我们的专家非 rank-1，要专家平均输出投影） | checkpoint 前向 |
| 17 | Geometric Routing 2604.14434 §5–7 `[全文]` | token 组 / 专家 | 句法分组 vs 频率分组的轮廓系数差（200 次置换零假设、500 次 bootstrap）；语法富集 OR；同词异义专家集 Jaccard；Gini / 熵 | 置换零假设；频率匹配的 15 对词 | "Syntax grouping significantly outperforms frequency grouping at all 8 layers … syntax dominance increases with depth"（§5） | **能** | hidden 或 `S_l` + UD |
| 18 | Expert Strikes Back 2604.02178 §6.2 `[节]` | 专家 × unembedding 聚类 | 路由进来的 token（输入）与 logit lens 推出的 token（输出）在 unembedding k-means 聚类（k = 10…5000）上的分布对层基率的 JSD | Random Expert Baseline（同 N 随机抽） | "MoE experts act as discrete sub-routines for specific tasks"（讨论节） | **部分**（输入侧能，输出侧要前向） | `S_l` + unembedding |
| 19 | Demons in the Detail 2501.11873 `[节]` | 专家 × 领域 | 各领域的专家选择频率 | micro-batch vs global-batch 均衡 | "the global-batch LBL also greatly improves the domain specialization of MoE experts"（摘要） | **能**（体裁代领域） | `S_l` + genre |
| 20 | Monet 2412.04139 知识遗忘节、图 3 `[节]`；MoE-X 2503.07639 `[节]` | 领域；棋盘状态 | 删掉对目标领域路由偏斜的专家后各领域 MMLU 变化；棋局 board-state 探针 F1 | Gemma Scope SAE、OLMoE 删最常用专家；稠密 MLP | Monet："experts encapsulate disentangled parametric knowledge across domains" | **GPU** + 新数据 | — |
| 21 | Vision MoE 2605.20610 Results 末段 `[节]` | 专家（跨 10 个 seed） | 每专家读出层对 1,854 张 THINGS 图的一阶 RDM → 全部（模型 × 专家）的二阶 Spearman RSA → 层次聚类 | 无随机 / 未训练 / 重跑对照；轮廓系数选簇数 | "an animate-inanimate distinction dominates expert partitioning … and is stable across independently trained models"（摘要；E ∈ {4, 8, 16} 各 10 seed） | **GPU**（专家输出）；路由版 RDM **能** | checkpoint 前向 / `S_l` |

**小结：**完全能纯 CPU 复算的 12 种（#1 2 3 5 6 7 8 13 15 17 19 + #21 的路由版），部分能的 2 种（#4 18），其余 7 种要 GPU 或新数据。导师说的"借现成分析法看结论跨模型稳不稳"，最便宜的一组是 #1 / #3 / #6 / #8 / #17：每个都给单模型一个排序或一条曲线，可直接问"9 个 run 上这条结论重现到重跑地板没有"。#8 已在 E172 做过（排序跨 seed .73 vs 重跑 .97）。

## 表 2. 专家几何与功能相似度（导师"读数 3"）

| 度量 | 论文（证据） | 定义 | 跨独立训练用过？ | 要先配对？ | 我们复算成本 |
|---|---|---|---|---|---|
| 矩阵级权重余弦 | Lo 等 2406.18219 §4.1.1 `[节]` | 展平 W_up / W_act / W_down 的余弦，同层专家两两 | 否（单模型；对照稠密 FFN） | 同模型内不需要 | CPU，秒级 |
| 神经元重排后余弦 | Lo §4.1.2 `[节]` | 用 Jonker–Volgenant 找使两专家余弦最大的神经元顺序 | 否 | 要（神经元级） | CPU，64² 对 × 12 层，分钟级 |
| 专家输出特征余弦 | Lo §5 `[节]` | 同一 token 上各专家输出向量的余弦；"weight similarity measurements can reflect output similarity" | 否 | 同模型不需要 | 要前向 |
| 权重 best-match 余弦 | Equifinality §5 `[节]` | 每个专家在另一 seed 的 1024 个里找 \|cos(W_up)\| 最大者 | **是**（2 seed） | best-match（非一对一） | CPU；但我们的专家权重是矩阵，要先做神经元对齐 |
| 词表投影 Jaccard | Equifinality §5；Geometric Routing §4 `[全文]` | 专家输出方向经 unembedding 的 top-20 词集 Jaccard | **是**（2 seed） | best-match | 要前向（专家平均输出），或 CPU 近似（W_down 列投影） |
| CKA（线性 / RBF） | Kornblith 2019 1905.00414 `[摘要]` | 两组表示 Gram 矩阵的中心化对齐；"CKA can reliably identify correspondences between representations in networks trained from different initializations" | **是**（稠密） | 不需要 | 层级：CPU，用 hidden `H_l`；专家级要专家输出 |
| 二阶 RSA + 聚类 | 2605.20610 `[节]` | 各专家 RDM 的 Spearman 相关，跨模型聚类 | **是**（10 seed） | 不需要 | 专家 RDM 要前向；路由版（token × 专家共现）CPU |
| 置换对齐 + 线性模式连通 | LMC of MoE 2509.11348 `[节]` | 证明 MoE 对称 = 专家置换 × 门控置换；给权重匹配算法，看插值 loss 壁垒 | **是**（独立训练；ImageNet / CIFAR / WikiText103 等） | 要（专家 + 门控） | 匹配 CPU；插值评估要前向 |
| 路由器–专家耦合 | Routers Learn Geometry 2605.12476 `[节]` | 路由分数与专家 gate 激活的相关（ρ = .43）；路由器向量间余弦（aux loss 下约 .2 → .6） | 否（单轨迹） | 不需要 | CPU（路由器向量余弦）；耦合相关要前向 |
| 路由共现 / route 指纹 | OLMoE §5.2；我们 R4 | 专家 × 类别的路由质量矩阵，Hungarian 对齐后相关 | 我们：是（9 run） | 要 | 已有（.81） |
| 置换不变划分一致 | 我们 T_lex / T_ctx / T_D | 两个 token 是否同组的配对一致，减未训练地板 | 我们：是 | 不需要 | 已有 |
| Jacobian 子空间 / Grassmann 距离 | 2605.16349 `[摘要]`；2601.11616 `[摘要]` | 专家局部 Jacobian 主子空间间的距离 | 否 | 不需要（子空间） | 要前向 + Jacobian，GPU |
| 模型缝合 | Bansal 2021 2106.07682 `[摘要]` | A 的下层 + 可训线性层 + B 的上层，看精度损失；"stitching connectivity" | **是**（稠密） | 不需要（学映射） | GPU 训练小层 |

**对 E174 的直接含义：**跨训练用过、且不需要先配对的只有 CKA、二阶 RSA、模型缝合（加我们自己的置换不变量）。Equifinality 的 best-match 两个读数都没有未训练或重跑对照，是我们能直接加地板复算的形式。

## 表 3. 相邻领域对照："换 seed 后什么重现"

| 工作（证据） | 怎么问 | 读数 | 结论尺度 | 对"骨架一致 / 填充偶然"的启示 |
|---|---|---|---|---|
| Li 等 2015 Convergent Learning 1511.07543 `[摘要]` | 多个 CNN 的单元能否一一对上 | 二部匹配、稀疏预测、谱聚类 | "some features are learned reliably in multiple networks, yet other features are not"；"subspaces are common … the specific basis vectors learned are not" | 与我们同形：粗的（子空间）重现、细的（基）不重现 |
| Kornblith 2019 CKA 1905.00414 `[摘要]` | 用什么度量比跨初始化的表示 | CKA | CKA 能找对应层，CCA 类在高维失效 | 表示几何跨 seed 高度一致是背景事实；我们的几何 .95 与之一致，问题在离散分组 |
| Bansal 2021 Stitching 2106.07682 `[摘要]` | 不同训练的网络能否接上 | 缝合后精度 | "typical minima reached by SGD can all be stitched to each other" | 功能可互换 ≠ 分工相同；缝合只需线性映射，置换不变 |
| Gurnee 2024 Universal Neurons 2401.12181 `[摘要]`（此前笔记 `[全文]`） | GPT-2 五个 seed 的神经元是否通用 | 激活相关 − 随机旋转基线 | "1-5% of neurons are universal" | 细粒度单元多数不重现；重现的是 unigram / 句法类——与我们"重现的是语法骨架"同向 |
| Dodge 2020 2002.06305 `[摘要]` | 微调种子的方差从哪来 | 拆开初始化与数据顺序 | "both contribute comparably to the variance" | 我们预训练里初始化对（.28）比顺序对（.45）更远，与微调结论不同，值得写 |
| McCoy 2020 BERTs of a feather 1911.02969 `[摘要]` | 100 个微调 seed 泛化是否一致 | MNLI vs HANS | MNLI 83.6–84.8%，HANS 主宾互换 0–66.2% | 平均指标一致、机制级不一致：与我们"专精度到地板、专家身份不到"同形 |
| Juneja 2022 2205.12411 `[摘要]` | 微调模型是否在同一盆地 | 线性插值 loss 壁垒 + 诊断集 | "distinct clusters of models which are linearly connected … correspond to different generalization strategies" | 提示 run 可能成簇（离散几种切法）而非连续散开——可用 9 run 的两两 T_D 矩阵检验 |
| Summers & Dinneen 2021 2103.04514 `[节]` §3 表 1 | 各非确定性来源的作用 | 预测分歧、CKA，ResNet-14 CIFAR-10 | "each source of nondeterminism has very similar effects … all are within a maximum of 20% (relative) of each other"；一比特初始化扰动即发散 | 我们重跑 .50 / 顺序 .45 / 初始化 .28 不同于"各来源等效"，深层的初始化印记是 MoE 特有的对照点 |
| Bhojanapalli 2021 churn 2102.03349 `[摘要]` | 同算法两次训练的预测分歧 | churn | 标准图像分类上 churn 显著；最小熵正则、共蒸馏可降 | 给"地板"一个现成名字（churn），不同来源分开报 |
| Zhuang 2022 tooling 2106.11872 `[摘要]` | 硬件 / 库的非确定性有多大 | top-1 与子群精度 | top-1 不变，"certain parts of the data distribution is far more sensitive" | 我们的精确重跑对正是"只剩工具链噪声"的地板，必须保留 |
| Achille 2019 关键期 1711.08856 `[摘要]` | 早期缺陷是否永久 | 缺陷窗口 × 最终精度；权重 Fisher 信息 | "the first few epochs are critical for the creation of strong connections"；信息先升后降 | 第 100–200 步锁定的经典语言；可借"缺陷窗口"做法（早期扰动路由） |
| Frankle 2020 Early Phase 2002.10365 `[摘要]`；Frankle 2020 LMC 1912.05671（此前笔记） | 早期几百步发生了什么 | 重初始化、插值稳定性 | "weight distributions are highly non-independent even after only a few hundred iterations" | 分叉实验范式（第 k 步复制、换噪声）是检验锁定的直接设计 |
| Fehlauer 2025 2509.26643（此前笔记 `[全文]`） | 跨 seed 输出分布何时收敛 / 发散 | 期望 KL × 训练步 | 四阶段：均匀 → 收敛 → 发散 → 缓慢再收敛 | 我们重跑对 T_D 的非单调曲线可对到这四段 |
| Margalit 2024 TDANN（Neuron；bioRxiv 2023.05.18.541361）`[节]` 图 3、6 | 一个学习框架能否同时预测早期与高级视皮层的拓扑 | 选择性地图、模型–人 RSM 相似，**以人–人两两相似为上限**；模型单元与体素一对一映射；5 个随机 seed | 空间约束 + 自监督最像脑；一对一映射比线性回归更能区分模型 | 神经科学里已有"个体间一致作上限"的做法，与我们的重跑地板同构；一对一映射 ≈ 我们的 Hungarian 配对 |
| Blauch 2022 PNAS `[摘要]` | 高级视皮层分区能否由布线约束 + 通用学习产生 | 拓扑网络的领域选择性簇 | 最小化布线 + 兴奋性连接 → 领域簇 | "骨架由约束产生"的机制候选：我们的约束是负载均衡 + top-k |
| Arcaro 等 2017 Nat Neurosci `[摘要]` | 面孔区是否需要经验 | 不看面孔长大的猴子 | 无面孔区，其他类别区与视网膜拓扑正常；作者认为类别区落在固定位置意味着存在原型结构 | intrinsic vs activity-dependent：**位置的一致来自先天原型结构，内容来自经验**——与"骨架由数据决定、填充由早期噪声锁定"形式相同但方向相反，可作讨论 |
| Weiner 等 2014 NeuroImage `[摘要]` | 面孔区位置跨个体有多一致 | 中梭状沟前端 ↔ mFus-faces | 解剖标志预测面孔区位置 | 个体间一致到"解剖标志"的粒度，细粒度不一致；对应我们的粒度梯度 |

**最像我们命题的两篇：**Li 等 2015（同一套网络里"有些特征可靠重现、有些不"，子空间重现而基不重现——就是"骨架一致 / 填充偶然"的稠密版）和 2605.20610（视觉 MoE，10 个 seed，粗划分"有生 / 无生"跨 seed 与跨专家数都稳定，细的特征调谐各异——MoE 版，且直接触到我们的配方轴）。

## 4. 压缩风险精读：Equifinality 2604.14419 `[节 §1、§3.7、§4.3、§5、§8 Limitations]` 与 Geometric Routing 2604.14434 `[全文]`

**设定（两篇共用）：**自造 ST-MoE（与 ST-MoE 2022 无关）：cosine 路由到 64 维空间里的 1024 个质心，top-4，3 跳重路由，1024 个 rank-1 专家 / 层，8 层，d=1024，WikiText-103 训 5 万步（16.4 亿 token，约 14 个 epoch），76–84M 参数。seed 42 / 137 / 7；"all models see the same token sequences in the same order (given the same seed)"（§3.7）——即 seed 同时改初始化与数据顺序。

**跨 seed 主张逐条：**

| # | 主张 | 读数 | seed 数 | 基线 / 对照 | 出处 |
|---|---|---|---|---|---|
| E1 | 五种 cosine 路由拓扑 PPL 等价（1 PPL 内） | 收敛 PPL，TOST | 3 seed × 5 = 15 run，区间 33.93–34.72 | 线性路由器作负对照；seed 噪声 0.12 PPL | §4.3 |
| E2 | OpenWebText 上 Wide / Deep 只差 0.03 PPL | PPL | 每条件 3 seed | seed 噪声 | §8 |
| E3 | hash / 固定随机 / top-1 路由只差 1.1–2.2 PPL | PPL | **单 seed**（"multi-seed confirmation is left to future work"） | seed σ = 0.25 PPL | §4.3 |
| E4 | "Same Functions, Different Weights" | 专家间 best-match top-20 词表投影 Jaccard：.15（Wide）/ .13（Deep）；best-match \|cos(W_up)\| .107 | **2 seed**（42 vs 137），只在收敛 checkpoint，各层平均 | 随机 Jaccard ≈ .0003；随机余弦 ≈ .116 | §5 图 5 |
| G1–G6 | 语义词典、频率→句法梯度、同词异义分流 86%、因果干预、跨层可加、线性路由也可 steering | 各自 | **无跨 seed 主张**：全部在单个收敛 checkpoint（Wide 1×12、Deep 3×4）上 | 置换零假设、随机抑制 | Geometric §2–11 |

注意 Geometric Routing 的摘要写"early layers separate tokens by word frequency, deeper layers by syntactic class"，正文 §5 是"Syntax grouping significantly outperforms frequency grouping at all 8 layers"，深度趋势 ρ = .81——"早层按频率"只是相对弱，不是频率占优。

**与我们四条轴逐项对照：**

| 轴 | Equifinality §5 | 我们 |
|---|---|---|
| 地板 | 解析随机基线（.0003 / .116）；无未训练模型、无同 seed 重跑 | 未训练 ckpt_0 地板 + 精确重跑上限（深层 .50）+ 三种配对（重跑 / 顺序 / 初始化） |
| 粒度 | 只有专家级 best-match 一档 | 词类级 .86 → 同词形上下文切法 .48 → 逐 token .19，同一套 run |
| 时间 | 只有收敛点 | 0 → 40 亿 token 9–10 个 checkpoint；第 100–200 步锁定 |
| 配方 | Wide 与 Deep 两种拓扑各报一个 Jaccard，未作对比解释；拓扑轴只用于 PPL | E173：均衡强度、冻结路由器、专家数（跑中，结果未出，不预写） |
| 架构 / 数据 | 非标准（rank-1、cosine、多跳），WikiText 多 epoch | OLMoE 式线性路由 64 专家 top-8，Dolma 单遍 40 亿 token |

**审稿人问"你和 Equifinality 有什么不同"时的回答（中文）：**
Equifinality 用两个 seed 的收敛模型报告了一个数：专家的词表投影在跨 seed 最佳匹配下重叠 .13–.15，高于随机集合的 .0003，而权重余弦等于随机。它回答的是"功能是否高于随机地重叠"。我们问的是另一件事：分工里哪一部分到了重跑地板、哪一部分没有。为此我们用了随机基线给不出的两个参照——未训练模型（同一路由器在训练前就会把同词形分到一起）和同 seed 精确重跑（训练本身的不可约噪声）——并在同一组 run 上沿粒度和训练时间展开：词类级的分区到地板（.86），专家级身份不到（.19），而这个差距在第 100–200 步就已定下。Equifinality 的 .13–.15 在我们的框架里落在哪一档，需要加上这两个参照才能判断；它的设定（rank-1 专家、cosine 多跳路由、WikiText 14 个 epoch）与标准 MoE 也不同，所以两者是互补的测量，不是同一结论的两次报告。

**審査者に「Equifinality との違いは」と問われたときの回答（日本語）：**
Equifinality は 2 つの seed の収束モデルについて、専門家の語彙射影の最良一致 Jaccard が .13–.15 でランダム集合の .0003 を上回り、重みのコサインはランダムと同等、という一つの数値を報告しています。これは「機能がランダム以上に重なるか」への答えです。私たちが問うのは別のことで、分担のどの部分が再学習（同一 seed の完全再実行）の床に達し、どの部分が達しないかです。そのためにランダム基線では得られない二つの参照――未学習モデル（学習前のルータでも同じ語形はまとまる）と同一 seed の完全再実行（学習そのものの除去できない揺らぎ）――を置き、同じ run の集合で粒度と学習時間に沿って展開しました。品詞レベルの分割は床に達し（.86）、専門家レベルの同一性は達せず（.19）、その差は学習の 100–200 ステップ目で既に決まっています。Equifinality の .13–.15 が私たちの枠組みのどの段階に当たるかは、この二つの参照を加えて初めて判断できます。また rank-1 専門家・コサイン多段ルーティング・WikiText 14 エポックという設定は標準的な MoE と異なるため、両者は同じ結論の重複ではなく相補的な測定です。

**仍要防的一点（不是判决，是定位）：**2605.20610 已在视觉 MoE 上用 10 个 seed × 三种专家数报告"粗划分跨 seed 与跨专家数都稳定"。E173 的"专家数改变填充、不改骨架"若成立，要把它列为最近邻，增量写成：语言、重跑地板、粒度梯度、时间锁定。

## 5. 阅读中碰到的别的方向（不锁主线；与"跨训练一致度"不同的问题）

只列能用现有资产（9 个自训 MoE 全程 checkpoint + 路由缓存 + UD 标注）或 < 20 GPU h 回答、且有命名对手的。证据标签指"最近邻"读到的程度。

| # | 问题（一句） | 对手假设 | 读数 | 为什么顶会会关心 | 最近邻 | 资产 / 成本 |
|---|---|---|---|---|---|---|
| D1 | 深层路由按"当前词"还是按"将要预测的词"分，这个转换在训练哪一段发生？ | OpenMoE：按 token ID、上下文无关、warmup 就定（§4.2 `[节]`） vs OLMoE：深层按预测输出 token 专精（§5.4 `[节]`） | OLMoE 式词表专精，分别以输入词 / 真实下一词为 x，逐层 × 逐 checkpoint；交叉点出现的步数，与 Fehlauer 的"开始用上下文"阶段对齐 | 两篇工业报告对同一现象给出相反描述；一条曲线能同时裁决两者，并把路由接到输出预测的形成上（ACL / ICML 都有读者） | OpenMoE §4；OLMoE §5.4；Fehlauer 2509.26643 | 输入 / 真实下一词版纯 CPU（`S_l` + words）；"预测词"版要前向，< 2 GPU h |
| D2 | 第 100–200 步的锁定，是路由器与专家互相加固的结果，还是表示几何先定、路由只是跟着？ | Routers Learn Geometry 2605.12476 的耦合累积（路由器行与专家输入权重同向增长） vs Myth 2604.09780 的"路由反映隐状态几何" | 各 checkpoint 上：路由器行与对应专家输入权重主方向的余弦（耦合）、相邻 checkpoint 隐状态的 CKA（几何稳定）、路由饱和；看三条曲线谁先到平台 | 把"为什么早锁"从描述变成可证伪的时间先后问题，回答两篇 2026 理论稿各自的预测 | 2605.12476 `[节]`；2604.09780 `[节]`；Achille 2019 `[摘要]` | 耦合与饱和纯 CPU（权重 + `S_l`）；中间 checkpoint 的隐状态要前向，< 3 GPU h |
| D3 | MoE 的划分是不是按数据统计的奇异值顺序"由粗到细"逐级分裂？ | 渐进分化（Saxe、McClelland、Ganguli 2019 PNAS 的线性网络理论：大奇异值方向先学；HME 1993"高层切分先成" `[全文]`） vs 负载均衡驱动的任意顺序（Eigen 2013 §3 的 rich-get-richer `[全文]`） | 对每层路由划分做层级聚类，记录每次分裂首次出现的 checkpoint；与 token × 下一词共现矩阵的奇异值大小做秩相关 | 给 MoE 分工一个定量发育理论的检验；E172 已有"词类 / 形态先、依存后"的顺序，这条问它是否由谱顺序预测 | Saxe 2019（未核对，凭记忆）；HME 1993；E172 顺序结果 | 纯 CPU（`S_l` 全 checkpoint + 留出集共现统计） |
| D4 | 相邻 token 被分给同一专家（Mixtral 表 5 的"位置局部性"），跟着的是短语结构还是只是同一词的子词？ | 词汇连续假设（同一词拆出的子词、重复词形，如 Mixtral 的 `self`、缩进） vs 成分结构假设（短语内同专家、短语边界换专家） | P(t 与 t+1 同专家)，按"同词子词 / 同 UD 子树 / 跨子树边界"三类分开，逐层；以打乱专家标签为零假设 | Mixtral 与 DBES 都报告了局部性却没解释来源；若成分结构成立，是路由编码句法的直接证据（ACL 偏好） | Mixtral §5 表 5 `[节]`；DBES n-gram 持续 `[节]` | 纯 CPU，但现有 UD 缓存没有依存头位置，需从 EWT 原始 conllu 重取 head 列；连续 token 路由用 hidden 的 `H·W`（只限终点 checkpoint） |

没列入的：多语言路由（要新数据）、领域专家放大（要梯度与领域数据）、"可复现的切法是否承载 loss"（与主线同一问题的因果版，归主线）。
