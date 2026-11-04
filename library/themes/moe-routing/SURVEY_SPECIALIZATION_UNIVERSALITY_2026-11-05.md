# MoE 专家专精与跨训练普遍性：文献精读笔记（2026-11-05）

> 配合 `workbench/mechanism-population-dynamics/division/SURVEY_AND_DIRECTIONS_2026-11-05.md` 使用。精读 16 篇、摘要级扫描 36 篇；PDF 本地转文本后阅读，数字以原文为准。每条写：做了什么 → 主张与尺度 → 对我们的含义。


## 2606.25092 How Modular Is a Frontier MoE? (Transformer Lab, Jun 2026, arXiv)
- 问题：专家是否构成"能力/语言模块"。方法：routing-mass atlas → 预注册 6 个 family→axis 假设 → 推理时消融（router mask）vs 同规模随机专家 null → 选择性判据（最差 off-target ≤ 1/3 on-target）→ 4 个指标 × 2 语料 × bootstrap。
- 结论尺度：**"只有 1/6（阿拉伯语）是稳健模块；其余的模块性随语料/指标/统计门槛翻转"**。"routing mass 不预测因果重要性"：high-mass shared core 因果上冗余（mask 32 个最共享专家 MMLU-Pro 只掉 .11）。
- 写法：结论硬（"mostly dissolves"），同时明说单模型、不做 base-rate 推广；所有数字带 CI；正对照（Qwen3 恢复已发表的 disjoint 结构）。
- 对我们的启示：(1) 他们把"测量作为变量"本身当成贡献——与我们"三个分母"同构，但他们表述为**一个判决 + 判决如何随测量翻转**，不是"部分一致"。(2) representational 轴（脚本/词汇）比 computational 轴（math/code）更容易成模块——与我们"语法层重现、具体实现不重现"同向。(3) 他们缺的正是"跨训练"维度：单模型。

## 2604.09780 Myth of Expert Specialization (JHU, Apr 2026)
- 主张：router 线性 ⇒ 隐状态相似则路由相似（Prop.1 数据几何 Lipschitz 上界）；专精是表示几何的涌现性质。Prop.2：负载均衡迫使 router 抑制共享方向（解释 Qiu 2025 小 batch 专精塌缩）。三个"难解释"现象：不同模型解同一题专家重叠 ~60% ≈ 同模型不同题；prefill 路由不预测 rollout；深层 prefill 下不相关输入专家几乎相同（router collapse，gpt-oss 推理模型）。
- 证据类型：5 个公开 MoE，观察性；一个不等式；无训练实验（自己承认 footnote 1）。
- 结论尺度：标题级否定（"Myth"），但正文是"至少和理解隐状态几何一样难"。
- 关键漏洞（我们可打）：Prop.1 只说"相似⇒相似"，三角形右侧（隐状态不同、路由可同可不同）正是切法自由度；他们没有跨 seed 同几何对照。我们 E169：几何 .95 相同而切法 .28–.50。但他们的"不同模型 60% ≈ 不同题"与我们"跨 init 具体实现 .06"同向。
- 他们点名的开放问题："unless an explicit objective is introduced, we should not expect hidden state / router logit space to have a metric aligned with human standards" ——我们的 E170 恰好说：对齐的是语法功能（线性可读的左文脉功能），不是语义/领域。这是一条可用的反题。

