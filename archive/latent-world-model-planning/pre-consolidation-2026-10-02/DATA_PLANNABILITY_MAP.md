# Data-Centric Plannability Map — What Data Makes a World Model Useful for Decisions?

更新：2026-10-02。  
这是 M3 的**母问题地图**，不是一个已经确定的论文题，也不是“找别人没做过的数据变量”。

> **核心问题：** world model 的数据不是单一的“多/少、好/坏”。不同数据属性可能决定完全不同的可规划能力。我们的目标是从已有局部规律中找出新的 capability–data relation、interaction、regime law 或数据选择原则。

---

## 0. Related work 是生长地图，不是封锁线

这个方向已经有很多强工作，正因为如此才说明母问题真实：

- ExORL：exploratory data本身可以改变offline learning结论；
- PLDM：data quality / size / trajectory length / random behavior / layout variation会改变latent planning与GCRL的相对优势；
- P94 Controlled-WM Identifiability：conditional action excitation决定 local controlled transition是否可识别；
- QRL / multistep quasimetric / CGCIVL：behavior future statistics、trajectory identity与optimal controllability不是一回事；
- RC-aux / Temporal-Distance JEPA：trajectory gap/order被直接写成planner-facing semantics；
- MIST-WM：主动probe task-relevant latent factors来收集 informative trajectories；
- FACT / VLAW：成功demo缺 failure/contact consequence coverage，真实 rollout可以补；
- Ego4WAM：human-robot alignment、duration、task diversity、action supervision、usage strategy影响不同 downstream capabilities；
- Scaling Laws for Agents/WMs：dataset size的最优 scaling系数会随 tokenizer / task / architecture改变。

这些论文**不是“已经把data做完了”**。恰恰相反，它们说明：

> **“data quality”不是一个标量；不同数据结构识别不同的模型能力。**

我们的工作空间在这些局部规律之间。

---

# 1. 六个数据轴 × 七种 plannability capability

## 数据轴

### D1 — State / observation coverage
数据看到了哪些区域、物体状态、视觉变化、contact modes。

代表：
- ExORL；
- PLDM；
- Ego4WAM task diversity / alignment。

### D2 — Conditional action excitation
在**相似 state 条件下**，actions是否有足够变化来区分 action effect。

代表：
- P94 Controlled-WM Identifiability；
- classic persistent excitation / system identification。

它回答：

> local action-conditioned transition 能不能被识别？

### D3 — Temporal / route organization
即使 one-step transitions类似，trajectory如何把它们组织成长路径：
- direct vs detour；
- loop frequency；
- route mixture；
- temporal gap；
- episode co-occurrence；
- long vs short trajectories。

代表：
- RC-aux；
- Bai/Xiong Temporal-Distance JEPA；
- QRL / multistep quasimetric；
- CGCIVL；
- PLDM trajectory length / stitching。

它回答：

> 数据里的 observed path statistics 会不会被当成 environment-level progress / reachability？

### D4 — Counterfactual / failure outcome coverage
模型有没有看到“坏动作发生什么”，而不只是成功demonstration。

代表：
- FACT；
- VLAW；
- Do-JEPA / FIRM-WM intervention branches。

它回答：

> candidate action 的失败后果是否被识别，而不是被 success prior 覆盖？

### D5 — Environment / task / query diversity
数据覆盖多少环境机制、布局、skills、goals、reward functions。

代表：
- PLDM layout variation；
- Ego4WAM；
- DINO-WM task-agnostic planning；
- WorldTest；
- ICLR 2022 procedural vs task generalization。

它回答：

> 一个 model 学的是 reusable physical dynamics，还是某组tasks的专用surrogate？

### D6 — Task-informed / decision-relevant probing
不是无差别增加coverage，而是专门采集**当前decision真正需要区分的因素**。

代表：
- MIST-WM；
- task-informed active system identification；
- VAML / PAML / value equivalence 的“model what matters”思想；
- P38 query/candidate/planner-dependent sufficiency。

它回答：

> 为了某个 query/candidate family，哪些data dimensions值得花预算？

