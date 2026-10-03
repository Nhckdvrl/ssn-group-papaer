# A02 — 对标同题材顶会论文：差距分析、叙事重包装、补充实验清单（2026-10-03）

人的指示（2026-10-03）：校对免了；按同题材成熟顶会论文的标准补工作量、补实验；叙事要按好论文的方式包装，对齐顶会尺度。
本文件只做规划。每个补充实验另有实验卡（R3），先写卡再跑。

## 1. 对标论文：它们靠什么撑起一篇顶会
| 论文（会议） | 核心命题的包装 | 撑起命题的实验配置 |
|---|---|---|
| Frankle et al., *Linear Mode Connectivity and the LTH*（ICML 2020） | 提出一个分析工具（instability analysis），得到一句可记的结论：网络在训练早期就对 SGD 噪声稳定 | 在训练第 k 步分叉、换噪声，看终点是否落在同一区域；k 扫描；多架构 / 多数据集 |
| Summers & Dinneen, *Nondeterminism and Instability*（ICML 2021） | 反直觉：一切随机源效果相同，改 1 bit 就够 | 逐一隔离随机源的协议（初始化、顺序、增强、cuDNN）；扰动幅度剂量；多种多样性度量 |
| Achille et al., *Critical Learning Periods*（ICLR 2019） | 借神经科学概念：深网也有“关键期” | 在不同时间窗施加缺陷，测恢复情况；时间窗扫描 |
| Bali et al., *Attention-Head Stability*（ICML 2026，最近邻） | 电路的跨实例稳定性是被忽视的前提 | 26 种架构 × 每种 50 次（小模型）/ 5 次（GPT-2 small）重训；层内最佳匹配相似度；残差 CKA；消融重要性；AdamW 操纵 |
| Gurnee et al., *Universal Neurons*（TMLR 2024） | 只有 1–5% 的神经元跨 seed 通用，且通用的可解释 | 5 个 GPT-2 seed，1 亿 token 上的逐对神经元相关；神经元家族分类；因果干预 |
| van der Wal et al., *PolyPythias*（ICLR 2025） | 资源 + “训练动态高度一致、离群 seed 可预测” | 5 个尺寸 × 10 个 seed（14M–410M）；下游任务、语言学探针、训练阶段（HMM）；**另设只换数据顺序 / 只换初始化的 160M 变体** |
| Tigges et al., *Circuit Analyses Consistent Across Training and Scale*（NeurIPS 2024） | 电路分析在训练和尺度上可迁移：成分会换，算法不变 | 70M–2.8B 的 Pythia、300B token 的 checkpoint；4 个任务；路径修补 + 成分功能验证 |
| Chan et al., *Data Distributional Properties Drive ICL*（NeurIPS 2022） | 数据的某个分布性质决定涌现的机制 | 受控训练：系统地操纵数据性质（突发性、Zipf），给出剂量关系 |
| Kim et al.（ACL 2026）；Goyal et al.（ICLR 2025 Oral） | 训练数据决定参数知识与上下文知识的仲裁 | 受控合成语料 / 受控微调数据过滤；多模型家族、多冲突数据集；简单理论模型 |
| Juneja et al.（ICLR 2023） | 损失面几何揭示不同的泛化策略 | 大量微调 seed；线性插值的势垒；聚类与行为诊断集对应 |

**共同标准（我们要达到的）：**
1. 一句反直觉、可记的命题，最好配一个可复用的分析框架；
2. 跨尺寸（≥ 4–5 个）且跨家族（≥ 2 个）；
3. 受控干预：自己训练或分叉，而不只靠相关；
4. 用因果手段（消融 / 修补）验证测量对象；
5. 对置换 / 旋转对称性的控制，即区分“同一功能存在”与“同一位置”；
6. 机制解释（为什么），以及边界条件（什么时候不成立）；
7. 对实践的直接后果（可解释性结论能否迁移、评测怎么做、训练怎么做）。

