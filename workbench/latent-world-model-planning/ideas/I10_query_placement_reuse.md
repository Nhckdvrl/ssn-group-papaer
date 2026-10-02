# I10｜Selective Query Specialization：任务对齐但不重写整个世界模型

- **状态：** SEED，未获得本地实验证据。
- **对应：** R3，见[研究计划](../RESEARCH_PLAN.md)。
- **来源：** S1任务无关预测、S4规划对齐、S18 query/candidate/planner sufficiency。
- **问题：** query/task information 应该进入哪一层，才能改善当前任务，又不让 predictive core 过度专门化、失去新目标复用？
- **实验入口：** E17。
- **研究边界：** “query conditioning有用”“模块化比联合模型更泛化”已有直接近邻；本seed不靠这些口号，而比较**selective query specialization**的具体接口与成本。

## 工作方法假设

保持一个 query-agnostic action-conditioned predictive core，只让query进入少量位置：

1. **COST-ONLY**：query只定义cost/goal embedding；
2. **PROPOSAL-ONLY**：query只影响candidate proposal / search initialization；
3. **PRED-ADAPTER**：predictor末端加轻量query residual/adapter；
4. **SELECTIVE-ADAPTER**：只对candidate boundary附近或高query-relevance latent channels启用adapter；
5. **FULL-QUERY**：query进入主predictor，作为强specialized reference。

第一轮不追语言。先用goal/task ID或同一goal-embedding信息，避免把VLM能力混进来。

## 想看到的科学对象

- seen-task gain 与 unseen-goal reuse 的trade-off；
- query specialization 是否真的需要进入dynamics，还是cost/proposal已足够；
- selective adapter 是否保留大部分seen收益，同时明显减少unseen degradation/额外compute；
- query information 放置是否与candidate difficulty / horizon相关。

如果FULL-QUERY在seen和unseen都最好，不强写“模块化必要”；转而分析为什么该task family没有specialization penalty。

## 与最近邻的距离

- **What Must a World Model Distinguish?** 已提出query决定planning sufficiency并主张模块化；我们若做，贡献必须落到可训练的轻量selective specialization、强baseline和跨目标实证，而不是重新陈述理论。
- **Grounded World Model** 已把language goal引入vision-language latent planning；我们首轮不把语言作为novelty来源。
- value-aware / goal-aware model learning是思想祖先；最终要证明的是modern compact latent planner中的实用设计增量。
