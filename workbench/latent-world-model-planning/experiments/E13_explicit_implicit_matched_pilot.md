# E13｜Planner-Stage Multi-Fidelity：候选筛选与高保真重评

- **状态：** RUNNING；两任务A0/A1、长短目标A2已完成，接续预测时域/搜索广度比较。
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

### PushT A1（运行前，2026-10-02）

原生 PushT A0 20% TOP-M-SCREEN recall=99.986% [99.958,100]，满足此前探索触发；12 factual suffix 正控全部成功，setter residual 非零单独审计。接续同8 TEST anchors、同8方法/seed/budget/原成功判据，不改selector。先cached actual GPU timing，并新增明确的cached/native cost逐值对照；随后closed-loop。离线bank采用原dataset current image，实际闭环采用restore后的实时image；二者差异明确记录，不能靠较高recall预言真实控制收益。

### A2：fidelity 的真实价值与强 search baseline（运行前）

8 pairs不足以区分小收益；PushT首轮全部方法8/8且无耗时优势。下一批暂不改selector，先测FULL scoring是否具有值得保留的真实价值。TwoRoom/PushT各64个25-step goals +64个75-step goals；整episodes互不重叠，排除旧12 CAL/TEST，seed61000，episode/start不按模型结果选。两个预定条件FULL-REFINE/N300与CHEAP-ALL/N900；同frozen checkpoint、同task input、30 CEM updates、25执行prefix、分别50/150 env-step预算、native成功判据。所有条件同encode-once cache。CEM搜索seed按episode/decision配对；不同N不称同candidate bank。样本量/goal跨度改变用于检测ceiling与真实compute-quality，不为挽救INTERVAL寻找窄场景。

每task/goal-offset分别报success、Wilson与episode-paired bootstrap差、time-to-success/env steps、含encoding的完整planning time。若FULL没有真实价值，不能仅凭恢复FULL elite宣称方法成立；若有价值，再找值得购买fidelity的设计问题。仍不关闭R2，不进入shared-head训练，不预先改变论文narrative。


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

### A2 factual controls 与计时混杂（补充运行前）

对全部256锁定的task/goal-range anchors逐一从public setter执行官方factual suffix，保留初始RGB、各状态维度的物理单位误差、wrapped角度及native success。25/75步全部保留，不依据结果筛评测起点。PushT只保证公开restore变量，不声称恢复完整physics memory。A2开始时GPU空闲，后续发现其他进程共卡；闭环成功读数保留，耗时降为非独占测量，不能用于speedup主张。独占timing需另跑。

### A3｜想象时域 × 搜索广度（2026-10-02，运行前）

推进P05/R2：长目标下，把计算花在更远的动作后果还是更多短候选？复用两任务released Fast及锁定g25/g75各前32起点，不筛失败；三方法H25-N300、H25-N900、H75-N300，合计384 episodes。均β=0/terminal latent cost/K30/30CEM，每次真实执行25steps后用当前pixel重规划，g25/g75的实际环境预算分别50/150。不改变数据/encoder/planner目标，也不把更长预测自动叫高保真。

H75把同一Fast的25步direct predictor递归3次；H25-N900与H75-N300每轮candidate-transition evaluations同为27,000，但实际batch/wall-clock可能不同，分开报。训练0、无router；native H1/H3正控及既有factual suffix恢复限制保留。每episode paired搜索seed66000+j*100+decision，reset seed66000+j；相同goal/method重放起点，horizon维度不同不能声称same candidate bank。source/config/helper/hash与各次nvidia occupancy记录写raw。

主读数：task×goal range的closed-loop success/paired help-harm与episode-bootstrap CI，原生最终distance和实际env steps；附计模型calls/候选×transition工作量与完整规划time。仅一个released checkpoint/task，32起点CI不是训练泛化证据。决策表（跑之前写）：H75胜H25-N900→长后果信息值得建更好的预测对象；H25-N900胜→优先改善候选/模型对长时预测的可用性，不盲加horizon；两者task-dependent→发展可复用结构/代价，而非挑task包装；都弱→对齐训练对象/goal geometry/任务代价等独立方法轴。raw `/tmp/latent-wm-runs/20261002-E13-horizon-breadth-RTX-s0`，完成自动复制持久cache；与E16 objective matrix分空卡运行。


