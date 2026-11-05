# MoE 专家分析的历史（1991–2026）与度量目录

**为什么写：** 11-05 面谈，导师问「MoE に関する研究って、そんなにないんですか？」，并布置「MoE がどういうふうに分析されてきたのか、一度きちんと調べたほうがいい」。我们当场答"几乎没有"，是错的。本页回答三个问题：(1) 专家分析从什么时候开始、分析过什么；(2) 用什么尺度；(3) 哪些工作做过"模型 A 高、模型 B 低"的对比，哪些做过跨独立训练的比较。逐篇笔记在 [`SURVEY_SPECIALIZATION_UNIVERSALITY_2026-11-05.md`](SURVEY_SPECIALIZATION_UNIVERSALITY_2026-11-05.md) 与 [`../../../workbench/mechanism-population-dynamics/division/SURVEY_AND_DIRECTIONS_2026-11-05.md`](../../../workbench/mechanism-population-dynamics/division/SURVEY_AND_DIRECTIONS_2026-11-05.md) 附录 A；现成读数目录、专家几何度量、相邻领域对照与 Equifinality 精读在 [`READOUT_CATALOGUE_AND_SEED_ROBUSTNESS_2026-11-06.md`](READOUT_CATALOGUE_AND_SEED_ROBUSTNESS_2026-11-06.md)。证据级别：`[全文]` 读过正文；`[节]` 只读了相关章节（写明节号 / 页码）；`[摘要]` 只读摘要；"未核对" = 没拿到原文。**11-06 v2：**§5 的未核对项逐篇拿原文核过，时间线改了 7 处与原文不符的地方（见 §5 "更正"），补了 2025-09 以后的 7 篇（5 篇来自换措辞的新检索，2 篇此前只在笔记里）。

## 0. 一页结论

- **专家"分什么工"从 MoE 诞生起就是核心问题。** Jacobs–Jordan–Nowlan–Hinton 1991 在四元音判别上看专家决策线随训练的轨迹，原文写的正是对称破缺："Once one or more experts begin to receive more error from cases in one class pair than the other, this symmetry is broken"（p.86）`[全文]`。Jacobs–Jordan–Barto 1990/91 的摘要已明说 "function decomposition is an underconstrained problem and, thus, different modular architectures may decompose a function in different ways" `[节]`。Eigen–Ranzato–Sutskever 2013 报告两层 MoE"第一层按位置（where）、第二层按类别（what）"`[全文]`。
- **2017 年后的每一代大 MoE 都附带一节专家分析**，形式是"每个专家最常接哪些 token / 哪些类 / 哪些语言"：Shazeer 2017 附录 E `[节]`、V-MoE 2021 `[节]`、BASE 2021 §5.2 `[节]`、Kudugunta 2021 §5.4 `[节]`、ST-MoE 2022 §7 `[节]`、NLLB-200 2022 §6.2.4 / §8.5 `[节]`、Mixtral 2024 §5 `[节]`、OpenMoE 2024 §4 `[节]`、DeepSeekMoE 2024 §4.5 `[节]`、OLMoE 2024 §5 `[节]`。反复出现的结论：**按词形 / 词类 / 标点 / 数字分，不按主题分；路由早定（OpenMoE "learned at the warmup stage or so"，OLMoE 1% 训练时 top-8 已 60% 饱和）。**
- **2024 年起出现跨模型的横向比较**，比较的都是**单模型内的专精程度**：Antoine 等 2024 在 6 个公开 MoE 上比 POS 专精度 `[全文]`；2604.05267 在 10 个模型上找领域专家 `[节]`；DBES 2026 用五个指标对比 Qwen / DeepSeek / GLM `[节]`；多语路由三篇比较语言路由随层的变化 `[节]`。
- **跨独立训练比较分工的工作，找到四件**：Equifinality 2026（2 个 seed，只在收敛点，随机基线）`[节]`；视觉 MoE 2605.20610（10 个 seed × 专家数 4 / 8 / 16，二阶 RSA，"有生 / 无生"粗划分跨 seed 稳定，无未训练 / 重跑对照）`[节]`；双语 MoE 2608.15102（2 个 seed，专精集中在哪种语言随 seed 变）`[摘要]`；和我们（9 个 run，置换不变读数，未训练地板 + 精确重跑 + 三种配对）。**沿训练过程比较跨 seed 分工的，没找到**（OLMoE / OpenMoE 的饱和曲线都是单条轨迹对自身终点）。
- 给导师的准确说法：MoE の専門家分析は 1991 年から続き、2024 年以降だけで十数本。ただし独立学習間で分担を比べたものは我々以外に 3 本（言語モデルでは 2 seed の 1 本）、学習過程に沿って比べたものは見つかりませんでした。

