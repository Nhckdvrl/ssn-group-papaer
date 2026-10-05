# Key papers — in-context evidence structure（深读卡，持续追加）

格式按 `templates/paper_card.md` 压缩：形态 / 压力 / 改变的前提 / idea 来源 / 与近邻距离 / 证据 / 可迁移动作 / 对我们。

---

## Kossen, Gal, Rainforth — *In-Context Learning Learns Label Relationships but Is Not Conventional Learning*（ICLR 2024）`[全文 §5–8]`
1. 形态：构念检验（把“理想常规学习者”写成 3 个零假设，逐一拒绝）。
2. 压力：Min 2022 说 ICL 不学 label 关系；Bayesian/GD 理论说 ICL 是通用学习算法——两边结论相反。
3. 改变的前提：不用准确率，用 **概率指标随 context 增长的轨迹**；把“学习者应如何对待信息”变成可拒绝的 NH。
4. idea 来源（RECONSTRUCTED）：统计学习者的公理化性质（exchangeability、能覆盖先验）→ 对 LLM 做 property test。
5. 距离：与 Min 2022 同问题但换度量；§8 是我们最直接的父工作——D→F / F→D / 交替 F↔D，在 2N 处翻转与默认标签数量相等，三者预测不同 → 拒绝 “ICL 平等对待 in-context 信息”，结论是 **偏向离 query 近的信息**。
6. 证据：LLaMa-2 / Falcon 多尺寸，SST-2/Subj/AGNews 等，500 次重复，bootstrap CI。
7. 短板：只给出“recency”这一个描述；**未区分固定位置核 vs 结构依赖**；交替条件是 50/50 最大冲突，不是“少数噪声”；无 normative 对照（Bayes 下 D→F 本来就应偏 F）。
8. 可迁移动作：把理想学习者的性质写成可拒绝零假设；同数量、不同顺序的配对设计。
9. 对我们：§8 的 recency 结论我们不能再主张。我们的增量必须是 **非可加性 / 方向相反预测**：在 Bayes 下“多给反例反而更不信反例”（噪声前缀），这是 recency 核无法产生的。

## Jiao, Wang, Hu — *Understanding the Dynamics of Demonstration Conflict in ICL*（arXiv 2603.04464, 2026）`[全文 §1–4]`
1. 形态：失败模式 + 机制（probe / logit lens / head 定位 + ablation）。
2. 压力：冲突研究多在 context–memory 冲突；规则归纳任务（zero-shot≈chance）里的 demo 间冲突无人细看。
3. 前提：选择 “demonstration reliance + majority rule + modularity（每条 demo 独立、等权）” 的任务（Operator Induction、Fake Word Inference）。
4. idea 来源：position bias 文献（Wang 2024, Cobbina 2025）+ ICL head 机制（Cho 2024 的 forerunner token 分段）。
5. 距离：把 Halawi 2023 的“false demonstrations”换成规则归纳 + 单点冲突；增量 = 新失败模式（单个错例平均 −16pt，最多 −58pt；错误中 71–81% 采用了错例的规则）+ 两阶段机制（Vulnerability heads 早中层、Susceptible heads 晚层）。
6. 证据：Qwen3-0.6B/4B、Llama-3.2-3B、Llama-3.1-8B；4/6/8-shot。
7. 短板：**默认“等权”才是理想**——但在非平稳先验下，单个最近的反例被当成可能的规则变化并不完全非理性；没有 normative 基准。
8. 可迁移动作：逐位置单点 corruption 得到位置核；用 Cho 的 forerunner token 读注意力。
9. 对我们：他们的 “81% 采用错例规则” 恰好可以被重新解释为 **变化假设**；我们的 noise-vs-change 设计能区分“过度敏感的投票”与“对变化的推断”。所有权栅栏：单冲突 + 头定位不是我们的主张。

