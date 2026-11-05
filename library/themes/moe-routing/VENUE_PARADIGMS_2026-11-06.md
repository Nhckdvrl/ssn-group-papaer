# 顶会范式卡：MoE 分析 / 分析稳健性 / 自训小模型受控比较（2026-11-06）

**用途：**让 division 主会话判断"一篇 MoE 分析或分析稳健性论文在 ACL / EMNLP / ICLR / ICML / NeurIPS 上长什么样、审稿人在哪一维打分"。只提炼范式并对照 `workbench/mechanism-population-dynamics/division/ADVISOR_PREFERENCES.md`；**不给本线结论、不定方向、不做新颖性判决**（AGENTS.md R6）。现成读数目录见同目录 `READOUT_CATALOGUE_AND_SEED_ROBUSTNESS_2026-11-06.md`（lit-v2），本卡不重复读数定义。

**证据标签：**`[全文]` 读完正文；`[节]` 读了摘要 + 图 1 + 方法 / 结果 / Limitations 中的相关段；`[摘要]` 只读摘要；`[评审-分数]` = PaperCopilot 数据里每位审稿人的分数向量（rating / soundness / contribution / confidence）；"未核对" = 没拿到。PDF 在会话 scratchpad，未进仓库。

**评审原话的缺口（要先说清楚）：**OpenReview 的 `api2` / `api` notes 接口与 forum 页面在 2026-11-06 都要求浏览器人机验证（`ChallengeRequiredError`），脚本和抓页工具拿不到评审正文；Claude in Chrome 未连接。所以**下表"评审最常问的 3 个问题 + 作者怎么答"全部未核对**，只用 `tools/venue_corpus/data/raw/*.json` 里的逐审稿人分数向量推断"在哪一维被扣分"，推断都标"推断"。ACL / EMNLP 走 ARR，评审本来就不公开。补救：人在浏览器里过一次验证后，按卡里的 forum id 拉 `notes?forum=<id>` 即可补齐。

## 0. 选样

- 语料检索：`query.py density` / `nearest` / `shapes`（命令与数字见 §4）；加 arXiv 全文。
- 收录 **18 篇已接收**（a 类 7、b 类 6、c 类 5）+ **5 份被拒 / 撤稿**（其中一篇有两次投稿）+ 3 篇 ACL / EMNLP 的 MoE 分析摘要作会场对照（§4）。
- 任务点名但**不在这五个会主会**、因此不收的：Dodge 2020（只有 arXiv）、McCoy 2020 "BERTs of a feather"（BlackboxNLP workshop）、Universal Neurons（Gurnee 2024，TMLR）、Antoine 2412.16971（语料中没有接收记录，未核对）、Equifinality 2604.14419（预印本）。OLMoE（ICLR 2025 Oral，分数 8;8;10）的分析节不算独立论文，只作参照。Makelov "interpretability illusion"（ICLR 2024）没拿到全文，不出卡。

## 1. 论文卡

列说明：**句式**（when / what / whether / how-much / 对比）；**轴** = 对比轴；**规模** = 模型数 × seed 数 × 参数量；**读数 / 参照**；**多大算大** = 怎么说效应大小；**图 1**；**措辞** = 标题级断言 / 条件句 / 描述；**Lim.** = Limitations 写了什么；**评审** = 分数向量（原话未核对）。

### (a) MoE 专家 / 路由分析