## 1. 时间线

| 年 | 工作 | 模型 / 任务 | 分析了什么 | 尺度 / 基线 | 跨模型对比 | 跨训练 |
|---|---|---|---|---|---|---|
| 1991 | Jacobs, Jordan, Nowlan, Hinton (Neural Comp. 3:79–87) `[全文]` | 四元音判别（75 人，前 50 训练） | 竞争学习让专家各管一对类；图 3 看专家决策线随 epoch 从共同点 X 分叉 | 决策线轨迹；对照 6 / 12 隐元 BP 网络（25 次模拟取均值） | 4 vs 8 专家 | 25 次模拟，原文只说解"typical"："in all simulations with mixtures of 4 or 8 experts all but 2 or 3 experts had mixing proportions that were effectively 0"（p.87）；未比较各次的分解是否相同 |
| 1990/91 | Jacobs, Jordan, Barto (COINS TR 90-27 / Cog. Sci. 15:219–250) `[节：TR pp.1–8，含摘要与 §1；§4–5 未读到]` | what / where 视觉任务 | 竞争使不同网络学不同函数，并把任务分给拓扑最合适的网络 | 对照两个多层 BP 网络 | 不同专家架构 | 摘要："function decomposition is an underconstrained problem … different modular architectures may decompose a function in different ways"（说的是架构，不是 seed） |
| 1993/94 | Jordan & Jacobs HME `[全文：IJCNN 1993 会议版 6 页；Neural Comp. 1994 期刊版未核对]` | 四关节机械臂正向动力学，16 专家 | 各节点门控后验的直方图随 epoch 由 .5 走向 0/1 双峰；"there is a tendency for the splits to be formed more rapidly at higher levels in the tree than at lower levels"（p.1342，即粗的切分先成） | 相对误差；对照线性、BP（60 隐元）、CART、MARS | — | — |
| 2012 | Yuksel, Wilson, Gader 综述 (TNNLS 23:1177–1193) **未核对** | — | 据出版社摘要：回归 / 分类基本模型、EM 训练、高斯过程专家、专家数选择 | — | — | — |
| 2013 | Eigen, Ranzato, Sutskever (1312.4314) `[全文]` | 平移 MNIST、单音素语音 | §5.1 图 2：第一层按平移分配、按类别均匀；第二层反之；易混类（3 与 5）同组 | 平均门控输出（与均匀目测比较）；§3 指出纯 SGD 会"rich get richer"塌缩，需分配约束 | — | — |
| 2017 | Shazeer 等 `[节]` | 翻译，2048 专家 | 专家按句法 / 语义专精（附录 E 表 9） | 按门控值排序的上下文表 | — | — |
| 2021 | Kudugunta 等 (Findings EMNLP) §5.4 `[节]` | 多语翻译 token-MoE | 编码器各任务偏好同一小撮专家；解码器按任务分；"English-Spanish and English-Catalan … have similar expert distributions" | 每任务 top 专家分布 | 编码器 vs 解码器 | — |
| 2021 | V-MoE (Riquelme 等) `[节]` | 图像分类 | 深层专家与类别相关、浅层按 patch 位置；单层换随机路由可容忍 | 专家 × 类别路由权重 | 层深 | — |
| 2021 | Hash Layers (Roller 等)；THOR (Zuo 等) `[摘要]` | LM / 翻译 | 固定哈希 / 随机路由不输学习路由 | 困惑度 / BLEU | 路由方式 | — |
| 2021 | BASE Layers (Lewis 等) §5.2 `[节]` | LM，128 专家 | "many assignment decisions appear to depend primarily on very local syntactic information"；表 1 每专家最常见的**前一输入词**；"the model primarily assigns experts based on fairly superficial signals" | 定性；无基线 | — | — |
| 2021 | DEMix `[摘要]`；2022 Branch-Train-Merge | LM | 按领域**构造**专家（非自发） | — | — | — |
| 2022 | ST-MoE (Zoph 等) §7 `[节]` pp.19–21 | 编码器-解码器，32 专家 × 6 层 | 人工检视：编码器专家接哨兵、标点、连词冠词、动词、专名、数字；解码器无专精；多语"Experts trained on multilingual mixtures do not exhibit language specialization"；专精"heavily influenced by the distribution of tokens in each group" | 表 14 哨兵 token 路由熵 vs 均匀 3.5 | 编码器 vs 解码器 | — |
| 2022 | NLLB-200 §6.2.4（式 13）与 §8.5 `[节]` | 53 / 202 语翻译 | 晚解码层按语言分专家（"late decoder MoE layers are language-specific"），早编码层次之；同语系选相近专家 | 每语言平均门控向量 → 余弦热图、UMAP | 层位置 | — |
| 2022 | MoEfication `[摘要]`；2023 Emergent Modularity `[摘要]` | 稠密 Transformer | 稠密 FFN 内自发功能分区；功能专家约 15% 训练处稳定 | 神经元共激活聚类 | 稠密 vs MoE | — |
| 2022 | StableMoE、X-MoE、Chen 等理论 | LM / 理论 | 路由波动；表示坍缩；专精由簇结构决定、分配由初始化决定 | — | — | 理论上提到 |
| 2022 | Pavlitskaya 等 (CNN-MoE) `[摘要]` | 图像 | 按子领域 / 物体尺寸专精；软 / 硬约束改变专精 | 专家 × 类别 | 约束方式 | — |
| 2024 | Mixtral §5 `[节]` p.7 | LM，8 专家 | Pile 子集上"we do not observe obvious patterns in the assignment of experts based on the topic"；`self`、缩进固定专家；相邻 token 同专家（第 0 层近随机，15 / 31 层显著高） | 图 7 基线 1/8；表 5 随机重复 12.5% / 46% | — | — |
| 2024 | OpenMoE §4 `[节]` | LM，32 专家 | 不按领域分；按 token ID 路由（context-independent）；中间 ckpt 的偏好"almost totally overlapped"，换数据配比与目标也不变；末尾 drop；§4.4：DeepSeek-MoE 也有、Mixtral 没有 | 路由可视化；无数值基线 | 3 模型 | — |
| 2024 | DeepSeekMoE §4.5 `[节]` p.13 | LM 2B | 屏蔽 top 路由专家损失升得更快 = 冗余更低；去掉共享专家 Pile loss 1.808 → 2.414 | 消融曲线 vs GShard×1.5 | 架构 | — |
| 2024 | OLMoE §5 `[节]` pp.18–22 | LM，64 专家 top-8 | 1% 训练时 top-8 约 60% 饱和、40% 时约 80%，深层先饱和、L0 最慢；共激活弱；arXiv / GitHub 有近 100% 专精专家；深层按**预测输出 token** 专精 | 饱和 / 共激活 / 领域 / 词表四个公式；随机 12.5% | 从头 vs Mixtral（作者推测 upcycled） | 单轨迹对自身终点 |
| 2024 | Lo 等 "A Closer Look" (Findings NAACL 2025) `[节]` | Mixtral / DeepSeek / Grok | 神经元是细粒度专家；路由偏向大输出范数；深层专家更不相似 | 矩阵级 / 神经元重排余弦、输出余弦 | 4 个模型 | — |
| 2024 | Antoine, Béchet, Langlais (POS sensitivity) `[全文]` | 6 个公开 MoE | ΔU +25.21%（Mixtral）～ +36.32%（OLMoE）；路径 MLP 预测 POS .79–.88，OLMoE 更低；标点 / 符号最专精 | Spec − 均匀 U；KL；路径探针（词形基线 .91） | **6 模型横比** | — |
| 2024 | Fan, Messmer, Jaggi `[摘要]` | GPT-2 small 自训 | 冻结随机路由器 ≈ 学习路由器 | 困惑度 | 路由可学 vs 冻结 | — |
| 2024 | Tang 等 (ACL)、Kojima 等 (NAACL) `[摘要]` | 稠密 LLM | 语言特异神经元集中在首尾层 | LAPE 熵 | 稠密对照 | — |
| 2025 | Olson 等 (semantic routing) `[摘要]` | 公开 MoE | 同词不同义 → 专家重叠下降，随规模增强 | 专家重叠 | 规模 | — |
| 2025 | Demons in the Detail (Qwen, ACL) `[节]` | 自训 | micro-batch 均衡抑制领域专精，global-batch 恢复 | 专家 × 领域选择频率 | 均衡作用域 | — |
| 2025 | Monet；MoE-X `[节]`；Hidden Collaboration `[摘要]`；知识归因 | 公开 / 自训 | 单义专家；删偏斜专家做领域遗忘；共享专家做通用 | 各自 | — | — |
| 2025-09 | LMC of MoE (2509.11348, NeurIPS) `[节]` | 自训 MoE（图像 / WikiText103） | MoE 对称 = 专家置换 × 门控置换；权重匹配后线性连通 | 插值 loss 壁垒 | — | **独立训练对**（权重级） |
| 2026 | Standing Committee (2601.03425, ACL) `[全文，见笔记]` | 3 个公开 MoE | 跨领域不变的 2–5 个专家吃 30–70% 路由质量，接句法骨架词 | ECI、跨领域 Jaccard | 3 模型 | — |
| 2026 | Routing signatures (2603.11114) `[摘要]` | OLMoE-Instruct | 同任务提示的跨层路由向量更相似（.84 vs .62） | 置换与负载均衡基线 | — | — |
| 2026 | Three Phases (2604.04230) `[全文，见笔记]` | OLMoE 20 ckpt + OpenMoE 6 | 拥塞系数先升、平台、再降 | 路由器 logits 回归 | 2 模型 | 单轨迹 |
| 2026 | Expert Strikes Back (ICML) `[节]`；RouterInterp (ICML) `[全文，见笔记]` | 公开 MoE | 专家比稠密 FFN 更单义；专家 = 多个不相关微领域的叠加 | k-sparse 探针；unembedding 聚类 JSD vs 随机专家基线；SSH 预测 | 多模型 | — |
| 2026 | Myth of Expert Specialization (2604.09780) `[节]` | 3 个公开 MoE | 隐状态相似 ⇒ 路由相似（Prop.1）；§5.1 同一题由 60 个**生成模型**写的解答，在同一 MoE 里只共享约 60% 专家，"on par with the same model solving different questions" | Top-p Jaccard；同题同模型不同采样 seed 作上限 | 文本来源 | — （"不同模型"指生成文本的模型，不是不同训练） |
| 2026 | Routers Learn Geometry (2605.12476, NeurIPS) `[节]` | 1B 自训 | 路由器与专家输入权重耦合累积（ρ = .43）；aux loss 使路由器向量余弦 .2 → .6；K-Means 质心路由只差 2.6% PPL | 相关、余弦 | 路由器变体 | 单轨迹 |
| 2026 | Geometric Routing (2604.14434) `[全文]` | 自训 rank-1 cosine MoE（单 checkpoint） | 15% 专家单义；句法分组在**全部 8 层**都优于频率分组，深度趋势 ρ = .81；同词异义专家 86% 不同；steering / 抑制 / 改写因果验证 | 轮廓系数 + 200 次置换零假设；随机抑制 | 线性 vs cosine 路由 | **无** |
| 2026 | **Equifinality in MoE** (2604.14419) `[节]` | 同上，WikiText-103 | 五种路由拓扑 PPL 等价（3 seed × 5）；§5 跨 seed 词表投影 best-match Jaccard .15 / .13 vs 随机 .0003，权重余弦 .107 ≈ 随机 .116 | 解析随机基线 | 拓扑（仅 PPL） | **2 seed**，只在收敛点 |
| 2026 | Causal Audit；预注册前沿 MoE (2606.25092) `[全文，见笔记]` | 公开 | 观察指标不预测消融重要性；6 个预注册模块只剩 1 个 | 消融 vs 随机专家 null | — | — |
| 2026 | Multilingual Routing (2510.04694, ICLR)；2601.14050；Language Routing Isolation 2604.03592 `[节]`；2605.29714 | 公开多语 MoE | 首尾层与英语的路由散度高、中层低（U 形）；同语系更相似；Qwen3-30B 与英语 Jaccard 孟加拉 .12 / .22 / .05，俄 .41 / .43 / .17 | 熵归一化 JS 散度；1 − JSD；top-K Jaccard | 语言 × 层 | — |
| 2026 | Do Domain-specific Experts Exist (2604.05267) `[节]` | 10 个公开 MoE，3.8B–120B | 都存在领域专家（取约 1% 专家）；放大它们提升领域成绩 | 梯度 × 嵌入的 token 评分 g(e) | **10 模型** | — |
| 2026 | DBES (2605.18498) `[节]` | Qwen3 / GLM-4.6 / DeepSeek-R1 | Qwen 系"模块化"、DeepSeek / GLM"分布式" | S_spec、R_eff、S_iso、RSS、n-gram 持续 | **多模型** | — |
| 2026 | Goodfire 2604.17837 `[摘要]` | 6 个公开 MoE | 低维控制子空间驱动路由；跨层专家路径单义 | 路径聚类 | 多模型 | — |
| 2026 | 2605.16349 `[摘要]` | Mistral / Qwen | 专家 Jacobian 去相关但子空间重叠；top-k 比 soft 分得更开 | Jacobian 对齐、Grassmann 距离 | 路由稀疏度 | — |
| 2026-05 | **Vision MoE: Beyond Routing (2605.20610)** `[节]` | 自训卷积 MoE，STL10 对比学习 | 各专家读出层对 THINGS 1,854 图的 RDM → 二阶 RSA 跨模型聚类："an animate-inanimate distinction dominates expert partitioning … and is stable across independently trained models"；细的特征调谐各专家不同 | 二阶 Spearman RSA + 轮廓系数；无随机 / 未训练 / 重跑对照 | **专家数 4 / 8 / 16** | **10 seed × 3 配置** |
| 2026-08 | Declarative–Procedural bilingual MoE (2608.15102) `[摘要]` | 自训英德小 MoE | 按词汇 / 语法 / 句法探针测路由互信息；无课程条件下专精集中在哪种语言随 seed 变 | 互信息 | 课程 | **2 seed** |
| 2026-10 | Muon first MoE layer (2610.37914) `[摘要]` | 自训 55M / 108M 激活 | Muon 使第一层均衡偏置跨度约翻倍，"at every seed" | 偏置跨度 | 优化器 | 多 seed（只看负载，不看分工） |
| 2026 | **我们 (E167–E172)** | 自训 9 run | 扣地板后深层切法一致 .28（重跑 .50）；词类 .86 → 切法 .48 → 逐 token .19；第 100–200 步定型；"哪类词最专精"排序跨 seed .73 vs 重跑 .97 | 置换不变划分一致 T_D、Hungarian 指纹相关、逐 token 因果角色 | 配对类型 × 层 × 粒度 × 时间 | **9 run** |

