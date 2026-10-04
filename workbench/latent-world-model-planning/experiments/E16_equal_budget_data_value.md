# E16｜Planner-Boundary Branching (PBB)：planner-aware data acquisition

- **状态：** RUNNING；TwoRoom Stage 0 完成，接续原生 PushT 与 Stage 1。
- **对应：** I12 / R1。
- **来源：** S2/S4/S10–S12；这是方法探索卡，不预注册结论。
- **阳性对照：** 等量IID追加数据应至少能在充分训练下被模型读取；same-state branch bank的隐藏outcome在“oracle selector”中给出可达上界，但绝不作为可部署selector输入。
- **噪声地板：** train seed、branch-bank生成seed、eval/planner seed分开；先用单seed探索找effect，再用独立训练seed确认。
- **决策表（跑之前写）：** decision-critical acquisition好→扩第二task/seed并拆score；global uncertainty/coverage更好→沿更强策略发展；所有数据追加差不多→查模型容量/训练量/branch budget；没有提升→换R1方法，不硬写“无效”。

## 核心问题

固定真实环境交互/branch-query预算时，**哪一条新经验最能改善latent planner的实际决策？**

第一版只改data acquisition，不改backbone/loss，目标是把方法杠杆隔离清楚。

## Stage 0｜可重置branch bank

优先TwoRoom/Wall，随后Push-T或Cube（取决于E00是否支持可靠state restore）。

对一批`(state, goal)`：
1. 从当前planner保存candidate action sequences与cheap predicted scores；
2. 保存可重置simulator state；
3. 离线为实验基础生成一个**隐藏branch bank**：同state下执行多个candidate prefix并记录真实outcome/transition；
4. 每种acquisition策略只能“揭示”自己选中的branches，训练数据budget按真实新增environment steps计。

branch bank只为可重复比较；selector不能偷看未购买的真实outcome。

## Stage 1｜等预算selector矩阵

探索阶段先1个task/1个train seed，预算按E00实测调整。至少包含：

1. **NO-ADD**：基础数据；
2. **IID/RANDOM**：普通追加；
3. **COVERAGE/EXCITATION**：低覆盖或局部动作多样性优先；
4. **GLOBAL-UNCERTAINTY**：模型预测分歧/误差proxy优先，作为OnlineWM-like control；
5. **TASK-RELEVANT**：当前goal rollout相关的uncertainty，作为ToIA思想control；
6. **DECISION-CRITICAL**：候选selection relevance × rank instability × predicted consequence span。

可加**ORACLE VALUE**只作上界：用隐藏branch outcome选择最能减少真实candidate regret的数据；不能进部署方法。

### 2026-10-02 Stage 1 基础训练与正控（运行前）

先训练有限数据模型，避免在已见大量数据的 released checkpoint 上把新预算作用压到噪声内。官方 TwoRoom 中以 seed=20000 选100整 episodes，排除此前 E13 的12 episodes；另选48个整 episode隔离的goal anchors供评测，训练不能消费其图像/transition。基础action statistics只来自这100 episodes。100是起始数据regime，非最终论文范围。

seed=0；从随机初始化开始，官方 LeWM 18M tiny ViT/history3/frameskip5，4帧@0/5/10/15，预测全部3个移位目标的MSE + 0.09 SIGReg（17 knots/1024 projections），AdamW lr5e-5/WD1e-3、clip1、bf16、batch128。10 epochs先测；constant LR 与自写小循环是明确的pilot偏差，不称完整Lightning/scheduler复现。边界clip不padding，记录有效样本、steps、loss、representation spread、GPU时间/显存、I/O。若正控弱，检查训练曲线并沿官方更长训练配方续训，不能据欠训练宣布数据假设失败。

native LeWM horizon=5 macro actions、每macro5 primitive、receding_horizon=5，50-step budget；真实history取t−10/t−5/t，过去2个action blocks仅作因果context，未来5个candidate blocks合计25steps。必须给native rollout拼接past2+future5，不能把带3帧history的5-action tensor误当25step forecast。缓存所有方法相同的冻结当前/goal encoding；先与native get_cost核对数值与5步rollout长度。先16个预定eval anchors比较released正控与基础模型；正式acquisition效果使用全部预定48 anchors及新的candidate-outcome审计，不以正控结果挑起点。

随后仅用于acquisition的3个bootstrap predictor heads共享基础encoder/projector，在基础数据feature上训练；不把独立模型的未对齐latent variance当GLOBAL-U。主模型所有policy沿相同基础checkpoint继续训练原始objective，固定optimizer步骤。购买时完整保留 NO-ADD、IID、uniform common-reset、coverage/excitation、GLOBAL-U、TASK-U、PBB；具体预算/训练步/anchor pool在查询前锁定。隐藏分支结果只对已购买数据开放。

