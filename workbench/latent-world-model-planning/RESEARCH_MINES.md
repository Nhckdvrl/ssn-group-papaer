# Research Mines — problem-led latent world-model planning (2026-10-02)

> 这不是 idea 榜单，也不是方法菜单。目标是找到 **ICLR / ICML / NeurIPS / CVPR 级母问题中仍有实验空间的 pressure region**，用大量受控实验让 observation / distinction / mechanism / method 自己长出来。
>
> 核心标准：世界模型的内部指标只有在影响 **prediction under intervention → candidate ranking/search → closed-loop behavior** 时才有科学重量。2026 survey “World Models for Embodied Intelligence: From Plausible to Controllable to Actionable”把这条线概括为 Plausible → Controllable → Actionable；本 workbench 以 **Actionable consequence** 作为 problem-mining gate，而不是靠新 probe 自我成立。

## 0. 为什么重新校准

前一版 workbench 很擅长把系统拆成 representation / dynamics / metric / search，但容易继续缩成“找一个细小 mismatch”。2026 的 latent-WM 文献已经证明，社区更关心的是：

- 什么 predictive state 才足够做决策；
- action intervention 是否真的改变 imagined future；
- offline data 里观察到的结构是否等于 environment controllability；
- planning 应该显式 rollout，还是把 long-horizon structure amortize 进 representation/policy；
- task/query 信息应该进入 dynamics、proposal、metric 的哪里；
- 在 partial observability / stochasticity 下，一个 point latent 是否还是正确的 planning object。

因此下面优先保留 **能改变模型/方法设计的真实问题**，而把 I06 这类较窄机制审计降成大问题中的探针。

---

# M1 — Observable goal ≠ control state: belief-aware visual planning

对应 idea: [I07](ideas/I07_observation_aliasing_belief_planning.md)

## Mother question

> **当两种真实状态产生相同/近似视觉观测，却要求不同动作时，reward-free image-goal latent planner 应该“离目标多近”地规划，还是应该维护“我现在到底处于哪种隐藏动力学状态”的 belief？**

这不是“context length 多几帧更好”，而是一个 state-definition 问题。

Image-goal planning天然有两个不同需求：

1. **goal-comparable state**：当前 observation 与 goal image 必须能比较；
2. **control-sufficient state**：还必须包含 velocity、contact mode、friction、occluded object state、latent regime 等决定 action consequence 的信息。

同一张 goal image通常不指定第二类信息。若模型用一个 deterministic point latent 同时承担两种角色，可能存在结构性冲突。

## 为什么不是空白猜测

直接近邻已经各做了一部分：

- **FIRM-WM (2609.22816)**：显式拆 goal-comparable configuration 与 history-dependent dynamic fiber，并加入 same-reset intervention branches；说明“goal state”和“dynamic state”角色冲突是真问题。它已经占了 generic factorization。
- **UWM-JEPA (2605.25313)**：把 partial observability 表述成 hidden futures 的 belief，并用 density-matrix latent；但主要证据是 hidden-velocity prediction/probe，未建立 image-goal MPC 的闭环决策问题。
- **Flow Equivariant World Models (ICML 2026)**：partial observability 下维护结构化 latent memory，重点是动态视频预测，不是 reward-free image-goal planning。
- **I-TAP (2602.18694)**：history-conditioned temporal abstractions + MCTS 处理 regime shift/POMDP，但属于 offline RL/token planning，不是 compact visual JEPA goal planner。
- **What Capable Agents Must Know (UAI 2026)**：理论上低 regret 在 POMDP 中迫使 predictive/belief-like memory；这是问题尺度锚点，不是我们的 empirical solution。
- VLA 邻域的 **IntentVLA / AliasBench** 也把 observation aliasing 当成真实控制 failure，而不是 probe artifact。

## Exact space

不能 claim：
- POMDP 很难；
- history 有用；
- 分开 goal latent 与 dynamic latent；
- belief state 是必要的。

值得挖的是：

> **在 compact reward-free visual world-model planning 中，什么时候 observation aliasing 从“prediction ambiguity”变成 action-selection regret？deterministic history state、typed state、stochastic/belief representation 分别在哪些 aliasing regime 够用？**

如果出现稳定 law，方法才从 law 长出来，例如：
- point state 足够：history resolves alias；
- history仍不能 resolve：需要 explicit uncertainty/multi-hypothesis belief；
- uncertainty本身不够：planner需要 risk/information-aware objective；
- goal-comparable 与 dynamics state 的耦合造成 metric contamination：需要 typed interface。

## 这条线为什么符合我们的资源

