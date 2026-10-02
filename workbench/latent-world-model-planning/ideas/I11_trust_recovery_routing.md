# I11 — Trust / repair / bypass: recovery action should match failure type

- **Program:** R5 — trust, repair, bypass
- **状态:** SEED
- **目的:** 不再问“uncertainty能不能检测failure”，而问：

> **当 world model 在某个 planning state 不可靠时，应该采取哪一种 recovery action？**

## Candidate recovery actions

已有方法已经形成一套 recovery-action library：

- failure detection：Foresight / MEND / FARM-like readout；
- verify-or-trust：Dual-Frontier；
- adaptive replanning：AdaReP；
- feedback observer：Feedback WM；
- test-time adaptation：AdaJEPA / residual adaptation；
- conservative safety filter：When World Models Lie；
- intuition / policy fallback：IMWM / CausalNav-like gate；
- shorten horizon / subgoal：Planning Limits / Anchored / HWM；
- increase search / learned proposal：IMWM/SAGE/RP1 family；
- active information gathering / abstain。

每一种都有人做——这正是 R5 成立的原因。**新问题不是发明第九个repair，而是 recovery action selection 本身是否存在可预测结构。**

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

## 直接 reviewer pressure

- AdaReP 已经给出 mismatch+sensitivity→replan cadence；
- Dual-Frontier 已经给出 certify→trust/verify；
- IMWM/CausalNav-like gates 已经做 trust/fallback；
- When World Models Lie 做 observed error→pessimistic safety。

因此 E18 必须比较 **多种 qualitatively different recovery actions**，并证明相同 signal并不总指向同一repair；否则会被压缩成已有 adaptive gate。

## 最大 compression

“只是一个ensemble/router / AdaReP+IMWM的拼装。”

所以论文必须先有 **recovery-action regime law**；router只是最小 consequence。

## 对应实验
E18。
