# E176：published-readout-reproducibility（2026-11-06）

- **状态：** DONE（2026-11-06；纯 CPU，0 GPU，只用 E167 路由 / hidden 缓存与 UD 标注）
- **类型：** REPRO（已发表单模型专家分析读数在 9 个 run 上的跨 seed 复算；不推进新主张）
- **对应：** [ROUTE_AUDIT](../ROUTE_AUDIT_2026-11-06.md) B4（".73 只有一种方法、一个族"）的修法；[DIRECTION](../DIRECTION_2026-11-06.md) F4；读数定义来自 [READOUT_CATALOGUE](../../../../library/themes/moe-routing/READOUT_CATALOGUE_AND_SEED_ROBUSTNESS_2026-11-06.md) 表 1 的 #1 #2 #3 #6 #7 #13，#8 引用 E172。
- **问题（一句话）：** 已发表的单模型 MoE 专家分析结论，换 init seed 还在不在；在模型级、类别级、专家级三级中的哪一级还在？

## 原文读数与要核对的那句结论（PDF 在会话 scratchpad，未进仓库）
| # | 原文 | 读数（原文定义） | 原文结论（原话） |
|---|---|---|---|
| 1 | OLMoE 2409.02060 §5.1 式 (5)、图 20 | 路由饱和 sat(t) = (1/N)Σ_i \|E_i^(t)∩E_i^(T)\|/k，k=8 与 k=1；随机 = 8/64、1/64 | "after 1% of pretraining … up to ∼60% of routing to the top-8 activated experts has already saturated"；"which top-1 expert … saturates slower"；"routing in later layers saturates earlier"；"Layer 0 is an outlier saturating significantly more slowly" |
| 2 | OLMoE §5.2 式 (6)、图 21 | 共激活 = N_{Ei,Ej}/N_{Ei}（同层 top-8） | "there is no strong co-activation among experts in one layer, with only few exceptions" |
| 3 | OLMoE §5.3 式 (7) | 领域专精 = N^(k)_{Ei,D}/N_D，k=8 | Mixtral "exhibits little domain specialization"；OLMoE 有领域专家（arXiv / GitHub） |
| 6 | ST-MoE 2202.08906 §7 表 14 | 某类 token 的路由分布熵；均匀 = ln(专家数) | "encoder experts specialize, but decoder expert don't"；解码器熵 3.4 / 均匀 3.5 |
| 7 | Shazeer 2017 附录 E、BASE 2103.16716 §5.2、OpenMoE 2402.01739 §4.1–4.2 | 每专家最常见 token 表；同一 token 的路由集中度；中间 ckpt 的偏好重叠 | BASE "the token input … is often highly indicative of the expert"；OpenMoE "the routing probably has been learned at the warmup stage or so" |
| 8 | Antoine 2412.16971 §3 | Spec_POS、ΔU、路径探针；专家 POS 分布对语料的 KL | 引用 E172（不重算模型级与类别级） |
| 13 | DBES 2605.18498 §3 | S_spec = 各层领域专家分布对均匀的 KL 之均值；R_eff = 领域的 层×专家 概率矩阵的归一化有效秩；S_iso = 1 − 领域间（层堆叠）路由矩阵余弦的均值 | "modular specialization with high domain isolation, while DeepSeek and GLM employ distributed"；表 1 中 S_iso 约 .22–.64 |

DBES 的式子在 pdftotext 中丢失，按正文文字实现：R_eff = exp(归一化奇异值的熵) / min(L, E)。

