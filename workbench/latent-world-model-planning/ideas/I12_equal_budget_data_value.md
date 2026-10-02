# I12｜Planner-Boundary Branching (PBB)：有限预算的数据价值

- **状态：** SEED，未获得本地实验证据。
- **对应：** R1，见[研究计划](../RESEARCH_PLAN.md) H-A。
- **来源：** S2/S4的数据与经验reachability；S10主动采集；S11 candidate-selection opportunity；S12 policy-aware model learning。
- **问题：** 在相同simulator/reset/transition预算下，是否应该优先收集**会改变planner候选选择**的same-state counterfactual branches，而不是随机/IID、纯coverage或全局prediction-uncertainty数据？
- **实验入口：** E16。
- **边界：** “active data有用”“same-state branches有用”“candidate ranking重要”均已有近邻；本seed的潜在增量是把采集价值直接定义在latent MPC的selection boundary，并验证每条新增transition对closed-loop planning的收益。

## 工作方法假设

从CEM/iCEM已有candidate batch中计算query前可用的cheap score：
- selection relevance：top候选或elite cutoff附近；
- rank instability：bootstrap/ensemble heads、augmentation或轻扰动下candidate相对次序是否不稳定；
- predicted consequence span：竞争candidate的预测后果是否足够不同。

第一版可用乘积/归一加权，不先发明复杂网络。选中state后，restore同一simulator state，执行2–K条竞争candidate prefix，获取真实branch transitions。**先只把这些数据加回原LeWM/RC-aux训练目标**，把“数据在哪里采”与“新loss”分开。

只有data-only信号成立后，才考虑pairwise/ordinal supervision；此时D-JEPA/AD-WM必须作为直接近邻/基线。

## 预期能长出的story

若成立：有限数据最有价值的位置不是平均预测误差最大的区域，而可能是planner即将作选择、且模型对候选相对后果不确定的位置。方法可以自然发展为planner-aware active world-model learning。

若不成立：比较会告诉我们coverage、global uncertainty、failure data或action excitation哪个更有效，从而回到R1继续发展数据策略；不把seed失败等同R1失败。


## 最近邻如何变成我们的起点

- **FIRM-WM**已经证明common-reset intervention branches可用于reward-free visual planning；PBB研究的是**branch budget allocation**，不是再次证明branch data有用。
- **OnlineWM / ToIA / Task-Sufficient WM**把active data对准model weakness或task-relevant information；PBB把acquisition value定义在**CEM candidate selection boundary**。
- **SPARK**在LLM-agent rollout里也按critical decision states branching；这说明critical branching是跨领域原理，不能当headline novelty。PBB的对象是learned visual dynamics data与planner-selected competing actions。
- **D-JEPA / AD-WM**直接改decision/action discrimination loss；PBB第一版保持loss不变，只决定真实world-model experience采在哪里。

因此最干净的第一claim若成立会是：在同样新增环境steps下，selection-boundary branches比global uncertainty/coverage/random branches更有效地降低candidate regret并提高closed-loop success。
