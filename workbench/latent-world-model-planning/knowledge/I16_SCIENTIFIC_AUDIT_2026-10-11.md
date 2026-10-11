# I16 独立科学复核：哪些观察可信，哪些解释尚未成立

日期：2026-10-11。审计模式：**只读代码、汇总数据与实验卡 + 对照外部论文，不启动新的 GPU 实验**。本文件只是研究判断，不修改实验状态、不把观察升级为 science claim。

## 0. 先给判断

- **值得保留的观察**：同一自建 LeWM-family 训练/评测协议下，TwoRoom 的 CEM+latent L2 在增大整个模型配方时反向变化；PushT 在相同类型扫描中大幅改善。该现象可从 [E21](../experiments/E21-scaling-planning.md)、[E23](../experiments/E23-paper-grid.md) 和 [E23 D_eff](../results/E23_deff_collapse.json) 回读。
- **既有强邻已覆盖的解释**：“latent L2 与 task cost 不一致”“信息存在但 planner 用不了”“各向同性导致目标函数偏差”“慢谱/时间距离可以改善导航”。见 [论文笔记](PAPER_NOTES_2026-10-11.md)。不要以其中任一单独作为 I16 新的主张。
- **目前被说得过满的机制**：“参数变大 → SIGReg 将高频等方差编码 → D_eff 增大导致 metric horizon 缩短 → 搜索一定失败”仍混合不同层级的关联、代码实现 confound 和不充分的推导。
- **真正开放且可能够大的问题**：端到端 latent WM 的**规模到底改变了预测能力、决策可用几何还是动作可达集**？何时三者不一致？如果经过一套精确但简单的行动排序实验后能建立可迁移规律，才考虑论文形态。
- 本轮从未独立重跑模型或重新生成评估结果。因此以下 [OBS] 表示**仓库报告且源文件可追溯**，不等价于多机独立校对通过。

## 1. 现有实证最强部分

### 1.1 主现象（[OBS]，E21/E23）

| 环境 / 测试条件 | XXS 1.7M | XS 4.1M | S 17.9M | M 71M | 如何解释 |
|---|---:|---:|---:|---:|---|
| TwoRoom CEM+L2，off50 | 72% | 66% | 63% | 53% | 在**这组联合缩放的架构配方**下恶化 |
| TwoRoom CEM+L2，off75 | 47% | 41% | 38% | 29% | 长目标下降更明显 |
| PushT CEM+L2，off25 | 17% | 53% | 85% | 87% | 操作任务反方向变化 |
| TwoRoom M，SFA k=4，off50/off75 | — | — | — | 98.5% / 94% | 不改 WM 权重、改代价 + 离线估计慢谱后强修复 |

原卡报告多训练种子（部分 M/L 只有 1–2 个），并有不同搜索预算、PointMaze、Reacher/Cube 的扩展。应原样引用 **n=200 episodes / cell 是评测样本**、**训练 seed 数不是 200**。不把不同任务的绝对成功率当成直接归一化的“scaling law”。

### 1.2 重要真实干预和边界（[OBS]）

1. 两室 S 模型中，SIGReg λ=0.01 的 off50 均值 80.7%，默认 λ=0.09 是 63.2%，三个训练 seed 内同方向；极低 λ=0.003 表示坍缩。**可以说正则权重对该评测结果有因果作用**，不能直接说 D_eff 是唯一中介。
2. 发布 224px LeWM 权重不是我们的 64px 配方：TwoRoom released L2 off50 57%、off75 32.5%，加 SFA/混合切换后更好；PushT released 完整 L2 off25 81.5%，强行 SFA 单独成本跌到 42%。这支持代价的任务差异跨分辨率存在，但没有验证官方配方的**规模扫描**。
3. 冻结的后验切换规则在 PointMaze-large 后续任务上优于 L2；Cube 部分状态不伤害，visual-antmaze 上全部方法很弱，因此后者不能提供有力的正面机制验证。慢谱在迷宫随规模的斜率仍可为负，远目标绕墙失败约 40%，记录必须留在正文而非附录隐藏。
4. 压低 latent 输出维度未如预期带来 metric horizon 增长或规划恢复。它是对“D_eff → horizon”朴素因果链的**重要反例**，不应以“也许因为折叠”一句话直接抹除。VICReg（E24）仍未有结果，不能以一般的“各向同性正则”宣布跨正则结论。