## 2. 我们现在的差距
| 标准 | 现状 | 差距 → 补充实验 |
|---|---|---|
| 命题包装 | “初始化决定由谁来做、数据决定做多少”：朴素，像观察记录 | 重包装成**双重分离**（§3） |
| 尺寸 | 1B + 300M 子集，只有 2 个点 | **E45**：DataDecide 全部尺寸（已查实 4M–750M 大多共用初始化） |
| 家族 | 只有 DataDecide（OLMo-v1 架构） | **E44**：Pythia（标准版与去重版共用 step0：70M / 160M / 410M）+ PolyPythias seed |
| 初始化与数据顺序的混杂 | DataDecide 的 seed 同时决定两者；只能间接排查 | **E44(b)**：PolyPythias 160M 的 data-seed 变体（同初始化、换顺序）与 weight-seed 变体（换初始化、同顺序） |
| 测量的因果有效性 | 只有注意力分数图 | **E42**：逐头消融的因果图 + 头级干预在模型间的迁移 |
| 对称性控制 | 只有按索引对齐的 Spearman | **E43**：按索引对齐 vs 置换 / 旋转不变（最佳匹配、CKA）；神经元、残差维度、权重插值 |
| 初始化的数量 | 1B 只有 3 个初始化 | **E46**：受控训练，多初始化 × 多语料；**E45**：1B 另有 small-aux 两个初始化（待核实） |
| 受控干预 / 关键期 | 锁定时间只有相关证据（E37 / E40） | **E46**：Frankle 式分叉 + 扰动时刻扫描（关键期）、Summers 式扰动幅度剂量（吸引域半径）、数据边界条件 |
| C04 的因果数据干预 | 两个天然实验（DataDecide 有 / 无 Flan；OLMo 2 中期训练） | **E47**：改写 Flan 模板的继续预训练（线索替换），预测触发词随之迁移 |
| C04 的数据集数量 | 2 个（ParaConflict、PopQA） | **E48**：NQ-Swap（Longpre 2021）上的线索对比 |
| C04 的机制 | E28 阴性、E33 不可判定 | **E49**：开关的逐头归因图，并检验它是否由初始化决定（把先天和后天连成一个对象） |
| 行为层的先天 / 后天 | 12 个知识冲突条件 | **E50**（不用 GPU）：DataDecide 公开的下游评测做方差分解；语料统计 → 机制强度（Chan 2022 的自然规模版）；双向 bootstrap 和稳健性；统计功效 |

## 3. 叙事重包装（论文草稿用英文）
**Working title:** *Seeds Decide Where, Data Decides What: A Double Dissociation in How Language Models Form Mechanisms*

**Hook（一句话）：** 把整个预训练语料换掉，一个 induction 头也不会挪位置；但加入 1% 的指令数据，就会改写模型什么时候相信上下文。

**Abstract draft（标 [P] 的为待补实验，结论未定）：**
> Mechanistic interpretability implicitly treats a model's circuits as products of its training data. We test this with a factorial design hidden in public pretraining suites: runs that share the same random initialization across many corpora (DataDecide: 3 seeds × 25 corpora at up to 14 sizes [P: E45]; Pythia/PolyPythias as a second family [P: E44]). Crossing initialization with data reveals a double dissociation. *Where* a mechanism lives — which heads become induction, previous-token and retrieval heads [and which neurons and residual directions carry which features, P: E43] — is set by the random initialization: models trained on entirely different, even source-disjoint corpora from one seed place their circuits in the same components, whereas models trained on identical data from different seeds do not, and the data component of placement is statistically zero. *What* the mechanisms do — their strength and the behaviours they support — is set by data and not by initialization: initialization has no main effect on behaviour, while a 1–2% slice of instruction data installs a context-reliance switch keyed to the literal template "Question:", which appears within the first 4% of pretraining and reappears when FLAN is added in OLMo 2 mid-training [P: E47 moves the trigger by rewriting the template]. Placement is fixed early, in the first 2–4% of training, by collective symmetry breaking that no single head's initial weights or gradients predict [P: E46 critical period and basin radius under controlled perturbations]. The dissociation has a practical corollary [P: E42/E43]: head-level circuit findings transfer between same-seed models trained on different data, but not between different-seed models trained on the same data. The seed, not the dataset, is the unit over which component-level mechanistic claims generalize.

