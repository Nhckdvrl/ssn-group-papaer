# Latent World Model Planning｜紧凑世界模型研究工作台

**状态：PROPOSED；已开始单卡实验，完整数值复现尚未完成。** 不改变仓库其他 ACTIVE 主线/探索线。

目标：围绕重要的视觉控制与规划问题，发展 ICLR / ICML / NeurIPS / CVPR 级贡献；不是搜寻无人触碰的角落，也不是交付一个预设现象。

## 从这里开始

| 你要做什么 | 唯一入口 |
|---|---|
| 理解问题、方法、研究空间与论文如何生长 | [RESEARCH_PLAN.md](RESEARCH_PLAN.md) |
| 把工作交给本地 agent | [LOCAL_AGENT_PROMPT.md](LOCAL_AGENT_PROMPT.md) |
| 接续代码、数据、权重和原生协议 | [ASSETS.md](ASSETS.md) |
| 找论文依据与完整历史阅读笔记 | [literature/README.md](literature/README.md) |
| 选择或修改下一组实验 | [experiments/README.md](experiments/README.md) |
| 查看实际证据 | [CLAIMS.md](CLAIMS.md)、[PAIN_LOG.md](PAIN_LOG.md) |

**默认只需先读本页、研究计划、执行提示，再按当前实验查资料。** 不要求读完一百多条文献或完成所有诊断才允许训练、改方法。

## 五个持续研究方向

| 方向 | 实际目标 | 现有探索入口；不是题目边界 |
|---|---|---|
| R1 数据与可规划性 | 用有限经验训练出更可靠的动作后果与可达性模型 | I09/E14 轨迹监督；I12/E16 数据选择、失败/干预经验 |
| R2 预测对象与规划计算 | 在长时任务、精度和计算预算间找到更好的预测/规划结构 | I08/E13 多时域与混合方法；I13/E19 变化后的复用/更新 |
| R3 任务对齐与复用 | 既改善当前任务，又保持新目标/新规划器上的用途 | I10/E17 query 注入位置、共享表示和轻量任务分支 |
| R4 状态、记忆与不确定性 | 在遮挡、隐藏动力学等实际条件下做对动作 | I07/E11 历史、belief、主动获取信息 |
| R5 可靠使用与恢复 | 模型不可靠时，仍能以合理成本完成任务 | I11/E18 重规划、反馈、适配、回退 |

这些方向互相共享模型、环境和经验；**一篇近邻、一项 null、一种简单修复，都不自动关闭整个方向。** 最终论文可以是有效的新方法、设计原则、系统性解释、评测贡献或组合；不强制先发现全新的失败模式或普适定律。

## 执行方式

先接续已有资产，在 TwoRoom/Wall 与 Push-T/Cube 中选择适合的原生任务。强基线复现、文献定向补读、方法小试、误差分析可以并行。默认从 R1 或 R2 启动，但根据已下载资产和真实结果调整，不锁定 E14、不锁定“换门”故事。

实验卡是可修订的记录，不是过关游戏。探索阶段做有解释力的比较；准备因果/机制主张时再补对应控制。新方法从一开始就允许，只需写清它针对什么问题、受哪篇工作启发、怎么判断是否有用。

[资源约束](../../RESOURCES.md)：研究室十几张 A100、8 张 RTX PRO 6000；实习处16张 H20；弱网络/弱磁盘/弱跨节点。使用独立单卡/单节点任务、节点内缓存、checkpoint 复用；不假定跨地点数据可混用。并行数由实际授权和 I/O 决定，不把“只有两条 ACTIVE”误读成“只能跑两个实验”。

## 当前最值得开挖的两个方法假设

**H-A / R1：Planner-Boundary Branching (PBB)。** 在相同新增环境交互预算下，把same-state counterfactual branch数据优先采在CEM candidate ranking不稳定、可能改变selection的state；先做data-only方法，和random/coverage/global uncertainty/task-aware acquisition比较。近邻OnlineWM、Task-Sufficient WM、ToIA、D-JEPA/AD-WM提供强支点而非禁区。

**H-B / R2：Planner-Stage Multi-Fidelity。** Fast-LeWM/cheap direct predictor筛大量候选，high-fidelity recursive/refined predictor只重评elite边界候选；在fixed wall-clock下比较pure cheap/pure expensive/random refine。Fast-LeWM已做direct prefix，DeepJEPA已做transition-depth adaptive compute，因此我们的差异必须落在**candidate-stage fidelity allocation**及其与transition-depth的互补性。

两者都属于“重要问题 + 便宜决定性实验 + 大量独立确认”的RC-aux式科研经济学；只是当前起跑点，不是预先宣布的论文主旨。

## 第二波也已具体化

- **H-C / R3：Selective Query Specialization** — query只在cost/proposal/轻量adapter中选择性进入，比较seen-task gain与unseen-goal reuse。
- **H-D / R5：Utility-Gated Recovery** — 用matched fork ledger学习什么时候HOLD / FEEDBACK / UPDATE / REPLAN真的值得做，而不是error大就更新。
- **H-E / R2/R3/R5：Selective Revaluation** — reward/query、局部transition、全局dynamics变化后，比较最小充分更新模块与full update。

它们不是“被近邻挤剩下的小角落”，而是从最新query-sufficiency、feedback/TTT、revaluation工作继续往**可训练方法 + planning consequence**发展。第一波H-A/H-B更优先只因为单位时间信息增益高。

## 当前证据与交付边界