## Cho, Kato, Sakai, Inoue — *Revisiting ICL Inference Circuit in LLMs*（ICLR 2025）`[全文 §1–4]`
1. 形态：机制刻画（真实 LLM 上的三步电路 + 测量 + ablation）。
2. 压力：induction circuit 只在玩具模型上被验证；真实 LLM 的 ICL 现象（位置偏置、标签噪声鲁棒、demo 饱和）零散无统一解释。
3. 前提：把 ICL 分解为 ① 输入编码在 forerunner token（“Label:” 的冒号）上形成线性表示 ② forerunner token head 把文本表示无选择地复制到 label token（semantics merge）③ induction head 在任务子空间里检索与 query 相似的 label 表示并复制回 query。
4. idea 来源：Elhage/Olsson induction 电路 + Singh/Reddy 玩具模型 + kernel alignment 表示度量。
5. 距离：把玩具电路搬到 Llama-3-70B；用电路解释已知现象：**recency 来自输入编码的“位置相似度偏置”**（近邻位置的 forerunner 表示更相似）；标签噪声鲁棒来自 label 语义与文本子空间的重叠。
6. 证据：Llama 3 8B/70B、Falcon 7B/40B，6 个分类数据集，k=4。
7. 短板：电路是**逐条检索 + 相似度加权复制**——天然可加；没有讨论 demo 之间的交互（一致性/结构）如何进入预测。
8. 可迁移动作：forerunner-token 分段读注意力；用 centroid/kernel alignment 测表示。
9. 对我们：给出“Account A（固定位置核）”的机制版本——若行为呈现非可加的结构依赖，说明电路图缺少一个“证据一致性/结构”通道；这是接到 Hakaze 系工作的机制问题（条件分支，E02 之后）。另外它预测 **demo 与 query 的相似度决定影响力**（kernel 视角，Han 2023），而规则推断视角下非规则属性的相似度无关——我们的单点翻转核可以顺带检验。

## Cho, Yang, Minegishi, Inoue — *Mechanism of Task-oriented Information Removal in ICL*（ICLR 2026）`[摘要]`
- zero-shot 表示包含“所有可能任务”的信息；few-shot demo 的作用是**移除**无关任务信息（低秩 filter；Denoising Heads）；ablate denoising heads 在 “正确标签不在 demo 中” 时尤其伤。
- 对我们：结构推断可以理解为在“旧规则 vs 新规则”两个任务子空间之间的移除/保留；未来机制分析可测 change 条件下旧规则信息是否被移除（vs 噪声条件下被保留）。

## Yang, Cho, Inoue — *Localizing Task Recognition and Task Learning via Attention Heads*（ICLR 2026）`[摘要]`
- TSLA 定位 TR heads（把 hidden state 对齐到任务子空间）与 TL heads（在子空间内旋转到正确标签）。
- 对我们：规则反转（同一任务子空间内标签映射翻转）应主要由 TL heads 承载；noise vs change 的区分若存在，候选位置是 TL heads 的输入加权。

## Yang, Cho, Zhong, Inoue — *Unifying Attention Heads and Task Vectors via Hidden State Geometry*（NeurIPS 2025）`[摘要]`
- separability（早层，previous-token heads）→ alignment（晚层，induction heads + task vectors）。

## Bigelow, Wurgaft, …, Lubana — *Belief Dynamics Reveal the Dual Nature of ICL and Activation Steering*（2511.00617, 2025/26）`[全文 §3–4]`
1. 形态：理论 + 受控实验（闭式 Bayesian belief 模型，r=0.98 预测 LLM）。
2. 前提：ICL = 累积似然证据，steering = 改先验；二者在 log-odds 空间可加 → 预测相变。
3. 关键模型：log p(x|c) ∝ −#(与概念不一致的标签)，再乘亚线性折扣 τ(N)=N^{−α}（解释 many-shot power law）。**纯计数 = 可交换证据**。
4. 对我们：他们的 belief 模型无顺序项；我们的问题恰好测试该模型的边界。另一个大胆连接：N^{−α} 亚线性证据累积 **可能正是非平稳先验的表现**（旧证据被折扣）——可作为后续检验（H-sublinear）。

## Bigelow, Lubana, Dick, Tanaka, Ullman — *ICL Dynamics with Random Binary Sequences*（ICLR 2024）`[全文 §1–4]`
- “Cognitive interpretability”：不看内部，用认知科学的 Bayesian 模型选择框架解释 LLM 行为；发现 model selection（S 型突变）而非 model averaging。
- 对我们：方法论直系祖先（行为 + normative 模型 + 认知科学范式）；我们换成 change-point/oddball 范式。

