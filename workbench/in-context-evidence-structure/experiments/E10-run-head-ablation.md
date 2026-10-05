# E10：表层时间敏感性的因果来源——“游程头”消融（2026-10-05）

- **状态：** RUNNING
- **对应：** C02 机制（条件分支：行为已区分各解释后才做白盒）
- **头的选择（来自 E06 注意力探针，跑前固定）：** 在 const 格式中，“suffix_4 时 B 的注意力份额 − disp_4 时 B 的份额”× 总标签注意力 最大的 16 个头（`results/switch_pilot_T16/run_heads_Qwen3-8B.json`，全部在第 20–31 层，如 L29H11、L24H22）。对照：总标签注意力量匹配、游程分数 < 0.05 的 16 个头。
- **干预：** 在 o_proj 输入处把这些头置零（全部位置）。
- **数据：** E06 的 const / irr5 / rule5 × 7 个条件（200 base），E08 的 aligned / anti × suffix4 / disp4 × B / allA（150 base）。设置：none / run16 / ctrl16。
- **预测：** 若游程头承载表层时间推断：run16 使 const/irr5 的 suffix4−disp4 与噪声前缀效应大幅缩小（ctrl16 不变）；rule5 本来就时间盲，变化小；anti-aligned 的“被表层游程带偏”（suffix−disp = −0.92）应被削弱。

## 结果
（待填）