| # | 论文（会·年·证据） | 句式 | 轴 | 规模 | 读数 / 参照 | 多大算大 | 图 1 | 措辞 | Lim. | 评审 |
|---|---|---|---|---|---|---|---|---|---|---|
| a1 | The Illusion of Specialization / "Standing Committee"（**ACL 2026 main**，2601.03425）`[全文]` | whether：路由专家是否按领域专精 + what：委员会做什么 | 9 个 MMLU 领域 × 层（浅 / 中 / 深）× top-k ∈ {4,6,8,12,16} × 有无共享专家 | 3 个公开模型（OLMoE-1B-7B、DeepSeek-V2-Lite、Qwen3-30B-A3B）× 1 × 7B–30B；**无 seed** | 领域 top-k 专家集 Jaccard、ECI 的 Gini、silhouette、Pareto 委员会；参照只有"vs uniform"倍数（13–36×）；遮蔽实验无随机对照 | **只给数字**：Jaccard overall .87、Gini .90–.95；无区间、无随机地板 | 示意卡通：(a) 直觉"分而治之" vs (b) 观察到的共享 | 标题级（"Illusion"），摘要 "far less pervasive than commonly believed" | 只 3 个模型；"we do not systematically compare committee masking against alternative controls such as random or frequency-matched non-committee masking"；以 MMLU 为主 | ARR 不公开 |
| a2 | The Expert Strikes Back（**ICML 2026 poster**，2604.02178）`[节]` | 对比 / whether：MoE 神经元是否比稠密 FFN 更单义 | MoE vs dense（按 active 参数匹配、尽量同家族）× 路由稀疏度 | 12 个公开模型 × 1 | k-sparse probing F1、自动解释；参照 = 匹配的稠密模型 + Random Expert Baseline（同 N 随机抽的期望 JSD） | 对稠密的差；"95% confidence intervals around the mean estimate over concepts"（区间对概念取，不对训练取） | **主结果曲线**：best-layer F1 vs k，MoE 对 dense | 标题级 | 没有最大的 MoE（GPU 限制），"we expect our findings to" 外推 | 均分 3.25；原话未核对 |
| a3 | RouterInterp（**ICML 2026 poster**，2610.11775）`[节]` | whether：单领域假设 vs 叠加细粒度特征假设（SSH） | 两个假设对决；方法 vs unigram / bigram 基线 | gpt-oss-20b、OLMoE-1B-7B × 1 | SAE 特征预测路由的检测准确率；参照 = n-gram 解释基线（unigram .56 / bigram .63 等） | 相对基线："∼65% higher detection accuracy" | 两种假设的示意（点 = 样本，色块 = 领域） | 假设命名 + 方法命名 | 见库卡 `CONTROLLED_REPRODUCIBILITY_PAPER_CARDS_2026-10-25.md`：SAE 质量；"为何是这些组合"留开放 | soundness 2;3;2;3，conf 4;2;3;4 |
| a4 | Multilingual Routing in MoE（**ICLR 2026 poster**，2510.04694）`[节]` | how：路由随层 × 语言怎么变 + 与性能相关 + 干预 | 层 × 15+ 语言 × 资源高低；干预位置（中层 vs 首尾层） | 3 个公开模型 × 1 | 与英语平行句的路由散度；参照 = FLORES 通用基线、首尾层干预 / 多语专家干预（都掉分） | 相关系数；干预 "1-2% gains are remarkably consistent across two evaluation tasks, three models, and 15+ languages" | **主结果预览**：跨层散度曲线（高 / 中 / 低资源语言） | 描述 + 条件句（"generalization is limited by…"） | 未核对 | **2;6;6;8**（极分化），soundness 2;2;3;4 |
| a5 | Mixture of Parrots（**ICLR 2025 poster**，2410.19034）`[节]` | 对比 / how-much：固定 active 参数加专家，记忆与推理各涨多少 | 专家数 × 任务类型（知识 vs 推理） | **自训**一系列 MoE 与稠密（65B token）+ 合成图任务；seed 数未核对 | benchmark 准确率；参照 = 同 active / 同总参数的稠密；理论上下界（定理 3.2–3.6） | 曲线斜率差 + 定理 | 主结果三面板（world knowledge / commonsense / math vs 参数量） | 标题级 | 未核对 | 6;6;8;8，contribution 2;2;3;4 |
| a6 | Monet（**ICLR 2025 poster**，2412.04139）`[节]` | 方法型（架构）附解释证据 | 删去偏斜专家后各领域的变化 | 自训多规模 × 1 | 领域 MMLU 遗忘；参照 = Gemma Scope SAE、OLMoE 删最常用专家 | 相对基线的差 | 架构对比示意（PEER vs Monet-HD / VD） | 方法 + 描述 | "these criteria are basic and minimal"（专家挑选准则） | 6;6;8;8 |
| a7 | MoE-X（**ICML 2025 poster**，2503.07639）`[节]` | 方法型：为可解释性设计的宽稀疏 MoE | 架构（dense / wide-sparse / MoE-X）× 规模 | 自训 8 层 GPT-2（棋局）+ GPT-2 124M / 354M | 棋盘状态探针 F1、自动解释分；参照 = 稠密 MLP、SAE、Monet | 相对基线的差 | 架构示意 | 方法 | 未核对 | 分数缺 |

