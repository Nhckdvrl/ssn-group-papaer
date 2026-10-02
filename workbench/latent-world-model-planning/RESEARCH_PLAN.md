# 研究计划｜问题、方法与贡献的生长

更新：2026-10-02。当前工作台的唯一科研计划；本页替代旧的多份 program/mine/positioning/novelty 文件。实验菜单见 [实验索引](experiments/README.md)，文献证据见 [核心阅读](literature/CORE_READINGS.md)。

## 1. 研究对象与选择标准

研究的是从视觉观测和动作学习紧凑动力学、并用于控制/规划的世界模型，不默认训练大型视频生成器。共同接口是 `history → state → action-conditioned prediction → planning/policy → real outcome`，但不是所有方法都必须有同一种 latent、同一种目标或同一种 planner。

目标不是找到别人没有说过的名词，而是改善重要问题上的理解或解决能力。允许两种循环交替：

- **问题驱动：** 现实任务/强基线的不足 → 相互竞争的解释 → 对比或干预 → 方法/结论。
- **方法驱动：** 文献中的有效原理 → 对当前问题的具体预测 → 原型和强对照 → 分析何时有效，再发展自己的设计。

两者都不要求先有独一无二的异常。“加一个 loss”可以是合理实验；仅有加法和一个分数不是足够的最终贡献。不要在探索阶段禁止简单方法，却又希望事后凭空产生好方法。

### 近邻如何使用

读到相关论文，记录它解决的具体目标、输入/数据假设、方法、决定性实验和边界，再问：我们要解决的实际问题有什么尚可改善的部分？哪些设计能直接复用？哪些对照必须补？

**“同样研究记忆/可达性/规划”不是精确重复。** 精确重复也先调整方法、证据或问题表述，而不是删掉母问题。摘要只能导航；不能据此声称方向已被研究完。新颖性是待证实的贡献差异，不是一个“空白认证”。

## 2. 问题—方法地图

下表是问题与可用工具的对应，不是互斥分区或红区评分。方法名称代表已有路线，具体实现与版本按 ASSETS 和原文确认。

| 真实需求 | 可以直接研究的方法轴 | 要看到的实际改善 | 主要近邻入口 |
|---|---|---|---|
| 用有限/偏置经验学好控制 | 数据选择、重采样、局部动作干预、失败/恢复经验、时序监督 | 数据效率、新目标成功率、低覆盖区域可用性 | PLDM、RC-aux、OGBench、goal-conditioned RL |
| 让长时想象既准又可用 | 多步训练、直接多时域预测、结构化动力学、层级/长期预测、混合规划 | 长时成功率、稳定性、端到端计算 | LeWM、DINO-WM、TD-JEPA、TD-MPC2 |
| 任务对齐不牺牲复用 | query 注入位置、双分支表示、轻量任务头、任务族训练 | 当前/新目标、换 cost/planner 的表现 | DINO-WM、RC-aux、value-equivalence/goal-aware 路线 |
| 看不全也能控制 | 历史、递归状态、belief、多未来、主动探测 | 遮挡/隐藏参数下成功、风险和恢复 | recurrent world models、POMDP、现有 belief/记忆路线 |
| 预测不准时仍能完成任务 | 重规划、改变 horizon、反馈校正、在线适配、policy 回退 | 成功率—延迟—交互成本 | PLDM、不确定性 MPC、适配/反馈方法 |

**文献事实与我们的推演分开：** 上述近邻证明这些需求已有研究基础；下面各方向是本工作台的探索提议，不声称文献尚无类似方法或已确定可投稿。

## 3. R1｜什么经验让世界模型真正更好用？

### 母问题
在固定或可计量的数据/交互预算下，如何训练出更可靠、可迁移、能支持规划的模型？场景不局限于一个房间、一个 sampler 或一种 reachability head。

