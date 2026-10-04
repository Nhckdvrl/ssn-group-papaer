# 实际痛点与成功记录

已有 E00/E13/E16 工程测量，尚无科学贡献确认。旧版R01–R15是文献/代码风险；完整保存于[历史账本](../../archive/latent-world-model-planning/pre-consolidation-2026-10-02/PAIN_LOG.md)。

## 执行前需注意

- 配置/平台API、checkpoint加载、时间单位和任务信息差异：见[ASSETS](ASSETS.md)。
- 时序标签、negative和latent距离的语义不能自动当作真实最短路、不可达性或物理误差。
- 更换数据同时改变coverage、动作激励等因素；记录并在解释需要时拆开，不把它们作为禁止做方法的门槛。
- 同信息的模型不能被要求恢复不可辨的隐藏状态；完整状态oracle是上界。
- 当前研究问题只由[RESEARCH_PLAN](RESEARCH_PLAN.md)定义；历史“被占/红区/只剩残差”判断不是执行规则。

## 实测记录格式

`P编号｜实际失败或成功｜任务/模型/config/seed｜量级与结果路径/hash｜关联E编号｜解释与下一步`

同时记成功案例、方法无效、简单基线出乎意料地强。不能只收集符合最初叙事的输出，也不要把重复日志当新增科学贡献。

## P01｜调用比例与真实 latency 不成比例（工程测量）

TwoRoom / Fast-LeWM / N=300,K=30,β=1,[2,3],seed=0。8 个 held-out generated episodes 的首/中/末 24 个 bank，3 次实际 GPU timing：FULL-REFINE 平均 57.90 ms；30% TOP-M-SCREEN 58.89 ms；LOWER-BOUND/batch16 用 43.4% 重评却耗时 201.80 ms。wrapper/native scoring 最大差为 0。[E13](experiments/E13_explicit_implicit_matched_pilot.md)、[结果/episode CI](results/E00_E13_E16_20261002_tworoom_engineering.json)。

解释限于工程 bank/此硬件：batch dispatch、CPU selection 和重复 encoding 不能忽略；call fraction 不能写成 speedup。DeepJEPA Appendix D 已明确同类限制，这不是新发现。

原生 TwoRoom、所有方法共享 encode-once cache 后：FULL 35.02 ms、TOP20% 35.00 ms、INTERVAL20% 54.05 ms；问题仍在。[原生结果](results/E00_E13_E16_20261002_tworoom_native.json)。下一步第二任务族与整体搜索预算比较，不凭此关闭 R2。

## P02｜same-state 分支工程接通，公开 setter 精度须另测

两 task 各 64 条分支、88 次 reset、2200 branch/replay controls；8 anchors × 3 replay/task，state 最大绝对误差和 pixel MAE 均为 0。生成数据使用 fresh reset + factual prefix replay，不能据此宣称 dataset setter 恢复完整 physics memory。[E16](experiments/E16_equal_budget_data_value.md) 后续单独做官方 factual-suffix audit。没有 acquisition-effect evidence。

原生 TwoRoom 单独完成：12 factual suffix 误差0/成功12，64 branches与24重复控制误差0；public proxy selector 隔离检查通过。PushT 原生 physics-memory 恢复尚未测，不外推。

## P03｜恢复模型 elite 尚未转化为控制收益（单 seed 小样本）

原生 TwoRoom / Fast-LeWM：20% TOP-M-SCREEN 离线 recall=96.86% [90.58,100]，但8 paired episodes 中与 FULL/CHEAP-300 同为7/8；CHEAP-900为8/8且 decision time仅0.523 s，FULL为1.230 s。7/8的Wilson CI=[52.9,97.8]%，不能声称等价；也不能以8/8宣称CHEAP-900确定更优。[E13](experiments/E13_explicit_implicit_matched_pilot.md)、[结果](results/E00_E13_E16_20261002_tworoom_native.json)。

这说明 offline 模型参照 recall 不足以建立方法价值；下一步保留全部 seed/起点与强 cheap-search baseline，测原生 PushT 后再决定 refinement/search/update 如何分配计算，不局部优化选择器来硬救预设故事。

## P04｜有限expert经验的训练误差下降，规划仍弱；追加数据有待确认信号

