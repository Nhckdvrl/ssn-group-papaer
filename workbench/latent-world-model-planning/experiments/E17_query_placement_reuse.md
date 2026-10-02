# E17｜Selective Query Specialization：任务条件化与复用

- **状态：** PLANNED；未运行。
- **对应：** I10 / R3。
- **来源：** S18 + I10；这是第二波方法线，不阻塞E13/E16。
- **阳性对照：** query-agnostic COST-ONLY baseline；FULL-QUERY specialized reference；seen目标上query信息确实能被模型利用。
- **噪声地板：** 固定goal split、训练量、query信息与planner预算；seen/unseen目标严格分开，测试目标不参与调参。
- **决策表：** selective adapter改善seen且保留reuse→扩seed/task；cost-only已足够→保留简化结论；full-query无unseen损失→该任务无明显specialization tradeoff，换更异质目标或停此方法；所有差异由参数量解释→做capacity match。

## 核心问题

一个compact world model需要多少query/task specialization，才能既对当前目标更好，又保留跨目标复用？

## 第一轮任务设计

优先用已有可多goal评测的TwoRoom / OGBench Cube：

- **seen goals**：训练时出现的goal families / task IDs；
- **held-out goals**：同动力学下未参与训练的目标组合；
- 可选 **query shift**：同一state-action dynamics，换cost/goal定义而不换环境物理。

首轮不用自然语言；所有方法看到等价的goal/task信息。

## 方法矩阵

1. **COST-ONLY**：action-conditioned predictor完全query-agnostic，query只进入goal/cost。
2. **PROPOSAL-ONLY**：predictor不变，query用于candidate proposal/initialization。
3. **PRED-ADAPTER**：predictor末端轻量query adapter/residual。
4. **SELECTIVE-ADAPTER**：只对planner boundary candidates或高query-relevance latent tokens/channels调用adapter。
5. **FULL-QUERY**：query注入主predictor，作为强specialized reference。

第一轮2–3个最容易实现的版本即可；不是必须一次跑齐五个。

## Fairness

- query表示和维度对齐；
- total train steps / data相同；
- adapter额外参数单独报告；
- deployment compute单独报告；
- COST-ONLY不能偷偷拿更强goal encoder；
- FULL-QUERY若需更多task labels，单独计task information。

## 主读数

### Performance
- seen-goal success / task cost；
- held-out goal success；
- query shift后的zero-/few-shot性能。

### Reuse
- 不更新predictor时新goal适配成本；
- 只换cost/head与更新adapter的差距；
- old-goal retention。

### Specialization
- predictor output在不同query下变化量；
- candidate ordering变化；
- seen gain / unseen loss ratio；
- 额外params与wall-clock。

## 最小可投叙事的条件

至少要有一个**设计决定**被清楚支持，例如：

- query只放cost/proposal已足够，full query-conditioned predictor没有必要；
- 轻量selective adapter保留大部分seen gain，同时显著改善unseen reuse；
- specialization的收益只集中在long-horizon / ambiguous candidates，形成可解释使用规则。

“query-conditioned比baseline高”本身不够。

## 结果
未运行。
