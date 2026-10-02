# Research Programs — latent world models beyond “find an empty gap” (2026-10-02)

> 这是当前 workbench 的**最高层科研地图**。  
> Program ≠ paper idea；它是一个足够重要、仍持续产出顶会工作的母问题。  
> 具体 I## / E## 是在 program 内挖 idea 的探针，一个 seed 失败不会关闭 program。

参考规则：[NOVELTY_GROWTH_RULES](NOVELTY_GROWTH_RULES.md)。

---

# R1 — What experience makes a world model actionable?
## 数据、可识别性、主动探索与反事实经验

### 母问题

> **世界模型需要看到什么样的经验，才能学到对 action selection 真正可用的 dynamics / controllability，而不只是复现 behavior policy 的观察统计？**

这比旧 M3“route semantics”大很多。

### 这个 program 已经有哪些答案

- **PLDM**：data quality/diversity/trajectory length/layout改变 latent planning 与 GCRL 相对表现；
- **Controlled-WM Identifiability (P94)**：conditional action excitation决定 counterfactual transition identifiability；
- **QRL / multistep quasimetric / IEL**：suboptimal behavior future statistics与 optimal goal distance需要结构性校正；
- **CGCIVL**：cross-trajectory identity不能直接代表 connectivity；
- **RC-aux / Temporal-Distance JEPA**：trajectory order/gap可作为 planning-aligned supervision，但只是 proxy；
- **Do-JEPA / FIRM-WM**：same-reset counterfactual intervention branches提供直接 action-effect evidence；
- **Task-Sufficient World Models (ICML'26)**：active probing可暴露 control-relevant latent factors；
- **WorldTest**：被动 rollout支持的事实不等于 environment-level query knowledge。

这些不是“把 R1 做完了”，而是在回答：
- excitation够不够？
- observed route能不能当distance？
- 要不要 intervention？
- 要不要主动 probe？
- 什么 query / task 决定需要哪些数据？

### 我们可以挖的方向族

#### R1-A behavior geometry
训练数据 route / temporal organization 是否写进 planner-facing semantics？  
**现有 seed：I09 / E14。**

#### R1-B action excitation vs trajectory diversity
固定 transition count 时：
- 多 action directions；
- 多 routes；
- 多 start states；
- 多 goal compositions；

哪一种 diversity 对 counterfactual planning最值钱？

#### R1-C passive data vs reset-matched interventions
同样 transition budget：
- ordinary behavior trajectories；
- same-state action branches；
- active disagreement probing；

planning lift / identification gain 谁更高？在哪些环境结构下？

#### R1-D failure / recovery data
成功 demo很多，但：
- near-failure；
- blocked action；
- recovery；
- contact failure；

是否对 world-model verifier / controllability特别高价值？

#### R1-E query-aware data acquisition
如果 model最终要支持一族 query：
- 通用 exploration；
- task-sufficient probing；
- uncertainty probing；
- decision-boundary probing；

谁更 sample-efficient，谁更可复用？

### 为什么适合我们的资源

绝大多数实验是：
\`\`\`text
same compact model
× data regime
× seed
× task
\`\`\`

天然单卡独立，且 simulator可批量生成数据；不需要大模型scale。

### 可能长出的论文形态

- data principle / scaling law；
- identifiability boundary；
- active data acquisition method；
- counterfactual-data-efficient training；
- trajectory supervision failure + repair；
- “what data matters for planning?” strong comparative science。

---

# R2 — What predictive object should a world model learn?
## 预测什么、预测多远、把计算放在哪里

### 母问题

> **world model真正需要表示的是 one-step transition、direct k-step future、future path distribution、policy occupancy/successor structure、hierarchical macro transition，还是它们的 hybrid？**

这是比“explicit vs implicit谁赢”更根本的问题。

### 已有方法只是 continuum 上的点

- **LeWM / JEPA-WM / DINO-WM**：explicit action-conditioned rollout；
- **Fast/VLWM/SALT**：multi-step / structured explicit dynamics；
- **Flow-JEPA / Branch-JEPA / UWM**：distribution / multi-future；
- **Universal Horizon Models**：arbitrary-horizon direct prediction；
- **Bagatella TD-JEPA**：policy-conditioned successor / occupancy predictive structure；
- **Jumpy WM**：policy-level multi-timescale occupancy；
- **HWM / Dual-WM / FF-JEPA**：hierarchy；
- **LeFlow / GC-IDM / RP1**：部分 planning computation amortized；
- **TD-MPC2-like**：hybrid model + policy/value + short search。

### 尚未闭合的问题

- horizon多长时 recursive model开始不划算？
- arbitrary action query是否迫使 explicit dynamics？
- reward/query频繁变化时，implicit predictive object还能复用多少？
- stochasticity何时需要 distribution而不是mean state？
- policy family固定时 successor结构是否足够？
- test-time compute受限时，应该把多少 planning amortize到training？
- 环境变化时，哪种 predictive object更容易adapt？

### 当前 seed

**I08 / E13** 是一个入口，不是整个 program。  
E13 先比较 continuum两端并做三本账：
- training compute；
- task/query information；
- deployment compute。

如果发现强 boundary，再加入一个中间 predictive object，而不是继续扩大 leaderboard。

### 可能长出的论文

- regime law；
- adaptive predictive horizon；
- hybrid explicit+occupancy architecture；
- query-dependent predictive object；
- compute allocation principle；
- unification of seemingly different world-model families。

---

# R3 — How specialized should a world model be?
## task/query/planner conditioning vs reusable world knowledge

### 母问题

> **对一个具体 planner/query 做得越“decision-aligned”，world model 是否越高效？它又会在多大程度上丢掉对 unseen goals / rewards / planners / queries 的复用能力？query information 应该注入到哪一层？**

这不是一句“alignment hurts generalization”。

### 理论与近邻

- **Value Equivalence**：只需保留一族 value/policy 所要求的 predictive distinctions；
- **Goal-Aware Prediction / Objective Mismatch**：task-aware modeling可以牺牲无关预测；
- **What Must a WM Distinguish? (P38)**：机制/response/decision sufficiency；query、candidate set、planner共同决定需要的信息；
- **Rank-One Corner**：objective dimensionality决定 latent 安装多少 task closure；
- **Task-Sufficient WM**：主动收集 task-relevant信息并压成 minimal state；
- **Action-Sufficient Goal Reps**：value-sufficient不代表action-sufficient；
- **WorldTest**：general WM 应支持 environment-level diverse queries；
- **Grounded WM**：language query进入 planning representation；
- **Physically Viable WM**：physical abstraction本身应依 intervention query。

这恰恰说明 R3 是一个**正在快速生长的 program**，不是“P38做过所以关闭”。

### 真正值得实验的轴

- query注入位置：
  - encoder / state representation；
  - dynamics；
  - cost / metric；
  - proposal；
  - verifier；
- query数量 / dimensionality；
- seen query → unseen query；
- planner改变；
- candidate distribution改变；
- capacity有限 vs充足；
- single-task data vs multi-task data。

### 新 seed: I10 / E17

不追求“谁都没做过 query-conditioning”，而是：
> **在同一个 compact visual WM stack 中，query conditioning放在哪一层，如何改变 in-query decision efficiency 与 cross-query reuse？**

如果出现稳定 frontier，可以自然长成 modular design / selective conditioning。

### 可能论文形态

- specialization–reuse frontier；
- query-placement law；
- modular world-model interface；
- task-conditioned capacity allocation；
- multi-query training principle。

---

# R4 — What is the right predictive state under partial observability?
## memory、belief、hidden physics 与主动消歧

### 母问题

> **当相同 observation/history 仍兼容多个 action-relevant world states 时，world model 应该保存单一点、history state、belief/distribution，还是主动获取信息？**

### 已有强答案

- FIRM-WM：goal-comparable config + dynamic fiber；
- UWM-JEPA：belief-space predictor；
- Branch-JEPA：多 latent successors；
- Flow Equivariant WM：structured memory；
- Physically Viable WM：hidden physics / intervention gap；
- I-TAP：history-conditioned temporal abstraction；
- POMDP / predictive-state理论。

这些工作证明问题重要，不是关闭理由。

### 还没统一的东西

- history-resolvable vs irreducible uncertainty；
- epistemic hidden physics vs aleatoric branching；
- belief应该只改善prediction，还是 planner要显式risk-aware？
- 何时应该主动 probe environment，而不是被动维护belief？
- goal image只定义 visible target时，hidden dynamic state如何和goal-comparable state交互？

### 当前 seed

I07 / E11 是**最低成本 existence probe**。  
如果 E11失败，淘汰这个 seed；R4本身不关闭，可转向 active disambiguation / belief-consumption / hidden-physics transfer。

### 可能论文

- belief requirement regime；
- active information-gathering planner；
- goal-state × dynamic-belief factorization；
- risk-aware latent MPC；
- uncertainty representation that changes action, not just prediction.

---

# R5 — When should an agent trust, repair, or bypass its world model?
## reliability、feedback、adaptation 与 planning compute routing

### 母问题

> **world model 不可能在所有 state/action/horizon/shift 下都可靠。planner 应何时相信 imagination、缩短 horizon、replan、请求更多数据、在线adapt、用feedback correction，或退回 policy/intuition？**

这不是“uncertainty calibration”一个指标问题，而是**world-model usage policy**。

### 已有方法是不同 recovery actions

- PLDM：ensemble uncertainty惩罚 OOD；
- Control Theory of Predictability：planner-reachable fidelity / exploitation；
- MEND：latent hallucination detection/correction；
- IMWM：world-model vs intuition hybrid reliability gate；
- AdaJEPA：test-time model update；
- Sandwich residual / ReDRAW：轻量adaptation；
- Feedback WM：observer-style feedback；
- AdaReP：按 mismatch动态决定 replanning；
- Foresight：world-model latent做 failure detection；
- Planning Limits：far goals超出 plannable range；
- HWM / subgoal方法：改变 planning horizon/interface。

这些工作没有给一个统一答案：
> **检测到哪种 failure 时，应该采取哪种 recovery action？**

### 新 seed: I11 / E18

先不设计复杂 router。利用现有 checkpoint / shift / horizon：
- 同一 episode/state；
- 多个可用 recovery actions；
- oracle看哪个 intervention真正提高utility；
- 测现有 reliability signals是否能预测 intervention ranking。

若存在稳定 mapping，才考虑 adaptive trust/routing method。

### 为什么适合资源

很多是 released checkpoint + evaluation，不需要重训；大量 OOD / horizon / planner-budget 条件可以独立并行。

### 可能论文

- reliability→intervention law；
- world-model trust calibration for action selection；
- adaptive horizon/replan/adapt router；
- failure-type taxonomy with actionability；
- compute-efficient recovery policy。

---

# Cross-cutting C1 — planner–world-model co-design

Representation / dynamics / query / data的价值都依赖 planner如何消费模型。

因此任何 program都记录：
- candidate set；
- search stage；
- H/K；
- planner budget；
- metric；
- query；
- true candidate utility。

但“planner matters”本身不是 research program的终点。

---

# Cross-cutting C2 — Actionability evidence

所有 internal measurement最终至少要问：

\`\`\`text
does it alter
candidate ordering / candidate availability / selected action
        ↓
real utility / regret / closed-loop success?
\`\`\`

probe可以产生 hypothesis；不能独立承担大 claim。

---

# First-wave mining portfolio

不是“选唯一方向”，而是对多个 program做**便宜而高信息增益的存在性探针**：

| Program | cheap seed | 当前卡 |
|---|---|---|
| R1 data / identifiability | route/data semantics + data-value decomposition | E14；新增 E16 |
| R2 predictive object | explicit↔implicit/direct horizon frontier | E13 |
| R3 specialization/reuse | query placement × unseen-query reuse | 新增 E17 |
| R4 state/belief | actionable hidden ambiguity | E11 |
| R5 trust/recovery | reliability signal × recovery action | 新增 E18 |

一个 seed失败：
- 回 program；
- 记录学到的 boundary；
- 产生下一 seed。

不要写“R# 被 paper X 做过”。

---

# 什么时候集中几十张 GPU

只在一个 program 的 seed拿到下面至少两项后：
- natural effect；
- decision consequence；
- clean intervention；
- strong baseline gap；
- surprising boundary；
- plausible method lever。

然后迅速扩：
- train seeds；
- environments；
- data regimes；
- nearest methods；
- ablations；
- hold-out conditions。

这才是我们多卡、弱互联资源的正确打法。
