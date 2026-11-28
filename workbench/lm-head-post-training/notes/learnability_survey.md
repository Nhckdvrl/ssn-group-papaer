# RLVR 训练历史与可学性：文献综述（2026-11-28）

范围：RLVR 中训练历史如何改变模型下一步能学什么（平台期、可塑性、unlearnable、渐近线）。不含实验。
读深度图例：【全文】= pdftotext 全文 + 实验/附录抽读；【节】= 读了指明章节；【摘要】= 只读 arXiv 摘要（不据此下判断）。
全部 PDF 在 /tmp/claude-1045/-home-xiang-ssn-group-papaer/194abef4-0025-41b1-b44e-ff434cc7560a/scratchpad/lit_c/（临时）。

## A. 七篇精读

### A1. 2605.16787 The Unlearnability Phenomenon in RLVR（Chen/He/Zhao，ICML 2026）【全文】
- 设定：Qwen2.5-0.5B（MATH L1-4）、Llama-3.2-3B-Instruct（MATH L3-5）、Qwen2.5-3B（DeepScaleR）；GRPO + dynamic sampling，单段训练，从基座起，约 100-150 步（§3.3, Fig 2/5）。
- 操作化（§3.2）：初始 pass@1 ≥0.1 为 easy，其余 hard；hard 中「训练全程见过正确 rollout、但**最终策略** pass@1<τ=0.1（N=32）」者为 unlearnable，其余为 learnable；3 次独立训练取交集。「平台」= 验证集饱和时仍低于 τ。
- 占比（Table 1，占初始 <0.1 的难题）：Du 30.2/21.9/16.7%，Dl 25.6/31.6/14.2%，全程无正奖励 23.5/37.7/47.2%（0.5B / Llama-3B / Qwen-3B）。
- 排除的解释：正样本不足（过采样+回放，k=8,kpos=1，Fig 2；SFT 蒸馏与 k=64，App A.2）、低参考概率（Fig 3 参考 log-lik 无差异）、clip 率（Fig 4）、clip-higher 与去 KL（Fig 5）、梯度干扰（App A.3，「几乎无」）。
- 机制证据：Du 样本是「梯度离群点」——正确 rollout 梯度与其余样本余弦相似度低（Fig 1c, 6；用固定随机 LoRA 梯度，0.5B 上与全参数相关）；GPT-5-mini 打分的推理质量低（Fig 1d, 7）；相似题/子题增广能学但不迁移（Fig 8-10）；OctoThinker 中训练提高梯度相似度（Fig 11，**只测相似度，没跑 RL 学习曲线**）。
- 控制情况：KL 锚——只做了「去 KL」消融，默认 β 在附录 B.1（未核对）。优化器状态——不适用（无阶段切换）。初始 ppl/acc——按初始 acc 分层，easy/hard 有分组；但 unlearnable 由**终点结果**定义（选择偏倚）；脚注 1（p.3）自述：长训练后部分 unlearnable 样本奖励陡升同时验证性能下降。局限自述：小/中模型、仅数学、阈值式定义（Limitations, p.9）。
- 重复训练同一批 prompt（多 epoch），所以「不学」混合了过拟合/重复，不是历史效应。

### A2. 2609.40115 Unlearnable, or Unmeasured?（Chakma 等，NeurIPS 2026 workshop）【全文，§3.1-3.4 + 摘要结论】
- 设定：复现 A1，Qwen2.5-0.5B、1,023 条 MATH、5 个种子、G=8；**生成长度 1,024（原文 5,120）**，作者自述不完全一致（§3.1）。
- 结论1（Fig 1）：Du 并非不学，训练奖励斜率 +0.0422 [+0.0259,+0.0590]/100 步，learnable +0.1119，easy +0.3800，约 learnable 的 1/3。
- 结论2（Fig 2）：同一批 292 个候选下，原五种子规则得 74 个，换聚合规则 228，单种子 145-150，零正确规则 181。逐种子取「全体都判难」的交集会趋向 p(x)=0 的退化集合，而随后的 no_reward 剔除恰好去掉它们；被剔除的 218 个中 116 个后续评测解出至少一次。
- 结论3：同一检查点重采样两次 Jaccard 0.798，跨训练种子 0.751（N=32），即约 81% 的「种子间差异」来自抽样；预算：8/16 rollout 一致性 0.63/0.73，≈40 达 0.80，0.90 需约 242（外推，§3.4，两个预先冻结预测落入区间）。
- 结论4（梯度）：难题正确 rollout 少，梯度估计更噪；配平正确数后 easy/unlearnable 相似度比从 2.327 降到 1.539，差距仍在（摘要/§3.5）。机制未解。
- 控制：KL/优化器/历史均不涉及；只重测 A1 的测量问题。