---

## Capability columns

| Capability | D1 coverage | D2 action excitation | D3 route/time | D4 failure/cf | D5 task/env diversity | D6 task-informed |
|---|---|---|---|---|---|---|
| representation / state recovery | strong | indirect | weak–medium | medium | strong | **strong if task-specific** |
| local controlled transition | medium | **critical** | weak | strong | medium | strong |
| counterfactual action ranking | medium | **critical** | medium | **critical** | medium | **strong** |
| long-horizon rollout | medium | high | **high** | medium | medium | medium |
| reachability / progress semantics | medium | high | **critical** | medium | high | strong |
| planner optimization / candidate regret | medium | high | high | high | medium | **critical** |
| unseen-query / reusable reasoning | **high** | high | medium | high | **critical** | tension: specialization vs reuse |

这不是已证明矩阵；它是 **experiment-design map**。  
真正有价值的是发现表中哪些“看起来合理”的关系其实不成立，或者多个轴存在强 interaction。

---

# 2. 已有工作分别回答了什么，留下什么

## ExORL：data generation本身可以比换offline-RL算法更重要
它证明“algorithm固定，换exploratory data”就能大幅改变下游结果。

**它没有回答：**
- 对 latent world model，什么data property对应什么 predictive/planning capability；
- exploration coverage 和 candidate-decision requirement如何对应。

## PLDM：data regime可以改变 planning vs GCRL 的相对优势
它已经系统做了：
- size；
- quality；
- random behavior；
- trajectory length / stitching；
- unseen layout / tasks。

**它留下：**
- coarse dataset regime → performance；
- 但没有把数据性质压成 **identifiability / planner-facing capability** 的可迁移变量。

因此我们的目标不能是“再做一个PLDM表”，而是：
> data property → learned capability → decision consequence 的机制链。

## P94：behavior policy决定 local controlled dynamics是否可识别
这是很强的理论局部规律。

关键不是躲开它，而是继续问：

> **规划并不总需要 full transition identification。对一个给定 query/candidate family，到底需要哪些 action-effect directions 被excite？**

这直接长出 I10。

## P38：query/candidate/planner决定需要保留哪些 distinctions
P94从 data side问“什么能识别”；P38从 decision side问“什么必须保留”。

两者之间天然有一个桥：

```text
data support / excitation
        ↓
what dynamics can be identified
        ↓
query + candidate + planner
        ↓
what dynamics actually need to be identified
```

这不是 claim；是当前最值得用实验和理论去检验的 **mother tension**。

## MIST-WM / task-informed system identification
它们已经说明“主动收集 task-relevant informative data”是有价值的。

这不会杀 I10；它提供祖先：
- task-informed sysID关心 physical property estimation；
- MIST-WM关心 task-specific minimal latent factors；
- I10若成立，关心 modern latent-WM planning 中 **query/candidate-sensitive action-effect identifiability**。

## FACT / VLAW
它们说明 successful demonstrations 对 **bad-action consequences / contact failures** 有系统盲点。

这给 M3 第二个强 slice：
> 即使 state/action coverage看起来不错，**outcome polarity**（success/failure）本身是不是一个独立data axis？

未来若 E14/I10 没有信号，可从这里继续，而不是“整个M3被杀”。

## Ego4WAM / GE-Act 2.0 / scaling work
这些大模型研究告诉我们：
- duration不等于diversity；
- aligned data与broad video作用不同；
- skill-specific coverage能与zero-shot success显著相关；
- model/data scaling law受architecture/task影响。

对 compact workbench 的启发：
> 不跟它们比规模；用受控小模型把“哪一种数据为什么支持哪一种能力”做得更可识别。

---

# 3. 当前 M3 不再等于 I09

**M3 = Data-Centric Plannability**

母问题：

> **What data is sufficient for the decisions a world model must support?**

当前至少四个可实验子矿：

### M3-A / I09 — trajectory semantics
local transition证据相近时，route/time organization是否把behavior geometry写进planning semantics？

入口：E14。

