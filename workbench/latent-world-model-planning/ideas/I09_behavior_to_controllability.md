# I09 — Dataset-induced planning semantics: behavior → controllability gap

- **状态：** SEED / broad problem mine
- **母问题：** 从 reward-free trajectory order / gap / cross-trajectory metadata 学 planning semantics 时，latent WM 是否把 behavior policy 的 route/tempo写进了“reachability/progress”，从而影响 test-time MPC？
- **直接近邻：** RC-aux、Bai/Xiong Temporal-Distance JEPA、PLDM、Offline GCRL Quasimetric、Multistep Quasimetric、CGCIVL。
- **已知，不能 claim：** behavior temporal statistics不等于 optimal shortest distance；cross-trajectory identity不等于 connectivity；offline data quality matters。
- **WM-specific delta：** 相同 environment dynamics 下，改变真实 behavior-policy-generated trajectory distribution，是否改变 planning-aware objective 学到的 metric/representation，并造成 candidate ordering / closed-loop control 的可重复差异。
- **重要：** 旧 I01/E03 的“只重切 episode、short windows保持不变”已因 loss不可见而 VOID。I09 必须改变 objective 实际读取的 pairs/windows，例如 direct vs looping vs route-biased vs mixed behavior。
- **控制：** 尽量匹配 state coverage、local transition/action support、样本量；无法匹配的轴必须定量报告。环境 shortest/geodesic 只作 oracle。
- **升级条件：** behavior change在 local prediction近似不变时仍系统改变 planner-consumed semantics，并跨至少两种 objective（RC-aux / Temporal-Distance JEPA等）或两个 task structures成立。
- **潜在方法：** Bellman/local consistency、multi-route aggregation、interval/censor supervision、quasimetric correction等都不预设。
- **I06 关系：** heuristic semantic negatives只是 I09 的一个局部机制审计，不再独立代表 workbench。
- **对应：** E14 → conditional E15；E08/E09可作为子诊断。
