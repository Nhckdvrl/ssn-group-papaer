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

## 4. Program-level positioning：近邻定义坐标，不定义禁区

以下 R1–R5 都是**社区已经持续发表、但认识仍未闭合的 research programs**。  
本表只规定：
- 哪些 atomic claims 不能重复当 headline；
- 哪些强 baseline必须比较；
- 我们如何继续生长 novelty。

不是为了把 program 压成“最后剩一毫米空白”。

---

### R1 — Data & Identifiability

**母问题：** 什么 experience 让 world model 学到可用于 counterfactual planning 的 dynamics / controllability？

**已有重要答案：**
- PLDM：data quality/diversity/trajectory structure影响 planning；
- P94：conditional action excitation控制 transition identifiability；
- QRL / IEL：behavior-time geometry与 optimal controllability要区分；
- RC-aux / Temporal-Distance JEPA：trajectory-derived planning supervision；
- Do-JEPA / FIRM：same-reset intervention branches；
- Task-Sufficient WM：active probing + structured representation。

这些结果构成一个**活跃 program**。

**不能单独 claim：**
- data distribution matters；
- action coverage matters；
- behavior gap不等于 shortest path；
- intervention data有用；
- active probing有用。

**仍然可以形成 novelty：**
- 不同 experience types 的**边际 planning value / regime law**；
- excitation与route diversity的 interaction；
- passive→counterfactual→active probing 的 sample-efficiency frontier；
- failure/recovery data的特殊价值；
- query-aware vs general-purpose data collection；
- trajectory supervision 的新 identification failure；
- 由 data principle 推出的 sampler / active collection method。

**当前 seeds：**
- I09/E14；
- I12/E16；
- I06/E08–E10（subdiagnostic）。

**Reviewer test：**
> “P94 / PLDM / Task-Sufficient WM 都做过 data。”  
回答不能是“我们变量不同”；必须是我们发现了**新的 data role / interaction / boundary / method principle**，并落到 counterfactual candidate / closed-loop。

---

### R2 — Predictive Abstraction

**母问题：** 什么 future object 是 planning 的最小充分预测对象？

**已有设计点：**
LeWM/SALT、Fast/VLWM、Flow/Branch、Universal Horizon、Bagatella TD-JEPA、Jumpy WM、HWM、LeFlow/RP1、TD-MPC2-like hybrid。

**不能单独 claim：**
- one-step有compounding error；
- longer horizon有用；
- successor representation高效；
- hierarchy有用；
- planner amortization省test compute。

**仍然可以形成 novelty：**
- predictive object 的 regime law；
- horizon/query flexibility/stochasticity决定 object choice；
- explicit + occupancy / distribution 的 hybrid；
- adaptive predictive horizon；
- training/test compute placement principle；
- new query/generalization boundary。

**当前 seed：**
I08/E13。

**Reviewer test：**
> “PLDM已经比较 planning vs GCRL；2021 planner amortization也做过。”  
因此新结果必须把 explanatory object放在 **predictive representation / future object 本身**，而不是重复 algorithm-family winner table。

---

### R3 — Specialization vs Reuse

**母问题：** 一个 world model 应该为当前 query/planner 专门化到什么程度，才能兼顾 decision efficiency 与 reusable world knowledge？

**已有答案：**
Value Equivalence、Goal-Aware Prediction、Objective Mismatch、P38、Rank-One Corner、Task-Sufficient WM、Action-Sufficient Goal Reps、WorldTest、Grounded WM、Physically Viable WM。

**不能单独 claim：**
- task-aware model可以忽略无关信息；
- query-conditioning seen objective更强；
- over-specialization可能伤 unseen query。

**仍然可以形成 novelty：**
- **query placement law**：encoder/dynamics/metric/proposal/verifier；
- query dimensionality × capacity frontier；
- seen↔unseen planner / objective transfer；
- selective/module conditioning；
- multi-query representation allocation；
- query-conditioned data acquisition与 reusable dynamics 的组合。

**当前 seed：**
I10/E17。

**Reviewer test：**
> “P38已经研究 query placement。”  
P38 是最强 anchor；我们若只是复现它就停 seed。但 R3 可以继续沿 capacity、multi-query、visual WM、query-aware data、planner changes 等方向长。**不是把 R3缩成一个没被P38提到的变量，而是找新的 law/interaction。**

---

### R4 — State / Belief / Information Gathering

**母问题：** partial observation / hidden physics / stochastic future 下，planner需要什么 internal state，并何时必须主动获取信息？