PLDM 的研究比较数据量、质量、轨迹长度与泛化；RC-aux 明确把轨迹时间差当作经验可达性代理。这些工作是研究支点，不是让我们只研究“所有已知因素之外的一点残差”的理由。[来源 S2、S4](literature/CORE_READINGS.md)

### 三条可以并行迭代的方法路线

**A. 改善经验的组成。** 同等预算比较增加覆盖、局部动作分支、多路线、接触失败/恢复经验；先回答实际哪类增量更改善规划，再研究原因。允许主动采样或重采样，而非只审计数据。失败数据可能有价值，也可能因为偏离任务而浪费预算，不能预设答案。

**B. 改善轨迹监督的用法。** 同一段轨迹同时提供事实转移、时序关系、成功/失败等不同证据。可以试 budget-conditioned reachability、局部一致性、保留不确定标签、同对状态的多路径聚合、动态损失配比。必须保留原始方法及等训练量基线；模型内自洽不保证环境可执行。

**C. 联合数据和目标。** 某类数据只在某种 objective 下有用，本身可以引出有价值的方法：例如有针对性的干预数据配合动作后果损失、恢复数据配合规划候选评分。比较单改数据、单改目标和联合改动，避免把机械拼接当机制解释。

### 从哪里开实验
E14 使用原生数据分布、轨迹质量、路径选择开展比较；多门 TwoRoom只是便于观察的一种方案。E16比较等预算数据配方，并允许小规模数据选择/训练目标原型。导航用于精细控制变量，Push-T/Cube用于确认对接触与操作任务的价值。

### 如何发展而不越缩越小
改变数据后性能变差，不自动等于“行为几何污染”；覆盖、动作激励、可识别性、保守性都可能解释它。如果覆盖解释了现象，可以转为覆盖感知采样/训练，而不是宣布 R1 无意义。若原方法的经验可达性恰好有利于保守规划，也要研究何时保留它，而不是一定把它替换成最短路。

探索时记录这些因素即可；只有声称独立的因果机制时，才要求对应的匹配、干预和替代解释排除。局部动作协方差只是描述性指标，不能充当完整的可识别性证明。

**可形成的贡献：** 更高效的数据采集/利用方法；对数据价值的可迁移规律；解决已有 planning-aware 方法实际局限的训练方法；新评价协议。不是强制“残差效应 + 一条定理”。

## 4. R2｜模型应该预测什么，规划计算放在哪里？

### 母问题
在有限训练资源和部署预算下，怎样兼顾长时任务、动作选择质量和目标灵活性？问题不是“两个模型谁赢”。

DINO-WM/LeWM可在动作条件下递归预测；Bagatella TD-JEPA学习 policy-conditioned 长期预测结构，状态编码与任务编码可分开。这是不同计算组织方式的依据，但不意味着两者有可直接横比的输入、目标和训练预算。[来源 S1、S3、S5](literature/CORE_READINGS.md)

### 建议的生长顺序，不是硬门槛

先在同一 compact backbone 上比较 teacher-forced one-step、多步 open-loop、直接给定动作序列与 horizon 的预测。保留同一目标与 planner，容易判断训练目标/递归方式的作用。可以试 horizon curriculum、多尺度预测、短步动力学配长期 terminal/value/reachability 头；不必等证明普适 crossover law 才开始混合方法。

再按结果引入长期 occupancy/successor、macro/hierarchy、learned proposal/policy 等代表。原生 TD-JEPA 等路线成本和接口不同，用作扩展参照而不是开工必须先复现的全家桶。

### 关键比较
- 相同目标，距离、动作预算与规划长度变化；不要把 goal offset 当 rollout horizon。
- 固定墙钟预算或 model calls，比较额外 search 与更好 predictor 的收益；两种预算都报更清楚。
- 新目标/奖励、接触/随机性、数据量变化；哪种方法能更好复用？
- 性能稳定增长也是有用结果，不强制出现名次翻转。

