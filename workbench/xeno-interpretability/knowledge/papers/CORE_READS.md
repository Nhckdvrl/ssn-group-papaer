# 核心论文精读 · 解释、因果结构与语义可达性

**2026-10-12。** 核心研究卡集中维护，避免每篇生成重复文件。**“起源重建”一律 RECONSTRUCTED**：是我们从原文论证反推研究设计的合理路径，不是作者关于历史灵感来源的证言。带数值的判断来自论文实验图表，未独立复现；不同版本的数字须回查其链接。

## 1. Feldhus & Kopf — Concept Descriptions Survey（BlackboxNLP 2025）
**原文：** [PDF](https://aclanthology.org/2025.blackboxnlp-1.8.pdf)；**阅读：主文 §1–6 + 关键评估段落。** 类别：综述，非新实证论文。

**研究谱系**：从人类预先列概念的 probing/TCAV，发展到根据 top-activating examples 让另一个 LLM 生成 *open-vocabulary* 描述；原来的评价多看描述是否让模拟器重现激活。§4 系统区分：(i) **simulation**（simulator-LLM 根据描述预测 activations）、(ii) **input contrast / specificity / AUROC**、(iii) **output-based causal intervention/steering**、(iv) 与已知标签的语义一致性、人类判断。这些维度不等价。

**关键研究压力**：模拟器也是黑箱模型；高预测相关性可能只是模拟器善于识别表面形式，不能证明模型实际使用某个“语义变量”。作者在 §6 强调 causal validation、对描述器自身偏差的分析、回路级组合解释以及 OOD stress test。

**idea 来源重建**：给模型内部变量命名 → 观察流畅标签难鉴别真伪 → 问“解释应通过什么测试” → 把解释可预测性、覆盖率、行为介入分层，而不是提出新的神秘概念。

**与 Xeno 的距离**：针对人类可表达的解释工具和评价；没有实证“人类本体必然遗漏哪些概念”。**可迁移**：任何声称“不可描述”的研究，先给语言/程序解释一个有竞争力的基线。

## 2. Wang et al. — Concept Bottleneck Models Survey（IJCAI 2026 Survey Track）
**原文：** [PDF](https://www.ijcai.org/proceedings/2026/0892.pdf)；**阅读：方法分类、典型对照、挑战等选定主文部分。** 非实验论文。

**改变的认知**：把概念可解释 AI 当作模型设计范式而非 SAE 自动标签。§3–6 把 **concept acquisition / concept-based decision / intervention / evaluation** 拆分：manual/LLM/VLM/prototype 自动发现；hard/soft/hybrid bottleneck；test-time concept correction；faithfulness 与 intervenability。强硬瓶颈虽能明确约束信息流，也会因概念不完整而降低精度；残差通路可恢复性能却弱化“决策全部经由概念”的可解释保证。

**idea 来源重建**：概念层提升透明性 → 人工概念昂贵且覆盖不足 → 用自动发现/视觉原型补充 → 发现可读性、预测准确率与真实可干预性相互牵制。与 Xeno 直接相关的“本体遗漏”其实已有成熟的 CBM 邻域，不是一个全新主题。

**实验启发**：比较“加入未知残差提高准确率”与“新增可解释概念解释残差”是两件事；前者不能直接作为后者的成功证据。该综述为**地图**而非新算法 benchmark。

## 3. Ma 等 — NeurIPS 2025：Revising and Falsifying SAE Feature Explanations
**原文：** [NeurIPS main PDF](https://papers.neurips.cc/paper_files/paper/2025/file/5b6ce2529a79862a2d8ac57ac0e01d90-Paper-Conference.pdf)，[官方代码](https://github.com/GeorgeMLP/feature-interp)。**阅读：主文 §1–6、图3–5、补充表1/附录相关段落。**

**Parent → pressure**：Bills 等通过 top-activating inputs 让 LLM 给特征一句解释，再用模拟器给一致性分数。问题：解释往往**宽泛、召回导向**；随机负样本太容易，难辨别“代码中定义”与单纯“有代码”等边界。

**作者的研究动作**：用 sentence embedding 从真实语料检索**与阳性相似但 activation 为零**的 close negatives；解释输出为多条 `activates_on + strength` 规则，允许一特征多语义；tree explainer 在模拟误差最大的例子上迭代改写，而不是一次性写 label。图3 比较 `random` 与 `similar-negative` 的假阳性，图4 用相同测试集比较 one-shot、structured 与 tree，图5分析多规则数。

**可核数字**：图4 unstructured 条件下 tree 相对 one-shot 提升 **19.8% Gemma-2-9B / 21.6% Llama-3.1-8B / 16.4% GPT-2 Small**；structured one-shot 分别 +5.8/+8.4/+9.2%，tree 情况下不再有明显结构化收益。表1 Gemma one-shot unstructured **0.363±0.032** vs tree unstructured **0.435±0.030**（模拟激活相关性）。加入训练负样本或 holistic activations **没有帮助**，是重要负结果。

**设计逆向**（RECONSTRUCTED）：若一个描述“看起来合理”，如何主动使其犯错？→ 保持语义相似而真实激活为零，能够隔离解释的 specificity；遇到假阳性再修订说明，形成闭环。这是实验推动方法，而非先堆更复杂解释模型。

**局限与距离**：依赖 top activation、以模拟器预测为目标、tree 约 1.5min/feature；**解释提升不直接证明是模型自然采用的因果机制**（§6）。“更强语言描述+hard negatives”已由本论文占据，不能当 Xeno 原创方案；但应作为所有概念缺失主张的强负对照。

## 4. Ma 等 — ICML 2026：Do SAEs Identify Reasoning Features in Language Models?
**原文：** [ICML 2026 / arXiv v7 PDF](https://arxiv.org/pdf/2601.05679)，[代码](https://github.com/GeorgeMLP/reasoning-probing)。**阅读：主文 §1–7、理论/方法/结果、附录 E/G 部分。注意早期旧稿数据有变化；以当前 v7 为准。**

**Parent → pressure**：大量工作从 CoT vs non-CoT 激活差选择所谓“reasoning feature”，甚至看到 steering 改变输出，便赋予推理语义。CoT 同时引入 `wait/therefore/let` 等**低维且反复出现的语言线索**，构成混杂。

**方法为何自然**：先给出简化数学模型 (h=a v_1 + b g)：稀疏重建可能倾向稳定低维 cue，而抑制许多维度中分散变化的真实计算信息。再做**双重 falsification**：① 非推理文本中只注入少数相关词元，观察候选 SAE feature 是否激活；② 对余下难解释的特征，让 LLM 生成形式相同但不推理的 false positives 与保持推理意义却改写形式的 false negatives。最后加少量 SAE 方向 steering 作为独立 sanity check。

**尺度与读数**：**22** 个模型×层×语料配置；Gemma-3-4B/12B、DeepSeek-R1-Distill-Llama-8B 等；s1K 与 General Inquiry CoT 对 The Pile 非推理样本；每配置按 activation difference 选 top100。摘要统计 **45%–90%** 受少量词元注入影响；在 **248** 个依上下文而定的候选特征中，经 LLM 辅助反例构造 **0** 个满足作者操作定义的单特征纯推理语义。表5 steering 结果很小或下降（示例 AIME baseline 26.7% → 20.0%）。

**强处与脆弱处**：它不仅说“SAE 有局限”，还给出**一种造成错误归因的机制性偏置**和具体证伪实验；但结论只针对这些 **contrastively selected、单 SAE feature、作者的 monosemantic 判据**，不能推出模型不做推理或不存在分布式推理表征。LLM 作反例生成与判读也不是完美 oracle。

**idea 来源重建**：先看到 contrastive 解释的潜在 surface confound；若真代表 reasoning，改变词元不应在缺少推理时频繁激活；保持推理内容换语体也不应静默。理论解释为什么这不是随机坏运气。

**与 Xeno 的距离**：自动解释为何可能误认高层概念，已经是一条实证型研究程序。若后续找“难命名特征”，必须反过来先检验它是不是 **普通低维词面相关项**。

## 5. Torop 等 — NeurIPS 2026：Inverted Detection and Control in Steering Vectors
**原文：** [arXiv v1 PDF](https://arxiv.org/pdf/2608.02957)；会议名单 [NeurIPS 2026](https://neurips.cc/Downloads/2026)。**阅读：主文 §1–6、图1–4、表1、附录超参数。**

**Parent → pressure**：ITI/mean-difference steering 先用正负样本的 representation 分离方向检测一个概念，再认为沿**正方向**加向量必然促进该概念。先前已有单个输入上的 anti-steering 报告；但“在整体输入群体上，高 AUC 的方向仍系统性反向”不是低区分度/偶然点可简单解释的。

**关键发现**：部分方向虽然能区分概念正负样本，向正方向干预却**稳定抑制概念表现**（ISV）。方法不再只观察输出：定义 upstream steering 后 downstream 判别空间上的 **Inner-Product Response** `κ(α)`，再取对干预强度 α 的斜率 **Representation Response Γ**，对多个有高判别力的下游对象平均为 **spoof score**。分数为负预测“向正方向注入使后续表示看起来更不像概念存在”，不需逐向量生成回答。

**实验链**：先筛强 AUC（多用 ≥0.85）的 candidate，独立测试评估 ISV/RSV → 测量 α–行为关系与下游几何响应 → 仅用 spoof score 预判翻不翻符号 → 改进 ITI 为 ITI-RRF。模型 **Gemma3-12B、Qwen2.5-14B、Olmo3-7B**，5 个概念 corrigibility、wealth、myopia、refusal、truthfulness；**45 ISV + 45 RSV** 验证，spoof-score 区分两者 AUC **0.91**、zero cutoff accuracy **81%**；真实 steering 30 对比中 **27/30** 改善，提升范围 **+0.9%–138%**。硬件作者报告单张 **A6000 48GB**。

**为什么这个实验好**（RECONSTRUCTED）：若数据判别高分但干预反号，究竟是输出评估噪声、单样本特例，还是网络计算真的把信号反转？检查**生成前**的下游表征可以区分；若确为内在响应方向，应该能不靠昂贵输出打分预测符号。这条链使简单发现变为可操作的因果几何解释。

**边界/比较**：仅覆盖 translation-based steering；open-ended 指标使用 LLM judge，效应与超参选择有关；下游“被 spoof”不等于天然的解释变量，也不证明某种外星本体。对我们：**检测→控制不能偷偷等号** 已是 NeurIPS 2026 结果；新工作必须超越“再找一个反号向量”。

## 6. Parisini 等 — 2026 预印本：Concept Frustration
**原文：** [PDF](https://arxiv.org/pdf/2603.29654)、[代码](https://github.com/CRSBanerji/concept-frustration)。**阅读：主文 §1–3、实验 §§2.2–2.11、方法 §4.6–4.8、附录统计表。尚未核到正式主会录用。**

**背景**：概念瓶颈模型（CBM）可透明预测，但人工概念列表可能遗漏任务相关维度；传统 Euclidean feature similarity 无法反映**该任务**怎样使用几何关系。

**方法/理论**：从黑盒预测器计算 task-aligned **Fisher 几何** (ar F)，比较监督概念方向与 SAE 自监督方向，检查一对已知概念和某未知方向构成的三角关联符号是否矛盾，定义 **concept frustration γ_FA**；与普通欧氏 γ_E 对照。在线性高斯构造中将 Bayes 最优概念分类准确率分解为 known/unknown 不同项（T1–T4），用于解释为什么某些“漏掉的概念”会损害原有概念模型而黑盒仍良好。

**严谨实验及重要数字**：(a) Flat vs spherical “treasure hunter”：每种 **50 repeats**，Fisher 区分 `p=5.4e-3`，Euclidean `p=.118`；(b) 60 组参数 × 10 seeds = **600** 合成数据集，探查几何、概念缺失和精度的关系；(c) 新闻讽刺检测 **28,000** 标题，DeBERTa-v3-base embeddings，C1/C2 为正负情感，C3 为情感强度；(d) CUB-200 gull vs tern **887** 图像，CLIP ViT-B/16，C1–C3 为指定视觉属性。真实任务固定相同 SAE dictionary，在 10 折 CV 比对只监督 C1,C2 的 CBM1 与也监督 C3 的 CBM2，Fisher 概念张力前者较强（两组配对 Wilcoxon 均 **p=.0488**），欧氏指标无差异。**注意**：作者表中真实任务 CBM 的 accuracy 改善 p=.058 / .0972，不能说“任务精度显著提升”；显著的是 Fisher metric 本身。

**关键证据边界**：现实任务的第三概念 **由作者事先知道、选定，才在 CBM1 故意隐藏**；实验验证“给定缺漏线索时几何指标能区分”，**没有演示从完全未知的 LLM 自然计算中自动发现未命名变量**。另需审计 SAE 字典大小、取最极端方向、多重比较、Fisher 来自下游模型而非底座自然因果作用。

**idea 来源重建**：已知概念间矛盾（类比科学概念跳跃）→ 把“补充未知因素”转成任务几何三角张力 → 找欧氏失效、Fisher 有效的反事实 → 用已知但故意隐藏的 C3 作真值验证。对 Xeno **强 ownership**：不能声称本体不完整无人形式化；更难的盲发现与因果验证仍需文献核准。

## 7. Song 等 — ACL 2026：Mechanistic Interpretability Should Prioritize Feature Consistency in SAEs
**原文：** [ACL 2026 main](https://aclanthology.org/2026.acl-long.99/)、[早期版本](https://arxiv.org/abs/2505.20254)。**阅读：正式版摘要 + 早期公开版本有关指标的部分；未逐页核正式版完整正文。**

**Parent/pressure**：SAE 学出可读特征，但同模型同数据换 seed 可能得到不一致字典，无法把单次字典当“模型必然如此”。作者把复现提升为独立评价目标，而不仅是 reconstruction/sparsity。

**关键定义与证据**：**PW-MCC** 以跨字典成对匹配衡量 feature 一致性，容许置换/尺度等价；在理想 TopK 设置给出理论依据，并用合成实验验证与真值恢复的联系，真实 LLM activations 报告 TopK 一致性约 **0.80**，与自动概念解释相似度关联。**这仍不能证明“高一致性=天然计算单位”**：不同算法可能一致地学习共同的简化描述、且因果功能尚未得到直接证明。

**idea 来源重建**：解释不断难复现 → 先分清是模型本身差异还是分析器学习不确定性 → 引入无需“语义对齐”的可量化跨次一致性。后续只在读完正式版方法和统计之后升级这张卡。

---

## 连续精读得到的“研究动作”而非现成标题
- Ma2025：**让解释暴露错处**（相似但真正不激活的 hard negatives），而不是增加标签。
- Ma2026：**语义与表面提示分别干预**，并给出为什么方法会系统性错判的理论解释。
- Torop2026：把输出异常移至**中间传播的几何响应**，先预测下游效应，再兑现操作价值。
- Parisini2026：**在已知真值上验证构念遗漏的测量**，但盲发现仍是未证明的更强一步。
- Song2026：把解释的**跨运行稳定性**当评价对象，先确认“工具制造的特征”是否重复。

**跨论文新的问题意识**：描述器、测量器、干预器和概念本体可能各自引入误差。要提出更深解释，必须设计能区分这些来源的实验；不能把解释失败留给最夸张的“外星语义”假说。


---

## 本轮重读新增：与 Xeno 真正邻接的严肃工作

### 8. Geiger et al. — Causal Abstraction: A Theoretical Foundation for Mechanistic Interpretability（JMLR 2025）
[全文，64 页](https://www.jmlr.org/papers/volume26/23-0058/23-0058.pdf) · **FULL 理论与适用前提**。
**parent/压力**：activation patching、DAS、circuit、steering 产生很多“因果”结果，但缺少统一标准解释低层神经计算与高层变量之间何时有一致的**干预保持映射**。作者用高级模型、低级模型、干预算子与抽象关系的严格条件处理这件事，区分精确与近似因果抽象。
**RECONSTRUCTED idea 来源**：操作方法互相不兼容 → 共同对象不是“某个 SAE 特征”，而是两个因果系统及其干预交换图 → 能设计超越单个 probe 的验证。**对 Xeno 的边界**：它说明怎样验证已指定的高层解释，却没有给出生成不属于人类现有概念本体的新语义的准则。也是 Xeno 必须吸收的因果 validity 基准。

### 9. Mueller et al. — MIB: A Mechanistic Interpretability Benchmark（ICML 2025）
[全文与附录](https://pdfs.assets.alphaxiv.org/2504.13151v2.pdf)、[代码](https://github.com/aaronmueller/MIB) · **MAIN+METHODS，主要结果、设置和核心控制**。
**parent/压力**：各派方法在不相同任务、指标上称为“更好的可解释性”，难比较。MIB 分为 **causal variable localization** 与 **circuit localization**，用 IOI / arithmetic carry / multiple-choice 等确定的因果目标，统一比较 DAS、probe、SAE、PCA、patching 等路线。强 **DAS supervised** 可很有竞争力；在所测设定中把 SAE/PCA 等中间变量代替原生组件未必优于基准。
**RECONSTRUCTED**：研究的是工具所能复原的真实变量，而不是工具生成对象的漂亮程度。**局限**：测试问题和高层变量先由人规定，不能从它得出“未命名模型原生表征不存在”。

### 10. Karvonen et al. — SAEBench（ICML 2025）
[全文](https://pdfs.assets.alphaxiv.org/2503.09532v4.pdf)、[代码](https://github.com/adamkarvonen/SAEBench) · **MAIN+METHODS**。
**parent/压力**：SAE 论文通常报告重构精度、激活稀疏和解释样例，但这些 proxy 不保证下游控制或因果效用。作者在 **200+ SAEs、8 种评价** 下对照概念检测、SCR/TPP 等实用任务，同时检查多种架构及稀疏性/重构的关系。
**RECONSTRUCTED**：若字典真有科学价值，应当在独立评价任务上有信息增量，而不只是拟合激活。结果显示多种 proxy 与实际 utility 的相关性较弱，特定架构（如 Matryoshka）在某些指标上更强。**Xeno 距离**：测的是给定任务概念及可解释工具的效用，并不构成语义可达性边界的证明；可以直接拿来做强 baseline。

### 11. Sutter et al. — The Non-Linear Representation Dilemma（NeurIPS 2025）
[42 页完整论文](https://pdfs.assets.alphaxiv.org/2507.08802v2.pdf) · **FULL 理论/主要实验与附录关键论证**。
**关键争议**：若允许不受限制、极灵活的非线性映射，一个训练或随机网络的隐藏状态都能被映射到貌似实现了某特定“算法”的高级变量。定理使用 countable inputs、内部层的 injectivity、输出结构匹配等假设；实验表明随机/不解决任务的网络也可能有很高的 IIA，对“找到了抽象”形成强反证。
**RECONSTRUCTED**：不是再提升 IIA，而是问“如果错的系统也能拿到满分，这个指标到底证明了什么？”→ 构造 randomized/untrained negative → 研究对齐复杂度使得因果抽象失去可反驳性。**Xeno 启发**：越开放地挖模型未知内部结构，越需要随机模型、错任务模型、复杂度匹配、自然分布交叉验证；否则 Xeno 可能只是任意拟合。

### 12. Paulo & Belrose — Sparse Autoencoders Trained on the Same Data Learn Different Features（ICLR 2026）
[10 页原论文](https://pdfs.assets.alphaxiv.org/2501.16615v2.pdf) · **FULL**。
**parent/问题**：“一个 SAE 字典就是模型唯一的特征分解”需要跨初始化稳定性才能令人信服。作者考虑字典 latent 的置换不变性，用 Hungarian bipartite matching 最大化 encoder/decoder cosine，再比较 shared vs orphan。**实测**：Llama 3 8B 的 131K-latent SAE，不同种子训练后匹配共享特征约 **30%**；跨三个模型、多层/数据/架构复验。部分不共享的特征仍有看似自然的解释，说明**能讲故事≠模型有唯一内部 feature 原子**。
**RECONSTRUCTED**：拒绝拿无意义的 feature index 当对象 → 先对齐等价类，再问 seed 是否稳定 → 检验「解释漂亮」和「自然分解」是否同一回事。**Xeno 边界**：方法不稳定不是 xeno 证据；更粗的等价功能/关系可能跨随机种子稳定。

### 13. Goyal et al. — Causal Differentiating Concepts（NeurIPS 2025 **Spotlight**）
[29 页正式主会论文](https://proceedings.neurips.cc/paper_files/paper/2025/file/5faf0f518f39e4d6b2b595e3ca2fe0c4-Paper-Conference.pdf) · **FULL 主要实验/理论及附录关键定义**。
**必须纠正 Xeno 新颖性的归属**：这篇**无需已有概念标签**就从激活和行为类别学潜在 causal concepts。它假设改变行为类别只需稀疏地改变底层潜变量，以 constrained contrastive objective 在给定假设下辨识解耦因子；行为类别由人工归并或 model-output clustering。合成中 DCI-D **>0.89**、MCC **>0.86**；semi-synthetic 与 Llama/Qwen refusal 场景验证。SAE 32K 虽然整体信息量约 **0.95±0.07**，概念解耦程度仅 **0.58±0.07**；取信息最强的 top2 反而更差。
**RECONSTRUCTED**：SAE 稀疏表达多却不一定对应造成行为改变的独立因素 → 把“最少改哪几个中介概念使行为改变”转成学习约束 → 用合成真值和真实 refusal 检验。**Xeno 相对增量不能是“无标签因果特征发现”**；它更想要不以人类可命名标签为最终验收标准的 *semantic accessibility*，以及跨场景关系定律。也必须承认这篇发现的概念是可被人类理解的。

### 14. Sheng & Fu — Circuit Claims Depend on What Is Extracted and How It Is Compared（2026 预印本）
[26 页全文](https://pdfs.assets.alphaxiv.org/2607.18921v1.pdf) · **FULL 主要方法/对照/图表/附录**。
**parent/压力**：“机制在 checkpoint 中是否一致”的结论可能依赖比较的是原始边、粗粒度路由对象，还是哪个训练损失预算下提取的图。通过密集 vs **75%** 权重稀疏 RL checkpoints、组合任务成功/near-miss、固定提取法，比较特征：routing-set Jaccard@10 **0.666/0.554**，而 exact-edge **0.163/0.142**；near-miss 的 exact-edge 与 random 没显著不同（**p=0.106**），但 coarse routing 远高于 random。对不同抽取对象与阈值进行控制。
**RECONSTRUCTED**：先观察边级结果不复现 → 区分“实验分析尺度错”还是“自然计算换了” → 同条件在多个可比尺度重复。**不要把这些结果说成发现了 Xeno**；它说明合理模型原生研究单位可能是**因果等价类/关系结构**而非具体边。
**名称警告**：NeurIPS2026 Downloads 的《Conclusions from Circuit Extraction Depend on the Level of Description: A Controlled Comparison》标题近似，但**没有取得作者或正式版本证据，不得断定就是本文**。

### 15. Williams et al. — Mechanistic Interpretability Needs Philosophy（2025 预印本／Position）
[全文](https://arxiv.org/pdf/2506.18852) · **FULL 主要哲学论证**。
**中心**：MI 不应默认存在唯一“真正的”拆解；科学解释与高层因果/表征内容、解释单位的选择需要哲学澄清。分析多个研究问题，尤其需要区分 representation **vehicle** 和 **content**，以及什么样的操作对应合理的科学对象。
**RECONSTRUCTED**：模型分析不断声称“这个 unit 就是某概念” → 发现归因、抽象单位和因果语义的理论假设并未证明 → 先建立合理的解释标准。
**Xeno 边界**：对人类语义的局限、解释的多元性早有讨论；然而哲学批评并未完成“标记一个无法完整翻译的 ξ 并在独立干预中建立模型原生关系规律”的经验工作。

### 16. Gurnee et al. — Verbalizable Representations Form a Global Workspace（Anthropic Transformer Circuits 2026）
[作者完整技术报告](https://www.transformer-circuits.pub/2026/workspace/index.html)、[arXiv](https://arxiv.org/abs/2607.15495) · **MAIN+METHODS（实验与技术正文，部分在线附录未逐图复核）**。
**Xeno 直接 parent**：过去靠模型实际生成的词推断“它心里有什么”；作者提出 Jacobian Lens（平均未来词元概率对中间激活的线性响应）定义 poised-to-verbalize 的 **J-space**，用 concept swap、任务内 silent reasoning、跨任务调用、workspace 容量/广播等实验验证。作者报告少量 verbalizable 内容能被下游灵活复用，某些自动解析或常规推断发生在 workspace 外部；不是每个模型内部变量都有相同语言报告通道。
**RECONSTRUCTED**：把“内部有信息却没说”变成**可测的输出准备度**，不止看是否在当前回答发声。**重要区分**：J-space 外≠“没有人类可理解的语义”；那里可能是普通句法/数值/格式特征。它是评估 *verbal reportability* 的强基线，但不是语义可达性的完备 oracle。Xeno 可探索二者系统性差异。

### 17. Li et al. — Inside the Visual Mind / ViSAE（ICML 2026）
[19 页会议原论文](https://pdfs.assets.alphaxiv.org/2606.06664v1.pdf)、[PMLR](https://proceedings.mlr.press/v306/li26s.html)、[代码](https://github.com/deep-real/ViSAE) · **MAIN+METHODS：§1–4、图1–7、表4–8与主要附录定位**。
**Parent/pressure**：ViT 传统 saliency 回答“在哪里”，而基于 SAE 的视觉概念解释面对**输入概念覆盖不足**、命名依赖主观摘要和跨层计算关系不清的压力。作者将视觉神经科学四层抽象（primitive/intermediate/object/scene）作为数据收集原则，构建约 **64K 图像、16,050 人类视觉概念**，CLIP + Soft-WPMI 自动给 SAE 的 top-activated 特征读语义，再用上游 SAE feature ablation 和下游 activation variation 连接 causal concept graph，提供诊断与 steering。
**方法与实验**：在 CLIP ViT-B/32 CLS/image-token 多层上比较 ReLU/Gated/JumpReLU/BatchTopK/Matryoshka SAE，最终用 **8× expansion、L0=128 的 BatchTopK**。表4 top-30 concept interpretation accuracy：使用 ImageNet/自建概念集 **50.7%**，MSCOCO/自建集 **51.2%**，自建图像+词表 **54.1%**；对照 LAION15K 和 Google20K 等明显较低。WaterBirds 表7 削弱 background concepts 后 worst-group **50.3→98.5%（+48.2点）**，增强方向使其降到 **5.3%**；表8 在相同 SAE 设置下由 ImageNet 探针训练的最差组为 **63.9%**，MSCOCO 为 **95.4%**，自建探针为 **98.5%**。
**RECONSTRUCTED idea 来路**：不是再发明 SAE，而是原来“只看像素/单个图层”缺少层间因果链 → 用视觉层级建设强概念覆盖的系统测量 → 定位反直觉的背景捷径 → 设计**反向增强/抑制**和数据源消融获得可信下游动作。**Xeno 的真实差异**：ViSAE 目标从头到尾是丰富 **人类视觉概念集合** 并赋义，验证其有用性。它使“词表不够好导致无法解释”成为 Xeno 必须认真排除的强零假设，但不等于证明模型没有概念集合之外的可复现关系结构。**局限**：强结果主要在单个 ViT 家族/WaterBirds，intervention 可改变后验决策却未自动证明 SAE 概念是原网络天然唯一分解，外推至跨域 xeno 不充分。


---

## 18. Gur-Arieh et al. — Enhancing Automated Interpretability with Output-Centric Feature Descriptions（ACL 2025 Main）
[原文/正式身份](https://aclanthology.org/2025.acl-long.288/) · **阅读范围：正式摘要、作者项目说明；细表待核**。
**Parent→pressure**：SAE/activation feature 的语言解释多从 top-activating input 得到。即使非常准确地预测该 feature 何时触发，也未必描述它**触发之后对输出做了什么**。作者用 steering 检验发现 input-centric 标签对输出作用描述不足，利用刺激特征后上升的 logit tokens、feature unembedding 生成 output-centric 标签；两侧结合效果最好，还找到了此前以为 dead 的 features。**RECONSTRUCTED 来源**：把同一“解释”分成 input causes 和 output consequences，先测不一致，再最小修正解释生成方式。**Xeno 距离**：改善已有人类词语解释；并未研究语义盲结构是否存在人类概念外的关系，但为强对照提供了最低要求。未读全文，不能报告主表数字。

## 19. Koromilas et al. — PolySAE: Modeling Feature Interactions via Polynomial Decoding（ICML 2026 Main）
[PMLR 正式](https://proceedings.mlr.press/v306/koromilas26a.html) · [arXiv v2](https://arxiv.org/abs/2602.01322) · **阅读：主文摘要/方法纲要/作者实验总体，未核全部图表**。
**Parent→pressure**：传统 SAE decoder 的线性加和使“Starbucks”究竟是“star+coffee”组合还是共同出现难区分，模型可能不得不为复合项单独编码 atom。方法：保留线性 encoder，增加 low-rank pairwise/triple polynomial decoder，约 +3% GPT2 参数；四种 LMs、三个 SAE 变体，摘要报告约 +8% probe F1、类似 reconstruction、相对 cooccurrence 统计的交互权重相关 r=.06（SAE feature covariance r=.82），并展示交互 steering。**RECONSTRUCTED**：先发现线性 decoder 的隐含 *additivity assumption*，再通过结构化非线性项区别真正交互与单纯共同出现。**科学边界**：表现和可操纵性不自动证明学到唯一真实组合本体；Xeno 不能把“特征之间有关系”当原创。

## 20. Gröger et al. — Revisiting Platonic: An Aristotelian View（ICML 2026 Main）
[全文 HTML v2](https://arxiv.org/html/2602.14486) · [代码](https://github.com/mlbio-epfl/Aristotelian) · **阅读：§1–7、关键公式与实验/补充统计验证**。
**重大研究动作**：Huh et al. ICML24 的 global similarity 随规模变高，通常被解作不同模态趋于共同世界结构。作者先在理论/合成 null 下问：如果输入完全不相关，CKA 随维度/样本比仍会抬高吗？如果在所有层对上挑最高分，深模型是不是天然占优？用**null-calibrated score + aggregation-aware permutation**修复两种偏差，不是仅仅替换 CKA。用 Huh 协议 **1024 image-text pairs、204 model-pairs，d/n 0.19–8** 复核；校准后 global/spectral convergence 证据大幅减弱，local kNN neighborhood 关系仍显著，但 local metric distance 不必一致。另在合成下证明 type-I 错误控制、power 未严重受损。**RECONSTRUCTED genesis**：大叙事“越来越像”→ 先测方法的 null behavior → 一个具体 confound 足以改变整体科学结论 → 从全局表示趋同重新归因到局部关系一致。**Xeno 约束**：任何称“陌生结构跨模型普遍存在”的结果都必须用等维/抽样与 layer-max calibrated null，不能用一张 CKA 热图。

## 21. Hoang et al. — Feature-Effect Geometry Analysis / Concepts and Functions（2026 arXiv，未确认顶会）
[原文](https://arxiv.org/abs/2607.24645) · [含全文的作者上传稿](https://www.researchgate.net/publication/410887183_Sparse_Autoencoders_Encode_Both_Concepts_and_Functions_The_Downstream_Geometry_of_Feature_Effects) · [官方代码](https://github.com/UKPLab/FEGA) · **阅读：主方法 §3–6、主要表格与 §8 limitation；未复现**。
**真正的动机**：same SAE latent 被赋一个“固定语义”，但 causal intervention 在不同输入上产生不同 logit 效应。定义同一输入的两条 baseline path `phi(D(z))` 和 `phi(D(z-z_j e_j))`，只差 feature j 而**不混入 SAE 重建误差**；跨上下文收集 downstream logit-effect cloud，再用 ray/axis/mixture/low-rank/diffuse 统计检验。作者只用 **Gemma-2-2B、post-layer12、65K SAE、3 decoder variants**，RAVEL attribute/value 与 copying/rule/prompt-local pointer tasks，匹配激活频次的 random ablation 对照。Pointer-like 特征即使有强因果效果，其输出 effect cloud 仍多为 diffuse，而固定方向较少；value-like 具有较多低秩结构。**重要边界**：pointer 分布是作者先指定结构化任务识别的，**不能外推为自然任务的“陌生语义”**；每 feature 最多 64 contexts，许多归类为 insufficient/undefined，分析在终端 logits 上混入后续传播。**RECONSTRUCTED genesis**：发现 feature 是否激活/是否有用不足以解释其作用 → 改为每个 context 的被干预**结果分布** → 用几何的差异区分静态值与条件性操作。**Xeno 新探索不能再只报“不同上下文 effect direction 不一致”——FEGA 已占据。**

## 22. Nava & Wyart — Hierarchical Concept Geometry Emerges from Word Co-occurrence（NeurIPS 2026；预印本 2605.23821）
[原文摘要/形式化概述](https://arxiv.org/abs/2605.23821) · [NeurIPS 官方目录](https://neurips.cc/Downloads/2026) · **阅读：摘要/原文元数据，34 页全文未逐页核**。
**改变前提**：Gemma-2B unembedding 的 word hypernym hierarchies 很容易被讲成模型特有高级概念组织；作者从“WordNet 相近者共现更频繁”出发，分析 cooccurrence Gram matrix 的谱：在正性/衰减条件下， leading eigenvectors 会先分开 broad tree branches 再分 fine branches；word2vec subtree 与 Gemma2B unembedding 出现对应结构。**RECONSTRUCTED**：出现层级几何→问无需复杂模型、纯词分布能否产生→先给出简单统计解释及可计算预测，再核更大的语言模型。**不能凭摘要断言 LLM 内所有层级都是语料伪影**；但它是对“几何很陌生 = 模型原生新语义”的直接反例源。

## 23. 神经科学借用的**实验动作**（不是一条新应用线）
- [Golan, Schütt & Kriegeskorte, Nature Reviews Neuroscience 2026](https://www.nature.com/articles/s41583-026-01070-0)（**综述摘要/图注**）：复杂神经网络在普通自然样本上可以同样解释已有记录，真正区分两个理论需**主动选择其预测分歧最大的自然可行刺激**，结合 OOD 检验；把 Bayesian optimal experimental design 移植到 LLM 内部解释竞争。**RECONSTRUCTED**：若所有模型都能拟合常规数据，再画拟合表无益；让解释承担不同反事实预测才是推进机制科学的方法。
- [Representation Biases: Variance Is Not Always a Good Proxy for Importance, eNeuro 2026](https://www.eneuro.org/content/13/3/ENEURO.0461-25.2026)（**摘要及综述网页**）：高方差/线性易读特征可能被优先编码，重要非线性功能信息却低方差；不能仅用 top PCA / top-activated SAE features 筛候选后宣称穷尽模型计算。