## 2604.14419 Equifinality in MoE (Uzhhorod, Apr 2026, preprint)
- 主旨其实是"路由拓扑不决定 PPL"：自造 cosine-centroid 路由、1024 个 rank-1 专家、WikiText-103 76M、62 个实验；五种拓扑 TOST 等价（1 PPL 内）；hash/随机固定路由只差 1–2 PPL。"routing capacity > mechanism > topology ≈ composition ≫ expert capacity"。
- 跨 seed 部分只是 §5 一小节（Fig.5）：2 个 seed，best-match 词表投影 Jaccard .13–.15 vs 随机 .0003（"500×"），权重余弦 .107≈随机 .116。→ "same functions, different weights"。
- 结论尺度：标题级强（"does not determine"），用等价检验 + 多 seed 给"无差异"以统计意义；跨 seed 那句是 slogan 式。
- 对我们：它占的是"功能重叠、权重不同"的口号；但 (a) 设定非标准（cosine、rank-1、WikiText 14 epoch），(b) 基线是随机匹配，(c) 没有扣词身份，(d) 没有上限。真正的核心主张（拓扑不重要、hash 路由只差 1–2 PPL）反而和我们的"路由切法自由度大"一致：**学到的切法不唯一，而且对 loss 几乎不重要**——这是我们该正面面对的问题：如果切法不决定质量，那"切法是否重现"为什么重要？必须回答"重现的那部分是否正是承载质量的部分"（hash 路由丢的 1–2 PPL 是什么？）。

## 2601.03425 Illusion of Specialization / Standing Committee (ACL 2026 main)
- 方法：CommitteeAudit——按 MMLU 9 个 domain 的平均路由权重（ECI）排序，跨 domain 出现率 >.8 且 Pareto（高均值、低方差）的专家为"常设委员会"。3 个公开模型。
- 数字：跨 domain top-k Jaccard .87（OLMoE）；Gini >.88；委员会 2–5 个专家吃掉 30–70% 路由质量；mask 委员会 MMLU .39→.03–.12。定性：委员会接 Which/What/Suppose/?/the/a/in（"推理框架 + 句法骨架"），领域术语分散在外围。
- 结论尺度：标题级否定 + 一个新名词（Standing Committee）+ 架构/训练建议（负载均衡与自然结构冲突）。证据全是观察性 + 一个无对照的 mask（自己在 Limitations 承认没有随机/频率匹配对照）。只在最后一个 token 上取路由（MMLU 选择题）。
- 对我们：它说"句法骨架是跨 domain 不变的核心"，我们说"句法功能是跨训练不变的部分"——两个"不变"轴正交（domain vs seed），可以合成一句更强的话：**语法骨架是 MoE 分工里唯一既跨领域又跨训练稳定的东西**。他们没有 seed 维度，也没有扣自然一致（句法 token 高频 → 任何路由器都会给它们固定专家）。

## 2604.04230 Three Phases of Expert Routing (单作者, Apr 2026)
- OLMoE 20 个 checkpoint + OpenMoE 6 个：拥塞系数 γ_eff 先升（5K–40K 步）、平台（100K–400K）、再降（400K–1.2M）；"早期优先均衡，后期优先质量"。隐式均衡是显式 aux loss 的 13×。
- 证据薄（量是 router 自己 logits 回归出来的），但写法值得学：一条随训练的非单调曲线 = 一个发现；"invisible to post-hoc analysis of converged models"是卖点。
- 对我们：我们有 8 个 run × 9 个 checkpoint 的完整路由轨迹，可以直接测"专精什么时候形成、什么时候冻结"，而且有跨 seed 维度（他们只有一条轨迹）。公开 checkpoint 只有 OLMoE/OpenMoE 一条线——这是我们自训平台的真实稀缺资源：**多条独立训练轨迹**。

## 2604.02178 The Expert Strikes Back (Hamburg, ICML 2026)
- 三个主张：(1) k-sparse probing：MoE 专家神经元比稠密 FFN 神经元更单义，稀疏度越高越单义（12 个模型、58 个概念，匹配激活参数量）；(2) 以"专家"为单位自动解释（explainer/scorer LLM，F1 >.8），Trigger–Target 因果归因验证；(3) 专家既非领域专家也非 token 处理器，而是"细粒度任务专家"（形态 → 句法 → 语义 → 格式 的层次），用 unembedding k-means 的 JSD 专精分数在 k=5000 远高于 k=10 来量化。
- 写法：三条清晰主张，每条一个图；"resolve the debate"这种强语气；Limitations 很短。
- 对我们：他们给了"专家是什么"的分类学（形态/句法/语义/操作），单模型。我们可以问：这四类里哪些跨训练重现？我们的数据恰好说：句法/形态类重现，具体操作类（哪些 token 依赖它）不重现。**这是把我们的结果挂到他们分类学上的方法**——用他们的自动标注管线给我们 8 个 run 的专家打标签，然后问"同一标签在另一个 run 里有没有对应专家"。这比 T_D 这种抽象量直观得多，而且是导师能听懂的形态。

