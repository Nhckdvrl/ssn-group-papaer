# E18 — Oracle recovery-action map

- **状态:** PLANNED / evaluation-first
- **对应:** I11 / R5
- **目的:** 先验证 failure state 下 oracle-best recovery action是否随 regime变化，不先训练router。

## Recovery action set

首轮要覆盖**不同机制**，而不是四个相似threshold：

1. **baseline / reuse**；
2. **replan cadence change**：AdaReP-style frequent refresh；
3. **planning abstraction change**：shorter horizon / nearby subgoal；
4. **model-use change**：policy/intuition fallback 或 certified abstain；
5. **state/model correction**：feedback observer（资产可用时）。

Test-time gradient adaptation先不加入；只有上述动作出现 clear regime 后，再作为更贵repair。

## Conditions

- near / far goal
- in-support / low-support action region
- clean / dynamics shift
- low / high candidate margin
- optional partial observation

## Oracle evaluation

同一 environment state/reset：
- 每种 recovery action运行多 stochastic seeds
- 计算 utility lift vs baseline
- 标记 oracle-best recovery action

## Candidate predictors

不新造 arbitrary probe，优先已有、已有论文证明和具体 repair相关的 signals：
- rollout residual after one real step（Feedback WM / When WMs Lie）；
- local dynamics sensitivity + cached-rollout mismatch（AdaReP）；
- certified decision-relevant error / predicted advantage（Dual-Frontier）；
- intuition-vs-WM disagreement / reliability（IMWM-like）；
- candidate margin；
- action-support score；
- goal distance / horizon ratio；
- planner-reachable fidelity；
- H/K mismatch indicator。

## Scientific question

是否存在：

```text
observable failure signature
        ↓
best recovery action
```

并能跨task泛化？

## Gate

- 一种 recovery action几乎总赢 → router没有意义，转研究该方法的failure boundary；
- signals无法预测 oracle ranking → I11 park；
- stable mapping + meaningful compute savings / success lift → 再设计 tiny router；
- 若每个 published signal只预测它自己原论文的repair，却无法比较不同repair，说明需要新的 common decision-level signal或failure taxonomy；这本身可生成下一seed；
- internal accuracy改善但utility null → 不升级。

## 结果
未运行。