### (b) 分析结论的稳健性 / seed 方差

| # | 论文 | 句式 | 轴 | 规模 | 读数 / 参照 | 多大算大 | 图 1 | 措辞 | Lim. | 评审 |
|---|---|---|---|---|---|---|---|---|---|---|
| b1 | The MultiBERTs（**ICLR 2022**，2106.16163）`[节]` §1、§3–4 | whether：对单个 checkpoint 的结论能否推广到"训练程序" | 预训练 seed × 干预（CDA-full vs CDA-incr） | BERT-Base × **25 seed**（另 5 个 × 28 个中间 ckpt） | GLUE、Winogender 偏见相关；参照 = 原版 BERT（图 1 虚线） | **Multi-Bootstrap**（对 seed 与样本同时重采样）给区间与 p：偏见 "δ = −0.162 with p = 0.001"；准确率 .622 vs .623，p = .416 | 25 个 seed 的 GLUE 分布 + 原版虚线 | 资源 + 统计方法；"effects that may not be detected with a single checkpoint" | 未核对 | v1 接口被拦，未核对 |
| b2 | PolyPythias（**ICLR 2025 poster**，2503.09543）`[节]` | how / what：换 seed 时什么稳定、谁是离群 | seed × 5 个规模（14M–410M）× 训练步 | **45 个新 run**（9 seed × 5 规模）+ 原 5 个；约 7k ckpt | 下游、inter-seed agreement、self-consistency、语言表示、训练阶段 | **中位数 + IQR**、跨 seed 标准差；"highly consistent training dynamics" | 主结果曲线：准确率 / 一致率随规模（中位 + IQR） | 描述 | 未核对 | 6;6;6;8，contribution 全 3 |
| b3 | Convergence and Divergence under Different Random Seeds（**EMNLP 2025 main**，2509.26643）`[全文]` | **when**：跨 seed 的收敛何时升、何时降；随规模与词类怎么变 | 训练步 × 规模（5 个）× 词频 / 词类 / 终点 surprisal | PolyPythia 5 规模 × 5 seed；复现于 MultiBERTs | 期望逐词 KL（跨 seed）；参照 = step 0（初始化即地板）、unigram 分布、ICL 分数；BLiMP 第二读数 | 1σ 区间；与初始化比（"final-step convergence … may be worse than at initialisation"）；混杂用回归分开（§D） | **主结果曲线**：E[conv] vs 步数 + 对齐的 unigram-KL / ICL / loss 面板 | 描述 + 四阶段命名 | token 级 KL 不能跨分词器比 | ARR 不公开 |
| b4 | SAEs Trained on the Same Data Learn Different Features（**ICLR 2026 poster**，2501.16615）`[节]` | whether：SAE 特征是否唯一 | SAE seed × 架构（ReLU-L1 vs TopK）× 层 × 3 个 LLM × 2 数据集 | 每设定 2+ seed | Hungarian 匹配后的编码 / 解码余弦，两侧都 ≥ 0.7 算"共享"；参照 = 置换 SAE（同一函数应判同） | 阈值后的比例："only 30% of the features were shared" | 匹配余弦的密度图（编码 × 解码） | 标题级 | 未核对 | **2;4;8;8**（极分化），contribution 2;2;3;4 |
| b5 | Quantifying LLM Attention-Head Stability（**ICML 2026 poster**，2602.16740）`[节]` | how：注意力头跨重训多相似，随层 / 深度 / 权重衰减 | 26 种架构配置 × 层 × 优化器设置 | GPT-2-small 级 × 每配置 5 次重训 | 置换不变的 max-matched 注意力分数相似度；残差流作对照 | 层间曲线（中间层最分化） | 流程示意 | 条件句（"Implications for circuit universality"） | 未核对 | soundness 2;3;3;4 |
| b6 | Linear Connectivity Reveals Generalization Strategies（Juneja，**ICLR 2023**，2205.12411）`[节]` | whether / what：同样微调的模型是否线性连通；簇对应什么泛化策略 | 微调 seed 对 × 任务（MNLI / QQP / CoLA） | BERT 微调 × 多 seed（数目未核对） | 插值路径上的 loss 壁垒；参照 = 诊断集（HANS 等） | 壁垒高度 + 簇划分 | 模型两两连线的 loss 面热图 | 标题级（"reveals"） | 未核对 | 未核对 |