**贡献（按论文写法）：**
1. **设计 / 资源：** 发现并验证公开套件中隐藏的“初始化 × 数据”析因结构（step0 权重哈希核实），并给出用于机制性质的无偏方差分量框架。
2. **发现一（先天，where）：** 成分的位置由初始化决定，数据分量为 0；跨尺寸、跨家族成立；按索引对齐的相似度与置换不变的相似度形成交叉分离 [P]。
3. **发现二（后天，what）：** 成分强度和行为由数据决定、不受初始化影响；1–2% 的数据装入一个由字面线索触发的开关，并有因果的线索替换干预 [P]。
4. **发现三（如何、何时）：** 位置在关键期内通过集体对称性破缺锁定；受控实验给出关键期和吸引域半径，并说明数据在什么条件下才能挪动位置 [P]。
5. **后果：** 成分级的可解释性结论按 seed 迁移，不按数据迁移；做数据归因或模型 diff 应当固定 seed；问答格式的知识冲突评测测到的部分是这个开关。

**主图规划：**
- Fig 1：析因设计示意，加核心结果（所有尺寸上 SI vs SD vs DD）。
- Fig 2：**双重分离矩阵**：行是性质（位置 / 强度 / 行为 / 开关），列是初始化分量与数据分量，含 CI。
- Fig 3：交叉分离：按索引对齐的相似度中 SI ≫ SD；置换 / 旋转不变的相似度中 SD ≥ SI [P: E43]。
- Fig 4：尺寸曲线与家族复现 [P: E44 / E45]。
- Fig 5：关键期与吸引域（受控训练）[P: E46]。
- Fig 6：开关：因子分解、线索拆解、发育、OLMo 2、线索替换干预 [P: E47]。
- Fig 7：迁移：头级干预与探针在 SI / SD 之间的迁移 [P: E42 / E43]；开关的归因图由初始化决定 [P: E49]。

## 4. 执行顺序（按信息量与依赖）
1. E44（Pythia 天然实验）、E45（尺寸曲线）：都是纯推理，复用 E35 的测量。
2. E42（因果图与迁移）、E43（表示基 / 神经元 / CKA / 插值）：1B 子集，推理。
3. E46（受控训练）：先做 pilot，确认小模型能在预算内形成 induction 头。
4. E47（线索替换继续预训练）：先做 pilot，确认开关在多少 token 内出现。
5. E48 / E49：推理。
6. E50：不用 GPU，GPU 跑的时候并行做。

## 5. 不做的事
- 不为凑尺度加无关任务；每个补充实验都要对应 §2 的一个差距。
- 不在看到结果后改读数；所有阴性结果都写进账本。
- 包装只改表述，不改数字；[P] 项在实验完成前不写进摘要定稿。

## 6. 叙事更新（2026-10-03 12:00，边做边想；随证据修订）
- **“初始化选规范，数据定功能”（理论化的表述，论文 §2 用）：** 同层内的头可交换（置换对称），“哪个编号的头做 induction”是规范（gauge）选择，本身对行为无影响。双重分离因此有一个干净的解释：初始化只决定规范，数据决定所有规范不变的量（角色是否存在、强度、行为）。经验上非平凡的是两点：(i) 规范选择对巨大的数据变化稳健——对称性破缺本可以由早期数据驱动，但实际上不是（E35 / E44 / E46）；(ii) 规范不变的量上初始化**没有主效应**（E36 / E51），也就是不存在“好 seed”。
- **“不存在跨数据的幸运 seed”（次要卖点，传播性强）：** E51 显示 seed 的好坏完全是与数据的交互；对 Picard 2021（“torch.manual_seed(3407) is all you need”）一类的说法给出 LM 预训练规模的反证；实践含义是配方比较中共用 seed 不降低噪声。
- **层级结构：** “在哪一层”近似普适（跨初始化、跨数据），“层内哪个头”由初始化决定（E35 / E44 层内拆分）。与 Bali 2026（最佳匹配集中在同深度层）一致，并给出原因。
- **同初始化 ≠ 同一盆地：** 同初始化、异数据的 1B 模型线性插值势垒很大（E43 首对 7.5 nats）→ 初始化保留下来的是对称性选择，不是权重的接近；这把我们的结果与 LMC / model merging 文献（Frankle 2020、Ainsworth 2023、Juneja 2023）区分开。
- **训练起点审计作为方法学贡献：** P09（PolyPythias weight-seed 实际从标准初始化训练）说明，用公开套件做“初始化”研究必须核对训练早期的 checkpoint；我们对 DataDecide 做了这一核对（通过）。
- **候选的应用实验（看 E43 再定）：** 若残差流按索引对齐（SI ≫ SD），则检验可解释性工件（SAE、线性探针）能否在同 seed、不同数据的模型之间直接迁移（E52 候选）。