### 1.3 已经做对的研究动作

- 冻结研究前已检查真实环境结果、搜索预算、真实动力学而非只看 predictor MSE。
- 把跨房间坐标误差、拟合指数 −1/d、失败的 PCA/dim bottleneck 实验明确撤回，而没有筛结果。
- 在发布检查点上检查了尺度之外的真实现象，并保留 PushT 对 SFA 反方向、maze 尺度非单调和视觉 antmaze 失败。

这些是 I16 最珍贵的资产，应基于它们继续找**竞争解释**，而不是围绕旧故事反复维护。

## 2. 代码层面最要紧的四个混杂

### C1. 所谓“模型规模”实际上联合改变了至少四项设计（[CODE]）

定位：[wm.py](../scaling/wm.py) SIZES / build_model、[train.py](../scaling/train.py)。

| 级别 | encoder 宽度 | encoder 层数 | predictor hidden 宽度 | latent 默认维度 |
|---|---:|---:|---:|---:|
| XXS | 64 | 6 | 64 | 64 |
| XS | 96 | 8 | 96 | 96 |
| S | 192 | 12 | 192 | 192 |
| M | 384 | 12 | 384 | 384 |
| L | 768 | 12 | 768 | 768 |

predictor 保留 6 层形式，但其中 MLP 宽度、attention head dimension、projection / action embed 和 latent D 会跟随 width 变化。**因此当前证据不支持“总参数数增加本身使规划变差”或“更深 encoder 让规划变差”的隔离因果判断**。

I16 也已有 latent dim 截断失败的干预，这意味着单独锁定 D 与改变整个架构不是同一个操作。下一轮如果做规模科学，首要问题是选对“scale treatment”，不能在每一种失败后再追加新的变量把文章救回来。

### C2. Equal optimizer steps 不等于等优化程度，更不等于训练收敛（[CODE]）

[train.py](../scaling/train.py) 所有 run 用相同 step 数、batch 128、默认学习率、warmup/cosine；训练数据选择一致是优点。但大/小模型每 step FLOPs 差异大，固定 step 不保证相同损失拟合程度；默认 λ=.09 也不保证不同 latent D 的正则梯度强度与预测梯度比相同。

可报告“matched update count”和“train compute / loss curves”；不能以此直接宣布 model-scale effect 已与 optimization/schedule 脱钩。两种匹配同时进行只有在有具体竞争假设时才值得耗 GPU。

### C3. Metric horizon 的定义**不是一般意义上的可规划视野**（[CODE]）

[eval_plan.py](../scaling/eval_plan.py) 271–302:
- 每个 lag h 分别从满足 episode length > h+1 的轨迹里**重采样另一组 episode 与起点**；
- 算这些 lag-pairs 的 full latent L2 **中位数**；
- 把最后一个可用 lag 的中位数当 plateau，然后定义第一个达到它 90% 的 lag 为 mh。

问题：由于每个 lag 的可抽样 episode 群随 h 变化，长轨迹可能只来自特殊策略/布局/速度。所谓 plateau 是**最长可测 lag 的数值**，而不是独立 iid/random-pair 远距统计或数学极限。在不同 task、训练 seed、trajectory length distribution 下，它可能同时受样本构成和固定 lag 网格影响。mh=10 对 TwoRoom 之类场景只是经验诊断值，不是“L2 在 10 步以后毫无排序信息”的定理。

[OPEN] 首先用**同一批足够长的 trajectory**在所有 lag 上做 matched curve；提供 median + conditional Spearman/Kendall vs true task progress，并把 “last lag plateau” 和 independent-pair reference 分开。若 matched curve 改变结论，过去的机制说明要降级。

### C4. 训练用线性 SFA 不是“零数据/零估计”的修复（[CODE]）

[eval_plan.py](../scaling/eval_plan.py) 234–267 拿训练轨迹 t 与 t+5 的 latent，估计 Cov(z) 与 Cov(Δz)，做广义特征值分解，选最低 4 个方向，再 whiten。**没有重新训练 world model 权重 / 也没有拟合新网络**，这是客观方法优势；但明确需要一个数据分布上的后验 basis fit（约 20k pairs）。