## 2. 度量目录：专精度与一致度是两件事

**(A) 单模型"专精度"**（文献主体；回答"专家有没有分工"）。公式、基线、原话与能否 CPU 复算的完整版见 [`READOUT_CATALOGUE_AND_SEED_ROBUSTNESS_2026-11-06.md`](READOUT_CATALOGUE_AND_SEED_ROBUSTNESS_2026-11-06.md) 表 1。

| 尺度 | 定义 | 出处 | 备注 |
|---|---|---|---|
| 每专家 top token / 上下文表 | 按门控值或计数排序 | Shazeer 2017、BASE、ST-MoE、OpenMoE | 定性 |
| 专家 × 类别 / 领域 / 语言矩阵 | 路由权重或计数 | V-MoE、OLMoE、NLLB、Kudugunta、Mixtral | 基线多为 1/E 或 k/E |
| 路由饱和 | 中间 ckpt 与终点 top-k 的交集比例 | OLMoE §5.1 | 单轨迹对自身终点 |
| 类别路由熵 | 某类 token 的专家分布熵 | ST-MoE 表 14 | 均匀熵作基线 |
| Spec_POS,l | 承担该词类最多的 top-k 专家吃掉的比例，减去均匀期望 U | Antoine 2024 | U 随 k / 专家数变，跨模型要看 ΔU |
| KL(专家分布 ‖ 语料分布) | 每专家的词类分布偏离语料 | Antoine 2024 | 无上界，难解释 |
| 路由专精 S_spec | KL(领域内专家使用 ‖ 均匀) | DBES | 与负载均衡目标相反 |
| 领域隔离 S_iso | 不同领域路由分布的余弦正交度 | DBES | "模块化 vs 分布式" |
| 有效秩 R_eff | 路由矩阵奇异值的有效维数 | DBES | 低 = 秩坍缩 |
| n-gram 路径持续 | 滑窗内至少一个专家持续激活的概率 | DBES | 序列级 |
| 语言 Jaccard / JS 散度 | 两语言 top-K 专家集交并比；配对句的熵归一化 JSD | 2604.03592；2510.04694 | 按层分 |
| 句法 vs 频率轮廓系数 | 两种分组在路由空间的轮廓系数差，置换零假设 | Geometric Routing §5 | 有零假设 |
| 路径探针 | 用 (层 × k) 专家 id 预测 POS / 功能 | Antoine 2024、Goodfire 2026 | 受词形基线 .91 约束 |
| 消融冗余 | 禁用 top 专家的损失曲线 | DeepSeekMoE、Causal Audit | 因果 |
| 神经元单义度 / unembedding 聚类 JSD | 专家内神经元的语义纯度；路由 token 在 unembedding 聚类上对基率的 JSD | Expert Strikes Back | 有随机专家基线 |

