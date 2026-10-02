# E13｜Planner-Stage Multi-Fidelity：候选筛选与高保真重评

- **状态：** PLANNED；未运行。
- **对应：** I08 / R2。
- **来源：** S7–S9/S13；Fast-LeWM与DeepJEPA是最直接近邻。
- **阳性对照：** 对同一candidate bank，full high-fidelity scoring定义“高保真elite”参照；cheap predictor必须在短/易任务上有合理top-M recall。
- **噪声地板：** planner sampling seed固定做paired candidate comparison；训练seed与搜索seed分开。fixed-wallclock与fixed-candidate两种协议都报。
- **决策表（跑之前写）：** cascade改善compute-quality→扩task/seed并训练shared head；cheap筛选漏掉好candidate→研究recall/calibration而非继续缩M；DeepJEPA/纯Fast已统治→分析是否还有candidate-stage互补；无收益→回R2换predictive object，不强写cascade。

## 问题

世界模型规划的计算是否应该**按candidate在搜索中的重要性分配**，而不是对每个candidate使用相同predictive fidelity？

## Stage A0｜Fast-LeWM selective self-consistency：先用同一模型验证principle

Fast-LeWM论文已经定义两种terminal estimate：
1. direct length-H prefix → terminal latent；
2. 先到intermediate prefix latent，再预测剩余horizon → decomposed terminal latent。

原方法可对每个candidate加self-consistency penalty。我们的第一实验把额外decomposed prediction当作**refined fidelity**：

- `CHEAP-ALL`：所有candidate只direct score；
- `FULL-REFINE`：所有candidate计算原self-consistency/refined score；
- `RANDOM-M`：随机M个candidate refine；
- `TOP-M`：cheap top-M refine；
- `ELITE-BAND`：cheap score靠近当前K-th elite cutoff的candidate refine；
- `INTERVAL`：用held-out candidate residual校准区间，只refine“仍可能跨过elite阈值”的candidate。

先在**完全相同candidate bank**上离线算：用多少refined calls能恢复FULL-REFINE的top-K elite set和最终selected action？再接在线CEM。这个experiment可以直接回答“candidate-stage fidelity allocation是否值得做”，甚至不需新训练。

## Stage A｜零/低训练原型

优先复用released LeWM与Fast-LeWM相同任务资产；若checkpoint不能严格对齐，先做native paired action-candidate audit，不直接比较raw latent cost数值。

每轮CEM：
1. sample `N` candidate sequences；
2. cheap predictor score all `N`；
3. 选择`M`个进入high-fidelity rescoring，`M > elite K`；
4. high-fidelity score决定最终elite与CEM update。

Refinement selectors：
- `TOP-M` cheap；
- `ELITE-BAND`：cheap elite cutoff附近；
- `LOW-MARGIN`：top/elite margin小；
- `RANDOM-M` budget control；
- `FULL-HF` oracle-cost upper reference。

若两predictor latent空间不同，只比较candidate IDs/rank/real utility，不把raw L2混成统一尺度。

## Stage B｜shared dual-fidelity method

只有Stage A有signal才训练：
- shared visual encoder；
- cheap direct-prefix/head；
- expensive recursive/multi-step/refinement head；
- 可选cross-head consistency/calibration；
- gating先用简单validation threshold，再考虑learned routing。

不要一开始就复刻DeepJEPA的continue head。我们的核心轴是**candidate fidelity**；DeepJEPA是transition-depth强参照。

## Baselines

- LeWM recursive CEM；
- Fast-LeWM；
- equal-wallclock Fast-LeWM with more candidates；
- equal-wallclock LeWM with fewer candidates；
- random high-fidelity refinement；
- proposed top/boundary refinement；
- DeepJEPA：截至2026-10-02官方仓库标“code will be released soon”，若执行时已release则加入；不阻塞首轮。

按证据再加入UHM/Jumpy/TD-MPC2，不先建全范式排行榜。

## Metrics

### Primary
- closed-loop success / task cost；
- wall-clock per planning decision；
- model calls / active params calls；
- success under fixed deployment compute。

### Mechanistic
- cheap top-M对high-fidelity top-K的**elite recall**；
- cheap/HF Kendall rank on decision-relevant subset；
- high-fidelity rescoring导致的elite membership flips；
- selected action变化及real regret；
- CEM iteration 1→last 的fidelity value。

### Training
- train GPU-hours / checkpoint size；
- shared dual-head若使用，分别报告参数与额外训练成本。

## First-wave规模

E00实测后填具体时间。探索先：
- TwoRoom + Push-T/Cube中一项；
- pure LeWM / pure Fast / random-refine / top-refine / boundary-refine；
- 1 evaluation seed/少量episodes用于工程与effect-size。

信号成立后：
- ≥3 independent train seeds（需要训练的variants）；
- 第二任务族；
- `M/N` sweep；
- fixed-wallclock确认；
- DeepJEPA code-ready时加入direct neighbor。

### Multi-fidelity历史基线

传统robotics已有多保真trajectory optimization / MPC，甚至有并行运行不同动力学fidelity的工作；因此不要声称“first multi-fidelity planning”。我们要证明的是**learned latent CEM中，elite preservation可以作为predictive fidelity allocation的有效接口**，并与Fast-LeWM/DeepJEPA的现代predictor设计互补。

