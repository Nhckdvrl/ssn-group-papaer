# 度量、干预与“可迁移性”：审计合同

**目的：不是堆控制变量，而是确保实验读数真的对应提出的问题。** 所有新实验应先写清估计对象、干预目标和比较基线，再选择计算公式。

## 1. 不要把“角色图”当“因果电路”

- **Attention role**：某个特征位置上的注意力权重统计，如 END→IO、induction pattern、previous token。注意模式可高、OV写出却无关，也可以承担中间信息传递而对最终logit直接贡献近零。
- **OV / copying score**：权重投影对特定 token 拷贝的潜力，不等于在自然前向中实际使用。
- **DLA**：某个头写到当前 residual 后、经恰当 normalization 线性化的直接输出 logit margin 贡献；正负作用可以抵消；不包含对后续路径的间接贡献。
- **Single-head mean ablation**：把某 head 输出在指定位置替成参考均值后的总输出变化。效应受其他组件修复/协作影响，不可简单解释成 DLA。
- **Joint ablation**：同时消融集合实际重新 forward；交互项决定它是否等于单头作用之和。
- **Circuit**：应说明节点与路径、输入条件、patching定义、对哪个功能量忠实。选 head 集合不是完整 circuit 的同义词。

## 2. 关键实施级不一致：E81 → v3 Table lineage

来源：[scripts/e81_analyze.py](https://github.com/Nhckdvrl/ssn-group-papaer/blob/d581ed4b9636319da8e8467930f716ab651f38c4/workbench/mechanism-population-dynamics/heads/scripts/e81_analyze.py)、[scripts/figs_v3.py](https://github.com/Nhckdvrl/ssn-group-papaer/blob/d581ed4b9636319da8e8467930f716ab651f38c4/workbench/mechanism-population-dynamics/heads/scripts/figs_v3.py)、[v3 main.tex](../../heads/1-original/papers/paper-acl-v3/main.tex)。

代码定义：

- 令 target 每个头单头消融的下降为 \(a_t(h)\)。
- 令 \(T_s^a\) 为 **source 单头消融值最大**的3个头。
- 代码的 transfer 是 \(R_\mathrm{add}=\sum_{h\in T_s^a}a_t(h)\ /\ \sum_{h\in T_t^a}a_t(h)\)。

而 v3 在文字里把 carrier 定义为 **DLA top-3**，transfer 说成其**联合**消融效果。Table lineage 的同一行又用 DLA top3 overlap、DLA 主力头，并把 additive transfer 塞进“transfer”列，部分值大于1时截断到1。

**这是真实的实验-论文指标合同不一致，而不是仅仅“不够严格”。**

修复路线（只允许作为未来明确授权的代码审计任务，当前不重跑）：
1. 明确目标到底是 DLA top3 还是 ablation top3，并在所有表列中一致。
2. 另存并分别报告 \(R_\mathrm{add}\) 与 \(R_\mathrm{joint}\)。联合效应需要真实 forward，不能由单头相加冒充。
3. 比值伴随报告 source/target 各自绝对 margin 下降和 baseline margin；大于1不能不解释就裁掉。
4. 对同一个固定 head 集合，用训练链与 siblings 两类比较，不允许中途改变定义。
5. 将原 v3 表标记为“混合指标、未修复”，不能直接引用作为当前稳定证据。

## 3. 排名相关、数值相关和信度不是一回事

现有层内相关通常对每层头分数取 Spearman，再跨层平均。大量近零的 DLA 头被强制排次，会产生很低的 rank reliability：E81 的 DLA Spearman–Brown约0.40，value Pearson约0.98。

正确选择：
- 关心头的整体顺序 → 保留层内 Spearman，解释近零排序导致的信度问题。
- 关心主要作用 → 在独立校准数据选 active heads，留出数据报告数值效应/秩，避免挑选样本自证。
- 关心集合功能 → 实际联合消融、干预随机对照、按任务和条件分层。
- 关心同类多头复用 → 同时观察单头、组、路径及上游/下游响应。

Spearman–Brown 公式 \(R_\mathrm{SB}=2r/(1+r)\) 假设拆半同类误差；跨模型相关的可靠性修正 \(r_{AB}/\sqrt{R_AR_B}\) 依赖其可用假设，不能把修正值当机制因果真值。

**一项重要的额外注意**：输入之间的真实因果效应异质性，不应全部归为“测量噪声”；在不同 token、position、反事实条件分解可能揭示真实变化。参考 [Méloux 2026](https://proceedings.mlr.press/v306/meloux26a.html)。

## 4. 三种“迁移”，分别报告

1. **Index transfer**：source 的同层同编号集合移到 target，其效果如何？适用共享祖先的比较，但索引本身无跨 seed 天然解释。
2. **Unsupervised role alignment**：仅用不包含目标待预测任务因果信息的统计角色建立对应，再在 target 留出任务验证。这可测潜在跨任务可预测性，但 E72 已研究通用角色留出。
3. **Target-aided causal relocation**：允许使用 target 的任务侧 DLA/消融挑选映射，在另一部分 target 数据验证。合法而有用，但不是 source-only transfer；必须与同目标校准预算、但不使用 source 的定位比。

源信息确有价值的近似必要条件：source-assisted 相对 target-only 的额外样本外预测/因果干预收益，超过随机、深度启发式、角色同类匹配等已强基线。

## 5. 数据切分、统计单位与归因

- 如果同一 target DLA 在拟合与留出提示上都有效，说明 target定位泛化，不能自动归功于 source知识。
- 语料配方的 3 个 seed 与配方对构成共享依赖；300 对不是300个独立配方。按初始化、recipe、训练分支进行层级bootstrap/置换，明确估计总体。
- DataDecide中 seed 标签有错误，实际用于分析的1B已验证集合是69个。Pythia weight-seed 和 2.8B-dedup异常也要剔除。
- 对序列指标含罕见 token 重尾，不要只看均值；报告中位数、分位和分层自然性。
- 对训练期规律，不得把早期观察的后验轨迹改写成前瞻验证；E83是很好的警示。

## 6. 小实验的“最低可解释性合同”

每次实验卡要求至少写：

**对象**（何模型、什么真实功能）、**操作**（动哪些张量、哪些位置）、**结果**（哪个 logit/behavior 量）、**正对照**（确认 hook 生效）、**阴性对照**（同信息预算的替代）、**竞争解释**、**哪一个观察会改变判断**、**post-hoc追加登记**。

优先在一条局部路径上满足合同，再扩展到多 GPU。不要先开80个run来换取一个可能永远解释不清的平均相关。

参见[失败手册](FAILURE_MODES.md)与[研究总档](../../heads/HISTORY.md)。
