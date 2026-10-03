# 主张账本

日期：2026-10-03。已有 TwoRoom / PushT 原生测量、LeWM有限数据训练与七策略pilot；**尚无已成立的科学主张或完整数值复现。** 文献中的成功率不是我们的 L1/L2 证据。

## 待验证的建设主张

| ID | 主张 | 等级 | 证据 | 校对 | 下一步 |
|---|---|---|---|---|---|
| C00 | 官方小模型能在授权单卡完成加载、训练步、CEM 与 simulator episode；工程建设主张 | L1 | [E00](experiments/E00_native_baseline_and_resource_preflight.md)；原生[TwoRoom](results/E00_E13_E16_20261002_tworoom_native.json)/[PushT](results/E00_E13_E16_20261002_pusht_native.json)、[LeWM有限数据](results/E16_20261002_equal_data_seed0.json) | strict LeWM303 keys/18M；native cost controls差0；全部TwoRoom factual controls误差0。PushT public setter有长时物理残差；自写constant-LR循环不是完整Lightning配方。Fast object未独立核对weights；旧optimizer污染比较降级，全部公平三pipeline重跑guards通过 | 原生论文配方与第二task数据效用确认；不称完整复现 |

## 科学主张

尚无。系统调查中的表示／动力学／搜索／数据／历史分支是探索范围，不预先注册其结果方向。

最新可用观察为[全部隔离后E16三pipeline](results/E16_20261003_optclone_independent_seeds.json)：NOADD7/16/19、uniform32/15/18、GLOBAL-U19/20/27、PBB20/11/13（各48），全部stepsguard通过；GLOBAL三pipeline正gain，PBB无稳定收益，但不是固定data训练seedCI。旧首轮/旧独立三seed及decision audit受optimizer alias污染，跨方法因果结论已撤回，见下方降级记录；不把旧数字当本次方法证据。E13/E17/E18/E11分方法轴持续试验，尚无支撑novel方法的成熟证据；科学主张仍0。

后续每条主张需要关联实验卡和结果文件，并区分：观察相关性、受控干预、机制归因、跨模型范围。不能因为方法名字叫 reachability／causal／verifier 就把其输出当作真实可达性／因果／可执行性。

## 作废与降级记录

2026-10-02：PushT 初次工程运行因 native info 无 `state` key 停止；failure artifact 保留，改读原生 observation state 后以相同 seed 重跑，不筛 seed。两 task 的工程 episode 均失败，不计为方法负结果，因为生成数据/action statistics 未对齐官方协议。第一批 TwoRoom 的 harness digest 缺失单列披露，正式批次预先快照源码。

2026-10-02：[E13 A2](results/E13_20261002_fidelity_value.json) 起跑时卡空闲，之后发现其他进程共卡；耗时降为非独占测量，不作speedup证据，成功率保留。PushT75步factual suffix的公开setter重放最大position残差92.48pixels、wrapped角度1.079rad，阳性63/64；不得把全部失败归因于模型或声称精确反事实。所有起点保留，[控制结果](results/E00_E13_E16_20261002_factual_controls.json)单列。seed0基础10→30epochs首次resume未保存RNG，明确记录restart，不伪称连续训练。

2026-10-02：[E18同initial plans重算](results/E18_20261002_short_updates_seed0.json)旧512条baseline success全部相同，但跨GPU重规划actions/完成步数/distance及latent features不完全一致。工程结论只到success复现，不称bit-exact逐轨迹复现；新增update效应使用本次同RTX对照。三样本fitting loss下降不是held-out预测或任务收益证据，未升级科学主张。


### 2026-10-02 23:37 JST｜优化器隔离校对与比较降级

**撤回旧E16比较的严格data-only解释和“PBB被强基线吸收”判断，待公平重跑。** 独立CPU复验发现torch2.7.1 AdamW加载公共CPU state时会保留`step` tensor引用；多方法顺序运行使源state计数累加。权重/数据/gradient steps相同，但初始bias-correction历史不同。旧seed0七方法、seed1/2四方法及由这些模型计算的decision audit受影响；数值和原始文件全部保留，不能用于方法优劣或排序机制的因果结论。六方法objective matrix也受影响，已停止自身未完成进程、保留partial与invalidation artifact。

[可复现校对](results/E16_20261002_optimizer_audit.json)。修复为每方法deepcopy完整optimizer state，并断言初始steps相同、源steps不可变、结束steps=初始+updates；所有原方法/seed/目标重跑，不筛选方法，不追加数据，不重训base。base checkpoint文件未被改写；E13无训练、E18每fork新optimizer均不受此alias影响。科学主张此前为0，继续为0；C00工程L1保留。
