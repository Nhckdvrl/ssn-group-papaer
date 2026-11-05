# MoE 专家分析的历史（1991–2026）与度量目录

**为什么写：** 11-05 面谈，导师问「MoE に関する研究って、そんなにないんですか？」，并布置「MoE がどういうふうに分析されてきたのか、一度きちんと調べたほうがいい」。我们当场答"几乎没有"，是错的。本页回答三个问题：(1) 专家分析从什么时候开始、分析过什么；(2) 用什么尺度；(3) 哪些工作做过"模型 A 高、模型 B 低"的对比，哪些做过跨独立训练的比较。逐篇笔记在 [`SURVEY_SPECIALIZATION_UNIVERSALITY_2026-11-05.md`](SURVEY_SPECIALIZATION_UNIVERSALITY_2026-11-05.md) 与 [`../../../workbench/mechanism-population-dynamics/division/SURVEY_AND_DIRECTIONS_2026-11-05.md`](../../../workbench/mechanism-population-dynamics/division/SURVEY_AND_DIRECTIONS_2026-11-05.md) 附录 A。证据级别：标 `[全文]` 的读过正文；标 `[节]` 的只读了相关章节；标 `[摘要]` 的只读摘要；未标的凭已知内容，可能有误。

## 0. 一页结论

- **专家"分什么工"从 MoE 诞生起就是核心问题。** Jacobs–Jordan–Nowlan–Hinton 1991 的元音任务与 Jacobs–Jordan–Barto 1991 的 what / where 任务，研究的就是竞争学习如何把任务**自发分解**给不同专家，以及分解结果如何依赖专家结构。Eigen–Ranzato–Sutskever 2013 的两层 MoE 第一次报告"第一层按位置（where）、第二层按类别（what）"的分层专精 `[摘要]`。
- **2017 年后的每一代大 MoE 都附带一节专家分析**，形式是"每个专家最常接哪些 token / 哪些类 / 哪些语言"：Shazeer 2017 附录 E 表 9 `[节]`、V-MoE 2021 `[节]`、Kudugunta 2021 `[节]`、ST-MoE 2022、NLLB-200 2022 `[节]`、Mixtral 2024、OpenMoE 2024、DeepSeekMoE 2024 `[节]`、OLMoE 2024。结论反复出现：**按词类 / 标点 / 数字 / 语言分，不按主题分；浅层按表面特征，深层按类别或语义。**
- **2024 年起出现跨模型的横向比较**，但比较的都是**单模型内的专精程度**：Antoine 等 2024 在 6 个公开 MoE 上比 POS 专精度 `[全文]`；"Do domain-specific experts exist" 2026 在 10 个模型上找领域专家 `[摘要+节]`；DBES 2026 用五个指标对比 Qwen / DeepSeek / GLM `[节]`；多语言路由三篇比较语言隔离随层的变化 `[节]`。
- **跨独立训练比较分工的工作只有两件**：Equifinality 2026（2 个 seed，功能重叠 500 倍随机）和我们（9 个 run，置换不变读数，三个参照）。**沿训练过程比较跨 seed 分工的工作没有。**"同一种分析方法的结论跨 seed 稳不稳"也没人报告过——Antoine 的 6 模型比较里 OLMoE 最低，但无法区分"OLMoE 的路由确实不那么语法化"和"单次训练的偶然"。
- 所以给导师的准确说法：MoE の専門家分析は 1991 年から続き、2024 年以降だけで十数本。ただし独立学習間の比較は 2 本、学習過程に沿った比較は 0 本。

## 1. 时间线