### A3. 2605.12484 Learning, Fast and Slow（Tiwari/Sareen/Agrawal 等，v3 2026-10-14）【全文，§4、§5、App F】
- 设定：Qwen3-8B（数学臂用 Qwen3-8B-Base 先 SFT Nemotron），CISPO（ScaleRL 配方），AdamW lr 1e-6；任务 CodeIO、Polaris 数学、HoVer-hard、Physics；方法 FST = RL（慢权重）与 GEPA 提示进化（快权重）交替。
- 渐近线（Fig 4）：按 ScaleRL 做 sigmoid 拟合，FST A=47.4/49.2/25.0 对 RL 43.0/46.4/17.3（CodeIO/Polaris/HoVer）。
- 可塑性操作化（§4 Adv 4, Fig 6）：阶段1在任务 X 上训 RL 或 FST，阶段2从该检查点起在 Y 上做 400 步标准 RL，看 Y 的验证准确率。Math→HoVer-hard：RL-init **40 步内降到约 0% 且持平**，FST-init 接近 base-init；Physics→HoVer：RL-init 19.9%，FST-init 24.2%（Fig 6 图注给出 base-init 参考线）。
- 连续训练（Fig 7, App F）：HoVer→CodeIO→Physics 每任务 200 步、**不重置优化器**（App F.3 明说）；RL 在 CodeIO 阶段「几乎不起飞」（20.4%，stage 起点 18.5%，峰值 21.1%），FST 达 39.8%。加 20% 回放（19.1%）、KL 惩罚 β=1e-3（20.2%）均无效（Fig 22 左）；换序 Physics→CodeIO→HoVer，CodeIO 停滞仍复现（23.8% vs FST 37.1%），而 RL 在末位 HoVer 反而更好（49.0 vs 45.6%）。
- 与本问题相关的未控项：Fig 7 的 CodeIO 阶段**没有「从基座起同样 200 步」的参照**（主文）；Fig 3 里 RL 在 CodeIO 要到约 1450 步才见峰值，所以 200 步内「停滞」不能直接归因于历史（未核对附录是否另有基座参照）。Math→HoVer 的「降到 0%」是检查点初始就能答 HoVer 而随后坍缩（还是起点本来就≈0）图里未明说（未核对）；格式/提示适配、遗忘与「不可塑」未分开。FST 的 KL 机制：作者自己用「更小 KL≈更少遗忘/更保持可塑」作解释，是相关性，没有单独操纵 KL 的因果实验；KL 惩罚 1e-3 是唯一一次干预且无效。
- 熵：RL 基线的熵未单独报告（只有 FST-distill 对照 Fig 18，未核对）。

### A4. 2510.13786 The Art of Scaling RL Compute（Khatri 等，ScaleRL）【全文，§2-5, App A.8】
- 设定：主实验 8B 稠密模型（先小规模推理轨迹 SFT，App A.3），Polaris-53k，批 768（48×16），16k 上限；无 KL（§2）；另有 Llama-4 Scout 17B×16 MoE、数学+代码多任务、100k GPU 小时单次训练。
- 渐近线操作化（Eq 1，Fig 3）：对**留出的 1000 条 iid 验证题**的 mean@16 做三参数 sigmoid，R(C)=R0+(A−R0)/(1+(Cmid/C)^B)；A=渐近线，B、Cmid=效率；留一法 LOO 的方差给误差带（Fig 7）。
- 哪些选择动 A：损失类型 CISPO/GSPO 高于 DAPO（Fig 5a）、LM head FP32（A 0.52→0.61，Fig 5b）、批量（Fig 10，小批早期好但 A 低）、生成长度 14k→32k（Fig 9）、模型规模（MoE A 更高，且用 1/6 算力超过 8B）。只动效率 B 的：损失聚合、数据课程、长度惩罚、优势归一化（引言原则3）。
- 重要限定：同一选择的效应与配方有关——DAPO 单独时 A 低，但在 ScaleRL 里留一法换回 DAPO 的 A 与 CISPO 接近（§4, Fig 7）；FP32 在 ScaleRL 稠密模型上几乎无差，在 GRPO/DAPO 与 MoE 上才有大差（§4）。
- 无历史操纵（所有运行从同一初始化起）；A 衡量的是**同分布验证集**，下游基准上小批出现「早停滞」（§5 批大小）。无 KL 锚变量，初始 acc 同一起点。