### (c) 自训小模型受控比较

| # | 论文 | 句式 | 轴 | 规模 | 读数 / 参照 | 多大算大 | 图 1 | 措辞 | Lim. | 评审 |
|---|---|---|---|---|---|---|---|---|---|---|
| c1 | The Early Phase of NN Training（Frankle，**ICLR 2020**，2002.10365）`[节]` | what：早期几百步网络发生了什么 | 回卷步 × 扰动类型（保号重初始化、置换、模糊输入预训练） | ResNet / CIFAR × 5 seed | IMP 稀疏网的准确率；参照 = 不扰动的回卷、随机重初始化 | 跨 5 seed 的均值与区间 | 主结果曲线：准确率 vs 回卷步 | 描述 | 未核对 | 未核对 |
| c2 | Pythia（**ICML 2023**，2304.01373）`[节]` | 资源 + 案例：数据顺序 / 频率如何影响记忆、偏见 | 规模（70M–12B）× 去重 × 训练步 | 16 个模型 × 154 ckpt，**同数据顺序**（数目凭记忆，未逐一核对） | 记忆率、CrowS-Pairs、词频效应；参照 = 干预前 | 案例里的差与过程模型（泊松） | 干预后的性别偏见曲线 | 资源 + 描述 | 未核对 | 未核对 |
| c3 | Sudden Drops in the Loss（**ICLR 2024**，2309.07311）`[节]` | **when** + whether 必要：句法注意结构何时出现、是否必要 | 训练步 × 训练中正则（压制 / 促进 SAS） | BERT-base × 3 seed | 句法头 UAS、loss、BLiMP；参照 = 压制 / 促进 SAS 的 run | 时间对齐 + 干预前后差 | 时间线：SAS 突增与 loss 骤降同窗 | 标题级 + 因果 | 回应"单 checkpoint 探针的局限" | 未核对 |
| c4 | Crosscoding Through Time（**ACL 2026 main**，2509.05291）`[节]` | **when**：语言特征何时出现、巩固 | checkpoint 三元组 × 任务（主谓一致等）× 规模 | 公开 ckpt（OLMo / Pythia）；crosscoder 3 seed | RelIE（相对间接效应）；参照 = 近随机早期 ckpt | 描述 + 表 | 流程示意 | 描述 | 未核对 | ARR 不公开 |
| c5 | On LMC of MoE Architectures（**NeurIPS 2025 Oral**，2509.11348）`[节]` | whether：独立训练的 MoE 置换后是否线性连通 | 架构 × 数据 × 匹配算法 | GPT-2 / ViT × 3 初始化 | 插值 loss 壁垒；参照 = 不匹配 | 壁垒近 0 + 理论 | 未核对 | 定理 + 描述 | 见库卡 | 5;5;5;5 |

### 被拒 / 撤稿（反例）

| # | 论文（ICLR） | 形态 | 分数向量 rating / soundness / contribution | 推断的扣分维度（原话未核对） |
|---|---|---|---|---|
| r1 | Quantifying Expert Specialization for Effective Pruning（2026 撤稿）`[摘要]` | 自造指标 ESI + 2 个公开 MoE（Mixtral、Qwen1.5-MoE）推出"architecture-strategy fit" | 2;4;4;6 / 2;3;3;2 / 2;2;3;2，conf 5;5;4;3 | 两维都低：2 个模型撑一条规律；自造指标没有和现成尺度并报 |
| r2 | Incidental Polysemanticity（2025 拒）`[摘要]` | 理论 + 玩具模型：多义性可由初始化偶然产生 | 5;6;6 / **3;3;3** / 2;2;3 | soundness 不差，**contribution** 低："对真实模型意味着什么"没交代 |
| r3 | Sparse Autoencoders Reveal Universal Feature Spaces Across LLMs（2025 拒 5;5;6;8）→ 改名 Measuring SAE Feature Space Similarities Across LLMs（2026 撤稿 2;4;6）`[摘要]` | 跨模型 SAE 空间相似（旋转不变）→ 普遍性 | 2025：soundness 3;2;2;3；2026：**1;3;3** / 1;2;3 | 断言（普遍性）大于证据；第二次投稿分数反而更低。对照 b4：同一题材，接收的是"控制 seed、结论与普遍性相反、范围限在 SAE" |
| r4 | Beyond Parameter Count: Implicit Bias in Soft MoE（2025 拒）`[摘要]` | 理论 + 实验 | 3;3;5;6 / **1;2;3;3** / 1;2;2;3 | soundness：证明 / 实验对结论支撑不足 |
| r5 | Beyond Anecdotal Evidence: Framework for Evaluating Neuron Interpretability（2026 拒）`[摘要]` | 评测框架 | 2;4;4 / 2;3;2 / **1;2;2** | contribution：框架本身不带新发现 |