### A3实际结果（2026-10-02，全部384episodes）

[完整config/hash/controls/summary](../results/E13_20261002_horizon_breadth.json)。H25N300/H25N900/H75N300，每组32：TwoRoom25=28/31/17、75=19/25/8；PushT25=31/31/5、75=6/7/0。H75−H25N300配对CI依次[-.5,-.1875]/[-.53125,-.15625]/[-.9375,-.65625]/[-.34375,-.0625]；没有把长预测直接当高fidelity。N900短与N300三macro的每轮candidate×transition相等，实际时间/完整episode计算不同。native allclose maxabs导航1.83e-4、操作1.53e-4，不声称exact0。零训练，不受E16optimizer问题影响。

解释限于此direct-prefix frozen backbone/terminal latent cost/CEM：递归误差、cost geometry、增加动作搜索维度都可能解释；Planning Limits在别的backbone/score上长rollout有益，不能推出“long horizon无价值”。下一步query proposal/cost或预测对象训练提供不同设计，不局部救refinement。


### A4：action trajectory parameterization强对照（运行前，2026-10-03 JST）

推进P05/R2：E17 goal-shuffled proposal几乎同正query，增益可能来自generic action prior/搜索结构，不能归因query。继承经典temporal action parameterization；iCEM的temporally correlated sampling属于成熟方法，不声称发明smooth planning，不称本prototype完整iCEM复现。此比较改变优化器动作表示，冻结WM/cost/query信息，和prediction fidelity、预测对象训练构成竞争设计。

同E17两Fast checkpoint、prepared两strata前16、seed68000、goal25/75各≤50/150envsteps，每25真实steps反馈，全部64anchors×4methods=256episodes。ZERO25-N300/ZERO25-N900 native50dim独立actions；LINEAR5-N300 native10dim（5×2knots线性interpolate成25×2，align_corners=True）；CONSTANT1-N300 native2dim repeat25。CEM H1/actionblock=k、K30/30iteration、initmean0/std1，cost输入用同exact normalized transform展开为原25真实动作序列、native MacroCost与fullsource actionnorm不变；elite-mean系数执行前用同transform。K5插值改变action-space支持与per-step方差/相关性，不假称equal exploration covariance。

正控：k25 identity、k1repeat、k5实际SWM CEM candidate/返回dimensions，cost执行transform一致，零候选各basis展开一致；native modelcost allclose；同lockedgoals，不挑成功episode。每anchor固定随机方法顺序，同decision seed；primary分task/range success、vs ZERO300/900的help-harm与episodepaired bootstrap CI；actualwallclock/candidatecalls/actionparamdim/realsteps分别计，不把params少直接称更少WM compute。

决策表（跑之前写）：generic低维结构已胜learnedproposal→升级为强baseline，原query增量重定位；只有queryproposal有效→补state-only head和更强训练；simplebasis仍弱→保留null，cost/预测对象/目标alignment实验继续。单releasedWM/16episodes条件CI，不是新论文或unseen WM episode证据。raw `20261003-E13-action-basis-RTX-s0`，E18结束后GPU0、data×compute之前，零训练。


### A5：共同初始plan的执行承诺/重规划频率（运行前）

对应P05/P08、R2/R5（R4是竞争解释，不预选）：E18频繁真实反馈FROZEN名义PushT5/16 vs E17整25执行14/16，但plannerseeds不同，需要公平同初始plan对照。先排除经典warm-start/优化重启，不把已有MPC原则称创新。

锁两Fast/同preparedg25/g75各前16/nominal；SEED78000，全部64anchors×4methods=256episodes，budget50/150 primitive steps。每anchor真实初始image/goal一次N300/K30/30/H25 CEM得到共同normalized25×2plan（seed78000+j*100），method复位同起点、首次执行同plan的5/10/25 prefix，早成功全保留。EXEC5-COLD / EXEC10-COLD / EXEC25-COLD / EXEC5-SHIFT-WARM。后续真实当前image重新encode、同goal/N300/H25；每decisionseed78000+j*100+steps//5。COLD新solver/initNone；WARM初始mean为previous normalizedplan向前移本次已执行5步，尾5补normalized0（不称物理zero），[1,1,50]；sampling std1/原native eliteupdate不变。budget末尾execute min(prefix,remaining)。