线性 SFA 的低变化方向既可能是 task 相关的导航位移，也可能是缓慢变化的背景/视觉 distractor；对 PushT 可能滤掉必须优化的物体姿态。没有证据保证慢方向都等于环境图 Laplacian 的正确 commute-time 特征，不能以“受谱理论启发”推出它对任意 long goal 的最优性。

**还有一个分层语义差异**：I16 的外层 frozen rule 先依据 mh < 25 决定运行“auto”还是保留 L2；[eval_plan.py](../scaling/eval_plan.py) 351–359 的 auto 是**控制循环内部**的慢/快代价切换。外层选择目前在 E23 的文字决策中固定，不能把两个同名策略混为一个。发布 PushT 原始 auto=76% 而 L2=81.5%，报告的“不伤害”是外层按 mh 选择 L2 的效果，并不是“内部 auto 每环境都不伤害”。必须在论文方法里画出这两个决定。

## 3. 当前“理论”最容易被审稿人指出的推理跳跃

### 3.1 核恒等式正确，但作用范围很窄

设 z=φ(s)−μ，s,s' 独立同分布，Cov(z)=Σ，定义 K= zᵀz' / trΣ。那么

\[
\mathbb E[K^2]=\frac{\operatorname{tr}(\Sigma^2)}{(\operatorname{tr}\Sigma)^2}
=\frac{1}{D_{\mathrm{eff}}}.
\]

因此（以 Markov 用在 K² 上）：

\[
\Pr(|K|\ge \kappa)\le \frac{1}{\kappa^2D_{\mathrm{eff}}}.
\]

这是 [kernel_bound.py](../scaling/kernel_bound.py) 用 iid 随机状态对在检查的数学恒等式。**它不包含任务、动作、真实动力学，也不包含 goal-conditioned candidate set**。从这里推出“更高 D_eff 必须降低 CEM 成功率”，缺少至少两座桥：
1. 对 planner 实际访问的**动作条件**状态对，K 或 cost gap 是否出现同一现象？这些不是 iid pairs。
2. 这些 cost gap 的统计变化如何导致 action rank inversion、CEM 选错、最终实际 success 降低？

等范数近似为常数，才可从 K 的分布推出典型 L2 距离集中；“典型状态对集中”仍不等价于“规划候选的**微小但关键的方向差异**不再可排序”。这里 CEM 排序是关键，而不是 pairwise 距离的绝对值。

### 3.2 “维度越高 ⇒ 特征频率越高 ⇒ metric horizon 变短”尚不是 I16 已证定理

Weyl 计数或拉普拉斯谱有严格的假设（空间域、边界条件、特征函数排序、平滑性及归一化方式）。真实 learned encoder 没有被证明在给定任务的数据分布上等价于最前若干 Laplacian eigenmodes 或等权谱和。

尤其 **同一 D_eff 可以对应不同的特征方向、不同频谱权重和不同目标排序**。I16 的 latent-dim 干预已经与强“D_eff 唯一决定”假说不符。CTWM 反而说明：**有效的谱权重不必均匀**，而各向同性的许多高维正则破坏的是**正确权重分配**，不只是 rank 高低。

应把现有理论写成：
- 定理 A：iid kernel 二阶矩恒等式（范围严格限定）；
- 观测 B：同一训练家族的规模/λ 与 D_eff、距离 lag 曲线和成功率相关；
- 未证 C：决策相关谱权重或排序裕量是怎样的真实中介。
没有 C 就不要称“机制闭环”。

### 3.3 D_eff 的相关性**比纯训练集内拟合更强一些，但仍不是因果**（2026-10-11 新的离线重算）

[deff_collapse.py](../scaling/deff_collapse.py) 汇总 26 个 TwoRoom run，基于同一系列 encoder width + λ 配方，对 success ~ log10(D_eff) 拟合直线。原报告 off50 R² = .886，Spearman −.94。源码先排除 λ<.005 的坍缩 run，故统计结论对 non-collapsed 系列成立。

