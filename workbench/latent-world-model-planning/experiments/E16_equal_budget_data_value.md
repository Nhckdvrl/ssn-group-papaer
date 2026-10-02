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

## Decision-critical score的最低实现

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
