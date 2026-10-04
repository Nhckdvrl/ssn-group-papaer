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

## 当前优先：有限数据下真实动作后果学习

2026-10-04人审后，优先[I14/E20](experiments/E20-action-consequence-learning.md)：同样合法common-reset分支数据，联合训练表示/动力学，比较plain prediction、误差重权、后果目标及deterministic/probabilistic inverse；完整近邻与native闭环仍是必要证据。备选[I09/E14](experiments/E14_behavior_policy_semantics_intervention.md)短片段可执行组合，需真正value传播/goal-policy强对照。基线校准与方法开发并行，PBB v0/self-consistency/tiny-update当前降序，不关闭R1–R5。

## 保留的首轮方法假设（当前降低追加优先级）

**H-A / R1：Planner-Boundary Branching (PBB)。** 在相同新增环境交互预算下，把same-state counterfactual branch数据优先采在CEM candidate ranking不稳定、可能改变selection的state；先做data-only方法，和random/coverage/global uncertainty/task-aware acquisition比较。近邻OnlineWM、Task-Sufficient WM、ToIA、D-JEPA/AD-WM提供强支点而非禁区。

**H-B / R2：Planner-Stage Multi-Fidelity。** Fast-LeWM/cheap direct predictor筛大量候选，high-fidelity recursive/refined predictor只重评elite边界候选；在fixed wall-clock下比较pure cheap/pure expensive/random refine。Fast-LeWM已做direct prefix；最新[核心阅读](literature/CORE_READINGS.md)已纠正旧candidate-vs-transition区分：DeepJEPA也处理candidate–time分配。当前尚缺真实高保真优势及实际延迟收益，不能把该区分当作已成立增量。

两者保留为首轮探索及其已有证据；当前追加优先级已降低，后续投入以本页顶部与RESEARCH_PLAN为准。

## 第二波也已具体化

- **H-C / R3：Selective Query Specialization** — query只在cost/proposal/轻量adapter中选择性进入，比较seen-task gain与unseen-goal reuse。
- **H-D / R5：Utility-Gated Recovery** — 用matched fork ledger学习什么时候HOLD / FEEDBACK / UPDATE / REPLAN真的值得做，而不是error大就更新。
- **H-E / R2/R3/R5：Selective Revaluation** — reward/query、局部transition、全局dynamics变化后，比较最小充分更新模块与full update。

它们不是“被近邻挤剩下的小角落”，而是从最新query-sufficiency、feedback/TTT、revaluation工作继续往**可训练方法 + planning consequence**发展。这些入口继续保留，不覆盖本页顶部更新后的优先级。

## 当前证据与交付边界