E13把上述原型与跨范式参照分成两个可独立运行的阶段。跨范式比较分开训练计算、任务信息、部署计算；例如 goal image 与 reward-labeled task-inference samples 不天然等价。

### 已并入的新入口：变化后的复用与更新

整理期间新增的I13/E19保留在当前目录，而不是退回历史。它问任务或环境改变后，局部动力学、长期预测、policy等结构中哪些可以复用、哪些要更新。第一轮可以同backbone比较少步更新、replay、短模型加长期头；局部物理变化不保证神经参数只需局部修改。经典SR/SF的reward/transition重估差别是背景，不预先当新发现。更有效的更新方法、恢复速度或可用范围都可以形成增量，不要求先获得一条普适定律。

**可形成的贡献：** 新的高效/稳定预测结构；实用的混合规划方法；计算分配原则；条件性解释。只有“原生方法排行榜”不够，但公平比较并导出重要认识可以是主体。

## 5. R3｜任务对齐与世界知识复用能否兼得？

### 母问题
任务条件应该进入哪一层，才能改善当前任务又不损害新目标和新使用方式？不要把“有人做 query conditioning”当作这条线结束。

可用设计包括共享表示加任务头、query-conditioned dynamics、仅改变 cost、仅指导 proposal、共享动力学加轻量适配。E17在一个共同系统里选两三种最能区分设计的方案；不要求首先实现所有位置，也不预设模块化一定最好。

第一轮保持任务信息一致：同一组目标图/目标标识，相同数据与评测清单。先比较已见与保留目标；有语言条件需求再引入语言，不让大型 VLM变成入场成本。

方法可以来自“共享底座 + 小任务分支”的成熟原理；真正需要贡献的是它解决的实际复用矛盾、训练方案或适用范围，而不是组件第一次出现。性能收益、训练稳定性、任务间干扰和适配成本都可帮助形成故事。

**可形成的贡献：** 一种兼顾任务性能与复用的结构/目标；对任务特化位置的系统解释；多目标训练或快速适配方法。结论可能是存在 trade-off，也可能是某设计改善两端。

## 6. R4｜观察不完整时如何可靠控制？

### 母问题
遮挡、隐藏速度/接触/物理参数、有限历史等条件下，什么状态与规划策略能完成任务？已有记忆/belief方法是可直接借用的基线。

E11同时比较短历史、较长历史/递归状态与一个简洁的不确定性或主动探测方案。先在原生任务的自然信息缺口上测，不为制造异常构造离散“怪位置”。更复杂的 belief 或多未来方法可以在有资源时小试，不必先证明所有 point estimate 都失败。

**公平性尤其重要：** 若两个隐藏状态对可用历史完全不可辨，而最优动作不同，任何同信息模型都不可能分别选中全状态 oracle动作。这是信息约束，不是模型缺陷。完整状态 oracle只能当上界；比较时给所有部署方法相同历史、可用动作和探测预算。主动获取信息的成本必须计入。

若短历史已足够，说明该条件无需复杂 belief；可以研究更便宜的状态估计、其他自然条件或主动控制，不自动停掉整个方向。最终关注成功率、风险、恢复和成本，而不是仅凭 hidden-state probe。

**可形成的贡献：** 更有效的状态/记忆/不确定性模型；主动消歧规划；不确定性如何被 planner利用的解释；更稳健的视觉控制方法。

## 7. R5｜模型什么时候应该被信任、修正或绕开？

### 母问题
世界模型不可能处处准确，怎样让使用它的控制系统仍可靠、高效？

E18可直接比较固定 horizon、缩短/延长规划、增加候选、反馈状态修正、少步适配、轻量 policy 回退。选择已有环境和checkpoint支持的两三种动作，不先建一个通用路由框架。

同时允许简单自适应策略原型：用当前可观测的预测残差、ensemble分歧、候选质量等决定下一步策略。与固定策略、简单阈值、预算匹配的强策略比较。Oracle“哪个恢复动作最好”仅用于解释和上界，不是执行时可用信息，也不是试方法前的必经关。

