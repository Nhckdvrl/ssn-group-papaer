# Problem × Method Map — latent world-model planning

更新：2026-10-02。  
用途：决定**该测什么、结果能归因到哪一层、哪些 claim 已拥挤**。不是 idea 清单。

## 1. End-to-end planning 的七层链

```text
L0  offline data / trajectory semantics
        ↓
L1  representation  z = E(o)
        ↓
L2  action-conditioned dynamics  z' = F(z,a)
        ↓
L3  planning metric / cost  C(z,g)
        ↓
L4  proposal / optimizer / verifier
        ↓
L5  temporal interface  H, K, action-block, subgoal
        ↓
L6  selected action → real environment utility
```

### L0 — Data / supervision semantics
**问题：** dataset metadata提供的是 observed trajectory facts，还是 environment controllability facts？  
变量：episode membership、temporal gap、cross-batch negatives、behavior optimality、local transition support、goal source。  
近邻：PLDM、OGBench、QRL/quasimetric、CGCIVL、RC-aux、TD-JEPA、Traj-LeWM。

### L1 — Representation
**问题：** state/action/task信息有没有保留；regularizer本身塑造了什么geometry；信息“存在”是否可由planner消费？  
近邻：DINO-WM、LeWM、SMWM/AC-MTM、SCALE、PSG-JEPA、physical grounding、ATLAS、AnisoWM、ALeWM、Task-Sufficient WMs。

### L2 — Dynamics
**问题：** action-conditioned future是否正确；recursive errors怎样传播；不同candidate actions是否真的得到可区分future；stochastic/partial observable dynamics是否被mean predictor掩掉？  
近邻：JEPA-WMs、Fast/VLWM、Flow-JEPA、SALT、Bilinear WM、ActSWM、AD-WM、Do-JEPA、FIRM-WM、one-step-not-a-WM。

### L3 — Planning metric / objective
**问题：** planner用的cost能否对当前candidate distribution正确排序？  
近邻：Temporal Straightening、CGS、DA-LeWM、Objective Is the Bottleneck、RC-aux、TD-JEPA、Traj-LeWM、LEAP、Anchored Planning。

### L4 — Proposal / optimizer / verification
**问题：** good plan有没有进candidate set；finite-budget search能否找到；optimizer是否query model在fidelity低的区域；verifier是否真对应environment executability？  
近邻：IMWM、SAGE、LeFlow、RP1、GC-IDM、Parallel Stochastic Gradient Planning、P40 Control Theory、ACID、MEND。

### L5 — Temporal interface
**问题：** planning horizon H、实际执行prefix K、frameskip/action block、scoring time index、goal distance、subgoal timescale是否对齐？  
近邻：Hidden Failure Modes、Planning Limits、Hi-LeWM/HWM、Dual-WM、FlexiWorld、FF-JEPA、Anchored Planning。

### L6 — Environment consequence
**问题：** internal cost/rank/probe/consistency/calibration改善是否真的改变success/regret？  
近邻：World-In-World、DA-LeWM/AD-WM、Planning Limits、Hidden Failure Modes。

---

## 2. Ownership matrix

