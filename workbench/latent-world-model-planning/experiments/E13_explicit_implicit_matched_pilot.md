# E13｜Planner-Stage Multi-Fidelity：候选筛选与高保真重评

- **状态：** RUNNING；TwoRoom A0/A1 已执行，接续 PushT 原生数据。
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
2026-10-02，官方 TwoRoom、12 episode anchors（4 CAL/8 TEST）、seed0：[结果与 episode CI](../results/E00_E13_E16_20261002_tworoom_native.json)。20% TOP-M-SCREEN elite recall=96.86% [90.58,100]；INTERVAL/cap20% 实际重评13.08%、recall=95.93% [87.79,100]。确定下界控制平均重评16.45%恢复全部 elite。以上是 FULL 模型评分参照，不是真实 simulator regret。

实际 cached GPU timing（24 banks，各3次）：FULL 35.02 ms、TOP20% 35.00 ms、INTERVAL20% 54.05 ms、LOWER-BOUND/batch64 54.45 ms；降低 call fraction 未带来耗时优势。完整闭环 8 paired start/goals：CHEAP-300、FULL、TOP20%/30%、INTERVAL20%、RANDOM30%、LOWER-BOUND 都为7/8；相对FULL没有观察到成功翻转。CHEAP-900为8/8，相对FULL差 +12.5个百分点 [episode bootstrap 0,37.5]。7/8 Wilson CI=[52.9,97.8]%，8/8=[67.6,100]%，不作等价或显著改善主张。含编码与 selector 的 decision time：CHEAP-300 0.486 s、FULL 1.230 s、TOP20% 1.277 s、INTERVAL20% 1.837 s、CHEAP-900 0.523 s。

**当前原型尚无实际收益证据。** 不为挽救 INTERVAL 反复局部调参；先检查原生 PushT，再据两类任务判断计算应该花在 fidelity、search breadth 还是 CEM updates。CAL/TEST 只对 selector calibration 隔离；发布模型训练集与这些 episode 的关系未核对，不能称 unseen world-model episodes。

## 2026-10-02 Stage A0 批次（运行前）

- 推进 I08/R2；先 TwoRoom + PushT，同任务全部条件使用 SAME Fast-LeWM checkpoint 与 SAME candidate bank。
- 第一轮 seed=0，保留官方 horizon/action repeat/CEM 设置；若工程预算先减 episode 数，明确记为 pilot，不改成功定义。
- 每任务至少 12 个互不重叠 start-goal episode anchors：前 4 个 calibration、后 8 个 held-out audit；候选为原生 CEM 各轮 cost wrapper 捕获的 bank，不按结果筛 anchor。资源允许后扩至 32+ anchors。
- CHEAP-ALL / FULL-REFINE / RANDOM-M / TOP-M / ELITE-BAND / INTERVAL；M/N=0.1,0.2,0.3,0.5,1.0。随机 promotion 使用预先固定 seed；每个点同时报告实际 call fraction，K 约束不得伪装为目标 fraction。
- refined 按官方 nonnegative self-consistency penalty；权重/分解方式从原生配置核对后在首次 model scoring 前锁定。FULL-REFINE 是 scoring reference，不预先叫 real-utility oracle。
- 主读数：FULL-REFINE elite recall、selected candidate/action agreement、FULL-score candidate regret、proposal mean/variance difference、额外模型调用比例与真实 wall-clock。真实 simulator regret 使用 E16 bank 的独立 outcome 审计，明确区分模型参照 regret。
- INTERVAL 仅用 calibration residual；held-out refined score 只用于评测，不能提前喂 selector。保留最简单 TOP-M，并检查未 refine 候选的混合成本是否诱发乐观偏置。
- 20–30% refined calls 达到 ≥90% elite recall 是扩 closed-loop 的探索触发，不是科学判决；若 TOP-M 已相当，记录；若 recall 差，先测 calibration/sentinels，不缩问题。