[E16全部七方法](results/E16_20261002_equal_data_seed0.json)：同100基础episodes从10到30epochs，train MSE约0.18→0.03–0.06，同16起点成功均3/16；released正控14/16。不能从training MSE推断held-out预测质量或新现象。30epoch后再各600 updates，48未见训练episode目标：NO-ADD9/48、IID17、uniform17、coverage18、GLOBAL-U24、TASK-U11、PBB19。GLOBAL-U相对NO-ADD配对增益31.25pp、episode bootstrap95% CI[18.75,45.83]；PBB20.83pp[4.17,37.50]。一完整数据seed，CI不是train-seed CI；不升级科学主张，不声称新颖性。

实际395 union branches/9875执行steps+24重放/600控制steps；每policy逻辑消费2000steps，IID来自预收集官方轨迹。所有policy在hidden文件生成前锁ledger；训练仅读取自己购买keys；NO-ADD同训练计算。[48 factual controls](results/E00_E13_E16_20261002_factual_controls.json)阳性48/48、state/pixel误差0。下一步独立seed1/2全pipeline确认、真实candidate后果、第二任务/data regime；不只优化PBB score。

## P05｜短期预测的额外一致性计算没有解决长目标规划

[E13 A2](results/E13_20261002_fidelity_value.json)：每task×goal-offset64整episode起点，FULL300 vs CHEAP900共512闭环episodes。TwoRoom25成功58/64 vs63/64；75成功27/64 vs47/64（cheap−full31.25pp、paired episode CI[20.31,42.19]）；PushT25为58/64 vs61/64；75为9/64 vs9/64。Goal-offset不是最短路径标签。此结果仅比较β=1 direct/decomposed consistency与更宽cheap CEM，不外推所有refinement或LeWM/DeepJEPA。

短goal最初8起点出现ceiling，已扩全部预定目标；long PushT存在真实困难，也有public-restore混杂，全部保留。下一步应改变预测对象/规划时域/目标复用/反馈等方法轴，不能把提高模型elite recall继续当最终目标。A2后来共卡，timing明确降级；不按该时间主张speedup。

## P06｜PushT公开restore的长时残差，不能误作模型失败

[全部304 factual controls](results/E00_E13_E16_20261002_factual_controls.json)：TwoRoom128/128+E16 48/48，位置与初始pixel误差0；PushT25阳性64/64、max position3.86pixels/angle0.075rad；PushT75阳性63/64、max position92.48pixels/wrapped angle1.079rad。公开7D state没有完整physics memory，长suffix偏差不能称精确反事实，也不能简单拿去归因WM。需查看残差分布/接触状态；所有起点保留，恢复协议单列。FIRM已明确public interface restore的边界，本记录不把接口限制包装成新idea。

## P07｜闭环增益未伴随旧candidate分布内regret改善

[E16统一bank](results/E16_20261002_decision_audit_seed0.json)48起点×64候选×七模型，NO-ADD/GLOBAL-U/PBB真实selected regret分别14.264/15.287/14.089pixels；配对差值区间都包含0。此bank由共同base CEM中期生成，不能代表各新模型完整搜索分布；也不能事后因此换bank来硬找正结果。现有闭环增益可能来自proposal distribution、后续反馈或encoder geometry，未核对。保留该null，后续从更广方法轴/第二task理解数据作用，不宣称PBB修正动作排序。

## P08｜观测反馈有局部收益，未知transition变化还需要别种response

[E18](results/E18_20261002_recovery_forks_seed0.json)在nominal TwoRoom HOLD12/32→FEEDBACK16/32，但action gain0.7下6→7；PushT nominal4→7（更多搜索9），gain0.7下1→0。future utility有任务/条件差异，尚无可部署gate证据。当前方法没有更新transition，本身可能缺乏恢复能力，不能因为误差大却replan无益就判母问题无价值。完整prefix重放same-state/pixel误差0，原dataset的PushT memory limitation仍保留。下一批增short head/dynamics update，再看response set价值与部署feature，而不是局部调error阈值。

P04确认补记：[三seed](results/E16_20261002_independent_seeds.json) NO-ADD9/19/22、uniform17/18/15、GLOBAL-U24/16/23、PBB19/13/15，每组48。G对NOADD+15/−3/+1，PBB+10/−6/−7。首轮大增益不稳定；现有数字不支持有效新采样方法。joint pipeline seeds、seed0 resume和硬件差异保留，不能解释成单一initialization效应。母问题仍重要，下一轮扩数据利用/预测对象/恢复方法轴，不反复救PBB公式。

