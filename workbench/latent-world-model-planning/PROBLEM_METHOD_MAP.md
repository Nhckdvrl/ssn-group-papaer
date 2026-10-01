# Problem × Method Map — latent world-model planning

更新：2026-10-02。  
用途：决定“该测什么 / 哪个 baseline 能排除什么 / 哪些 claim 已拥挤”。**这不是 idea 清单。**

## 1. 把 end-to-end planning 拆成七个可干预层

给定 observation history (h_t)、goal (g)、offline dataset (D_eta)、candidate action sequence (a_{t:t+H-1})：

```text
data / behavior β
      ↓
representation z = E(o)
      ↓
dynamics ẑ = F(z, a)
      ↓
planning metric C(ẑ, zg)
      ↓
proposal / optimizer q(a | h,g)
      ↓
selection / replanning
      ↓
environment execution → task utility
```

### L0 Data / behavior geometry
问题：dataset 中哪些 local transitions 存在？它们被怎样串成 trajectories？behavior 走了什么 detour/loop？goal 如何抽样？  
近邻：PLDM、OGBench、QRL/quasimetric、TD-JEPA、RC-aux。

### L1 Representation state
问题：state/action/task 信息有没有保留？哪些方向承载？是否 collapse？  
近邻：DINO-WM、LeWM、SMWM、AC-MTM、SCALE、ATLAS。

### L2 Dynamics / rollout
问题：action-conditioned next latent 是否正确；recursive error 怎样传播；不同 action 是否仍可区分；stochastic branch 是否被平均？  
近邻：JEPA-WMs、Fast-LeWM、VLWM、Flow-JEPA、SALT、ActSWM、MEND。

### L3 Planning metric
问题：planner 使用的 (C) 能否对**当前 candidate distribution**正确排序？  
近邻：Temporal Straightening、DA-LeWM、RC-aux、TD-JEPA、LEAP、Anchored Planning。

### L4 Proposal / search
问题：good plan 是否进入 candidate set？optimizer 是否逐步进入 OOD/support hole？  
近邻：IMWM、SAGE、LeFlow、RP1、GC-IDM。

### L5 Temporal abstraction / target interface
问题：rollout horizon、goal distance、action chunk、subgoal timescale 是否匹配？  
近邻：Planning Limits、Hi-LeWM、HWM、Dual-WM、FlexiWorld、Anchored Planning。

### L6 Closed-loop execution
问题：internal cost/rank/consistency 的改善有没有变成 environment success，而不是 self-consistency？  
近邻：World-In-World、ACID、Decision-Metric Alignment、Planning Limits。

---

## 2. 方法 ownership matrix

| 方法/论文 | Data | Rep. | Dynamics | Metric | Proposal/Search | Time | 主要已占 claim |
|---|---:|---:|---:|---:|---:|---:|---|
| DINO-WM |  | ● | ● | ● | ● |  | frozen visual feature latent planning |
| PLDM | ● | ● | ● | ● | ● |  | offline reward-free data regimes + uncertainty planning |
| LeWM |  | ● | ● | ● | ● |  | simple end-to-end anti-collapse + compact planning |
| JEPA-WMs |  | ● | ● |  | ● | ● | recipe/design-space study |
| Temporal Straightening |  | ● |  | ● | △ |  | curvature → planner-friendly geometry |
| SMWM / AC-MTM |  | ● | △ |  |  |  | inverse/action contrastive anti-collapse |
| SCALE |  | ● |  | ● |  |  | privileged state-distance calibration |
| DA-LeWM |  | ● | ● | ● | ● |  | Plan-Real/CEM-stage alignment + action heads |
| RC-aux | ● | ● | ● | ● | △ | ● | finite-budget reachability + multi-horizon |
| TD-JEPA | ● | ● | ● | ● |  | ● | trajectory-derived directed temporal progress |
| Fast/VLWM |  |  | ● |  |  | ● | direct/prefix variable horizon prediction |
| Flow-JEPA |  |  | ● |  |  |  | stochastic whole-trajectory latent prediction |
| SALT |  |  | ● |  |  | ● | error-propagation structure / state-affine transition |
| ActSWM |  | ● | ● |  |  | ● | action-sensitive rollout / context collapse |
| ACID |  |  | △ | ● | ● |  | inverse-cycle realizability verifier |
| GC-IDM | ● | ● |  |  | ● | ● | amortized direct action inference |
| IMWM | ● |  |  | ● | ● |  | perfect dynamics not enough; demo intuition |
| SAGE | ● |  |  |  | ● | ● | subgoal-conditioned proposals |
| LeFlow | ● | ● |  |  | ● | ● | amortized generative latent plan |
| RP1 |  |  |  |  | ● |  | learned plan-update operator |
| Hi-LeWM/HWM |  | ● | ● | ● | ● | ● | hierarchy/multiscale planning |
| Planning Limits |  | ● | ● | ● | ● | ● | finite plannable range, even with perfect dynamics |
| What Must… |  | ● | ● | ● | ● |  | mechanism/response/decision sufficiency |
| QRL/quasimetric | ● | ● |  | ● | policy | ● | optimal goal distance from suboptimal/stochastic data |

