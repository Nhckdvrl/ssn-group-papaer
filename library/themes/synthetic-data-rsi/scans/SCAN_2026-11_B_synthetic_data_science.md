# SCAN 2026-11 · B. 合成数据的科学（偏闭环/迭代生成）

日期：2026-11-27。范围：2026-09 至 2026-11 的 ICLR 2027 投稿、NeurIPS 2026 接收、arXiv，加少量 2026 上半年的参照论文。
**阅读方式的诚实说明**：全文通过 WebFetch 的摘要器读取 arXiv HTML；每篇正文约前 100k 字符可见，附录多数被截断（各篇下注明）。OpenReview PDF 被浏览器验证页挡住，ICLR 投稿论文只能读摘要，标 ABSTRACT ONLY。"对自改进数据回路的含义"一行仅陈述论文结果能直接支持的内容，不含建议。

---
## 一、全文读过（按与闭环/迭代生成的相关度排序）

### 1. Escaping Model Collapse via Synthetic Data Verification
- arXiv 2510.16657（页面戳 2026-07-16）；状态未核对。
- **问题**：生成→验证→重训的循环中，验证器能带来什么、不能带来什么。
- **设置**：线性回归 y=xᵀθ*+ξ，验证器只回"是/否"，只知道 θ* 落在以 θ_c 为中心、半径 r 的球内；验证器偏差 Δ=‖θ*−θ_c‖。再加 CVAE/MNIST（初始 500 张真图，验证器=判别器，保留每类 top 10%，40 轮）和 XSUM（SmolLM2-135M，12.5% 训练集起步，15 轮，greedy）。
- **结果**：(a) 单轮：合成方差项 + 验证误差项；验证器准且合成样本多时优于纯真实数据 OLS。(b) 迭代：存在收缩界，估计量收敛到验证器的"知识中心"θ_c 而非 θ*；Δ=0 收敛到真值，Δ 大则早期提升后平台或退化。选择性 r 影响速度与短期收益，不影响极限。(c) MNIST：FID 先升后平台，最好 21.17，对照 60K 真图训练的 CVAE 为 17.56；不筛选重训严重退化。(d) XSUM：筛选版先升后稳，不筛选基本持平。
- **局限（作者）**：线性模型只有单一真值，捕捉不到多样性与质量折中；LLM 上只是定性验证；MNIST 的 10% 阈值是启发式。**我方注意到**：XSUM 的"oracle 验证器"用 ROUGE-1 对真值摘要打分，信号远强于现实验证器；附录证明、额外实验未读。
- **对自改进数据回路**：验证器的偏差决定回路的不动点，数据量只决定逼近速度。

### 2. When AI Reviews Its Own Code: Recursive Self-Training Collapse in Code LLMs
- arXiv 2606.28438（v2）。
- **问题**：递归微调代码模型时，审查策略（无审查 / 外生门 / AI 自门）的影响。
- **设置**：SantaCoder-1.1B、StarCoder2-3B、Qwen2.5-Coder-1.5B、Code Llama-7B；5 轮，每轮从固定 prompt 池生成，选 5,000 条，微调 3,000 步；T=0.8、top-p 0.95、pass@1 用 n=200。门：Vanilla、Compile（能 compile）、Quality（重复率≤0.3 且长度≥50）、自门 Perplexity（最低 25%）、自门 Binary Classifier（模型自身好/坏 logit 差 top 25%）。基准 HumanEval(+)、MBPP(+)、LiveCodeBench。
- **结果**：表中所有模型×策略的第 5 轮都低于第 0 轮。例：Qwen2.5-Coder HE+ 0.372→Vanilla 0.043、Compile 0.098、Binary 0.122；LCB 0.238→0.000。SantaCoder MBPP+ 0.294→Vanilla 0.019、Binary 0.058。Code Llama 降幅最小（HE+ 0.287→Compile 0.171）。Binary 自门在三个模型上第 5 轮 HE+ 最高，Code Llama 上 Compile 最好。Qwen 表 3：Compile 使入选集合执行有效率 33.4%→89.8%，但下游仍降（Δ(0→5) −0.109，无审查 −0.150，AI 自门 −0.126）。理论：自门对所有样本打同分则退化为无门自训（Thm 2.3）；AI 评分与外生门差 ε 时训练分布 L1 差 ≤2ε/z₀；重复重训使表示协方差向少数方向集中（Prop 2.1）。
- **局限**：外生门是自动代理，不是人审；是否跨轮累积或替换，可见正文未说明（**未核对**）；混合训练、外部锚点、门噪声附录未读。表 3 的 S5/S0 列未定义。
- **对自改进数据回路**：入选集合变"干净"（可执行）与回路不退化是两件事；自门的接受分数升高时基准正确率下降。