| 年 | 工作 | 模型 / 任务 | 分析了什么 | 尺度 | 跨模型对比 | 跨训练 |
|---|---|---|---|---|---|---|
| 1991 | Jacobs, Jordan, Nowlan, Hinton (Neural Comp.) | 元音判别 | 竞争学习下专家自发分割输入空间 | 门控权重随输入的分布 | — | 讨论了不同运行得到不同分解 |
| 1991 | Jacobs, Jordan, Barto (Cog. Sci.) | what / where 视觉任务 | 任务分解给哪个专家、依赖专家结构 | 每任务的门控分配 | 不同专家架构 | — |
| 1994 | Jordan & Jacobs HME | 回归 / 分类 | 树状软划分 | EM 后验 | — | — |
| 2012 | Yuksel, Wilson, Gader 综述 (TNNLS) | — | 二十年 MoE 的回顾 | — | — | — |
| 2013 | Eigen, Ranzato, Sutskever `[摘要]` | 平移 MNIST、音素 | 第一层 where、第二层 what | 分配可视化 | — | — |
| 2017 | Shazeer 等 `[节]` | 翻译，2048 专家 | 专家按句法 / 语义专精（"innovation"专家、"plays a … role"专家、"rapidly"专家） | 按门控值排序的上下文表 | — | — |
| 2021 | Kudugunta 等 (Findings EMNLP) `[节]` | 多语翻译 token-MoE | 编码器各任务偏好同一小撮专家；解码器按任务分；相近语言（西/加、俄/乌）专家分布相似 | 每任务 top 专家分布 | 编码器 vs 解码器 | — |
| 2021 | V-MoE (Riquelme 等) `[节]` | 图像分类 | 深层专家与 ImageNet 类别强相关，浅层按 patch 位置；单层换随机路由可容忍，连续多层不可 | 专家 × 类别路由权重；随机路由替换 | 层深 | — |
| 2021 | Hash Layers (Roller 等)；THOR (Zuo 等, ICLR 2022) `[摘要]` | LM / 翻译 | 固定哈希 / 随机路由不输学习路由 | 困惑度 / BLEU | 路由方式 | — |
| 2021 | BASE Layers (Lewis 等) | LM | 平衡分配后专家聚集语义相近词 | 每专家最常见词 | — | — |
| 2021 | DEMix (Gururangan 等) `[摘要]`；2022 Branch-Train-Merge | LM | 按领域**构造**专家（非自发） | — | — | — |
| 2022 | ST-MoE (Zoph 等) §7 | 编码器-解码器 | 编码器专家：哨兵、标点、连词冠词、动词、专名、数字；多语不按语言分；解码器无专精 | 每专家 top token | 编码器 vs 解码器 | — |
| 2022 | NLLB-200 §8 `[节]` | 202 语翻译 | 早编码 / 晚解码层按语言分专家；同语系、同文字、地理相邻的语言共享专家 | 每语言路由向量 → UMAP / 相似度 | 层位置 | — |
| 2022 | MoEfication (Zhang 等) `[摘要]`；2023 Emergent Modularity (Zhang 等) | 稠密 Transformer | 稠密 FFN 内自发出现功能分区；功能专家在训练 15% 左右稳定 | 神经元共激活聚类 | 稠密 vs MoE | — |
| 2022 | StableMoE、X-MoE、Chen 等理论 | LM / 理论 | 路由波动；表示坍缩；专精由簇结构决定、分配由初始化决定 | — | — | 理论上提到 |
| 2022 | Pavlitskaya 等 (CNN-MoE) `[摘要]` | 图像 | 专家按子领域（花 / 动物）、按物体尺寸专精；软 / 硬约束改变专精 | 专家 × 类别 | 约束方式 | — |
| 2024 | Mixtral §5 | LM | 无主题专精；"self"、缩进固定专家；连续 token 同专家；句法味 | 按 Pile 子集的专家分布 | — | — |
| 2024 | OpenMoE §4 | LM | token-ID 路由、warmup 后固定、末尾 drop | 路由饱和率 | — | — |
| 2024 | DeepSeekMoE §4.5 `[节]` | LM | 禁用 top 路由专家损失上升更快 = 冗余更低；共享专家不可替代 | 消融曲线 | 与 GShard×1.5 对比 | — |
| 2024 | OLMoE §5 | LM | 1% 训练后路由 60% 饱和；按领域与词表专精；upcycling 无专精 | 饱和率、专家 × 领域 | 从头 vs upcycled | — |
| 2024 | Lo 等 "A Closer Look" (Findings NAACL 2025) `[摘要]` | 公开 MoE | 神经元是细粒度专家；路由偏向大输出范数；深层专家更多样 | 专家相似度、范数 | 3 个模型 | — |
| 2024 | Antoine, Béchet, Langlais (POS sensitivity) `[全文]` | 6 个公开 MoE | 各模型 POS 专精高于均匀 +25（Mixtral）～ +36（OLMoE）；路径 MLP 预测 POS .72–.88；标点 / 符号最专精；OLMoE 聚类最散 | Spec = top-k 专家承担比例 − 均匀；KL(专家 POS 分布‖语料)；路径探针 | **6 模型横比** | — |
| 2024 | Fan, Messmer, Jaggi `[摘要]` | GPT-2 small 自训 | 冻结随机路由器 ≈ 学习路由器 | 困惑度 | 路由可学 vs 冻结 | — |
| 2024 | Tang 等 (ACL)、Kojima 等 (NAACL) `[摘要]` | 稠密 LLM | 语言特异神经元集中在首尾层 | LAPE 熵 | 稠密对照 | — |
| 2025 | Olson 等 (semantic routing) | 公开 MoE | 同词不同义 → 专家重叠下降，随规模增强 | 专家重叠 | 规模 | — |
| 2025 | Demons in the Detail (Qwen, ACL) | 自训 | micro-batch 均衡抑制领域专精，全局均衡恢复 | 专家 × 领域 | 均衡作用域 | — |
| 2025 | Monet；MoE-X；Standing Committee (ACL 2026)；Hidden Collaboration `[摘要]`；知识归因 | 公开 / 自训 | 单义专家；跨领域不变核心；跨层协作簇；共享专家做通用 | 各自 | — | — |
| 2026 | Expert Strikes Back (ICML)；RouterInterp (ICML) | 公开 MoE | 专家比稠密 FFN 更单义；专家 = 多个不相关微领域的叠加 | 神经元单义度；SSH 预测 | 多模型 | — |
| 2026 | Myth of Expert Specialization；Routers Learn Geometry (NeurIPS)；Geometric Routing | 公开 / 自训 | 路由反映几何；router–专家耦合；早层频率、深层句法 | 几何相似 → 路由相似 | — | — |
| 2026 | **Equifinality in MoE** | 自训，2 seed | 路由拓扑不决定困惑度；跨 seed 功能重叠 500 倍随机 | 功能重叠（随机基线） | — | **2 seed** |
| 2026 | Causal Audit；预注册前沿 MoE | 公开 | 观察指标不预测消融重要性；6 个预注册模块只剩 1 个 | 消融 | — | — |
| 2026 | Multilingual Routing (ICLR)；2601.14050；Language Routing Isolation 2604.03592 `[节]`；2605.29714 | 公开多语 MoE | 首尾层语言特异、中层共享（Qwen3-30B 与英语的 Jaccard：孟加拉 .12/.22/.05，俄 .41/.43/.17）；高低资源语言专家集几乎正交；同语系更相似 | top-K 专家集 Jaccard | 语言 × 层 | — |
| 2026 | Do Domain-specific Experts Exist (2604.05267) `[摘要+节]` | 10 个公开 MoE，3.8B–120B | 都存在领域专家，约 1% 专家；放大它们可提升领域成绩 | 梯度 × 路由的 token 评分 | **10 模型** | — |
| 2026 | DBES (2605.18498) `[节]` | Qwen3 / GLM-4.6 / DeepSeek-R1 | Qwen 系"模块化"（领域隔离高），DeepSeek / GLM"分布式协作" | 路由专精 KL、有效秩、领域隔离余弦、路由刚度、n-gram 路径持续 | **多模型** | — |
| 2026 | Goodfire 2604.17837 | 6 个公开 MoE | 低维控制子空间驱动路由，编码抽象功能；跨层专家路径单义 | 路径聚类 | 多模型 | — |
| 2026 | 2605.16349 `[摘要]` | Mistral / Qwen | 专家 Jacobian 去相关但表示子空间重叠；top-k 比 soft 分得更开 | Jacobian 对齐、Grassmann 距离 | 路由稀疏度 | — |
| 2026 | **我们 (E167–E171)** | 自训 9 run | 扣地板后深层切法一致 .28（重跑 .50）；词类 .86 → 切法 .48 → 逐 token .19；第 100–200 步定型 | 置换不变划分一致 T_D、Hungarian 指纹相关、逐 token 因果角色 | 配对类型 × 层 × 粒度 × 时间 | **9 run** |