**(B) 跨模型"一致度"**（Equifinality、2605.20610、2608.15102 与我们；回答"分工是不是同一套"）。专家编号在不同训练里无对应，必须三选一：

1. **先配对再比**：Hungarian 对齐指纹（我们的 R4 route / drop 指纹）、best-match（Equifinality 的词表投影 Jaccard 与权重余弦），或权重置换对齐（LMC of MoE）。缺点：配对质量本身是变量；best-match 不是一对一，会高估。
2. **配对无关的量**：不问"哪个专家"，只问"这两个 token 是否同组"——我们的 T_lex / T_ctx / T_D（减未训练地板）；或比较各专家表示几何的二阶 RSA 再聚类（2605.20610）。优点：不依赖配对；缺点：粗粒度。
3. **分析结论的一致**：同一种 (A) 类分析分别跑在各模型上，比较其输出剖面（我们的 83 词分离度剖面 .85–.92、"哪类词最专精"的排序 .73 vs 重跑 .97）。这是导师第 12 条的直接形式；读数目录表 1 里能纯 CPU 复算的 12 种都可以这样做。

**(A) 与 (B) 的关系要讲清楚：**专精度高不等于一致度高。两个 seed 可以都高度按词类专精、却把词类切成不同的组合；也可以专精度一般、但切法相同。Antoine 报告 OLMoE 专精最高（ΔU +36%）而路径探针最低，Equifinality 报告跨 seed 重叠高于随机，两者说的不是一回事。

