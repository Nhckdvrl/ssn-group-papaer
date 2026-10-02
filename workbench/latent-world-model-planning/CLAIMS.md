# 主张账本

日期：2026-10-02。已有 TwoRoom / PushT 原生测量、LeWM有限数据训练与七策略pilot；**尚无已成立的科学主张或完整数值复现。** 文献中的成功率不是我们的 L1/L2 证据。

## 待验证的建设主张

| ID | 主张 | 等级 | 证据 | 校对 | 下一步 |
|---|---|---|---|---|---|
| C00 | 官方小模型能在授权单卡完成加载、训练步、CEM 与 simulator episode；工程建设主张 | L1 | [E00](experiments/E00_native_baseline_and_resource_preflight.md)；原生[TwoRoom](results/E00_E13_E16_20261002_tworoom_native.json)/[PushT](results/E00_E13_E16_20261002_pusht_native.json)、[LeWM有限数据](results/E16_20261002_equal_data_seed0.json) | strict LeWM303 keys/18M；native cost controls差0；全部TwoRoom factual controls误差0。PushT public setter有长时物理残差；自写constant-LR循环不是完整Lightning配方。Fast object未独立核对weights；独立seed确认进行中 | 原生论文配方与第二task数据效用确认；不称完整复现 |

## 科学主张

尚无。系统调查中的表示／动力学／搜索／数据／历史分支是探索范围，不预先注册其结果方向。

首轮[E16](results/E16_20261002_equal_data_seed0.json) GLOBAL-U24/48、NO-ADD9/48、PBB19/48是待确认观察，不升级科学主张。相对NO-ADD，GLOBAL-U配对episode gain31.25pp [18.75,45.83]；这不是独立train-seed CI，也不是新颖性证据。E13 [A2](results/E13_20261002_fidelity_value.json) 没有支持当前self-consistency refinement收益，不能据此关闭R2。

后续每条主张需要关联实验卡和结果文件，并区分：观察相关性、受控干预、机制归因、跨模型范围。不能因为方法名字叫 reachability／causal／verifier 就把其输出当作真实可达性／因果／可执行性。

## 作废与降级记录

2026-10-02：PushT 初次工程运行因 native info 无 `state` key 停止；failure artifact 保留，改读原生 observation state 后以相同 seed 重跑，不筛 seed。两 task 的工程 episode 均失败，不计为方法负结果，因为生成数据/action statistics 未对齐官方协议。第一批 TwoRoom 的 harness digest 缺失单列披露，正式批次预先快照源码。

2026-10-02：[E13 A2](results/E13_20261002_fidelity_value.json) 起跑时卡空闲，之后发现其他进程共卡；耗时降为非独占测量，不作speedup证据，成功率保留。PushT75步factual suffix的公开setter重放最大position残差92.48pixels、wrapped角度1.079rad，阳性63/64；不得把全部失败归因于模型或声称精确反事实。所有起点保留，[控制结果](results/E00_E13_E16_20261002_factual_controls.json)单列。seed0基础10→30epochs首次resume未保存RNG，明确记录restart，不伪称连续训练。