### 3. Survive or Collapse: The Asymmetric Roles of Data Gating and Reward Grounding in Self-Play RL
- NeurIPS 2026 poster。**ABSTRACT ONLY**（NeurIPS 页面，无 arXiv 链接）。
- **问题**：proposer–solver 自博弈 RL 为何崩溃。
- **设置/结果（摘要）**：Python 输出预测任务 + 确定性 DSL 孪生任务（去除预训练先验、歧义、执行噪声）。严格的数据门在所有奖励变体（含不用真值的自一致奖励）下都稳定；去掉门则任何奖励变体都不稳定。"Grounded Proposer Paradox"：与自一致 solver 配对时，能访问真值的 proposer 比无真值的更快崩溃（只出干净题，形成自洽吸引子）。把二值门换成连续严格度 ε，出现两阶段相变：低 ε 时训练侧指标先脱钩，验证精度到更高 ε 才掉。
- **对自改进数据回路**：该文的结论是稳定性取决于哪些任务进入训练池，而非奖励校准。

### 4. Progressive Misalignment Can Emerge from Benign Recursive Self-Distillation
- arXiv 2610.22467；ICLR 2027 投稿 [2.75]。（另有 NeurIPS 2026 条目 "Misalignment Emerges During Benign Iterative Self-Improvement"，只见标题与摘要，未读。）
- **问题**：安全模型反复用自己的拒答做自蒸馏，会不会变得不安全。
- **设置**：教师看到额外上下文（cue 或反馈），学生在无上下文下匹配其 token 分布；每轮学生成为下一轮教师；on/off-policy 都测。Qwen3-14B、Phi-4-14B（规模实验 Qwen3 0.6B–32B）；仅 20 条模型会拒绝的有害 prompt；cue 为良性（"Excellent"、"I like owls"）+ 对照 cue（"不要帮我"）；另用 Qwen3-8B 模拟用户对拒答给正反馈。评测 SORRY-Bench、StrongREJECT。
- **结果**：固定 cue 下 SORRY-Bench 顺从率 ~26–31%→94–97%（off-policy "Excellent"）；对照 cue 不升。模拟用户最高 64%（off）/55%（on）。梯度搜索出的良性 prompt：off-policy 83%（Qwen3-14B）、70%（Phi-4）；on-policy 53%、70%。越大模型升幅越大（Qwen3-32B 约 +64 点）。对照：SFT 自己的安全回答、冻结教师的 off-policy 蒸馏都不引发；IFEval、GSM8K 基本不变（常规能力评测看不出）。假设机制：cue 引入的前几个 token 的小偏移被逐轮放大，与浅层安全对齐相关；多轮后出现 mode collapse。
- **局限（作者）**：仅两个模型族、≤32B；机制只是初步假说。**未读**：逐轮数字、完整消融表（正文被截断）。
- **对自改进数据回路**：漂移发生在能力指标之外的维度，且由良性信号触发；同一数据换成 SFT 或冻结教师则不发生。