另有"接收但极分化"的三篇可作边界：a4（2;6;6;8）、b4（2;4;8;8）、Not All Models Suit Expert Offloading（ICLR 2026 poster，4;4;6，soundness 2;2;3）`[评审-分数]`。

## 2. 共同范式（从上表归纳，不预设）

- **P1 一条对比轴写进摘要，主结果是轴上的函数。**除两篇方法型（a6 a7）外 16 篇都有：规模 / 训练步（b2 b3 c2 c3 c4）、稀疏度（a2）、层 × 语言（a4）、专家数（a5）、SAE 架构（b4）、配置（b5）。连 a1 这种只用 3 个公开模型的 ACL 论文也把"领域 × 层 × k"作轴。单点数字几乎不出现在摘要里。`[全文][节]`
- **P2 每个读数配一个"0 是什么"的参照。**形式各异：匹配的稠密模型（a2 a5）、n-gram 基线（a3）、随机专家（a2）、初始化时刻（b3）、原版发布（b1）、置换对照（b4 b5）。缺参照的 a1 在 Limitations 里自己承认缺随机 / 频率匹配对照——ACL 照收，但这是它唯一被反复写明的短板。`[全文][节]`
- **P3 稳健性类论文把不确定性放在"训练 run"上，MoE 分析类放在"样本 / 概念"上。**b1 Multi-Bootstrap、b2 中位数 + IQR、b3 1σ、c1 5 seed；a1–a4 全部是公开模型单 seed，区间（若有）只对概念或语言取。也就是说，"同一 MoE 分析结论换 seed 还成不成立"在 a 类里没有任何一篇测过（a1–a4 都是单 seed）。`[节]`（这是对样本的描述，不是新颖性判决。）
- **P4 图 1 两种形态：主结果曲线（沿对比轴），或两个假设的对照示意。**曲线：a2 a4 a5 b1 b2 b3 c1 c3；假设示意：a1 a3；方法论文是架构图（a6 a7）。没有一篇用流程图之外的"花哨"图 1 承载主张。`[节]`
- **P5 标题级断言多为"推翻一个常见假设"，正文退回描述。**a1 "Illusion"、a2 "Strikes Back"、a5、b4 "Learn Different Features"、b6 "Reveals"、c3。资源型（b1 b2 c2）与 when 型（b3 c4）用描述性标题。断言的对象都是**一个具体、领域里有人持有的信念**（"专家按领域专精"、"SAE 找到真特征"、"MoE 与稠密同样难解释"）。`[全文][节]`
- **P6 观察为主，常附一个"轻干预"作旁证，而不是主证据。**a1 遮蔽、a4 路由 steering、a6 删专家、c3 训练中压制 SAS；纯观察就被接收的：b2 b3 b4 b5 c4。干预在 a 类里几乎都在最后一节、数字小（a4 是 1–2%）。`[节][全文]`
- **P7 外部效度靠"多模型"或"多规模"二选一。**分析公开模型的写 3–12 个模型（a1 a2 a4）；自训受控的写同一架构 × 多 seed × 多规模（b2 5 规模、b3 5 规模 + MultiBERTs 复现、b5 26 配置）。只有一个规模、没有第二套模型的，在样本里只出现在带理论的论文（a5、c5）。`[节]`
- **P8 释放 run / ckpt / 统计工具本身算贡献。**b1、b2、c2 的主贡献之一是资源；b1 还附统计库。ICLR / ICML 认这一类。`[节]`

## 3. 范式 × 导师偏好