基础训练首轮：560 updates / 167.89 s，peak allocated VRAM12.57 GiB，16 anchors success3/16；released正控仍在完成同组16起点。loss仍下降（末段pred MSE约0.18），不据此判采集价值。**续训前修订**：同100 episodes/同16正控/同48评测anchors、相同loss/lr/batch，resume到总30 epochs（1680 updates），不新增数据。旧checkpoint未保存RNG，首次resume明确记录dropout RNG restart；随后保存RNG。训练不足是待核对混杂，不能作为PBB正/负证据。

### Stage 1 首次 equal-data pilot（查询/训练前）

- 以总30 epochs基础checkpoint为统一起点，先1 train seed；本阶段是离线branch-bank data-value simulation，必须分别报告每policy消费的逻辑steps与生成整个bank的真实总steps，不冒充线上查询成本。
- 3 bootstrap prediction heads从同一基础predictor初始化，共享冻结encoder/projector；各自按整episode bootstrap训练500 updates（MSE原3移位目标，encoder不更新）。只用于acquisition，主模型训练objective仍完全不变。encoder feature cache保留版本/hash。
- 64 acquisition anchors从基础100 episodes内抽，真实历史/goal图像均已在基础经验中。native CEM N300/K30/30 iterations；固定取中间iteration15，避免选择器不同CEM阶段导致额外变量。3 heads + primary对同一candidate population给cost/terminal estimates。
- 每policy固定新增2000 logical steps=10 anchors×8 branches×25 controls；branch末端观察额外保存但不算新action。NO-ADD与各方法固定600额外gradient updates/batch128、同基础optimizer/seed、原MSE+.09SIGReg。每条25-step追加clip滑窗@0/5/10/15，末端未使用的第4 action block允许0-padding；三个预测目标必须全部位于已购买25-step范围，不加入decision loss。
- IID：排除base/eval/旧E13 episodes，从80个新factual episodes各买25 transitions；UNIFORM-COMMON-RESET：64 anchors中均匀选10，same-state CEM population中均匀8 prefixes；COVERAGE：共享latent的局部低密度state + action-prefix diversity；GLOBAL-U：共享latent terminal variance；TASK-U：goal-cost variance；PBB：elite-membership entropy×cutoff proximity×terminal diversity。其余两uncertainty策略也各买8最高uncertainty prefixes。UNIFORM是common-reset data思想参照，不声称完整复刻FIRM architecture/loss。
- 先完成所有public selection ledgers、锁hash，再生成各policy所需branch的union；selector此时不能读取尚不存在的hidden outcomes。生成顺序不按模型预测优劣排列。policy训练只载入自身已买keys，NO-ADD不得读任何追加branch。重复reset/state/pixel一致性先留控制。
- 主读数：全部48预定未见训练episode goal anchors的closed-loop success（50-step budget、native成功判据）/相对NO-ADD提升/每1k新增logical steps；episode paired bootstrap+Wilson。小样本单seed不升L2。real candidate regret另建同candidate/同真实utility的评测bank，未生成前不能用model score regret替代。
- 决策：若所有方法都随600步大幅改善，先查优化量；若uniform/uncertainty优于PBB，直接沿强方法理解数据痛点；若有稳定增益，再扩3 seeds、PushT和预算。不会只报最好selector或只保留成功seed。

## Decision-critical score的最低实现

### 2026-10-02 独立确认批次（seed 1/2 运行前）

首轮全部七方法保留：NO-ADD 9/48，IID 17/48，uniform 17/48，coverage 18/48，GLOBAL-U 24/48，TASK-U 11/48，PBB 19/48；这只是一次 pilot，没有 PBB 优于强基线的证据。相对 NO-ADD，GLOBAL-U 帮助15/退步0，PBB帮助14/退步4；尚未做独立训练seed确认。

下一批固定 seed=1,2，各自从随机初始化、100整episodes split、30 uninterrupted epochs开始，重新生成48评测anchors、3 bootstrap heads、64 acquisition anchors与全部七policy密封ledgers。确认训练保留 **NO-ADD / UNIFORM-COMMON-RESET / GLOBAL-U / PBB**，均600 updates、2000追加logical steps；不按后续结果增删种子。先报告每seed配对结果，再报告seed间范围；episode bootstrap不能冒充train-seed置信区间。seed0首次resume的RNG偏差保留。独立单卡，硬件逐run记录，A100/RTX计时不混表。

并行补全部48 seed0评测起点的factual-suffix阳性对照：public setter后执行25个官方动作，记录成功、初始RGB/position误差、终点position误差；不剔除失败起点、不改变已经锁定的主读数。任何恢复异常先降级对应解释。随后在统一candidate bank上测真实动作后果，不用模型score代替真实utility。

不要先训练复杂acquisition network。可从：
- CEM top-2 margin / elite-cutoff margin；
- 多个bootstrap prediction head或轻augmentation下的Kendall/elite disagreement；
- candidate terminal/progress prediction spread；
得到可计算score。

