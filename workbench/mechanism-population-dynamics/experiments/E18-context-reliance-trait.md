# E18 — Is context reliance a stable run-level trait?（2026-10-02）

- **状态：** RUNNING（判据提交于计算之前）
- **类型：** PILOT（把 E13/E17 的发现从“单任务、可能单点异常”推进到“稳定特质”或否定它）
- **对应：** E13、E16、E17；Fouilhé 2026（模型家族间差异、措辞可改变依赖达 80 个百分点）；PolyPythias（410M seed3、seed4 为离群 run）
- **阳性对照：** 每个条件内，已知条目上的采信率应显著高于 0（上下文确实能改变答案），且条件间难度不同
- **噪声地板 + MIE：** 每个 run × 条件，按条目 bootstrap 的 95% CI；实验单位 = run
- **决策表（跑之前写）：** 见下方
- **问题（只回答这个）：** 同一配方的独立 run 之间“依赖上下文还是记忆”的差异，是否在不同知识关系、不同冲突形式下保持一致的 run 排名（特质），且不是由离群 run 驱动？在 160M 群体上是否同样存在？

## 设置
- 数据：ParaConflict（gaotang/ParaConflict，test），6 个类别（Athlete Sport、Book Author、Company Headquarter、World Capital、Company Founder、Official Language）× 2 种冲突形式（Substitution Conflict、Coherent Conflict）= 12 个条件。
- 每个 run 的“已知”条目：Clean Prompt 下 lp(' '+Answer[0]) > lp(' '+Distracted Token)。
- 采信 = 冲突提示下 lp(干扰) > lp(答案)；条件内采信率 = 已知条目上的平均。
- 模型：`pythia-410m` + seed1..9（step 143000）；`pythia-160m` + seed1..9（step 143000）。

## 判据
- **P1 特质（410M）：** 12 个条件两两之间 run 排名的平均 Spearman ≥ 0.5；**去掉 seed4 后（n=9）仍 ≥ 0.4**。
- **P2 差异显著：** ≥ 6/12 个条件中，run 间采信率极差 > 2 × 平均 bootstrap 半宽。
- **P3 160M：** 若每个 run 在 ≥ 6 个条件上有 ≥ 30 个已知条目，则同样计算 P1；否则记为“不可判定”。
- **判定：** P1 与 P2 成立 → “上下文依赖是 run 特异的稳定特质”成为候选主张（C04）；P1 只在含 seed4 时成立 → 记为离群 run 驱动，不建主张；P1 不成立 → E13 的差异是任务特异的，不是特质。