primary分task/range成功与vs EXEC25的paired help-harm/bootstrapCI；native distance/搜索次数/真实steps/模型calls/encode与wallclock另列。每轮预算相同但更密cadence可用更多总compute，不能说equal-totalcompute/wallclock。正控公共plan源码/hash、最初state/pixel replay一致、shift/pad/nativeinitshape与cost执行一致；不筛目标/方法，不偷偷让warm看到未来groundtruth。

决策表（跑之前写）：warm修复cold差异→提高所有恢复方法的强MPC baseline，不能把冷重启伪影写成新feedback机制；不同commit仍稳定影响utility→扩两seed/backbone，分辨优化、planned tail、feedback表示/hidden velocity；无差→保留旧跨run差异未复现，转向data/objects/querycost，不救narrative。是经典强对照与方法生长pilot，尚无paper claim。raw `20261003-E13-commitment-cadence-RTX-s0`，A4后GPU0，先于已锁data×compute；data实验不会取消，只有执行顺序改变。

### A4完整读数（2026-10-03）

[完整config/hash/controls/summary](../results/E13_20261003_action_basis.json)，256episodes/16,539真实steps；ZERO300/ZERO900/LINEAR5/CONSTANT1，导航近=13/15/14/8、远=10/14/14/9；操作近=14/16/15/7、远=3/4/3/0，每组16。LINEAR5导航远相对ZERO300 +4/16，pairedCI[-.0015625,.5]；与ZERO900同14个成功但help2/harm2、CI[-.25,.25]，不称等效。操作远未改善。CPU原生k25/5/1各30costcall、展开input50dim/return50/10/2全PASS；nativecost最大abs1.83e-4。经典support/方差/相关性改变，单plannerseed，无novelty/WM未见episode/墙钟加速主张。后续不再局部调knots救故事，A5共同初始plan与data×compute分别检验部署接口和训练条件。

### A5全部实际读数

[完整256episodes](../results/E13_20261003_commitment_cadence.json)，同commonplan/state/pixel初始误差0。EX5/EX10/EX25/EX5warm：导航近10/9/13/12、远7/6/10/11；操作近5/3/14/4、远2/0/3/2，每组16。操作近warm−EX25=−10/16、pairedCI[-.875,-.375]；warm并未修复丢失，不支持单纯coldrestart解释。已知terminal25score/execute5时间失配（S24）与反馈latentstate/optimizersearch是竞争解释，不能直接说velocity遗忘或feedback普遍有害。导航还有physicalclipping但scoringraw的接口混杂。R3cost（已补execution动作评分）与R4固定cadence observer均已锁卡，保留母问题不把cadence原理改名新贡献。

### A6：Fast screen → released LeWM reference（2026-10-03，GPU运行前）

推进I08/R2/P05。A0同checkpoint的self-consistency并不等于更可靠的动力学；A2增加一致性评分未改善utility。现在直接测试两种预测对象的candidate筛选是否互补，不再调self-consistency系数。继承Fast直接action-prefix与LeWM递归预测，后者只称reference，不预设其为真值或更高质量；各自表示的latent distance不能跨模型相减。

两个冻结released checkpoint、各自encoder/goal/actionnorm，same physical candidate bank。prepared两task×g25/g75前16=64起点，SEED81000+j*100；每anchor从公开state复位得到一张真实current image和同goal image，不输入HDF5过去图像/hidden velocity。官方LeWM HF history capacity3不是要求3张真实输入，原生get_cost允许T1；递归ctx1→2→3，5个5-step macro共25真实步。Fast为同current直接25-step prediction。TwoRoom双方score physical clip[-1,1]后的实际动作，PushT双方identity；CEM保留raw normalized elite mean/update，不把score修复混成改变优化器。Fast N900/K30/30 native CEM，固定捕获iteration15的900候选及其physical action序列，不按LeWM结果重新选bank。