### scoring 前的原文/代码核对

Fast-LeWM v2 Appendix D 明确 β=1、分解 [2,3]（10+15 primitive steps）；公开 eval yaml 的 β=0 是 direct 默认，不能把它误当 self-consistency 配方。本批锁 β=1，原生 N=300、K=30、30 CEM iterations、25 primitive-step prefix。

增加 `LOWER-BOUND` 强参照：β≥0 且 consistency penalty≥0，因此 native cheap cost 是 refined cost 的确定下界。按 cheap cost 从小到大，至少 refine K 个；若下一候选 cheap cost 已超过当前 refined K-th cost，则剩余候选不可能进入 refined elite，可以停止（ties 保守重评）。这是特定 scoring 结构的算法控制，不提前声称新颖或一般 learned predictor 保证。若它高效，closed-loop 必須与 TOP-M/INTERVAL 和更多 cheap candidates 比较；后续跨 predictor 的 residual 可以为负，需独立校准。

- 下载期间 simulator-generated anchors 只供仪器/计算量 pilot；正式科学读数使用官方 HDF5。CAL/TEST 按整条 episode 分开，bootstrap 也以 episode 为单位，不能把 30 CEM iterations 当 30 独立样本。
- 固定预算 selectors 默认以 calibration median residual 填补未重评 cost；额外保留 `TOP-M-SCREEN`（只在 shortlist 中选 elite）和 `TOP-M-MIXED`（直接混合 refined 与未校正 cheap cost）强基线/混合偏置诊断。不把 shortlist recall 当作实际混合 planner recall。
- 此发布 CEM 更新的是 sample standard deviation（`torch.std` 默认 correction=1），不是 population variance。精确 elite 对照应比较实际 mean/std 更新，修正旧文字中的 variance 简称。

### 实际 GPU timing audit（运行前，2026-10-02）

固定每个 held-out episode 的第 1 / 中间 / 最后 CEM bank，不按结果选 bank；使用原 checkpoint、N=300/K=30 和 β=1/[2,3]。保留原生 FULL-REFINE 与 CHEAP-ALL，实际执行 TOP-M-SCREEN（20%/30%）、TOP-M（30%）、INTERVAL（20%/30%）、LOWER-BOUND（batch=16/64/128）。2 次 warmup，3 次重复，各 bank 内以固定 seed 随机化运行顺序；CUDA 同步计时，CPU selector、传输和小批调用均纳入时间。首次核对记录 wrapper 与原生 β=1 cost 的数值一致性，并测 subset evaluation 的数值漂移。报告实际 candidate/refinement forward calls、elite recall、CEM mean/std difference 和真实 wall-clock；call fraction 不能替代 speedup。工程 bank 与原生数据 bank 分开汇报。

### 冻结编码缓存控制（运行前修订）

初次实际计时发现小批查询 overhead 不可忽略；原生 get_cost 每轮重复编码同一观测和 goal。增加所有方法共享的 encode-once 缓存条件，核对缓存后 direct/full cost 与原生 cost 一致，不把删除冗余 encoding 当成 selective 方法的收益。编码一次成本单列；CEM 总时间须计入一次编码，不能只报 predictor kernel 时间。候选与 promotion/calibration 协议完全不变。

### Stage A1 首轮 closed-loop（运行前，2026-10-02）

官方 TwoRoom 的 8 held-out episodes：20% TOP-M-SCREEN 离线 elite recall=96.86% [episode bootstrap 90.58,100]，INTERVAL/cap20%=95.93% [87.79,100]、实际重评13.08%；因此执行探索性 closed-loop。固定同一组 8 start/goals、seed=0、原成功判据、50 primitive-step budget。比较 CHEAP-ALL/N300、FULL-REFINE/N300、TOP-M-SCREEN/20%与30%、INTERVAL/cap20%、RANDOM-M/30%、LOWER-BOUND/batch64、CHEAP-ALL/N900（更大 cheap search 强参照）。所有方法缓存同一冻结 current/goal encoding，报告包括一次 encoding 与 selector 的完整 CEM/episode time；实际执行 native CEM elite mean，不能把最优候选 ID 当作 executed action。calibration 只用此前独立4 episodes，按 CEM iteration 固定，不用 closed-loop future labels重调。比较按 episode paired；样本小只作 pilot，不升 manuscript-critical claim。原生数据的 subset/native numeric drift 另做 timing audit。


