# Territory 卡：紧凑潜在世界模型与规划

日期：2026-10-02。通道：our-taste。状态：**PROPOSED / problem-led literature+code-hardened / execution-ready；不是 candidate。**

工作台：[latent-world-model-planning](../../workbench/latent-world-model-planning/README.md)；资源：[RESOURCES](../../RESOURCES.md)。  
全领域地图：[FIELD_PROBLEM_MAP_2026](../../workbench/latent-world-model-planning/FIELD_PROBLEM_MAP_2026.md)。  
研究入口：[RESEARCH_MINES](../../workbench/latent-world-model-planning/RESEARCH_MINES.md)。  
定位 authority：[PAPER_LINEAGE](../../workbench/latent-world-model-planning/PAPER_LINEAGE.md) · [LITERATURE_LEDGER](../../workbench/latent-world-model-planning/LITERATURE_LEDGER.md) · [POSITIONING](../../workbench/latent-world-model-planning/POSITIONING.md)。

## 1. 为什么保留

这不是“找一块没人做过的 world-model 小角落”。保留理由是：

1. **顶会母问题成立。** DINO-WM、PLDM、Temporal Straightening、WorldTest、Jumpy WM、Action-Sufficient Goal Representations 等已证明 representation、data、planning semantics、predictive abstraction 都是顶会级问题。
2. **领域仍没有统一答案。** 2026 papers 分别把成功/失败归因到 geometry、reachability、recursive dynamics、action identifiability、search、belief、data、query interface、test-time adaptation；很多 broad claim已拥挤，但“什么时候哪种结构真正必要”仍未闭合。
3. **可做 controlled science。** compact model + offline trajectory + resettable simulator + candidate-level planner使 oracle replacement / fixed-candidate regret / same-state intervention可行。
4. **资源极匹配。** 单次训练小、独立run多；几十个 GPU slot可以用于 data regimes × seeds × environments × strong baselines，而不依赖多节点高速互联。
5. **方法可从问题自然长。** 不预设必须有新 architecture/loss；先找到 action/decision-level pressure，再做最小 correction。

## 2. 当前排序

### Tier A1 — M3 / I09：behavior trajectory semantics → controllability

核心不是“data distribution matters”，而是：

> 在 **conditional action excitation 与 one-step transition support 已匹配/控制** 后，trajectory-derived planning supervision 是否仍把 higher-order behavior geometry（route / tempo / temporal co-occurrence）写进 deployed reachability/progress，并改变 same test candidate pool 的 ordering / MPC？

为什么这个 exact delta重要：

- RC-aux 自己明确 trajectory offset 只是 empirical proxy；
- Bai/Xiong Temporal-Distance JEPA 直接从 trajectory gap学 directed progress；
- quasimetric GCRL / CGCIVL 已占 behavior-statistics vs optimal controllability broad distinction；
- **P94 Controlled-WM Identifiability** 又进一步证明 behavior policy 的 conditional action excitation本身可决定 counterfactual transition identifiability与planning。

因此 E14 的科学价值完全取决于把普通 coverage / action-excitation解释排掉。

执行：
- Stage A：公开 OGBench `navigate/stitch/explore`、`play/noisy` 只找 sensitivity；
- Stage B：fixed start-goal DIRECT vs DETOUR/LOOP，匹配 state/action/local-transition support 与 conditional action covariance；
- LeWM control + Temporal-Distance JEPA first；
- fixed candidate rank/regret + closed-loop gate；
- signal成立再 RC-aux / E15。

### Tier A2 — M2 / I08：predictive-computation placement frontier

问题不是 explicit vs implicit谁强，而是：

> world-model predictive structure应该保存在 primitive action-conditioned rollout、direct arbitrary-horizon predictor、policy occupancy/successor abstraction、amortized policy/planner，还是 hybrid？什么 regime决定？

TMLR 2026 JEPA-WM study明确把 explicit/implicit training-cost、inference-cost、generalization trade-off 的 direct comparison留作 future direction；Bagatella TD-JEPA、Universal Horizon、Jumpy WM、TD-MPC2等形成 continuum。

E13必须拆三本账：
1. training compute；
2. **task/query information budget**；
3. deployment compute。

重要实现事实：Bagatella TD-JEPA official OGBench eval会从 replay buffer采样约 10k states，并用 OGBench `physics` relabel task reward做 reward inference；这不能和 image-goal MPC的一张 goal observation假装成同等 task information。

目标是跨 task 的 **regime boundary / hold-out prediction**，不是 Pareto表。

### Tier B — M1 / I07：finite-history 后的 actionable ambiguity

Broad POMDP/hidden-physics/belief空间已经很拥挤：
Physically Viable WM、FIRM-WM、UWM-JEPA、Branch-JEPA、Flow Equivariant WM、Action-Sufficient Goal Representations等都直接占位。

所以 E11只问：

> 给足 deployment 可用 finite history 后，是否仍存在多个 action-relevant hidden hypotheses，使同一个 visible history对应不同 best action，并造成 baseline planner regret？

history能解决就 STOP，不造 belief method。

## 3. 子诊断与共享仪器

- **I06 / E08–E10**：heuristic semantic negatives vs global geometric regularization；只作为 M3 子机制。
- **I03 / E06–E07**：representation/dynamics/search/time/query bottleneck oracle；只有形成 cross-task predictive regime law才独立升级。
- **E02**：candidate decision alignment calibration。
- 旧 E03/E04 = VOID；I01/I02 parked；I05由I07 supersede。

## 4. 明确红区

不能再直接当 headline：

prediction≠planning；L2≠progress；generic reachability；generic multi-step；generic inverse/physical grounding；action futures要可分；CEM会OOD；long horizon难；subgoal/hierarchy；POMDP需要history；uncertainty/multimodal future本身；test-time adaptation；latent action；efficient transition；closed-loop比open-loop重要；false negatives存在。

这些都只能是 baseline / diagnostic / related-work pressure。

## 5. 执行图

```text
E00/E01 common substrate
   ├─ E14 M3 FIRST  → conditional E15
   │      └─ E08 → E09 → E10 subdiagnostic
   ├─ E13 M2 SECOND → regime confirmation / one middle-family baseline
   └─ E11 M1 CONDITIONAL → conditional E12

E02/E06 = common scientific instruments
```

第一轮不铺大矩阵。哪个 mine 先得到 **natural failure + decision consequence + clean intervention leverage**，再用多 GPU迅速扩 seeds / task structures / strongest neighbors。

## 6. 顶会升级标准

至少同时满足：

- 真实、自然、社区关心的问题；
- 不是一个内部 probe anomaly；
- candidate action / regret / closed-loop consequence；
- exact related-work delta；
- 强 alternative explanations 被 controlled intervention 拆开；
- 第二 task structure / objective / method确认 scope；
- 若做方法，method 是 diagnosis 的最小后果，而不是“LeWM + module”。

## 7. 当前状态

- science claim = 0；
- GPU run = 0；
- workbench保持 PROPOSED；
- FIELD map / lineage已扩至 P01–P95；
- 本地 agent入口：[LOCAL_AGENT_PROMPT](../../workbench/latent-world-model-planning/LOCAL_AGENT_PROMPT.md)。