### A5. 2509.04259 RL's Razor（Shenfeld/Pari/Agrawal，MIT）【全文，§3-4】
- 设定：Qwen2.5-3B-Instruct（数学、科学问答、工具使用）与 OpenVLA 7B；GRPO 二元奖励「不加显式 KL」（§3）；SFT 对照，跨数十组超参取 Pareto 前沿（Fig 2）。
- 结论：新任务上同等性能下，RL 对旧任务（Hellaswag、TruthfulQA 等）遗忘少；遗忘由**新任务分布上**的 KL(π0‖π) 预测（Fig 3 中、右）；权重变化量、更新稀疏度、梯度秩等备选预测量都不稳（§4/§6）；构造「oracle SFT」（最小 KL 且 100% 准确）比 RL 遗忘更少（Fig 3 左），说明优势来自隐式 KL 最小化而非 RL 本身。
- 与本题距离：只测「先学新任务后旧任务掉多少」，**不测下一个任务还能不能学**；单阶段、从 instruct 起。Tiwari 引用它作 FST 的背景。

### A6. 2609.13443（Noukhovitch 等，NGU）Fig 10 与 2611.04061（Nguyen 等，Primacy Bias）逐项对照【全文】
**Noukhovitch Fig 10**（§6，p.9）：对象=Qwen3-4B-Instruct-2507 在 Manufactoria（编码），按 Sun 等 RL Grokking 配方，KL β=0.01、lr 5e-7，2 节点×8 H100 约 28 小时（App D.3 Table 6）。先用 per-test 奖励训 3000 步（baseline 学会约 80% 测试但几乎不过全测试，§6 Signal Efficiency），然后从**这个检查点**分叉两路：(a) 全测试通过奖励，(b) 仍 per-test 奖励但加 NGU 采样；横轴为算力时间（0-80 小时），两路表现「近似持平」。作者的推论：LLM-RL 可以用次优目标训 3000 步后再恢复，所以 Matthew 效应「不同于可塑性丧失」。
- 它实际测的：改变奖励/采样后，同一检查点能否继续爬升。没有「同样新信号从基座起」的算力匹配对照（图中只有两条线；Fig 9 有 NGU 从基座起，初期稍慢，但算力轴不同）；未报遗忘/旧能力。
**Nguyen Fig 7-10**（§6，附录 B）：对象=Qwen2.5-3B-Instruct 在 MATH 7500 题上 GRPO，lr 1e-6，批 256，16 rollout，无 KL、无熵项；先训一次，**按终点策略的 pass@1** 把可解题分成难度分段，再对每段单独训新策略（Fig 7）：难段几乎不进步，易段进步；仅训难题时 pass@128 在**基座无法解**的题上随步数上升（Fig 10），但易题遗忘使全局 pass@k 下降（Fig 8-9）。「primacy bias」在这里指**预训练特征的 lazy 区**，证据是 MNIST 玩具（Fig 2-3，Zipf 偏斜）+公开检查点的线性化近似（Table 1, Fig 6）。
**差别（具体）**：(1) 起点：Noukhovitch=RL 过 3000 步的检查点→改信号；Nguyen=预训练/instruct 基座→同信号。(2) 被测量：Noukhovitch=改信号后全测试通过率的恢复；Nguyen=固定奖励下不同难度子集的提升速度与覆盖。(3) 难度定义：Nguyen 用「同一奖励训练后的终点策略」分段（分段本身已条件于结果）；Noukhovitch 用初始模型 128 采样（及适配 prompt 后重分类，Fig 8）。(4) 任务：Nguyen 的 MATH 是 instruct 已熟练领域；Manufactoria 是新任务（模型在前 100 步先适配 prompt/harness，§5）。(5) 术语撞车：Noukhovitch 按 Nikishin 的「从零训练的可塑性丧失」使用 primacy bias，并明说他的 Matthew 效应「不同于可塑性」；Nguyen 用同一个词指 lazy 区。
**是否矛盾**：不矛盾。两者对「易题涨得多、难题涨得慢」方向一致（Noukhovitch Fig 1/8，Nguyen Fig 7）。Nguyen 也看到难题训练最终能涨覆盖（Fig 10）——是慢而非零。两篇都没有「同一检查点、同一新信号、对 fresh 起点」的配对实验，因此「历史是否降低后续可学性」在两篇里都没被直接检验。Noukhovitch 的发表日期早于 Nguyen，未引用后者（其参考文献只引 Nikishin 2022/2023）。