| 工作 | Data semantics | Rep | Dyn | Metric | Search | Time | 已占核心 |
|---|---:|---:|---:|---:|---:|---:|---|
| DINO-WM |  | ● | ● | ● | ● |  | frozen foundation features for latent planning |
| PLDM | ● | ● | ● | ● | ● |  | offline data regimes + uncertainty planning |
| OGBench | ● |  |  |  | policy | ● | stitching/long-horizon/data benchmark |
| QRL / multistep quasimetric | ● | ● |  | ● | policy | ● | optimal distance from suboptimal behavior data |
| CGCIVL | ● |  |  | value | policy |  | connected vs unconnected cross-trajectory goals |
| LeWM |  | ● | ● | ● | ● |  | simple compact end-to-end JEPA |
| Temporal Straightening |  | ● |  | ● | △ |  | curvature / geodesic-friendly geometry |
| CGS |  | ● | △ | ● | ● |  | local action-displacement geometry |
| SMWM / AC-MTM |  | ● | △ |  |  |  | inverse/action supervision |
| PSG / Physical grounding |  | ● | △ |  |  | ● | proprio/state-change grounding |
| SCALE |  | ● |  | ● |  |  | privileged state-distance calibration |
| ATLAS / AnisoWM |  | ● |  | ● |  |  | relational / anisotropic geometry |
| ALeWM |  | ● | ● |  |  | ● | adaptive latent capacity |
| DA-LeWM |  | ● | ● | ● | ● |  | Plan-Real / CEM-stage alignment |
| RC-aux | ● | ● | ● | ● | △ | ● | finite-budget trajectory-derived reachability |
| TD-JEPA | ● | ● | ● | ● | △ | ● | trajectory-derived temporal cost + heuristic negatives |
| Traj-LeWM | ● | ● | △ | ● | ● | ● | full-path preference / failure mining |
| Fast/VLWM |  |  | ● |  |  | ● | direct/variable-horizon prediction |
| Flow-JEPA |  |  | ● |  |  | ● | stochastic whole-trajectory prediction |
| SALT |  |  | ● |  |  | ● | recursive propagation / state-affine transition |
| Bilinear WM |  | ● | ● |  | ● |  | structured bilinear dynamics / action recoverability |
| ActSWM |  | ● | ● |  |  | ● | action-sensitive future / context collapse |
| AD-WM |  | ● | ● | △ | ● |  | counterfactual action discrimination / elite regret |
| Do-JEPA / FIRM-WM | ● | ● | ● | △ |  | ● | same-reset interventions / typed state roles |
| P40 Control Theory | ● |  | ● | ● | ● |  | planner-reachable fidelity / off-manifold divergence |
| Objective Is Bottleneck |  | ● |  | ● | ● | ● | information present but objective unusable |
| ACID |  |  | △ | ● | ● |  | inverse-cycle transition consistency |
| GC-IDM | ● | ● |  |  | ● | ● | amortized goal-conditioned inverse planner |
| IMWM | ● |  |  | ● | ● |  | ideal dynamics still search-limited |
| SAGE | ● |  |  |  | ● | ● | subgoal-conditioned proposal |
| LeFlow | ● | ● |  |  | ● | ● | generative latent-plan prior |
| RP1 |  |  |  |  | ● |  | learned planner update |
| Hidden Failure Modes |  |  |  | ● | ● | ● | H/K scoring mismatch + controllability interface |
| Planning Limits |  | ● | ● | ● | ● | ● | finite plannable range even with perfect dynamics |
| HWM / Hi-LeWM / Dual-WM |  | ● | ● | ● | ● | ● | hierarchy / multiscale temporal roles |
| What Must… |  | ● | ● | ● | ● |  | mechanism/response/decision sufficiency |
| World-In-World | ● | ● | ● | ● | ● | ● | closed-loop embodied utility |

“●”核心；“△”间接。矩阵用于**防止重复发现**。

---

## 3. 两套 oracle：I06 与 I03 不混

### 3.1 Pair-semantic oracle（I06）

给一个被训练loss当作 negative 的 pair (s,g)：

- TD-JEPA：它被要求 distance >= margin m；
- RC-aux：它在 budget h 下被标 reachability 0。

audit优先输出：
- CERTIFIED_REACHABLE_WITHIN_BUDGET
- CERTIFIED_OUT_OF_BUDGET
- UNKNOWN

如果能严格求 D*(s,g)，再报告exact shortest-step。  
**trajectory identity本身不能当oracle。**

### 3.2 Decision bottleneck oracle（I03）

固定 start/goal + candidate pool：

1. environment utility of each candidate；
2. encoded-real endpoint score；
3. predicted endpoint score；
4. candidate-set oracle；
5. true-dynamics scoring；
6. counterfactual-action discrimination diagnostic；
7. terminal@H vs prefix@K / running-cost control；
8. nearby true subgoal diagnostic；
9. closed-loop outcome。

归因：
- encoded-real已坏 → metric/representation；
- encoded-real好、predicted坏 → dynamics；
- candidate pool ceiling低 → proposal；
- H/K control救 → time-interface；
- true dynamics仍坏 → 不只怪predictor；
- internal verifier高 ≠ real executable。

---

## 4. 七个 load-bearing interaction

