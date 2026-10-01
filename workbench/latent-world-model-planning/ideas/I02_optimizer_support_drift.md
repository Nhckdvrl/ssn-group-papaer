# I02：CEM 是否把候选推向“数据支持更低、模型更乐观”的 false-elite 区域？（2026-10-02）

- **状态：** SEED
- **来源：** 近邻分歧 + 系统测量入口：PLDM 显式用 ensemble uncertainty 防 OOD transition；Hi-LeWM 报告 high-level search distribution mismatch；ACID/MEND 分别从 inverse consistency / latent score 检查 imagined transition；offline MBRL 的 model exploitation 是经典压力。当前 LeWM/RC-aux stack 有可重置 simulator 和迭代 CEM，可逐 stage 审计。
- **研究动作：** 定位 + 干预/反事实 + 重新归因。
- **如果为真，主张是：** compact latent CEM 的主要 failure 之一不是静态 prediction error，而是 optimizer-induced candidate distribution shift：CEM 迭代降低行为数据 support，同时提高 model-based optimism，造成 false elites 与 environment regret；该链条在匹配动作幅度/平滑度和 compute 后仍存在。
- **不同结果各带来什么 information gain：**
  - A：support drift 先于 false-elite/regret，跨 ≥2 tasks → 进入机制/修复；
  - B：false elite 存在但 support 不解释 → 转向 candidate margin / metric/dynamics；
  - C：support 下降但 true utility 不受影响 → support metric 不是 load-bearing；
  - D：简单 ensemble uncertainty/behavior prior 完全修复 → 不造复杂新方法，记录强 baseline。
- **最近 3 个近邻与增量：**

| 近邻 | 它的 claim | 我们必须达到的增量 |
|---|---|---|
| PLDM | ensemble uncertainty 惩罚 OOD transition | stage-wise optimizer distribution shift → false elite → real regret 的直接环境审计 |
| ACID | inverse-cycle residual 检查 intermediate realizability | 证明 support/optimism 是否是 ACID residual 未覆盖的 distinct failure，或反之 |
| Hi-LeWM | high-level search distribution mismatch | 从 hierarchical macro-action case 推到 compact latent CEM 的可测 support chain；不能只复述“search OOD” |

- **最便宜的决定性 pilot：** [E05](../experiments/E05_cem_support_drift.md)
  - 阳性对照：人为把 action chunk 替成远离数据 support 的 sequence，support metric 必须下降；true-dynamics rollout 能识别 model optimism。
  - 噪声地板 + MIE：同 candidate/restore 重跑；MIE 在 E02 之后按 false-elite rate / paired regret CI 填。
  - 决策表：稳定链条 → 扩 seed + verifier controls；只有相关无时间顺序 → 不升级因果；无链条 → PARK。
- **预期论文形态：** A 失败+修复 / B 构念+测量。
- **排序打分（1–3）：** 证据 1 · 增量清楚度 2 · 形态匹配 3 · 成本 3 · 可完成性 3 · 不同结果的信息增益 3
- **PARKED / REFUTED 时：** 若 action magnitude/smoothness 或 PLDM uncertainty 已完全解释，park 并写重开条件。