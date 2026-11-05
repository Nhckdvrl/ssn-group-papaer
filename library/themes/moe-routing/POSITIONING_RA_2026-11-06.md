# R-A 定位表（2026-11-06；主旨改为方法学后按 AGENTS.md R6 重扫）

**只写定位，不写判决（R6）。** 主旨来源：`division/DIRECTION_2026-11-06.md` §10–§11。证据标签：`[全文]` 读了全文，`[节]` 只读相关节，`[摘要]` 只读摘要，"未核对"= 没拿到原文或只凭记忆。PDF 都在会话 scratchpad，没有进仓库。

**检索用的主旨句（英文）：** "Across independently trained mixture-of-experts language models with identical configuration, reproducibility of expert specialization decreases with readout granularity relative to an exact-rerun ceiling; coarse agreement is inherited from representation geometry and frozen random routers, and published single-checkpoint expert analyses generalize only to the class level and must report an untrained floor."

**检索范围：**
- venue corpus：`query.py nearest` 跑了 5 句（主旨句；seed 稳健性；随机 / 冻结 / hash 路由；MoE 专家分析；未训练基线），每句取前 12–20 条已接收论文和 6–10 条被拒论文。
- arXiv API：19 组查询，限 2025-09-01 以后，人工筛掉应用类论文；另按 ID 取了 19 篇的摘要。
- 本轮新读：Hash Layers §5、Clark 2022 §5.3 与附录 B.4、SMoE-Dropout §4、Self-Routing §3–4.1，都是 `[节]`。
- 其余条目沿用 `MOE_EXPERT_ANALYSIS_HISTORY_2026-11-05.md` 和 `READOUT_CATALOGUE_…` §4 的阅读。
- 没覆盖到：OpenReview 上没挂 arXiv 的投稿、非英文文献。

## (a) 分析结论的 seed 稳健性（稠密模型与可解释性）

| 近邻 | 他们有什么 | 我们的增量 | 压缩风险 | 他们已 own、我们不能写的话 |
|---|---|---|---|---|
| MultiBERTs 2106.16163（ICLR'22）`[摘要]` | 25 个 BERT seed；"conclusions … apply to the artifact … not always clear whether they hold for the more general procedure"；Multi-Bootstrap | 对象换成 MoE 分工；重跑上限与未训练地板；按级别回答哪一级可推广 | **高**（框架层面） | "单 checkpoint 的结论未必推广到训练程序，应报多个 seed" |
| Gurnee 等 2401.12181 Universal Neurons `[摘要]` | GPT-2 换 5 个 seed，只有 1–5% 的神经元是 universal | MoE 的单元是专家：配对后专家级只到重跑的约一半；同一套 run 上把模型级、类别级、专家级放在一起比 | **中–高** | "个体单元大多不跨 seed 重现"作为一般现象 |
| Paulo & Belrose 2501.16615（ICLR'26）`[摘要]` | 同数据同模型训 SAE，换 seed 只有 30% 的特征共享 | 被测的是模型自身的分工，不是分析工具；有重跑上限 | 中 | "分解是有用的切法，不是唯一的真实单元" |
| 2509.22831 机制可解释性的可推广性理论 `[摘要]` | Pythia 各 seed 的 1-back 头：发育轨迹一致，位置一致性有限 | 换成 MoE 路由；三级量化；带地板与上限 | 中 | "发育 / 功能层面一致而位置 / 身份层面不一致"这个模式 |
| Fehlauer 等 2509.26643（EMNLP'25）`[摘要]` | 跨 seed 的逐 token KL 呈四阶段；功能词、高频词收敛更快 | 测的是路由划分而不是输出分布；粒度梯度与时间锁定 | 低–中 | "功能词跨 seed 更稳"（输出层面） |
| PolyPythias 2503.09543（ICLR'25）`[摘要]` | 50 个 run，训练动态跨 seed "highly consistent" | MoE；分工级读数 | 低–中 | "稠密 LM 的训练阶段跨 seed 一致" |
| McCoy 等 1911.02969 `[摘要]` | 100 个 BERT 微调：域内准确率一致，HANS 泛化相差到 0–66% | 预训练的内部分工，不是行为 | 低 | — |
| Li 等 1511.07543 Convergent Learning `[摘要]` | 子空间跨网络共享，具体的基不共享 | 语言 MoE；离散的划分；有地板 | 中 | "子空间重现、基不重现" |
| Heap 等 2501.17727（ICLR'26）`[摘要]` | SAE 的自动可解释性分数分不开训练过的模型与随机初始化模型；"argue for routine randomized baselines" | 换成 MoE 专家分析读数；逐条给出 step 0 下是否同样成立（11 条里 4 条一样） | **高**（只针对"要报地板"这一句） | "常用解释性指标须并报随机初始化基线" |
| Dead Salmons（ICLR'26 撤稿）`[摘要]` | 解释性发现应对随机计算的零分布做检验 | 同上，给出 MoE 上的具体数 | 中 | 同上的方法论主张 |