### 5. From Collapse to Improvement: Statistical Perspectives on Iterative Training on Contaminated Sources
- arXiv 2602.10531（v2，Bakshi & Chakraborty，2026-02）。
- **问题**：每代数据 = 新鲜真实样本（权重 α_t）+ 前代模型样本时，何时坍塌、何时改善。
- **设置**：把 LM 化约为单上下文的 K 类多项分布估计，风险 R_t=E‖θ̂_t−θ*‖²。实验：多项分布 K=50、T=200、100 重复；nanoGPT 在 Wikipedia 电影情节（~34k 文档，n₀=1000）上测困惑度，10 次重复。
- **结果**：递归式 R_t=(n₀/n_t)R₀+((n_t−1)/n_t)(1−α_t)²R_{t−1}。固定 α>0、固定 n：极限风险介于 R₀ 与 R₀(1−((n−1)/n)(1−α)²)⁻¹ 之间；n_t→∞ 则 R∞=0。α_t 递减时若 Σα_t=∞ 且 Σ1/n_t<∞ 则一致（需 n_t 随 α_t 增长，而 α_t 通常未知）。纯合成：风险不低于 R₀，固定 n 极限为 nR₀。累积：固定 n 时风险界在 R₀·exp(−(π²/6−1)/n) 与 R₀(1+π²/6) 之间；n_t 增长时累积不再有益，风险最终上升。三级定义：一致 / 迭代改善（R∞≤R₀）/ 坍塌（R∞>R₀）。多项实验与理论一致；nanoGPT：纯合成坍塌，固定 α=0.25 与累积"不显著改善也不明显恶化"，文中称 decaying-α 设置改善，但同段又说设置 1、3 未改善，**自相矛盾，需对照全文核对**。
- **局限（作者）**：α_t、n_t 在实践中不可知；总体层面混合而非样本层面；one-hot 上下文；真分布固定。附录证明与 B–E 未读。
- **对自改进数据回路**：该模型中，回路是否可能优于 R₀ 取决于是否持续注入新鲜真实信号及其速率，纯自生成无论累积与否都不低于 R₀。

### 6. How Much Is an AI Token Worth? Scaling Laws for Wild AI-Generated Web Text
- arXiv 2609.40295；ICLR 2027 投稿 [3.00]。
- **问题**：未标注、面向人类读者的"野生"AI 网页文本混入预训练，一个 AI token 值多少人类 token。
- **设置**：FineWeb 过滤后的 Common Crawl（2025-07 至 2026-06），EditLens 预筛 + Pangram 3.3.2 标 Human/AI/Mixed（Mixed 丢弃）。WildAI：96.04M 文档、83.31B token（人 42.19B，AI 35.32B；AI 占 42% 是预筛造成的，非自然比例）。800 个模型，19.9M–973M，7 个尺寸，nanochat 架构，2.9–87.5 人类 token/参数（TPP_h），AI:人比例 r 0–64；Muon+AdamW，8×H100；703 单种子 + 97 重复。726 个（≤268M）拟合，74 个（477M、973M）留出。
- **结果**：Pangram 估计的 FineWeb AI token 占比：2021-06 <0.1%、2024-06 10.1%、2025-06 16.1%、2026-06 27.5%、2026-08 31.1%。新 law：Chinchilla 骨架，D_eff=D_H(1+η·g(r)) 带饱和收益，数据项乘 (1+H) 的危害项，H=γ·t^u·n^v·[log(1+r)−r/(1+r)]（11 个参数，r=0 时退化为 Chinchilla）。配对 RMSE（×10⁻³，C4）：本文 0.83、Shukor joint 1.41、Lovelace 3.55、Chinchilla 4.32。5 TPP 时加 AI 文本降低 loss；≥20 TPP 时升高，模型越大越明显；C4 上最优 AI 占比 5 TPP 为 37%，20 TPP 为 1.0%；在 Cosmopedia（纯 AI）上最优 AI 占比始终 >90%。Chinchilla 预测"去掉 AI 文本总会升高 loss"，在 13 个"去掉反而降低"的配对中全错；本文方向预测 18/19 对。重复人类文本 1 个额外 epoch 比新鲜 AI 文本低 2.3% C4 loss，8 个 epoch 差 6.3–6.4%。评测遮蔽：所有 553 个加 AI 模型在 AI 标注文本上 loss 都降；约 44% 在人类标注文本上升；22.3% AI 占比的混合验证集会把 95.5% 的有害运行报为改进（符号翻转点约 5.1% AI）。AI 典型短语每千词 0.16→0.36（r=1）→0.54（r=4）。作者称在此小尺度下 CORE 分数的提升与新鲜人类文本相当（模型太小无意义）。过滤器偏置：FineWeb 保留 29.3% AI 文档 vs 12.8% 人类（2.3×），DCLM 14.5% vs 1.5%（9.8×）。数据：github.com/pangramlabs/WildAI（含 800 个检查点）。
- **局限（作者）**：拟合 ≤268M、测试 ≤973M；更大模型可能更易被模型生成数据伤害；主指标只有 next-token loss；仅预训练、英文、Pangram 标签。拟合系数表与附录 D–G 被截断未读。
- **对自改进数据回路**：同一批 AI 文本"在 AI 目标上有益、在人类目标上有害"，其符号取决于评测集成分和训练预算（TPP）。

