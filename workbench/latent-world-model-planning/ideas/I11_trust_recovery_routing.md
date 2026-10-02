# I11 — Trust / repair / bypass: recovery action should match failure type

- **Program:** R5 — trust, repair, bypass
- **状态:** SEED
- **目的:** 不再问“uncertainty能不能检测failure”，而问：

> **当 world model 在某个 planning state 不可靠时，应该采取哪一种 recovery action？**

## Candidate recovery actions

已有方法分别给出：

- shorten horizon / closer subgoal
- replan more frequently
- increase search budget
- uncertainty penalty / conservative candidate filter
- model correction / feedback observer
- test-time adaptation
- intuition / policy fallback
- abstain / active information gathering

每一种都有人做。新问题是 **哪一种在什么 failure regime 真正提升 utility**。

## First seed

不训练 router。

对同一 start-goal / checkpoint / episode state：
1. baseline planner；
2. 各 recovery action；
3. simulator reset 得到真实 utility lift；
4. 记录已有 signals：
   - rollout disagreement / uncertainty
   - horizon / goal distance
   - candidate margin
   - planner-reachable fidelity
   - H/K mismatch
   - action-support score
   - model residual after one executed step

问：

> 是否存在稳定的 signal / failure-type → best recovery action mapping？

## 直接近邻

- PLDM uncertainty
- MEND hallucination detector/correction
- IMWM intuition hybrid / reliability gate
- AdaJEPA / Sandwich / ReDRAW adaptation
- Feedback WM observer correction
- Planning Limits / Anchored Planning
- HWM / subgoal / adaptive replanning lines

它们是 recovery-action library，不是关闭 R5 的理由。

## 升级条件

- 不同 failure regimes 的 oracle-best recovery action真的不同；
- 一个或少数 signals能跨task预测 intervention ranking；
- static “always use X” 不能完全吸收；
- action-level utility / closed-loop consequence显著。

## 方法形态（只有过gate后）

- tiny router
- confidence-to-action policy
- adaptive horizon/replan/adapt schedule
- trust calibration layer

## 最大 compression

“只是一个ensemble/router。”

所以论文必须先有 **recovery-action regime law**；router只是最小 consequence。

## 对应实验
E18。
