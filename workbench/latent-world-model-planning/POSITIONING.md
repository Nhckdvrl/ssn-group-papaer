# Positioning / novelty ownership map（D5 hardening）

更新：2026-10-02。  
目标会议：ICLR / ICML / NeurIPS；视觉贡献足够时 CVPR。  
当前科学 claim = 0；本表的任务是**给探索设边界、让 reviewer compression risk 在跑 GPU 前显式化**，不是“桌面证明 novelty”。

## 0. 如何使用 related work：ownership map 不是禁区图

**这是本 workbench 的硬规则。**

AI 研究高度拥挤。一个强近邻已经研究变量 X，**只意味着我们不能把“X 存在 / X 有效”本身当唯一 novelty**；它绝不意味着包含 X 的整个母问题已经关闭。

本文件中的“ownership / compression risk / 已有 claim”应被这样解释：

### 近邻的正面作用

1. **证明母问题值得社区关心。**  
   同一问题连续产生 ICML / ICLR / NeurIPS 工作，通常说明 territory 重要，不是应该逃离。

2. **提供 idea-growth lineage。**  
   强论文最有价值的是：它接受了哪些旧前提、发现了什么 pressure、如何把 broad complaint 压成一个可操纵对象、用什么决定性实验完成 claim。

3. **制造 tension。**  
   两篇论文分别证明 A 与 B，并不意味着 A+B 空间被占完；更可能意味着“什么时候 A、什么时候 B”就是下一层问题。

4. **提供强 baseline。**  
   我们应该在已有最强解释上继续推进，而不是绕开它去找没人关心的残差。

### occupied atomic claim 之后仍然合法的 novelty

- **regime boundary / phase law**：已有方法各自在不同 regime 成立，我们找决定切换的变量；
- **interaction / unification**：两条已有规律组合后出现新的 consequence；
- **new distinction**：原来被混在一起的两个对象被证明应分开；
- **mechanism / identification**：已知现象背后的 load-bearing variable；
- **method from diagnosis**：不是换 loss，而是由新机制自然推出 correction；
- **transfer/generalization boundary**：方法对齐当前 planner/query 时，什么时候保留或损害 reuse；
- **data/compute law**：什么数据或计算资源对某种能力真正必要；
- **strong comparative science**：controlled study 推翻一个领域默认设计假设。

### 什么时候才能真正停止一条方向

不能因为“paper 提到过这个变量”停止。要有更强证据，例如：
- 自然现象在强 baseline 上不存在；
- 最近邻已经**实质解释/解决我们想拥有的同一个 claim**，且没有 meaningful extension；
- effect 只停在 probe / toy，对 decision 没 consequence；
- 深读 + controlled pilot 后，所有差异都被已知更简单解释吸收；
- 资源条件无法获得与目标会议匹配的证据。

因此下面的“已占核心 / compression risk / 红区”统一理解为：

> **不能单独作为 headline 的原子 claim；仍可作为更大新叙事的 ingredient。**

不是“禁止研究这些区域”。

