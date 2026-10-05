# 主张账本 — Incremental Interpretation & Revision

**状态：2026-10-05 / PROPOSED baseline residency。**

当前**没有科学主张**。下表只登记待验证对象，不能在汇报/论文中写成 finding。

| ID | 待验证对象 | 等级 | 当前证据 | 升级条件 |
|---|---|---|---|---|
| C00 | 本地 harness 能在公开 GP 数据上复现一个已知的 GP-specific behavioral deficit | L0 | [E00](experiments/E00-baseline-reproduction.md) / [结果](results/E00-summary.json)：全 16-prefix 主效应 −2.81 pp [−11.50, 5.89]，顺序敏感，gate 未通过 | E00 阳性对照通过，并报告 item-paired CI |
| C01 | interpretation revision 可被“最终解释支持”和“初始错误解释残留”两个读数分开测量 | L0 | 数据模式可构造；尚无本地结果 | 至少一个受控构式中两个读数具有稳定、可重复的不同响应 |
| C02 | 不同 cue timing / cue strength 条件下存在可区分 competing accounts 的 revision structure | L0 | 仅 territory hypothesis | 预先写出不同解释的预测并由 E01/E02 区分 |

**禁止提前升级：**
- 上游已报告的 garden-path effect 不是我们的 C-level novelty；
- “某模型答错很多”不是机制主张；
- probe/hidden-state separability 不能单独升级为“模型保留旧解释”。

## 作废 / 降级 / 未通过记录
- 2026-10-05：E00 不升 C00。句先有已知方向，但 prompt suite 整体不稳定；不得把选择句先视作通过。E03 注册追 why，原 E00 结果完整保留。

- 2026-10-05：[E04](experiments/E04-known-positive-control.md) 正方向 +19.84 pp [14.04, 25.82]，但 nonGP 30.71%、raw specificity DiD CI 跨零；[E05](experiments/E05-response-meaning-calibration.md) 8B 的 assertion response 下句先 +30.43 pp、题先 −23.91 pp。C00 不升级；原协议有效性问题未解决，不能把 positive direction 当严格 gate。C01/C02 未运行。