## 3. 谁做过"模型 A 高、模型 B 低"

| 对比轴 | 工作 | 结果 | 比的是 |
|---|---|---|---|
| 公开模型族 | Antoine 2024 | ΔU +25（Mixtral）～ +36（OLMoE） | 专精度 |
| 公开模型族 | DBES 2026 | Qwen 模块化、DeepSeek / GLM 分布式 | 专精度 |
| 公开模型族 | 2604.05267 | 10 个模型都有约 1% 领域专家 | 专精度 |
| 规模 | Olson 2025 | 语义路由随规模增强 | 专精度 |
| 编码器 vs 解码器 | ST-MoE、Kudugunta | 编码器分、解码器不分 / 按任务分 | 专精度 |
| 从头 vs upcycled | OLMoE §5.3（推测）、OpenMoE §4.4（引推文） | Mixtral 几乎无领域专精 / 无 token-ID 专精 | 专精度 |
| 负载均衡作用域 | Demons in the Detail；ST-MoE §7（group 内均衡） | 全局均衡 → 领域专精出现 | 专精度 |
| 软 / 硬约束；top-k vs soft | Pavlitskaya 2022；2605.16349 | 约束改变专精结构；top-k 分得更开 | 专精度 |
| 层深 | Eigen 2013、V-MoE、多语路由三篇、Geometric Routing、我们 | 浅层表面 / 位置 / 语言，深层类别 / 句法 | 专精度；我们是一致度 |
| 学习路由 vs 哈希 / 随机 / 冻结 | Hash Layers、THOR、Fan 2024、Equifinality（单 seed） | 小规模下只差 1–2 PPL | 损失 |
| 专家数 | 2605.20610（视觉） | E = 4 / 8 / 16 下"有生 / 无生"粗划分都跨 seed 稳定 | **一致度（粗划分）** |
| 配对类型、粒度、时间 | 我们 | 重跑 .50 / 顺序 .45 / 初始化 .28；词类 .86 → 逐 token .19；100–200 步定型 | **一致度** |
| **语言 MoE 的配方 × 一致度** | 没找到 | — | — |

