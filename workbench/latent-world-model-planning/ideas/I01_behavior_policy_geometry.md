# I01：Trajectory-supervised planning geometry 是否继承 behavior-policy geometry？（2026-10-02）

- **状态：** SEED
- **来源：** 近邻分歧：RC-aux / Temporal-Distance JEPA 用同轨迹时间差、轨迹内/跨轨迹 pair 提供 planning-aware supervision；NeurIPS 2025 Quasimetric GCRL 与 ICLR 2026 Multistep Quasimetric 明确处理 suboptimal behavior statistics 与 optimal goal-reaching distance 的差异；PLDM 证明 offline data structure 会改变方法排序。详见 `PAPER_LINEAGE.md` P02/P05/P06/P14/P15。
- **研究动作：** 重新归因 + 干预/反事实 + 改变数学对象。
- **如果为真，主张是：** 在 environment dynamics、local transition support 和 one-step model samples 被控制时，仅改变 behavior path / episode organization 就会系统改变 trajectory-supervised latent-WM 的 reachability/progress geometry，并进一步改变 candidate ordering 与 closed-loop planning；说明“planning-aligned trajectory target”可能对 behavior policy 不具有应有的不变性。
- **不同结果各带来什么 information gain：**
  - A：head/geometry、ranking、control 都变化 → 建立 behavior→geometry→decision 链，继续找最小 structural correction；
  - B：只 head 变化，ranking/control 不变 → 说明 proxy bias 存在但非 load-bearing，I01 降级，保留为 negative result；
  - C：只要 local transition manifest 固定就完全不变 → 说明 RC-aux/TD-JEPA 实现比直觉更 robust，转向寻找是哪种 label construction 提供了 invariance；
  - D：变化来自 local samples/coverage 不一致 → identification 失败，先修数据构造，不解释科学现象。
- **最近 3 个近邻与增量：**

| 近邻 | 它的 claim | 我们必须达到的增量 |
|---|---|---|
| RC-aux | trajectory-offset proxy 学 finite-budget reachability | 固定 environment/local transitions 后，直接操纵 behavior/partition，量化 proxy→decision 因果后果 |
| Temporal-Distance JEPA | 从轨迹挖 directed temporal progress | 不只是换 temporal loss；比较同一 dynamics 下 behavior-dependent geometry 与 environment-oracle structure |
| Quasimetric GCRL / Multistep QRL | suboptimal/stochastic data 下恢复 optimal goal distance | 把 behavior-vs-optimal tension落到 **latent world-model planning objective + CEM candidate ranking/closed loop**，而不是重做 GCRL |

- **最便宜的决定性 pilot：** [E03](../experiments/E03_trajectory_partition_invariance.md)
  - 阳性对照：同 pair 在人为改变 trajectory-pair metadata 后，RC-aux/TD-JEPA 的监督 target/采样频率应按预期变化；LeWM one-step manifest 必须完全相同。
  - 噪声地板 + MIE：相同 checkpoint/seed 的重复 evaluation；pilot 的 MIE 以“至少使 pair-level calibration/ranking 差异明显超过重复波动，并足以改变是否进入 E04”为准，数值在 E00/E02 后填。
  - 决策表：A 明显 target→geometry/rank shift → E04；B target shift 但 geometry 无 shift → 增强训练/核对优化后一次复验；C target 本身未 shift → implementation invalid；D local manifest 不同 → VOID 重做。
- **预期论文形态：** A 失败模式+修复 / C 理论+受控实验。
- **排序打分（1–3）：** 证据 1 · 增量清楚度 3 · 形态匹配 3 · 成本 3 · 可完成性 3 · 不同结果的信息增益 3
- **PARKED / REFUTED 时：** 由 E03/E04 证据决定；不得因“temporal distance 已有人做”桌面判死。