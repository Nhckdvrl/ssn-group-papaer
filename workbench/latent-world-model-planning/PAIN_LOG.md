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
