# I05 — Generic history / partial observability（SUPERSEDED）

- **状态：** SUPERSEDED by [I07](I07_observation_aliasing_belief_planning.md)
- **日期：** 2026-10-02
- **原因：** “history length / context sweep”本身太弱，而且 2026 近邻已经覆盖 structured memory、typed state、belief-space prediction、POMDP temporal abstraction。继续围绕“多看几帧是否更好”容易退化成无尺度的 probe / recipe study。
- **保留的科学压力：** observability 确实重要，但已被重写成更强的 mother question：

> image-goal 中 **goal-comparable observable state** 与 **control-sufficient hidden belief** 是否发生角色冲突？当同/近同 observation 对应不同 hidden dynamics 时，这种 aliasing 是否真正改变最优 candidate action、造成 deployed planner regret；deterministic history 何时足够，何时 multi-hypothesis belief 才必要？

- **新入口：** I07 → E11（actionable aliasing oracle）→ conditional E12。
- **禁止复活为：** context length sweep、hidden-state linear probe、generic“POMDP需要memory”。
