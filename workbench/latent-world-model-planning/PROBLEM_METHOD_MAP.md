# Problem × Method Map — latent world-model planning

更新：2026-10-02。  
用途：决定**该测什么、一个结果允许归因到哪一层、什么 claim 已拥挤**。不是 idea 清单。

## 1. End-to-end planning 的七层因果链

给定 observation history (h_t)、goal (g)、offline dataset (D_eta)、candidate action sequence (a_{t:t+H-1})：

```text
L0 data / behavior β
      ↓
L1 representation z = E(o)
      ↓
L2 dynamics ẑ = F(z, a)
      ↓
L3 planning metric C(ẑ, zg)
      ↓
L4 proposal / optimizer q(a | h,g)
      ↓
L5 temporal target / abstraction
      ↓
L6 selection → environment execution → utility
```

### L0 — Data / behavior geometry
**问题：** environment 允许什么 transition，与 dataset 中 behavior 如何把这些 transition 串成 trajectories，是两件事。  
**变量：** local transition support、route frequency、episode boundary、goal source、behavior optimality、stochasticity。  
**近邻：** PLDM、OGBench、QRL/quasimetric、RC-aux、TD-JEPA、Traj-LeWM、Behavior-Invariant Task Rep。

### L1 — Representation / state
**问题：** state/action/task information 有没有保留？保留在哪些方向？regularizer 自己塑造了什么 geometry？  
**近邻：** DINO-WM、LeWM、SMWM/AC-MTM、SCALE、PSG-JEPA、physically grounded JEPA、ATLAS、AnisoWM、ALeWM、Task-Sufficient WMs。

### L2 — Dynamics / rollout
**问题：** action-conditioned future 是否正确；recursive error 如何传播；counterfactual actions 是否可区分；stochastic futures 是否被平均？  
**近邻：** JEPA-WMs、Fast-LeWM、VLWM、Flow-JEPA、SALT、ActSWM、AD-WM、MEND、Control Theory of Predictability。

### L3 — Planning metric / objective
**问题：** planner 实际用的 (C) 能否对**当前 candidate distribution**排序？representation 有信息不代表 L2 cost会用。  
**近邻：** Temporal Straightening、CGS、Decision-Metric Alignment、Objective Is the Bottleneck、RC-aux、TD-JEPA、Traj-LeWM、LEAP、Anchored Planning。

### L4 — Proposal / optimizer / planner
**问题：** good plan 是否进入 candidate set？finite-budget optimizer 是否找到它？planner 是否主动走入 world-model fidelity 低的区域？  
**近邻：** IMWM、SAGE、LeFlow、RP1、GC-IDM、Parallel Stochastic Gradient Planner、Control Theory of Predictability。

### L5 — Temporal target / abstraction
**问题：** model rollout horizon、goal distance、action chunk、replanning interval、subgoal timescale 是否匹配？  
**近邻：** Planning Limits、Hi-LeWM、HWM、Dual-WM、FlexiWorld、Fast/VLWM、Anchored Planning。

### L6 — Closed-loop consequence
**问题：** internal cost/rank/probe/consistency 的改善有没有变成真实 task outcome？  
**近邻：** World-In-World、ACID、DA-LeWM、AD-WM、Planning Limits。

---

## 2. Ownership matrix

