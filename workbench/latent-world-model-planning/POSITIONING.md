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
| RC-aux | NeurIPS 2026 | multi-horizon open-loop + finite-budget reachability proxy；trajectory hard negatives识别budget | 轻量 planning-aligned supervision也能成为顶会贡献，但 proxy semantics必须说清 |
| Offline GCRL Quasimetric | NeurIPS 2025 Main | suboptimal/stochastic behavior data 下恢复 optimal goal distance | behavior future ≠ optimal controllability |
| CGCIVL | ICML 2025 | cross-trajectory state-goal pairs必须区分 connected / unconnected | trajectory identity ≠ environment connectivity；I06重要邻居 |
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
| Hidden Failure Modes (ICML'26 Workshop Oral) | replanning interval K / score time index / controllability interface can dominate apparent model quality | “terminal score mismatch / waypoint interface” |
| PhyLatent | physical invariance/distinguishability/counterfactual-dynamics collapse | “global noncollapse 不够 / dynamics-relevant collapse” |
| Do-JEPA / FIRM-WM | same-reset physical interventions for action effects / counterfactual branches | “offline factual data缺 counterfactual，所以做 intervention” |
| Bilinear WM | structured bilinear dynamics + action recoverability + efficient planning | “structured dynamics / action recoverability” |
| One-Step Next-Latent… | one-step conditional mean does not generally identify rollout kernel | “one-step objective不是真 world model” |
| FF-JEPA | action-free latent subgoal planner for long horizon | “learn latent subgoal planner” |
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
- world models should be evaluated by decision success；
- terminal-at-H scoring under K<H replanning can be misaligned；
- one-step next-latent regression is not generally a full rollout kernel；
- factual offline data lacks paired counterfactual action outcomes。

## 4. 当前 research mines

### R-N / I06 — **Semantic negatives vs geometric regularization**（当前第一优先）

**直接 tension：**
- TD-JEPA 把 cross-trajectory pair 推到 margin 外，同时明确承认 reachable false negatives；
- TD-JEPA 的 published ablation 又显示去掉 cross-trajectory hinge 会系统伤 Push-T planning；
- RC-aux 把 batch/cross-trajectory goal直接标成 reachability 0，但 temporal hard negatives已经负责 budget identifiability；
- CGCIVL 已证明 cross-trajectory pair不能仅凭 trajectory identity判 connected/unconnected；
- standard contrastive negative是 marginal/reference sample，不等价于逐pair声明不可达。

所以新的问题不是“false negatives exist”，而是：

> **plan-aware WM 的 heuristic negatives 同时承担 semantic reachability supervision 与 non-semantic geometry/repulsion regularization 吗？哪一个才是 published planning gain 的 load-bearing作用？**

只有完成：
1. oracle/certified semantic audit；
2. FULL vs NO-XNEG 的已知作用复现；
3. oracle-valid / censored / count-matched干预；
4. calibration vs dispersion/scale机制分解；
5. fixed-candidate + closed-loop consequence；
6. oracle-free role-separated correction；

才可能形成独立顶会 story。

### R-C / I03 — **Bottleneck relocation / regime law**（第二优先）

近邻已经分别把 blame 放到 metric、dynamics、action discrimination、search、replanning-time index、horizon和target interface。我们的增量不是排一次方法，而是：

> goal distance / candidate margin / planner-reachable fidelity / replanning ratio 等少数变量，能否跨任务预测**哪个 layer 成为 binding bottleneck**，并预测哪类 intervention有效？

P57 Hidden Failure Modes 使 H/K/scoring-index 成为必须控制的 protocol layer；P40 又使 planner-reachable fidelity 成为 search/dynamics control。没有 predictive regime variable 就只是 benchmark。

### R-A / I01 — trajectory-factorization / route imprinting
**已 PARKED。** 代码级审计发现 pinned TD-JEPA / RC-aux 的主要 positive/hard-negative supervision只看短 loaded windows；若强制 full local-window manifest不变而只改更长 episode factorization，当前 loss基本看不到 intervention。因此原 E03/E04 已在运行前 VOID。未来只有真正 full-trajectory objective 或能改变方法实际读取pair distribution的 clean intervention出现时再开。

### R-B / I02 — optimizer support drift
**已 PARKED。** A Control Theory of Predictability 已直接 formalize planner-reachable/off-manifold divergence；再加经典 offline-MBRL model exploitation，generic support-drift story compression risk过高。E05仅保留给 I03 conditional diagnostic。

## 5. Idea 状态

| ID | 状态 | 角色 | 当前最大 compression |
|---|---|---|---|
| I06 semantic negatives vs geometric regularization | **SEED / first gate** | E08→E09→E10 主 mining lane | “false negatives in contrastive learning is old” |
| I03 bottleneck regime switch | **SEED / second** | 统一大量实验的探索引擎 | “只是 component benchmark” |
| I04 random→elite alignment gap | SEED / subordinate | E02 measurement calibration | DA-LeWM + AD-WM elite diagnostics |
| I01 trajectory-factorization | **PARKED** | future full-trajectory objective reserve | pinned methods短window下 treatment不可识别 |
| I02 optimizer support drift | **PARKED** | I03 diagnostic only | P40 + offline MBRL overlap |
| I05 history/POMDP | PARKED | future reserve | 易退化为 context-length sweep |

## 6. 反向 reviewer test

### I06
**“False negatives in contrastive learning 不是老问题吗？”**  
是老问题，所以不能以此为贡献。I06必须证明这里的 negative 被赋予**absolute planning semantics**（distance margin / reachability 0-label），并且 semantic correctness 与 representation regularization 对真实 MPC 有可分离的作用。

**“TD-JEPA 自己已经承认 false negatives。”**  
所以“存在”不是贡献。新信息必须是：它们在真实 sampler中有多频繁、是否 load-bearing、published gain来自哪种作用，以及 role separation 能否保持/提升 planning。

**“oracle filtering不现实。”**  
E09 oracle variants只是 mechanism upper bound；E10若做方法，必须不用 privileged test oracle。

**“CGCIVL 已经区分 connected/unconnected cross-trajectory pairs。”**  
它解决 offline value learning 的 cross-trajectory sampling。我们的 delta 必须落在 visual latent-WM 的 **semantic distance/reachability training → candidate ranking → MPC**，并解释 negatives的双重角色。

### I03
**“不就是 method benchmark？”**  
没有 cross-task predictive regime variable 就不升级。必须预先预测 intervention ranking，不事后解释表格。

**“protocol 差异造成 apparent switch？”**  
H/K、scoring index、goal offset、action block、replanning、candidate budget进入 common manifest；native result与 common-audit result分表。

## 7. Stop rules

- E08 contamination极低/不稳定 → I06 park，不造难例；
- E08 oracle coverage太低 → 只做 certified bounds，不能伪造精确 false-negative rate；
- E09 FULL vs NO-XNEG 不能复制已知 component direction → 先修复现，不做新解释；
- E09 semantic calibration变但 decision null → I06不升级；
- E09所有差异只来自 negative count / gradient scale，且 count-match后消失 → 把机制收敛到 optimization，不夸大 semantic failure；
- E10需要 privileged oracle才有效 → 只能当 diagnostic，不叫方法；
- I03只能 per-task threshold → park；
- E05被 P40 fidelity/PLDM uncertainty完全解释 → 保持 diagnostic。

这些 stop rules只停止具体 lead，不桌面关闭整个 territory。