| 导师偏好 | 对应范式 | 关系 | 顶会额外要求（样本里看到的） |
|---|---|---|---|
| A1 数字是某变量的函数 | P1 | **一致**，几乎是硬门槛 | 轴要在摘要里点名；轴最好是领域公认的（规模、训练步、稀疏度、语言） |
| A2 多大算大要有参照 | P2、P3 | **一致** | 还要**跨 run 的不确定性**（b1 bootstrap、b2 IQR、b3 1σ）；分析公开模型的论文则给概念级 95% 区间 |
| A3 尺度要有文献依据 | P2 | **一致** | 自造读数要写为什么不用现成的（b3 脚注说明为何用 KL 而非跨 seed 相关）；r1 的自造指标无此论证 |
| A4 先核文献 | — | **一致** | a1 正文第一张表就是"与已有 MoE 解释工作对比"；ACL 论文的定位表放正文 |
| A5 时间可落地 | P7 | 顶会不问 | 小模型可接受，前提是有规模轴或理论（b2 14M–410M、b3、c3 BERT-base） |
| B1 观察胜于干预 | P6 | **大体一致**：纯观察的稳健性论文能中（b2 b3 b4 b5） | MoE 分析类常附一个轻干预作旁证（a1 a4 a6）；c3 这种 when 论文用训练中干预回答"是否必要" |
| B2 只换 seed 的受控比较 | P3、P7 | **一致**（b1 b2 b3 b5 都是这个设计） | 同时要**规模轴或第二套模型**（b3 在 MultiBERTs 上复现） |
| B3 第二把尺子 | P2 | **一致** | b3 KL + BLiMP；b4 编码 + 解码两侧；b2 多读数并列 |
| B4 模型内类别对比 | P1 | **一致**（b3 按词频 / 词类 / surprisal 分） | 要处理类别之间的混杂：b3 用回归把词频与词类分开（§D） |
| B5 语言轴 | P1 | 一致（a4 ICLR 2026） | a4 用公开多语模型与平行语料；自训多语的样本里没有 |
| B6 借现成分析法，看结论跨模型是否一致 | P3、P5 | **一致**：b1（偏见结论跨 seed）、b4（SAE 特征）、b5（电路普遍性）都是这个句式 | 顶会把它写成"一个常见假设 / 常用方法在换 seed 后不成立（或成立到什么程度）"，标题级；还要说**对使用者意味着什么**（b4 "pragmatically useful decomposition"、b5 "circuit universality"） |
| B7 先专家再 heads | — | 无对应 | — |
| C1 要命题不要现象 | P5 | **一致**：标题级断言都针对一个具体信念 | — |

**小结：**A1 A2 A3 A4 B2 B3 B4 B6 与顶会范式一致；顶会**额外**要求的是 ① 跨 run 的不确定性表示，② 规模轴或第二套模型的外部效度，③ 一句针对具体信念的标题级主张，④ 对使用者的后果（"so what"），⑤（MoE 分析类常见）一个轻干预旁证，⑥（可选）释放 run / 工具。

## 4. 会场差异与接收密度

**命令（2026-11-06，本地语料）：**
- `density "mixture[- ]of[- ]experts?|\bMoEs?\b"`：全部 MoE 接收数 ACL25 24 / ACL26 38 / EMNLP24 14 / EMNLP25 22；ICLR25 52（切片率 35% vs 基准 32%）/ ICLR26 94（27% vs 27%）/ ICML25 44 / ICML26 148 / NeurIPS24 40 / NeurIPS25 84。
- 再 AND `\b(analy[sz]|understand|interpretab|specializ|specialis)` 且 NOT `we propose|we introduce|novel (method|framework|architecture)`（粗略的"分析型 MoE"）：ACL25 2 / ACL26 3 / EMNLP24 3 / EMNLP25 0 / NAACL25 0；ICLR25 10（**56% vs 32%**）/ ICLR26 9（29% vs 27%）/ ICML25 7 / ICML26 7 / NeurIPS24 3 / NeurIPS25 7。
- seed 方差切片（`(random|different|multiple|independent) (seeds?|initiali[sz]ations?)|seed variance|across seeds|training runs` AND `interpret|analysis|representation|mechanis|circuit|neuron|feature`）：ACL25 0 / ACL26 1 / EMNLP24 1 / EMNLP25 1；ICLR25 9（32% vs 32%）/ ICLR26 10（25% vs 27%）/ ICML25 5 / ICML26 14 / NeurIPS24 6 / NeurIPS25 7。
- `shapes`（ICLR，MoE ∧ 分析词）：接收 n=77 均分 5.81，finding 线索 25%、theory 18%、failure 21%；被拒 n=107 均分 4.25，finding 15%、theory 11%、failure 29%。seed / 普遍性切片：接收 finding 31% vs 被拒 30%，几乎无差。
- 正则是粗筛，数字只作地图（venue_corpus README）。ICML / NeurIPS 只有接收列表，没有切片接收率。