**已有答案：**
FIRM、UWM-JEPA、Branch-JEPA、Flow Equivariant WM、Physically Viable WM、I-TAP、POMDP/predictive-state theory。

**不能单独 claim：**
- history有用；
- hidden physics存在；
- belief比point state丰富；
- multimodal future需要多个branches。

**仍然可以形成 novelty：**
- history-resolvable vs active-information-required boundary；
- epistemic vs aleatoric ambiguity对应不同 planning strategy；
- belief如何进入 cost/search而非只提升prediction；
- goal-comparable state × dynamic belief interface；
- active experiment design for hidden physics；
- uncertainty representation与risk/information-seeking planner的 co-design。

**当前 seed：**
I07/E11。

**Reviewer test：**
> “POMDP当然需要belief。”  
顶会 story不能停在这句。需要一个自然 decision failure / regime law / active information method。

---

### R5 — Trust / Repair / Bypass

**母问题：** learned WM 在不同 state/action/horizon/shift 下可靠性不同，planner应如何选择 recovery action？

**已有 recovery mechanisms：**
- uncertainty penalty；
- support/exploitability diagnostics；
- MEND correction；
- IMWM intuition hybrid；
- AdaJEPA / residual adaptation；
- Feedback WM；
- AdaReP dynamic replanning；
- subgoal/horizon shortening；
- failure detection。

**不能单独 claim：**
- uncertainty能检测风险；
- online adaptation有用；
- feedback有用；
- replanning更频繁可减少error。

**仍然可以形成 novelty：**
- failure type → best repair action；
- reliability signal → intervention ranking；
- adaptive compute/horizon/replanning law；
- detect→repair unified policy；
- when to adapt model vs bypass model；
- confidence calibration specifically for **action-selection utility**。

**当前 seed：**
I11/E18。

**Reviewer test：**
> “不就是把已有recovery methods做router？”  
若只是heuristic router，确实弱。需要先发现一个稳定 failure taxonomy / intervention-ranking structure，method再从它长出来。

---

## 5. 当前 seed portfolio

| ID | Parent | 状态 | Pilot | Seed 被吸收后 |
|---|---|---|---|---|
| I09 | R1 | SEED | E14 | 回R1，转I12/active/counterfactual data |
| I12 | R1 | SEED | E16 | 回R1，换 data role / acquisition problem |
| I08 | R2 | SEED | E13 | 回R2，换 predictive-object axis |
| I10 | R3 | SEED | E17 | 回R3，换 query/capacity/data interaction |
| I07 | R4 | SEED | E11 | 回R4，转 active sensing / belief consumption |
| I11 | R5 | SEED | E18 | 回R5，收敛到最强 recovery boundary |

I03 / I06 / I04 默认是 scientific instruments / subdiagnostics，不占 parent program 名额。

---

## 6. Reviewer compression 的正确时机

### Seed 阶段
compression 用来：
- 加强 baseline；
- 明确 alternative explanation；
- 设计更有区分力的 pilot。

**不用于桌面关闭 parent program。**

### PROMISING / CLAIM 阶段
当已有 L1/L2 evidence 后，再问：
> 最坏审稿人会压成哪个 nearest paper？

此时我们已经有 observation，可以通过：
- boundary；
- mechanism；
- stronger baseline；
- additional regime；
- method；
来建立实际 delta。

没有实验时不停做 reviewer-compression，只会把题压成没人关心的小点。

---

## 7. Stop rules：只停 seed，program 由人审暂停

### Seed-level stop
- phenomenon不存在；
- tool positive control失败；
- effect只在probe不在decision；
- exact atomic claim已经被更完整工作覆盖且当前没有new evidence；
- simple baseline完全吸收。

→ 记录结果，PARK seed，**回 R#**。

### Program-level pause
只有满足 workbench 总章程：
- baseline/assets已建立；
- 有系统measurement；
- 至少多个不同 seed真的跑过；
- positioning完成；
- 人类判断 scientific yield低；

才允许暂停 R# / workbench。

“相关论文太多”不是 pause condition。

---

## 8. Novelty synthesis loop

每次 seed有结果后，本地 agent 做：

\`\`\`text
Observation
  ↓
Which R# mother problem does it change?
  ↓
Nearest 3–5 papers: what exact assumption/result differs?
  ↓
Try at least two:
  boundary / interaction / mechanism / unification /
  method / data law / compute law / transfer
  ↓
New seed or claim
\`\`\`

这才是“从 related work 中长 idea”，而不是从 related work 中不断删空间。
