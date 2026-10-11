# E19｜Selective Revaluation：变化后最小更新集

- **状态：** PLANNED；未运行。
- **对应：** I13 / R2，兼R3/R5。
- **来源：** S21 + I13；second-wave study。
- **阳性对照：** no-change、reward/goal-only change、full retrain / full update upper reference。
- **噪声地板：** shift instance、post-shift data seed、train seed分开；更新前后的optimizer state明确记录。
- **决策表：** selective update更快恢复且少遗忘→扩shift/task；full update始终最好且成本可接受→保留简化结论；module rule只在一个task成立→限制scope或训练router；prediction改善但planning不变→不升级。

## 核心问题

post-deployment变化后，world-model system到底需要重学哪一部分？能否用更少samples/steps恢复规划，同时保留旧能力？

## Shift matrix

至少三类：

### Q — query/reward shift
环境动力学不变，只换goal/reward/cost definition。

### T — local transition shift
如门开/关、局部障碍、局部contact rule变化；只影响部分state region。

### D — broad dynamics shift
如action scale、friction、mass/actuation变化，影响较广。

可选 P — planner/interface shift：换planner、horizon或query representation，测试是否根本不应更新world dynamics。

## Update variants

1. HOLD；
2. TASK/COST only；
3. SHORT-DYNAMICS only；
4. LONG-HORIZON / reachability head only；
5. SHORT + LONG；
6. ENCODER + predictor；
7. FULL UPDATE；
8. replay-mixed update；
9. fresh small residual adapter（若现成最省）。

第一轮每类shift只选3–4个最有判别力variants，不做全Cartesian。

## Fairness

每种方法：
- 相同post-shift transitions；
- 相同gradient-step / wall-clock预算至少报一种matched协议；
- 相同goal/query信息；
- full update不偷多数据；
- 旧数据replay量单独计；
- 若某method依赖shift label，显式说明。

## 读数

### Recovery
- post-shift success curve；
- samples-to-90%-recovery；
- wall-clock-to-recovery；
- cumulative regret during adaptation。

### Retention
- pre-shift tasks after update；
- untouched-region performance；
- no-shift control damage。

### Localization
- 各module gradient norm / validation improvement；
- changed-region vs unchanged-region prediction error；
- planner candidate ranking recovery。

## 方法生长

如果固定“shift type→update module”规则已经稳健，就优先保留简单规则。

如果同类shift内部差异很大，可训练轻量selector：
- features：residual location、action-conditioned error、goal/query change flag、support/OOD；
- output：which modules to update / replay ratio / step budget。

不要让selector使用未来return或oracle shift class作为部署输入；oracle shift labels只可做analysis upper bound。

## 最近邻与exact delta

- WorldAgen / AdaJEPA：test-time training本身已做；
- Feedback WM：无需参数更新的observer-style correction；
- CAWM：检测dynamics changepoint并flush stale replay；
- ReDRAW / residual adaptation：局部residual update；
- successor/revaluation literature：reward change vs transition change的差别是经典背景。

E19若成论文，必须是**modern visual latent WM的selective update allocation + planning recovery/retention evidence**，不是“transition change更难”。

## 结果
未运行。