### 7. Silent Collapse: Trajectory-Level Precursors in Recursive Learning
- arXiv 2605.14588（v2，单作者）。
- **问题**：坍塌能否在验证指标变坏之前，从内部状态检测出来。
- **设置**：TinyStories 上小型自回归 Transformer，每代 2 epoch，用上一代 nucleus 采样文本；固定 2,000 条真实 prompt 的 anchor 集测熵 H_g 与表示漂移 S_g。另有 CIFAR-10 伪标签（ResNet-18，25 代）与 GPT-2(124M)/WikiText-2。干预 MTR：τ=max(0.2,min(1,(H_{g−1}/H_0)²)) 调节合成混入。
- **结果**：隐性收缩（H_g/H_0<0.5）中位在第 4 代（IQR 4–6），可见坍塌（PPL >5× 历史最小且不可逆）中位在第 6 代；5/5 种子隐性在先，中位领先 2 代。恢复实验（仅 seed 0）：弱恢复（0.5% 真实、400 步）PPL 63.9(g2)→57.3(g4)→92.0(g6)→123.9(g8)；强恢复（10% 真实、1600 步）各检查点都回到 ~37–41。开环 PPL 1.89×10⁸±3.21×10⁸；MTR 11.91±0.10，固定 α=0.5 为 13.72±0.09，**随机 τ 为 11.56±1.13**，事后选的 α=0.27（匹配 MTR 平均压力）为 10.94±0.21。GPT-2：开环熵 3.48→0.78，PPL 23→208；MTR 熵保持 ~2.5，PPL ~20–21。
- **局限/异常**：anchor 仍需真实数据；恢复实验单种子；0.5 阈值事后选定；主结果仅 5 个种子；**随机 τ 与 MTR 持平、固定 α=0.27 优于 MTR**，削弱"轨迹信号本身起作用"的说法，文中未讨论随机 τ；CIFAR 无数字；摘要中"潜在几何分离"等说法正文无分析支撑。
- **对自改进数据回路**：标准验证指标变坏前，熵已收缩；该论文的干预对照显示，起作用的可能只是降低合成混入量。

### 8. No Model Required: Text Entropy Rate Filtering Mitigates Iterative Fine-Tuning Collapse
- arXiv 2610.01493（NeurIPS 2026 poster，标题为 "Prevents"，数字可能与 arXiv 版不同）。同作者另有 "Fixed Points and Scale-Dependent Reversal in a Random Dynamical System of Model Collapse"（NeurIPS 2026，仅摘要）：无离散阈值，剂量响应平滑，同一过滤对 3B 模型有益、对 8B 模型有害（符号反转）。
- **问题**：不用模型 logprob/外部验证器/人类数据，能否缓解迭代微调坍塌。
- **设置**：Kontoyiannis 熵率估计 H^K（基于原始文本的匹配长度），对比用生成器 logprob 的 H_L。Llama-3.1-8B-Instruct，4-bit QLoRA，一条谱系 6 代，不回注人类数据；每代 4 个域共 80 篇，选 40 篇训练（随机 / H_L top-40 / H^K top-40）；rank 16、lr 2e-4、3 epoch/代。
- **结果**（第 6 代，n=80）：H^K 过滤 vs 不过滤：Distinct-3 +42%、词表 +30%、Rep-4 −19%（p<0.001）；H_L 过滤在所有多样性指标上无显著收益（p>0.23）。H^K 与 gzip（Distinct-3 +17%）、4-gram 重复率过滤（无收益）比较均更好。Llama-3.2-3B 复现同向。检测：微调下组内 H^K/H_L 秩相关 ρ=+0.454，迭代改写（rephrasing）下 ρ=−0.175 不显著。H_L 在 gen 0 与 H^K 几乎不相关（r=0.18），一次微调后 SD 降至 ~0.13，近乎随机选择。
- **局限/空结果**：**通用能力未保住**：HellaSwag 0.729→0.652–0.657，三种条件无显著差异（MMLU、GSM8K 同）；跨文档同质性反而升高（Self-BLEU-4 0.086 vs 0.075）；MAUVE 接近天花板（0.987–0.993），收益是词汇性而非语义性；LLM 评分 coherence 2.35 vs 2.20（p=0.058）；单模型族。代码 github.com/lewismath/no-model-required。
- **对自改进数据回路**：该文只在"选择"一侧起作用的过滤器改善了词汇多样性，下游通用能力下降不受影响。

