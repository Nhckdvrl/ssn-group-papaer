# E15 — Remove behavior-path semantics without privileged test oracle

- **状态：** CONDITIONAL / requires E14
- **对应：** I09
- **目标：** 只有E14证明 behavior-policy geometry污染 deployed planning semantics 后，寻找最小 correction。
- **候选原则而非预设方法：**
  - local Bellman / transition consistency；
  - multi-route aggregation；
  - interval/censored temporal targets；
  - quasimetric / triangle-consistency；
  - semantic negatives与global regularization role separation（可复用 I06/E09 证据）。
- **约束：** deployable方法不能使用 environment shortest-path oracle；oracle只作为 measurement / upper bound。
- **成功标准：** 在至少两个 behavior regimes 上保持 planning semantics 稳定，同时不牺牲 in-distribution closed-loop；最好在 unseen behavior mixture 上泛化。
- **失败也有信息：** 若任何 correction都需要 privileged connectivity，问题可能属于 data identifiability，而不是 loss设计；不要硬造模块。