先分两个fresh Python phase避免Fast/LeWM同名pickle module冲突：Fast产生bank与cheap terminal costs；LeWM仅读取相同bank、缓存current/goal编码并用5-step递归score。cheap排名TOP与固定随机RANDOM promotion分别取10/20/30/50%，参考elite K30。主读数为参考elite recall、所选动作与LeWM全bank argmin一致率、LeWM自身cost内selected regret、实际promotion fraction；按task/range汇总episode bootstrap CI。原始cost、rank、candidate IDs、每次promotion均保存。LeWM cost regret不是环境selected-action regret，也不是跨latent MSE。

陽性对照：两个checkpoint strict keys/hash、相同physical candidate SHA、current pixel/reset误差0；LeWM T1 cached recurrence与native get_cost全候选/小batch allclose、六预测frames；无训练/goal未来/branch outcome；cost为finite且batch/subset评分一致。噪声地板：单released checkpoint/单候选seed/16anchors条件CI、预训练episode未见性未知、PushT公开restore边界。真实timing仅在独占空GPU，同步CUDA、warmup后full与selected batch各8次重复，编码时间另列；calls比例不冒称墙钟加速。

决策表（跑之前写）：TOP在20–30% calls保持≥90% reference elite→进一步测同bank真实candidate后果或同预算closed-loop，只有reference确实改善控制才发展Elite-Preserving CEM；cheap/reference差异大且TOP recall低→考虑共享双head/决策校准/sentinel，不能从一个bank关闭R2；差异小→测试更好的预测对象/训练与任务cost，不包装无价值refinement。保持全64anchors，不筛方法或成功case。新源two_backbone_bank.py，raw `20261003-E13-two-backbone-bank-RTX-s0`，PushT derived object放HF latent-wm-derived并记录strict metadata。GPU前仍需CPU原生controls/root审阅；不依赖DeepJEPA未release代码，不新增大framework。

A6最终GPU前补记：capture_call_index15为0-based第16次，非1-basediteration15。root全文审200行，两个fresh CPU真实nativecost控PASS（LeWM差0/current1+predicted5frames；Fast max6.1e-5且allclose），原生N900/K30/30捕获[1,900,1,50]、expert sourceprefix仅用于控、不加candidate、all64预定bounds有限。两phase raw/durable独立basename `20261003-E13-two-backbone-fast-RTX-s0` 和 `20261003-E13-two-backbone-reference-RTX-s0`，避免通用bank目录冲突；script SHA c8ab31af3954c83824029c3278b86f7b988d2fbd0759ae9d07f047c0ab89eb05。4metrics保存2000bootstrapCI。GPU0已空，将由free-wrapper复核后运行；此时尚未GPU读数。

A6工程重试（未有reference科学结果）：Fast64bank完整sealed/durable；LeWMphase在import sklearn失败，旧reference failure与used源码保留。仅在isolated `/home/xiang/.cache/latent-wm-python-deps/sklearn-1.5.2` 安装scikit-learn1.5.2/scipy1.13.1/joblib1.4.2/threadpoolctl3.5.0，不修改正在运行的venv或NumPy/torch；确认导入后PYTHONPATH限定新进程，same sealed bank/source/seed/normalization formula，raw重试独特 `20261003-E13-two-backbone-reference-RTX-s0-retry1`，不能把import failure算method负结果。

重试前精度补记：首isolated安装的target复制阶段被提前import生成的pycache打断（shutil FileExistsError），失败log保留；改用节点local `/tmp/latent-wm-python-deps/sklearn-1.5.2-complete` 全部安装退出0后再import，四包版本与NumPy1.26.4核对，完整CLI/LeWM入口预控仍在完成。64bank独立hash/seal/源审计通过、均900不同physical候选；Fast部分scores有ties，ID不同不是质量差。保存promotion IDs并核对实际小batch参考评分与全900评分：仅timings/scorer新增诊断，producer/Reference/native_check/physical/normalize AST与sealed used完全不变，CPU45call/tie/fail-halt控通过；新source SHA `c0cfbfdf78cc53aea37bad293e18f51eb3bf1a6fcddc129483b85801fa37acb1`，旧bank不重生。依旧只测候选argmin/reference ranking，不是CEM最终elite-mean动作；TwoRoomclip不可逆，旧bank不能重建rawelite参数。完整GPU参考通过前无新读数。

### A6完整读数与A7实环境候选质量（整批执行前）

