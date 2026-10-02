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