P08短适配补记：[768 continuations](results/E18_20261002_short_updates_seed0.json)同RTX FEEDBACK/HEAD/DYNAMICS，nominal导航16/12/12，shift7/9/6，分母32；PushT nominal7/6/4，shift0/1/0。对3样本训练误差明显下降，未来utility未稳定改善；不据此判适配无价值，也不先造gate。512旧baseline success全部复现，动作/距离/latent features跨硬件不完全一致，新增method对同RTX baseline作配对。下一批已展开数据利用×目标（R1/R2）与预测时域×搜索广度（R2），避免只优化短更新阈值。


## P09｜公共CPU optimizer step别名破坏方法隔离

**撤回旧E16比较的严格data-only解释和“PBB被强基线吸收”判断，待公平重跑。** 独立CPU复验发现torch2.7.1 AdamW加载公共CPU state时会保留`step` tensor引用；多方法顺序运行使源state计数累加。权重/数据/gradient steps相同，但初始bias-correction历史不同。旧seed0七方法、seed1/2四方法及由这些模型计算的decision audit受影响；数值和原始文件全部保留，不能用于方法优劣或排序机制的因果结论。六方法objective matrix也受影响，已停止自身未完成进程、保留partial与invalidation artifact。

[可复现校对](results/E16_20261002_optimizer_audit.json)。修复为每方法deepcopy完整optimizer state，并断言初始steps相同、源steps不可变、结束steps=初始+updates；所有原方法/seed/目标重跑，不筛选方法，不追加数据，不重训base。base checkpoint文件未被改写；E13无训练、E18每fork新optimizer均不受此alias影响。科学主张此前为0，继续为0；C00工程L1保留。


P05/A3补记：[384episodes](results/E13_20261002_horizon_breadth.json)，H25N300/H25N900/H75N300，导航长goal19/25/8、操作长goal6/7/0，各32。长递归在四task/range都退化；这是更换方法轴的依据，不是R2失败。近邻Planning Limits指出即使perfect dynamics仍可能受cost/局部feedback限制，且其长rollout有益；本实验模型/预测对象/cost/搜索维度不同，需从query-in-proposal/cost和训练对象分辨竞争解释。

E18连续适配运行前独立校对：[CPU物理控制](results/E18_20261002_physics_preflight.json)确认PushT mass/moment同比例缩放不改transition（16轨迹全0、15条有接触）；moment-only×2则15/16改变。保留原控制、在GPU运行前修订physics为moment-only，不按适配success选条件。停止仅自身waiting queue并重启；没有废弃GPU方法结果。

P05/R3补记：[E17全部320episodes](results/E17_20261002_query_proposal.json)，导航proposal16/15 vs ZERO90015/14，goalshuffle15/14，各16；PushT long proposal6 vs9004/goalshuffle5/GCBC0。组合可能受generic action prior帮助，query-specific作用未核对。GCBC弱不是强邻居被击败，CI宽、一headseed；接下来action trajectory structure/state-only prior、cost/query placement与数据regime是竞争设计，不重复微调同head。

P05/经典优化对照：[A4全部256episodes](results/E13_20261003_action_basis.json)。导航远LINEAR5-N300 14/16，ZERO30010/16、ZERO90014/16；操作远3/3/4。前者配对CI含0，后者null；低维搜索是强baseline，不把generic action prior重新命名成query贡献。两task结构不同，需要预测对象、目标代价、控制反馈的竞争解释，不能只优化节点数。

P08/连续适配：[288episodes](results/E18_20261002_continuous_adaptation.json)，名义/0.7gain/physics，导航FROZEN/PREDLAST/+PROJECTOR=10/10/9、8/8/9、8/8/9；操作=5/4/3、3/4/3、3/2/3（各16）。14,313真实steps、公共5步state/pixel误差0。未见稳定success收益，操作nominal distance utility反而下降；训练误差不等于适配价值。此Fast/目标/lr不称完整AdaJEPA复现。频繁replan5名义操作FROZEN5/16 vs E17整25执行14/16跨plannerseed，不能归因；A5锁共同初始plan/5-10-25cadence/warm排除优化重启，R4历史/反馈表示仍是竞争解释。

P04公平重跑seed0：[七方法](results/E16_20261003_optclone_seed0.json)NO/IID/uniform/coverage/global/task/PBB=7/18/32/27/19/13/20，每48。uniform对NO+52.08pp、episodeCI[35.42,66.72]；PBB对uniform−25pp、CI[-41.72,-6.25]。全部AdamW1680→2280/source不变；只能限定此pipeline，不沿旧污染模型排序/机制。两个原seed继续，数据×compute/训练对象已并行；强knownbranchbaseline是方法生长起点，不关闭R1。