如果一种固定策略始终最好，这是简化系统的证据；如果收益随任务/错误类型变化，再研究路由规则和泛化。训练路由器的数据与测试episode分离，不能用未来结果做在线特征。

**可形成的贡献：** 更稳健的规划/恢复方法；可靠性信号与有效干预的关系；预算自适应控制；减少失败或无效搜索的系统方案。

## 8. 共同实验原则：先探索，再加强证据

### 探索层
原生复现、方法对照、数据配方和误差分析可以并行。写一个简短实验卡，固定主读数与改动，留原始输出。允许粗粒度的数据/模型/任务比较产生线索；不能把线索写成因果结论。

### 解释与确认层
线索有用之后，针对最重要的替代解释补控制，而不是预先完成一份无限审计清单。训练量、数据量、planner预算、任务信息、输入历史、评测清单、随机种子是常见因素，但具体主张决定控制强度。

候选评分质量与闭环成功相互补充；需要区分没有好候选、评分错、动力学错、信息不足和代价定义错。测试时的预测误差和不同模型的 raw latent L2 不是跨模型统一尺度。

方法收益必须与充分训练的强基线比较，保留独立训练随机性。只增加 seed 提高统计显著性不等于提高研究价值；反过来，早期 1–2 次运行不稳定也不自动证明没有方向。

### 论文形成层
把有效方法/重要认识写成：实际问题 → 现有解决办法及不足 → 我们新增什么 → 关键证据 → 范围与限制。Novel narrative要对应实质增量，不是重新命名或包装成熟方法。相关工作表同时写“借用了什么”和“比最近邻多解决什么”，不要只有撞车名单。

## 9. 起步与并行

默认起步组合：一个训练友好的 LeWM-family 原生任务 + 一个较强表示/规划参照；在导航与操作中各选一个资产最成熟的环境。E00/E01产出可以边用边完善，不要求所有环境准备齐再试方法。

首批以 R1 数据/目标配方和 R2 预测/规划结构最容易复用资产，R3–R5按资源与新结果接续。这只是工程便利排序，不是科研价值评级或方向关闭。

单卡/单节点的 model × data × task × seed可以广泛铺开；先实测I/O与完整训练/评测成本，再给有信息增益的比较分卡。重复相同局部优化却不改变问题认识时，回到本页的方法空间调整，不靠再加限制词寻找“仅剩空白”。

## 10. 参照RC-aux的工作量形态，而非锁定RC-aux题目

用户提供的RC-aux §4.4报告本地scoring模块约18.7M参数、单GPU实验；Table 2把训练侧与planner侧作用分开。它说明**小改动可以承担重要问题，成熟后可以用独立实验快速补齐证据**，而不是“小模型只能研究小问题”。它的背景中已有JEPA、reachability、几何和多步预测，这些并没有取消做新工作的空间。[S4](literature/CORE_READINGS.md)

本工作台优先三类可快迭代的实验：已有checkpoint上的planner/反馈改动；同一小backbone的目标/结构/数据改动；有必要时再做较长的独立原生训练。目标是减少单次实验耦合与失败成本，不要求所有有价值方法只改一个head，也不禁止需要几次训练才能看清的问题。

**“整套确认实验约一天”是待实测的吞吐量目标，不是论文证明的事实。** RC-aux未给足逐任务训练与全项目GPU-hours，不能把单个cost-call时延乘算成复现时长。执行机先测训练、完整闭环eval、I/O，再按可用卡数排：例如3个方法×3个训练seed×2类任务是18个独立训练作业；8个同时可用槽位至少3批，实际还取决于作业长短和评测/数据瓶颈。该例只是排程算术，不是预估这些任务的实际小时数。

