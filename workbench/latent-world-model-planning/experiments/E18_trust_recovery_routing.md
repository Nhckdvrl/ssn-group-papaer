# E18 — Oracle recovery-action map

- **状态:** PLANNED / evaluation-first
- **对应:** I11 / R5
- **目的:** 先验证 failure state 下 oracle-best recovery action是否随 regime变化，不先训练router。

## Recovery action set

首轮选择成本差异明显的4类：

1. baseline
2. shorter horizon / nearby subgoal
3. more frequent replanning / feedback
4. policy/intuition fallback 或 uncertainty-conservative scoring

test-time adaptation只在前四类出现 clear regime 后加入。

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

不新造probe，优先已有 signals：
- ensemble / latent disagreement
- rollout residual after one real step
- candidate margin
- action-support score
- goal distance / horizon ratio
- planner-reachable fidelity
- H/K mismatch indicator

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
- internal accuracy改善但utility null → 不升级。

## 结果
未运行。
