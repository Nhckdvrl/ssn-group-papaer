# I08 — Where should predictive computation live?

- **状态：** SEED / **Tier A2 problem mine**
- **母问题：**

> Reward-free offline data可以被压成很多不同的 predictive objects：one-step action-conditioned dynamics、arbitrary-horizon future model、policy occupancy/successor features、amortized planner/policy、hybrid short-rollout model。**什么 regime 决定哪种 predictive object 最合适？**

这不是“explicit vs implicit谁SOTA”，而是 **predictive computation placement**。

---

## 1. 这个问题是领域自己留下的，不是我们造缝

TMLR 2026 **What Drives Success in Physical Planning with JEPA-WMs?** 明确区分：

### Explicit world model
\[
\hat z_{t+1}=P(z_t,a_t)
\]

- training 与 reward/task decouple；
- test-time可以 hard-code arbitrary action sequence；
- CEM/MPPI/GD优化任意 embedding-space cost；
- counterfactual trajectory generation灵活；
- 代价是 deployment search / recursive rollout。

论文还指出 compact JEPA-WMs 在简单模拟任务可以只需 thousands of gradient steps。

### Implicit predictive model
Bagatella **TD-JEPA**：

- policy-conditioned multi-step predictor；
- latent-predictive TD objective等价/关联 successor-measure approximation；
- 把 long-horizon occupancy structure amortize 到 representation / policy；
- training 约 1–2M gradient steps；
- test-time reward adaptation无需 iterative search；
- 但可优化的 reward受 learned feature span约束，也不能像 explicit model一样生成 arbitrary supplied-action counterfactual rollout。

### Hybrid
TD-MPC2：
- explicit dynamics + learned reward/policy；
- policy warm-start MPPI；
- 部分 search amortization。

该 TMLR 论文直接把 **explicit/implicit 的 training-cost、inference-cost、generalization trade-off 的 empirical comparison** 列为 future direction。

---

## 2. 2026 后续把二分变成 continuum

M2不能停在 explicit / implicit 两列。

### Direct arbitrary-horizon
**Universal Horizon Models (ICML 2026)**：
- 不递归 one-step；
- 直接预测任意 horizon future；
- 试图绕开 compounding error。

### Policy-level jump models
**Compositional Planning with Jumpy World Models (ICML 2026)**：
- 预测 pre-trained policy诱导的 multi-step occupancy；
- 多 timescale；
- planning action不再是 primitive action，而是 policy sequence。

### Amortized search
GC-IDM / LeFlow / RP1 等：
- 从 inverse action、generative path、learned optimizer角度把 search往training搬。

所以真正设计轴是：

\[
\boxed{\text{where is future computation stored?}}
\]

而不是“world model vs policy”。

---

## 3. 最大 collision：PLDM 已经做过“大类方法什么时候更好”

**P02 / PLDM (NeurIPS 2025)** 不是普通 baseline。它已经系统比较：
- latent-dynamics planning；
- HILP / GCIQL / HIQL / CRL / GCBC；
- random vs better behavior data；
- trajectory length / stitching；
- dataset size；
- unseen layout；
- new task；
- inference time / replanning interval；

并给出 practitioner-facing method-selection guidelines。

再加 **P96 (2021) planner amortization** 已经研究 MPC + learned proposal 与 planner-to-policy distillation。

所以 M2 绝不能只是：

> “系统比较 model-based planner 和 implicit/model-free policy，在不同 data quality / horizon / compute 下谁好。”

这会被直接压成 PLDM + old planner-amortization。

### M2 剩余 exact space

只能问更结构化的问题：

> **控制 data/task semantics 后，future information 被存成哪一种 predictive object，才决定某类 generalization / query / horizon / compute capability？**

即：
- one-step action-conditioned transition；
- direct arbitrary-horizon future；
- policy-conditioned successor occupancy；
- learned latent path / amortized planner；
- hybrid。

关键不是“policy vs model”，而是 **predictive object**。