最后一行：在语言 MoE 上，没找到报告"一致度作为配方（均衡强度、专家粒度、top-k、路由可学性）的函数"的工作；视觉上 2605.20610 已覆盖"专家数 × 粗划分"一格（无地板）。这是导师第 8 条要的东西，E173 正在做。

## 4. 给下次 Slack 的日文段落（草稿，11-06 改）

前回「MoE の解釈研究はほとんどない」と申し上げたのは不正確でした。専門家が何を分担するかの分析は MoE の原点から続いており、Jacobs ら（1991）はすでに専門家の決定境界が学習中に「対称性の破れ」を経て分かれていく様子を描き、Jacobs・Jordan・Barto（1991）は「関数の分解は劣決定問題で、アーキテクチャによって分け方が変わりうる」と述べています。Shazeer ら（2017）以降の主要な MoE 論文はほぼ毎回、各専門家がどの語・品詞・言語を担当するかを一節設けて報告しています（BASE、ST-MoE、NLLB-200、Mixtral、OpenMoE、OLMoE など）。共通する結論は「話題ではなく語形・品詞・記号で分かれる」「ルーティングは学習のごく初期に固まる」の二点です。2024 年以降は複数の公開モデルを横断して専門化の度合いを比較する研究も出ています（Antoine ら 2024：6 モデルで品詞専門化、DBES 2026：Qwen は分離型・DeepSeek は分散型、など）。
ただし、これらは「1 つのモデルの中で専門家がどれだけ偏っているか」を測っています。独立に学習したモデル同士で分担を比べた研究は、言語モデルでは 2 seed の Equifinality（2026）と 2 seed の小規模二言語モデル、視覚では 10 seed の研究（2026、「有生／無生」の粗い分割は seed をまたいで安定）が見つかりました。いずれも同一 seed の再実行や未学習モデルを基準にしておらず、学習過程に沿って一致を追ったものはありません。また言語 MoE で「一致度が設定（負荷分散の強さ、専門家の数、ルータを学習させるか固定するか）でどう変わるか」を報告したものも見つからず、先生のおっしゃる「このモデルでは低く、このモデルでは高い」を出せるのはここだと考えています。

