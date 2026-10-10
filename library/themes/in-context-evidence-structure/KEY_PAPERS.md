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

## Pan, Gao, Chen, Chen — *What ICL “Learns” In-Context: Disentangling Task Recognition and Task Learning*（ACL Findings 2023）`[摘要]`
- 分类任务上：TR（随机标签/保留语义先验）vs TL（抽象符号标签学新映射）；TL 随规模与 demo 数增长。
- 对我们：我们的分类条件同时覆盖 TR+TL（自然标签 positive/negative、even/odd、small/large）与纯 TL（nonce 标签）——两者都时间盲；时间敏感与否不由 TR/TL 决定，而由“分类映射 vs 全局变换”决定。

## Wei et al. — *Larger Language Models Do In-Context Learning Differently*（2023）`[摘要]`
- 大模型能在翻转标签下覆盖语义先验、学会 semantically-unrelated labels。
- 对我们：模型能学会翻转映射（Wei），却不知道翻转**何时**发生——在时间维度上，翻转证据被与原映射证据混在一个集合里。

## Wang, Ward, Zhang — *Comparative Reversal Learning Reveals Rigid Adaptation in LLMs Under Non-stationary Uncertainty*（IPMU 2026; arXiv 2604.04182）`[摘要]`
- LLM 作为两臂概率反转学习任务中的决策策略（DeepSeek-V3.2 / Gemini-3 / GPT-5.2 vs 人类）：win-stay 近天花板、lose-shift 衰减，反转后坚持；分层 RL 拟合给出多种僵化来源。
- 距离：多轮决策 + 自身选择的反馈（agentic bandit）；无 noise-vs-change 的规范检验、无“全局 vs 按输入路由”的边界、无机制。我们的分类映射翻转正是监督式 ICL 中的反转学习；可在叙事上把“LLM 的 in-context 反转学习失败”与认知科学的反转学习/认知灵活性文献接上。

## *The Alchemy of Thought: Understanding In-Context Learning Through Supervised Classification*（arXiv 2601.01290, 2026）`[摘要]`
- 6 个文本分类数据集、3 个 LLM：demo 相关度高时 ICL 行为更接近 kNN 而非逻辑回归（“attention 更像 kNN 而非 GD”）；相关度低时 LLM 借参数记忆胜出。无时间/顺序分析。
- 对我们：kNN/核回归视角（还有 Han 2023、Cho 2025）已被占有；我们的增量是它的**时间后果**——分类 ICL 按输入相似度而非时间选证据（“最近邻，不是最近期”，E21），以及“输出漂移被跟踪 vs concept drift 不被跟踪”的解离（E22）与规范的方向相反检验。

## Xiong, Cai, …, Lee, Papailiopoulos — *Everything Everywhere All at Once: LLMs can In-Context Learn Multiple Tasks in Superposition*（ICLR 2025, arXiv 2410.05603）`[摘要]`
- **发现：** 上下文里混合多种任务的 demo 时，模型的输出分布是各任务答案的混合（“任务叠加”），内部是各任务向量的混合；越大的模型越能同时保持多个任务。
- **与我们的距离：** 我们的 concept drift 场景正是“同一输入格式下两个相反映射的叠加”。叠加文献把混合当作能力；我们问的是混合**是否按时间结构加权**——E02/E16 显示分类映射的混合权重≈两种映射的计数（可交换），E22 显示即使 regime 被标出，混合权重也不随“哪种映射更新”改变。E24 检验另一侧：混合能否按**输入可检索的上下文**（标注者名）来选择——若能，则“叠加 + 按相似度选择”可行，缺的是“按时间选择”。
- **idea 来源：** 训练分布的任务混合 → 推理时的任务向量混合；我们的 toy（E12）与之同源（任务同质的训练 → 时间盲）。

## Krishna Kumar — *Semantic Anchors in ICL: Why Small LLMs Cannot Flip Their Labels*（arXiv 2511.21038, 2025）`[摘要]`
- **发现：** 1–12B 模型在全部反转标签的 demo 下学不会“反语义”分类器（semantic override 率为 0）；ICL 调整输入在已有语义方向上的投影，而不重写标签含义。
- **与我们的距离：** 我们的自然任务一半 base 使用反转映射；在数字 small/large 上 allA 准确率 0.97（Qwen3-4B），说明在只有 2 类、输入简单时反转是可学的，与其结论在任务难度上有边界差异。对我们更重要的含义：若“映射”主要是投影到固定语义方向，那么 concept drift 要求在上下文内重写这一投影，比改写输出格式（只需复制表面特征）难得多——这与 E22 的格式/映射解离同向，可作为机制节的相关讨论。