高score state选择2–K个相互竞争candidate prefix执行。预算一律按新增真实steps/reset成本报告。

## 训练与读数

### Training
- 固定基础dataset/model/optimizer steps；
- added transitions数量相同；
- 第一轮保持原LeWM objective；
- 如果RC-aux family已跑通，可做第二objective确认，但不作为开工前置。

### Primary
- closed-loop success / real task cost；
- success gain per 1k added env steps；
- held-out goal/start transfer。

### Planner-facing
- 固定candidate bank上的selected-action regret；
- elite recall / elite order；
- acquired states上counterfactual action-effect error；
- 改进来自“有更好候选”还是“候选排序更准”。

### Data accounting
- environment steps、reset次数、branch count；
- state/action coverage；
- training GPU-hours；
- selector本身wall-clock。

## First-wave规模

E00后再填绝对小时数。研究逻辑：
- 探索：5–6 selectors × 1 seed × 1 task；
- 若有signal：保留top 2–3 selectors，≥3 train seeds；
- 确认：第二任务族（导航→操作）+ 2–3 acquisition budgets；
- 最后才补最强近邻和消融。

这些job天然单卡独立，符合多GPU弱互联条件。

## 最强近邻与exact delta

### FIRM/SPARK压力测试

**FIRM-WM control：** 若能获得其数据/实现，则比较“固定每个state均匀K branches”与PBB同等branch budget；若代码尚未公开，至少复刻最小common-reset uniform-branch data protocol，不复刻其完整typed recurrent architecture。

**SPARK cross-domain warning：** critical-state dynamic branching在LLM agents已有ACL 2026论文。不要写“我们首次在critical states branching”；只写visual latent-WM acquisition的具体接口与实证增量。

**RMWorld/dual-control warning：** value-of-information与task-risk active trials也已有先例。PBB若只是uncertainty×task weight没有独立candidate-boundary作用，不足以成新贡献。

### Direct neighbors


- **OnlineWM**：active query当前predictive weakness + same-state causal contrast；我们把query价值放到planner candidate-selection boundary。
- **Task-Sufficient WM / ToIA**：task-relevant information acquisition；我们针对同state competing action branches与candidate rank flip。
- **TOM / Policy-Aware Simulator Learning**：policy/strategic-region model learning；我们研究visual latent MPC的具体candidate interface。
- **Beyond Visual Quality / D-JEPA / AD-WM**：candidate selection/decision alignment；我们第一版改**数据采集位置**而不是decision loss。

最终写“首次”前必须再专项检索；当前只把这些差异当可证伪research hypothesis。

## 结果
2026-10-02：[原生 TwoRoom 结果](../results/E00_E13_E16_20261002_tworoom_native.json)。8 anchors × 8 branches=64条；含重复控制88次reset、2200 branch/replay steps，24次同动作重复 state/pixel 误差全部为0。12条官方 factual suffix 重放误差为0，success阳性控制12/12。240个 held-out CEM banks 的 public PBB ledger 使用 direct/decomposed cost proxy；每 bank 选8个不同candidate，屏蔽文件读取、变动独立隐藏标签均不改变选择。只有接口/输入隔离证据，未称独立 ensemble，也没有数据效用或 regret 改善证据。

PushT 工程 replay 使用 factual-prefix 恢复，与 dataset setter 的 physics-memory 覆盖不同；原生数据精度仍需单独测。下一阶段先在有限数据 LeWM 基线上比较新增数据，保留 uniform common-reset branches 强参照，不加 decision loss。

## 2026-10-02 Stage 0 批次（运行前）

- 推进 I12/R1；复用 E13 原生 CEM trace，先 TwoRoom，再 PushT。
- seed=0，保留 candidate ID/action sequence、anchor/goal、各轮 cheap score/top-K；真实 branch outcome 放在独立 hidden artifact。
- 每任务至少 8 个 held-out anchors、每 anchor 8 条竞争或均匀候选的原生执行 prefix；另同 state 同 action replay 3 次，测 state/pixel replay error。prefix 与 frameskip 逐配置记账，记录每次 reset 和真实 environment steps。
- 显式核对版本是否有 callback；无 callback 时用 cost wrapper 捕获 candidate，保持 native CEM。验证 candidate 可重放、state setter 的公开变量覆盖、终止/截断处理。PushT 的 physics memory 若不能 exact restore，先报告 replay residual，不称精确反事实。
- selector 函数只接 public candidate predictions/action arrays；future utility 与 simulator hidden state 禁止进入 selector。写一次 outcome shuffle / mutation 检查，selector outputs 必须完全不变。
- Stage 0 不声称 acquisition 提升。下一阶段保留 NO-ADD、IID、uniform common-reset branches（FIRM-WM 思想强参照）、coverage/excitation、GLOBAL-U、TASK-U、PBB 的等新增 env-step比较，保持 LeWM 原 loss；先 1 train seed。
- 初轮不训练 acquisition network；若只有一个 checkpoint，任何 augmentation/decomposition uncertainty 只能标 proxy，不能冒充独立 epistemic ensemble。