## 2. 度量目录：专精度与一致度是两件事

**(A) 单模型"专精度"**（文献主体；回答"专家有没有分工"）

| 尺度 | 定义 | 出处 | 备注 |
|---|---|---|---|
| 每专家 top token / 上下文表 | 按门控值排序 | Shazeer 2017、BASE、ST-MoE、Mixtral | 定性 |
| 专家 × 类别 / 领域 / 语言矩阵 | 路由权重或计数 | V-MoE、OLMoE、NLLB、Kudugunta | 可视化为主 |
| Spec_POS,l | 承担该词类最多的 top-k 专家吃掉的比例，减去均匀期望 U | Antoine 2024 | U 随 k / 专家数变，跨模型要看 ΔU |
| KL(专家分布 ‖ 语料分布) | 每专家的词类分布偏离语料 | Antoine 2024 | 无上界，难解释 |
| 路由专精 S_spec | KL(领域内专家使用 ‖ 均匀) | DBES | 与负载均衡目标相反 |
| 领域隔离 S_iso | 不同领域路由分布的余弦正交度 | DBES | "模块化 vs 分布式" |
| 有效秩 R_eff | 路由矩阵奇异值的有效维数 | DBES | 低 = 秩坍缩 |
| n-gram 路径持续 | 滑窗内至少一个专家持续激活的概率 | DBES | 序列级 |
| 语言 Jaccard | 两语言 top-K 专家集的交并比 | 2604.03592 | 按层分 |
| 路径探针 | 用 (层 × k) 专家 id 预测 POS / 功能 | Antoine 2024、Goodfire 2026 | 探针上限受词形基线 .91 约束 |
| 消融冗余 | 禁用 top 专家的损失曲线 | DeepSeekMoE、Causal Audit | 因果 |
| 神经元单义度 | 专家内神经元的激活语义纯度 | Expert Strikes Back | — |