## (b) MoE 跨 run 比较

| 近邻 | 他们有什么 | 我们的增量 | 压缩风险 | 他们已 own、我们不能写的话 |
|---|---|---|---|---|
| Equifinality 2604.14419 `[节]` | 76M，WikiText；2 个 seed 的专家词表投影 best-match Jaccard .13–.15，高于随机 .0003，权重余弦等于随机；PPL 不随路由拓扑变 | 未训练地板、精确重跑、三种配对；粒度梯度；时间；标准线性路由 + 单遍语料 | 中 | "跨 seed 专家功能高于随机地重叠、权重不同" |
| 视觉 MoE 2605.20610 `[节]` | 10 个 seed × 专家数 4 / 8 / 16，二阶 RSA；"有生 / 无生"粗划分跨 seed 与跨专家数都稳定 | 语言；重跑上限与地板；粒度梯度；时间锁定；冻结路由对照 | **高**（"粗划分跨 seed 稳"一句） | "专家的粗划分跨独立训练重现" |
| 2608.15102 双语 MoE `[摘要]` | 2 个 seed，专精集中在哪种语言随 seed 变 | 9 个 run，按级别分 | 低–中 | — |
| LMC-MoE 2509.11348（NeurIPS'25 Oral）`[节]` | 独立训练的 MoE 经专家置换对齐后在同一低损失盆地 | 置换对齐后专家**职责**只部分一致（专家级 q ≤ .55） | 中 | "独立训练的 MoE 在置换意义下等价（损失层面）" |
| Myth of Expert Specialization 2604.09780 `[节]` | 命题 1：隐状态相似 ⇒ 路由相似；单模型 | 跨 run 分解：几何零假设 N1 解释了词类级一致的约 80% | **中–高**（几何一句） | "路由由表示几何决定"作为单模型机制 |
| Routers Learn Geometry 2605.12476 `[节]` | 1B：路由器与专家耦合；K-Means 质心路由只差 2.6% PPL | 跨 run；耦合与可重现度分开测 | 中 | "路由器学的是几何"；"质心路由近乎不掉 PPL" |
| Geometric Routing 2604.14434 `[全文]` | 单 checkpoint；句法分组在所有层优于频率分组；置换零假设 | 跨 seed 版本，加未训练地板 | 低 | "路由按句法类组织"（单模型） |
| Standing Committee 2601.03425（ACL'26）`[摘要]` | 单模型：跨领域不变的一小组专家承担大部分路由 | 跨 run；我们的 E176 也是"领域专精弱、类别结构强" | 低 | "领域专精远不如通常认为的普遍" |
| OLMoE §5.1 / OpenMoE §4.2 `[节]` | 单轨迹的路由饱和：早期即定 | 跨 run 的锁定；E176 9/9 复现饱和曲线形状 | 低 | "路由在训练早期饱和" |

## (c) 随机 / 冻结 / hash 路由与学习路由等效（FRZ 结果的 claim ownership）

| 近邻 | 规模与设定 | 他们有什么 | 我们的增量 | 压缩风险 | 不能写的话 |
|---|---|---|---|---|---|
| Hash Layers 2106.04426（NeurIPS'21）`[节 §5]` | 751M / 1.28B（Reddit，单层 64–128 专家）；4.5B 对 BASE（RoBERTa+cc100en，4 万步） | 按 token 的 hash 路由优于 Switch 0.4–0.5 PPL；固定随机分配 23.22 ≈ 平衡 hash 23.16；聚类 hash 更差 | 冻结的是**隐状态上的随机线性路由器**，不是 token hash；测跨 seed 一致度 | **高** | "不学路由也不输" |
| THOR 2110.04260 `[摘要]` | 机器翻译 | "gating mechanisms do not work better than randomly routing inputs to experts" | 同上 | 高 | 同上 |
| SMoE-Dropout 2303.01610（ICLR'23）`[节 §4]` | Transformer-XL enwik8、BERT | **随机初始化后冻结的路由器**（与我们的 FRZ 同构）；专家 ≥ 16 时优于学习路由 | 测的是分工的可重现度，不是性能 | **高** | "随机冻结路由器性能不输" |
| Self-Routing 2604.00421 `[节]` | GPT-2 small，8 专家 top-2；另有 LLaMA 135M / 360M | 冻结随机投影 WikiText 27.0 vs 学习 26.7；每步重抽的随机路由明显更差（34.6） | 同上 | 高 | "路由信号已在隐状态里，不需要学的投影" |
| Equifinality 2604.14419 `[节]` | 76M | 冻结随机质心只差 +1.6%，hash +4.6%，都是单 seed | 多 seed；跨 seed 一致度 | 高 | 同上 |
| Routing absorption 2603.02227 `[摘要]` | 稀疏注意力门控，31M；Qwen3-1.7B | 冻结随机门控与学习门控只差 1.1 PPL；可训练层越多差距越小；"co-adaptation in MoE" | 是 MoE 专家路由本身，且测分工 | 中 | "表示会吸收任意强加的路由" |
| Grouter 2603.06626 / StableMoE 2204.08396 `[摘要]` | 预训练 | 固定的蒸馏路由器收敛更快、更好 | — | 中 | "固定路由可以不差甚至更好" |
| **反证：** Clark 等 2202.01169 `[节 §5.3]` | 最多 2000 亿参数 | S-BASE 在所有规模都优于 RL-R 和 HASH；HASH 的初始开销大，专家多时更不均衡 | — | — | 不能写"任何规模下都不输" |
| **反证：** Chen 等 2208.02813 `[摘要]` | 理论，簇结构合成任务 | 路由器学到簇中心，MoE 才成功 | — | — | — |

