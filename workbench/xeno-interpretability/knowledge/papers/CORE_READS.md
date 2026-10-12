# 关键论文连续精读：从“能命名”到“解释计算作用”

**2026-10-12。** 7 篇有内容的研究卡合并在一处，避免每篇生成重复文件。**“起源重建”一律 RECONSTRUCTED**：是我们从原文论证反推研究设计的合理路径，不是作者关于历史灵感来源的证言。下列带数值的判断均来自原文对应章节/图表，未独立复现。

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