成熟论文包围绕一个中心贡献组织：最强可比基线、核心方法/问题的主结果、能区分解释的消融、至少一种有意义的范围/限制测试，计算与数据成本。需要更多任务时扩，不机械要求每个方向都先做完整论文级证据才能试原型。


## 11. 第一波方法假设：从文献张力直接长方法，不等“空白”

下面不是已成立的paper idea，而是**现在最值得本地agent迅速做实验的两个方法假设**。它们有明确近邻、也有明确增量；相近工作越多越要求比较做扎实，而不是自动放弃。

### H-A｜Planner-Boundary Branching (PBB)：把新经验花在planner真正可能改主意的地方

**母问题（R1）：** simulator/reset预算有限时，下一条world-model经验应该采哪里？

已有工作已经分别说明：active querying可以追预测弱点；task-aware acquisition比全局uncertainty更有用；same-state counterfactual action branches能强化动作因果；candidate selection opportunity集中在少数决策。我们的工作假设把这些压力落到latent MPC的具体接口：

> **不是“最不确定的state”都同样值钱；更值钱的是那些候选动作排序不稳定、且排序翻转会改变planner选择的decision-critical states。**

第一版不改loss，先只改**数据分配**，避免和D-JEPA/AD-WM的decision loss混在一起。CEM/iCEM运行时，用cheap ensemble/bootstrapped heads估计候选的rank disagreement，并结合top-2或elite-cutoff margin形成criticality score。对高criticality state做same-reset branch：执行2–K条竞争candidate prefix，把真实transition加入普通LeWM/RC-aux训练数据。若这个data-only版本优于random/coverage/global uncertainty/OnlineWM-like predictive-error acquisition，再考虑branch-aware ordinal或consistency loss。

工作分数可从简单式开始：`criticality = selection_relevance × rank_instability × predicted_consequence_span`。这些因子都只能用query前可得信息；真实branch outcome只在被选中后揭示。

**为什么不是机械拼接：** OnlineWM问模型哪里预测弱；ToIA问哪些观测能帮助task-relevant rollout；TOM/strategic model learning问policy相关区域；我们问的是**哪条新counterfactual经验最可能修正planner即将做出的候选选择**。这是一个不同的data-value定义。最终若实验显示普通task-aware uncertainty已等价或更好，就直接收敛为负结果/改设计，不靠改名保story。

### H-B｜Planner-Stage Multi-Fidelity：广筛候选用快模型，elite附近才用高保真世界模型

**母问题（R2）：** CEM一次要评估大量candidate，而只有很少candidate会进入elite set并影响下一轮search。是否有必要给所有candidate同样昂贵的predictive fidelity？

Fast-LeWM已经拥有parallel prefix prediction；DeepJEPA已经拥有transition-level adaptive depth。它们不是kill，而是构成两个强支点。我们的不同轴是：

> **在planner的candidate population上分配prediction fidelity：cheap predictor负责高召回筛选，high-fidelity predictor只重评可能进入/改变elite set的candidate。**

最便宜原型甚至不用训练新模型：Fast-LeWM给N个candidate排序，保留top-M（M明显大于CEM elite K），再由LeWM/open-loop multi-step/high-fidelity predictor重评M个，最终elite只按高保真分数更新。比较同wall-clock下的纯Fast大N、纯LeWM小N、随机M重评、只重评top-M，以及elite-boundary/低margin重评。如果有清晰收益，再训练共享encoder的dual-fidelity head或学习screening-confidence。

与DeepJEPA的关系必须正面写：DeepJEPA决定“一个transition内部算几次”；H-B决定“候选群体中谁值得调用哪种predictor”。两者可组合；若DeepJEPA完整发布后，最强实验之一就是Fast screen → DeepJEPA refine。

### 第二波而非关闭：H-C/H-D

R3的selective query conditioning、R5的feedback/recovery routing仍值得保留；它们目前近邻较多且首轮方法杠杆不如H-A/H-B直接。E17/E18可利用released checkpoints低成本并行摸底，不因暂列第二波而降级科学价值。

