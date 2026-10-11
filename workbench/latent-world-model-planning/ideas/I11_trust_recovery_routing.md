# I11｜Utility-Gated Recovery：什么时候该继续信任、修正或绕开世界模型？

- **状态：** SEED，未获得本地实验证据。
- **对应：** R5，见[研究计划](../RESEARCH_PLAN.md)。
- **来源：** S19 Feedback WM / WorldAgen / CAWM；S20 counterfactual update utility。
- **问题：** world model出现prediction mismatch时，应该hold、只做feedback state correction、少步parameter update、增加replanning compute，还是切到fallback policy？单纯“error大就update”是否浪费甚至伤性能？
- **实验入口：** E18。
- **研究边界：** feedback、TTT、shift detection、replay flushing都已有强工作；本seed不争“首次在线适配”，而研究**intervention utility routing**。

## 工作方法假设

先离线构建小型fork ledger：

对同一deployment checkpoint / state / history，在同一随机条件下比较：
- HOLD；
- FEEDBACK；
- SHORT-UPDATE；
- EXTRA-REPLAN；
- FALLBACK（若已有）；

得到真实 `Δutility`。这些fork outcome只用于训练/分析标签，不进入部署时输入。

然后训练一个轻量router，只使用部署可见特征：
- one-/multi-step residual；
- ensemble disagreement；
- candidate elite margin / rank instability；
- recent progress / no-progress counter；
- OOD/support proxy；
- available compute budget。

输出不一定是复杂网络；可先用decision tree / logistic / threshold。

## 想看到的结果

- update的value与raw prediction error并不单调；
- 不同failure mode对应不同intervention；
- utility-gated routing在同compute/interaction budget下优于always-update、always-feedback、always-replan；
- router能跨goal/task或shift强度泛化。

若一个固定策略始终最好，保留为系统简化结论，不硬造router。
