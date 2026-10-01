# Positioning / novelty ownership map（D5 hardening）

更新：2026-10-02。  
目标会议：ICLR / ICML / NeurIPS；视觉贡献足够时 CVPR。  
当前科学 claim = 0；本表的任务是**给探索设边界、让 reviewer compression risk 在跑 GPU 前显式化**，不是“桌面证明 novelty”。

## 1. 顶会 / journal 尺度锚点：这个领域什么问题已经被认为值得发表

| 工作 | Venue | 它真正拥有的 claim | 我们要学习的 idea-growth |
|---|---|---|---|
| DINO-WM | ICML 2025 | pretrained visual features + offline latent dynamics 可直接 zero-shot visual-goal planning | 去掉 pixel reconstruction 这一默认前提 |
| PLDM / Reward-Free Offline Data | NeurIPS 2025 Main | 系统比较 offline GCRL 与 latent control；data quality/diversity/layout/stitching 分开 | comparative science 必须让 data regime 改变方法结论 |
| OGBench | ICLR 2025 | 把 stitching / long horizon / vision / stochasticity 拆成能力维度 | benchmark 要揭示结构性能力差异 |
| Temporal Straightening | ICML 2026 | local trajectory curvature 是 planner-consumed geometry；straightening 改善 optimization | broad “representation 不好”压成可操纵几何对象 |
| Offline GCRL Quasimetric | NeurIPS 2025 Main | suboptimal/stochastic behavior data 下恢复 optimal goal distance | behavior future ≠ optimal controllability |
| Multistep Quasimetric | ICLR 2026 | local Bellman optimality 与 global Monte-Carlo stability 的张力/统一 | 从理论 tension 长 objective |
| TempDATA | ICML 2025 | temporal-distance abstraction 帮助 long-horizon offline MBRL | temporal structure 已是成熟邻域 |
| JEPA-WMs / What Drives Success | TMLR 2026 | architecture/training/planner design-space study，simulation + real data | 强 recipe 先做透；普通 sweep 不是 novelty |
| Learning Task-Sufficient WMs | ICML 2026 | active probing + structured model 学 task-specific minimal sufficient latent | “task sufficient”本身是大而成熟的目标 |
| Behavior-Invariant Task Rep + WM | ICML 2026 | offline meta-RL 中 task representation 对 behavior policy invariant | broad behavior-invariance 已有顶会 ownership |
| Parallel Stochastic Gradient Planner | ICML 2026 | differentiable WM 中 virtual states + soft dynamics + stochastic parallel optimization | planner architecture 本身已有顶会空间 |
| World-In-World | ICLR 2026 Oral | generative WM 必须闭环 task-success；visual quality 不够 | diagnostic 必须落到 embodied consequence |
| Sparse Imagination | ICLR 2026 | token-sparse rollout 保 control、降 test-time cost | efficiency compute axis 已成熟 |
| CompACT | CVPR 2026 | 8-token compact world representation + fast planning | representation compression已有视觉顶会路线 |
| GeoWorld | CVPR 2026 | hyperbolic/geometric WM 做 multi-step visual planning | “换非欧 geometry”本身不新 |

结论：**问题尺度成立，且顶会并不要求巨大预训练。** 但 2026 compact-JEPA stack 已非常拥挤，必须通过强 identification / mechanism / regime law 获得自己的 narrative。

## 2. 直接 claim ownership：最容易被 reviewer 压缩成“你不就是 X”的地方