### 第一波如何用多卡

先用**一个导航任务 + 一个接触/操作任务**分别跑最小方法矩阵，不先做全家桶。H-A先比较5–6种acquisition policy的单seed探索，H-B先比较4–5种fidelity allocation的单seed探索。任何明显signal先复核实现，再把最有区分力的2–3种方案铺3个以上训练seed和第二任务族。GPU数用来缩短idea迭代周期，不用来一次性把所有组合做成大网格。

这两个假设都允许失败。失败之后回R1/R2继续选方法，不把“有人做过active learning / adaptive compute”当作关闭理由。


### H-B 的更具体方法核：elite-preserving fidelity allocation

Fast-LeWM已经提供一个几乎零训练成本的第一实验：每个candidate都有cheap direct-prefix goal cost；论文的self-consistency需要额外做一条“经过中间prefix再到terminal”的预测路径。原论文对所有candidate统一加self-consistency，我们可以先问：

> **如果只对可能进入/改变CEM elite set的candidate支付这次额外预测，能否用少量high-fidelity calls恢复接近full self-consistency的planning质量？**

先把“高保真”定义为同一Fast-LeWM内部的direct + decomposed/self-consistency score，避免不同模型latent尺度不一致。然后再扩LeWM recursive、DeepJEPA或multi-step head。

若cheap cost与high-fidelity cost的残差可以在held-out candidate bank上校准成区间 `[L_i, U_i]`，一个候选的“最好可能cost”仍差于当前elite边界时可以跳过；只有区间与elite阈值重叠的候选升级。后续可把这个规则做成 **Elite-Preserving CEM**：主要测top-K elite recall、high-fidelity call fraction、closed-loop success和fixed-wall-clock Pareto。严格coverage/概率保证只有校准成立后再写，不预注册理论结论。

这个方向的novel narrative不是“多保真第一次用于规划”，而是：**modern latent-WM planners的compute bottleneck发生在成百上千candidate反复scoring；planner只消费elite set，因此prediction fidelity应该围绕elite preservation来分配。**


## 12. 什么结果能长成顶会叙事，而不只是“一个小技巧涨点”

### PBB 的叙事分叉

**最强形态：data-value principle + method。**
如果PBB在TwoRoom/Wall与Push-T/Cube都显示：同样的新增env-step预算下，candidate-boundary branches显著优于IID、coverage、global uncertainty与task-aware uncertainty，而且主要改善counterfactual ranking/elite regret而不是只扩大state coverage，那么论文可以讲：

> **World models should acquire counterfactual experience where the planner's decision is fragile, not merely where prediction is globally uncertain.**

方法可以仍很简单。novelty来自“planner-boundary data value”这个可验证原则、对应acquisition rule，以及跨任务证据。

**中等但可继续形态：不同采样策略在不同任务占优。**
如果导航偏coverage、接触任务偏PBB，不要把它判死。继续寻找决定这种差异的task factor（branching factor、contact multimodality、candidate margin、support density），可能长成“何时应该采哪类world-model data”的设计原则。

**需要转向形态：PBB≈task-aware uncertainty。**
这时不靠重新命名保idea。检查二者是否实际上选到同一states；若高度重合，贡献应转到更轻量的proxy、branch action selection或与training objective的联合设计。若没有实质增量，则回R1别的data-value路线。

### Elite-Preserving CEM 的叙事分叉

**最强形态：planner interface principle + efficient method。**
如果selective refinement在fixed wall-clock下稳定超过pure Fast与pure expensive，并保持接近FULL-REFINE的elite set，且价值集中在少量candidate/后期CEM iterations，那么可以讲：

> **Prediction fidelity in latent world-model planning should be allocated to preserving the optimizer's elite set, rather than uniformly to every imagined trajectory.**

