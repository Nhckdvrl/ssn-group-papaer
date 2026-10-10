# Literature-first research reselection — 2026-10-10

> **性质：研究选择备忘录，不是新主张、论文 V3、实验已运行记录或状态变更。** 当前 workbench 已由人决定停止原 Flan / 仲裁分支；本文没有重新开启任何实验，亦不更动既有原始结果。研究对象必须从科学问题出发，历史资源只能决定实验的边际成本，不能决定问题是否重要。

## 0. 结论（条件性选择，不预支结果）

当前最值得进入**最小可证伪 pilot** 的问题：

**复杂的上下文任务学习是如何在预训练中形成的？较早形成的简单复制/匹配计算，对较晚出现的可迁移任务表示究竟具有因果必要性，还是两者仅受同一训练分布驱动、可以独立形成？**

这是学习过程的路径依赖性问题，而**不是同一个 attention-head 编号是否从早期传到晚期**，也不是“induction head 出现过，因此它是前驱”的相关性论文。

首个实验必须先验证两个性质在本地可用模型上有可测的、因果上有效且相互区分的读数。**若前提不成立，就不进行预训练干预。**

次选但降级：小模型对预训练语料选择的跨尺度预测何时失败，且失败能否由机制测量改善。此问题的原始实用性很高，但 DataDecide、ICLR'26 小模型 proxy 方法和 ICML'26 data-mixing 结果已挤占宽泛新颖性；不应简单重算 rank reversals 写论文。

## 1. 文献谱系 A：简单复制 → 抽象任务表示 → 训练过程中的因果依赖

