# 主张账本

日期：2026-10-02。已有 TwoRoom / PushT 工程测量；**尚无已成立的科学主张或完整数值复现。** 文献中的成功率不是我们的 L1/L2 证据。

## 待验证的建设主张

| ID | 主张 | 等级 | 证据 | 校对 | 下一步 |
|---|---|---|---|---|---|
| C00 | 官方小模型能在授权单卡完成加载、训练步、CEM 与 simulator episode；工程建设主张 | L1 | [E00](experiments/E00_native_baseline_and_resource_preflight.md)；[原生 TwoRoom](results/E00_E13_E16_20261002_tworoom_native.json)、[工程 PushT](results/E00_E13_E16_20261002_pusht_engineering.json) | 参数有限；wrapper/native scoring 差0；原生 TwoRoom 12 factual suffix 误差0/阳性12成功；8 paired closed-loop 可执行。PushT 尚属生成数据；训练步只测吞吐；Fast object 未独立核对weights。第一批工程 TwoRoom 缺 harness digest，正式批次已补 | 原生 PushT、训练与论文协议评测；不称完整复现 |

## 科学主张

尚无。系统调查中的表示／动力学／搜索／数据／历史分支是探索范围，不预先注册其结果方向。

后续每条主张需要关联实验卡和结果文件，并区分：观察相关性、受控干预、机制归因、跨模型范围。不能因为方法名字叫 reachability／causal／verifier 就把其输出当作真实可达性／因果／可执行性。

## 作废与降级记录

2026-10-02：PushT 初次工程运行因 native info 无 `state` key 停止；failure artifact 保留，改读原生 observation state 后以相同 seed 重跑，不筛 seed。两 task 的工程 episode 均失败，不计为方法负结果，因为生成数据/action statistics 未对齐官方协议。第一批 TwoRoom 的 harness digest 缺失单列披露，正式批次预先快照源码。