- 固定 stable-worldmodel 0.0.6 wheel 实测源码没有 CEM callback；第一版用 cost wrapper 旁路记录相同信息，不改 CEM sampling/update。先行 simulator-generated bank 的 replay/隔离检查可以复用，但不能称为 acquisition-effect evidence。
- 先行生成数据保留 reset seed 与 factual action prefix；从 fresh reset 重放 prefix 恢复真实 physics memory，再更换 goal。分支查询步数与 prefix replay 的 restore 开销分别计账。dataset setter protocol 则单独审计，不能把这两种 reset 协议混为同一精度。


## 代码可行性：same-state branch与candidate trace已有接口

stable-worldmodel代码已核对：

- 历史 main 的 `CEMSolver` callback 提供 candidate/elite 信息；本批 0.0.6 无 callback，cost wrapper 捕获 candidates/costs 并按原生 topk 重建 elite boundary，不必重写 CEM；
- TwoRoom支持 `_set_state(state)`，规划配置本来就从dataset restore agent state；
- PushT支持公开 `_set_state(state)`；
- OGBench Cube/Maze支持 `set_state(qpos, qvel)`；
- FIRM-WM也使用这些released state-setting interfaces做common-reset intervention，并明确说明common-reset只保证公开restore变量一致，不等于完整simulator memory相同。

所以首轮工程路线：

1. 用原生 CEM 的 cost wrapper（或所锁版本 callback）记录 candidate sequences、cheap score、top-k membership；
2. 从dataset/eval start state建立branch anchors；
3. 按selector选择anchor + competing candidate prefixes；
4. 用对应环境公开setter reset并执行；
5. branch bank保存真实transitions/outcomes；
6. 每个acquisition policy只消费相同env-step budget；
7. TwoRoom先做reset-replay exactness check；PushT/Cube照FIRM思路做factual-suffix replay误差audit，再决定是否进入确认实验。

这足以让本地agent直接开工；不需要先开发通用active-learning框架。


## PBB selector v0：先用elite-membership uncertainty，不训练acquisition network

对一个decision state的CEM candidate bank ({a_i}_{i=1}^N)，先用可部署的cheap uncertainty来源得到 (M) 组cost estimates (hat c_i^{(m)})。第一版优先顺序：

1. 已有多个训练seed/checkpoint时直接用小ensemble；
2. 否则训练2–3个bootstrap/lightweight scoring heads；
3. 不把真实branch outcome、未来success或privileged state喂给selector。

令 (K) 为CEM elite数，定义候选进入elite的经验概率：

[
p_i^{elite}=rac{1}{M}sum_m mathbf 1[iin TopK(hat c^{(m)})].
]

一个最简单的state criticality是elite-membership entropy：

[
U_{boundary}(s)=sum_{iin mathcal B} h(p_i^{elite}),
]

其中 (mathcal B) 只保留cheap top-M或elite-cutoff附近候选，避免远离决策边界的无关不确定性。branch action pair优先从：
- 一个高 (p_i^{elite}) 但不确定的candidate；
- 一个与其动作/预测后果有明显差异、同样可能跨elite cutoff的candidate；
中选。

这比“prediction variance最大就采”多了**decision boundary filter**，也比ToIA式task relevance更直接针对“谁会被CEM选中”。

### 不把公式当贡献

v0 score只是为了快速判别研究假设。若它有效，再比较：
- entropy vs pairwise rank-flip probability；
- top-1 boundary vs top-K elite boundary；
- candidate action diversity是否需要显式进入score；
- query one-step branch还是prefix branch。

若简单margin/uncertainty已经足够，保留简单方法，不为“看起来新”加网络。

## PBB的paired-action读数

对被query的同state branches，除了训练数据本身，还保存：

- cheap model排序；
- branch真实outcome排序；
- 是否发生top-1 flip；
- 是否发生elite membership flip；
- 两候选真实utility gap；
- query前 (p_i^{elite}) / margin；
- query后模型更新使该decision的regret减少多少。

这些读数允许直接检查“acquisition score高”是否真的对应**decision correction value**，而不是只对应视觉/latent prediction error。

### 2026-10-02 held-out decision audit（运行前）

seed0全部48个锁定评测anchor、共同base30 checkpoint的native CEM N300/K30/30，固定iteration15。每anchor以seed74000+j均匀抽64个candidate ID，七个已训练模型评估同一64序列；不能各自挑容易的bank。真实执行每序列25steps，保存完整状态轨迹及第25步图像；额外同动作重复控制，不剔除任何起点。