**(B) 跨模型"一致度"**（只有 Equifinality 与我们；回答"分工是不是同一套"）。专家编号在不同训练里无对应，必须二选一：

1. **先配对再比**：Hungarian 对齐指纹（我们的 R4 route / drop 指纹；Equifinality 的功能重叠），或权重置换对齐（LMC of MoE）。缺点：配对质量本身是变量。
2. **置换不变量**：不问"哪个专家"，只问"这两个 token 是否同组"——我们的 T_lex / T_ctx / T_D（同词形的上下文对的划分一致，减未训练地板）。优点：不依赖配对；缺点：粗粒度（见不到具体专家）。
3. **分析结论的一致**：同一种 (A) 类分析分别跑在各模型上，比较其输出剖面（我们的 83 词分离度剖面 .85–.92、"哪些词的功能被路由暴露" .85）。这是导师第 12 条的直接形式。

**(A) 与 (B) 的关系要讲清楚：**专精度高不等于一致度高。两个 seed 可以都高度按词类专精、却把词类切成不同的组合；也可以专精度一般、但切法相同。Antoine 报告 OLMoE 专精最低，Equifinality 报告跨 seed 重叠 500 倍随机，两者说的不是一回事。

## 3. 谁做过"模型 A 高、模型 B 低"

| 对比轴 | 工作 | 结果 | 比的是 |
|---|---|---|---|
| 公开模型族 | Antoine 2024 | ΔU +25（Mixtral）～ +36（OLMoE）；路径探针 OLMoE 最低 .72 | 专精度 |
| 公开模型族 | DBES 2026 | Qwen 模块化、DeepSeek / GLM 分布式 | 专精度 |
| 公开模型族 | 2604.05267 | 10 个模型都有约 1% 领域专家 | 专精度 |
| 规模 | Olson 2025 | 语义路由随规模增强 | 专精度 |
| 编码器 vs 解码器 | ST-MoE、Kudugunta | 编码器分、解码器不分 / 按任务分 | 专精度 |
| 从头 vs upcycled | OLMoE | upcycled 几乎无专精 | 专精度 |
| 负载均衡作用域 | Demons in the Detail | 全局均衡 → 领域专精出现 | 专精度 |
| 软 / 硬约束；top-k vs soft | Pavlitskaya 2022；2605.16349 | 约束改变专精结构；top-k 分得更开 | 专精度 |
| 层深 | Eigen 2013、V-MoE、多语路由三篇、我们 | 浅层表面 / 位置 / 语言，深层类别 / 共享 | 专精度；我们是一致度 |
| 学习路由 vs 哈希 / 随机 / 冻结 | Hash Layers、THOR、Fan 2024、V-MoE 附录 | 小规模下不输；单层随机可容忍 | 损失 |
| 配对类型、粒度、时间 | 我们 | 重跑 .50 / 顺序 .45 / 初始化 .28；词类 .86 → 逐 token .19；100–200 步定型 | **一致度** |
| **模型类型 × 一致度** | 无 | — | — |