P08共同计划对照：[A5完整256episodes](results/E13_20261003_commitment_cadence.json)，操作nearEX5/10/25/5warm=5/3/14/4，各16；同初始plan排除初始seed差，warm不能修复但不能归因velocity。terminal25score/execute5时间失配已有HiddenFailureModesownership；固定cadence observer与cost/预测结构是竞争方法轴。导航nativephysicalclip缺失在score的混杂已独立发现，须强对照。

## P10｜预测评分与实际动作接口不一致（工程校对）

[独立CPU/全部command统计](results/E00_E13_E16_20261003_action_interface_audit.json)：TwoRoom真实step裁剪physicalcommands到[-1,1]、MacroCost/LeWMNativeCost原生评分未裁剪；A5全部128导航planfiles真实issued动作超界41–73%、max20.42，E16bank3072/3072序列含超界、primitive44.85%。4真实CPUsteps验证[2,0]与[1,0]导航状态差0；PushT完整state差374.15，后者并不clip。只能确认接口/覆盖混杂，未证明success因果或data收益由其解释。cost-onlyclip/renorm强baseline已加E17，原nativeCEMrawelite更新不变；FlexiWorldE.2已有相同原则，不当novel贡献。未来新方法必须面对actual-action baseline，R1/R2母问题不因此关闭。

P04全部公平三pipeline：[完整结果](results/E16_20261003_optclone_independent_seeds.json)NO7/16/19、uniform32/15/18、GLOBAL19/20/27、PBB20/11/13，每48。GLOBAL三个正gain，PBB和uniform跨pipeline不稳定；不能从seed0最强说普遍data选择原则。训练计算对照BASE100全部快照已完成560/1680/5650=7/13/38，BASE1000未complete，不升级data×compute结论；充分训练强baseline是后续方法必要参照。

P05/R3代价完整补记：[352episodes](results/E17_20261003_continuation_cost.json)，导航远NATIVE/EXEC/REAL/WM/MIX=10/6/9/9/8，操作近14/14/7/7/8（第一个14为EXEC、第二为COS），各16。imagined calibration未胜REAL/head未胜强native；不能将只对弱EXEC的局部gain包装成方法成立。训练fit不能代替candidate utility，RC-aux的joint representation/budget negatives与L2耦合不是这个小head负结果。

P08/R4完整补记：[384episodes](results/E11_20261003_latent_observer.json)固定5步cadence，Pushnominal/gain/moment OBS4/4/3→PREFIX5 11/10/10，各16；prior/filter均不胜此classic强baseline。下一方法须对齐执行目标后再验证history/feedback，不调融合权重救null。原native task_distance含7D速度与未wrap角度，和success位置/角判据不同，不能从其均值归因失败尾部或纯position风险；原raw/读数保留，位置分解仅POST-HOC辅助。

P04训练对象完整补记：[六格](results/E16_20261003_objective_matrix.json)NO ONE/TF/OPEN21/14/16，UNIFORM11/24/19，各48。branch效应随此训练设计变号，但ONE/LONG labels+SIGRegframes不匹配、onepipeline/weakbase，OPEN无稳定胜TF；只作数据利用×预测对象下一研究来源，不能直接升因果或顶会叙事。额外训练38强基线必须保留。


2026-10-04 P04训练随机性补记：[固定data独立重训](results/E16_20261004_fixed_data_trainseeds.json)同BASE100/原norm/eval48/5650updates，seed0/1/2成功38/19/36。两个新run完整无failure，eval48计数/anchor SHA一致；完整独立optimizer/RNG审计待做。不筛19，不以38/36称充分训练必然接近released；计算曝光解释仍重要，但存在训练随机性需要分辨。E20三source方法matrix全部保留，增加数据与额外训练必须用PLAIN同曝光解释；不把弱source增益当机制成立。

### 2026-10-04｜P04/P10：同数据动作目标的收益不能由单seed或小bank确认

[E20整批15run](results/E20_20261004_joint_candidate_results.json)严格同数据/曝光/freshoptimizer与同sourceu0/query矩阵，PLAIN8/11/9、CENTER12/11/8、PROB-INVERSE10/11/11（每source12真实候选查询）。CENTER source0完美但source2低于plain；双向开发CI差[−.1667,.3611]，PROB[−.0278,.3333]，均未建立稳定收益。概率inverse对照目前比强推centered新loss更有价值，但它不是novelty，也不是完整AD-WM。重要下一判断是新sourceepisode闭环、跨任务、强同数据replay与完整近邻，不是继续围绕λ局部调参。原science claims0保持；不是方法母问题关闭或预选paper narrative。