## Falck, Wang, Holmes — *Is ICL in LLMs Bayesian? A Martingale Perspective*（ICML 2024）`[摘要+结论]`
- exchangeable 数据上的 Bayesian 学习者必须满足 martingale 性质；GPT-3/3.5/4、Llama-2、Mistral 违反；不确定性缩放也偏离 Bayesian。
- 对我们：**调和点**——违反 exchangeability 不等于“非 Bayesian”；如果 LLM 是带非平稳先验的 Bayesian，它在可交换数据上必然违反 martingale。我们的 meta-oracle 能量化这一点。

## Arora, Jurafsky, Potts, Goodman — *Bayesian Scaling Laws for ICL*（2024/ICLR'25）`[摘要]`
- 把 ICL 曲线写成 Bayesian 形式（任务先验、学习效率、每例概率）；用于 many-shot jailbreaking 预测。计数式。

## Gupta et al. — *Enough Coin Flips Can Make LLMs Act Bayesian*（2025）`[摘要]`
- 有偏硬币：先验校准差，但更新大体 Bayesian；（他们也提到注意力强度对 Bayesian 推断影响小）。

## Schubert, Jagadish, Binz, Schulz — *ICL Agents Are Asymmetric Belief Updaters*（ICML 2024）`[摘要]`
- 认知心理学范式（两臂 bandit）→ LLM 学习率不对称（乐观偏差），随 agency 框架改变；用 meta-RL 理想智能体对照。
- 对我们：同一“认知科学范式 + 计算模型拟合”路线；我们的范式是 Nassar 的 changepoint vs oddball，量化“隐式 hazard / noise 先验”。

## Xu et al. — *When Should Models Change Their Minds? Contextual Belief Management*（BeliefTrack, 2605.30219）`[§1–3]`
- 多轮、逻辑（确定性）证据、显式更正、无关噪声；Failed Stay / Update / Isolation；RL + steering 修复。
- 距离：他们的“更新”由显式 CORRECTION 触发，“噪声”是任务无关文本；我们是**统计**噪声 vs 规则变化、无任何显式信号，问题在于 **从证据的组织方式推断**。不冲突，但在叙事上是“agent 何时改主意”的同一大问题。

## Dudley, Bi, Liu, Oymak — *ICL Under Regime Change*（ICML 2026）`[摘要+引言]`
- 形式化 in-context change-point detection；构造 transformer（层数随 change-point 信息量变化）；训练小模型达最优；TS foundation model 加 change-point 提示有用。
- 距离：从头训练/构造；**不问预训练 LLM 是否在噪声与变化之间做推断**。

## Qin, Jiang, Zhu — *Learning to Adapt: ICL Beyond Stationarity*（ICLR 2026）`[摘要]`
- GLA 在 AR(1) 漂移回归中实现可学的 recency；理论。

## Letey et al. — *Sequential Correlations Change ICL*（2607.03660, 2026）`[摘要]`
- 相关 prompt 等价于更短的 iid prompt（有效 context 长度）；query 相关时 softmax 更优。

## Bai, Chen, Wang, Xiong, Mei — *Transformers as Statisticians*（NeurIPS 2023）`[摘要]`
- 构造证明：单个 transformer 能按输入序列自适应选择算法（post-ICL validation / pre-ICL testing）。
- 对我们：理论上“结构选择”可实现；我们问的是预训练 LLM **是否**做了、做得多 normative、在哪坏掉。

## Park, Lubana, Pres, Tanaka — *Competition Dynamics Shape Algorithmic Phases of ICL*（ICLR 2025）`[摘要]`
- Markov 链混合任务：四种算法（模糊检索 vs 推断 × unigram/bigram）竞争，context 长度/训练量决定哪一个胜出。
- 对我们：“算法随 context 改变”的玩具版本；我们的问题是真实 LLM 的证据聚合算法随证据组织而变。