- **科学主张：0。** 论文报告值不是我们的实验结果。
- 2026-10-05最新整批：[matched1056](results/E01_E14_20261005_matched_control_results.json)、[经验利用864](results/E20_20261005_experience_control_results.json)、[Push672](results/E20_20261005_pusht_fresh_control_results.json)全部独立轨迹校对。Push发布24/48原native→分支联合3–6；Nav三数据利用对照无稳定控制gain。source0分阶段value远目标有线索、已有近邻机制；三seed训练已齐、闭环重复中，新geometry×data交互先经CPU/CUDA阳控，尚未确认novelidea。
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
- [E13 A6两模型候选审计](results/E13_20261003_two_backbone_reference.json)已完成并独立复算：TOP20%对LeWM参考elite recall导航近/远=.777/.469、操作=.510/.190；实际参考批次900→90仍约42–44ms。参考模型排序不是真实后果，不支持加速或控制收益。
- [E13 A7真实候选后果](results/E13_20261003_candidate_quality.json)192branches/5545steps完整落盘：Fast/LeWM近目标导航13/13、操作15/11（各16）；factual四组均16/16。上传前计数/hash核对通过，完整独立trajectory/statistics校对待做；不是两种原生CEM控制器比较。
- [E17任务几何代价](results/E17_20261003_task_factor_cost.json)384episodes/24005steps完整落盘：导航远NATIVE25/PREFIX5/REAL-GEO/MIX-GEO/REAL-JOINT/MIX-JOINT=10/7/11/11/12/12；操作近14/11/9/9/10/9（各16）。尚无跨任务稳定收益；extra task labels、共享首计划、训练量边界见卡，独立完整校对待做。
- [E16固定data独立trainseeds](results/E16_20261004_fixed_data_trainseeds.json)原seed0/新seed1/2为38/19/36（各48），新两个run完整，保留全部种子；不能称充分训练稳定等效released。[曝光终点100epochs/u56500](results/E16_20261005_exposure_endpoint.json)已complete并校对39/48，约同epoch但10xupdates/单source，不当数据only结论；新48两接口强参照正在部署。
- [E20整批联合训练](results/E20_20261004_joint_candidate_results.json)15/15完成并经checkpoint/optimizer/RNG/query复核：PLAIN8/11/9、CENTER12/11/8、PROB10/11/11（每source12真实bank查询），开发差值CI仍跨零。新48独立episode factual exact；[physical](results/E20_20261004_fresh_physical_control_results.json)/[native](results/E20_20261004_fresh_native_control_results.json)各15方法与三BASE整批校对，CENTER对PLAIN分别−4.9pp/+2.8pp、CI均跨零；跨节点失败完整保留，未放宽守卫；[PushT五arm](results/E20_20261004_pusht_candidate_results.json)已完整训练校对：4/4/4/3/4（各12），没有稳定开发gain；尚无成立novel方法。
- [AD-WM完整发布参照](results/E01_20261004_adwm_full_reference.json)：同新48原native近24/24、远18/24；physical20/24、8/24，全部96轨迹成功判据/源hash/native parity经独立复算。仅一发布seed，训练data未匹配，不是完整论文数字复现或同data方法因果gain。
- [跨节点复现校对](results/E20_20261004_crossnode_restore_audit.json)：两节点48条factual位置轨迹逐点exact；A100 46/48 warm图像≤1 uint8差，RTX全部exact，原因不确定。主方法闭环不放宽守卫、不删anchor，改同RTX复跑；不是方法负结果。
- [E01/E14完整训练支点预控](results/E01_E14_20261004_matched_learning_preflight.json)CPU/CUDA actual loss/gradient/SG/Bellman/两阶段隔离/native parity全过；九个ABS/RES/FULL-AD×三seed与两个JOINT/SEPARATE支点共11次5650训练已全部完成并经[完整endpoint审计](results/E01_E14_20261005_matched_endpoint_audit.json)。训练终点的同48、physical/native评测已入队（11模型共1056episodes），整批效用尚未齐；[E20数据利用九run](results/E20_20261005_experience_candidate_results.json)全部训练校对，小bank IID12/12/11、仅REPLAY11/11/11（各12）；newgoal两接口与Push672episodes正在实际运行，尚非novelidea。
- D5/D6 问题—方法地图、近邻定位、可生长方案和实验入口：已整理，随实验更新。
- 尚无候选论文；目标会议具体届次由证据成熟度决定，不按文献数量或“没有撞车”决定。

大文件在标准 HF cache 与 `/home/xiang/.cache/latent-wm-results/`；节点内数据使用 `/tmp/latent-wm-data/`。版本、hash、重建入口见 [ASSETS](ASSETS.md) 与结果文件。

## 这次整理改变了什么

21 份互相竞争的顶层说明合并为6份；实验与 idea 编号去重。旧的 M1/M2/M3、Tier、Wave、红区、强制审计门槛不再是当前执行规则。R1–R5 保留，具体方法/种子可以增加、改写或合并。

完整旧目录（包括整理期间新增的I13/E19）以同一 Git tree 保存于 [历史快照](../../archive/latent-world-model-planning/pre-consolidation-2026-10-02/README.md)，包括原始文献笔记、所有重复方案和旧日志。没有删掉实验结果来整理叙事。映射与检查说明见 [整理记录](logs/2026-10-02-consolidation.md)。

状态与资源分配仍由人决定；本地 agent 可在授权的本工作台内自主完成实验、分析、修订方法和下一轮研究，不需要每个 job 回来请示。

## 2026-10-04方向审阅入口

建议按本页 → [研究计划](RESEARCH_PLAN.md) → [痛点与失效记录](PAIN_LOG.md) → [主张账本](CLAIMS.md) → 对应实验卡/results阅读。**已有大量探索结果，尚未找到经强基线、独立训练种子和第二任务共同确认的novel方法。** 不应把工程修复、经典时间对齐、充分训练收益直接包装成论文。

当前值得人判断的是问题/方法轴：R1中数据预算、训练曝光和预测目标的相互作用；R2中候选搜索质量与模型评分质量的区别；R3中短经验如何支撑长任务价值与复用。PBB v0不稳定，单纯self-consistency和换cost head未形成可靠收益，但R1–R5持续开放。RC-aux、PLDM、HIQL及近期objective工作提供强基线与idea来源；任何新叙事都需要说清继承和实际增量。此次上传不改变workbench状态、不升级科学主张，不预选论文方向。
