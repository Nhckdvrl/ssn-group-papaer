# E06：Oracle bottleneck ladder / regime identification（2026-10-02）

- **状态：** PLANNED
- **类型：** EXPLORE
- **对应：** I03
- **问题（一句话）：** goal distance、candidate budget、replanning protocol变化时，end-to-end ceiling是否在 metric/representation、dynamics、action discrimination、proposal/search、time-index、horizon/target层之间系统迁移？
- **设置：** E01/E02可信后。首轮 2 tasks（navigation + contact-rich）× 3 goal-distance bins × 2 candidate budgets；先 LeWM baseline，不一开始堆方法。
- **协议控制（必须显式）：**
  - planning horizon H；
  - execution/replanning prefix K；
  - terminal@H / prefix@K / running cost；
  - frameskip / action block；
  - max env budget。
  P57 已证明这些变量本身可造成大幅 apparent failure，因此先control再归因model。
- **oracle ladder：**
  1. candidate-set real-utility ceiling；
  2. encoded-real endpoint rank；
  3. predicted endpoint rank；
  4. true-dynamics scoring（可可靠reset/replay时）；
  5. counterfactual-action discrimination diagnostic；
  6. terminal@H vs prefix@K / running-cost control；
  7. nearby true subgoal diagnostic；
  8. closed-loop success。
- **failure signature：**
  - R = representation/metric；
  - D = dynamics/rollout；
  - A = action discrimination；
  - P = proposal/search；
  - T = time-index/replanning interface；
  - H = horizon/target distance；
  - M = mixed/unidentifiable。
- **读数：** above ladder、goal distance、candidate margin、planner-reachable fidelity、data support、action-discrimination margin、H/K ratio、compute。
- **阳性对照：**
  - 极低 candidate budget应降低 candidate-set ceiling；
  - known H>K terminal@H case应能用prefix/running control暴露time-index effect；
  - near goal + true dynamics应降低H/D负担；
  - intentionally corrupted dynamics应由true-dynamics replacement救。
- **噪声地板 + MIE：** pair/episode bootstrap + train-seed variance。只有 oracle replacement的paired improvement超过repeat floor才标binding bottleneck；signature阈值在pilot后冻结。
- **混杂审计：**
  - goal bin用environment/native distance，不用被测模型metric；
  - native protocol与common audit分表；
  - one intervention若同时改多个layer标M；
  - true-dynamics仅在restore valid环境；
  - subgoal仅diagnostic；
  - H/K/scoring index不按结果重选；
  - compute/model calls + wall-clock双报；
  - method加入必须有明确layer目的。
- **决策表：**
  - 少数observable variables跨task预测signature/intervention ranking → E07；
  - protocol control解释主要差异 → 记录并不重复P57；换更难regime或park；
  - per-task arbitrary patterns → I03 PARK；
  - 单一layer始终主导 → 生成更窄idea；
  - ladder不稳定 → 修harness。
- **算力预算：** 先复用checkpoint做 fractional evaluation；各cell独立job，观察稳定后才扩train seeds/methods。  
- **实际：** 待运行

## 结果
未运行。