主读数是**64候选内**选中单candidate的真实任务距离regret（执行时首次native成功便停止，否则第25步终点；参照同bank最优，绝不称全局oracle）。另报不中止第25步位置距离排序的top7 elite recall、真实candidate terminal与模型terminal的latent MSE、成功候选比例。native CEM实际执行的是elite mean：七模型各对同bank top7取动作均值，另执行其25步，报告success及相对bank最优的signed utility gap，均值可好于64个单candidate，不能截断负数。此诊断是固定bank的模型选择质量，不替代已有完整CEM闭环成功率。

全部模型/ID/读数在真实outcome执行前锁定。评测branch数据与主训练/独立seed acquisition目录完全分开，无线上budget主张。以episode paired bootstrap 2000次报告差异，不把3000多个候选当独立样本。factual恢复对照若异常须单列降级。

### 独立pipeline seed结果：首轮大增益未稳定复现

全部三seed完成，[完整config/hash/每seed配对CI](../results/E16_20261002_independent_seeds.json)：NO-ADD=9/19/22，uniform=17/18/15，GLOBAL-U=24/16/23，PBB=19/13/15，分母每组48。GLOBAL-U的对NO-ADD增益=+15/−3/+1起点，PBB=+10/−6/−7；不能拿seed0的episode CI说方法稳定有效。这里是whole-pipeline variation（data、eval、head/acq、optimizer共同随机），不是固定data的3初始化seed；seed0首resume偏差及A100/RTX精度/硬件都保留。

PBB当前v0没有优于GLOBAL-U的证据，global的正增益也不稳定；不关闭R1。后续应扩大**经验类型/利用方式/训练目标/任务复用**的比较，结合近邻的learnability/variance reduction/contrastive objective，而不是多次改变entropy权重。E18反馈/短适配、R2预测对象继续作为独立方法轴。两种首轮具体实现均未显示strong-baseline之外的价值，按用户原始人审条款请人复核下一批科研优先级；尚无paper narrative或状态变更。

### 2026-10-02 数据利用 × 预测目标矩阵（运行前）

推进P04/R1/R2：新经验的价值是否受训练对象限制？不是救PBB。固定seed0 common base30、100基础episodes、已密封uniform common-reset的80×25步经验、全部48目标和原CEM。借用RC-aux公开代码commit `cbdf3786b149df8145d6c7314f32f460d43c9695` 的 `JEPA.rollout_open_loop`，只研究其多步预测组件；不称完整RC-aux复现，不加入reachability/planner head。

矩阵：NO-ADD / UNIFORM × ONE-STEP / TF-LONG / OPEN-LONG，共6方法。每方法600 AdamW更新/b128/lr5e-5/WD1e-3/clip1/bf16，重新加载相同model与optimizer；训练seed51000/52000、全部48评测seed0，不选幸存方法/目标。训练均读6帧(0,5,10,15,20,25)、25真实动作；基础episode只用完整不跨边界clip，每branch一个完整25步clip，无假future或padding标签。UNIFORM每batch固定13/128 branch、115/128 base；NO-ADD全部128 base。该明确mix/clip规则不同于v0按所有合法短clip均匀采样，必须重跑全部对照，不能直接与v0分数归因比较。

ONE-STEP保持原3 shifted-target MSE与前4帧SIGReg。TF-LONG、OPEN-LONG均为原MSE + 0.5×三未来目标loss + 0.09×六帧SIGReg；目标为初始3帧后15/20/25步，权重[1,2,3]/6。TF使用真实滑动history，OPEN逐步回填预测history、不detach。TF/OPEN同labels/regularization/权重，是区分额外监督与递归训练的关键控制；ONE与LONG的差值不单独归因recurrence。全部encoder照常训练，禁止跨step缓存其latent；本实验匹配gradient steps，记录实际训练时间/预测calls，不声称等墙钟。

阳性对照：已跑通released/native cost；本次运行前再核对官方RC递归与独立展开、首步TF/OPEN一致，训练finite/gradient norm，所有方法native CEM正控。主读数为48 held-out closed-loop success、paired help/harm与episode bootstrap CI；train MSE只作训练诊断，不当机制证据。噪声地板：一个探索train/data seed，原seed0 resume限制继承，48目标CI不能代替独立train-seed CI。

决策表（跑之前写）：OPEN胜TF且跨两data条件有差异→确认数据×目标并扩seed/task；TF与OPEN相当→收益可能来自更多监督/regularization，不称递归特效；两者不胜ONE→保留null，转向经验类型、预测结构或任务复用；所有模型仍弱→补原生训练配方/data regime而非包装少数据corner。raw `/tmp/latent-wm-runs/20261002-E16-objective-matrix-RTX-s0`，完成后复制持久cache，模型仍在HF cache。单个授权空RTX slot执行6个独立方法，现有E18另卡并行。


### 2026-10-02 optimizer修复与重跑（运行前）

旧acquisition三seed及未完成objective matrix受CPU AdamW step alias影响，严格方法判断撤回，见[校对](../results/E16_20261002_optimizer_audit.json)。旧raw/模型不覆盖，六方法partial作废为公平比较证据、保留故障。每方法deepcopy optimizer state并记录begin/end/source steps，源state不可变断言。