| 直接原文 | 已经证实的部分 | 尚不能据此宣称 |
|---|---|---|
| Olsson et al., *In-context Learning and Induction Heads* (2022), https://arxiv.org/abs/2209.11895 | 重复/前缀匹配机制与训练阶段的 ICL loss 改进有联系 | few-shot 新任务必然由该机制完成 |
| Todd et al., *Function Vectors in Large Language Models* (ICLR'24), https://arxiv.org/abs/2310.15213 | 可移植的任务向量对部分 few-shot 任务有因果控制作用 | 这些向量的形成必须经过 induction 计算 |
| Singh et al., *What needs to go right for an induction head?* (ICML'24), https://proceedings.mlr.press/v235/singh24c.html | 训练期激活钳制与对 induction 的子电路形成干预可行 | 这些子电路是后续抽象任务机制的必要先决条件 |
| Yin & Steinhardt, *Which Attention Heads Matter for In-Context Learning?* (ICML'25), https://proceedings.mlr.press/v267/yin25e.html | 在 12 个模型中 few-shot 准确率更多受 FV 组件影响；一部分 FV 组件在训练早期曾有 induction 特性。其论文 Table 1 把“induction 为 FV 提供 stepping stone”标为猜想（~） | **观察到同一组件的发育轨迹，不构成发展上的必要性** |
| Minegishi et al., *Beyond Induction Heads: In-Context Meta Learning Induces Multi-Phase Circuit Emergence* (ICML'25), https://proceedings.mlr.press/v267/minegishi25a.html | 对超越精确复制的 ICL，存在多个阶段和不同计算组件 | 自然语料中 IH→FV 的因果先决关系 |
| Aoyama et al., *Predicting the Emergence of Induction Heads in Language Model Pretraining* (ICML'26), https://proceedings.mlr.press/v306/aoyama26a.html | 训练的 batch/context 与数据中的 bigram 统计可预测 IH 形成 | IH 形成已解释更抽象的 ICL 策略发展 |
| Chen, Luo & Pan, *Mechanistic Data Attribution* (ICML'26), https://proceedings.mlr.press/v306/chen26cv.html | 训练数据干预可改变 IH 形成，且 ICL 能力同步变化；这已证明部分 IH↔ICL 因果联系 | 同步变化不能区分“早期 IH 必要”与“数据同时塑造 IH 和后期任务表示”；未单独证明后期 FV 的因果中介 |
| Wang et al., *How Few-Shot Examples Add Up* (ICML'26), https://proceedings.mlr.press/v306/wang26hp.html | FV 来源于多个示例表征的组合，其 QK 路由与 contextualization 可被因果分解 | 不回答 FV 为什么以此形式从预训练出现 |
| Opielka et al., *Causality ≠ Invariance* (ICLR'26), https://proceedings.iclr.cc/paper_files/paper/2026/hash/86b3697c4eb7792c951831636bfdacd5-Abstract-Conference.html | FV 可能对任务/答案格式极不稳定，概念向量与 FV 不是同一概念 | 用一种提示模板测出的 FV 不等于抽象泛化能力 |
| Rohweder et al., *Hierarchical Latent Structures in Data Generation Process Unify Mechanistic Phenomena across Scale* (arXiv v2, Jul'26), https://arxiv.org/html/2603.06592 | 层级数据生成结构可同时催生 IH、FV 和自修复，提供**强竞争解释**：共因而非必要序列 | 共现本身不证明 IH 是 FV 的必经步骤 |
| Wessel, *In-Context Learning Amplifies a Latent Symbolic Circuit* (2026-09 preprint), https://arxiv.org/abs/2609.36265 | 抽象规则的电路可在低 few-shot 准确率时已可观察，并能用向量修补 | 说明推断时的 latent circuit 与训练时形成的因果先决条件不是一回事 |

**真正留下的认知缺口**：Yin 的发展时序，MDA 的数据干预，以及 Rohweder 的共同层级生成因素，构成可区分的三种因果解释。需要训练期**功能性中介剥夺/替代**（而不是坐标级头剥夺）来判定简单机制是必要脚手架、可替代脚手架，还是共因标志。

## 2. 文献谱系 B：数据 → 算法选择 → 泛化；宽泛命题已被强占有

- Kawata et al., *From Shortcut to Induction Head* (NeurIPS'25), https://proceedings.neurips.cc/paper_files/paper/2025/hash/6499b639e8a4b5c9a780d9b88c09722f-Abstract-Conference.html ：理论/合成实验证明数据多样性改变位置捷径与 IH 算法选择、进而改变 OOD 泛化。不能重做 toy shortcut 对比作为新中心。
- Aoyama ICML'26 / MDA ICML'26：已把问题从合成推到自然语言训练统计及训练数据催化，见谱系 A。
- Tigges et al., *Circuit Analyses Consistent Across Training and Scale* (NeurIPS'24), https://proceedings.neurips.cc/paper_files/paper/2024/hash/47c7edadfee365b394b2a3bd416048da-Abstract-Conference.html ：组件更换不等于算法更换。
- Sun, *Circuit Stability Characterizes Language Model Generalization* (ACL Main'25), https://aclanthology.org/2025.acl-long.442/ ：已研究 circuit-equivalence/stability 与泛化的关系。不能把“看电路预测 OOD”当泛化创新。
- *Many Circuits, One Mechanism* (TMLR'26), https://arxiv.org/abs/2606.06267 与 *All Circuits Lead to Rome* (ICML'26)：同一个计算可有不重叠的忠实稀疏电路。不同 head/edge 图不能作为不同算法的证据。

**处置**：自然语料的算法选择依然重要，但我们自己的 E55 发现 DataDecide-1B 在 75/75 模型里有相似的 previous-token→induction 权重组合；这对“数据导致算法类型显著分岔”的先验不利。必须先找到可稳定复现的**功能分岔和不同 OOD 外推预测**，而不是在相同计算上追求不同图。

## 3. 文献谱系 C：小模型预训练数据选择的预测失效（实用但拥挤）

- Magnusson et al., *DataDecide* (ICML'25), https://proceedings.mlr.press/v267/magnusson25a.html ：25 语料×14 尺寸×3 seed；150M 的数据配方排序对 1B 约 80% 正确；8 种 scaling-law 方法未超越直接排序基线。
- Wang et al., *Can Small Training Runs Reliably Guide Data Curation?* (ICLR'26), https://proceedings.iclr.cc/paper_files/paper/2026/hash/c7d04ce5e71efdfc7a4a78f7161238a9-Abstract-Conference.html ：已发现固定超参数下的 proxy 数据排名随轻微超参改变而翻转，且提供降低学习率的低成本修正。**直接占有大量 rank-flip 问题**。
- Shukor et al., *Scaling Laws for Optimal Data Mixtures* (NeurIPS'25), https://papers.nips.cc/paper_files/paper/2025/hash/bc1d640f841f752c689aae20b31198c1-Abstract-Conference.html；Dai & Zheng, *Explaining Data Mixing Scaling Laws* (ICML'26), https://proceedings.mlr.press/v306/dai26l.html：跨规模估计数据混合的经验和理论方法已经形成成熟竞争。
- Hao et al., *BLISS* (ICML'26), https://proceedings.mlr.press/v306/hao26b.html：数据偏好随训练状态变化的多步 influence 学习也已有方法。

**处置**：不建议把 DataDecide 排名反转写作主线。在比较 ICLR'26 的降学习率 proxy baseline 后，若仍存在显著、系统性、可预测的非超参反转，并且一种**机制/任务层读数可以产生比简单 logit/数据统计更高的样本外决策价值**，才允许重开。

## 4. 文献谱系 D：可解释性证据效度（科学重要，但没有现成的独立论文增量）

- Geiger et al., *Causal Abstraction* (JMLR'25), https://www.jmlr.org/papers/v26/23-0058.html。
- Müller et al., *MIB* (ICML'25), https://proceedings.mlr.press/v267/mueller25a.html。
- *Mechanistic Interpretability as Statistical Estimation* (ICML'26)：因果头/边重要性估计在有限样本下易变。
- *Many Circuits, One Mechanism* / *All Circuits Lead to Rome*：解释不唯一。
- *Causality ≠ Invariance* (ICLR'26)：任务向量的因果有效不代表跨格式语义抽象。

**处置**：将可靠性检验当成所有实验的必要基础，而不是没有新突破便写一篇通用“机制分析不可靠”。

## 5. 候选比较（按“科学问题本身”先排，再考虑资产）

| 候选问题 | 为什么有人真正关心 | 与最近邻的具体距离 | 当前最大风险 | 选择 |
|---|---|---|---|---|
| A **后期抽象任务机制是否需要早期简单复制计算作为训练脚手架？** | 区分训练路径依赖 vs 共因，理解复杂能力如何形成及何时可改变训练 | Yin 明确 speculative；MDA 测 IH+ICL 共变；Rohweder 有强共因替代解释；三者尚未直接判别 | FV 信号可能需要更大模型；损伤 IH 会同时损伤一般 LM 训练 | **先做校准 pilot，不启动大训练** |
| B **预训练数据导致的真实计算算法选择能否解释 OOD 泛化差异？** | 解释泛化差异并指导数据构建 | Kawata/MDA/Aoyama/Sun 已大量覆盖，仅“自然文本、更多模型”不足以新颖 | 已有 75/75 模型共享基础组合，没有明确分岔 | BACKUP/PARK，需新的功能分岔证据 |
| C **何时小模型的最佳预训练数据决策不能迁移至大模型？** | 真正的训练成本决策 | DataDecide 和 ICLR'26 数据 proxy rank-flip、ICML'26 混合规律已很近 | 已有强超参修复，机制增量未证实 | 低成本审计才可重开 |
| D **不同运行的电路能否一一对应？** | 分析复用 | Tigges、Bali、Many Circuits、All Circuits、DFA 已覆盖大量问题 | 坐标/结构等价问题；E75 任务映射用了目标 DLA | 不作新主线 |
| E **某个模板/数据切片改变上下文采信？** | 个别提示格式敏感性 | Goyal、Wang、Kim、Task Matters 已近；先前 E80 失败 | 泛化/意义不足 | 人已决定停止，**不重启** |

## 6. A 的优先 pilot：先证明真正可测，后谈因果

**研究对象不是 head 的编号**。定义三个行为/因果量：
1. **简单复制能力**：重复/前缀匹配情景下，允许模型复制上一同型上下文后继 token 的改善；并有冻结模型的功能性消融验证。
2. **抽象 few-shot 任务执行**：任务映射必须用新 query 的正确答案、且目标答案不能从 demonstrations 原样复制；评价实际 held-out 准确率、跨表面格式的鲁棒性，而不以 token-loss difference 替代。
3. **可迁移任务中介**：从任务 demonstrations 计算/抽出的隐状态，在新的 query 上注入后应带来任务特异的因果改进；与随机任务、shuffled demonstrations、匹配激活规模和直接复制 baselines 对照。因为 ICLR'26 表明 FV 格式不完全不变，至少报告固定格式和跨格式两种效度，不把任意 FV 等同于“抽象概念”。

**Gate 0 — 测量可行性（冻结的公共模型，不训练）**：
- 优先 Pythia 410M/1B，结合现有训练轨迹；另一模型家族优先 DataDecide 300M/1B 作为后验复制（需兼容架构）。
- 复用 Yin 官方开源几类原始 ICL tasks 和 causal intervention，先检验晚期任务中介真正影响新 query 的正确率，再确认与 copy test 的因果效应可以区分。
- 对已有 E55/E35 的 early induction 数据作校验，但不以同层同头出现判定发育关系。测同一训练轨迹的时间先后、**功能因果**关系。
- 预先固定：task 与 held-out 模板、最小有意义的中介效应（应显著超过随机/零样本/直接复制；初拟 5 个百分点以上，需依据基准方差调整）、不少于 3 个独立任务组的重复。
- **若只有 copy 信号而没有可信的抽象任务中介，Gate 0 FAIL。不得转成“另一个 induction head 时间线”**。

**Gate 1 — 区分 3 个解释，不允许只做相关追踪**：

H1. *必要脚手架*：暂时在训练早期阻断简单复制的功能形成/使用，释放后且训练数据和预算相同，晚期抽象 few-shot 中介仍显著滞后；仅在晚期阻断或者匹配损失的随机干预不产生相同的特异后果；恢复该早期功能可救回晚期中介。

H2. *共同数据驱动*：相同层级结构或重复统计在两个机制上都有效，但功能性早期阻断一旦恢复、优化预算配平，晚期抽象中介可正常形成；二者时间先后不代表必要性。

H3. *可替代脚手架/路径依赖*：部分模型/训练配方依赖早期复制，但另一些可经不同功能路径形成同一类抽象中介；需要区分具体任务/数据 regime，而不是夸大为全局必要。

**两个正交干预**（Gate 0 过后才允许，必要时先少量试运行）：
- 训练数据层：修改早期可学习的重复/匹配统计（保持长度、token unigram、数据量、优化超参），然后**在后续共享同一份自然语言训练数据**；检查训练初期对复制的操纵是否成功。
- 训练计算层：参考 Singh ICML'24 的训练期 activation clamping，早期暂时阻断功能性复制路径，而不是永久删 head 或固定头编号。需要和同训练阶段的随机/层匹配干预、匹配训练损失/扰动强度的控制、晚期同等干预比较；释放后继续相同 tokens。允许备用组件形成：若替代功能恢复，不能错误认定“原头已被删除”=“复制已被抑制”。
- 训练预算、学习率轨迹、复制条件与抽象任务的最终评价全部按模型 pair 配对，多 seed、held-out tasks；确保单一干预的语言建模损伤不解释所有变化。

**首轮决策**：先只验证 Gate 0；若抽象任务因果中介可靠，再写严格的受控实验卡并做极小设置的操纵检查；若正负控制无法把 IH 特异效应和一般训练损伤分离，标 **INCONCLUSIVE** 并停止规模化，不把失效也包装成论文。

**投稿最低形态**：一个清楚的训练路径因果问题；功能层因果测量而非 head index；明确竞争的共因解释；至少两种独立任务类别 + 多 seed/第二设置验证；真实下游 few-shot/OOD 后果；保留强 baseline。若只是“删 IH 后 ICL 下降”，属于 MDA 已覆盖，**不够新**。

## 7. 资产与边界

可直接复用：Pythia/DataDecide public checkpoints；E01/E02 induction score 与复现排雷；E35/E42 角色与因果测量（仅作工具/背景）；E46 的小模型训练脚本、扰动/branching infrastructure；E55 K-composition 检验；已有公共 Yin 官方代码。**E46 自训 S 模型是否具备可测的抽象任务机制未知，不得假设。**

不得复用为新论文结论：head coordinate inheritance C05；E75 的基于目标 DLA 的所谓 transfer；E24 的语料家族混杂相关；E77/E80 的失效 γ / Flan 单点。旧论文 V0/V1/V2 作为历史，不能靠替换 Introduction 复活。

与另一 workbench（in-context-evidence-structure）的界限：该 workbench研究提示中的当下信息更新/部署与信息结构；本选择只研究**预训练过程中的能力形成与因果依赖**，不重复问短期提示的冲突策略。

## 8. 开始和停止条件

- 本文**没有**修改 README、CLAIMS、实验状态、其他实验卡、脚本或结果，未创建主动训练任务。只有科学负责人可批准将候选 A 转成正式 active 研究线。
- 论文新颖性复核优先核查 Yin/MDA/Rohweder/Opielka/Minegishi 等原文的方法与实验边界。引用已经核对官方论文主页及 Rohweder arXiv HTML 全文；不是声称每篇都逐页读完。
- 不以文献中的一句 future work 单独充当 novelty。所选问题须以三个竞争解释、行为效度和正交训练干预同时成立为前提。
- 没有通过 Gate 0 → 不跑训练、不开 V3、不开更多同义指标。找新 territory 时回到新的 primary-paper genealogy，而不是捡起 Flan/头身份继续修补。