## B. 扫描（arXiv 2025.06-2026.11，export API 关键词检索 + 若干网页检索）
检索方式：arXiv API 的 abs/ti 布尔查询（plasticity、continual、sequential、warm start、plateau、checkpoint、asymptote 等约 40 组）+ 1 次网页检索；API 对多词 AND 很严，召回有限，所以「未检索到」不等于不存在。
带 ★ 的 6 篇为与「RL 历史是否改变后续可学性及原因」最近、已读章节；其余仅摘要。

| ID | 一句话发现 | 深度 |
|---|---|---|
| ★2606.09932 When RL Fails after SFT（Rejuvenation） | EvoLM-4B 上 SFT 到 32 epoch 的检查点 RL 增益显著小于 2 epoch（Fig 5）；过训 SFT 熵 0.024 vs 0.184（Table 1），RL 梯度范数更大但权重更新更小（Fig 4）；用基座插值 α≈0.5+神经元重置恢复 | 节：§1-3.2、§4.1 |
| ★2509.21016 RL Grokking Recipe（Sun 等） | Qwen3-4B-Instruct 在 pass@K=0 的 Manufactoria 家族上，全通过奖励一直为 0，先 per-test 奖励热身再切换才「grok」；同难度的两条课程（先 REGEX vs 先 COMPR）使目标 HAS 家族一成一败（Fig 7, §3.4）；PREPEND 家族热身也出不了零区（Fig 8） | 节：§3.3-3.4 |
| ★2512.07783 Interplay of Pre-/Mid-training and RL（Zhang/Neubig/Yue） | 100M 合成可控模型（KL 1e-3）：RL 仅在预训练留有余量且数据在「能力边界」时增 pass@128；长尾上下文需 ≥1% 预训练暴露做种子，近零暴露 RL 失败；中训练决定 RL 响应度（Takeaway 1-3） | 节：设定+Takeaway 1-3 |
| ★2611.02747 Zero-to-One Jump（NAPO） | Qwen2.5-Math-7B 固定 1024 题 10 步；从同一检查点（同优化器状态、数据序）回放、只改采样随机性，两条延续的 N→P（零转一）次数不同（Table 1：n1 比 n2 多）；转一前的负样本早期 token 熵更高；提出按早期熵排序负样本 | 节：§1-4.1（仅10步窗口） |
| ★2510.02230 Reasoning Boundary Paradox | Qwen2.5-Math-1.5B/7B、Llama-3.2-3B：RLVR 中「负干扰」（学会一些题降低其他题正确解概率）与「赢者通吃」（强化基座下已高概率的题），解释 pass@k 缩小 | 节：§1、§3 开头、Fig 2-4（未读附录） |
| ★2601.04537 Linear Dynamics in RLVR | 多模型族上权重与输出 log-prob 随 RLVR 步数近线性（R²>0.7）；权重外推加周期重锚定 6.1× 加速 | 摘要+§1 抽读，机制未读 |
| 2610.04158 How RL Reshapes LLM Reasoning | Qwen/Gemma 上既有跨域提升也有遗忘；策略选择/执行两阶段模型；给出 log-sigmoid 与 log-linear RL 算力律 | 摘要 |
| 2602.14872 Implicit Curriculum in RLVR | 理论：混合难度训练诱导「易→难」隐式课程；难度谱不连续时出现 grokking 型相变与长平台 | 摘要 |
| 2606.24752 Can Scale Save Us From Plasticity Loss | 5M-314M GPT 型模型多语持续学习中可塑性丧失的起点随规模亚线性增长；静态多语训练也出现（非 RL，非推理） | 摘要 |
| 2602.06453 Plasticity and Stability for Post-Training LLMs（PCR） | GRPO 中可塑性梯度与稳定性梯度冲突，贝叶斯软投影（未读设定） | 摘要 |
| 2607.04364 RL Forgets!（CPO） | VLM 持续后训练标准 RL 仍灾难遗忘；原因：KL 在当前任务数据上估计，遗忘发生在旧任务分布（非 LLM 文本） | 摘要 |
| 2512.13607 / 2603.19220 Nemotron-Cascade 1/2 | 顺序分域 RL（Cascade RL）后续域 RLVR「很少降低」先前域基准；2 加多域在线蒸馏恢复回退 | 摘要 |
| 2606.25178 TAC | 多域 RLVR 课程：按跨域梯度对齐选域；六域套件 | 摘要 |
| 2610.22650 Ephemeral Cost of Switching Optimizers | 1.2B 预训练-SFT-RLVR 阶段间 AdamW↔Muon 的失配代价小；Qwen3-1.7B/4B 数学 RLVR 两者终点相当 | 摘要 |
| 2610.25836 Where RL Breaks | RL 失败 rollout 由少量 n-gram 预测、全程持续；用其检索 35M token 做继续预训练再 RL | 摘要 |
| 2507.12507 Scaling Up RL: Prolonged Training | 小模型长训：受控 KL、clip 比、**周期性参考策略重置**作为长期收益的关键成分 | 摘要 |
| 2511.04285 RLoop | RL 过拟合源于策略过特化与遗忘；用 RL→RFT 迭代重初始化 | 摘要 |
| 2610.12659 MagicBeanStalk | 合并开源数学语料对固定策略与预算约 88% 题全对或全错（零优势陷阱） | 摘要 |
| 2609.35897 Is Learning History an Asset or a Burden? | **非 LLM**：自发现 RL 规则的循环状态；固定历史（持续钳制）有代价，让导入状态自然演化可减弱（2026-09-27） | 摘要，仅概念类比 |