重跑锁定：原seed0七策略、seed1/2四策略，原base checkpoint/bank/base episodes/eval anchors、每方法600updates与原training seeds完全不变；只修optimizer隔离并使用不同output/model-cache。base30初始step seed0/1/2=1680/1650/1680（manifest决定clip数，不能强行设相同），不重购simulator数据、不重训base或bootstrap。先seed0七策略，再seed1/2，全保留；修复后统一bank audit需重算，否则旧audit只描述受污染模型。

六方法矩阵用 `20261002-E16-objective-matrix-RTX-s0-retry1` / HF `E16_objective_matrix_RTX_s0_retry1`重跑全部六方法。同先前定义与seed、clip/frame/action、label/regularizer、eval不变。**OPEN-LONG从当前context的第10步预测第15/20/25步，最长forecast=15steps，不是部署25steps监督匹配**；原25step clip名称只指素材长度。输出校对断言、finite梯度、native正控和全部48goal结果。matched gradient steps≠matched wallclock；仅一探索seed，后续扩data regime/native recipe/第二task，不局部救PBB公式。


### 2026-10-02 P04：数据量 × 训练计算（运行前）

为区分有限经验、训练不足与方法效果，不把base100 pilot当官方充分训练。新BASE100/BASE1000均fresh同random architecture init（seed0）与fresh AdamW；BASE100继承exact旧100、BASE1000 nested加入900 len>36 episodes（extra seed40000，排除旧native12/eval48/base100），同旧48evalanchors及其hash、固定旧base100 actionnorm，不重新挑目标。继承同合法clip `range(n-20)`，不混入clip修复、scheduler或normalizer改变；各case独立RAMcache，1000预计约13GiB。

同原history3/all3 MSE+.09 SIGReg(17knots/1024proj)、AdamW5e-5/WD1e-3/b128/bf16/clip1/constantLR，**不是官方Lightning/paper配方复现**。每条件精确5650 updates，step1680/5650为主数据×compute四格；560快照为次读数（100条件exact10epochs，1000条件5650是该nested数据的10epochs，clip计数运行前核对）。每个快照全部48native CEM闭环，不按中途读数取消/增训；eval后恢复训练CPU/CUDA/NumPy RNG，使eval不改变后续优化。模型存新HF `E16_data_compute_s0`，old base不覆盖，不resume；source/eval/normalization/init/checkpoint hash及optimizersteps、VRAM/I/O/wall-clock保存。

released LeWM最后在同48起点作正控，沿其full-dataset action statistics；不是同训练data公平方法基线，只用于harness/能力参照。positive controls为同初始weights digest、wholeepisode/norm/eval一致、native scoringallclose、loss/gradientfinite。primary成功/help-harm和episodepairedCI，训练MSE仅诊断；单init/data seed，不能升级科学主张。

决策表（跑之前写）：1000在matchedupdates已改善→数据覆盖/利用更重要，下一批在较强dataregime确认acquisition/objects；只有更多updates改善→先补optim训练，再评idea；双方仍弱且released强→官方resolvedrecipe/representation/normalization作对照，不能把欠训练失败当方法边界。原paper每task10epochs、repo默认100以及当前HF history设置不同；分别报告，不冒称原数值复现。raw `20261002-E16-data-compute-RTX-s0`，GPU0在E18后，独立单GPU、不用DDP。

运行前placement补记（2026-10-03）：检测本机GPU1释放，data×compute由GPU0等待队列移到GPU1独立运行，与A5/GPU0及optimizer-fix/GPU3并行；数据/目标/seed/updates/CLI不变。free-GPU wrapper再次确认，模型HF缓存、数据node-local。

### Optimizer-isolated seed0：全部七方法实际读数

[完整config/hash/source-stepguards/pairedCI](../results/E16_20261003_optclone_seed0.json)：NO-ADD/IID/UNIFORM/COVERAGE/GLOBAL-U/TASK-U/PBB=7/18/32/27/19/13/20，各48；所有297optimizerstates从1680开始到2280、600updates、source不变。UNIFORM对NOADD+25/48、pairedepisode95%CI[.3542,.6672]；PBB对UNIFORM−12/48、CI[-.4172,-.0625]。这是一完整探索pipeline seed，不是独立trainseedCI，另外两seed继续全部原方法，不停止/筛种子。simplecommon-reset是强baseline而非新方法；下一步数据×compute与数据×objective检验支撑范围/利用，不局部优化PBBentropy。旧被污染结果仍作废为因果证据。

### Optimizer-isolated全部原三pipeline完成