最后一行是空白：没有任何工作报告"一致度作为配方（均衡强度、专家粒度、top-k、路由可学性）的函数"。这正是导师第 8 条要的东西，也是我们能用 2 seed × 若干配置、每配置约 4 GPU 小时（训到 8 亿 token）填上的。

## 4. 给下次 Slack 的日文段落（草稿）

前回「MoE の解釈研究はほとんどない」と申し上げたのは不正確でした。専門家が何を分担するかの分析は、MoE の原点である Jacobs ら（1991）の what/where 課題から続いており、Shazeer ら（2017）以降の主要な MoE 論文はほぼ毎回「各専門家がどの語・品詞・言語を担当するか」を一節設けて報告しています（V-MoE、ST-MoE、NLLB-200、Mixtral、OLMoE など）。2024 年以降は複数の公開モデルを横断して専門化の度合いを比較する研究も出ています（Antoine ら 2024：6 モデルで品詞専門化、DBES 2026：Qwen は分離型・DeepSeek は分散型、など）。
ただし、これらはすべて「1 つのモデルの中で専門家がどれだけ偏っているか」を測っており、「独立に学習したモデル同士で分担が同じか」を測った研究は、2 seed の Equifinality（2026）と我々の 9 run 以外に見つかりませんでした。学習過程に沿って分担の一致を追った研究はありません。また、「一致度がモデルの設定（負荷分散の強さ、専門家の粒度、top-k、ルータを学習させるか固定するか）でどう変わるか」を報告した研究もなく、ここが先生のおっしゃる「このモデルでは低く、このモデルでは高い」を出せる空白だと考えています。

## 5. 未核对 / 可能有误
- Jacobs 1991 两篇、Jordan & Jacobs 1994、Yuksel 2012、BASE Layers 的分析细节凭记忆，未拿到原文。
- ST-MoE、Mixtral、OLMoE、OpenMoE 的条目来自此前的卡片，本次未重读。
- DBES 的理论部分（Bellman rank 等）质量存疑，只取其指标定义与模型对比。
- 2026 年 9 月以后的预印本可能有漏（本次 arXiv API 检索八组关键词，未覆盖"expert routing" + "seed"以外的措辞）。