## Novelty pressure

DeepJEPA已明确“decision-critical transitions值得更深计算”，Fast-LeWM已明确“prefix prediction可以更快”。因此最终故事不能是“adaptive compute”或“coarse-to-fine”四个字；必须证明**candidate-stage predictive fidelity allocation**是独立load-bearing轴，并在相同compute下给出更好的search/decision结果，最好与transition-depth routing互补。

## 结果
未运行。


## 代码可行性：不需要重写CEM

已审 stable-worldmodel `CEMSolver` 与 Fast-LeWM `get_cost`：

- CEM 每轮已经显式持有 `candidates / costs / topk_inds / topk_candidates`，并支持 callback；
- Fast-LeWM `get_cost` 先对所有candidate做direct rollout；只有 `consistency_loss_weight != 0` 时才额外跑 `rollout_action_num_blocks_per_step` 得到decomposed terminal estimate；
- 因此 selective refinement 可以以很小改动实现：direct score全体 → selector返回candidate indices → 对该subset切片 `info_dict/action_candidates` 做decomposed rollout → 回填refined cost → CEM按混合后的cost选elite；
- callback可以记录每轮cheap elite、refined set、最终elite membership、mean/var shift，不需要另写一套planner。

第一版先 fork/patch evaluator或cost wrapper，不改Fast-LeWM训练代码。只有Stage A0显示compute-quality收益后，才考虑shared dual-head训练。


## Promotion rule v0：从top-M到elite-crossing interval

第一轮必须保留最简单的 `TOP-M`，因为它是不可缺的baseline；然后再测一个真正利用cheap→refined discrepancy的selector。

在**独立calibration candidate bank**上计算：
[
r_i = c_i^{refined}-c_i^{cheap}.
]

先不拟合复杂模型。按 cheap rank / CEM iteration / horizon 做粗bin，估计residual的下分位数 (q^-_alpha) 和上分位数 (q^+_alpha)。对当前candidate i得到：
[
L_i=c_i^{cheap}+q^-_alpha,quad
U_i=c_i^{cheap}+q^+_alpha.
]

因为cost越低越好，先refine cheap top-K（或一个很小sentinel set）得到当前refined elite阈值 (	au_K)。随后：
- 若 (L_i > 	au_K)，即使按乐观residual也难进入elite，可跳过；
- 若区间与 (	au_K) 重叠，则promotion到refined evaluation；
- 每次新refined candidate改变 (	au_K) 后可更新一次promotion判断。

这个 `INTERVAL` 不是预先宣称conformal guarantee；它只是**elite-crossing heuristic**。只有held-out coverage/calibration通过后，才考虑正式的distribution-free bound。

### 为什么比raw TOP-M更值得研究

TOP-M默认cheap rank近似refined rank；INTERVAL显式建模**cheap predictor在哪些candidate上可能错过elite**。如果它能以明显更少的refined calls达到相同elite recall，说明真正需要分配的是**ranking uncertainty around the optimizer boundary**，而不是单纯“给最好候选多算一点”。

## Offline candidate-bank audit先于closed-loop

每个task先保存固定CEM candidate banks，并对所有candidate离线算cheap+FULL-REFINE，得到真实的refined ranking。对不同selector模拟promotion，不让closed-loop噪声掩盖算法性质。

主图之一可以直接是：
- x：high-fidelity call fraction；
- y1：top-K elite recall；
- y2：selected-action agreement with FULL-REFINE；
- y3：candidate-bank regret。

只有离线trade-off有价值，才跑完整闭环 wall-clock / success。这样能把很多候选M/alpha筛选在单GPU甚至一次checkpoint评测里完成。


## Elite-set sufficiency：一个可以支撑方法的结构性事实

CEM 对下一轮 proposal distribution 的更新只消费 elite candidate actions，而不是所有 candidate 的精确 cost。令 full high-fidelity evaluator 的 elite set 为 \(E\)，selective method 恢复的 elite set为 \(\hat E\)，两者大小都为 \(K\)。如果 \(E=\hat E\)，那么在相同 sampled candidate bank 下，**CEM 的下一轮 mean / population-variance update完全相同**；非elite candidate 的high-fidelity cost可以完全不知道。

更一般地，若每个action-sequence向量 \(x_i\) 满足 \(\|x_i\|_2\le B\)，且两elite sets各错换 \(r\) 个candidate（对称差大小为 \(2r\)），则均值更新有直接界：
\[
\|\mu_E-\mu_{\hat E}\|_2 \le \frac{2rB}{K}.
\]
对二阶矩阵同理有 \(O(rB^2/K)\) 的扰动；协方差更新也因此随elite mismatch比例增长。这个推导很简单，**当前只作为待形式化/单元测试的设计依据，不登记为已证明论文定理**。

这使H-B的目标从“近似所有high-fidelity costs”转成更贴合planner的任务：

> **用尽可能少的 refined evaluations 保住 high-fidelity elite set。**

因此 offline candidate-bank 的第一指标应是 elite recall / symmetric-difference，而不是全体candidate的MSE或Spearman。若这个接口成立，后续理论与算法都围绕elite-membership uncertainty自然生长。