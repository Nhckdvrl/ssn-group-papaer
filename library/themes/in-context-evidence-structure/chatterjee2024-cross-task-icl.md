# Language Models can Exploit Cross-Task In-context Learning（ACL 2024）`[主文§2–6，尤其§5；附录未全面核对]`

[官方论文](https://aclanthology.org/2024.acl-long.621/)。

1. **自然问题：** 缺少目标任务标签时，已有其它任务的样例能否帮忙？主文比较源/目标任务组合、混合少量目标样例与伪标签方法。
2. **idea来源（RECONSTRUCTED）：** 把跨任务转移变成prompt中的示例选择，而非参数微调；用任务相似性解释转移差异。
3. **证据与边界：** §5是hidden-state相似性与提升的相关，不是相关层已完成因果定位；§6明确观察到label-space复制。
4. **对E92：** “另一来源帮助当前任务”已有所有权。我们固定Input家族，用可枚举的来源关系与歧义区分直接跟随输出和可用criterion，继而检查whole-query禁读信息源时的历史功能。
5. **设计学习：** 强同任务baseline与错误类别同时分析；不要把内部相关峰直接写成信息在那一层开始传递。
