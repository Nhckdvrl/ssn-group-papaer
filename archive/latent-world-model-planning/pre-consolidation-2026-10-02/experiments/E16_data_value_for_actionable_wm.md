# E16 — Equal-budget data value for actionable world models

- **Status:** PLANNED
- **Program/Idea:** R1 / I12
- **Goal:** 不问“更多数据是否更好”，而是在相同 transition budget 下比较不同 experience composition 对 planning utility 的边际价值。

## Stage 0 — shared model, tiny matrix

优先 TwoRoom/PointMaze-like topology，固定：
- model architecture；
- optimizer / steps；
- total transitions；
- eval start-goal manifest；
- planner budget。

只选 3 个 data regimes：
1. **coverage-heavy passive**；
2. **action-excitation-heavy**：同局部 state 下更多 action variation；
3. **route-diverse / multi-route**：更多 alternative paths。

若 simulator接口允许，再加 4:
4. **same-reset counterfactual branches**。

## 必须测的数据属性

不是只按名字比较策略，实际量化：
- state coverage；
- conditional action covariance / excitation；
- transition support；
- route/path diversity；
- repeated-state branching；
- shortest-path / detour composition；
- failure/recovery fraction。

## Outcome

- factual one/multi-step prediction；
- counterfactual action discrimination；
- planner-consumed candidate ranking/regret；
- closed-loop success；
- unseen goal/query transfer；
- planning utility per 1k transitions。

## Scientific question

是否存在一个简单 data property / environment property 能预测：
> 哪种 experience composition 对 planning 最值钱？

如果只是“覆盖更多的 dataset最好”，不升级。

## Follow-up only if signal

- active probing / disagreement selection；
- query-aware data collection；
- contact-rich confirmation；
- second model family。

## Gate

- data regimes的 measured properties没有真正分开 → 重做数据，不解释；
- planning差异完全由transition count/support解释 → 普通data scaling；
- fixed budget下出现稳定不同 planning utility，并能用 data property解释 → I12 PROMISING；
- second environment验证排序/边界 → 大规模扩展。