## Wang, Li, Dai, et al. — *Label Words are Anchors: An Information Flow Perspective for Understanding ICL*（EMNLP 2023 best paper, arXiv 2305.14160）`[摘要]`
- **发现：** 浅层把每条 demo 的语义汇聚到其**标签词**位置；深层的最终预测主要从这些标签词“锚点”读取信息。基于此提出锚点重加权、demo 压缩（只保留标签词表示）与错误诊断。
- **与我们的距离（关键近邻，机制层）：** 我们的行为结论“ICL 按输出标签存放证据，在时间/上下文上可交换地汇总”（I04、E31、E32）正是锚点机制的可检验后果：所有用同一标签词的 demo 汇入同一类锚点，锚点读出不携带“哪条更新、谁标的”这一二阶信息；换成不同的词 = 不同的锚点（E31 nonce 零泄漏），近义词锚点表示相近 → 部分合并（E31 近义词溢出 0.12–0.64）。增量：(1) 锚点机制对非平稳证据的后果（concept drift 盲、上下文交互泄漏）从未被指出；(2) 我们给出锚点之外的第二个通道——输出层面的变化点先验（标签流/格式/偏置成分规范）；(3) “换输出词”这一建设性预测被验证（E32）。
- **idea 来源：** 信息流（saliency）分析 + 隔离实验。可借鉴其“隔离标签词”方法做机制验证：若锚点不携带位置信息，则在锚点层之后注入位置/时间信息也无法恢复时间推断。

## 2026-10-10：来源条件化新结果后的参照系修正

