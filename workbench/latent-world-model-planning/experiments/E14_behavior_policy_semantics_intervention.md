# E14 — Behavior-policy intervention on planning semantics

- **状态：** PLANNED
- **对应：** I09 / M3
- **与 VOID E03/E04 的区别：** 这里真正改变 generating behavior policy，使 Temporal-Distance JEPA / RC-aux 实际读到的 temporal pairs/windows/offsets发生改变；不是只重切相同short clips。
- **首选环境：** topology/navigation（可算 shortest/geodesic）；第二阶段再 contact-rich。
- **数据 regimes：** efficient/direct、random/suboptimal、detour/looping、route-biased、mixed。先小规模 2–3 个regime，不一次全铺。
- **匹配/记录：** trajectories、transition count、state coverage、action coverage、local transition support、start-goal distribution；若无法严格匹配，估计 overlap / density并在解释中保留。
- **methods：** Bai/Xiong Temporal-Distance JEPA + RC-aux；LeWM native作为 non-temporal-supervision control。
- **读数：**
  - environment shortest distance vs learned temporal/reachability score；
  - fixed-candidate rank/regret；
  - same task closed-loop success；
  - one/multi-step dynamics error guard；
  - learned geometry route imprinting。
- **关键 pattern：** local predictive fidelity近似稳定，但 planning semantic / decision随behavior policy系统变化。
- **gate：**
  - 变化完全由coverage解释 → 不升级；
  - 仅head calibration变、decision不变 → 不升级；
  - 跨objective/第二task结构仍有behavior imprint → E15。