## 2610.11775 RouterInterp / Superposed Specialisation Hypothesis (TU Wien + UK AISI, ICML 2026)
- 命题：DSH（专家=连贯领域）vs SSH（专家=互不相关的微领域的并集，"专家层面的叠加"）。证据：每个专家 top-20 预测性 SAE latent 落在 ~11 个语义簇（DSH 预测 1，随机 16.6）。方法：SAE latent → 路由预测 macro-F1 .73；RouterInterp 解释分 .49/.60，比 unigram 高 65%。
- 两个理论论证：干扰最小化（不相关特征共享一个专家干扰小）；小 batch 负载均衡迫使同一宏领域拆到不同专家。
- 关键开放问题（他们自己提的）："experts aggregate by input similarity or by functional similarity (same downstream transformation)?" ——**这正是我们 E170 能回答的东西**：可重现的切法沿左文脉已决定的语法功能组织 = functional similarity 的一种证据。
- 写法：提出一个有名字的假设（SSH），对立假设（DSH），给出可区分的预测（G=1 vs G→n），一个数字（11 vs 1 vs 16.6）。这是导师会认的形态。

## 2605.12476 Routers Learn the Geometry of Their Experts (Geva 组, NeurIPS 2026)
- 理论：router 行 r_i 与专家输入侧权重行对同一 token 收到 ∝x 的梯度 → 二者是同一路由历史的耦合累积器（正反馈）。实证：1B SMoE 自训 50B token，router 分数与专家 gate 激活相关 ρ=.43。aux loss 让 router 向量彼此相似 3×（.63 vs .18）；K-Means 质心路由（无参数）只差 2.6% PPL。
- 对我们：(1) 它给了"初始化印记在深层持久"的机制候选：路由历史自增强；(2) 它给了"切法不唯一"的机制：质心路由就够，说明切法是在线聚类，初始质心不同 → 不同的局部最优分割；(3) 他们**只有一条训练轨迹、没有 seed 对照**。我们可以直接检验"耦合累积"预测：同初始化的两个 run 深层共享更多是否因为早期路由历史相同——我们 E167 的 order 对（同 init 不同顺序）深层比 init 对高 .12–.17，恰是"历史不同但初始质心相同"。
- 另一个预测：aux-loss 强度调节专精——我们所有 run 用 aux .01 + 偏置均衡，这是一个未变的旋钮。

## 2606.10703 Causal Audit of Expert Importance (HPI, ICML 2026 PhilML workshop)
- 60 个 metric×layer 格子里没有一个观察性指标（利用率、激活范数、平均路由权重、std）预测逐 token 消融重要性（d<.23）；只有逐 token 路由权重在 OLMoE L15 有 d=.23。渐进消融：L0–9 去掉 8 个里 7 个激活专家 loss 只升 .083 nat；L15 去 2 个就 +.155。
- 结论尺度：标题级方法论警告（"observation ≠ intervention"），单一清晰的 null + 一个正对照。
- 对我们：(1) 早中层极度冗余 ⇒ 早中层的"分工"在因果上几乎不存在，分析分工重现应聚焦深层（我们也确实只在深层看到结构）；(2) 任何路由统计量（含我们的 T_D）都不等于因果重要性——我们的 E168 token-level 因果角色是对的方向，但它只有 .33 重跑上限，说明逐 token 因果读数本身噪声大。

