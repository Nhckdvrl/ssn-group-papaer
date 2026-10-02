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
近邻：PLDM、OGBench、QRL/quasimetric、CGCIVL、RC-aux、Bai/Xiong Temporal-Distance JEPA、Traj-LeWM。

### L1 — Representation
**问题：** state/action/task信息有没有保留；regularizer本身塑造了什么geometry；信息“存在”是否可由planner消费？  
近邻：DINO-WM、LeWM、SMWM/AC-MTM、SCALE、PSG-JEPA、physical grounding、ATLAS、AnisoWM、ALeWM、Task-Sufficient WMs。

### L2 — Dynamics
**问题：** action-conditioned future是否正确；recursive errors怎样传播；不同candidate actions是否真的得到可区分future；stochastic/partial observable dynamics是否被mean predictor掩掉？  
近邻：JEPA-WMs、Fast/VLWM、Flow-JEPA、SALT、Bilinear WM、ActSWM、AD-WM、Do-JEPA、FIRM-WM、one-step-not-a-WM。

### L3 — Planning metric / objective
**问题：** planner用的cost能否对当前candidate distribution正确排序？  
近邻：Temporal Straightening、CGS、DA-LeWM、Objective Is the Bottleneck、RC-aux、Bai/Xiong Temporal-Distance JEPA、Traj-LeWM、LEAP、Anchored Planning。

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
| Bai/Xiong Temporal-Distance JEPA | ● | ● | ● | ● | △ | ● | trajectory-derived temporal cost + heuristic negatives |
| Bagatella TD-JEPA | ● | ● | implicit | reward/query | policy | ● | successor-feature / implicit long-horizon predictive abstraction |
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

## 5. Atomic claims vs parent programs

上面的 L0–L6 是**系统归因层**，不是选题层。  
某个 atomic claim已有论文，只代表相应 cell 需要更强 baseline，不代表跨层 research program关闭。

### 已建立的 atomic claims
- prediction error != planning utility；
- L2 geometry != real progress；
- action-conditioned factual prediction不自动等于counterfactual discrimination；
- recursive error / horizon / search / H-K interface会影响planning；
- partial observation / hidden physics需要memory/belief/identification；
- uncertainty/adaptation/feedback可以改善部分 failure。

这些可以反复出现在新 paper 的机制链里，只不能单独当“我们首次发现”。

---

## 6. R1–R5 如何穿过 L0–L6

### R1 Data & Identifiability

\`\`\`text
L0 data composition / interventions / active probes
      ↓
L1-L2 what state & action effects are identified
      ↓
L3 planner-facing reachability/progress semantics
      ↓
L4 candidate comparison
      ↓
L6 real planning utility
\`\`\`

关键 interactions：
- action excitation × route diversity；
- state coverage × counterfactual branches；
- trajectory supervision × planner metric；
- passive vs active/query-aware data。

当前 probes：E14 / E16 / E08。

### R2 Predictive Abstraction

\`\`\`text
L2 predictive object
  one-step / k-step / distribution / occupancy / macro
      ↓
L4 planning/search object
      ↓
L5 horizon + compute placement
      ↓
L6 utility
\`\`\`

关键 interactions：
- horizon × predictive object；
- stochasticity × point/distribution；
- arbitrary-action flexibility × successor/policy abstraction；
- train compute × test compute。

当前 probe：E13。

### R3 Specialization vs Reuse

\`\`\`text
query/task information
   ├─ L1 representation
   ├─ L2 dynamics
   ├─ L3 metric
   └─ L4 proposal / verifier
        ↓
seen decision efficiency ↔ unseen query reuse
        ↓
L6 utility
\`\`\`

关键 interactions：
- query dimensionality × capacity；
- query placement × planner stage；
- multi-query training × reuse；
- query-aware data × reusable dynamics。

当前 probe：E17。

### R4 State / Belief / Information Gathering

\`\`\`text
partial observation / hidden physics
      ↓
L1 point state / memory / belief
      ↓
L2 multi-future / hidden-parameter prediction
      ↓
L4 risk / information-gathering planning
      ↓
L6 utility
\`\`\`

关键 interactions：
- history length × hidden-state persistence；
- epistemic vs aleatoric uncertainty；
- belief representation × planner consumption；
- passive memory × active probing。

当前 probe：E11。

### R5 Trust / Repair / Bypass

\`\`\`text
L1-L5 reliability signals
      ↓
failure type / severity
      ↓
choose intervention:
replan / shorten H / more search / feedback / adapt / fallback
      ↓
L6 utility lift per compute
\`\`\`

关键 interactions：
- mismatch × local dynamics sensitivity；
- support × uncertainty signal；
- goal distance × replanning；
- failure type × repair action。

当前 probe：E18。

---

## 7. Shared oracle family

### 7.1 Candidate decision oracle

固定 start/query + candidate set：
1. real environment utility；
2. encoded-real score；
3. predicted score；
4. true-dynamics score；
5. candidate-set ceiling；
6. selected-action regret；
7. closed-loop outcome。

### 7.2 Data/identifiability oracle（R1）
- state/action support；
- conditional action covariance/excitation；
- counterfactual branch coverage；
- route/path diversity；
- oracle reachability / shortest path；
- intervention fidelity。

### 7.3 Query/reuse oracle（R3）
- seen vs unseen query；
- same physical prediction reused under multiple objectives；
- retraining/conditioning requirement；
- candidate proposal efficiency。

### 7.4 Belief oracle（R4）
- hidden state/parameter；
- observation-history equivalence；
- action utility vector；
- best-action flip；
- information-gain action。

### 7.5 Recovery oracle（R5）
对同 planning state执行多种 repair：
- native；
- replan；
- shorter horizon；
- more search；
- feedback；
- adapt；
- fallback。

记录 utility lift / compute。

---

## 8. Scientific instruments vs paper claims

以下默认是**仪器**：
- E02 random/mid/elite rank；
- E06 bottleneck ladder；
- E08 negative semantic audit；
- probes / latent visualization；
- prediction MSE；
- support/uncertainty scores。

如果某个 instrument 本身暴露一个此前未知、跨task稳定且有decision consequence的 construct，它可以升级；否则只服务 R1–R5。

---

## 9. 已被代码审计淘汰的旧 I01 设计

原 I01要求：
“完整 short-window samples相同，只改更长 episode factorization”。

pinned Temporal-Distance JEPA / RC-aux 主要 temporal pairs来自 loaded short clips；如果 short clips不变，objective几乎看不到 treatment。

因此 E03/E04 VOID 是正确的。  
但它只否定**那个 intervention**，不否定 R1“trajectory/data semantics”program。E14/E16已经用真正改变 model所见经验的方式重开 R1。

---

## 10. Workbench success criteria

最终至少形成一种：

- program-level new distinction；
- regime / phase law；
- data / compute / query allocation principle；
- interaction / unification；
- mechanism / identification result；
- diagnosis-derived minimal method；
- strong comparative science that changes design practice。

普通 leaderboard、更多seed、单一probe、单个false-negative rate都不是终点。  
**近邻多不是失败；没有新的 scientific information 才是失败。**