任务/模型可以很小；真正需要的是大量：
- hidden-state regimes；
- seeds；
- aliasing strength；
- observation history；
- candidate action pairs；
- simulator resets；
- planner variants。

全部天然 single-GPU / independent-run，且 simulator privileged state只作为 oracle。

## 不能退化成

“做一个 hidden-velocity probe，R² 下降了。”

最小可升级证据必须是：

```
same/near-identical observation
+ different hidden state
→ different optimal / low-regret action
→ deployed latent planner confuses them
→ one candidate representation/interface fixes the decision
→ closed-loop consequence
```

---

# M2 — Where should predictive structure live? Explicit rollout vs implicit predictive abstraction

对应 idea: [I08](ideas/I08_explicit_implicit_frontier.md)

## Mother question

> **对于 reward-free offline data，要把未来动力学保存在一个可 rollout 的 explicit model 里，还是把 long-horizon occupancy / policy-conditioned predictive structure amortize 进 representation/policy？什么时候哪一种更合适？**

这不是“比较两篇 paper 谁分高”。

TMLR 2026 **What Drives Success in Physical Planning with JEPA-WMs?** 已明确区分：

- **explicit WM**：action-conditioned autoregressive predictor；训练与具体 reward/task 解耦，test time 用 CEM/MPPI/GD 对任意 cost 做 counterfactual rollout；
- **implicit WM**：例如 Bagatella et al. **TD-JEPA**，把长时 predictive structure / successor features折入表示和 policy-conditioned predictor；训练更重，部署无需 search，但 reward/task受 learned feature span 等限制；
- **hybrid**：如 TD-MPC2，在 learned policy/value 与短 rollout/search 之间折中。

该论文直接把 **training cost / inference cost / generalization trade-off 的 empirical comparison** 留作 future direction。这里是明确的领域问题，不是我们凭空造的缝。

## 为什么现在值得做

2026 同时出现：
- compact explicit JEPA-WM：DINO-WM / PLDM / LeWM / JEPA-WMs；
- implicit long-horizon predictive representation：Bagatella TD-JEPA；
- search-amortization：GC-IDM / LeFlow / RP1 / INTACT；
- hierarchical/hybrid planning：HWM / SAGE / FF-JEPA / TD-MPC2。

领域正在从“有没有 world model”转向 **predictive computation 放在哪里**。

## Exact space

普通 leaderboard 没价值。真正目标是找 **regime boundary**：

- reward / goal **重定义** vs fixed objective；
- environment dynamics/layout shift；
- target horizon；
- offline data coverage；
- contact-richness / multimodality；
- train compute vs deployment compute；
- candidate search budget；
-需要任意 supplied action 的 counterfactual query，还是只需快速 zero-shot policy。

如果少数变量能预测 explicit / implicit / hybrid 的相对优势，并导出一个可验证的 hybrid allocation principle，才是论文。

## 工程约束

这是三条 mine 中接入成本最高的一条，因为 native training/evaluation contracts不同。第一轮：
- 不强行统一所有框架；
- 用共享 offline dataset / task definition / real env utility 做 **common audit layer**；
- native result与matched-audit result分开；
- training FLOPs/steps、test model calls、planner budget全部记账。

## 名称警告

本仓库已有 **Temporal-Distance JEPA (Bai & Xiong, 2607.25337)**，其历史 config 名也叫 `td_jepa`。  
这里的 **Bagatella TD-JEPA (2510.00739, ICLR 2026)** 是另一篇论文。所有记录必须写全名/作者。

---

# M3 — Dataset-induced planning semantics: behavior trajectories ≠ environment controllability

对应 idea: [I09](ideas/I09_behavior_to_controllability.md)

## Mother question

> **当 planning-aware latent WM 从 offline trajectory 的时间顺序、间隔和 cross-trajectory metadata 学“progress / reachability”时，它学到的是环境真正的 controllability，还是 behavior policy 恰好走过的路线？**

这是 RC-aux / Temporal-Distance JEPA 所在方向的更大问题。

## 已知边界

- RC-aux 自己明确：trajectory offset 是 empirical finite-budget proxy，不是真实 shortest hitting time；论文还给出 data coverage/competitive behavior 的限定。
- Temporal-Distance JEPA 从 same-trajectory step order/gap 挖 temporal progress，并使用 heuristic cross-trajectory negatives。
- Quasimetric GCRL（NeurIPS 2025）和 Multistep Quasimetric（ICLR 2026）已经明确：behavior future statistics 不天然等于 optimal goal distance。
- CGCIVL (ICML 2025)：trajectory identity 不能直接告诉你 connected/unconnected。
- PLDM (NeurIPS 2025)：offline data quality/diversity/stitching 会改变方法行为。