**"冻结路由器 CE 不输"已知到什么规模：** 按 token 的 hash 到 4.5B 参数（4 万步，只比 BASE 一种），作者 Roller 等。随机冻结的线性路由器到 GPT-2 small 规模（Self-Routing）以及 Transformer-XL / BERT（SMoE-Dropout）。注意力门控的类似现象到 1.7B。在 Clark 2022 的大规模比较里，学到的路由（S-BASE）始终优于 hash。所以我们 E173 的 FRZ 损失结果是**在本规模上复现了一个已知现象**，不能当作发现写。

## 未训练模型上的"专精"：有无先例（任务 3）

一般原则早已有人提出："解释性指标在随机初始化模型上也会给出像样的数，须并报随机基线"。见 Heap 等 2025（ICLR'26，SAE 自动解释分数分不开训练与随机 Pythia）、Dead Salmons（撤稿）、Zhong & Andreas 2024 的随机 Transformer 已能做部分算法任务 `[摘要]`；探针领域也有 Hewitt & Liang 2019 的控制任务和随机编码器基线（凭记忆，未核对）。

MoE 专家分析这一支，我们读过的单模型分析都没有报未训练模型的基线：OLMoE §5、OpenMoE §4、Antoine 2024、Geometric Routing、DBES、2605.20610，在已抓的原文里检索 untrained / initialization 都没有命中。它们的基线是解析随机值（OLMoE 的 12.5%、Antoine 的均匀 U、DBES 的均匀分布）或置换零假设。Hash Layers 的随机 token hash 在构造上就是"未训练的按 token 专精"，但它是当作路由方法提出的，没有当作分析读数的地板。

所以"E176 的几条已发表结论在 step 0 上判定相同"，在 MoE 读数上没找到先例；在原则层面它被 Heap 2025 压缩。我们能写的增量是：逐条指出哪几条在 step 0 上判定相同，哪条是训练后才成立的（只有词形纯度 #7a）。

## R-A 的标题级主张：哪一句是真正没人写过的，哪一句只是复现

**没找到先例的：**
1. 同配置 MoE 跨独立训练的一致度**随读数粒度递减**，并且以**同 seed 精确重跑**为上限、未训练模型为地板来标定。找到的四件跨 run 工作都没有重跑上限：Equifinality、2605.20610、2608.15102、LMC-MoE。也都没有在同一套 run 上展开粒度。
2. **冻结随机路由器也给出跨 seed 可重现的粗划分**（词类级约 .66，与几何零假设相当）；而同词形分区这一级只有学到的路由才有（FRZ 的 T_D ≈ 0）。即粗粒度一致不是路由学习的产物，路由学习造就的是几何之外那一部分的可重现性。性能等效有人做过，冻结路由下的**跨 run 一致度**没人测过。
3. 已发表 MoE 读数的**三级审计**：模型级可推广，专家级不可推广，并逐条报 step 0 判定。审计这一形式没找到先例；"要报地板"这一原则归 Heap 2025。

**只是复现或已被 own 的：**
- 冻结 / 随机 / hash 路由对损失无明显害处：Hash Layers、THOR、SMoE-Dropout、Self-Routing、Equifinality；反证 Clark 2022。
- "单 checkpoint 结论不一定推广到训练程序"：MultiBERTs。
- "统计量重现、个体单元不重现"作为一般模式：Gurnee 2024、Paulo & Belrose 2025、Li 2015、2509.22831。
- "粗划分跨 seed 稳定"：视觉 MoE 2605.20610。
- "路由由表示几何决定"：Myth、Routers Learn Geometry。
- 路由早期饱和：OLMoE、OpenMoE。

**写作时的约束：**
- 上面"复现"类的每一句都只能带引用、作为背景，不能写成"我们发现"。
- 标题级主张要放在第 1、2 两句上；第 3 句是第 1 句的应用。
- 第 2 句最容易被读成 Hash Layers / SMoE-Dropout 的复述，要明确写"测的是一致度，不是损失"。