## 2503.09543 PolyPythias (ICLR 2025)
- 资源论文：45 个新 run（9 seed × 5 尺寸 14M–410M，seed 同时改初始化与 batch 组成），7k checkpoint。发现：下游稳定、跨 seed 预测一致 κ≈.5；语言探针（PoS/Dep/NER…）跨 seed 相似、跨尺寸轨迹 r≈.99；HMM 训练地图找到异常 seed。
- 写法：三个大问题（下游 / 表示 / 参数动力学），每个一句"largely stable"；稳定性定义为跨 seed 标准差。它被接收的核心是资源 + 系统性，不是某个尖锐发现。
- 对我们：(1) 它没有拆开 init 与 data order（我们拆了）；(2) 它测的是"表示里有没有信息"，不是"分工/模块是否一致"；(3) 稠密模型。我们平台的差异化：MoE 显式模块 + init/order 分解 + 完全重跑对。

## 2509.26643 Convergence and Divergence under Different Seeds (EMNLP 2025)
- 一个干净的量（跨 seed 期望 KL）× 训练 × 尺寸 → 四阶段（均匀 → 急剧收敛[unigram 阶段] → 急剧发散[开始用上下文] → 缓慢再收敛[induction head 形成]）；小模型不再收敛；函数词/高频词收敛、内容词/低频词发散。
- 写法：**一个指标、一条曲线、四个有名字的阶段、与已知里程碑对齐**（unigram 阶段、induction heads）。短文（EMNLP 短/长？页数少）。结论尺度朴素但清晰："convergence is far from uniform"。
- 对我们：我们的重跑对 T_D 曲线（L11 .88 → .46 → .52 → .42 → .50；L0 .96 → .07 → .18）就是这种"先收敛后发散再缓慢回升"的 MoE 版本，而且我们有 init/order/rerun 三种对——**可以直接写成"MoE 分工的收敛—发散阶段图"**，对齐到 Fehlauer 的输出层阶段。深层 .42 → .50 的缓慢回升 = 他们的 slow reconvergence。这是把我们的"训练不稳定"从弱点变成现象的办法：发散本身是阶段。

## 2501.16615 SAEs on Same Data Learn Different Features (EleutherAI, ICLR 2026)
- SAE 只换 seed：Llama-3-8B 131K latent 只有 30% 共享；越大越不共享；共享的是高频 latent；孤儿 latent 也可解释。结论："SAE 的特征集是实用分解，不是模型'真正使用'的特征的唯一清单"。
- 写法：一个尖锐数字（30%）+ 一个哲学结论（没有唯一分解）。
- 对我们：MoE 的专家是模型自己学的"分解"，我们在问同样的问题——分解是否唯一。他们的答案"越细越不唯一、高频共享"与我们"越细越不重现、句法骨架（高频功能词）共享"一致。**可以把 MoE 专家 vs SAE 特征 vs 神经元的跨 seed 共享率并列成一张表**（神经元 1–5%，SAE 30%，MoE 深层切法 .28/.50，词类级 .81/.95）。

## 2401.12181 Universal Neurons in GPT2 (Gurnee et al., TMLR 2024)
- 5 个 seed 的 GPT2-small/medium；跨模型最大激活相关 − 随机旋转基线 > .5 ⇒ 1–5% 神经元"通用"。通用神经元更单义（高偏度、高峰度、大范数、负偏置）。分类学：unigram / 字母 / 前一 token / 位置 / 句法（否定、复数、动词形态）/ 语义（地名、子分布）。第二部分：权重层面的通用功能角色（预测/抑制/分区神经元、熵神经元、关头的神经元）。
- 写法：明确区分四种 universality（功能/算法/表示/实现）；用随机旋转作基线；"look for that which is universal"作为发现策略；主数字 1–5% 很尖锐。
- 对我们：(1) 他们的"通用神经元是什么"分类（句法/形态/位置/unigram）与我们"重现的切法沿语法组织"一致——跨 seed 共享的东西在所有粒度上都是语法/表层的；(2) 他们的基线思想（随机旋转基）就是我们 N1 的思路；(3) 他们没有训练动态、没有 init/order 分解。

