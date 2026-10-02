# I13 — Revaluation frontier: what must be recomputed when the world/task changes?

- **Program:** R2 — predictive abstraction
- **状态:** SEED
- **目的:** 从经典 model-based vs successor-representation 的 revaluation tension 出发，研究现代 latent world-model continuum 在 **reward/goal change vs transition/dynamics change vs query/planner change** 下的复用边界。

## Mother question

不同 predictive objects 把未来计算“缓存”在不同位置：

- explicit transition model：缓存 local dynamics，test-time重新 plan；
- arbitrary-horizon model：缓存多 horizon future；
- successor / occupancy model：缓存 policy-conditioned long-horizon visitation；
- amortized planner/policy：缓存更多 decision computation；
- hybrid：缓存一部分，同时保留短 rollout/search。

于是一个自然、重要的问题是：

> **环境/任务发生哪种变化时，哪些缓存仍然有效，哪些必须被重新计算或重新学习？**

这不是“谁SOTA”，而是 **what information is precomputed, and what kind of revaluation invalidates it?**

---

## Why this grows naturally from related work

### Classical anchor: successor representation
Successor representation / successor features本来就把 dynamics 与 reward 部分解耦：
- reward revaluation通常可以快速完成；
- transition revaluation会使 cached successor occupancy过时，除非有 replay/model更新。

这不是新发现，而是一个**经典 computational distinction**。

### Modern explicit side
LeWM / JEPA-WM / D-MPC等保留 action-conditioned predictive dynamics：
- 新 reward / goal可通过 test-time objective替换；
- D-MPC还展示过 novel reward optimization / dynamics adaptation；
- 但每次 deployment都要 rollout/search。

### Modern implicit / occupancy side
Bagatella TD-JEPA：
- reward-free offline learning后，可对新 reward做 zero-shot task inference；
- long-horizon policy dynamics被 amortize进 successor-like representation；
- 主论文重点是同 environment dynamics 下的 zero-shot reward/task adaptation，而不是 transition revaluation。

Jumpy WM：
- 更进一步缓存 pre-trained policies在多 timescale下的 occupancy；
- planning action变成 policy sequence。

Universal Horizon Model：
- 不完全是 successor，也不是recursive local model；
- 直接预测 arbitrary horizon future，提供一个中间 predictive object。

### Hybrid
TD-MPC2 / Dyna-SR式思路说明：
- local model + cached value/policy / occupancy可以组合；
- 理论上可能获得 fast task adaptation + dynamics-change flexibility。

---

## Exact scientific object

不是“reward shift vs dynamics shift performance table”。

真正想找的是一个 **recomputation law**：

[
	ext{predictive object}
	imes
	ext{change type}
	imes
	ext{change locality}
	imes
	ext{horizon}
ightarrow
	ext{how much must be recomputed / adapted?}
]

变化至少分：

1. **Reward/goal revaluation**
   - dynamics不变，只换 objective；
2. **Local transition revaluation**
   - 增加/移动障碍、friction、door connectivity、action effect局部变化；
3. **Global dynamics shift**
   - morphology / broad action scaling / contact law变化；
4. **Planner/query revaluation**
   - cost / risk / candidate interface变化。

局部 transition change尤其有价值：
- explicit local dynamics只需局部模型更新或直接观察新 transition；
- successor/occupancy cache可能需要把远处 predecessor 的 long-horizon predictions重算；
- 这与经典 SR transition-revaluation tension直接对应，但可以在 modern visual latent planning中形成新的 empirical law。

---

## Potential narrative

如果结果支持，论文可以讲：

> **World-model architectures differ by where they cache future computation.**
> This determines their revaluation behavior: reward changes can often reuse cached dynamics/occupancies, while localized transition changes invalidate different amounts of predictive structure. We identify a revaluation frontier across explicit, direct-horizon, successor, and hybrid models, and derive a hybrid update rule that recomputes only the predictive structure invalidated by the change.

这比“explicit更灵活、implicit更快”更具体，也更像一个新 principle。

---

## What would be surprising

不是 explicit 对 dynamics shift更好这种常识本身。

真正有价值的是例如：

- small **local** transition change导致 successor/occupancy method出现远距离 stale errors，而 explicit model只需局部 correction；
- arbitrary-horizon direct model在 reward revaluation和transition revaluation之间出现不同 failure profile；
- hybrid短 rollout + successor tail存在一个可预测 crossover horizon；
- transition-change locality / graph distance 能预测需要 recompute 的范围；
- task/query revaluation只需要换 metric/proposal，但 representation-conditioned methods需要重训；
- update cost / sample cost 与 decision quality形成稳定 frontier。

---

## Baselines / nearest neighbors

必须包含：
- Bagatella TD-JEPA；
- LeWM / JEPA-WM explicit；
- 一个 direct-horizon中间点：UHM 或 Jumpy WM（按环境匹配选）；
- 一个 hybrid：TD-MPC2-like / model+policy-value；
- classical SR/SF revaluation作为 conceptual anchor，不必硬迁移到pixels主表；
- D-MPC作为 reward/dynamics flexibility neighbor。

---

## First cheap test

优先 maze / topology：

1. offline training environment固定；
2. test-time先做 reward/goal revaluation；
3. 再做 **localized transition change**：
   - close/open one door；
   - move one wall/obstacle；
   - change one local action effect；
4. 给各方法相同 amount of post-change evidence：
   - 0 new transition；
   - small local update set；
   - larger update set；
5. 测：
   - immediate decision regret；
   - adaptation samples/gradient steps；
   - amount of representation / predictive object that changes；
   - distant-state policy/value/planning recovery；
   - deployment compute。

---

## Gate

- 只得到“reward shift容易、dynamics shift难” → 不够；
- 只有不同 native task interface造成差异 → 不够；
- 出现稳定的 **change locality × predictive object × recomputation cost** law → strong signal；
- second environment/task复现 → 可升级；
- law能导出 selective/hybrid recomputation method → 很强。

## Relation to I08

- **I08 / E13:** broad predictive-object frontier under different task/compute regimes；
- **I13 / E19:** 更聚焦的 **revaluation / change-type stress test**，用经典 theory帮助形成可解释 narrative。

如果 E19给出强 clean law，R2可围绕I13发展；I08退为 broader context。
