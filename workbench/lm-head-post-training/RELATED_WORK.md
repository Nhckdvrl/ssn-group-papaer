# 关联工作、文献地图与选题排雷（2026-11-26）

本文件是此前 GPT/Gemini 多轮讨论的研究交接，不是论文 Related Work 初稿，也不是已经完成的系统综述。直接服务 LM Head 的文献先读；其他保留为边界和历史素材，不要为读完本文件才开始 E01/E02。链接以论文原始入口优先。此前有正文、摘要、第三方索引和访问失败等不同核查层级；凡未取得全文，一律视为定位线索，执行者引用具体数字或 claim 前须核对原始版本、方法、实验条件与图表。没有论文新颖性保证。

## 1. P0 核心必读：两篇有实证张力的研究

### A. Godey & Artzi — Lost in Backpropagation: The LM Head is a Gradient Bottleneck
[arXiv 2603.10145](https://arxiv.org/abs/2603.10145) · [HTML v1](https://arxiv.org/html/2603.10145v1) · [作者博客](https://nathangodey.github.io/posts/lm-head-bottleneck/) · [作者发表列表（列为 COLM 2026）](https://yoavartzi.com/pubs)

- 问题：常规词表输出投影 W 既决定前向分布，也限制骨干收到的 logit-space 梯度；作者研究误差信号在列空间与正交补间的几何分解及训练后果。
- 此前讨论报告 95%–99% 梯度范数损失等数量级及约 2B 规模实验；不要未经原文核对将 norm、squared energy、rank/维数比例互换。更不能直接把这些数字与本项目 ρ（投影能量比例）比较。精读理论定义、实验模型配置、真实梯度分布与低秩干预，写一份短复现笔记。
- 对 E02：不仅报几何保留率，更需分开奇异值增益、实际训练信号和无关/冗余方向。低保留率不证明性能损害；不能把线性代数恒等式当新发现。
- 对 E03：若实测有值得追查的效应，复核前向秩限制与反向梯度限制是否能被分别干预。首轮不预设作者正确。

### B. Murugan — Does the LM Head Create a Harmful Gradient Bottleneck? A Causal Test
[arXiv 2608.16671](https://arxiv.org/abs/2608.16671) · [作者文章](https://www.anandmurugan.me/writing/lm-head-gradient-bottleneck)

- 问题：几何投影损失是否真的是有害优化瓶颈？低秩输出头改变前向表达和反向梯度，不能直接从性能下降认定后者承重。
- 方法：比较仅反向干预与前向低秩头；指出输出头自身还收到 g_W=g_z h^T，当前 g_h 未含某方向不等于整模型永久丢失该信息。
- 此前阅读记录：一组约 226 万参数模型的五 seed 对照中，讨论报告验证 loss 增量约 0.0586 vs 0.1795（仅反向 vs 前向头降秩）；使用前须核对 rank、单位、基线及统计范围。论文还讨论重复观测/独立样本数的混淆以及额外梯度通路未稳定胜过调优 baseline。
- 对 E03：冻结头使其直接参数更新渠道消失，但同时限制前向适应；骨干仍能学习。即使观察到冻结损害，也不自动证明梯度瓶颈。先 E01/E02，后根据真实信号确定是否需要单独反向对照。
- 两篇的规模、任务、优化设置不同；不是逻辑上的非此即彼，也不声称后训练尚无任何同类工作。首轮应复核两篇的真正实验差异，而非仅复述争议故事。

**共同研究张力：** 前向表达限制、当前梯度几何与真实长期学习效率是否一致？在哪些实际后训练设置中，LM Head 的功能变化或可训练性值得关注？不要提前给出答案。

**精读核对（2026-11-26，全文）：** A 是 COLM 2026 正式版（v2）。95–99% 指 ‖P_ker g‖/‖g‖（范数比），对应保留余弦 0.1–0.3，即本项目 ρ≈0.01–0.09；随机方向的期望 ρ=d/V（Qwen3-8B 为 4096/151936≈0.027），所以“真实梯度几乎不比随机方向更对齐列空间”才是 A 的实质观察。A 的全部实验是预训练（FineWeb 上的公开 base 模型 + 2B 低秩头预训练 + SpamLang），没有任何后训练实验；附录 E 显示 OLMo-2-1B 预训练全程该比例几乎不变。B 的规模是 2.26M 参数（宽 96，BPE-8192），核心结论是“仅反向降秩”（+0.059）远小于“前向降秩头”（+0.180），且从头部自身更新里去掉正交分量最伤（+0.625，3 seeds）——即 g⊥ 被 W 自己的更新用掉了。B 的实现见公开仓库 `kupilikula/lm-head-gradient-bottleneck`（`DecoupledLinearFunction`：前向不变、反向用 W 的秩 r 近似并匹配 RMS），可直接借作对照。**两篇都只在预训练里成立/不成立；后训练里头部自身更新通道有多大，是双方论证都依赖却都没测的量。**

## 1.5 后训练中的输出头：直接证据现状（2026-11-26 全文精读）

结论：没有工作在标准 Base→SFT→DPO→RLVR 谱系上定量测过 lm_head；主流权重解剖论文普遍把 head 排除在外。最近的近邻是一篇 CPT/指令微调的遗忘机制论文。

| 工作 | 与 head 相关的实际内容 | 对本项目的意义 |
|---|---|---|
| Han et al., [A Deafening Silence](https://arxiv.org/abs/2610.09835)（2026-10） | 冻结实验因果定位：CPT/指令微调的遗忘 31–51% 集中在**新语料中几乎不出现的 token 的输出 embedding 行**；机制是非目标行的单边梯度 −p_t h 被 Adam 的 √v̂ 归一化放大成满步长；只对输出投影调大 Adam ε 可去掉 39–68% 遗忘；事后重置漂移行只恢复 <5%。Pythia/Qwen2.5-0.5B/TinyLlama/OLMo-2-1B，无 DPO/RL。 | **最近邻。** 机制直接预测：on-policy RL 的非目标行梯度带优势符号、会互相抵消，SFT 不会。这正是 I04 的来源；必须把“SFT vs RL 的头部行符号结构”与它区分开（它只做了 SFT/CPT，未比较 RL）。 |
| Wu et al., [Sparsity Curse](https://arxiv.org/abs/2606.18521)（KDD'26） | 层级稀疏图（bf16、1e-5 绝对阈值）：RL 模型的 embedding 与 head“更新稀少”，SFT 的 head“显著更新”；只有图，无数字。 | 与 I04 方向一致的定性线索；阈值口径有偏（低幅行），需用 ULP/舍入基线复核。 |
| Altaf, [Rank Measures Need a Noise Baseline](https://arxiv.org/abs/2610.22438) | BF16 舍入零基线：两端独立 U(±ulp/2) 误差 E，σ1(E) 以下的 ΔW 奇异方向不可信；OLMo-2-1B 的 DPO→RL 只有 3% 方向高于地板。head/embedding 明确排除。 | E01 权重谱必须附舍入地板（已实现）；DPO/RL 阶段的 head 谱可能大部分在地板以下。 |
| Zhu et al., [The Path Not Taken](https://arxiv.org/abs/2511.08567)；Mukherjee et al. [2505.11711](https://arxiv.org/abs/2505.11711)；[2507.17107](https://arxiv.org/abs/2507.17107)（已撤回） | RL 更新“稀疏”、离开主奇异方向；**分析只含 transformer 线性层，明确排除 embedding 与 head**。RL's Razor 附录：fp32 训练下稀疏性消失。 | 原 T2“RL 稀疏子网”不再做；head 是这批工作的空白，但“稀疏/不稀疏”本身不是目标。 |
| He & Cao, [Post-Training Structural Changes](https://arxiv.org/abs/2509.17866) | 奇异值近似整体缩放 + 奇异向量一致旋转；head 只在附录 E.3 定性：大体相同但部分子空间不共转，假设因“直接受外部监督”扰动更大。 | E01 的 W0 比例分量 / 主角余弦正好量化这句假设。 |
| Shiromani, [What a Weight Update Buys](https://arxiv.org/abs/2610.37719) | 用 Olmo-3-7B 的 SFT/DPO/RLVR/RL-Zero 阶段算 ΔW 的 Fisher “杠杆”；DPO 相对改变 ~1e-4–1e-3，SFT ~1e-1；无逐模块 head 结果。 | 同一谱系的近邻；E01 的 head 行级/功能读数不与其重复。 |
| [HeadEdit](https://arxiv.org/abs/2610.01170)；Madl, [Channel Location and Subliminal Learning](https://arxiv.org/abs/2606.22019) | 冻结 unembedding 上的低秩推理期校正，部分预测 LoRA-DPO 的 logit 变化；子类学习迁移由 unembedding 行纠缠 cos(W_τ,W_j) 决定，正交化一行可降 >500×。 | 相邻（推理期 steering / 迁移审计），不是后训练动力学。 |
| Ren & Sutherland [ICLR'25](https://arxiv.org/abs/2407.10490)；Cui et al. [Entropy Mechanism](https://arxiv.org/abs/2505.22617)；Razin et al. [ICLR'25](https://arxiv.org/abs/2410.08847)、[ICLR'24](https://arxiv.org/abs/2310.20703) | 后训练 logit 动力学理论。Cui 明确假设表格 softmax（每个 logit 独立参数）；Ren & Sutherland 的 squeezing 证明只用固定特征的读出层（K=‖φ‖²I，恰是 head 通道）；Razin 2025 把 h 当自由参数。**无一拆分 head 通道（各向同性 ‖h‖²I）与骨干通道（W J Jᵀ Wᵀ，秩 ≤ d）。** | 若后训练实际 logit 变化主要走骨干通道，这些理论的“表格”预测需要修正；可作为 I02/I04 之后的理论落点，先不展开。 |

工程事实（代码/文档核对）：verl FSDP 默认 FP32 master + bf16 计算、单一参数组（head/embedding 与其他参数同 LR、同 AdamW）；TRL GRPO 默认 LR 1e-6、可选 `cast_lm_head_to_fp32`（ScaleRL 推荐，需非 tied）；MiniMax-M1 把训练/推理概率不一致定位到 head 高幅激活并改 FP32 head，ScaleRL 报告 FP32 head 提升渐近 reward，Sea AI Lab 的 FP16 论文认为仅 FP32 head 不足以防崩溃；Muon 系实现中 head 与 embedding 一律留在 AdamW。OLMo 3 报告：中训引入未见特殊 token 会导致模型输出它们、GSM8K 49.4→0（embedding 行问题的现实例子）。

## 2. P1：直接相邻理论、方法与实验口径

| 文献 | 已知内容/与本项目的关系 | 本地执行需要避免的重复或混杂 |
|---|---|---|
| [Breaking the Softmax Bottleneck: A High-Rank RNN Language Model](https://arxiv.org/abs/1711.03953) | 经典输出分布表达秩限制 | 前向 softmax bottleneck ≠ 反向梯度有害 |
| [The Softmax Bottleneck Does Not Limit the Probabilities of the Most Likely Tokens](https://proceedings.iclr.cc/paper_files/paper/2026/hash/d9b42c5f263a3f7486e50b84d6bbc0d3-Abstract-Conference.html), ICLR 2026 | 针对最可能 token 的实践表达能力分析 | 不要从 V≫d 或整体秩直接推出解题受限；读其适用范围 |
| [Min et al., Noisy Channel LM Prompting, ACL 2022](https://aclanthology.org/2022.acl-long.365/) | 少样本分类中的 head tuning（只微调 O∈R^{V×h}）是很强的基线 | Head-only tuning、冻结/解冻本身不是新方法；检查真实权重共享 |
| [LoRA](https://arxiv.org/abs/2106.09685), [QLoRA](https://arxiv.org/abs/2305.14314), [GaLore](https://arxiv.org/abs/2403.03507) | 参数高效与低秩梯度优化 | 不能把更多可训练参数的收益解释为特定 head 机制；报告真实训练成本 |
| [Understanding Post-Training Structural Changes in Large Language Models](https://arxiv.org/abs/2509.17866) | 此前初筛：分析谱结构、奇异值与方向的功能 | E01 的权重谱不应成为唯一贡献；固定隐状态反事实仍有共同适配问题 |
| [DAPO](https://arxiv.org/abs/2503.14476) | GRPO 组内零优势、动态采样与训练细节 | 全对/全错组要记录；单 token CE 与未裁剪策略梯度共线，不能把 reward 加权当新局部方向 |
| [Failure-Prefix Conditioning](https://arxiv.org/abs/2601.20829) | 饱和任务可借失败前缀恢复学习信号 | 不以“饱和不等于掌握”作为当前研究新意 |
| [LLMs Gaming Verifiers](https://arxiv.org/abs/2604.15149) | 同构变换检测与修正奖励捷径 | 数学任务 verifier 与答案格式需控制；不能把所有奖励差异解释成梯度结构 |
| [Quagmires in SFT-RL Post-Training](https://arxiv.org/abs/2510.01624), [Good SFT Optimizes for SFT, Better SFT Prepares for RL](https://arxiv.org/abs/2602.01058), [Reinforcement Learning Unlearns Corrupted SFT Reasoning](https://arxiv.org/abs/2611.26756) | SFT 分数与后续 RL 学习潜力不一定一致 | 自然 checkpoint 比较只发现现象；不重复泛化的 SFT-to-RL 题目 |
| [SFT Conflicts, RL Coexists](https://arxiv.org/abs/2608.03573), [Decouple before Integration](https://arxiv.org/abs/2605.00610) | 多任务/后训练更新结构与冲突 | 不把梯度方向差异、任务向量稀疏当作自动原创性 |

核查状态：核心 A/B 本轮已再次定位原始论文与作者入口；softmax bottleneck ICLR 2026 和 ACL 2022 head-tuning 原文入口亦已定位。其他 P1 多来自此前正文或摘要初筛，非完整逐页核查。具体算法与结论以正式版本为准。

## 3. P1/P2：参数更新、谱与数值精度（E01 及后备空间）

| 工作 | 需要知道的边界 |
|---|---|
| [Reinforcement Learning Fine-Tunes a Sparse Subnetwork in Large Language Models](https://arxiv.org/abs/2507.17107) | RL 更新稀疏与受限子网训练已有直接工作；原 T2 不再立项 |
| [Why RL Updates Look Sparse](https://openreview.net/pdf/00f465ba63bf06cb7d8df77db1a0fa4eee449754.pdf) · [索引](https://lacuna.tiptreesystems.com/work/why-rl-updates-look-sparse-an-implicit-compass) | 讨论优化几何及 BF16 可见更新；不能从公开权重精确零比例推断真实优化自由度 |
| [Rank Measures of Fine-Tuning Updates Need a Noise Baseline](https://arxiv.org/abs/2610.22438) | 已精读（见 §1.5）：两端独立 U(±ulp/2) 舍入误差 E、σ1(E) 作地板；head/embedding 被排除。E01 已按此实现 |
| [The Surprising Effectiveness of Deleting Weights in LLM Post-Training](https://arxiv.org/abs/2611.10866) | 此前初筛报告极少量置零可匹配部分 SFT/RLVR/蒸馏表现；原始全文访问曾失败。不能说它证明完整微调只有稀疏有效参数，更不能和 BF16 表观稀疏视为直接矛盾 |
| [DARE](https://arxiv.org/abs/2311.03099), [TIES-Merging](https://arxiv.org/abs/2306.01708) | 微调增量裁剪、重缩放、冲突处理 |
| [Less is More: Binary Task Switch](https://arxiv.org/abs/2412.00054), [Auto-FlexSwitch](https://arxiv.org/abs/2604.28109) | 极简 mask/sign/scale 原语与模型合并；原语–能力大网格不能直接当新题 |
| [Early-Bird Tickets](https://arxiv.org/abs/1909.11957), [EarlyBERT](https://aclanthology.org/2021.acl-long.171/), [RigL](https://arxiv.org/abs/1911.11134) | 早期掩码与动态稀疏训练经典前沿 |
| [Diff Pruning](https://aclanthology.org/2021.acl-long.378/), [FishMask](https://arxiv.org/abs/2111.09839), [LT-SFT](https://aclanthology.org/2022.acl-long.497/) | 语言模型稀疏微调的既有思路；具体编号与方法版本引用前复核 |
| [BitFit](https://arxiv.org/abs/2106.10199), [IA³](https://arxiv.org/abs/2205.05638) | 极少参数、缩放原语并非新概念 |

注意：E01 谱需要同 dtype、差值累加精度、量化/rounding floor、归一化与数值阈值；可选最小噪声基线用于解释，不自动启动第二研究空间。非结构化稀疏不等于 GPU 速度或峰值显存节省。参数坐标不唯一，幅值/符号/低秩对比不能直接证明某能力的本质载体。

## 4. P2：输出头效率与评测可靠性（不是首轮实验任务）

- [Dynamic Vocabulary Pruning in Early-Exit LLMs](https://neurips2024-enlsp.github.io/papers/paper_95.pdf)、[SlimSpec](https://arxiv.org/abs/2605.10453)、[Vector Index Based Output Embeddings](https://arxiv.org/abs/2608.27460)、[Vocabulary Pruning by Log-Mass Maximization](https://www.amazon.science/publications/which-tokens-can-a-device-afford-to-score-vocabulary-pruning-by-log-mass-maximization)：候选词、低秩/索引、词表频率压缩有直接研究。只有 E01/E02 揭示明确可用冗余，才考虑输出头压缩；不能把大矩阵等同端到端瓶颈。
- [Accuracy is Not All You Need](https://openreview.net/forum?id=QVG7j29Sta)、[Quantization Meets Reasoning](https://openreview.net/forum?id=So3hbnEGYV)、[Reasoning-Aware Compression](https://arxiv.org/abs/2609.05512)、[Beyond Activation Alignment](https://arxiv.org/abs/2607.00908)、[Target-Aware Calibration Data Selection](https://aclanthology.org/2026.findings-emnlp.670/)：平均分/PPL 掩盖行为退化、层级保护、校准问题已有大量近邻。
- [Measurement Artifacts in Trustworthiness Evaluations of Quantized Small Language Models](https://arxiv.org/abs/2611.32848)：此前讨论中评分协议和 batch/padding 可能改变所测退化；不把测量伪影当模型能力。对 E02 保持 token、mask、replay 与采样分布一致。
- [Thinking Machines Lab research blog](https://thinkingmachines.ai/blog/)、[Transformer Circuits](https://transformer-circuits.pub/)、[Nathan Godey research notes](https://nathangodey.github.io/)：此前建议的异常挖掘来源。不是必读全集。

## 5. 方法论标杆：塚越与笹野的 embedding 研究

[Redundancy, Isotropy, and Intrinsic Dimensionality of Prompt-based Text Embeddings](https://aclanthology.org/2025.findings-acl.1330/)（公开论文）。

此前精读的关键启发：简单降维在分类/聚类与检索/相似度上的效果不同；任务依赖的冗余差异比“可以压缩”本身更有研究意义。论文还讨论尚未解释的底层原因。不要为了模仿该论文就把 E01 做成无目的 rank sweep；只有与真正的功能差异联结才有意义。该已发表论文是方法论参考，不改变本仓库投稿规则。

## 6. 历史排雷地图：不再把旧想法当当前任务

为避免本地 Agent 又从已有研究重新发明旧方向，保留此前讨论的重要近邻。以下是**历史线索索引**，不是每篇均已全文核实，也不是要求逐篇读完。不要擅自据此关闭其他 workbench。

| 已暂停的问题 | 此前讨论的直接近邻/原始入口 | 为什么不在当前做 |
|---|---|---|
| 多轮退化、更新与旧知识干扰 | [LLMs Get Lost in Evolving User Intent](https://arxiv.org/abs/2607.20734), [CCOPD](https://arxiv.org/abs/2605.30251), [FiC](https://arxiv.org/abs/2605.24432), [TRACK](https://aclanthology.org/2026.eacl-long.273/), [DERELAB](https://aclanthology.org/2026.emnlp-main.1625/), [AGM-Bench](https://openreview.net/forum?id=2s1BujG84C), [When Context Changes](https://arxiv.org/abs/2609.38866) | 传播失败、证据修正及 attention 干预已密集；Evolving Intent 的两任务预算比较不证明倒 U 型 |
| 行动相关性与异常归因 | [Ask, Relax, or Act?](https://arxiv.org/abs/2610.03102), [Ask2Decide](https://arxiv.org/abs/2611.13015), [ToolMaze](https://arxiv.org/abs/2606.05806), [Loud Failures, Quiet Failures](https://arxiv.org/abs/2610.10062), [Failing to Falsify](https://arxiv.org/abs/2604.02485), [FALSIFYBENCH](https://arxiv.org/abs/2606.04751), [Beyond Accuracy](https://arxiv.org/abs/2611.29467) | 可行动不确定性、故障恢复、主动证伪已有强近邻；单次异常否定辅助假设的合取而非单独环境规则 |
| 经验形成、成功稀释和泛化 | [Experience Rot](https://arxiv.org/abs/2611.20922), [Don't Just Trust Your Memory](https://arxiv.org/abs/2611.14320), [Self-Evolving Agents Can Repair Failures but Struggle to Generalize from Them](https://arxiv.org/abs/2610.22984), [Faithful Self-Evolvers](https://arxiv.org/abs/2601.22436), [RegimeCouncil](https://arxiv.org/abs/2611.22113), [More Evidence Is Not Always More Support](https://aclanthology.org/2026.findings-emnlp.747/) | 不可识别 vs 可识别有信息上限混淆；重复证据与经验泛化已有研究 |
| 结果奖励与动态可塑性 | [Primacy Bias](https://proceedings.mlr.press/v162/nikishin22a.html), [Loss of Plasticity](https://www.nature.com/articles/s41586-024-07711-7), [Continual RLVR](https://arxiv.org/abs/2608.18574), [Why Do LLM Agents Fail in Exploring New Environments?](https://aclanthology.org/2026.findings-emnlp.1023/), [Spurious Tool Use](https://arxiv.org/abs/2609.16268) | 必须区分奖励不充分、零优势饱和、探索失败、真实可塑性丧失；不再单独启动 |
| 状态隔离与上下文/KV | [MemGPT](https://arxiv.org/abs/2310.08560), [Zep](https://arxiv.org/abs/2501.13956), [TEM](https://arxiv.org/abs/2610.21900), [Lost in Context Compaction](https://arxiv.org/abs/2608.11242), [Questions That Come Later](https://arxiv.org/abs/2610.27301), [Positions Are Not Facts](https://arxiv.org/abs/2609.33759), [ReCAP](https://arxiv.org/abs/2609.40118), [DTOC](https://arxiv.org/abs/2609.26121), [ReFold](https://arxiv.org/abs/2610.07863), [Folio](https://arxiv.org/abs/2611.16627) | 可逆历史、时态记忆、查询路由、独立约束提取已有方法 |
| 增量 KV 刷新（β） | [PatchKV](https://arxiv.org/abs/2609.26219), [Budgeted KV-Cache Repair](https://arxiv.org/abs/2610.17338), [Context Language Models](https://arxiv.org/abs/2609.37725), [Request Order Matters](https://arxiv.org/abs/2610.05833), CacheBlend / EPIC | 局部刷新、后缀复用、依赖识别已有强系统近邻 |
| 推理早停 | [When More Thinking Hurts](https://arxiv.org/abs/2604.10739), [Stop When Enough](https://aclanthology.org/2026.acl-long.1256/), [When Is Thinking Enough?](https://aclanthology.org/2026.acl-long.1080/), [Confidence Dynamics](https://arxiv.org/abs/2604.04930), [Entropy After Think](https://arxiv.org/abs/2509.26522) | 不再做新的 entropy/probe 阈值 |
| 验证器误差（T3） | [Delay, Plateau, or Collapse](https://arxiv.org/abs/2605.02909), [Noisy Rewards](https://arxiv.org/abs/2510.00915), [Verifier Errors in RLVR](https://arxiv.org/abs/2609.35677), [Audit Where Hacks Pay](https://arxiv.org/abs/2610.35716), [Are Verifier Errors Independent Within a GRPO Group?](https://arxiv.org/abs/2609.06386) | 组内相关、审核预算及系统误差已有近邻；简单 advantage 算例是定义直接推导 |
| 蒸馏闭环 | [Distillation Traps and Guards](https://aclanthology.org/2026.acl-long.908/), [Entropy-Aware OPD](https://proceedings.mlr.press/v306/jin26e.html), [Unmasking OPD](https://arxiv.org/abs/2605.10889), [When Context Returns](https://arxiv.org/abs/2606.11627), [Gains and Collapse in OPD](https://arxiv.org/abs/2610.03185), [When Students Fail to Learn from Teachers](https://arxiv.org/abs/2611.27125) | 同分不同质和闭环分布失配已受关注 |

## 7. 执行者怎样使用文献

E01/E02 前只精读 P0 两篇；针对 E01 的谱测量额外核对 rounding floor 线索的相关段落；其他是必要时索引。把原文的公式、模型/数据/干预和实际本地口径差异写入实验卡；如果论文与交接描述不符，以原文为准并在日志更正。新结果出来后按具体结果查最强近邻和替代解释，不进行无边界阅读。任何引用进入稿件前必须独立核实。没有实际证据不能写“首次”“普遍瓶颈”“因果机制已证明”。