## 2602.16740 Attention-Head Stability (Bali et al., ICML 2026)
- 26 种小架构（2–12 层）×（50 或 5）个 seed，注意力分数矩阵最佳匹配余弦 = 稳定性。发现：中层最不稳（L5 ≈ .70 vs L1 1.0）且最独特；越深中层越不稳；不稳的头更重要；AdamW（权重衰减）大幅提高稳定性；残差流比头稳定。
- 写法：五条 bullet 发现，每条一张图；"universality 的强弱版本"作为框架；一个可操作的旋钮（weight decay）。注意他们**没有未训练基线**——我们之前在头上吃过这个亏。
- 对我们：(1) 他们已经占了"头的跨 seed 稳定性地图"；我们做头只能是子集；(2) **权重衰减/优化器影响跨 seed 稳定性**——这是我们没动过的旋钮，也是"分工重现是否取决于训练配方"这个更大问题的入口；(3) "残差流比模块稳定"= 我们"几何 .95 同、切法不同"的头版本。

## 2509.05291 Crosscoding Through Time (EPFL, ACL 2026)
- 用 crosscoder 跨 checkpoint 对齐特征，RelIE 指标追踪哪个特征何时对任务（主谓一致）因果重要；Pythia/OLMo/BLOOM 三个家族；发现低层/不可解释特征消退、高层语法检测器涌现并增强；token/语言特异概念逐渐抽象为通用概念。
- 写法：**方法 + 一个语言学任务 + 三个模型家族 + "涌现/维持/消失"三种命运**。ACL 偏好这种"语言概念在训练中如何形成"的问题。
- 对我们：他们只跟一条训练轨迹；我们可以问 "同一个语法特征的**分工归属**（哪个专家负责）在不同 run 里何时固定"。而且我们的 E170 探针阶段 2 已经有"路由可解码性 ≈ 表示可解码性"（.80–.86 秩相关），可以做成"分工跟随表示涌现"的时间线。

## 2409.02060 OLMoE §5（路由分析部分）
- Router saturation：1% 训练（20B token）时 top-8 已有 ~60% 与终点相同；40% 时 ~80%；深层饱和更早，L0 最慢。Domain specialization：arXiv/GitHub 有专家接近 100%（L0）；Mixtral（upcycled）几乎没有领域专精 → 归因于从同一稠密局部最优出发。Vocabulary specialization：深层更高，而且按**预测输出 token** 而非输入 token 专精。
- 对我们：(1) "深层按输出 token 专精"与我们"深层路由预期右文脉角色（L11 .42）"同向；(2) "upcycling 限制专精——所有专家从同一局部最优出发"= 初始化决定分工的工业版证据，和我们"初始化印记持久"一致；(3) saturation 只是与自身终点比，没有跨 run。

## 2208.02813 Towards Understanding MoE (Chen et al., NeurIPS 2022, 理论)
- 混合分类数据（簇中心信号 + 标签信号）；非线性专家 + 梯度下降 → 专家各专精于至少一个簇，**"由权重初始化决定"**；router 学到簇中心特征。线性专家学不出簇结构。
- 对我们：理论上已经写明"哪个专家负责哪个簇由初始化决定，但簇的划分本身由数据决定"。我们的实证正是这句话在语言数据上的版本：**划分（语法簇）由数据决定并跨 seed 重现；分配（哪个专家）由初始化决定**。可以把 E167 结果讲成对这条理论的语言级检验——而且我们发现"划分"也只部分重现（.5 重跑上限），说明语言数据的"簇"不是离散的。