A6 reference-retry1已complete64bank，无failure；独立复算640policy/全部raw-durablehash/180个实际subset评分一致性均PASS。TOP20%参考elite recall导航近/远=.777/.469，操作近/远=.510/.190；RANDOM20%分别.208/.196/.163/.217。TOP30%也未恢复90%elite。特别是导航near TOP20% mean reference-normalized-regret .749，RANDOM .018；高recall和低argmin regret不是等价读数，保留全部16anchor与CI，不筛离群。四strata参考900/90/180/270/450批次中位42–44ms，未见batch缩小的实际耗时收益，不把20%calls称speedup；此参考成本不是实环境真值，科学主张0。

A7只问同bank两个模型各自argmin的实际候选质量，不训练、不继续调selector。固定全部64anchors/四strata各16，Fast与LeWM各执行所选physical25序列，FACTUAL独立读原HDF完整25/75步source suffix，仅阳性、不用于选择；最多6400真实steps/192branches。每branch freshenv+同seed/publicstate，保存每primitive state/pixelhash/reward/success和首末pixels，跨method初始state/pixel必须完全相同。g25 primary实际success、paired help/harm/2000bootstrapCI；g75 success原样报，25步期末native distance与纯位置/wrappedangle仅proxy，不称optimal regret或未来任务utility。单argmin不是CEM最终elite均值；双方都在Fast条件bank上，不排nativecontroller胜负。

四固定j0/task×range同动作fresh重复的真实CPU预控全trace完全一致，共154steps；起点pixel0，Push相对dataset publicstate max差.411/.345，保留setter/contactmemory边界，绝不宣称dataset真实隐藏state精确恢复。factual失败不筛掉起点。127行源码 `candidate_quality_cpu.py` SHA `f693e79dcc57e863a599d1620b01c3a4938e905b03ae02d1f56449540aca985a` root全文审，CPU全部前控已durable `20261003-E13-candidate-quality-cpu-controls`，完整raw/durable `20261003-E13-candidate-quality-CPU-s0`。决策表（跑之前写）：LeWM真实近goal选择有益→才考虑同wallclock/nativeelite更新的闭环；只有模型排名不同/真实无益→换预测对象或数据训练，不救TOP threshold；两model均差且factual好→检验candidate支持/评价几何；factual不佳→报告reset范围、保持全部anchors、不把失败全归模型。当前尚未整批A7。


2026-10-04上传核对：A7已complete64anchors/192branches/5545steps，198个raw/durable文件逐SHA相同、各method/stratum均16、所有trace SHA/selection IDs/初始pixel/summary success计数复算通过。近goal Fast/LeWM导航13/13、操作15/11（配对CI[-.5,-.0625]）；远goal7/7、2/1，仅25步候选后果，不能当长任务闭环。FACTUAL四组16/16。完整独立trajectory与CI审计仍pending；[portable结果](../results/E13_20261003_candidate_quality.json)。参考模型没有被证明具有更好真实候选质量，不继续把elite recall当control gain；科学主张0。

## A8：固定目标几何中的预测对象对照（2026-10-05，运行前）

对应R2/R3、P04/P05与I08，不改变已审paper narrative。三seed分阶段value远goal收益重复，但value geometry×CF MIX未成立；Push单模块冻结也没有保住发布控制。不继续self-consistency promotion阈值或把freeze+mix换名。最便宜下一比较直接复用Fast-LeWM官方action-prefix组件，在固定PRED/VALUE前端中比较DIRECT多horizon与LOCAL一步训练/递归使用，先区分预测对象与既有目标几何是否互补；direct prediction本身不是novelty。

四cell PRED/VALUE×DIRECT/LOCAL，两个geometry sources与E20Stage4一致（ABS5650、SEP value phase2825，prior目标/budget不同，不能作puregeometryobjective因果）。encoder/projector所有params与BN frozen；Fast官方Embedder(state-conditioned causal transformer3layers6heads192)与ARPredictor6layers/2048hidden、pred_proj MLP统一一个保存CPU初始化seed113000，完整head同capacity/初始SHA，不加载发布Fast已训权重。两对象共同使用current单frame latent（原35stepclip第10步），五真实未来15/20/25/30/35与physical actions10…34，同样100episodes/5795合法starts；DIRECT从同current与前缀一次预测五future，LOCAL对五相邻真实latent/action作一步teacher target，部署递归五次。不给DIRECT future真实states，不把LOCAL训练teacher信息当部署feature；两者部署均T1，不与旧LeWMH3对比时伪称historymatched。