[完整结果](../results/E16_20261003_optclone_independent_seeds.json)：NOADD7/16/19，uniform32/15/18，GLOBAL-U19/20/27，PBB20/11/13，各48；全部source1680/1650/1680→+600 guards通过、未筛种子/方法。GLOBAL-U三个对NOADD均+12/+4/+8，PBB+13/−5/−6；uniform+25/−1/−1。三pipeline共享recipe但data/eval/init变化，是whole-pipeline variation，不是固定data trainseedCI。uniform首seed优势未稳定；GLOBAL是需要强基线确认的成熟采样参照，PBB v0无稳定收益。当前native evaluator还有P10动作接口限制；data×compute及sixobjective全部继续，不能只救PBBscore。

### 数据×训练计算完整读数与曝光控制（2026-10-03 GPU前修订）

[完整六快照+released正控](../results/E16_20261003_data_compute.json)：BASE100560/1680/5650成功7/13/38，BASE1000为12/19/21，released39，各48。共同初始化/held48/固定base100norm；100条件5650=100.893epochs，1000条件5650=10epochs，不能称少数据更好或等效released。独立audit CI在结果文件补记，原raw结果不重写。

下一已锁控制P04/R1：BASE1000_u5650在565batches×10整epoch末，保存fulloptimizer/CPU-CUDA-NumPy RNG；严格resume同constantLR/all3+.09SIGReg/同128bf16/同数据norm/held48，snapshot总16950=30epochs、56500=100epochs。先问高data条件是否训练曝光不足，不同时换scheduler/globalnorm/labels。BASE1005650作为近似100epoch参照，明确不是exactepochmatch；原baseline不重训、不删任何已完成snapshot。这里只是充分训练强baseline建设，不预设paper叙事。

正控：sourcecheckpointSHA/strictstate/297steps均5650，deepcopy optimizer source不可变与end=5650+actualupdates；10epochpermutation NumPy state精确再生/nextorder相同，CUDA/CPU RNG还原、isolatedeval保留；new HF目录与raw/durable均不存在。primary原48 success/pairedhelp-harm/CI与trainupdates/wallclock/epoch分别报告，保留源6snapshot与released；max2snapshots、1exploratoryseed/独立授权GPU1。额外环境仅评测不采新data，raw `20261003-E16-data-exposure-RTX-s0`，HF `latent-wm-trained/E16_data_exposure_s0`。决策表（跑之前写）：large充分训练追上→旧equal-update差是optimization/exposure竞争解释，不重命名新规律；large仍弱→查data composition/regularizer/训练对象，方法应面对BASE10038强base，不救原selector；large明显改善→以其checkpoint扩第二task与公平data acquisition/预测目标。代码data_exposure_continue.py正CPU准备，root审后才GPU，当前无新读数。

### 固定数据的充分训练独立种子（2026-10-03，训练前）

推进P04/R1/R2：38/48是否只出现于首trainseed，关系到新方法应面对哪种强base。固定原seed0 BASE100全部episode/9295rows/7295clips/原norm与eval48；fresh架构/AdamW，trainseed1/2只改变初始化、训练CUDA/dropout/SIGReg投影与shuffle(33000+seed)，各5650updates≈100.893epochs，末尾只评全部48、评测localCEM/resetseed0，globaleval RNG固定0并保存恢复trainRNG。原三shiftMSE+.09SIGReg17/1024、frames0/5/10/15、20action支撑、b128/bf16/clip1/LR5e-5/WD1e-3/constantLR全部同；不用旧optimizer、不增加数据，不称原论文配方。trainseed0 CPU初始化需逐tensor复现原commoninit、实际loss/gradient/optimizer/RNG独立控通过再跑。

uint8/controls/clipstarts/原行映射一次从原HDF严读为自含nodecache；raw terminal action允许保留NaN，只有实际20-action训练clip必须全finite，normalizer照原filterfinite，不悄悄删row。compressed nodecache只搬运一次、解压后逐fileSHA核验，模型各seed存HF不同目录。首独立batch计划两个空A10080GB各一job，启动freewrapper再次复核，A100计时不混RTX；无multi-node训练。主读数三trainseed各success与同48 help/harm、完整训练loss/steps/wallclock/hash，48episodeCI与trainseedvariation分开。决策表（跑之前写）：充分训练收益重复→新方法从该强data regime对比；不重复→保留全部seed并查训练/representation/goalcost，不挑38模型替paper筛seed。新162行脚本fixed_data_train_seed.py CPU准备中；尚无新train读数。

曝光控制最终CPU/root审（GPU前）：独立145行、source SHA c804d278c214e7e0e014d4ab1433a938ccca8edd730c53000da43ab4f84010b1，297states5650/deepclone不可变、72359clips/565batches、模型manifest/norm/48anchors全通过；10epochs RNG和nextorder精确再生。script SHA e5e136b4e2e00cbd2cd435e76efce51d3d975ff8ff1f157b3b2fe6f9f05ad132。源未保存NumPy globalstate但训练shuffle用独立Generator已精确恢复，全局沿原seed0明示；CUDA/CPU restored。GPU1已空，free-wrapper再复核并真实context，启动两固定stops，不重写原6snapshot。

