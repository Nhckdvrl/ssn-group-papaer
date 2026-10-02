# Method Library — 用方法生成 hypothesis，不拿锤子乱找钉子

更新：2026-10-02。

> problem-led 与 method-led 不是对立阵营。  
> 好的 method-led research 是：一个成熟方法原理对重要 program 给出**非平凡、可证伪的新预测**；实验验证后，方法成为解释/解决问题的自然工具。  
> 坏的 method-led research 是：“这个模块还没人塞进 LeWM，所以加一下看涨不涨点”。

---

# 1. Representation / state methods

## Frozen semantic features
DINO / V-JEPA family。

**能测试的科学假设：**
- semantic invariance何时帮助/伤害 controllability；
- frozen reusable state vs task-specialized state 的 R3 frontier。

**不能只做：**
换 backbone + leaderboard。

## End-to-end JEPA / anti-collapse
LeWM、SIGReg、sensorimotor/action-NCE。

**可生成：**
- data objective如何塑造 geometry；
- R1 data composition × representation；
- R3 objective/query dimensionality × latent closure。

## Physical / proprio / state grounding
SCALE、PSG、physical grounding。

**可生成：**
- privileged structure作为 oracle；
- 哪些 physical variables对不同 query真正必要。

**风险：**
simulator state supervision本身不是新贡献。

## Belief / memory / multi-future
UWM-JEPA、FIRM、Branch-JEPA、Flow-equivariant memory。

**适用 program：R4。**

可测试：
- point vs belief 的 regime；
- belief是否真的被planner消费；
- epistemic vs aleatoric uncertainty需要不同表示吗？

---

# 2. Dynamics methods

## Generic nonlinear recursive predictor
LeWM / JEPA-WM baseline。

用作 default substrate。

## Multi-step / direct horizon
RC-aux multi-horizon、Fast/VLWM、Universal Horizon。

**适用 R2：**
- recursion vs direct prediction frontier；
- horizon-dependent predictive object。

## Structured operators
SALT state-affine、Bilinear WM。

**能生成：**
- error propagation structure是否比 raw accuracy更重要；
- simple operator在哪些 dynamics regime足够。

**不能只做：**
把 affine/bilinear塞进新benchmark。

## Distributional / flow / branches
Flow-JEPA、Branch-JEPA、Var-JEPA。

**适用 R2/R4：**
- stochasticity/multimodality是否真的要求 distribution；
- uncertainty representation是否改变 action。

## Path-space / trajectory distribution
Path-space formulation、trajectory-level flow等。

**潜在 method-led seed：**
如果 R2 中 irreversible/contact dynamics 导致 one-step/direct-horizon都出现系统 failure，可检验：
> path-level structure / irreversibility是否是更自然 predictive object？

先要有 program evidence，不预注册“entropy production regularizer”。

---

# 3. Geometry / controllability methods

## Euclidean latent metric
baseline。

## Temporal distance / reachability
TD-JEPA、RC-aux。

**适用 R1：**
data-derived semantics到底识别什么。

## Quasimetric / hitting-time geometry
QRL、Multistep QRL、IEL。

**method-led价值：**
方向性、triangle inequality、Bellman/local consistency提供一个清晰理论 hammer。

可产生的好 hypothesis：
> 当 behavior trajectories 对 same pair 给出多种 route length 时，local Bellman/quasimetric structure是否比 raw Monte-Carlo temporal gap更 invariant？

这比“把QRL loss移植到LeWM”更有科学含义。

## Straightening / geometry regularization
Temporal Straightening、CGS、ATLAS/AnisoWM。

适合验证 planner geometry mechanism，不单独作为 R#。

---

# 4. Decision-alignment methods

## Value-aware / value-equivalent
Goal-Aware Prediction、Value Equivalence、Rank-One Corner、Value-Aligned WM。

**适用 R3：**
- objective rank；
- query family；
- specialization vs reusable closure。

好 hypothesis：
> query family维度增长时，task-specific supervision需要多少 predictive closure才能保持 unseen-query planning？

## Candidate-local ordinal / decision-focused
DA-LeWM、D-JEPA。

**适用 R3/R5：**
- final candidate selection所需信息；
- candidate-distribution shift；
- decision-local reliability。

风险：generic “rank matters” 已占。

---

# 5. Data / exploration methods

## Passive behavior datasets
默认。

## Coverage diversification
random/explore/multi-route。

## Conditional action excitation
P94。

**适用 R1：**
transition identifiability baseline。

## Same-reset counterfactual branches
Do-JEPA / FIRM。

**适用 R1：**
直接 action-effect supervision。

## Active probing / information gain
Task-Sufficient WM。

**适用 R1/R4：**
- query-aware probing；
- hidden-parameter identification；
- data value per environment step。

## Failure / recovery data
Foresight/FARM邻域提供 motivation。

**适用 R1/R5：**
成功数据是否缺少 planner失败边界附近的信息？

---

# 6. Planning methods

## Sampling MPC
CEM / iCEM / MPPI。

baseline，尤其适合 candidate audit。

## Gradient-based planning
Parallel stochastic gradient planning、LEAP等。

**可作为 R2 compute/search consumer变化**。

## Learned proposal / intuition
IMWM、SAGE。

适用 R2/R5：
- search amortization；
- model vs intuition trust。

## Amortized planning
GC-IDM、LeFlow、RP1。

适用 R2。

## Hierarchy / subgoal
HWM、FF-JEPA、Anchored Planning。

适用 R2：
- predictive abstraction × horizon。

## Adaptive replanning / compute
AdaReP。

适用 R5：
- mismatch→replanning 已占；
- 可作为一个 recovery action。

---

# 7. Trust / adaptation methods

## Ensemble / uncertainty
PLDM等。

## Support / intervention fidelity
Control Theory、Intervention Gap。

## Error detector / failure readout
MEND、FARM、Foresight。

## Feedback state
Feedback WM。

## Gradient / residual adaptation
AdaJEPA、Sandwich Residual、ReDRAW。

## Hybrid / gate
IMWM reliability gate。

**R5 的核心不是再发明一个 detector，而是：**
> detector / signal / failure type 与 **哪种 repair action** 的关系。

---

# 8. Method-led seed 生成协议

允许本地 agent从一个方法原理出发，但必须填写：

### 8.1 它属于哪个 R#？
没有重要 parent program → 不做。

### 8.2 它提出什么新预测？
例：
- quasimetric：multi-route data下 local consistency应比 raw temporal gap更稳定；
- belief filter：persistent hidden parameter下 history point state会出现可预测 regret；
- active probing：低 action-excitation区域，decision-boundary probe应比 random coverage更值钱；
- modular conditioning：query只进入proposal可能保留 reusable dynamics。

### 8.3 什么结果会证伪？
必须有。

### 8.4 nearest method 已经证明什么？
不能只换名字。

### 8.5 downstream consequence是什么？
最终连到 data efficiency / candidate regret / closed-loop / transfer / compute。

---

# 9. 当前特别值得留作 method-led ammunition

不是当前 paper commitments：

1. **quasimetric / Bellman geometry** → R1；
2. **active probing / experiment design** → R1/R4；
3. **direct arbitrary-horizon / successor occupancy** → R2；
4. **path-distribution / irreversibility** → R2；
5. **selective/modular query conditioning** → R3；
6. **belief / multi-hypothesis filtering** → R4；
7. **adaptive control / gating / metareasoning** → R5。

本地 agent可以在真实 experiment evidence出现后，从这里选 hammer；不必等对话 agent指定。
