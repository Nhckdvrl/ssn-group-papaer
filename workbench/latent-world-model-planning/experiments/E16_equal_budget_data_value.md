# E16｜Planner-Boundary Branching (PBB)：planner-aware data acquisition

- **状态：** PLANNED；未运行。
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
未运行。


## 代码可行性：same-state branch与candidate trace已有接口

stable-worldmodel代码已核对：

- `CEMSolver` callback 每轮拿到 `candidates / costs / topk_inds / topk_candidates`，因此PBB所需的candidate bank与elite boundary可以旁路记录，不必重写CEM；
- TwoRoom支持 `_set_state(state)`，规划配置本来就从dataset restore agent state；
- PushT支持公开 `_set_state(state)`；
- OGBench Cube/Maze支持 `set_state(qpos, qvel)`；
- FIRM-WM也使用这些released state-setting interfaces做common-reset intervention，并明确说明common-reset只保证公开restore变量一致，不等于完整simulator memory相同。

所以首轮工程路线：

1. 用CEM callback记录candidate sequences、cheap score、top-k membership；
2. 从dataset/eval start state建立branch anchors；
3. 按selector选择anchor + competing candidate prefixes；
4. 用对应环境公开setter reset并执行；
5. branch bank保存真实transitions/outcomes；
6. 每个acquisition policy只消费相同env-step budget；
7. TwoRoom先做reset-replay exactness check；PushT/Cube照FIRM思路做factual-suffix replay误差audit，再决定是否进入确认实验。

这足以让本地agent直接开工；不需要先开发通用active-learning框架。