| 近邻 | 已占的具体 claim | 若我们这么做，会被压缩成 |
|---|---|---|
| LeWM | simple end-to-end SIGReg + next-latent compact JEPA | “LeWM 换 loss” |
| JEPA-WMs | model/training/context/planner recipe sweep | “再扫几个 hyperparameter” |
| RC-aux | multi-horizon + finite-budget trajectory-derived reachability | “reachability head v2” |
| TD-JEPA | trajectory step-gap mined directed progress cost | “temporal distance 换写法” |
| Traj-LeWM | full predicted path preference + failure mining + path-aware cost | “再做 trajectory score” |
| Temporal Straightening | curvature / local trajectory straightening | “另一种 straightening” |
| Control-Geometry Straightening | local action↔latent displacement geometry + finite-budget sampling theory | “另一种 planner geometry loss” |
| SCALE | privileged state-distance calibration | “用 simulator state 对齐 latent” |
| PSG-JEPA / physically grounded JEPA | proprioception/state-change grounding | “加 physical state supervision” |
| SMWM / AC-MTM | inverse dynamics / action contrastive anti-collapse | “再加 IDM” |
| AD-WM | factual prediction vs counterfactual action discrimination；CEM elite regret | “让不同 action future 更可分” |
| DA-LeWM | Plan-Real + CEM-stage rank / candidate margin | “我们也测 Spearman/elite rank” |
| ATLAS / AnisoWM | relational geometry / anisotropic regularization | “改 prior / covariance / pairwise geometry” |
| ALeWM | adaptive latent prefix capacity / MixSIGReg | “latent width/capacity sweep” |
| Fast-LeWM / VLWM | direct/parallel/variable-horizon prediction | “多预测几步/少递归” |
| SALT | recursive error propagation + state-affine transition | “one-step error 不重要” |
| ActSWM | Context Collapse / action-sensitive futures | “不同动作未来太像” |
| DRPE | decision-relevant error vs total error | “不是所有 prediction error 都重要” |
| Control Theory of Predictability | planner-reachable measure / off-manifold divergence / plan-cost discrepancy | “CEM 把模型带 OOD 所以 average error 不够” |
| Objective Is the Bottleneck | representation 含信息但 L2 planner objective 用不好 | “objective 比 predictor 更重要” |
| ACID | inverse-cycle intermediate realizability | “加 consistency verifier” |
| MEND | label-free latent hallucination detection/correction | “检测 rollout hallucination” |
| IMWM | ideal dynamics 仍会 finite-sample search fail + demo intuition | “planner 才是 bottleneck” |
| SAGE | subgoal-conditioned candidate proposal | “learned proposal for long horizon” |
| GC-IDM | amortized goal-conditioned inverse action planner | “不跑 CEM” |
| LeFlow | amortized generative latent trajectory prior | “flow planner” |
| RP1 | learned plan-update operator | “learn planner” |
| LEAP | composite energy + differentiable action optimization | “换能量函数/梯度 plan” |
| Planning Limits | finite plannable range even with perfect dynamics | “long horizon 本身有极限” |
| Anchored Planning | far final goal 对短 horizon 误导；nearby anchor 可救 | “用 intermediate goal” |
| Hi-LeWM/HWM/Dual-WM/FlexiWorld | hierarchy / multiscale / split temporal roles / variable chunks | “多时间尺度” |
| RWM | direct latent path + local inverse actions | “在 latent 里直接连路径” |
| What Must a WM Distinguish? | mechanism / response / decision sufficiency | “world model 不必预测所有东西” |
| World-In-World | closed-loop utility > open-loop visual metric | “应该闭环评估” |
| Behavior-Invariant Task Rep | behavior policy invariant task latent | “做 behavior-invariant representation” |

## 3. 明确不能再作为我们的 headline

以下可以当背景、sanity、复现，不是我们的新发现：

- predictive accuracy does not imply planning quality；
- latent Euclidean distance does not reflect true progress；
- information is present but the planner metric cannot use it；
- long-horizon planning is hard / finite planning range exists；
- perfect dynamics alone does not guarantee planning；
- planner-reachable/off-manifold error matters more than data-average MSE；
- inverse dynamics / physical grounding makes latents more action/control aware；
- multi-step/open-loop supervision matches deployment；
- CEM proposal quality is a bottleneck；
- path-aware / subgoal / hierarchy / variable chunk helps long horizons；
- action discrimination matters for counterfactual MPC；
- OOD/model exploitation can hurt offline model planning；
- world models should be evaluated by decision success。

## 4. 当前 research mines

### R-A / I01 — **Trajectory-factorization dependence / route imprinting**（第一优先）

**核心张力：** RC-aux / TD-JEPA / Traj-LeWM 都从 observed trajectories 获得 long-range planning supervision；QRL/quasimetric 明确说 behavior future statistics 与 optimal goal distance 不同；Temporal Straightening 已指出 suboptimal routes 可扭曲 temporal geometry；ICML 2026 又已有 broad behavior-invariant task representation。

所以我们的 delta 绝对不能是：
- “trajectory offset 不是 shortest path”；
- “suboptimal data 会 bias temporal distance”；
- “behavior policy 影响 representation”；
- “数据质量影响 planning”。

只有更强的 identification 才可能成立：

> **同一个 empirical local transition multiset / same one-step windows，被重新组织成不同但合法的 trajectories（valid cut-and-splice / route mixture），trajectory-supervised WM 是否因此学习不同 planning geometry，并做出不同 MPC decisions？**

如果是，这揭示的是**planning objective 对 trajectory factorization/routing 的非不变性**，而不是一般 data shift。