| 方法 / 工作 | Data | Rep | Dyn | Metric | Search | Time | 已占核心 |
|---|---:|---:|---:|---:|---:|---:|---|
| DINO-WM |  | ● | ● | ● | ● |  | frozen foundation feature latent planning |
| PLDM | ● | ● | ● | ● | ● |  | offline data regimes + uncertainty-aware latent planning |
| LeWM |  | ● | ● | ● | ● |  | simple end-to-end compact JEPA |
| JEPA-WMs |  | ● | ● | △ | ● | ● | design-space / recipe characterization |
| Temporal Straightening |  | ● |  | ● | △ |  | temporal curvature / geodesic planning geometry |
| CGS |  | ● | △ | ● | ● |  | local control geometry + finite-budget sampling |
| SMWM / AC-MTM |  | ● | △ |  |  |  | inverse/action supervision for representation |
| PSG / Physical grounding |  | ● | △ |  |  | ● | proprioceptive / state-change grounding |
| SCALE |  | ● |  | ● |  |  | privileged state-distance calibration |
| ATLAS / AnisoWM |  | ● |  | ● |  |  | relational / anisotropic geometry |
| ALeWM |  | ● | ● |  |  | ● | adaptive latent capacity |
| DA-LeWM |  | ● | ● | ● | ● |  | decision-metric / CEM-stage alignment |
| RC-aux | ● | ● | ● | ● | △ | ● | trajectory-derived finite-budget reachability |
| TD-JEPA | ● | ● | ● | ● |  | ● | trajectory-derived directed temporal progress |
| Traj-LeWM | ● | ● |  | ● | ● | ● | full-path preference / path-aware cost |
| Fast/VLWM |  |  | ● |  |  | ● | direct/variable-horizon prediction |
| Flow-JEPA |  |  | ● |  |  | ● | stochastic whole-trajectory prediction |
| SALT |  |  | ● |  |  | ● | recursive error propagation / state-affine transition |
| ActSWM |  | ● | ● |  |  | ● | action-sensitive futures / context collapse |
| AD-WM |  | ● | ● | △ | ● |  | counterfactual action discrimination / elite regret |
| Control Theory Predictability | ● |  | ● | ● | ● |  | planner-reachable fidelity / off-manifold divergence |
| Objective Is Bottleneck |  | ● |  | ● | ● | ● | representation info vs usable planning objective |
| ACID |  |  | △ | ● | ● |  | inverse-cycle transition consistency |
| GC-IDM | ● | ● |  |  | ● | ● | amortized goal-conditioned inverse planner |
| IMWM | ● |  |  | ● | ● |  | ideal dynamics still search-limited |
| SAGE | ● |  |  |  | ● | ● | subgoal-conditioned proposals |
| LeFlow | ● | ● |  |  | ● | ● | generative latent plan prior |
| RP1 |  |  |  |  | ● |  | learned plan-update operator |
| HWM / Hi-LeWM / Dual-WM |  | ● | ● | ● | ● | ● | hierarchy / multiscale temporal roles |
| Planning Limits |  | ● | ● | ● | ● | ● | finite plannable range even with perfect dynamics |
| What Must… |  | ● | ● | ● | ● |  | mechanism / response / decision sufficiency |
| QRL / multistep quasimetric | ● | ● |  | ● | policy | ● | optimal goal distance from suboptimal behavior data |
| Task-Sufficient WMs | ● | ● | ● |  | policy |  | active identification of minimal sufficient state |
| World-In-World | ● | ● | ● | ● | ● | ● | closed-loop embodied utility benchmark |

`●` 核心；`△` 间接。矩阵的作用是防止 local agent 看到一个 failure 就误以为“这一层没人做”。

---

## 3. Oracle ladder：新 lead 先定位，再加方法

对固定 ((start, goal)) 和相同 candidate pool：

1. **Environment utility:** 执行 candidate 得到 (U_{env}(a))。
2. **Encoded-real endpoint score:** (C(E(o_H^{real}), E(o_g)))。
3. **Predicted endpoint score:** (C(hat z_H, E(o_g)))。
4. **Candidate-set oracle:** pool 中按 (U_{env}) 选最好者。
5. **Proposal oracle / retrieved valid plan:** 判断 candidate-set ceiling。
6. **True-dynamics scoring:** 可重置 simulator 中替换 learned dynamics。
7. **Nearby true subgoal diagnostic:** 判断 far final goal interface。

### 归因规则

- 2 坏：metric/representation 已足够解释，别只怪 dynamics。
- 2 好、3 坏：rollout/dynamics更可疑。
- 4 本来就低：candidate proposal ceiling，不应只修 scoring。
- 6 仍失败：不能只怪 learned dynamics。
- 7 大幅救：target/horizon interface压力大，但 Anchored Planning / Planning Limits 已是强近邻。
- internal verifier/uncertainty/probe高：**不能**替代 environment utility。

---

## 4. 六个 load-bearing interaction

### A. Data × planning geometry
Trajectory gap/reachability supervision直接依赖 behavior route。环境最短距离不变时，(Delta_eta=j-i) 可以因 detour / route mixture / factorization 而变化。

**I01 就在这里，但必须做 same-local-evidence identification。**

### B. Dynamics × metric × candidate margin
Encoder geometry再好，terminal rollout error 在 elite margin 很小时也能翻转 ranking。DA-LeWM 已把 distortion/error/margin联系起来；AD-WM又把 elite regret与 counterfactual action discrimination连接起来。

### C. Proposal × metric
Random bank alignment高，不保证 optimizer产生的 elite bank仍可分；planner本身改变 query distribution。

### D. Planner × model support
Candidate optimizer会进入 planner-reachable measure。P40 已直接 formalize off-manifold divergence；因此 generic“search OOD”不是新 idea，只是 I03 diagnostic。