### M3-B / I10 — decision-relevant excitation
full controlled transition可能要求global action excitation；但一个specific planner/query只需要某些action-effect directions。

入口：E16。

### M3-C — failure / counterfactual outcome coverage
success-only data是否让 compact latent WM 在bad-action candidate上系统过乐观？  
FACT/VLAW是强近邻，不从“failure data useful”开始；要找compact planner中 **哪种 failure coverage 对哪种 candidate decision必要**。

暂不单独注册 E##；等 E14/E16 或 baseline pain指向。

### M3-D — diversity vs specialization
environment/task diversity什么时候提升 reusable dynamics，什么时候稀释特定 decision 的data efficiency？

与 M4 / M2联动，不先开大矩阵。

---

# 4. I10 的核心新问题：global identifiability 可能比 decision需要的强

P94 的 `rho_tr(pi)=lambda_min(E Cov(a|s))` 关注 **所有 action directions** 的 controlled-transition identification。

但 P38告诉我们：
- decision requirement依 query；
- candidate set越粗，只需保留更少distinctions；
- planner search阶段与final selection阶段甚至需要不同信息。

因此一个自然 hypothesis family 是：

> **Data should be judged in the action-effect directions that can change the current planning decision, not only by global excitation / global prediction error.**

例如在2D action space：
- 两个 behavior datasets拥有**相同 action-covariance eigenvalues**，因此global `rho_tr`相同；
- 但高-variance主轴方向不同；
- query A 的 low-regret candidates主要在 x-action direction竞争；
- query B 主要在 y-direction竞争。

如果：
- dataset X → query A可靠、query B差；
- dataset Y → 反过来；
- global prediction MSE / global rho无法解释；
- projected decision-relevant excitation能解释；

这就是一个很干净的 new distinction。

**注意：** task-oriented system identification / VAML / PAML / MIST-WM 已经提供“只学task-relevant信息”的历史脉络。novelty不是这句话，而是：
- modern latent visual WM；
- behavior-data action excitation；
- planner query/candidate set；
- decision regret；
- 一个可测/可干预的 data-sufficiency quantity；
- 最后可能导出 trajectory selection / reweighting。

---

# 5. 什么结果可能长成方法

## 如果 I09 成立
可能是：
- censored / one-sided temporal supervision；
- multi-route aggregation；
- local Bellman/quasimetric consistency；
- semantics与representation regularization解耦。

## 如果 I10 成立
可能是：
- query-conditioned trajectory selection；
- candidate-sensitive replay reweighting；
- decision-relevant exploration；
- data curriculum优先补足 planner真正需要的action-effect directions；
- reusable base dataset + small query-specific data adapter。

## 如果 failure-coverage slice成立
可能是：
- success/failure balanced candidate data；
- targeted counterfactual branch collection；
- planner-selected hard-negative/failure rollout acquisition。

方法必须从最便宜的 positive result长出来，不提前选锤子。

---

# 6. 多 GPU 为什么特别适合这个 mother problem

这里最贵的不是单个模型，而是 **data regime × query family × task × seed × objective**。

我们可以把卡用于：
- 固定数据预算下多个data curricula；
- 相同architecture跨data regimes；
- query/candidate families；
- multiple train seeds；
- second environment；
- data selection / reweighting ablations。

每个job单GPU，天然 embarrassingly parallel。

这比用全部卡去同步训练一个大video WM更适合我们的infra。

---

# 7. 不能把“大问题”重新压成小残差

以下都**可以继续作为 broader paper 的一部分**：
- behavior path != optimal path；
- action excitation；
- false negatives；
- planner alignment；
- failure data；
- task-specific sufficiency。

“别人已经做过其中一项”只意味着：
- 这句话不能单独当贡献；
- 我们要说明它在新 distinction / interaction / regime / method 中扮演什么角色。

**不是意味着这块 territory 不能做。**

M3的目标不是找到一个无人碰过的数据bug，而是：
> **建立 modern latent-world-model planning 中 data → identifiability → planner capability 的新认识。**