## 5. 未核对 / 更正记录（11-06）

**仍未核对（拿不到原文）：**
1. Yuksel, Wilson, Gader 2012（TNNLS）：出版社闭源，OpenAlex 无开放版本，第三方镜像返回空页；只核对了书目信息与出版社摘要。
2. Jacobs, Jordan, Barto 1991 期刊版：只拿到 COINS TR 90-27 前 8 页（摘要、引言、§1）；§3–5（what / where 实验与"分解依赖架构"的讨论）未读到。
3. Jordan & Jacobs 1994 期刊版（Neural Comp. 6:181–214）：只读了 IJCNN 1993 会议版全文；MIT AI Memo 1440 长版下载被拦。

**更正（原表与原文不符处）：**
1. Jacobs 等 1991：原表写"讨论了不同运行得到不同分解"——原文没有比较各次运行的分解，只说 25 次模拟里的解是"typical"（p.87）。
2. BASE Layers：原表写"专家聚集语义相近词"——原文 §5.2 的结论是按局部句法 / 表面信号（前一输入词）分，"fairly superficial signals"。
3. Mixtral：原表把"Mixtral 是 upcycled"写成事实——Mixtral 论文本身未说；OpenMoE §4.4 引推文、OLMoE §5.3 写作"We hypothesize"。
4. NLLB：主要分析在 §6.2.4（式 13），§8.5 是 200 语版本；原表只写 §8。
5. Myth of Expert Specialization：此前笔记把"不同模型 ~60% 重叠"读成跨训练——原文 §5.1 的"不同模型"是 60 个**生成解答的模型**，解答喂进同一个 MoE，不是不同训练；对我们不是同向证据。
6. Geometric Routing：此前笔记写"早层按频率、深层按句法"——那是摘要的说法；正文 §5 是句法分组在全部 8 层都优于频率分组，只是越深越强；且全文无跨 seed 主张。
7. Antoine 2024：原 §0 / §2 写"OLMoE 专精最低"、路径探针".72–.88"——原文是 OLMoE 的 ΔU 最高（+36.32%），路径探针 "between 0.79 and 0.88, except OlMoE"（OLMoE 更低）。

**仍存疑：**DBES 的理论部分（Rademacher / Bellman 秩）质量存疑，只取指标定义与模型对比。2608.15102、2610.37914、2603.11114 只读摘要。
**补漏检索：**arXiv API 25 组查询（含 "random seeds" / "independently trained" / "different initializations" / universality / "symmetry breaking" / "division of labor" / "expert identity" / "routing consistency" / "router saturation" / "expert alignment" / "part-of-speech" 等），限 2025-09-01 以后，人工筛掉应用类；新收 2605.20610、2608.15102、2610.37914、2603.11114、2509.11348 进表。未覆盖：OpenReview 未上 arXiv 的投稿、非英文文献。