## 认知科学参照
- **Nassar et al. (2010 J Neurosci; 2012 Nat Neurosci; Nassar, Bruckner & Frank 2019 eLife)**：changepoint 条件下学习率随惊讶上升，oddball（离群）条件下随惊讶下降——同样的预测误差，统计语境决定其意义。**我们的 E02 是 ICL 版 changepoint-vs-oddball。**
- **Piray & Daw (2021 Nat Commun)**：联合估计 stochasticity 与 volatility；噪声↑ → 学习率↓，波动↑ → 学习率↑；二者需要互相解释掉。
- Behrens et al. 2007（volatility 调节学习率）；Adams & MacKay 2007（BOCPD）。

## Chan, Dasgupta, Kim, Kumaran, Lampinen, Hill — *Transformers Generalize Differently from Information Stored in Context vs in Weights*（2022）`[摘要+引言]`
1. 形态：认知科学范式（Dasgupta 2022 的 rule-vs-exemplar 判别分类任务）+ 受控训练。
2. 发现：受控刺激上 in-context 泛化偏 **exemplar**，in-weights 偏 **rule**；但在自然语言预训练模型上 ICL 显著偏 rule，且模型越大越 rule；假说：语言中稀疏的规则结构使 rule-based ICL 涌现（用受控数据验证）。
3. 对我们：rule vs exemplar 已被占有；我们的增量是把它与 **时间证据结构** 连起来——exemplar 式聚合天然对时间盲（只看相似度），因此 (i) 无法区分噪声与变化，(ii) 对变化的适应是“局部的”（只在与新例相似的 query 上翻转）。Qwen3-8B pilot：单点翻转影响由相似度决定（规则属性同值 +0.61、每个无关属性 +0.15），exemplar 模型逐条拟合最好——与 Chan 的“大模型更 rule”是否一致，要看规模扫描。

## Li, Ding, Hu — *Understanding Generalization and Forgetting in In-Context Continual Learning*（2605.28705, 2026）`[摘要]`
- 线性/masked 线性注意力理论：多任务顺序 prompt 中注意力均匀/因果聚合历史 → 任务间干扰、遗忘；bias–variance–interference 分解。
- 对我们：理论上“注意力聚合不区分时间”；我们在真实 LLM 上直接测到“相似度而非时间”的聚合。

## Qiu et al. — *When Correct Demonstrations Hurt*（2605.26350, 2026）`[摘要]`
- 正确但输入被扰动的 demo 也会伤 ICL（contextual evidence shift）：demo 的效用取决于它如何改变“证据混合”，与正确性分离。
- 对我们：与 exemplar/相似度视角一致——demo 的影响由其在表示空间中与 query 的关系决定。

## Yin & Steinhardt — *Which Attention Heads Matter for In-Context Learning?*（ICML 2025）`[摘要+引言]`
- 12 个模型（70M–7B）、45 个自然语言 ICL 任务：归纳头与函数向量（FV）头几乎不重叠；消融 FV 头显著伤 few-shot ICL，消融归纳头影响有限；部分 FV 头在训练中由归纳头演化而来。
- 对我们：他们的任务多为“变换”（反义词、翻译、大写…）。我们的边界（变换时间敏感 / 分类时间盲）给出一个新的机制假设——**FV 式的函数推断在 demo 间做时间敏感整合，归纳/检索式的按内容复制则对时间盲**。可检验：从 suffix vs disp 的 context 抽 FV 并 patch 到零样本 prompt。

## Todd et al. — *Function Vectors in Large Language Models*（ICLR 2024）`[摘要+引言]`
- 因果中介分析找到少数注意力头，其平均输出（FV）可在零样本 context 中触发任务执行；FV 可组合。
- 对我们：提供抽取/patch 函数向量的工具；问题是 FV 如何在 demo 之间聚合证据（对时间结构是否敏感）——这在文献中没有人问过。

## Hendel, Geva, Globerson — *In-Context Learning Creates Task Vectors*（EMNLP 2023 Findings）
- ICL 可压缩为一个 task vector θ(S)，再作用于 query。
- 对我们：θ(S) 对 S 的顺序/时间结构的依赖从未被刻画；我们可以测 θ(suffix_4) vs θ(disp_4)。