固定phi先对9295训练frame FP32 encode形成node-local featurecache，source/image rows/hash/geometryprior/frozenBN/no-grad保存；cache仅训练事实obs，no physical state/no evaluation goals/outcomes。缓存FP32执行与旧pixel-bf16训练、DIRECTprefix位置和LOCALsingleprefix等差异列账，不冒称Fast完整数值复现；官方已具有jointdense训练，本pilot为固定geometry port。每cell B128/2825 freshAdamW5e−5WD.001/clip1/bf16，loss五真实targets平均MSE，无SIGReg（phi固定），共361600clips与1808000futuretargets；两对象forward compute不同，时间/VRAM另列，不当equalFLOPs。没有新增sim数据或CF混入。

阳控：严格geometry源拷贝/immutability、共同head保存初始exact、CPU/CUDA实际B128五future/action索引不跨episode；DIRECT扰动后缀action不能改变前缀prediction（eval），LOCAL teacher prediction独立手算，所有trainable head finite gradients/freshopt1step、frozenphi全tensor/BN不变；actual25step cached terminal cost与完整encode+五prefix/五递归reference一致、批次/单candidate评分容差明确；任何失败halt并留原artifact。上述预控完成/hash冻结才铺四训练，不以emptyGPU代替校对。

主读数：固定全部原新48两接口sameH25EX25/300-30-30/最多100step，全state/动作/goal初始pixel guards与success16px independentlytrace复算、paired sameanchor效应，near/far分层；strong oldABS/valueSEP/fullRC发布参照保留，发布data/训练不同明确。离线held12新branch排序/真实endpoint只辅助，不以model elite/MSE代控制。noise：一exploratory训练source、共享48开发tasks，不筛seed或目标；有真实方法增益才扩三source/第二任务及goalpolicy近邻。

决策：DIRECT/LOCAL只在一个geometry内有明显收益→扩完整seed与二task，进一步辨coverage/表示用途/预测对象；两者均改善→保留更强成熟预测baseline再找增量；都不胜充分支点→转goal-policy/层次/复用与变化后的模块更新，不调prefixλ/少数queries救故事。母问题开放，不选择新论文主旨，不升science claim。节点localcache、四独立单GPU任务，HF checkpoint/raw durable unique20261005-E13-object-{PRED/VALUE}-{DIRECT/LOCAL}-A100-s0；仅实际empty slots，featurecache只各geometry生成一次再复用。

A8实际接续2026-10-05：四cell各2825已全部DONE，源geometry/frozen所有参数与BN/officialFast共同head容量与保存initial exact/optstates×2825/finite moments/firstbatch与全部2825步sampler精确再生、361600clips/1808000future targets经独立endpointaudit PASS，见E13_20261005_predictive_object_endpoint_audit.json。actual CPU/CUDA B128四precontrols、DIRECT suffix扰动不改prefix、LOCAL目标手算/freshstep、fullactualpixel Cost vs五前缀/递归手算bit-exact0、batch/subset容差全PASS，见E13_20261005_predictive_object_preflight.json。features9295事实帧FP32 source/hash/node-local cache完整保留，不含goal/outcome。

首CPU预控因Model.training名称与nn.Module.training布尔字段冲突在loss/optimizer之前停止，两原队列与used source/failurelog完整保留20261005-E13-object-{geometry}-cpu-preflight，无训练/效用输出。仅rename训练模式方法为training_mode，增加phi-cache hash强制相等；source/prior/actions/features未改，原features producer sourcehash与最终trainer hash分开记。新CPU/CUDA retry1才是正式启动依据，预控后源码冻结；不是数值失败重抽数据。

四训练固定终点之后完整same48/两接口384实际RTX闭环已启动：PRED physical0 PID3590795、VALUE physical1 PID3590796，logs/tmp/latent-E13-object-{PRED/VALUE}-RTX-control.log；actual source checkpoint/strict state/原warm state-pixels守卫已通过并产生真实轨迹。LOCAL与DIRECT各自同T1，旧LeWM H3与RC发布训练差别单列；两geometry source prior budgets不同，不以跨geometry原数称pureobjective causal。整批未齐，不筛prefix或partial结果，不称novelidea，科学主张0。