2026-10-04 P10工程校对：[跨节点完整复算](results/E20_20261004_crossnode_restore_audit.json)两节点48条factual真实位置轨迹全部exact；A100 46/48 warm图像有≤1级uint8差、RTX全exact，具体数值原因不确定。三个A100队列均在第一anchor守卫停止，效用rows0；失败不作方法负结果，不放宽守卫、不挑匹配anchor，主方法比较迁到原RTX同hardware。完整AD-WM参照原native42/48提示强方法可用，但其数据量/训练均未匹配，不能归因inverse或当ours已胜/败的公平结论。

### 2026-10-05｜P04/P10：离线后果线索尚未转化成稳定新任务收益

[E20 physical](results/E20_20261004_fresh_physical_control_results.json)与[strong-native](results/E20_20261004_fresh_native_control_results.json)各15方法+三BASE共864episodes整批独立trace/state/success/checkpoint复算PASS。physical PLAIN20/32/21 vsCENTER19/27/20；native PLAIN26/29/27 vsCENTER25/34/27，各48/source。CENTER相对plain physical−.0486 CI[−.1597,.0556]，native+.0278[−.0833,.1458]。小bankCENTER12/11/8不能支撑一般控制收益；任务/目标/controller都改变，不能归因单metric。三个train sources共享任务，不膨胀样本量。强native中plain相对原BASE30/19/26也非三个正gain，新增经验价值尚未确立。

下一竞争解释是batch经验覆盖、额外五future训练、旧经验保留，以及完整residual/learned-action/价值表示机制。E20事前锁定IID-BRANCH/REPLAY-ONLY/MIX三arm×三source；仅成熟必要对照，不是新idea宣告。E01九完整matched训练、E14 joint/sep继续完整终点评测，不救CENTER系数、不关闭R1–R5。原native可发行未匹配AD42/48是强参考，不作同数据loss归因。科学主张0保持。

2026-10-05 P04/P10数据利用补记：[全部九run开发审计](results/E20_20261005_experience_candidate_results.json)IID12/12/11、REPLAY11/11/11、MIX11/10/10 vsGROUPED-PLAIN8/11/9，各source12已见状态上的新branch查询。IID差+.1944 CI[0,.4167]；单纯原经验replay+.1389[−.0556,.3889]，表明新增反事实价值不能由更好的bank读数确认。成熟shuffle/replay对照有信息，但不是论文增量；强closedloop全matrix仍待齐。下一问题是有限经验怎样同时教会动作后果与保留可复用规划用途，不归因SIGReg/batch或遗忘机制、不救CENTER、不围绕12query局部打磨。

### 2026-10-05｜P04/P05/P10：经验应怎样变成可复用规划能力

完整[Push闭环672](results/E20_20261005_pusht_fresh_control_results.json)原native released24/48，分支联合PLAIN5、各aux3–6；physicalreleased21、分支3–6，完整AD发布参照26/29（数据未匹配）。单transferseed开发，训练后能力丢失真实可复算，但原因未定位，不宣称表示漂移/SIGReg导致或干预数据普遍有害。Nav[经验利用864](results/E20_20261005_experience_control_results.json)IID/REPLAY/MIX对GROUPED原native−4.17/0/−2.78pp，全部source+anchor CI跨0；小bank近完美不是新goal控制功效，后果学习与规划复用需要分开验证。

[匹配value支点](results/E01_E14_20261005_matched_control_results.json)source0 SEP远goal physical17/24 vsABS7、native13vs9，near分别16vs17、19vs21；总体gain在强nativeCI跨0。Value-Guided JEPA已拥有Sep机制，不是novelty；两个额外seed六value终点已完成且全部audit，闭环重复正在运行。Stage4 conditional2×2固定PRED/VALUE geometry×FACT/MIX/common reset decoder，分辨有限经验在表示/动力学上的用途；priorgeometry训练预算不同显式报告，不自动合并研究narrative，不沿CENTERλ或bankquery优化。R1–R5持续开放，science claims0。

### 2026-10-05｜P04/P05/P10：可靠value支点与经验效用的分离

[三seed完整闭环](results/E14_20261005_three_seed_control_results.json)：SEP native32/34/39 vssame-seed ABS30/23/24（各48），整体+19.44pp、paired source+anchor95%CI[2.08,36.81]；远24目标13/17/18 vs9/6/5，近平均无收益。三训练source与全部任务保留。已有Value-GuidedJEPA机制可靠，不是ours novelty，也非一般跨环境确认。

