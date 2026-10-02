# I13｜环境或任务变化后，什么需要重学？

- **状态：** SEED，未获得本地实验证据。
- **对应：** R2，兼 R3/R5；见[研究计划](../RESEARCH_PLAN.md)。
- **来源：** 整理期间新提交的原I13/E19；successor representation的经典revaluation问题和S5长期预测结构。
- **问题与方法：** 区分只换goal/reward、局部门/障碍/动作后果变化、query/planner变化。比较模型/长期头/策略的复用与更新；可试局部更新、replay、短模型加长期缓存。
- **实验入口：** [E19](../experiments/E19_revaluation_frontier.md)。
- **研究边界：** 经典reward/transition revaluation差别不是新发现；局部物理变化不保证神经网络更新也局部。不给方法额外隐藏信息；不要求先找到普适recomputation law才允许试新设计。

与I08互补：I08关注预测结构与预算，I13关注变化后的更新/复用。可以合并成一个有效方法或重要解释，不预先承诺两篇论文。