### A8完整闭环结果与A9独立源重复（2026-10-05，追加运行前）

[A8全部384](../results/E13_20261005_predictive_object_control_results.json)八groups/全部48/native成功/trace/checkpoint/source独立审计PASS。native PRED-DIRECT31、PRED-LOCAL29、VALUE-DIRECT39、VALUE-LOCAL22；physical20/21/44/19（各48）。DIRECT−LOCAL withinPRED native+4.17ppCI[−6.25,14.58]、physical−2.08[−10.42,4.17]；withinVALUE native+35.42[22.92,50]、physical+52.08[37.50,66.67]。oldH3 SEP32/33与RC H1ON38/34（native/physical）保留：VALUE-DIRECT相对SEP+14.58ppCI[0,29.17]、+22.92[8.33,37.50]，相对RC native+2.08CI[−12.5,16.67]、physical+20.83[6.25,33.33]。oldSEP有不同futuretargets/sampling/H3；RC发布training unmatched，不把参考差叫isolated因果。所有train/coreinit、futuretargets与loss手算/frozenphi、实际控制都已通过audit。

这是可继续研究的交互线索，不能直接claimgoal表示一定非Markov、direct在所有goal表示更好或VALUE+Fast是首次。Value-GuidedJEPA/Fast/TemporalStraightening/TD-JEPA/ProWorld等均有ownership，当前只是shared-capacity matched port的一个source/开发48。不要把弱LOCAL作为solebaseline或把physical优势当原native普遍优势；两个geometryprior目标与compute不同。后续问题是goal-comparable结果空间与可组合动态状态是否必须相同、预测单位怎样与表示用途匹配。该问题值得关心，不把论文锁成某个TwoRoom起点/某个horizon或简单组件组合；仍不切paper叙事/PROPOSED/science0。

A9先重复原source1/2的四cell，共八新训练2825与完整768控制，source0原结果全保留。使用既有same100/完整source1/2 ABS5650与SEP value phase2825，不重训或筛phi；新head初始化113000+seed/采样113100+seed/训练Torchseed=seed各pipeline独立，但每source四cell的head容量与完整初始tensors/clip indices保持common随机数。全部训练模型在HF，CPU保存init→CUDA继承；FP32 featurecache各geometry/source9295原事实帧、同5795starts，所有语义/physicalactions/目标/单frame/deploymentbudget同A8。新源码版本仅加入明确seed/source/unique artifact字段，不改A8 frozen源码与任何已报数字；CPU/CUDA同actualB128/手算/causal-prefix/grad/BN/nativefullcost0控全过才跑。四个实际空A100slots各source/geometry独立LOCAL/DIRECT顺序，不依赖跨节点通信；features共享nodepagecache，保存真实I/O/profile，不声称formal4并发吞吐。

确认读数仍是两个geometry内DIRECT−LOCAL，并事前锁定interaction差值(PRED与VALUE预测对象收益之差)；near/far与总体全部报告、paired source+anchor bootstrap、同48共享开发task，≥3source不是144新task。数据/表示prior与head随机数都明确，主张不越过这些条件。下一history输入控制要保持训练target/容量/实际warm信息一致，操作task需另actualfactualcache/目标geometry可用性阳控；两者不是已启动/已跑通，不能先给数字。若重复不稳先读模型误差/候选支持/目标语义而非调λ网格；若稳定面对旧H3强SEP仍有益，再扩history/第二task/不同预算与完整近邻定位，仍先人审真正新narrative。

A9执行校对：八新训练已全部2825终点/独立audit PASS（E13_20261005_predictive_object_repeat_endpoint_audit.json）。首版重复controller的train seed被decision seed覆盖，整批source1/2闭环输出排除，原used source/log/failure保留，见CLAIMS作废记录。A8与八训练未受影响。修正v2静态AST确认train_seed在evaluate体内无赋值、逐interface/anchor强制r.SEED/checkpoint/config相等，planner_seed独立。新raw/durable `20261005-E13-object-repeat-v2-control-{geometry}-{arm}-{interface}-RTX-s{1,2}` 完整768重跑，同全部48/targets/预算/成功定义，没有新训练数据或科学读数调整。


