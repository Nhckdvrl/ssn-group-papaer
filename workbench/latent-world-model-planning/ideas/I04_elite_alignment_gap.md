# I04：random-plan alignment 到 CEM elite alignment 的退化由什么决定？（2026-10-02）

- **状态：** SEED（从属于 I02/I03，不单独抢主线）
- **来源：** Decision-Metric Alignment 已定义 Plan-Real 与 CEM-stage Spearman，并指出 candidate margin 是 sufficient-condition 中的控制量；本 workbench 需要先复现它作为 measurement calibration。
- **研究动作：** 强基线复现 + 定位。
- **如果为真，主张是：** 只有在复现后发现一个**DA-LeWM 尚未解释的稳定 hidden variable**（候选 margin/support/rollout uncertainty）能够预测 random→elite alignment collapse，且它连接真实 selection regret，才升级。
- **不同结果各带来什么 information gain：**
  - A：support/margin 稳定预测 elite collapse → 并入 I02/I03；
  - B：复制 DA-LeWM 但没有新增解释 → 作为工具资产，不成 paper；
  - C：复现不了 → 先解决 protocol，不挖新故事。
- **最近 3 个近邻与增量：**

| 近邻 | 它的 claim | 我们的增量 |
|---|---|---|
| DA-LeWM | random/mid/elite rank diagnostics | 只有 hidden variable + real regret causal link 才有增量 |
| Temporal Straightening | geometry improves planner conditioning | 检查 geometry intervention 是否改变 elite margin/alignment，不重做 curvature |
| PLDM uncertainty | OOD uncertainty affects planning | 检查 uncertainty/support 是否解释 stage-dependent alignment |

- **最便宜的决定性 pilot：** [E02](../experiments/E02_decision_audit_replication.md)
  - 阳性对照：复现 random vs CEM-stage paired rank measurement。
  - 噪声地板 + MIE：同 start-goal/candidate pool 重算；bootstrap over start-goal pairs。
  - 决策表：只复现 → asset；有稳定 unexplained gap → 接 E05/E06。
- **预期论文形态：** 默认无；只作为 I02/I03 证据。
- **排序打分（1–3）：** 证据 1 · 增量清楚度 1 · 形态匹配 2 · 成本 3 · 可完成性 3 · 不同结果的信息增益 3
- **PARKED / REFUTED 时：** 若无新 hidden variable，保留 diagnostic，不继续包装。