## 设置
- **主数据（9 个 run，全程 checkpoint）：** `~/mechpop_cache/e167_analysis/routing/<run>__ckpt_<t>.npz` 的 `S{l}`（29,551 个锚点 × top-8，`S[:,0]` = top-1）。锚点 = 出现 ≥6 次的小写词形、每词形 ≤40 个、1,827 个词形、取词末 token（E175 已核对），不是自然流。标注：`pairs.npz` 的 `anchor_word` → `results/e167/ud_annotations.json`（upos / genre / doc_id）。
- **自然流复核（8 个 run）：** `hidden/<run>__ckpt_<t>.npz` 的 H_l·W_l^T + b_l 取 top-8 重算路由（113,118 个连续词的词末 token：anchor 88,802 + cal）。先核对重算结果与 `S` 在锚点上逐一一致。只有终点（I0–I3、I0D1、I1D1 在 40 亿；I4D0、I4D0R 在 32 亿）与 I0D0 / I1D0 的 step 0；**没有 I5D0**。只用于对样本分布敏感的读数：#3、#7（模型级与类别级）、#13，以及 #2 的模型级。
- **checkpoint：** 主分析 3.2B（9 个 run 都有；I4D0R 用 `ckpt_3200000000`）。#1 的饱和曲线用 0 / 25M / 50M / 100M / 200M / 400M / 800M / 1.6B → T = 3.2B。
- **run 与配对：** 只换初始化 I0D0–I5D0（15 对）；只换顺序 (I0D0, I0D1)、(I1D0, I1D1)；**重跑 (I4D0, I4D0R) = 上限 / 阳性对照**；**step 0 = 地板**（I0D0–I5D0 的 ckpt_0，15 对；同 init 的重跑在 step 0 完全相同，不算）。
- **层：** 主值为全部 12 层平均（原文都逐层画图）；深层 L6–11 存进 json。#13 按 DBES 定义堆叠全部层。
- **专家配对（专家级用）：** 每层用 Hungarian 最大化 top-8 共同 token 数。**交叉拟合**：按 doc_id 把锚点分成两半（种子 176），在一半上配对、在另一半上算专家级读数，两个方向取平均。配对带来的偏差由 step-0 地板吃掉（step 0 用同一流程）。
- **脚本：** `scripts/e176_readouts.py`（主数据）、`scripts/e176_natural.py`（自然流复核）、`scripts/e176_summarize.py`（三级汇总 + 逐 seed 定性结论）、`scripts/e176_figure.py`；结果 `results/e176/`。并行 ≤ 8 进程。

## 读数（看到结果之前固定）
每个读数三级。**模型级**：每个 run 一个数。**类别级**：一个与专家编号无关的类别剖面，跨 run 算 Spearman。**专家级**：配对后的专家向量，跨 run 算相关。
| # | 模型级 | 类别级（剖面，Spearman） | 专家级（配对后） |
|---|---|---|---|
| 1 | sat(50M→T)，k=8，层平均；另报 k=1、层最大、各层 | 各 UPOS（≥200 个 token 的类）在 50M 的 k=8 饱和度 | 各专家的饱和度：T 时分给 e 的槽位中、50M 时也分给 e 的比例；Pearson |
| 2 | 共激活 ≥ .5 的有序专家对比例（层平均）；另报每专家最大共激活的均值；随机 = 7/63 | 不适用（原文没有类别；专家对需配对） | 配对后 64×64 共激活矩阵的非对角元，Spearman |
| 3 | 每专家在 5 个体裁上的 lift = spec(E,D)/spec(E,全部) 的最大值，专家平均 | 各体裁的路由偏离 = ½Σ_E \|spec(E,D) − spec(E,全部)\|，(层, 体裁) 共 60 个值 | 配对后每专家的 5 维 (lift − 1)，展平 Pearson |
| 6 | 各 UPOS 类 top-1 路由分布熵 / ln64，按 token 数加权平均 | 各 UPOS 类的熵 | 配对后每类的 P(e\|c)（top-1），各类 Pearson 的均值 |
| 7 | 词形纯度 = 词形内 top-1 最常见专家的占比，按词形平均；另报同 run 内 400M 与 T 的每专家前 10 词形表 Jaccard | 各词形的纯度（1,827 个词形） | 配对后每专家前 10 词形表（top-1 计数）的 Jaccard，专家平均 |
| 8 | 引 E172：Spec_POS、ΔU、探针 | 引 E172：Spec_POS 剖面 Spearman（.73） | 本卡新算：每专家 KL(P(c\|e)‖P(c)) 配对后 Pearson |
| 13 | S_spec、R_eff、S_iso | 5 个体裁的 S_spec；10 个体裁对的 1 − cos | 不适用（三者都与专家编号无关） |