本次**独立读取已提交的** [E23_deff_collapse.json](../results/E23_deff_collapse.json)，没有重新跑 GPU，按如下方法重新分析：每次将一个 size（或一个 λ 值）的**所有 run** 完整留出，只在其余组拟合带截距的一元 OLS success = a+b·log10(D_eff)，对留出组每个 run 预测；拼接所有 out-of-fold predictions，按全部 26 个 run 的共同均值计算 1−SSE/SST 的 pooled out-of-fold R²。没有用测试组估计系数，也没有在每组内选样本。

| Goal offset | 原 in-sample R² | 留出整个模型尺寸 R² | 留出整个 λ 组 R² |
|---|---:|---:|---:|
| 25 | 0.832 | **0.783** | **0.668** |
| 50 | 0.886 | **0.805** | **0.766** |
| 75 | 0.850 | **0.763** | **0.668** |

**新的判断**：这个 D_eff 线性关系在所研究训练家族内并非完全由训练集内拟合形成；即使留出单个完整 size/λ，它仍有实质的预测力。**不能**轻率当作“相关性不足”而丢弃此线索。

**仍未回答的关键问题**：全体训练/测试仍来自同一个 TwoRoom 任务、同一种 SIGReg-based 模型家族，而且同一独立 episode 分布、多数规格的 seed 不多；训练后的 D_eff 可以是“造成坏排序的中介”，也可以仅是“SIGReg optimization 的可见 proxy”，二者在此数据里不可区分。此 CV 没有重训 model、没有新任务、新 regularizer、不跨部署域；它不是因果检验，也不是为 R² 计算的置信区间。

下一个高信息量动作不应是继续提升 R²，而是问：**当 D_eff 变化但真实候选动作的任务相关 cost ranking 不变时，成功是否也不变？当 ranking 已改变却不依赖 D_eff 时，究竟谁解释行动效果？** 这直接指向 [下一步 D1](NEXT_DECISIONS_2026-10-11.md)。


## 4. 统计与评测审计：目前的 CI 不够支持“论文级斜率”

[scaling/e23_report.py](../scaling/e23_report.py) 设参数量 XXS~L 的 x=log10(params)，每个 size 放入当前已完成训练 seeds 的 cell mean / 单 seed success；将每个 size 的 seeds 在该 size 内 bootstrap 抽样，然后对这些行做 OLS 斜率。问题：

1. 有些 size 仅 1–2 seed，其区间不能捕获真实训练方差；1 seed 重采样毫无不确定性，CI 会假精确；
2. 每个 size 有不同 seed 数，OLS 行数量在各尺寸不相等时会形成**不透明的加权**；
3. n=200 真实测试 episodes 的抽样误差没有进入 slope CI，seed 与 episode 两种不确定度没有完整分层；
4. 各 train seed 可能评测共享测试 episode ID，但每个 result 保存了 episodes 与 success，应该利用**paired goal** 不确定度估计，而不是把所有样本当独立；
5. 同一任务不同 offsets / 多种后验方法重复分析有选择性探索风险；预注册 E23 与后验 E22 必须分开。

**无需新 GPU 的首选审计**：以 raw eval JSON 重新生成固定 model-seed 的 paired episode success，聚合时让 size 权重等同；先报告 size mean 与原始 seeds 全部结果，随后给一套可重复 seed × eval-episode hierarchical bootstrap 或混合效应模型，不要制造小样本精细 CI。当训练 seeds 少于 3 时，报告观察区间与结论边界，比报漂亮置信区间更科学。

本轮 GitHub 中的 [E23_table.json](../results/E23_table.json) 有些 cell 仍只有 seed0，属于**运行中的快照**，而不是全体最终确证表。文字 E23 更新到 21:20，但不等于文件里所有组都已同步完成。这些结果必须按文件版本/数据信源标注，不能直接用一张局部表替代最终报告。

## 5. 复现与协议中的潜在威胁