### E. Horizon × proposal / target
goal越远、action dimension越高，candidate ceiling和finite planning range同时变化；SAGE/Planning Limits/Anchored Planning/HWM已覆盖多个切面。

### F. History × action discrimination
POMDP/aliasing 下 inverse-action recoverability可能不可识别。I05 只有找到 clean POMDP substrate 才重开，不能做 context-length sweep。

---

## 5. 红区 / 黄区 / 当前矿层

### 红区：只作 baseline / measurement

- prediction error ≠ planning success
- latent L2 ≠ real progress
- information present but objective unusable
- generic reachability / temporal distance
- generic multi-step
- inverse dynamics / physical grounding
- generic action discrimination
- generic path-aware cost
- generic CEM proposal / hierarchy / subgoal
- generic off-support / model exploitation
- generic OOD robustness
- closed-loop evaluation is better

### 黄区：只有出现具体 mechanism 才升级

- trajectory-factorization / route dependence
- bottleneck relocation
- planner-specific elite collapse
- history / observability
- stochastic multimodality
- data support × objective interaction

### 当前优先

1. **I01 trajectory-factorization dependence / route imprinting**
2. **I03 bottleneck regime law**
3. I04 decision-audit calibration
4. I02 support drift = PARKED diagnostic
5. I05 POMDP = PARKED

---

## 6. I01 identification：environment geometry vs trajectory factorization

目标不是普通 “dataset A vs B”。

要求构造：

[
P_{env}(s'|s,a) 	ext{相同},qquad
mathcal T_{local} 	ext{multiset相同},qquad
mathcal W_{1step/history} 	ext{manifest相同},
]

但：

[
mathcal F_{trajectory}^{A}
eq mathcal F_{trajectory}^{B},
]

即同一 local transition evidence 被合法地组织成不同 trajectories，导致 long-range pair/gap statistics不同。

### E03 core：valid cut-and-splice

共享 junction (x)：

```text
original:  p1 -> x -> s1      p2 -> x -> s2
refactor:  p1 -> x -> s2      p2 -> x -> s1
```

所有 adjacent transitions仍来自原 store。若 history window跨 junction变化，就排除/match这些 windows，直到 hash等价。

**比 split-only 更强：** episode splitting只是 logging-boundary sensitivity；cut-and-splice测试真正的 trajectory factorization。

### Negative controls

- LeWM：不读取 long-range pair labels。
- Temporal Straightening / CGS：使用 local temporal/control geometry，不应直接跟 long-range route factorization走。
- QRL/quasimetric：作为“behavior MC statistics vs optimal/local consistency”概念/方法对照。

### Consequence ladder

```text
target/pair statistic shift
      ↓
learned Rϕ / dψ / geometry shift
      ↓
fixed-candidate ordering / regret shift
      ↓
closed-loop decision shift
```

只有第一层变不够。

---

## 7. I03 regime map

E06 初始 fractional grid：

- 2 tasks：topology/navigation + contact-rich
- 3 goal-distance bins
- 2 candidate budgets
- LeWM baseline

oracle ladder标 signature：

```text
R metric/representation
D dynamics
A action-discrimination
P proposal/search
H horizon/target
M mixed
```

只有少数 observable variables能跨 task预测 signature / intervention ranking，才扩 E07。

候选 regime variables：
- goal distance
- candidate margin
- planner-reachable fidelity
- local data support
- action-discrimination margin
- replanning ratio

如果每个 benchmark要单独解释，不形成 science law。

---

## 8. I02 为什么 PARKED

原假设：CEM iteration → support下降 → optimism → false elite → regret。

现在：
- P40 已把 planner-reachable/off-manifold divergence formalize；
- PLDM已有 ensemble uncertainty；
- offline MBRL model exploitation是经典；
- Hi-LeWM已有 search-distribution mismatch。

因此 E05 只在 I03 需要定位 search/support层时跑。重开必须找到这些现有量解释不了的更具体 planner-stage law + distinct intervention。

---

## 9. Workbench 的“成功”定义

不是图多，而是至少得到一种：

- **new distinction:** 原来混在一起的两个量，在 controlled intervention 后对 decision有不同后果；
- **new failure law/regime:** 能跨方法/任务预测何时谁失败；
- **minimal intervention:** 从机制自然推出并跨 substrate验证；
- **identification protocol:** positive/negative/oracle controls证明它测的是 load-bearing quantity，并因此改变方法设计。

普通 leaderboard、更多 seed、更多 benchmark、单个相关性都不是终点。