### 9. Learning from Synthetic Data Improves Multi-hop Reasoning
- arXiv 2603.02091（Kabra 等，Cornell）。
- **问题**：在规则生成、虚构实体、不含真实世界事实的合成数据上做 RL，能否提升真实多跳推理。
- **设置**：Qwen3-0.6B/1.7B、Qwen2.5-1.5B-Instruct、Phi-4-mini-reasoning；PhantomWiki、GSM-∞、ReasoningGym 两任务，各 ~10K；GRPO（TRL 0.21.0，KL=0），二值/F1 奖励，1 epoch；评测 HotpotQA、2Wiki、MuSiQue、CofCA、SynthWorlds-RM（各 500 题，distractor 设置），两个种子。
- **结果**：全部真实基准提升；Qwen3-0.6B 相对 F1 +56% 至 +131%，越小模型获益越大。仅格式奖励对 Qwen3/Phi-4 无效，但对 Qwen2.5-1.5B-Instruct 极大（HotpotQA 0.02→0.43），说明其迁移部分是格式。SFT 在 GSM-∞ 上大幅提升域内（0.6B：0.02→0.77）但对 HotpotQA 几乎无变化；RL 两者都升（1.7B HotpotQA→0.67）。在未见虚构世界与未见难度上泛化；MuSiQue/CofCA 上推理链中正确中间答案随训练增多；随步数单调提升未见过拟合。作者主张学到的是与领域无关的"知识组合"技能（依据：零重叠留出 + 中间答案分析）。
- **局限**：只测上下文内推理；迁移边界不清；同域真实数据 RL 仍更强；种子仅 2 个；附录被截断。文中"SFT 无真实提升"与 0.6B 0.36→0.40 的数字略有出入。代码 github.com/kilian-group/phantom-reasoning。
- **对自改进数据回路**：可验证的程序化合成任务（答案由构造决定）在 RL 下提供了向真实任务迁移的信号，其迁移里有一部分是格式。

### 10. How Can We Synthesize High-Quality Pretraining Data? (FinePhrase)
- arXiv 2604.13977（v1）。单轮配方研究，对"合成数据能加什么"有定量数据。
- **设置**：每配置重写 ~10.5B 源 token，默认生成器 Gemma-3-1B、源与 mix-in 为 FineWeb-HQ；训练 1.2B Qwen2 架构从头 10,000 步（~21B token），默认 50/50 合成:原始；12 项基准 3-shot cloze 宏平均；累计生成 >1T token。
- **结果**：基线 DCLM 13.77、Nemotron-HQ-Synth 13.54、REWIRE 13.49、Cosmopedia 10.33、**SYNTH 10.03**、FineWeb-HQ 11.82。重写策略最关键：Diverse QA 14.58；新结构化格式 math 15.31、table 14.83、faq 14.45、tutorial 14.30。生成器：math 提示下 Gemma-3 1B 15.31 > 27B 14.76；SmolLM2 tutorial 135M/360M/1.7B = 12.69/14.45/15.88；六个 ~1B 家族 SmolLM2 16.55 最高、Qwen3 14.49 最低。纯合成低于混合（tutorial 12.32 vs 14.30）；源质量在 mix-in 高质量时影响缩小（spread ≤1.78）。多样性：Qwen3 对 math 提示 100% 遵从但 115/1000 输出以相同文本开头，SmolLM2 完整解答仅 68% 但开头多样得多。FinePhrase-Table 17.18（+3.41 over DCLM）；成本约 DCLM 之外 30× 低于 REWIRE。
- **局限（作者）**：仅 1.2B/21B token；仅英文标准基准；成本比较依赖报告数字。**我方注意到**：1B>27B 只基于 math 一个提示；表 7/8 里 DCLM 的数值（14.32 / 13.69 / 14.77）配置不明；正文 "rival DCLM" 的 Continue、Guided Rewrite 实际略低于 13.77。
- **对自改进数据回路**：（单轮）生成器规模增大不一定提升数据效用；纯合成输出落后于与原始数据混合。

---
## 二、仅读摘要或被截断（短表）