**原文结论的逐 seed 定性判定（写死；9 个 run 各自判，报"几/9"）：**
- #1a 早饱和：50M 时 k=8 饱和的层最大值 ≥ .5。#1b k=1 比 k=8 饱和慢：50M 时 sat_k1 < sat_k8（原始值，同原文）。#1c 后层饱和更早：L1–L11 的 50M 饱和与层号 Spearman > 0。#1d L0 最慢：sat_L0 < min(L1..L11)。
- #2 无强共激活、少数例外：每层共激活 ≥ .5 的有序对 ≤ 1%。
- #3 体裁专精：存在 (E, D) 使 lift ≥ 2 → 判"有"；否则判"很少"（Mixtral 式）。领域 = EWT 5 体裁，比 OLMoE 的领域粗得多，记录。
- #6 解码器专家不按类专精：熵 / ln64 ≥ .9 → 判"不专精"（ST-MoE 解码器 3.4/3.5 = .97）；否则判"专精"。
- #7a token 决定专家：词形纯度 ≥ .5。#7b warmup 内已定：400M→T 的前 10 表 Jaccard ≥ .5。
- #13 模块化：S_iso ≥ .5 判"模块化"，否则"分布式"（阈值按 DBES 表 1 的数值区间设，原文没有阈值）。

## 阳性对照与地板
- **#1 的地板（跑前补注）：** 50M 换成 step 0，即 sat(0→T)；类别级、专家级同样换成 0→T。
- **阳性对照 = 重跑对 (I4D0, I4D0R)：** 类别级与专家级的上限。重跑相关 < .5 的读数记为"本身噪声大"，不做跨 seed 判断。
- **噪声地板 = step 0：** 模型级报 6 个 step-0 值；类别级与专家级报 step-0 的 15 对相关（同一配对流程），即"未训练也能得到多少一致"。
- **重现指数（写死）：**
  - 模型级 R_m = 6 个 init 的极差 / \|init 均值 − step-0 均值\|。R_m ≤ .25 → 重现；.25–1 → 部分；> 1 → 不重现。若 \|init 均值 − step-0 均值\| 小于 step-0 自身的极差，判"训练不改变此量"。
  - 类别级 / 专家级 q = (ρ_init − ρ_floor) / (ρ_rerun − ρ_floor)。q ≥ .7 且 ρ_init ≥ .5 → 重现；q < .3 → 不重现；其余 → 部分。若 ρ_rerun − ρ_floor < .1 → "地板≈上限，此级不可判"。
  - 只换顺序的两对单独报告，不进 q。

## 混杂审计
- **锚点抽样压平词频（每词形 ≤40）：** 对 #3、#7、#13、#2 用自然流复核；其余读数的绝对值不能与原文直接比，只比跨 seed 的一致。
- **只有词末 token：** 词中子词不在样本里。未控制，记录。
- **专家配对的循环性：** 专家级在配对用的另一半文档上算；step-0 地板吃掉配对本身带来的相关。
- **I4D0 / I4D0R 的终点是 3.2B，其余 40 亿：** 主分析统一用 3.2B，所以无关；自然流复核中混用，记录。
- **体裁样本量不均（newsgroup、answers 较少）：** 报各体裁 n；lift 门槛 2 远大于抽样噪声（专家负载约 n_D·8/64）。
- **层平均掩盖层差异：** 逐层值存进 json，图中画出。

## 决策表（跑之前写）
- **情形 A：模型级重现、专家级不重现（多数读数如此）** → 已发表的模型级结论（饱和、熵、纯度、S_iso 这类）在单 seed 上可以下；"第 k 号专家管什么"的专家身份结论在我们的设置里不能跨 seed 移植，要多 seed。论文句式取 MultiBERTs 式"统计量重现、个体单元不重现"。B4 的修法：把".73"推广成一张按级别的表，写进 ROUTE_AUDIT。
- **情形 B：类别级有读数不重现** → 列出是哪几个读数、它们对应原文的哪句类别级结论，这些结论在单 seed 上不可靠；与 E172 #8 的 .73 并列。
- **情形 C：三级全部重现（含专家级）** → 专家身份跨 seed 可配对重现；我们"一致度低"的主张只剩 token 级（.19），叙事要改；作为压缩风险报主会话。
- **混合** → 按读数逐条归入 A / B / C，不选代表。
- **逐 seed 定性结论有分歧（某条结论不是 9/9 或 0/9）** → 单独列出，这条原文结论就是"取决于 seed"。
- **自然流与锚点结论不同** → 两者都报，不选一个。
- 以上都不是关线条件。

- **算力预算：** 0 GPU；CPU 约 1 小时，≤ 8 进程。**实际：** 0 GPU；锚点 48 秒 × 2 次（6 进程），自然流约 5 分钟（4 进程）。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

完整表：`results/e176/summary_table.md`；图：`results/e176/e176_figure.png`；数字：`results/e176/summary.json`、`pairs.json`（`runs.json`、`natural.json` 是逐词形数组，本地可由脚本重建，不进 git）。