### A. Negative sampling × semantic geometry（I06）
Cross-batch/cross-trajectory metadata不是MDP reachability标签。  
TD-JEPA/RC-aux却把它变成 pair-specific far/unreachable constraint。  
关键问题：**semantic supervision 与 global repulsion/scale 是否混为一体？**

### B. Data behavior × optimal controllability
Observed temporal gap是某个behavior走的路径长度，不自动等于shortest distance。QRL/CGCIVL已占 broad distinction，因此新工作必须落到latent-WM planner consequence。

### C. Dynamics × metric × candidate margin
rollout error在elite margin小时可翻转排序；DA-LeWM已形式化一部分。

### D. Counterfactual action distinction × search
factual prediction好不等于candidate actions可分；AD-WM/PhyLatent/Do-JEPA已强占 broad claim。

### E. Planner distribution × model fidelity
optimizer主动改变query distribution；P40已formalize planner-reachable measure，因此 generic “CEM goes OOD”不是新idea。

### F. H/K/scoring-index × model quality
P57已证明 terminal-at-H在K<H时可制造巨大假failure；所有I03实验必须先control。

### G. Horizon × proposal / target
goal distance、candidate dimension、search budget一起变；Planning Limits/SAGE/HWM/Anchored Planning已覆盖多个面。

---

## 5. 红区 / 黄区 / 当前优先

### 红区
- prediction error != planning
- L2 != real progress
- information exists but metric cannot use it
- generic temporal distance / reachability
- generic multi-step
- inverse/physical grounding
- action discrimination
- path-aware scoring
- CEM OOD / model exploitation
- subgoals / hierarchy
- long horizon
- closed-loop evaluation

### 黄区
- semantic-negative role conflation
- cross-method bottleneck relocation
- planner-stage alignment collapse
- history/POMDP
- stochastic multimodality
- data semantics × planner objective

### 当前优先
1. **I06 semantic negatives vs geometric regularization**
2. **I03 bottleneck regime law**
3. I04 measurement calibration
4. I01 / I02 / I05 PARKED

---

## 6. I06 的逻辑链

```text
actual negative sampler
      ↓
semantic validity audit
      ↓
FULL vs NO-XNEG
      ↓
ORACLE-VALID / CENSOR / COUNT-MATCH
      ↓
semantic calibration  vs  scale/dispersion/gradient role
      ↓
fixed-candidate ranking/regret
      ↓
closed-loop planning
      ↓
oracle-free role separation (only if supported)
```

必须区分：

### Contrastive/reference negative
用于 marginal normalization / density-ratio reference，不等于逐pair“不可能”。

### Planning-semantic negative
直接给pair一个 absolute semantic constraint：
- far beyond margin；
- unreachable within budget。

I06只对后者的 conflation claim novelty。

---

## 7. I03 regime map

初始只做小 fractional grid：

- topology task + contact-rich task
- 3 goal-distance bins
- 2 candidate budgets
- fixed H/K controls

signature：

```text
R  representation/metric
D  dynamics/rollout
A  action discrimination
P  proposal/search
T  time-index/replanning
H  horizon/target
M  mixed/unidentifiable
```

候选 predictive variables：
- goal distance
- candidate margin
- planner-reachable fidelity
- data support
- action-discrimination margin
- H/K ratio

没有跨task predictive relation就不形成paper law。

---

## 8. 被代码审计淘汰的 I01

原设计要求：
“local/full short-window samples完全相同，只改更长 trajectory factorization。”

但 pinned TD-JEPA/RC-aux 的主要 temporal/reachability pairs只来自 loaded short clip；cross negatives也只是batch row permutation，不查episode graph。

所以严格保持short windows不变时，loss几乎看不到treatment。  
**E03/E04在运行前VOID是正确结果：这证明workbench真的在用实现约束筛实验，而不是拿GPU撞墙。**

---

## 9. Workbench 成功标准

至少得到一种：
- 新 distinction，并证明它对decision load-bearing；
- 新跨method/task failure law/regime；
- 由机制自然推出的 minimal intervention；
- validated identification protocol，能改变method design。

普通 leaderboard、更多seed、更多benchmark、单相关性、单个false-negative rate都不是终点。