要证明这一点，实验必须尽量避免：
- policy class差异；
- task-information差异；
- data-support差异；
- pure search-budget差异；

把 relative advantage压到 representation/predictive-object本身。

---

## 4. 为什么现在仍有空间

这些工作各自提出一个点，但没有给出一个 **regime map**：

\[
\text{task/query flexibility}
\times
\text{horizon}
\times
\text{data coverage}
\times
\text{dynamics shift}
\times
\text{train compute}
\times
\text{deployment compute}
\]

→ 哪种 predictive object是最合适的？

这正适合我们的多卡资源：
- 每个方法单卡；
- 数据/任务共享；
- 多 regime 独立；
- 可以快速做 hold-out prediction。

---

## 5. 最大难点不是算力，是公平性

Bagatella TD-JEPA 和 LeWM-style image-goal MPC **解决的 task specification 不完全一样**。

### Bagatella TD-JEPA official OGBench evaluation
代码审计：
- pixel OGBench：1M train steps，batch 256；
- evaluation对每个 task采约 10k replay states；
- OGBench relabel function使用 `physics` + action计算 task reward；
- model再从 `(next_obs, reward)` 做 reward inference，得到 task context。

### Explicit image-goal planner
通常：
- test-time直接给 goal image / observation；
- 不需要 10k reward-labeled states；
- 但要每个 control step做 CEM / rollout。

因此如果只比较 wall-clock：

> 不公平。

E13 必须拆：

\[
\boxed{\text{training compute}}
\]

\[
\boxed{\text{task/query information}}
\]

\[
\boxed{\text{deployment compute}}
\]

三本账。

---

## 6. 一个关键 fairness bridge：单 goal observation 能否直接实例化 TD-JEPA task latent？

官方 TD-JEPA **没有**用 goal image做主评测；它通过 reward inference 得到 task vector：

[
z_r
=
argmin_z
mathbb E_{(s,r)sim D_{m rwd}}
[(r-psi(s)^	op z)^2]
approx
C_psi^{-1}mathbb E[psi(s)r(s)].
]

但 pinned OGBench code还有一个重要事实：

- training 中 `sample_mixed_z(train_goal=psi_next_obs)` 会把真实 next-state embedding作为一部分 policy-task latent；
- 当 `scale_train_goals=True` 时，代码先做
  [
  z_g propto psi(g) C_psi^{-1}
  ]
  再 project/normalize；
- OGBench launcher默认打开 `scale_train_goals=True`。

对于理想的 point-goal reward (r_g(s)) 集中在 goal (g) 附近，reward-inference解近似也是 covariance-whitened (psi(g))（差一个 normalization / goal-neighborhood averaging）。

因此 E13 增加一个 **non-official but architecture-consistent diagnostic**：

### GOAL-Z bridge
给 TD-JEPA **一张 goal observation**：

1. encode (psi(g))；
2. 使用训练中相同的 covariance scaling；
3. project 到 z；
4. 直接 rollout policy (pi_{z_g})。

然后比较：
- GOAL-Z vs official reward-inferred (z_r) cosine / policy-action agreement；
- goal-reaching success；
- goal neighborhood大小的 sensitivity；
- single goal image vs multiple positive goal exemplars。

### 为什么它重要

若 GOAL-Z 已经工作：
- M2 可以构造更公平的 **same goal-observation information** 比较；
- explicit vs implicit 差异不再主要来自 task interface。

若 GOAL-Z 明显失败而 reward inference强：
- 这本身说明 implicit successor/task representation需要 **task distribution information**，不能把“single-pass deployment”写成免费的任务泛化；
- 但这仍只是 M2 fairness/result的一部分，不单独当 novelty。

**严禁写成“TD-JEPA官方支持goal-image inference”。** 这是由 paper reward-inference公式 + official training code推导出的实验桥，必须在 E13 里标作 exploratory/common-protocol variant。

---

## 7. 最有价值的 regime hypotheses

都只是 hypotheses，不是 claim。