- **模型身份**：S width 192 在模块设计上接近 LeWM，但自己的主要训练使用 64px、patch8、60k iterations、GPU 常驻数据管线。官方发布权重验证了部分 observation，不能证明“所有缩放档与官方实现完全相同”。
- **goal construction**：[eval_plan.py](../scaling/eval_plan.py) 从 held-out episode 按 offset 取起终点，成功预算 2×offset 步；这是条件于 **数据采集行为的目标分布**，offset 不等于最短路径长度，也不能假设不同任务拥有同一目标难度。
- **候选动作**：CEM 固定 budget 和参数并不能完全排除搜索器–loss landscape 的交互（参数尺度、cost 平台、elite ranking noise、梯度错位），应先检查排序裕量和 true terminal task utility，不再只扫候选数量。
- **强基线**：对训练 free 的 SFA，除了原 L2、PCA、GC-IDM，还必须有 TEMPO、AnisoWM、CTWM、ICML Laplacian/straightening 作为机制和方法的近邻。否则修复做得再强也只是和弱成本函数比。
- **成功率不是理论量**：TwoRoom 近接100%、PushT 低频处理可能不合适。不同真实任务的 CEM 预算和控制难度均可触发天花板/地板效应。成功率曲线差异不足以单独证明一种普遍 learning law。

## 6. 新旧主张如何裁剪

| 旧版常见说法 | 当前审计后的可说版本 | 缺少何种证据 |
|---|---|---|
| “越大越短视” | “在当前联合放大的 LeWM-family 配方、特定任务和固定 CEM-L2 interface 下，TwoRoom 出现性能下降” | 独立尺寸/embedding D/compute 干预，更多环境 |
| “原因是各向同性 SIGReg” | “调 SIGReg λ 对 TwoRoom L2 planning 有稳定影响，伴随 D_eff/metric changes” | 不改变动力学/训练预算的几何隔离；行动排序中介 |
| “D_eff 是充分统计量” | “同一 TwoRoom 训练家族内拟合相关性强” | 留出 size/λ/正则/模型家族预测；与 VIScore 比较 |
| “度量视野比规划视野短则失败” | “训练轨迹按选定 lag 定义的 mh 与部分 L2 failure 有经验对应” | 采样定义审计、独立 goal action ranking、留出任务检验 |
| “无训练、万能修复” | “冻结 WM 上以约 20k 数据轨迹估计 SFA k=4，可强烈改善导航；部分操作退化/迷宫远目标失败” | TEMPO、CTWM、AnisoWM 公平 baseline，数据成本与 OOD |
| “从机制统一解释所有 scale failure” | “已展示相关的不同失败与成功边界，统一机制**尚未建立**” | 直接决策比较与反事实、跨任务 falsification |

## 7. 一个很可能比继续叠 loss 更值得检验的因果切面

把候选动作 j 的真终点记为 s_j、模型预测 latent 为 \hat z_j、真实目标 s_g、编码器输出 φ(s)，则构造：

- **Target ordering**：真实环境下哪个 s_j 最能提高任务进度 U(s_j,s_g)？
- **Metric ordering**：用完整环境真终点 φ(s_j) 的 latent cost 与 U 排序的一致性（测独立于 predictor 的**表示/代价错位**）。
- **Prediction ordering**：同一个 cost 作用于 \hat z_j 后与真实 φ(s_j) cost 的一致性（模型误差）。
- **Optimization ordering**：给定相同 candidate set，CEM 优化是否能找到最优 ranking? 更多预算是否产生 Goodhart / model exploitation？
- **Closed-loop success**：实际执行 + 重规划把上面哪些错误纠正或放大？

这个 decomposition 才真正检验“信息、模型、损失、搜索在不同规模下如何脱钩”。这不是最先提出 action ranking 的工作：SCALE、VIScore、ARC-Bench、CTWM、Search Difficulty、Planning Limits 等都是最近邻。它的科学增量必须来自**规模变量被隔离后的可迁移关系、及此前解释不了的任务差异**，而不是分解图本身。

## 8. 目前决定

**建议保留 I16 研究对象，不自动恢复实验，先用现有 artifacts 做 C3/C4/statistical audit 和 matched action-ranking 的可行性论证。** 如果审计后现象只在 64px 联合尺度 + TwoRoom 存在，或与 CTWM/TEMPO 的机制完全同义，则降低 I16 独立论文优先级，转而从 [NEXT_DECISIONS](NEXT_DECISIONS_2026-10-11.md) 的更大问题重新选题；不是再调 k、阈值、λ，也不是宣告整个 WM territory 已无价值。