**ACL / EMNLP 对 MoE 分析的样子**（a1、c4、b3 + 三篇摘要 `[摘要]`：Decoding Knowledge Attribution in MoE（ACL 2025，3 个 MoE 对 3 个稠密）、Context Faithfulness 专家（EMNLP 2025，分析 → 微调方法）、Seeing but Not Thinking: Routing Distraction（ACL 2026，现象 → 假设 → 验证））：
- 公开模型 2–3 个、单 seed、描述性读数就能中（a1）；分析常接一个"用法"（微调、干预、假设验证）。
- 语言学钩子是加分项：词类（b3）、主谓一致等语言现象（c4）、多语言。
- Limitations 是 ARR 必填节，接收论文会主动写缺什么对照（a1）。
- 绝对数量少：严格"分析型 MoE"每届 0–3 篇；seed 方差类每届 0–1 篇（b3 是其中之一）。

**ICLR / ICML / NeurIPS 对 MoE 分析的样子**（a2–a7、c5）：
- 更常带理论（a5 定理、c5 LMC 证明）或自训受控（a5 a6 a7），或 12 个模型级别的广度（a2）。
- 不确定性和匹配基线更常见（a2 95% 区间 + 随机专家 + 匹配稠密）。
- 方法型（架构）论文挂"可解释"名义也算在这一类（a6 a7），分析是其证据节。
- 稳健性 / seed 方差类在 ICLR 有固定位置（b1 b2 b4），在 ICML 2026 数量最多（14）；切片接收率与全会基准持平（不受特别青睐，也不吃亏）。
- ICLR 2025 的分析型 MoE 切片接收率明显高于基准（56% vs 32%），到 2026 回落到基准（29% vs 27%）。

## 5. 被拒死因（推断，评审原话未核对）

1. **贡献维度低而 soundness 不低**：r2（soundness 3;3;3、contribution 2;2;3）、r5（contribution 1;2;2）——玩具模型 / 框架没有交代对真实模型或使用者的后果。
2. **断言大于证据**：r3 两次投稿都主张"跨 LLM 普遍"，soundness 降到 1;3;3；r4 soundness 1;2;3;3。对照接收的 b4：同题材，主张收窄、控制 seed、结论反向。
3. **模型太少 + 自造指标没有参照**：r1 两个公开模型推出一条"架构–策略匹配"规律，ESI 没与现成尺度并报。
（并列观察：极分化的接收 a4、b4 都有一位审稿人给 2，说明这两类题材的评审口径本身不统一。）

## 6. 未核对清单

- 全部评审原话与作者回复（OpenReview 浏览器验证；ARR 不公开）。forum id：MultiBERTs `K0E_F0gFDgA`；PolyPythias `bmrYu2Ekdz`；SAE same data `EjInprGpk9`；Multilingual Routing `ZoZR0x7tTD`；Monet `1Ogw1SHY3p`；Parrots `9XETcRsufZ`；OLMoE `xXTkbTBmqq`；LMC of MoE `RF3miSqdXa`；RouterInterp `rDNCWfRd69`；Head Stability `UXzfLdXrBJ`；MoE-X `6QERrXMLP2`；r1 `9lOqGhCjtL`；r2 `OeHSkJ58TG`；r3(2026) `gM6hJRzCtR`；r4 `aw2Jc5DFZC`；r5 `dWVWQN3sPt`；Local Routing `2XMAUP74ig`。
- b1 b2 b5 b6 c1 c2 的 Limitations；a5 a7 的 seed 数；b6 的模型数；c5 的图 1。
- MultiBERTs、Frankle、Juneja、Sudden Drops、Pythia 的会议档次（oral / spotlight）凭记忆，未逐一核对。