- **科学主张：0。** 论文报告值不是我们的实验结果。
- D1 完整数值复现未完成；D2 Fast两任务原生加载/训练步/闭环完成，LeWM有限数据训练已运行；均使用节点数据缓存。
- E13：两任务20% TOP-M-SCREEN分别恢复96.9%/99.99%模型elite，未见实际耗时收益。扩到[256个长短目标/512配对episodes](results/E13_20261002_fidelity_value.json)：TwoRoom75步goal FULL300成功27/64、CHEAP900为47/64；PushT75步两者9/64。尚无self-consistency refinement控制收益；共卡timing不用于speedup。
- E16：[全部公平三pipeline](results/E16_20261003_optclone_independent_seeds.json)NOADD7/16/19、uniform32/15/18、GLOBAL-U19/20/27、PBB20/11/13（各48），AdamW隔离guards全过。GLOBAL三个正gain，PBB不稳定，uniform首seed优势未重复；pipeline包含data/eval/init变化。旧污染模型比较降级，不作为当前证据。
- [全部起点factual controls](results/E00_E13_E16_20261002_factual_controls.json)：TwoRoom128/128与E16 48/48成功、状态/初始pixel误差0；PushT75步63/64成功且有显著物理恢复残差，保留所有起点并限制解释。
- E18：[反馈/重规划fork](results/E18_20261002_recovery_forks_seed0.json)与[六response/768 continuations](results/E18_20261002_short_updates_seed0.json)已完成。nominal导航FEEDBACK16/32、短head/dynamics均12；shift下为7/9/6。适配训练误差下降但效用弱；没有router或稳定恢复方法证据。
- E13时域×搜索宽度384episodes已完成：[结果](results/E13_20261002_horizon_breadth.json)。同released Fast，H25N300/H25N900/H75N300在导航长goal为19/25/8（各32）；操作长goal6/7/0。只限定此backbone/terminal cost，不否定长时域母问题。
- [E17 proposal320episodes](results/E17_20261002_query_proposal.json)：导航远proposal15/16、ZERO90014/16、goalshuffle14/16；操作远6/4/5，query-specific作用未证实。
- [E18连续适配288episodes](results/E18_20261002_continuous_adaptation.json)：nominal操作FROZEN/PREDLAST/+PROJECTOR=5/4/3（各16），尚无稳定success收益；不称完整AdaJEPA复现。
- [E13经典动作参数化256episodes](results/E13_20261003_action_basis.json)：导航远LINEAR5-N300/ZERO300/ZERO900=14/10/14，操作远3/3/4；经典强baseline、单seed，不当新idea。
- [共同初始计划256episodes](results/E13_20261003_commitment_cadence.json)：操作近EX5/10/25/5warm=5/3/14/4，warm未修复；time-index失配已有强近邻，不能归因velocity。
- [E17代价352episodes](results/E17_20261003_continuation_cost.json)：导航远NATIVE10/EXEC6/REAL9/WM9/MIX8，操作近EXEC14/REAL7/WM7/MIX8，各16；imagined-domain训练未胜强baseline，不外推所有goal value。
- [E11状态估计384episodes](results/E11_20261003_latent_observer.json)：操作nominal/gain/moment OBS4/4/3、PREFIX5 11/10/10（各16）；prior/fixedgain不胜经典time-alignment强对照，不称新idea。PushT原生7D距离含velocity，不能叫纯位置进展。
- [E16数据×计算](results/E16_20261003_data_compute.json)全部完成：100轨迹在1680/5650updates为13/38，1000轨迹为19/21，released正控39（各48）；独立优化器/RNG审计通过，不能把equal-update差称数据价值规律。
- [E16数据×目标](results/E16_20261003_objective_matrix.json)全部完成：NO ONE/TF/OPEN=21/14/16、UNIFORM=11/24/19（各48）；单pipeline、额外监督/regularizer目标改变，未胜充分训练强base。
- 运行中：1000轨迹固定30/100epochs训练曝光控制；A6 Fast64physical banks已sealed，LeWM参考评分缺依赖的失败保留并准备隔离重试；E17任务几何代价在CUDA数值预控，尚未训练/闭环。精确process/artifact见当天日志。
- D5/D6 问题—方法地图、近邻定位、可生长方案和实验入口：已整理，随实验更新。
- 尚无候选论文；目标会议具体届次由证据成熟度决定，不按文献数量或“没有撞车”决定。

大文件在标准 HF cache 与 `/home/xiang/.cache/latent-wm-results/`；节点内数据使用 `/tmp/latent-wm-data/`。版本、hash、重建入口见 [ASSETS](ASSETS.md) 与结果文件。

## 这次整理改变了什么

21 份互相竞争的顶层说明合并为6份；实验与 idea 编号去重。旧的 M1/M2/M3、Tier、Wave、红区、强制审计门槛不再是当前执行规则。R1–R5 保留，具体方法/种子可以增加、改写或合并。

完整旧目录（包括整理期间新增的I13/E19）以同一 Git tree 保存于 [历史快照](../../archive/latent-world-model-planning/pre-consolidation-2026-10-02/README.md)，包括原始文献笔记、所有重复方案和旧日志。没有删掉实验结果来整理叙事。映射与检查说明见 [整理记录](logs/2026-10-02-consolidation.md)。

状态与资源分配仍由人决定；本地 agent 可在授权的本工作台内自主完成实验、分析、修订方法和下一轮研究，不需要每个 job 回来请示。