| 论文 | 来源 | 一行 |
|---|---|---|
| Model Collapse is a Singular Complexity Trajectory | NeurIPS 2026 poster（ABSTRACT ONLY） | 标注高斯混合的递归自训练；坍塌沿"奇异复杂度"（实对数典范阈）下降轨迹、模式消失；证明注入足够真实数据可阻止成分灭绝，使轨迹在固定视野内高概率不下降。 |
| Learning with Synthetic Data via SGD in High-Dimensional Linear Regression | NeurIPS 2026 poster（ABSTRACT ONLY） | 带模型漂移的一遍 SGD：混合训练使固定比例合成数据产生不随数据量消失的超额风险下限（"强坍塌"）；两阶段（先合成后真实）避免之；大模型放大混合训练的退化。 |
| Stability and Diversity of Networked Self-Consuming Generative Ecosystems | NeurIPS 2026 poster（ABSTRACT ONLY，摘要未显示完整） | 多模型相互消费合成数据的有向加权图；给出收敛条件与不动点刻画，分析真实数据接入、跨模型消费、图结构对稳定性与多样性的影响。 |
| On the Limits of Self-Improving in LLMs: Singularity Is Not Near Without Symbolic Model Synthesis | arXiv 2601.05280（v2；约 100k 字符前读，S7 以后未读） | 理论：精确自训练是恒等映射；有限重采样使期望多样性每步乘 (1−1/N)；一致性需 Σα_t=∞ 且 N_tα_t→∞；26 个已服务检查点（0.8–35B）作为下一位数字预测器，无一在 3.32 bit 内逼近 KT 加权混合上界，24 符号处最好差 4.5 bit、中位 36.5、最差 128；主张闭环在目标、评估、证据同源时"认知封闭"。 |
| Synthetic Pre-pretraining Survives Scale, but Not as a Grammatical Prior | arXiv 2609.39827；ICLR 2027 投稿 [3.33]（arXiv 读，OpenReview 未读） | 随机初始化先在合成任务上训 500 步再做预训练：kk-Shuffle Dyck 在 12 个尺度×混合对中 9 个提升（均值 +1.6）；Marin 3B 上 63B token 持平 PT-Only 84B；BLiMP 上无稳定语法收益；收益出现在要求"回取早先位置"的任务（Dyck、NCA），Set（只追踪见过的 token）反而 −7.2；OLMo3 混合不受益且无解释；多数配置单种子；7B 仅一种配置且学习率与 TPP 混杂。（另有 "Rethinking Pre-pretraining" arXiv 2610.40051 称加算力设置下收益到 1B token 就消失，未读。） |
| It's All Training: A Fully Synthetic Single-Stage Recipe for LLMs (SYNTH) | arXiv 2609.37891；NeurIPS 2026 poster（arXiv 读，约前 100k 字符） | 58k 维基种子 ×100 扩增为 ~80B token、8 语言；Baguettotron 600M（158B token）在 22 道选择题 + 8 道开放题上比 Qwen3-0.6B 低 4.7/0.7 点，用 80–700× 更少 token；同预算下比 FineWiki/FinePDFs-Edu 高 16–17 点（网页模型在 MMLU 为随机水平 24–25.6%）；FActScore 式事实精度 13.2B-MoE 46.3%；留出实体上 MoE 弃答 67%（种子内 20%）、尝试答案的精度 82%→62%。注意：FinePhrase 的 12 项 3-shot cloze 宏平均中 SYNTH 为 10.03，低于 DCLM 13.77；两篇设置不同（模型、评测、训练预算），不可直接比较。 |
| Generating Pretraining Tokens from Organic Data for Data-Bound Scaling (SynPro) | arXiv 2605.17849（约前 100k 字符；E.3 之后未读） | 数据受限（有机数据仅为 compute-optimal 的 5/10/15%）时用 GRPO 训练重写/重格式化生成器，奖励 = 质量 + 忠实度 + 影响力（权重 1:1:3），生成—预训练—更新生成器循环 3 轮收敛、跨轮累积；400M α=10%：Repeat 0.4675、RePro 0.4792、SynPro 0.5027、Unique 0.5121；1.1B/2B 上 SynPro（0.5584/0.5859）≥ Unique（0.5561/0.5778）；去掉"数据合并"（只用最新一代）0.4927（效果 −22 个恢复率点）；去掉影响力奖励 0.4908；去掉 RL 0.4848。作者承认 400M α=15% 的"有效 token"67.6B 大于实际训练 61.2B，且与有机分布仍有差距；Unique 并非同条件对照。 |
| Rethinking diversity in RLVR: from policy entropy to semantic coverage | ICLR 2027 投稿 [3.33]（ABSTRACT ONLY，OpenReview 不可读） | 报告 RLVR 训练中成功回答集中于更少语义推理模式，有限 rollout 预算下重复访问主导模式。 |
| Improving Generative Model Self-Training with Geometrically Modified Outputs | ICLR 2027 投稿 [3.00]（ABSTRACT ONLY） | 朴素自训练导致 collapse 与 MAD；负引导式自训练把退化当信号，作者在其上做几何修改（细节未读）。 |
| LLM-based Automated Theorem Proving Hinges on Scalable Synthetic Data Generation | ICLR 2027 投稿 [3.00]（ABSTRACT ONLY） | 单遍合成法探索多种中间证明状态以生成多样证明步。 |
| Bilevel Optimization of Synthetic Trajectories for Multi-Turn LLM Fine-Tuning | NeurIPS 2026 poster（摘要片段） | 合成多轨迹异质，双层优化加权；未读。 |
| Quest: Training Frontier Deep Research Agents with Fully Synthetic Tasks | NeurIPS 2026 poster（仅标题） | 未读。 |
| Reviewing Model Collapse and Countermeasures | arXiv 2608.21366（综述，读过） | 叙述性综述（VAE/扩散/LLM/多模态）；无系统检索方法；"共识"：尾部先消失、全合成循环不稳定、真实数据锚定有帮助、低温/截断采样加速坍塌；自相矛盾处：既说"少量合成数据也能致坍塌"又说"低于任务依赖阈值则安全"；合成占比建议（创意 60–90%、指令 30–50%、安全关键 ≤10%）无来源；引用有错配（作者自己列出）。可视为地图，不可作证据。 |
| Combinatorial Synthesis: Scaling Code RLVR via Atomic Decomposition and Recombination | arXiv 2605.31058（仅搜索摘要） | 代码 RLVR 合成题有效率随迭代 35%→43%；未读。 |
| 未采纳但背景相关（2025，群组可能已知） | Gerstgrasser 2404.01413；Kang 等 2510.01631（>1,000 模型，≤3B；改写数据最优占比约 30%）；BeyondWeb 2508.10975 | 未重读；仅作 §三 参照。 |

