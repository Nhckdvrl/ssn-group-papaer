# I03：latent planning 的主要瓶颈是否随 goal distance / data support / candidate margin 系统迁移？（2026-10-02）

- **状态：** SEED
- **来源：** 近邻之间的解释分裂：Temporal Straightening/DA-LeWM/RC-aux 指向 geometry/metric；SALT 指向 recursive dynamics；IMWM/SAGE/LeFlow 指向 proposal/search；Planning Limits/Anchored Planning 指向 target distance/horizon；What Must a World Model Distinguish 强调 requirement 依赖 query/candidate/planner。
- **研究动作：** 设计空间分解 + 定位 + 成功案例解剖。
- **如果为真，主张是：** 这些“互相竞争”的方法不是在解决一个固定 bottleneck；少数可观测 regime variables（优先 goal distance、candidate margin、data support）能预测 performance ceiling 位于 representation、dynamics、proposal 还是 horizon/target interface，并预测哪类 intervention 有效。
- **不同结果各带来什么 information gain：**
  - A：跨任务出现可预测 signature switch → 形成 principle，考虑 adaptive method；
  - B：只有 per-task arbitrary threshold → 只是 benchmark，不升主张；
  - C：一个 bottleneck 始终主导 → 反而简化后续研究，集中该层；
  - D：oracle ladder 本身不稳定 → 修 harness，不做大 sweep。
- **最近 3 个近邻与增量：**

| 近邻 | 它的 claim | 我们必须达到的增量 |
|---|---|---|
| Planning Limits | plannable range / distant goal 的 intrinsic limit | 不重新证明 horizon effect，而是定位何时 bottleneck 从其它层迁到 horizon |
| What Must a WM Distinguish? | sufficiency 依 query/candidate/planner | 给 compact visual planning 中可实测、可预测 intervention ranking 的 regime law |
| JEPA-WMs | recipe choices 的系统 empirical study | 不是更多 sweep；必须有 oracle-identifiable bottleneck + predictive variable |

- **最便宜的决定性 pilot：** [E06](../experiments/E06_oracle_bottleneck_ladder.md)
  - 阳性对照：在构造的短/远 goal 与 intentionally weakened candidate budget 下，oracle ladder 应分别暴露不同 ceiling。
  - 噪声地板 + MIE：按 failure signature 的 paired CI；数值在 E01/E02 后填。
  - 决策表：跨 task 共享变量预测 signature → E07；每任务各说各话 → PARK/改 decomposition。
- **预期论文形态：** C 理论/受控 + 方法；或 B 构念/识别方法。
- **排序打分（1–3）：** 证据 1 · 增量清楚度 2 · 形态匹配 3 · 成本 2 · 可完成性 2 · 不同结果的信息增益 3
- **PARKED / REFUTED 时：** 没有 cross-task predictive variable 时不把“大矩阵”包装成论文。