[geometry×data四cell384控制](results/E20_20261005_geometry_control_results.json) native29/26/36/36、physical25/24/36/33（PRED-FACT/MIX、VALUE-FACT/MIX各48）；两geometry内MIX差与交互CI均含0，没显示goal geometry使分支data稳定有效。prior训练预算不同，不作objective-only解释。不能把value优点与CF混合相加就写成新方法。完整[训练审计](results/E20_20261005_geometry_module_endpoint_audit.json)通过。

[完整RC-aux384](results/E01_20261005_rcaux_full_control_results.json)原head ON/OFF、H1/H3全部合法任务/真实成功复算：native38/33、37/34（各48），full312keys含9head/原criterion/官方scaler；训练data未知不与own100差值作因果。强近邻确实可用，这提高下一方法证据门槛，不关闭母问题。

Push joint更新控制损失已确定，但机制未知；新增两模块隔离actual训练全部2000/预控/独立checkpoint-accounting PASS，完整新任务192控制实际运行中。不叫encoder遗忘，不按小bank或partial结果救局部设计。当前科学主张0、PROPOSED不变。

Stage5整批覆盖上述running：四groups192实际Push控制complete，独立完整trace/checkpoint/source/normalizer/初始25D状态/native成功/全部48分母与两interface审计PASS，见E20_20261005_pusht_module_control_results.json。DYNAMICS-ONLY native12(近11/远1)、physical9(8/1)；GEOMETRY-ONLY native12(10/2)、physical8(6/2)，发布24/21、原joint5/6（各48）。两隔离native对发布均−25pp pairedCI[−37.5,−12.5]。冻结减轻joint损失但不保住发布能力，不能简单归因仅encoder漂移；两模块职责仍需和experience/model-use/coverage一起理解，单seed不当一般定理。原两个RTX3584419/3584420已自然退出；不重启unique run、不将freeze包装成newidea。


### 2026-10-05｜P04/P05：预测对象与规划表示存在可追查的交互

E13A8 shared Fast head/capacity/初始化、same100事实35stepclips、两者部署T1，384闭环完整审计。PRED DIRECT/LOCAL native31/29、physical20/21；VALUE39/22、44/19（各48）。withinVALUE direct收益+35.42pp CI[22.92,50]、+52.08[37.5,66.67]，withinPRED CI跨0。完整H3 SEP32/33、RC38/34参照保留：VALUE-DIRECT native未显著胜RC，physical优于发布RC的比较训练未匹配。两个前端prior5650/2825且目标不同，不能说Bellman geometry本身因果造成非Markov、direct普遍优于recursive。单source/共享开发48不是新方法确认；旧prior/H3/targets/sampling与compute差异单列。证据[E13A8](results/E13_20261005_predictive_object_control_results.json)。

价值在于可以检验重要设计问题：同一latent承担任务比较、动态状态、预测结果时是否存在用途张力，怎样改预测对象/训练条件改善实际控制。近邻Value-GuidedJEPA App7已试两表示（其WS未改善）；ProWorld在Euclidean z递归后投影hyperbolic goal space，不能claim首次分角色或AR在goal geometry不可用。A9八独立source1/2重复训练已完整审计PASS，正式全768控制重跑中；首版controller种子覆盖导致全批输出排除并记录CLAIMS，A8及模型未受影响。不以弱LOCAL为solebaseline、不局部调prefixλ，不改变已审路线；下一实验需区分history/conditioning、真实目标代价与candidate质量，并扩操作任务或变化后的复用。


A9覆盖上一pending：三source完整1152控制已审计，PRED direct/local native31/42/36 vs29/39/35；VALUE39/40/34 vs22/13/32。withinVALUE+31.94pp CI[4.17,56.25]，但source2仅+2/48。physical交互CI[−4.17,62.5]含0；DIRECT对strong旧SEP与RC两个接口CI全含0。不能只报相对弱LOCAL的大gain而说新idea已确认。保留重要的表示用途×预测对象问题，增加E14G0真实goal-policy使用轴，研究母问题不缩成单框架的局部decoder优化；[整批源/轨迹/CI](results/E13_20261005_predictive_object_three_seed_control_results.json)。


### 2026-10-05｜P04/P05：事实经验经独立policy使用可强于候选搜索