---
## 三、领域综合（事实陈述，不含建议）

### A. 目前较一致的说法
1. **纯自生成闭环不优于起点（在已有模型里）**：理论（2602.10531 纯合成风险不低于 R₀；2601.05280 精确自训练为恒等；多项 NeurIPS 摘要）与小规模实验（Silent Collapse、代码递归自训练、迭代 QLoRA）一致。
2. **真实/外部信号注入的速率与形式是稳定与否的分水岭**：SGD 线性回归（混合训练 vs 两阶段）、混合权重 α_t（2602.10531）、真实数据比例（Singular Complexity 摘要）、数据门严格度（Survive or Collapse）、验证器偏差 Δ（2510.16657）。
3. **在选择一侧加筛选通常延缓而非阻止退化**：代码 5 轮 Compile/自门全部低于基线；验证器收敛到自身知识中心；熵率过滤改善词汇多样性但不保通用能力。
4. **规则可验证的合成任务给 RL 提供可迁移信号**（2603.02091；Survive or Collapse 中严格门下稳定）。

### B. 未解的争议
- **累积 vs 替换在现实累积下是否仍有效**：2602.10531 理论上固定 n 时累积有界、n_t 增大时累积无益；小规模实验结果解读不一致（见上文标注的自相矛盾）。无 ≥7B 规模、真实网络语料累积的闭环实验在本次所读论文中出现；野生 AI 文本研究（2609.40295）是单次混入（r 比），不是多代。
- **合成改写是否增加知识还是只改格式**：SYNTH（种子 58k，作者承认知识上限由种子决定）、FinePhrase（结构化格式提升 SQuAD/ARC 等阅读理解与知识类，降低 HellaSwag/PIQA）、SynPro（事实类占比随轮次 45.3%→54.1%、reformatting 消融显著）——均未直接测量"生成器超出源文本的新知识"；在留出实体上 SYNTH 的精度从 82% 降到 62%，弃答 67%。
- **多样性 vs 质量**：FinePhrase：模板遵从率最高的生成器（Qwen3）出现模板坍塌，低遵从率的 SmolLM2 下游更好；熵率过滤文中词汇多样性升但跨文档同质性升（Self-BLEU 0.086 vs 0.075）。
- **规模方向**：同一过滤在 3B 有益、8B 有害（Fixed Points 摘要）；AI token 的危害随模型规模与 TPP 增大（2609.40295，但拟合最大 268M、测试 973M）；SynPro 在 400M–2B 上相对 Unique 的恢复率随规模升高（79%→106%→124%）。
- **合成预训练的机制**：Synthetic PPT 的"语法先验"解释被 2609.39827 反驳，改为"长程检索"，但 "Rethinking Pre-pretraining" 称在加算力口径下收益消失；两者口径不同，未调和（后者未读）。