### Data×prediction-object matrix完整读数

[六格修复重跑](../results/E16_20261003_objective_matrix.json)：NO-ADD ONE/TF-LONG/OPEN-LONG=21/14/16，UNIFORM=11/24/19，各48，全部297steps1680→2280/source不可变。uniform−no在ONE为−10/48 CI[-.375,-.0417]，TF为+10/48 [.0625,.3542]，OPEN+3/48 [−.1042,.2292]；TF/OPEN直接差CI均含0。仅一个pipeline、有额外label/正则frames与FLOPs差别；ONE(4frames)、LONG(6frames)不是独立horizon变量，最大open-loop forecast15而非部署25；6methods均未超过充分训练100条件38/48。交互读数只是新线索，不登记普遍data-loss原则，不能筛ONE/TF来救叙事。


2026-10-04上传状态核对：[曝光控制partial](../results/E16_20261004_exposure_partial.json)30epochs/u16950保存37/48；原5650/10epochs为21/48，训练曝光是值得继续分辨的解释。100epochs终点未complete、最后日志epoch44/u24860、本机没有对应训练进程，原因未核对；不能写整批DONE或仍在运行，不以partial筛选终点。固定数据trainseed脚本最终170行SHA b17bb1efe80a1fff1816bd0a66681f41dd39b01d9533c5cb1f9970258bf0d747；CPU实际init/loss/gradient/optimizer/RNG控已通过，但没有已核对GPU训练读数。恢复需核对源checkpoint完整RNG/optimizer及remote staging，再沿原锁定终点执行，禁止凭日志步数拼接。


2026-10-04人审反馈后、独立种子GPU运行前：保留原锁定固定data/eval48/终点5650及seed1/2；现有seed0提供第三个独立训练随机性条件，旧eval48仍为开发集，不能当确认集。原A100 placement目前两卡均占用，改为本机两张实际空闲RTX PRO 6000分别GPU0/1，各fresh process；数据/recipe/seed/终点不变，不混硬件timing。源码与先前CPU PASS SHA完全一致，既有venv和节点cache复用。新raw/durable `20261004-E16-fixed-data-trainseed-RTX-s1/s2`，模型HF `latent-wm-trained/E16_fixed_data_trainseed_RTX_s1/s2`，由freewrapper再次确认并创建实际context；本段在launch前写，不代表训练完成。完整训练曲线loss与终点success保留，未来增加中途success评测另锁协议，不回改此批。

2026-10-04 exposure恢复运行前：原partial保持不动，不能从epoch44日志伪造checkpoint；从已保存完整u16950/epoch30恢复，仅完成原锁定u56500/100epochs终点。新增resume可选入口，先验证原5650 checkpoint/manifest/recipe，再逐SHA核对30epochs checkpoint/summary、strict weights、297完整AdamW/deepclone/source不可变、30epoch shuffle RNG再生、CPU/CUDA/NumPy全state。same RTX、constantLR、原48开发集与optimizer/RNG隔离eval不改；new raw/durable `20261004-E16-data-exposure-resume-RTX-s0`，new HF `E16_data_exposure_resume_s0`，原30epochs结果不重写。仅末端一snapshot的complete不代表重新生成此前所有曲线。CPU实际通过/root复核后独立GPU2，source SHA 9a36eb83df7b5d5eb53201e830bff9705c6acd8a8b9aa86592d0af3b429ac350。

### 2026-10-05曝光终点已完整；新增fresh48强参照（运行前）

原锁定1000轨迹/100epochs/u56500已全部训练与原48终点评测complete/no-failure，39/48；原同data u5650/10epochs21/48、u16950/30epochs37/48，充分100轨迹5650为38/48、released39/48。仅同pipeline/source0的开发校准，不能称稳定等效或新data规律；1000的updates为100条件约10倍，不能把data×compute混作因果。原partial/中断日志保留，最后完整checkpoint源16950恢复与optimizer/RNG契约依前控。

新增必要强参照：固定该u56500到E20新独立48wholeepisode ledger、两接口native/physical各48、原H25EX25/300-30-30/100新steps/原seed/原RTX精确warm守卫，所有anchor保留不依效用选任务。fresh48排除原BASE1000 episodes，强data baseline不是同100-data公平methodgain，训练预算单列。主读数各goalspan成功、真实envsteps、同eval ledger原数；不和旧48跨任务相减，发布预训练未知继续单列。阳控完整source checkpoint/hash、303strictload、nativecostparity、原精确factual/restore；噪声单trainseed且同48配对，不能以96episodes充trainseeds。GPU2原曝光自然释放后free-wrapper；代码fresh_exposure_control_queue.py不改已有训练/评测runner。决策：充分大data明显胜新增branch方法→方法需要证明相同总资源下更有效经验或更好复用；未胜→结合完整AD/value/experience矩阵判竞争设计，不调centerλ。只作为D1/P04基线/measurement，不预选paper、scienceclaims0。