所以 broad claim “suboptimal behavior causes bias” 已经被占。新的 WM-specific 问题必须落到：

> **planning-aware WM 的 supervision 是否把 behavior-policy geometry 写进 deployed planning metric/representation，并在 test-time MPC 的 candidate ordering 和闭环控制中留下可重复的 imprint？**

## 关键修正：旧 I01 为什么 VOID，新 M3 为什么不是同一个实验

旧 I01/E03 只想“保持所有 loaded short windows不变、重新切 long episode”。代码审计发现 Temporal-Distance JEPA / RC-aux 的主要 loss只看 short clip，所以 treatment 对 loss不可见，正确 VOID。

M3 必须**真实改变 behavior policy / trajectory distribution**，让 objective 实际看到不同的 temporal pairs，例如：
- efficient/direct behavior；
- random/suboptimal behavior；
- looping/detour behavior；
- route-biased behavior；
- 同 environment dynamics 下的 mixed policies。

尽可能匹配 state-action/local-transition support，并显式量化无法匹配的部分。

## 可能长出的 idea

先不预设方法。若现象成立，可能出现：
- behavior path length 直接扭曲 metric，但 local dynamics没坏；
- negative semantics污染；
- route bias只在远目标/障碍环境出现；
- Bellman/local-consistency 类 objective 比 Monte-Carlo temporal gap 更 invariant；
- multi-route aggregation / interval supervision 比单条 observed path 更稳。

I06 **semantic negatives vs geometric regularization** 是 M3 的一个低成本 slice：它只审 cross-negative 的双重角色，不再作为整个 workbench 的第一主旨。

---

# M4 — Query / goal interface and model reuse（WATCH，不作为当前主矿）

## 为什么重要

- image goal 本身限制强；Grounded World Model (2604.11751) 已把 language-conditioned semantic goal带入 WM-MPC；
- What Must a World Model Distinguish for Planning? (2609.33030) 已 formalize mechanism/response/decision sufficiency，并显示 query-conditioned joint model在 seen objectives有优势，但泛化到 unseen objective 时优势缩小；其 modular solution让 query guide proposal，而 action-conditioned model保留 reusable outcome prediction。

因此“planning alignment 会不会牺牲 generality”是重要问题，但**已被非常直接地碰到**。

当前用法：
- 作为 M1–M3 的 transfer stress axis；
- 任何 planning-aware method都测 unseen goal/query/planner transfer；
- 不单独开“再测一个 alignment-generalization tradeoff”的 paper。

---

# 5. 2026 problem map：我们真正关心的问题，而不是 loss 名字

```
What should a compact world model know?
    ├─ fully observed → representation / controllability geometry
    └─ partially observed → predictive belief / hidden state                [M1]

Where should predictive computation happen?
    ├─ train explicit dynamics, search at test time
    ├─ amortize long-horizon structure into representation/policy            [M2]
    └─ hybrid

What does offline supervision actually identify?
    ├─ factual local transitions
    ├─ behavior-policy temporal statistics                                   [M3]
    ├─ counterfactual action effects
    └─ environment-level reachability / optimal controllability

How is the model consumed?
    ├─ goal/query
    ├─ candidate proposal
    ├─ ranking / verification
    ├─ temporal interface
    └─ closed-loop utility                                                    [common audit]
```

# 6. 从“问题”到“paper”的门槛

一个 mine 要升级，不看“probe 显著”，看是否形成：

1. **real failure / tension**：真实模型或主流训练目标在自然 regime 失败；
2. **load-bearing consequence**：影响 candidate decision / regret / closed-loop，而不是只影响 probe；
3. **new distinction or law**：不是已有 broad claim换名；
4. **controlled identification**：替代解释（data coverage、H/K、search budget、compute、history）被拆开；
5. **method follows diagnosis**：如果需要方法，它应是机制的最小自然后果；
6. **scope**：至少跨两个 task structures / model families，且最强近邻在公平协议下存在。

# 7. 执行优先级不是“先把一个题做到底”

第一轮按 **information gain / cost** 排：

- **E11**：M1 observation-aliasing decision oracle，先验证 problem 是否真的影响动作，不先训练新架构；
- **E14**：M3 behavior-policy intervention，先做小数据/一两个 objective；
- **E08**：I06 zero-training negative semantics audit，可与 M3 并行，作为其局部证据；
- **E13**：M2 explicit/implicit matched pilot，在 baseline substrate稳定后启动；
- E11/E14/E13 哪条出现最强的自然 failure + clean causal leverage，再把卡数集中到那条。

不要因为 I06 文档最详细就默认它是主论文。