**必须有：**
1. byte/hash-level same local transition/window evidence；
2. valid trajectory refactorization，不是任意打乱；
3. environment shortest/reachability oracle（navigation）；
4. geometry/head → fixed-candidate ranking/regret → closed-loop consequence；
5. LeWM + local-geometry（TS/CGS）negative controls；
6. ≥2 trajectory-supervised methods（RC-aux + TD-JEPA）；
7. minimal dynamics-defined / multi-route / quasimetric-style correction only after evidence；
8. 至少一个 contact-rich extension，不能停在 toy graph。

### R-C / I03 — **Bottleneck relocation / regime law**（第二优先，探索引擎）

近邻已经各自把 blame 放到 metric、dynamics、counterfactual discrimination、search、horizon、target interface。我们的增量不是再排一次方法，而是：

> goal distance / candidate margin / data support 等少数可观测变量，能否跨任务预测 **哪个 layer 成为 binding bottleneck**，以及哪类 intervention 会有效？

要过 reviewer：
- oracle ladder 必须真正 isolate layers；
- 不能每任务手调阈值；
- intervention ranking 必须按 regime 切换；
- 最终最好导出 practical adaptive rule / training principle；
- 至少两种 substrate/model family。

### R-B / I02 — optimizer support drift
**已 PARKED 为独立 idea。** A Control Theory of Predictability 已直接处理 planner-reachable/off-manifold divergence；经典 MOPO/MOReL 与 PLDM 也覆盖 model exploitation / uncertainty。E05 只保留为 I03 判断 search/off-support layer 的 diagnostic。

只有发现 P40 fidelity/uncertainty 都解释不了的 planner-stage-specific failure law，才允许重开。

## 5. Idea 状态

| ID | 状态 | 角色 | 当前最大 compression |
|---|---|---|---|
| I01 trajectory-factorization / route imprinting | **SEED / first gate** | 主 mining lane | “MC temporal distance 本来就 behavior-dependent” |
| I03 bottleneck regime switch | **SEED / second** | 统一大量实验的探索引擎 | “只是 component benchmark” |
| I04 random→elite alignment gap | SEED / subordinate | E02 measurement calibration | DA-LeWM + AD-WM elite diagnostics |
| I02 optimizer support drift | **PARKED** | I03 diagnostic only | P40 + offline MBRL exact conceptual overlap |
| I05 history/POMDP | PARKED | future reserve | 易退化为 context-length sweep |

## 6. 反向 reviewer test

### I01
**“你们不就是重新发现 temporal distance 受 behavior policy 影响？”**  
回答只有在数据支持时成立：不是。我们保持 local transition evidence / one-step windows不变，只改变合法 trajectory factorization；然后观察现有 plan-aware JEPA objective 的 geometry 与真实 MPC decision 是否变化，并用 dynamics-defined correction恢复 invariance。

**“改 trajectory 不就是造假数据？”**  
E03 用真实 transition multiset 在共享 junction做 valid cut/splice；每个 adjacent transition仍是原数据真实 transition。E04 再用自然 shortest/detour/route-mixture behavior policy 复验。

**“navigation toy？”**  
navigation 只用于 exact identification/oracle；主张升级需要 contact-rich continuous task 的 consequence，且不伪称 shortest oracle。

**“这不是 offline GCRL/quasimetric 已解决？”**  
GCRL 建立 behavior-vs-optimal distance理论；我们必须展示它如何进入 **visual latent-WM planning supervision、CEM candidate ordering 与 closed-loop control**，并比较 local/optimal-structure correction。

### I03
**“不就是方法 benchmark？”**  
没有 cross-task predictive regime variable 就不升级。必须能预先预测 intervention ranking，而不是事后解释表格。

**“protocol 差异？”**  
native reproduction 与 common audit protocol 分表；相同 observation/action/time/goal/candidate manifest 才做 layer inference。

## 7. Stop rules

- E03 只改变 head output、decision null → I01 不扩 seed；
- valid splice null、只有 arbitrary split/corruption有结果 → 不包装；
- I01 effect 由 local window/support mismatch解释 → VOID，不归因；
- E04 只有 one toy、contact-rich无 counterpart → scope不足；
- I03 只能 per-task threshold → park；
- E05 由 P40 planner-reachable fidelity/ensemble uncertainty完全解释 → 保持 diagnostic。

这些不是自动关闭 territory；只是防止把 GPU 用在已被近邻压缩或没有 decision consequence 的故事上。