## C. 领域现状（只写事实，不给建议）

### C1. 已建立的（括号为证据与读深度）
1. 同一训练内，易题涨得多、难题涨得慢，是 ≥4 个独立设置的共同观察：Noukhovitch Fig 1/8（Olmo-3、DeepCoder、DeepSWE；0.5B-4B；全文）、Chen Fig 1b（全文）、Nguyen Fig 7（全文）、Chakma Fig 1（斜率 0.042 vs 0.112 vs 0.380，全文）。慢≠零已有一次直接重测（Chakma Fig 1）。
2. 「慢」不能归于正样本稀少或 clip/KL：Chen Fig 2-5（0.5B/Llama-3B，全文），但见 C2-1。
3. 渐近线 A 受配方选择影响（损失类型、FP32 头、批量、生成长度、模型规模），而课程/聚合/归一化等主要动效率（ScaleRL Fig 5/9/10，全文）；A 的估计依赖同分布留出集与外推，已有延长运行验证（Fig 2 的 × 标记）。
4. 起点检查点的状态影响 RL 增益：SFT 过训使后续 RL 增益下降，伴随熵低、梯度大而更新小（2606.09932，节）；预训练暴露/中训练决定 RL 响应（2512.07783，节；Chen Fig 11 只测相似度）。
5. 先学新任务后旧任务的遗忘由新任务上的 KL 预测，RL 比 SFT 偏小 KL（RL's Razor Fig 3，全文）；该规律不涉及下一任务可学性。
6. 同一目标内的课程顺序可决定目标家族能否学会：REGEX vs COMPR（2509.21016 Fig 7，节）；per-test 热身→全通过奖励才离开零区（同篇 Fig 4/5，节）。