E14G018heads/1728完整闭环与actualCPU/CUDA/训练终点/原Policy/raw动作/源hash/全部native事件校对PASS。PRED GC-IDM43/46/44、samegoal GCBC43/44/44 vsDIRECT31/42/36（各48）；GC-IDM vsDIRECT +16.67pp CI[4.17,29.17]，成熟基线收益而非新方法。VALUE GC-IDM38/38/39、GCBC41/41/41、PAIRWISE42/30/40；PRED pairwise仅14/19/22，latent用途/监督分布依赖值得继续解释。不能说CEM失效代表事实经验没价值，也不能把零horizonGCBC称新技巧；逐步反馈/优化结构/targets/训练compute一起改变。100-step总体horizon input没有稳定胜samegoal zero输入；50读数只是100-budget前缀，不是独立50预算评测。证据[E14G0全matrix](results/E14_20261005_goal_policy_control_results.json)。下一数据/复用/shift问题要面对这个强支点，不在弱LOCAL小head上做救援叙事。

### 2026-10-05｜P04/P05/P08：策略强支点具有跨任务边界，需要分解数据与状态

[E14G1完整288审计](results/E14_20261005_pusht_goal_policy_control_results.json)：Push GC-IDM/GCBC/PAIRWISE1/2/2，各48（near1/2/2、far全0），所有方法均含原始起点成功1，raw/clip逐动作相同；发布CEM24native/21physical。GC-IDM−released native−47.92pp95CI[−60.42,−35.42]；一个headseed、first86 facts、publishedphi pretrain未知。完整终点/RNG、实际CPUCUDA策略返回、25D起点、angle-position criterion、trace来源均PASS，差距仍可能由head数据覆盖、单帧状态、行为回归、控制反馈/训练差异产生，不能归因唯一机制，也不以导航策略强关闭WM。

连续动作已铺开：A10同初始化/容量/目标/B128/2825的五步BPTT强递归baseline六个sources，终点审计通过后完整576闭环；G2两task samecapacity/goals/init/starts TRUE-HISTORY vsCURRENT-COPY四训练350update已审计，实际v2控制384继续；G3 Push86/860×400/4000updates分离数据覆盖与计算，新860缓存104261事实帧已完成，四head正在原RTX跑。三个解释轴并行，不为DIRECT或history预定故事，不把冻结head负结果升成母问题判决。G2首launcher import collision被源identity assertion在efficacy之前拦住，完整failure/source/log保留，训练终点不受影响。科学主张0。

G2完整384已独立trace/checkpoint/全11warm/raw-vsclip/native-success审计PASS：Nav HISTORY/COPY44/45（near24/24、far20/21），Push3/2（near3/2、far0/0），每48均含initial1，两接口实际逐动作相同。Nav差−2.08pp95CI[−8.33,4.17]，Push+2.08[0,6.25]，一个headseed不含训练方差。见E14_20261005_history_policy_control_results.json；不会把一条额外成功叫memory修复，弱Push原因仍竞争，G3完整数据×计算在跑。原v2两个queue3622514/15自然完成；已等空的A10 source1/2 queue3623770/71实际接管各卡，未重启任何unique run。


### 2026-10-05｜P04/P05/P08：完整coverage、BPTT及反事实矩阵

[E14G3完整384](results/E14_20261005_coverage_policy_control_results.json)：Push86×400/86×4000/860×400/860×4000分别2/2/4/5（每48/native与clip动作相同/含initial1），数据effect400为+4.17pp95CI[−4.17,12.5]、4000为+6.25[−2.08,14.58]；compute及interaction CI含0。单headseed、prior未知，额外数据/计算未稳定恢复已发布CEM24/21能力；不是“数据无用”或belief唯一原因。

[E13A10完整576](results/E13_20261005_rollout_control_results.json)：PRED OPEN native27/42/38 vsDIRECT31/42/36，整体−1.39pp CI含0；VALUE OPEN25/18/11 vs39/40/34，−40.97pp95CI[−56.25,−25]，physical同向−40.28。完整五步BPTT没有吸收VALUE设计差距，但prior任务/预算与BN调用不同，不能据此宣布非Markov原因。全source保留，knownGCpolicy/SEP/RC仍为更强支点。

[E13A11十八模型全8712query](results/E13_20261005_full_branch_matrix_results.json)：VALUE DIRECT−OPEN含goal +39.67ppCI[29.20,50]、leave-goal-out+21.49[17.70,25.41]，25step endpoint regret−28.09pixels[−35.98,−18.91]；PRED不存在同向普适收益。true-latent leave-outoracle每sourcePRED186/196/196、VALUE193/202/197（各484），regret PRED26.75/23.56/17.21、VALUE3.84/2.03/4.19；这是cost用途线索，原44state×11goals聚类、实际branch覆盖和阈值结构强相关，不将484当independentstate或宣称oracle闭环成功。全prefix action-effect误差PRED LOCAL优于DIRECT，说明不能只用latentMSE排序。真实动作后果/goal geometry/预测对象三者仍须配合actualbenefit验证。