“●”表示核心，`△` 表示间接。矩阵目的是防止 local agent 看到某个 failure 就误以为那个层没人做。

---

## 3. Oracle ladder：所有新 lead 先定位，不要直接加模块

对固定 ((start,goal)) 和**相同 candidate pool**，逐层替换：

1. **Observed end-state oracle**：执行候选到 simulator，得到真实 terminal/task utility (U_{env})。
2. **Encoded-real endpoint**：(C(E(o_H^{real}), E(o_g)))。隔离 metric/representation，不含 rollout error。
3. **Predicted endpoint**：(C(hat z_H, E(o_g)))。2→3 的差来自 dynamics/rollout。
4. **Candidate oracle**：固定 pool 中选 (U_{env}) 最好者。selected vs oracle = selection regret。
5. **Proposal oracle / retrieved expert segment（任务允许时）**：判断 candidate-set ceiling。
6. **True-dynamics rollout（可重置 simulator 才用）**：把 learned dynamics 替成 environment；仍失败才能把 blame 推向 objective/search/horizon。
7. **Nearby-ground-truth subgoal（diagnostic only）**：判断 final-goal interface vs local controller。

### 禁止错误归因
- 2 好、3 坏 → 不能说“representation geometry 坏”。
- fixed-pool oracle 本来就差 → 不能只修 scoring。
- true-dynamics 仍差 → 不能只说 predictor 不够准。
- internal verifier 高 → 不能叫“realizable”，除非 environment execution 支持。
- simulator privileged state 只作 oracle/diagnostic；不能与纯 pixel method 混成公平主表。

---

## 4. 关键交互，不应当被边际 ablation 隐藏

### A. Data × geometry
trajectory gap/reachability supervision 与 behavior policy 直接耦合；如果 behavior 绕路，(Delta=j-i) 会变，但 environment shortest distance 可不变。

### B. Dynamics × metric
即便 encoder geometry 很好，rollout error 可在 elite margin 小时翻转 ranking；DA-LeWM 已将 terminal error + candidate margin 写入 sufficient-condition 分析。

### C. Proposal × metric
random candidate 上 Spearman 很高，不表示 CEM elite 上仍能区分；optimizer 会主动改变 candidate distribution。

### D. Horizon × proposal
goal 越远、candidate action dimension 越大，有限候选预算的 proposal bottleneck 与 planning-range bottleneck同时上升；SAGE/Planning Limits 已分别占一部分。

### E. History × action sensitivity
在 partial observability 下，inverse-action recoverability/transition separation 可能因为 observation aliasing 而无解；不能把它误判成 dynamics architecture failure。

### F. OOD × optimizer
CEM/gradient optimizer 不是被动 evaluation distribution；它会搜 model 的低-cost区域。若这些区域缺数据 support，model exploitation 可能被放大。

---

## 5. 红区与黄区

### 红区（只作 baseline/测量）
- prediction error ≠ planning success；
- latent L2 ≠ real progress；
- generic reachability/temporal distance；
- generic multi-step supervision；
- inverse dynamics/action consistency；
- generic long-horizon/subgoal/hierarchy；
- generic CEM learned proposal；
- generic OOD robustness / visual perturbation。

### 黄区（只有形成更具体 mechanism 才可能升级）
- candidate-support drift；
- history / observability；
- stochastic multimodality；
- data coverage；
- planner-specific metric alignment；
- bottleneck relocation。