这与DeepJEPA的transition-depth routing是互补轴，与传统multi-fidelity optimization的区别由modern learned latent predictor、CEM elite dynamics和closed-loop control证据建立。

**中等形态：只省计算、不提高success。**
如果达到相同性能但显著减少refined calls/wall-clock，这仍可能是有价值的方法论文，前提是加速真实、实现通用、强于简单candidate reduction，并在多个任务保持质量。不要因为“只是效率”自动否定；Fast-LeWM本身就是效率+准确度型工作。

**需要转向形态：cheap predictor的elite recall太低。**
这时真正问题变成screening calibration。可以训练shared cheap head专门保证elite recall、用conformal/quantile residual做promotion interval，或者改成每轮先高保真校准少量sentinel candidates再决定refine set。不要硬缩M制造失败。

### 两条线如何可能汇合

PBB优化**训练时真实数据预算**，Elite-Preserving CEM优化**部署时模型计算预算**。如果两者都成立，可形成更大的统一观点：

> **World-model resources should be spent around decision boundaries—environment interaction during learning, and predictive compute during planning.**

但不要一开始强行合并。只有两条独立结果都成立、且共享candidate-boundary指标确实能解释收益时，再考虑统一论文；否则各自保持清晰。


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

### H-C｜Selective Query Specialization：只在需要的地方任务化

**母问题（R3）：** query-conditioned world model在当前任务上可能更强，但会不会为seen objective牺牲prediction reuse？

直接近邻已经把“query决定需要区分什么”说清，所以我们不重复理论。方法假设是：保持query-agnostic predictive core，只在proposal/cost或少量predictor adapter上做任务化，并让adapter只在planner真正需要更细分辨率的candidates上启用。

首轮E17比较COST-ONLY、PRED-ADAPTER、FULL-QUERY，seen/unseen goals与新query shift都测。若selective adapter能保住大部分seen gain、又明显降低unseen degradation或额外compute，这条线才值得扩；如果COST-ONLY已足够，就把“无需重学dynamics”的简化结论作为结果。

### H-D｜Utility-Gated Recovery：不是error大就更新，而是问“这次干预值不值”

**母问题（R5）：** feedback、TTT、replan、fallback都已有方法，但哪次deployment mismatch真正值得用哪种干预？

E18先用matched fork ledger产生 `HOLD / FEEDBACK / SHORT-UPDATE / EXTRA-REPLAN` 的真实 `Δutility`，然后用部署可见的residual、elite margin、rank instability、progress等特征训练轻量router。核心不是检测异常，而是预测**intervention utility**。

若固定feedback或固定update已经统治所有条件，保留简化结论；如果不同failure modes明显对应不同干预，并且router在预算匹配下优于always-X，才形成更大的可靠规划故事。

### H-E｜Selective Revaluation：变化后重学哪一层

**母问题（R2/R3/R5）：** reward/query变化、局部transition变化和全局dynamics shift不应该默认用同一种update recipe。

E19把可更新对象分成TASK/COST、SHORT DYNAMICS、LONG-HORIZON、REPRESENTATION与FULL。先做固定module update对照；只有“minimal sufficient update set”在多个shift/task上稳定，才训练selector。

这条线与经典successor revaluation的关系是直接继承：经典结果给出reward vs transition change的计算差异；我们要解决的是**modern compact visual WM中哪层参数/预测结构需要更新，以及如何以planning recovery而不是prediction loss衡量**。

### 第一波/第二波资源排序不是科研评级

当前工程上优先：
1. E13 Stage A0：几乎零训练，最快验证candidate-stage fidelity；
2. E16 Stage 0/1：branch bank + data acquisition，训练独立可大面积并行；
3. E17/E18/E19：已有checkpoint可复用时并行小pilot。

这个排序只由“单位时间信息增益”决定，不表示R3–R5价值较低。任何第二波pilot先出现强signal，都可以立即转为主线。