---

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
| Bai/Xiong Temporal-Distance JEPA | trajectory step-gap mined directed progress cost | “temporal distance 换写法” |
| Bagatella TD-JEPA (ICLR'26 Oral) | TD successor-feature / implicit long-horizon predictive representation for zero-shot RL | “再做一个 successor-feature / zero-shot RL objective” |
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
| Controlled-WM Identifiability | conditional action excitation governs transition identification/counterfactual planning | “behavior policy变了所以world model变差” |
| IEL / Hitting-Time Isomorphism | explicit directed hitting-time regression + trajectory-label mismatch + compositional geometry | “把observed gap换成hitting-time / expectile / quasimetric” |
| PLDM comparative science | explicit latent planning vs GCRL under data quality/length/size/OOD task-layout + inference time | “我们再画一张planning-vs-policy regime表” |
| Planner amortization (2021) | MPC + learned proposal + planner-to-policy distillation | “把search搬到training / distill planner” |

## 3. 已被充分占有的原子 headline（可以继续作为更大 story 的 ingredient）

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

## 4. Problem-led research mines（2026-10-02 recalibration）

本 workbench 不再把某个局部 loss 当作第一主旨。当前三个 mine 都对应**模型到底需要解决什么真实决策问题**。

### M1 / I07 — Observable goal ≠ control belief（Tier B conditional）

**Problem:** image goal可以相同，但 hidden velocity/contact/friction/regime 不同会要求不同动作。point latent / goal-comparable latent 是否仍是正确 planning state？

**最强近邻：**
- Physically Viable WM：same-looking scene + hidden physics + intervention failure；
- Branch-JEPA：multiple latent successors；
- FIRM-WM：goal-comparable config + dynamic fiber + intervention branches；
- UWM-JEPA：belief-space predictor；
- Flow Equivariant WM (ICML'26)：structured memory under partial observability；
- UAI'26 selection theorem：低regret下belief-like memory必要；
- I-TAP：history + temporal abstraction + POMDP/regime shift。

**Exact delta 必须是：**
> 给足 deployment 可用 finite observation-action history 后，是否仍存在多个 action-relevant hidden hypotheses，导致 best-action flip / planner regret；只有这个 **history-resolvable vs irreducible actionable ambiguity boundary** 还有空间。

**Reviewer compression：**
- “FIRM 已经拆 state了。”
- “UWM-JEPA 已经做 belief latent。”
- “POMDP 当然要 history。”

所以 E11 必须先建立 **same observation / different hidden state → different best action → deployed planner regret**，不能靠 probe。

### M2 / I08 — Predictive-computation placement（Tier A2）

**Problem:** predictive structure 应保留成 task-agnostic explicit dynamics + test-time search，还是 amortize 到 long-horizon representation/policy，或者 hybrid？

**领域依据：** TMLR'26 P09 已明确区分 explicit/implicit WM，并把 training-cost、inference-cost、generalization trade-off 的 direct empirical comparison 留作 future direction；Bagatella TD-JEPA 是 ICLR'26 Oral 的 implicit anchor。

**最强 collision：** PLDM 已系统比较 latent planning vs HILP/GCIQL/HIQL/CRL/GCBC，在 data quality、trajectory length/stitching、dataset size、random-policy data、new task/layout和inference time下给 method-selection结论；planner amortization也早于2026。

**Exact delta：**
> 控制 data/task/compute后，找到能跨任务预测 **one-step explicit / arbitrary-horizon / successor occupancy / amortized / hybrid predictive object** 相对优势的 regime variables；explanatory variable必须是 predictive object，而不是再做 planning-vs-policy排行榜。

候选轴：reward/goal redefinition、unseen objective composition、layout/dynamics shift、horizon、data coverage、deployment search budget、**task/query information budget**、arbitrary-action counterfactual需求。

**Reviewer compression：**
- “apples-to-oranges benchmark”
- “只是一个训练更久、另一个test时search更多”
- “TD-MPC2已经 hybrid”

因此 E13 必须有 common data/task/utility，并分开 **training compute / task-query information / deployment compute**；还要加入至少一个中间 predictive object验证 continuum。没有 hold-out regime law不升级。

### M3 / I09 — Behavior trajectory semantics ≠ environment controllability

**Problem:** RC-aux / Temporal-Distance JEPA 这类 planning-aware supervision 从 behavior trajectory 的 gap/order/negatives 学 progress/reachability；这些 semantics 会不会继承 behavior policy 的 route/tempo，而不是 environment controllability？

**最强近邻：** QRL/multistep quasimetric、PLDM、CGCIVL 已占 broad “behavior statistics ≠ optimal control”；P94 已占 conditional action excitation→transition identifiability→planning；P95 IEL 已占 directed hitting-time regression + trajectory-label mismatch。

**Exact delta：**
> **在 conditional action excitation 与 one-step transition evidence 已匹配/控制后**，改变 higher-order trajectory organization / route gap，planning-aware visual latent WM 的 deployed metric/reachability 是否仍留下 behavior imprint，并改变 same fixed candidate pool / closed-loop MPC。最强实验是 transition-equivalent / trajectory-different control。

旧 I01/E03-E04不构成这个 intervention，因为它只改 long episode factorization而 short-window loss不可见。E14 才是有效 treatment。

**Reviewer compression：**
- “offline data distribution当然重要”
- “quasimetric已经研究suboptimal behavior”
- “只是coverage变了”
- **“P94已经证明 behavior-policy conditional action excitation 决定 counterfactual transition identifiability / planning。”**

所以 M3 只能在 conditional action excitation 与 local transition support已经匹配/控制后，研究 **higher-order temporal organization / route semantics 的额外 imprint**；若最终修复只是 IEL/QRL式 hitting-time / expectile / quasimetric移植，也不够。

所以必须匹配/量化 state-action/local-transition support，并证明 effect 在 planning-aware semantics 上 load-bearing。

### I06 — M3 的 subdiagnostic，不再自动做主论文

semantic negatives vs geometric regularization 仍是好 probe：
- E08 sampler semantic audit；
- E09 semantic/count/repulsion role decomposition；
- E10 conditional role separation。

但 P69 已进一步表明 negative construction本身可扭曲 planning geometry，所以“negative坏”更不够新。I06 只有在解释 M3 更大的 behavior→controllability failure 时才优先扩展。

### I03 — common bottleneck oracle

E06/E07 用于 M1–M3 的归因；只有少数observable variables能跨task预测 binding bottleneck与 intervention ranking时，才允许独立升级成 regime-law paper。

### M4 — Query/goal interface & model reuse（WATCH）

P38 *What Must a World Model Distinguish for Planning?* 已直接研究 query/candidate/planner-dependent sufficiency与 seen→unseen objective trade-off；Grounded WM 又占 language-semantic goal interface。当前只作为 transfer stress axis。

## 5. Idea 状态

| ID | 状态 | 角色 | 最大 compression |
|---|---|---|---|
| I07 observable goal ≠ control belief | **SEED / Tier-B conditional** | E11→conditional E12 | PVWM/FIRM/UWM/Branch + generic POMDP |
| I08 predictive-computation placement | **SEED / Tier-A2** | E13 matched regimes | PLDM + old amortization + apples-to-oranges |
| I09 behavior→controllability semantics | **SEED / Tier-A1** | E14→conditional E15 | P94 action excitation + P95 IEL + QRL/PLDM |
| I06 semantic negative roles | SEED / M3 subdiagnostic | E08→E09→E10 | false-negatives/negative-geometry已有大量先例 |
| I03 bottleneck regime | SEED / common diagnostic | E06→conditional E07 | component benchmark |
| I04 random→elite alignment | subordinate | E02 calibration | DA-LeWM / P38 |
| I01 trajectory-factorization | **PARKED** | historical invalid design | treatment对short-window objective不可见 |
| I02 optimizer support drift | **PARKED** | conditional diagnostic | P40 + offline MBRL |
| I05 generic history/POMDP | **SUPERSEDED by I07** | 不再做context-length sweep | FIRM/I-TAP/FloWM等 |

## 6. 反向 reviewer test

### I07
**“这不就是 POMDP 需要 memory 吗？”**  
只有在我们证明 image-goal interface 自身造成 **observable-goal / control-belief role mismatch**，且这种 mismatch 在现实 candidate decision上有 regime-dependent consequence，才超过 textbook claim。

**“FIRM-WM已经拆goal state和dynamic fiber。”**  
所以 factorization不是贡献。新的信息必须是 belief/aliasing何时 load-bearing、history何时不够，以及对 candidate decision 的稳定 law/repair。

### I08
**“PLDM早就做过 model-based planning vs goal-conditioned/model-free methods 的 regime study。”**  
所以必须把 explanatory variable压到 **predictive object**，并明确超过 PLDM 已经测过的 data quality/trajectory length/data size/OOD layout/inference time。

**“一个是MPC，一个是zero-shot policy，本来就不同。”**  
正因此不能只比较分数。必须用 common data/task/utility 和 compute ledger，把差异压成可解释的 predictive-computation placement trade-off，并预测未见 regime。

### I09
**“P94已经证明behavior policy action excitation决定counterfactual planning。”**  
所以先match/audit conditional action covariance / excitation。

**“IEL/QRL已经研究behavior hitting-time geometry。”**  
所以不能以hitting-time regression / expectile / triangle/quasimetric本身作贡献；必须证明 visual latent-WM planner里的 trajectory auxiliary 在 local identification已满足后仍引入 decision-level policy dependence。

**“换behavior policy当然换训练数据。”**  
必须控制/量化 local transition support与coverage，最好做 transition-equivalent / trajectory-different control，并落到candidate/closed-loop。

### I06
**“False negatives老问题。”**  
存在性不是贡献；semantic pair label与global regularization的角色分离才可能是贡献，而且现在只是M3子机制。

## 7. Stop rules

- **E11** 同观测不同hidden state基本不改变真实最优动作 → I07 park；
- **E11/E12** 简单短history稳定消除所有decision regret → 不做复杂belief方法；
- **E13** explicit/implicit差异只能由train/test compute解释，或没有跨task regime signature → I08不升级；
- **E14** effect被coverage/local-support完全解释 → I09不升级；
- **E14** learned semantics变化但candidate/closed-loop null → 不升级；
- **E08** contamination极低/不稳定 → I06 park；
- **E09** calibration变但decision null → I06不升级；
- **E06** 只能得到per-task post-hoc thresholds → I03保持diagnostic；
- 任何方法若只改善 internal probe、不改变Actionable consequence → 不作为 manuscript-critical contribution。

stop只停具体 lead，不自动关闭整个 territory。