### 当前高收益矿层
1. **behavior-policy geometry contamination**：trajectory-derived “planning geometry” 是否随 behavior organization 改变，即便 local transition support/dynamics 不变？
2. **support drift chain**：optimizer iteration → data-support下降 → predicted optimism/false elite → environment regret，是否是 compact JEPA planners 的稳定 failure chain？
3. **bottleneck phase/regime**：goal distance × data support × search budget 改变时，真正限制 performance 的层是否系统迁移？

---

## 6. I01 的核心识别设计：环境几何 vs behavior 几何

目标不是“换一个 dataset 再看分数”，而是尽量构造：

[
P_{	ext{env}}(s'|s,a) 	ext{相同},quad
	ext{local transition support 尽量相同},quad
	ext{behavior path / episode organization 不同}.
]

### 最干净的三种 intervention

**(a) Episode-partition invariance（最便宜）**  
相同原始 transitions 与视觉帧，改变 trajectory boundary / pair sampling metadata，使 RC-aux/TD-JEPA 的 long-pair labels 改变，但 LeWM one-step training windows 保持 byte-identical manifest。  
风险：若改 boundary 也改 local training windows，则识别失败；实验卡必须 hash one-step sample set。

**(b) Route inefficiency / detour**  
TwoRoom/maze 中同 start/goal 和可行 transition graph，behavior policy 一个走近最短路，一个系统性 detour/loop。通过 reweight/subsample 尽量匹配 state/edge occupancy。

**(c) Route-mixture**  
保持可达 graph 和局部 edge support，改变不同 route 的 mixture，使同 state-pair 的 observed temporal gap 分布变化。

### 读数层
- supervision target shift：同 pair 的 label/temporal-gap distribution；
- learned geometry/head shift：(R(z,z',h))、TD distance、rank；
- environment-oracle shortest distance/reachability（navigation 首先用）；
- fixed candidate Plan-Real / regret；
- closed-loop success/stitching；
- LeWM/Straightening 等不直接依赖 long-pair metadata 的 negative controls。

如果只看到 head 输出变化但 planning 不变 → 不升级；如果只有 novel goal/coverage同时变 → 不能归因于 behavior geometry。

---

## 7. I02 的 support-drift chain

每个 CEM stage (k) 保存**同一批候选**：
- action-chunk kNN / BC log-likelihood（state/history conditioned）
- ensemble disagreement（PLDM-style，可用时）
- predicted latent cost
- real simulator utility（小样本 candidate audit）
- action magnitude/smoothness/bounds
- ACID consistency / MEND score（可用时）

核心曲线：
[
	ext{support}(k),quad
	ext{optimism gap}(k)=C_{	ext{pred}}-C_{	ext{real-rank}},quad
	ext{false-elite rate}(k),quad
	ext{candidate regret}(k)
]

只有 support 下降**先于并预测** false elite，且匹配 action magnitude/compute 后仍存在，才值得方法化。

---

## 8. I03 的 bottleneck regime map

三组可替换组件，不跑全 Cartesian product：

- **geometry/metric:** LeWM base vs one strong geometry method（优先 corrected Temporal Straightening 或 RC-aux training-only）。
- **dynamics:** LeWM vs SALT（代码成熟后）或 Fast-LeWM/multi-horizon。
- **proposal:** CEM vs one strong proposal method（已有 checkpoint 时 SAGE/GC-IDM/IMWM 其一）。

先在 2 个任务 × 3 个 goal-distance bins × 2 search budgets 做 fractional factorial。  
每格同时跑 oracle ladder，问：
- candidate ceiling 是否低？
- real-endpoint ranking 是否低？
- predicted-vs-real endpoint 是否翻转？
- true-dynamics 是否救得回来？
- 近 subgoal 是否救得回来？

若这些 failure signature 随单一变量（goal distance/data support/candidate margin）形成可复现切换，才扩展多任务、多 seed。

---

## 9. 工作台“成功”的标准

不是生成最多图，而是从实验中得到至少一种：
- 一个**新 distinction**：以前被混成一个问题的两个量，在控制变量后对 decision 有不同后果；
- 一个**新 failure law/regime**：能跨方法/任务预测何时谁失败；
- 一个**新 minimal intervention**：由机制自然推出，并跨至少两种 substrate 验证；
- 或一个**新 identification protocol**：通过 positive/negative/oracle controls 证明它测的是 load-bearing quantity，并改变方法设计。

仅 leaderboard、更多 seed、更多 benchmark、普通 correlation 都不是终点。