### C2. 真正分歧及具体原因
1. 「unlearnable」是否存在：Chen（终点 pass@1<0.1 且见过正确 rollout；训练约 100-150 步；3 次训练取交集）vs Chakma（同一设置复现，只是更慢；集合规模 74→228 取决于聚合规则；梯度差距配平正确数后 2.33×→1.54×，但生成长度 1,024 vs 5,120 与原脚本不一致，作者自述）。分歧来源是**测量定义**与脚注 1 所述长训练后的陡升，不是两个对立的实验结果。
2. 「RL 之后是否还可塑」：Tiwari（Math→HoVer-hard，RL-init 40 步降到 ~0%，Fig 6）vs Noukhovitch（Manufactoria，3000 步次优奖励后换信号恢复到与全通过奖励相当，Fig 10）。具体差别：目标任务是否换了域与格式（HoVer 与数学 vs 同任务换奖励）、模型（Qwen3-8B vs Qwen3-4B-Instruct）、KL（Tiwari 的 RL 臂无 KL，Noukhovitch β=0.01）、检查点之后换的是**任务**还是**奖励/采样**、有无 fresh 对照（Tiwari 有 base-init 参考线；Noukhovitch 无）、训练步数（400 vs 约 80 小时）。两者没有在同一设置下被并排检验，所以不是已被证实的矛盾。
3. 「primacy bias」一词：Noukhovitch=Nikishin 式从零训练的可塑性丧失（他认为 Matthew 效应与之不同）；Nguyen=预训练特征的 lazy 区，证据主要来自 MNIST 玩具与公开检查点线性化；Nguyen 称「LLM RLVR 近似线性」，2601.04537 也报告近线性但解释为噪声低通（摘要+抽读，机制未读）。同一个词指两个对象。
4. 「训练更久是否扩展边界」：Nguyen Fig 8-10（Qwen2.5-3B-Instruct，MATH，512→2048 步，pass@128 总体下降、基座不可解题上升，原因归遗忘）vs ProRL/长训报告（摘要与 Nguyen 引用，未读全文）。差别：评测集是否含基座不可解题、模型是否在该域饱和、是否有 KL/参考重置（2507.12507 摘要）。
5. 停滞是否来自历史：Tiwari 的 CodeIO 停滞在两种任务顺序中都复现（Fig 22），而 RL 在末位 HoVer 反而更好；停滞与顺序/位置的关系未分开（见 C3-1）。

### C3. 没人测过的（基于以上检索与阅读；检索有限，只能说「我未检索到」）
1. 同一检查点（含/不含优化器状态与 KL 参考）分叉后，同一新任务/新奖励对 fresh 起点的**匹配算力**对照：Tiwari Fig 6 有 base-init 参考但无优化器重置变量；Fig 7/22 的连续训练主文没有基座同步数对照；Noukhovitch Fig 10 无 fresh 对照。我未检索到在 LLM-RLVR 上同时操纵「优化器状态、KL 锚、初始熵/准确率」并以 fresh 起点做对照的 RL→RL 实验。
2. 把「已学会」与「还能学」分开的度量：目前混用 Pass@1/Pass@k、斜率、渐近线 A；可塑性读数在 Tiwari 里是 Y 任务终点准确率（含格式适配与遗忘），在 Zero-to-One 里是 TTFP/N→P 计数（10 步窗口），在 Rejuvenation 里是 RL 增益。三者之间没有交叉验证。
3. 渐近线 A 作为历史相关量：ScaleRL 的 A 只在「同初始化、单阶段」下比较配方，从不同训练历史出发的检查点上 A 是否变化未被报道（我未检索到）。
4. 初始困惑度/准确率导致的天花板效应与历史效应的分离：Rejuvenation 选 EvoLM-4B（MATH-500 约 15%）刻意避开饱和，Tiwari 数学臂自述 Qwen3-8B 已饱和故改用 Base+SFT；其他 RL→RL 比较未单独控制起点准确率。
5. 「unlearnable/慢学」样本在**换历史**（换起点检查点、换前序任务）后是否仍慢：Chen 只在基座起的单段训练里定义；Nguyen 先训再按终点分段，也在同一起点；两者都未做跨历史重复。
6. 对 unlearnable 集的成员稳定性（Chakma）在跨检查点、跨训练阶段下的行为未测。
7. 单种子问题：本次读到的 RL→RL 结果（Tiwari Fig 6/7、Sun Fig 7）种子数在主文中未明示（未核对）。

## 读深度汇总（防止误读）
- 【全文】：2605.16787、2609.40115（§3.1-3.4 为主，附录仅抽读）、2605.12484、2510.13786、2509.04259、2609.13443（Fig 8-10 与 §3-6 及 App D.3 表）、2611.04061（§1-7 与附录 B）。
- 【节】：2606.09932、2509.21016、2512.07783、2611.02747、2510.02230、2601.04537（后两篇仅部分章节）。
- 其余皆【摘要】，其结论只作地图，不用于上文 C 部分的判断，除非标明。
- 未下载/未核对：ProRL（2505.24864）、BroRL、Invisible Leash（Wu 等 2026）、Sun 等 2025 Manufactoria 原文中的种子数。