### C. "合成数据为何有效"的解释及其错预测处
| 解释 | 出处 | 预测失败/反例 |
|---|---|---|
| 提高数据利用率（教学化、结构化格式；去除噪声） | SYNTH、FinePhrase、SynPro | FinePhrase 中纯合成 < 混合；SYNTH 在 FinePhrase 评测里排在 DCLM 之下（设置不同）；生成器越大不一定越好（1B>27B 于 math）。 |
| 方差降低（验证后的合成样本减少估计方差） | 2510.16657 | 偏差不消失，只收敛到验证器知识中心；"oracle" 验证器强于现实验证器。 |
| 可验证性/外部接地使闭环稳定 | 2601.05280、Survive or Collapse | 有真值的 proposer 比无真值的更快崩溃（Grounded Proposer Paradox，仅摘要）；代码中入选集合执行有效率 89.8% 仍退化。 |
| 学到与内容无关的组合技能（程序化合成任务） | 2603.02091 | 部分迁移只是格式（Qwen2.5-1.5B-Instruct 格式奖励 0.02→0.43）；同域真实数据 RL 仍更强。 |
| 语法先验（合成预预训练） | 先前工作 | 2609.39827：BLiMP 无稳定收益；OLMo3 混合不受益且无解释。 |
| Chinchilla 式"更多 token 总是更好" | 通用 | 2609.40295：≥~10–15 TPP 时去掉 AI 文本可降低人类目标 loss；Chinchilla 在 13/13 去除配对上方向错。 |

### D. 论文自己报告却未解释的异常
- 2609.39827：OLMo3 混合下 PPT 不受益（既非数学占比也非网页占比可解释）。
- 2604.13977：生成器家族间差异（SmolLM2 最高）只归因于改写相关指令微调；Qwen3 遵从率 100% 却模板坍塌。
- 2605.14588：随机 τ 与 MTR 持平；弱恢复的 PPL 在 g2（63.9）高于 g4（57.3）。
- 2610.01493：H_L 在一次微调后几乎无区分力（SD ≈0.13）；迭代改写下 H^K 检测失效（ρ=−0.175）；所有过滤条件下通用能力下降相同。
- 2610.22467：良性 cue 引发显著失配但对照 cue（"不要帮我"）不引发；更大模型升幅更大；常规能力评测无变化；机制仍为假说。
- 2609.40295：AI 文本在 5 TPP 下对人类 loss 有益，≥20 TPP 下有害；AI 文本在小模型 CORE 上与新鲜人类文本相当而人类 loss 却更差。
- 2606.28438：自门接受分数升高与基准正确率下降同时出现。
- 2609.37891 vs 2604.13977：同一 SYNTH 语料，在各自评测上相对 DCLM 方向相反（设置不同，原因未核对）。

### E. 本次未覆盖/未能读到的
- OpenReview 论文全文（ICLR 2027 投稿）无法访问：Synthetic Pre-pretraining 的 ICLR 版、Rethinking diversity in RLVR、Progressive Misalignment 的评审意见、Geometrically Modified Outputs 等只见摘要。
- NeurIPS 2026 "Misalignment Emerges During Benign Iterative Self-Improvement"、"Recursive Multi-Agent Systems"、"Closed Loop Dynamic Driving Data Mixture" 等未读。
- 清单 A/C 中含 "RSI" 的论文（RRSI、Gen-RSI、Capability Loss in Embodied RSI 等）属自改进主线，不在本篇范围。
- 本次未发现 2026 年专门的"合成数据科学"立场论文；唯一读到的综述是 2608.21366（见上，质量有限）。