A11首次10D-state理解与第二次CPU/CUDA TF32守卫失败各完整保留，v3关闭TF32不放宽容差。producer把ZERO branch0描述成factual，正式reader依据实际branch2纠正annotation，预测/选择未改。A11操作H3 reference仍待做；A12 Push matchedDIRECT/LOCAL/OPEN训练/完整288已完成，独立读数audit进行，不用partial救想法。INTACT两task全joint发布权重下载验hash，isolated runtime严控加载，尚无强邻效用结论。

A12覆盖pending：[全部288审计](results/E13_20261005_pusht_object_control_results.json)PASS，native DIRECT/LOCAL/OPEN2/2/1、physical2/1/1，各48含initial1、far全0；对releasedH3 24/21无能力优势。T1/frozenphi/86facts/一个source，不据此否定direct预测对象或把数据/历史/优化的混杂隐去。完整joint公开INTACT为必要强支点，现venv与其ViT keylayout真实冲突，独立新venv处理而非strict=False。

完整jointINTACT强支点：[两task192已审计](results/E01_20261005_intact_published_control_results.json)Nav37/48（22near/15far）、Push25/48（22/3），native/clip相同、各initial1。发布joint模型恢复Push能力，说明先前冻结policy/小数据T1 Fast1–5不能代表end-to-end latent action family；不将data/容量/训练预算与反馈混杂当唯一representation因果。该强支点支持R3/R5继续研究经验使用、角色与复用，未确认novel方法。


A11操作全2904query完成并独立审计：[H3完整结果](results/E13_20261005_pusht_full_branch_matrix_results.json)。旧12query-state×11goals含goal成功RELEASED69/PLAIN62/GLOBAL54/CENTER53/DET49/PROB44（各132），方法未改善。leave-goal-out真实native可行支持只有8/132=6.06%；全部模型同物理候选，所以低成功有支持上限，不能误解释成ranking/geometry唯一机制。chosen3/2/1/2/2/5，oracle5/4/3/3/3/4；这不是strongmethod证明。old32干预train/12query、一个transferseed、publishedpretrain未知保持，全部状态goal保留。A11导航/操作均已完成，诊断不等于新的control方法；下一步跨完整强支点的实际feedback/utility axis E18F0，不连续救44bank。


2026-10-05 P04/P05/P08｜完整联合模型的wholepolicy反馈频率并非统一改善。E18F0全192新控制+96原参照独立审计PASS：Nav EX25/5/1=37/28/30，Push25/29/27（各48）；EX5−25 Nav−18.75ppCI[−35.42,−2.08]、help4/harm13，Push+8.33[2.08,16.67]、help4/harm0。EX1更多调用未统一胜EX5；单发布seed/开发48，不称feedback无用/可靠router。沿R5/R4同state fork分辨一次换计划、继续已有计划与多次反馈；与SA/DEHP/attention adaptive chunking保持定位，futureutility不能作feature。


2026-10-05 P04/P05/P08｜同state有效恢复空间比wholepolicy频率更有限。E18F1全864独立auditPASS，HOLD/REFRESH15/REFRESH5：Nav nominal37/37/37、gain32/33/33、wind34/36/33，Push25/26/28、16/19/21、20/22/19（每48）。Push gain连续反馈+10.42ppCI[2.08,18.75]，但oracle vsbestfixed Nav0/0/0、Push+1/+1/+3，当前不能据此造复杂gate。momentshift实际改变24/48prefix，不筛零效果/吸收state；F0/F1介入起点/时长不同，不能把Nav harm定位为仅latefeedback。下一F2借RWM reference+完整actor localtarget复用，真实效用胜过模型误差，science0不升。


2026-10-05 P04/P05/P08｜RWM/INTACT原理的目标复用pilot有条件线索，尚未胜strongfixed。F2全576审计PASS：Nav trackingfeedback nominal/gain/wind37/35/37，Push28/23/20（各48），对应REFRESH5为37/33/33和28/21/19。Pushgain vsHOLD+14.58ppCI[4.17,27.08]，vsREFRESH5区间含0；wind导航 vsREFRESH5正，但REFRESH15已36。开放预测current控制Pushgain15/48低于真实feedback23，支持读回实际state有用，不等价全新tracking/因果机制或任意goal泛化。下一组按新episode/三发布seed/fullpolicy确认，不在t10window调λ。科学主张0。