## 摘要级扫描（2026-11-05）
- **2605.06663 EMO (AI2/Berkeley, May 2026)**：文档内 token 限定在同一专家池 → 1B/14B、1T token；只留 25% 专家只掉 1%。**关键发现：标准 MoE 的路由聚类是"介词 / 专有名词 / 系动词 / 定冠词"这种词汇-句法类；EMO 变成"影评 / 医疗 / 新闻"这种领域类。**即：标准训练配方下分工天然是语法层的，语义层分工要靠训练目标诱导。这与我们的 E170 完全一致，而且给了"为什么"的一个旋钮（目标函数）。
- **2501.11873 Demons in the Detail (Qwen, ACL 2025)**：负载均衡在 micro-batch 内算 ≈ 序列级均衡 → 抑制领域专精；改为 global-batch → PPL 更好且出现领域专精（SFT-Math 有专家频率 >.2）。micro-batch 下"只有 token 级专精"。**又一个决定分工粒度的训练旋钮（均衡作用域）。**
- **2401.04088 Mixtral §5**：按 Pile 子集没有主题专精；"self"/"Question"/缩进 token 固定专家；连续 token 常同专家；"更像句法而非领域"。
- **2412.16971 POS sensitivity (Antoine et al.)**：6 个公开 MoE，按 POS 专精高于均匀 +25%（Mixtral）到 +36%（OLMoE）；路由路径预测 POS 准确率 .79–.91。
- **2604.14434 Geometric Routing（Equifinality 的姊妹篇）**：rank-1 专家 + cosine 路由；15% 专家单义；**早层按频率、深层按句法类分（控制 Zipf 后仍成立）**；steering 实验。
- **2502.10928 Olson et al. 语义路由**：WiC 同词不同义 → 专家重叠显著更低（p<.001），效应随规模增大，中层最强（DeepSeek-R1 671B 最明显）。即**语义专精随规模出现**——小模型（我们 7.5 亿）上几乎只能看到语法专精，这是我们尺度的边界，必须写明。
- **2406.18219 A Closer Look (Lo et al., NAACL 2025 Findings)**：神经元是细粒度专家；router 选大输出范数的专家；专家多样性随层数增加，末层例外。
- **2510.04694 Multilingual Routing (ICLR 2026)** / **2601.14050** / **2605.29714**：早晚层语言特异、中层跨语言对齐（U 形）；与英语路由相似度预测该语言性能；steering 中层 +1–2%。持续预训练下语言专精出现在末层。
- **2608.15102 Declarative–Procedural bilingual MoE**：小型自训英德 MoE，按词汇/语法/句法探针测路由互信息；**两个 seed 的复现发现无课程条件的专精集中在哪种语言是 seed 依赖的**。小作坊论文，但正好是"语言学框架 + seed 依赖"。
- **2607.28308 Coherent Overlap**：专家子空间大量重叠，但实际路由仍比匹配替代解释更多残差；"几何相似不等于功能冗余"。
- **2609.01100 CoRM**：减去 EMA 背景后路由边界更贴语言结构；按 UPOS 的专精分数，函数词增益最大。
- **2610.32153 Sparsity-driven modularity**（多任务小网络）：稀疏正则 → 深层出现任务选择性子网络，早层共享；30 个独立 run。
- **2610.41236 Structured redundancy**：专家输出有效秩远低于专家数。
- **2505.24593 / 2601.08383 知识归因（HKUST-GZ）**：共享专家做通用、路由专家做领域；MoE 在 <100K 步内锁定重要性剖面而稠密模型持续波动；top 1% 神经元占 45% 正向更新。
- **2509.11348 LMC of MoE (NeurIPS 2025 Oral)**：MoE 的对称性 = 专家置换 × 门控置换；匹配后线性模式连通。→ 独立训练的 MoE 在置换后处在同一盆地，这是"分工可对应"的权重级依据。
- **2405.07987 Platonic**：表示随规模收敛（核对齐）。**2410.06672 Towards Universality**：Transformer vs Mamba 多数 SAE 特征相似。**2302.03025 Chughtai 玩具模型**：算法族可完全刻画，但具体学到哪些表示和顺序是任意的——"mixed evidence"，与我们"切法层级可重现、具体实现任意"同形。
- **2412.04139 Monet** / **2503.07639 MoE-X**：把专家数推到 26 万 / 强制稀疏，专家单义；说明"粒度越细越单义"是架构可控的。
- **2607.08499 跨 seed SAE（BERT）**：Procrustes 对齐后联合训练 SAE，跨 seed r ≥ .70。
- **2509.05291 Crosscoding 结果**：Pythia 1B→4B→286B：token 级检测器消退，群体级抽象（动名词化、复数名词类、介词）涌现；OLMo 更长视界同样。