## 代码可行性：不需要重写CEM

已审 stable-worldmodel `CEMSolver` 与 Fast-LeWM `get_cost`：

- CEM 每轮显式持有 `candidates / costs / topk_inds / topk_candidates`；历史 main 审计存在 callback，但本批使用的 0.0.6 wheel 没有 callback，使用 cost wrapper 记录 candidates/costs 并按原生 topk 复算 elite；
- Fast-LeWM `get_cost` 先对所有candidate做direct rollout；只有 `consistency_loss_weight != 0` 时才额外跑 `rollout_action_num_blocks_per_step` 得到decomposed terminal estimate；
- 因此 selective refinement 可以以很小改动实现：direct score全体 → selector返回candidate indices → 对该subset切片 `info_dict/action_candidates` 做decomposed rollout → 回填refined cost → CEM按混合后的cost选elite；
- cost wrapper 可以记录每轮 cheap elite、refined set、最终 elite membership、mean/std shift，不需要另写一套 planner。

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

CEM 对下一轮 proposal distribution 的更新只消费 elite candidate actions，而不是所有 candidate 的精确 cost。令 full high-fidelity evaluator 的 elite set 为 \(E\)，selective method 恢复的 elite set为 \(\hat E\)，两者大小都为 \(K\)。如果 \(E=\hat E\)，那么在相同 sampled candidate bank 下，**CEM 的下一轮 mean / sample-standard-deviation update完全相同**；非elite candidate 的high-fidelity cost可以完全不知道。

更一般地，若每个action-sequence向量 \(x_i\) 满足 \(\|x_i\|_2\le B\)，且两elite sets各错换 \(r\) 个candidate（对称差大小为 \(2r\)），则均值更新有直接界：
\[
\|\mu_E-\mu_{\hat E}\|_2 \le \frac{2rB}{K}.
\]
对二阶矩阵同理有 \(O(rB^2/K)\) 的扰动；协方差更新也因此随elite mismatch比例增长。这个推导很简单，**当前只作为待形式化/单元测试的设计依据，不登记为已证明论文定理**。

这使H-B的目标从“近似所有high-fidelity costs”转成更贴合planner的任务：

> **用尽可能少的 refined evaluations 保住 high-fidelity elite set。**

因此 offline candidate-bank 的第一指标应是 elite recall / symmetric-difference，而不是全体candidate的MSE或Spearman。若这个接口成立，后续理论与算法都围绕elite-membership uncertainty自然生长。

## 结果后的近邻重查（2026-10-02）

[ICML 2026 Depth over Fidelity in Fixed-Budget Noisy Evolution Strategies](https://proceedings.mlr.press/v306/wang26ff.html) 已深读方法/实验与残差池附录：以低开销 residual-bootstrap probabilistic elite membership 替代 hard ranking，保留更多 distribution updates；COCO、RL policy search、HPO，并有低噪声 probe-and-switch。它已经拥有 elite-membership probability、rank-instability gating 和 depth/fidelity trade-off 的相应 claim，不能归为我们的新发明。与 E13 的差异是 stochastic oracle 重复评测/软权重更新， versus learned visual terminal prediction 的系统误差/不同 fidelity 与 native CEM。与 E16 的差异是当前优化器 selection versus 购买真实环境经验后再训练模型。作为方法支点与强参照，不作自动关闭判断。当前 CHEAP-900 结果提示首先测整个 search budget，而不是继续调 INTERVAL。