**一句话：** 换 init seed 以后，模型级的数几乎都还在；类别级一半在；专家级一个都不在。原文那句定性结论在 9 个 run 上全是 9/9 或 0/9，没有一条取决于 seed。不过其中有几条在未训练的模型上也成立。

- **模型级（12 层平均，3.2B）：** 10 个数里 8 个重现，R_m 都 ≤ .25：饱和 k=8 .15、k=1 .17、共激活 .06、体裁 lift .06、词形纯度 .06、Spec_POS .24、S_spec .05、R_eff .16。重跑差都 ≤ .02。另外两个是"训练不改变此量"：类别熵（init .69–.71，step 0 .76）和 S_iso（init .087–.099，step 0 .105）。自然流结论相同，只有共激活（R_m .36）和 R_eff（.27）落到"部分"。
- **类别级（Spearman）：**
  - 重现：#1 各词类饱和，ρ_init .70，重跑 .92，地板 .16，q .71。
  - 部分：#6 各词类熵，ρ .73，地板 .41，q .60；#8 Spec 剖面（E172），ρ .65，q .61。
  - 不重现：#7 各词形纯度，ρ_init .32 与地板 .33 一样，q −.04；重跑也只有 .69。
  - 地板≈上限，不可判：#3 体裁偏离、#13 各体裁 S_spec 与体裁对隔离度。未训练时 ρ 就已经 .90–.95，体裁剖面是数据定的。自然流里 #3 的 q 为 .14。
- **专家级（配对后，交叉拟合）：** 重跑上限 .86–.91，测量本身可靠。init 对没有一个读数重现：
  - #1 每专家饱和：.27，q .29；
  - #2 共激活矩阵：.64，地板 .60，q .14；
  - #6 P(e|c)：.55，**低于地板 .67**，q −.52；
  - #3 体裁 lift：.52，q .55，部分；
  - #8 专家 POS-KL：.65，q .52，部分；
  - #7 前 10 词形表：init .08，地板 .01，重跑 .42，读数本身噪声大。
  - 只换顺序的两对在每个读数上都落在 init 与重跑之间（专家级 .71–.85）。配对后 top-8 重合：init .42、换顺序 .61、重跑 .71、step 0 .26。
- **原文结论逐 run：**
  - 9/9：#1b k=1 比 k=8 饱和慢；#1c 后层饱和更早；#3 有体裁专精（lift ≥ 2）；#7a 词形决定专家；#8 ΔU ≥ 25 pp。
  - 0/9：#1a "1% 训练时 ≥ .5"，我们 50M 处层最大约 .31，200M（约 6%）才过 .5，1.6B（50%）处 .82–.84，与原文"40% 时约 80%"接近；#1d L0 最慢，我们的 L0 反而最快，因为它在 step 0 就有 .28；#2 无强共激活，我们 ≥ .5 的有序对约 1.3%，略过 1% 门槛，对阈值敏感；#6 解码器不专精，我们是 .70，但 step 0 已是 .76；#7b warmup 内已定，Jaccard 约 .31；#13 模块化，S_iso 约 .09。
  - **POST-HOC（同一规则用在 step 0）：** #3 有体裁专精在未训练时 6/6 成立。#2、#6、#13 的判定在 step 0 与训练后相同。只有 #7a 是训练后才成立（step 0 为 0/6）。所以"结论跨 seed 不变"不等于"结论由训练产生"，单看 9/9 不够，要并报 step 0。
- **按决策表：** 混合，逐条归类如下，没有读数落入情形 C（三级都重现）。
  - 情形 A（模型级重现、专家级不重现）：#1、#2、#3、#6、#8。
  - 情形 B（类别级不重现）：#7 词形纯度剖面；#6、#8 是部分。
  - 地板≈上限：#3、#13 的类别级。
  - 论文句式（MultiBERTs 式）："已发表的单模型 MoE 读数，汇总统计跨 init 重现，专家身份不重现；有几条结论在未训练模型上就成立。"B4 的修法就是这张按级别的表；写进 ROUTE_AUDIT 由主会话决定。
- **主张变化：** 不改任何主张，只提供证据。和 E174 方向一致：粗粒度一致里，几何 / 地板的成分很大。
- **POST-HOC：** 饱和首次 ≥ .5 的 checkpoint 和 1.6B 处的值，见 summary_table 末节。
- **没做的：** #4、#5（D1 归 E175）；预测下一词版需要前向。