### A9整批完整结果（2026-10-05）

新v2全部768 DONE，原A8+v2共1152/24groups全trace/初始state/native成功/源hash与scaler独立审计PASS，[三source结果](../results/E13_20261005_predictive_object_three_seed_control_results.json)。PRED DIRECT/LOCAL native31/42/36 vs29/39/35，physical20/33/31 vs21/30/26；VALUE39/40/34 vs22/13/32，physical44/41/34 vs19/13/32（每source48）。withinVALUE平均native+31.94pp CI[4.17,56.25]、physical+38.19[6.25,63.19]；native交互+27.78[.69,52.08]，physical+33.33[−4.17,62.5]。source2 VALUE仅+2/48、physical交互负，不能把平均/CI包装成各seed稳健机制。

VALUE-DIRECT对更强旧H3 SEP native+5.56pp CI[−12.5,21.53]、physical+9.03[−12.5,27.78]；对发布RC native−.69[−15.97,13.89]、physical+11.81[−5.56,27.08]，都未稳定领先。整体信息是shared Fast LOCAL对VALUE几何明显脆弱且有source异质性，DIRECT缓解不等于新的强baseline胜利；不claim非Markov/编码漂移唯一原因，不选择新paper narrative/science0。首版错误控制器整批完全排除，不使用其partial读数；原权重/checkpoint未改。下一独立方法轴E14G0官方GC-IDM/同goal零horizon GCBC/PAIRWISE：判断事实经验和表示怎样被使用才能产生控制，history/第二task仍须精确预控，不做prefixλ救援。
### A10：强递归训练对照（2026-10-05，运行前）

推进P04/P05与R2：A8/A9的LOCAL只接受teacher一步训练，不能从它的弱表现断言递归预测对象或value geometry不适用。增加成熟OPEN-ROLLOUT五步BPTT训练，继承同官方Fast head、容量、初始化113000+source、采样113100+source、same100事实5795starts/当前10+未来15…35/25动作、frozen FP32 phi及全部五个未来target。六个PRED/VALUE×source0/1/2独立单卡jobs，各2825updates/B128/AdamW5e−5/WD.001/bf16/clip1/noSIG，与已完成DIRECT/LOCAL对照相同最终曝光。OPEN每步输入前一步预测且不detach，所有五步监督；未来事实latent只作target，不能进入预测递推。递推BatchNorm/dropout调用方式与teacher/direct不同，记录此实现设计，不宣称纯计算或BN-only因果。

预控先实际CPU/CUDA B128手算五步递推loss、早期prediction收到末步loss梯度、目标改动不能影响预测、freshopt所有参数finite/step1、frozenphi与BN不变、eval batch/subset与完整五步cost；全部通过才训练。失败保留原run/source/log。保存共同initial/firstids/最终RNG/完整AdamW/参数SHA，独立终点校对后才启动部署。主读数原完整48/near-far/native与physical合法CEM/100steps，递归部署五步，相同candidate budget，全部六source/geometry固定终点保留；不能按表现挑epoch/seed。paired source-anchor CI及强GC-IDM/GCBC、oldSEP/fullRC参照，预测MSE只是辅。

决策表：OPEN吸收DIRECT收益→将此前线索解释为训练与部署条件差距，并保留强递归baseline；OPEN仍弱而DIRECT强→继续检查预测对象是否保留任务进度/动态状态，不跳到普适非Markov结论；两者均不胜成熟策略/RC→从复用、经验监督及history设计探索实际增量，不救同selector。只补现有方向的关键强对照，不更改人审优先、PROPOSED或scienceclaims0。训练snapshot仍HF，raw本地，六run全部报告。

A10执行覆盖pending：六个2825终点全DONE，12actualCPUCUDA B128预控及独立六run共同初始化/firstids/finalRNG/fulloptimizer/frozenphi审计PASS，见E13_20261005_rollout_endpoint_audit.json；十二控制组576已锁，source0 GPU3实际运行，source1/2分别等原history0/1空卡。实际每geom先CPUCUDA完整cost手算exact/全部48warm守卫过才闭环，没有给效用结论。