### H1 — task redefinition favors explicit
同 dynamics，但 test objective频繁换：
- arbitrary visual goal；
- new reward；
- composite goal；
- unseen cost。

explicit model的 dynamics task-agnostic，可能更可复用。

### H2 — repeated fixed task + strict latency favors implicit
如果同一 task family长期重复：
- front-load training；
- amortized policy / successor structure；
- single-pass deployment可能占优。

### H3 — far horizon favors temporal abstraction
primitive explicit rollout可能：
- search dimension增大；
- recursive error积累。

direct arbitrary-horizon / jump model / successor abstraction可能更有效。

### H4 — counterfactual query favors explicit
如果 deployment要问：

> “给我这条**指定 action sequence**，未来会怎样？”

successor/policy-conditioned implicit representation不一定能回答。

### H5 — dynamics shift may favor models that can update local transition
但 AdaJEPA / ReDRAW / feedback WM已经让 adaptation很拥挤；这里只作为 regime variable，不单独 claim。

---

## 8. 什么样结果才够强

最理想是得到一个 **predictive frontier**：

例如：

\[
R = f(\text{task novelty},H,\text{deployment budget},\text{query info})
\]

能够在 hold-out task 上预测：
- explicit；
- direct-horizon；
- implicit；
- hybrid；

谁更合适。

这可以长成：
- empirical law；
- adaptive compute allocation；
- hybrid model；
- planner selection rule。

### 不够
- 一张 success-vs-time Pareto；
- TD-JEPA快，LeWM灵活；
- explicit在一个task赢；
- implicit在far horizon赢；
- 只用原论文不同输入/任务数字直接排名。

---

## 9. E13 最小进入方式

1. OGBench Cube pixels，双方 native reproduction；
2. common task utility；
3. **TD-JEPA GOAL-Z bridge diagnostic**：single goal observation vs official reward inference；
4. task/query information单独记账；
5. ID + task redefinition + near/far；
6. 只做两端：
   - explicit JEPA-WM / LeWM；
   - Bagatella TD-JEPA；
7. 出现稳定 ranking switch 后，才加一个中间 family：
   - Universal Horizon；
   - Jumpy WM；
   - 或 TD-MPC2。

没有 switch / regime relation就停，不把 benchmark包装成 paper。

---

## 10. Reviewer compression

### “PLDM已经告诉你 model-based planning / GCRL 各自什么时候好。”
这是当前最强 reviewer attack。回答不能是“我们换成更新模型”。必须证明 explanatory variable 是 **predictive object / compute placement**，而不是 PLDM 已测的 data quality、trajectory length、dataset size、OOD layout 等宏观 regime。

### “planner amortization 2021就做过。”
是。因此“把 search 搬到 training”不是贡献；需要 modern reward-free visual predictive-object frontier + hold-out predictive law。

### “这只是 train-vs-test compute trade-off。”
所以必须有 **generalization / task-interface / horizon** 维度，而且 hold-out regime可预测。

### “TD-JEPA与image-goal MPC根本不是同task。”
对，所以 E13不假装完全相同；用 task-information ledger把差异显式化。若无法定义公平 common question，M2应停。

### “TD-MPC2已经hybrid。”
Hybrid本身不是贡献。只有一个 **regime law 导出为何/何时 hybrid** 才可能有新意。

### “Jumpy/UHM已经解决长 horizon。”
它们分别定义特定 predictive object。M2问的是这些 objects 的 **selection boundary**。

---

## 11. 升级条件

I08 从 SEED → paper hypothesis：

1. native baselines复现；
2. common utility明确；
3. training / query-info / deployment budget全部记录；
4. 至少一个 regime variable导致 **relative ordering发生稳定变化**；
5. second task structure复现；
6. hold-out regime预测成立；
7. 加一个中间 predictive family后仍支持 continuum explanation。

若始终一个 family全胜：
- 先检查 compute/task-info；
- 若仍全胜，可转成“为什么强 baseline dominates”的问题；
- 不能硬画 frontier。