### Cho et al. — *Revisiting In-context Learning Inference Circuit*（ICLR 2025）`[全文 §3–5.2 复读]`
- 原文：[2410.04468v3](https://arxiv.org/html/2410.04468v3)。其三步框架明确允许并行电路、直接读出及 forerunner→forerunner shortcut；“找到非label位置的通路”本身不是ICES增量。
- idea来源（DOCUMENTED于文中）：电路消融后性能未退至zero-shot → 被剩余能力逼出旁路；不是先假设唯一电路再吸收反例。
- 应学的研究动作：完整预测与干预后残差对照；区分电路存在、主导与充分。ICES E39只证明通用通路参与，E59需对不同反事实分别定位；E61再问两者是否组合。

### Cho et al. — *Mechanism of Task-oriented Information Removal*（ICLR 2026）`[全文 §2–4.4，Appendix A.3 复读]`
- 原文：[2509.21012v2](https://arxiv.org/html/2509.21012v2)。correct label未在demo出现而仍能回答，直接限制“复制已经出现的标签”的充分解释；TVS同时定义task与verbalization。
- idea来源（DOCUMENTED于问题与方法，非完整发现过程）：上述反例 → train low-rank filter测试可行 → 用两个指标测自然过程 → 组件消融建立因果。filter后的query访问被截断，是归因清晰的重要设计。
- 对ICES：E56逐层query模块跨20层，且没截断后续上下文计算，不能称无代价readout；E56c换数据与词表的失败不能单独证明source×label合取。

### Cho et al. — *Token-based Decision Criteria Are Suboptimal*（NAACL 2025）`[全文 §2–4，Appendix A.2]`
- 原文：[2406.16535v3](https://arxiv.org/html/2406.16535v3)。比较token、全词表、hidden-centroid读出；明确token probability的边界与hidden表征可分性不同。
- idea来源（DOCUMENTED论证，发现顺序未核对）：输出词embedding给定的分类方向限制calibration → 对hidden与logit做相同centroid比较。
- 对ICES：换词时准确率差不能自动归因source selection。E60 paired verbalizers的name-key transfer无收益，须优先保留输出几何/校准替代解释，不将得分涨幅当新路由。

### Dai, Heinzerling, Inui — *Cell-Based Representation of Relational Binding*（ACL 2026）`[全文 §2–3.3，Appendix A.28–30]`
- 原文：[2604.19052v1](https://arxiv.org/html/2604.19052v1)，[ACL主会记录](https://aclanthology.org/2026.acl-long.2194/)。实体×关系索引组成cell，用PLS、交换与跨域测试研究；涵盖Qwen3-8B。
- idea来源（DOCUMENTED）：从实体/顺序的单维binding扩展至discourse的entity×relation；one-shot analogy用于减少直接query表层替代策略。
- **所有权修正：** “双键绑定尚未被研究”不成立。ICES可检验的是“由demonstrations推断来源特定函数”与“检索上下文显式关系”是否采用相同计算条件，不能仅换名为双键。

### Lepori et al. — *Language Models Struggle to Use Representations Learned In-Context*（ACL 2026）`[摘要，全文未深读]`
- [原文](https://aclanthology.org/2026.acl-long.676/)。区分表示诱导与后续部署，覆盖开放模型及闭源reasoning；“表示有而不用”已属其问题空间。
- 对ICES：只能作为ownership/竞争解释参照；本文具体电路与所有任务细节未核对，不能据摘要宣称它已经/尚未覆盖我们的完整设定。

### Guo et al. — *When Context Changes: Understanding Update Failures in LLMs*（arXiv 2609.38866）`[全文 §4–6与C.1]`
- [原文](https://arxiv.org/html/2609.38866v1)，2026-09-30。current value仍可读出、old-value attention竞争、组件替换与training-free干预；直接current-state读取与复杂更新场景分开。
- 对ICES：时间更新、保留但选择失败及晚层干预均有强近邻。它不是exact collision（显式状态更新vs来源特定映射学习）；单靠新增probe/attention steering不能主张新机制。

### Ravulapalli & Chadha — *Decodable In-Context State and Model Output Across Training*（arXiv 2609.31401）`[全文 §2.1–2.2、§5、代码可用性]`
- [原文](https://arxiv.org/html/2609.31401v1)。给出反例：错误argmax不等于logits丢掉信息；比较hidden与candidate-logit decoder，明确external probe不是native readout。
- idea来源（DOCUMENTED）：前作probe-correct/native-wrong现象 → 检验训练轨迹和读出可用性，而非直接认定丢弃信息。
- 对ICES：E55可读出不定位原因；E56外部训练成功不证明native完整算法已存在。公开原始资产仍有缺口，作为概念压力而非替代本地复算。

### 研究过程材料（与论文发现顺序区分）
- [Steinhardt, Film Study](https://jsteinhardt.stat.berkeley.edu/blog/film-study)：完稿不展示全部思考；不把论文的方法章节当作发现顺序。
- [Cho 博士答辩修改记录](https://www.hakaze-c.com/phd_defense)：公开记录委员会对“哪部分是新认识”、实验依赖关系与测量依据的追问，以及rebuttal后将方法/结果重新组织的过程。它是整理后的修改记录，不是原始实验日志。
- [Hase et al., NeurIPS 2023](https://papers.neurips.cc/paper_files/paper/2023/hash/3927bbdcf0e8d1fa8aa23c26f358a281-Abstract-Conference.html)：因果定位与最佳编辑位置的桥不自动成立。ICES相应拆开表示可读出、自然计算中介与训练后的改进。

### 新异常后追加近邻（2026-10-10）
- *Test, then Route*（arXiv2608.04183，2026-08-04；[全文§3–4.2](https://arxiv.org/html/2608.04183v1)）：四donor将predicate outcome与answer word拆开；label-pair router跨词不迁移。**更重要的参照：** 原文已在query-digit位置检出早期predicate计算、随后传至最后token；不能把“答案前存在计算”当作首次发现。ICES潜在增量只能是来源条件化检索的具体消息链、何种末位诊断会误判，及可预测边界。其高准确率与donor-correct筛选设定不同于ICES保留全部弱signal实例；不混比能力数字。
- *How Few-Shot Examples Add Up*（arXiv2605.16591v2，2026-05-24；[全文§3–6与K/L](https://arxiv.org/html/2605.16591v2)）：对contextualization的QK/V做2×2 causal decomposition，FV质量收益主要来自QK reweighting。**所有权：** “routing与payload应拆开”及“二者存在交互”本身已被研究。ICES需证明来源/任务关系的具体过程与边界，而非把QK/V交换当贡献。该文关注抽取FV与注入效果，E64测的是native模型整个query的metadata-conditioned消息传递。

### E65新位置结果后重新核对（2026-10-10）

**Bai et al., Identifying and Analyzing Performance-Critical Tokens（AAAI2026，arXiv2401.11323v4，全文§5–6/Limitations）。** [原文](https://arxiv.org/html/2401.11323v4)
1. 形态：token信息汇聚与格式依赖的机制测量；不是证明模型忽略内容。
2. 压力：LabelWords/FV只盯标签或末位；其它token可带内容信息。改变前提：区分删除原token与遮住已上下文化的表示。
3. idea来源（RECONSTRUCTED）：这两种消融影响不同，提示内容通过模板/stopwords间接使用；论文叙事不是原始发现日志。
4. 距离：Wang标签锚点、Hendel/Todd全局向量、Cho forerunner；扩到token类型，并分别检验lexical meaning/repetition/structural cue。
5. 证据/短板：分类/翻译/QA，多尺寸；representation mask**始终保留demo答案token**，故不能说模板单独含全部规则。类型人工分类、mask重归一化与输出格式线索影响未完全分开。
6. 可迁移动作：保留上下文化状态而切断未来访问，再和原文本删除竞争；不能把Label marker relay本身作为ICES novelty。

**Xiong et al., Everything Everywhere All at Once（ICLR2025；arXiv2410.05603v1全文§6/附录C，与旧摘要卡并存）。** [原文](https://arxiv.org/html/2410.05603v1)
- 用100个60-shot+dummy query的末位层状态均值构造task vector，在100个新query按迁移accuracy选层；混合任务状态沿单任务向量间插值。向量凸组合可产生输出任务叠加，但irrelevant outputs更多且权重曲线非完全线性。作者明确不把它当完整解释。
- 对ICES：跨输入task-state迁移/混合向量已被拥有；E66只问在显式metadata之后、尚未见input的native cache能否选择规则。没有abstract rule唯一解释，缓存可压缩exemplars。

**Li, Campbell, Chan, Lampinen, Just-in-time and distributed task representations（arXiv2509.04466v3，全文§3–5/附录D–F；接受信息本轮未核对）。** [原文](https://arxiv.org/html/2509.04466v3)
1. 形态：inert task identity与transferrable task knowledge的动态/范围边界。
2. 改变前提：task identity遍布context、可解码，不等于每位置均可迁移完整程序；task state可消退/重启。
3. idea来源（RECONSTRUCTED）：把既有task-vector成功从“存在”扩到when/for how long，分别测identity与transfer。原文不是发现过程日志。
4. 近邻：Hendel/Todd、Cho2025/2026、Xiong；已有跨token迁移（**input前的Q冒号也能部分恢复**）、simple-vs-mixed-generation、context不同任务状态改变。
5. 实验：Gemma3 4/12/27B，Qwen3 4/8/14B；50-query development选注入层、独立余下queries评估，dummy query消除真实query泄漏。FV按token重新选critical heads；部分development限定正确答复，与ICES保留所有contexts不同。
6. 短板：失败可能是表示未形成或注入无法重新启动，作者主动保留二者；单位置不能排除跨token/cross-layer机制。混合任务局部/分布式知识已是强近邻，不能将E66 negative重命名composition瓶颈。
7. 对ICES：E66的metadata选择若成功仅提供native KV接口充分性；若失败，必须先看single/answer阳性，不能从缓存失败推断模型无function state。未来需要比较来源选择/示例检索的**具体条件与可预测算法**。

**Verbalizable Representations Form a Global Workspace（Anthropic2026，全文intermediate-swap/broadcast与方法限制）。** [原文](https://transformer-circuits.pub/2026/workspace/index.html)
- J-lens以输出Jacobian构造可命名方向，intermediate概念swap改变后续答案；与answer-direction swap比较生效层，避免把答案共线误读为中间计算。广播到多个不同下游函数，而非只看最终token的可解码性。
- 可迁移动作：先建立多种函数可消费同一状态，再谈共享机制；decoder好看不等于causal/部署。文章的relay/J-space不属于ICES。公开材料是整理后的研究论证，非原始迭代日志。

### Lepori et al. ACL2026：从摘要核对到正文（2026-10-10）
[原文§2–5与Limitations](https://aclanthology.org/2026.acl-long.676.pdf)。以随机walk引入任意词对应的grid/line结构，再要求next-word或few-shot位移规则；Dirichlet energy/distance correlation衡量几何。关键对照是即时prefilled continuation vs用户指令后延迟回答、few-shot token表示保真度、显式拓扑与meta-learning样例。不是来源probe或同任务query路由的实验；“inert”主要来自几何与下游行为分离，未直接给出来源维度的因果swap。
- frontier测试包含Gemini2.5、GPT5系列；grid仍弱于line。Gemini最多5000 reasoning tokens，GPT自行选预算；目标是是否任何模型可靠完成，不是预算匹配比较，不能借它证明所有reasoning均不管用。
- 论文保留表示不足/调用不足与CoT机制不清的限制，不提供修复并不损害其清楚的检验对象。可迁移动作是把支持“已有表示”的证据与支持“后续部署”的证据分开，加入显式结构阳性；ICES现在需进一步证明**来源、任务规则与输出的特定组合条件**，不能再以一般部署失败立novelty。

### E67：强近邻产生的明确预测（2026-10-10）
- 重读[Cho2410.04468v3§4/5.2](https://arxiv.org/html/2410.04468v3)：forerunner复制并非special-token独有；shortcut明确利用之前demo本身作为query时已形成的判断。这使E67的source-code prefix收益可由旧电路解释，不能以“找到了新位置”立novelty。区分**prefix局部address**与**prefix的历史计算**才是下一必要动作。
- 重读[Wang2305.14160v3§3](https://arxiv.org/html/2305.14160v3)：anchor reweighting直接把注意力看成分类器，单head/layer的label键决定系数、可训练截距调贡献；压缩依赖标签上下文化状态。E67全prefix格式改变但label-only K/V迁移不足，不能说该文错误，需量化其它carrier/全query计算的边界。

**Huang, Zhang, Zhang — Challenging the Explanation Based on Preceding Tokens: Discovering Transferable Non-Literal Biasing（ACL2026 short；全文§2/Limitations）。** [原文](https://aclanthology.org/2026.acl-short.52.pdf)
1. 形态：观察＋替换/迁移preceding text的行为证据，关注解释faithfulness。
2. 前提：字面上不包含答案的前句也可能带有特定答案的预训练联想；以语义类似的改写、删掉实体证据检验。
3. idea来源（RECONSTRUCTED）：从CoT解释疑问转向答案前措辞的独立作用；不是原始发现日志。
4. 证据：Llama2-7B、DeepSeek-R1-distill-Qwen7B；GPT5.2造prompt/改写；样本仅保留Llama在40tokens内生成指定答案的条件，故不能把其比例当未经挑选任务分布的普遍率。
5. 边界：等义改写、字面不相关不消除预训练搭配/概率选择偏差；论文明确没有直接揭示模型实际reasoning，也未解决CoTfaithfulness。E67的source code与rule orientation随机独立、最终标签/词频不变，与该文静态答案关联不同；但任何prefix提高margin都不能自动称新算法。
6. 可迁移动作：把prefix作用与实体证据独立改变。ICES需分别核对accuracy/source排序与K/V/history，不能只看answer confidence。

### E69/E70后再次校准所有权（2026-10-10）
[How Few-Shot Examples Add Up, §2.3/5–6与Appendix K](https://arxiv.org/html/2605.16591v2)已经用跨example edge isolation和QK/V patch测contextualization。附录K更进一步：x→x、y→y、错配/跨task例子产生的Q也可能维持原任务FV与QK alignment；作者主动保留“相关semantic manifold而非唯一task identity”的解释。因此label-independent alignment或宽泛非任务specific state**不是ICES空白**。
ICES E69指定prefix K全label列禁读、E70的common key translation仅改变fixed-Q下的group logit偏移（组内相对分数不变），是更具体的竞争解释；只有可迁移gate/共同frame与selection/content的明确边界及新布局预测，才可能构成增量。不要把label-blind/history必要的对照重新命名成首次发现contextualization；他们关注FV注入，ICES关注native完整query与指定cached carrier，证据范围不同。


### Bakalova et al. — Contextualize-then-Aggregate（COLM2025/arXiv2504.00132v2）与Cho的过程材料（2026-10-10继续核对）
[全文§3.2/§3.3及附录H](https://arxiv.org/html/2504.00132v2)。该文已用保持/改变输入空间、输出空间、具体identity、functional mapping的donor拆解contextualization内容；部分task的context边传domain而非具体item或rule。§3.3用可同时符合copy/past的ambiguous例子增加不确定性，保留full-model正确行为后再辨别必要路径。**所有权：** 历史依赖不等于任务知识、position-level circuit、任务相关边界都已有；E69不能将no-label历史作用本身当新认识。ICES潜在距离是source-code关系×载体位置的具体预测，以及公共K平移固定Q不变性与预测/来源排序恢复的分离；还需要native/模型边界。
[Cho公开Hidden Calibration审稿材料](https://www.hakaze-c.com/reviews/hidden_calibration)是讨论与批评的过程材料，**不是完整发现记录，也不证明实验发生顺序**。reviewer指出probe/calibration额外监督、总标注数据预算比较，以及几何separation若只重复accuracy为何有额外理解价值；AC肯定简单想法与全面比较，并要求补数据效率对照。对ICES：E56额外1.31M训练参数、E70每层每head偏移都须明示资源；新状态图/方向只有能检验新的推断、给出独立预测时才加深理解，不能凭漂亮几何自动升级贡献。

### E72–E74：改进观测与反事实，而不是靠失败立新意（2026-10-10）

**Heimersheim & Nanda, How to use and interpret activation patching（方法预印本2404.15255v1，正文§2–4）。** [原文](https://arxiv.org/html/2404.15255v1)。形态：方法解释/测量。AND/OR或冗余路径令noising与denoising并非互补；大幅恢复不识别整个算法，抑制组件可造成超过100%的恢复。idea来源RECONSTRUCTED：简单反例拆开常用因果读数的含义。最近邻是patching/circuit faithfulness；不提出ICES新机制。对我们：E56/E70过恢复与“修复≠完整原算法”属于已有方法认识，不能据此立novelty；新增价值必须是具体反事实及可预测行为。

**ICLR2026作者blogpost：随机walk几何与induction heads。** [原文](https://iclr-blogposts.github.io/2026/blog/2026/iclr-induction/)，正文模型/消融/简单邻居混合构造。形态：重现＋过程解释；不是已确认的全图推理算法。消融induction heads伤预测、几何却可留存；对随机向量作前词邻居混合也能出现grid PCA，需用bigram表示检查构造预测。idea来源DOCUMENTED于作者整理的过程材料，不是原始逐步日志。最近邻Lepori的geometry/deployment分离。对我们：几何像某种结构不等于部署该结构；先构造会产生相同图的更简单算法，再找分歧读数。

**Fang et al., ICL Ciphers（2504.19395v1，正文方法/覆盖与局限，后续版本未全文比对）。** [原文](https://arxiv.org/html/2504.19395v1)。形态：学习/检索边界的受控测量；输入词替换为双射cipher，独立noise与coverage控制；作者保留二者难完全分离及自然性限制。idea来源RECONSTRUCTED：操纵能否从demo恢复输入意义，超越只换标签。近邻SUL-ICL、task recognition/learning。对我们：bijection/不可识别性与coverage不是空白；E74仅进一步问来源内函数约束与正向label支持的相反预测。

**Gur-Arieh et al. Mixing Mechanisms重读§3.4/§4（v2，非新增论文）。** [原文](https://arxiv.org/html/2510.06182v2)。其reflexive并不是“按来源检索”：中间变量指向目标word，移植后需要原context有该词才能dereference。令反事实目标词在原context缺失，ℓ层移植不输出该词；ℓ+1已取回答案时可输出，排除通用absent-word抑制。这个**改变可访问对象＋下一阶段阳性**的动作，比画注意力更有辨别力。组合模型.95为1−JSD分布相似度，非95%全词表准确率；训练/测试分割发生于机制索引组合。ICES若做word来源/关系来源分离，需要越过该文和Test-then-Route已有的指针/答案区分，不能重命名即当增量。

**E74定位（不是novelty裁决）。** venue corpus两次nearest：抽象“provenance/scoped completion”命中多篇非ICL任务，不能当无近邻证据；改用“label anchors / unseen label / information removal”后Cho2026第一，另有Selective Induction Heads、Task Recognition/Learning、Without Copying等。最新arXiv/主文核对仍以Cho、Incomplete ICL、ICL Ciphers、Mixing Mechanisms、Test-then-Route为强参照。compression risk：只是已知排除机制换了带来源任务；或只是“attention非解释”的新例。潜在增量须是**source-local关系使用与答案词读出的独立因果预测及成立边界**，当前没有证明。不能据检索排序或热度自动关线。

**Ortu et al., Competition of Mechanisms（ACL2024；2402.11655v2，正文§3–6；另TMLR条目同题命中但受访问验证、未全文核对）。** [原文](https://arxiv.org/html/2402.11655v2)。形态：熟知的事实召回与context-copy的竞争，idea来源RECONSTRUCTED于正文；并非完整发现日志。它已发现支持事实的头也读counterfactual word，但主要压低该词；因此“读某token≠采用该token的事实”早有强机制参照。post-softmax缩放两/三条attention边提高原事实响应，含GPT2/Pythia；10K实例按原事实正确、单token属性筛选，alpha网格选最优，logit lens尤其早层不保证重要性，正文主动保留简单模板/模型限制。E74若未来成功仍只是source-scoped证据的候选，必须在新映射、owner/foreign分解与可预测条件上超过该文，不能将泛用的读取/采用区别当首次贡献。

**Khandelwal / Pavlick, How Do Language Models Compose Functions?（2510.01685v2）。** 阅读范围与ICES距离见[论文卡](khandelwal2026-function-composition.md)；本次整理保留一般组合gap与处理机制选择的已有所有权，不继续把函数任务有效性当ICES主线门槛。

### 本次人审计后的核对（2026-10-10）
- [CoSToM论文卡](li2026-costom.md)：自然心理状态→行为问题，有监督构造与下游验证；不把它说成原生电路完整逆向，也不将涨分方法作为ICES的要求。
- How Few-Shot Examples Add Up已核对[ICML2026官方记录](https://proceedings.mlr.press/v306/wang26hp.html)，重读§2.3/§4–6及QKV操作定义：干预的Q/K/V主要供最后token的FV，区别于ICES整个query上的实际source-code载体。一般上下文化/QK−V分离已有所有权；这不是完整算法的自动覆盖证明。
- [Selection–Realization论文卡](li2026-selection-realization.md)：新搜到并读§2–5，已有共存规则的query条件选择与表示恢复/行为恢复区分。不能将自然问题当空白；具体原生载体的反事实分解仍需实测。
- Test, then Route重读§3–4.2：四donor把predicate与答案身份解耦，筛四donor都正确的范围明确；token-bound路由的结论限指定patch/学习子空间，不是所有路由不可能抽象。
- corpus nearest本次命中ICR及多个广义routing工作，不能当无近邻证据。以上只输出定位与compression risk，不自动关线；E81只检验source-conditioned分类的具体因果解释。
- [Cho Hidden Calibration](https://arxiv.org/html/2406.16535v3)重读§2.2/3与讨论/限制：label-token方向与决策边界已有缺陷分析，额外监督centroid可改善，但不能据此说默认表示已完全部署。E81的s/b分解只是对现有输出读数的精确解释，不以它立新校准贡献；新的因果证据在固定码分配与更广query读取的反事实比较。

### E82前：强近邻的具体预测，而不是泛称QK/V已知（2026-10-10）

再次细读[Wang2026 §6–7](https://arxiv.org/html/2605.16591v2)：query-only与examples-only corruption分别偏向改变示例总预算与示例偏好，capitalization有相反特例。因此**access/selection的宽泛分离已直接被研究**，不能作为ICES中心新意。§7还区分query-input相似性与task-identity信息量，给出离散任务下query-independent FV的构造；这是特定理论/FV路径，不等于全模型的所有query都无关。多规则ICL的问题是query需要决定哪条规则有效，不能只用“对唯一任务的信息量”描述所有示例。E82先检查whole-query读取收益是否主要落在Label或query relay，而不是为了术语区别再做一轮mass/selection图。

[Cho2025 §5.2](https://arxiv.org/html/2410.04468v3)重读原生消融：主label检索断开后仍有输出，作者提出并行电路、直接解码和forerunner shortcut，并未宣称完整枚举。因此ICES若只发现其它位置参与不构成反驳；应建立Source条件如何改变这些已有操作、为何单末位视角可能误判的具体预测。E82的固定log概率拼接同时重归一化其它组，须保留这个测量限制，不能包装成独立组件的百分比归因。
