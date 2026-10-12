# LMs as Task-Specific Knowledge Bases: An Interpretability Analysis（2026-06-25 arXiv v1） `[证据级别：完整主文]`

[作者正文](https://arxiv.org/abs/2606.27237)。TAU/Google、Globerson/Geva；读主文§1–7全部及AppendixC、D1过滤/D4读数与D5说明、F方案/过滤/结果，其他附录长表/提示未逐项核对。33页PDF不代表全附录精读。NeurIPS初始名单精确题名未匹配，接收/评审未核对，不能写成已接收。

1. **形态/压力：** 数据库类比的可检验性质＋训练纵向行为＋必要/充分/特异因果子网。单一事实用不同任务取回应共享truth source，但已有paraphrase不一致、reversal curse和editing泛化失败。
2. **改变前提：** 不把知识视为与任务独立的参数存储；研究(fact,task)这个联合对象。不是多增加一种QA格式。
3. **idea来源：** DOCUMENTED：Petroni/Roberts KB比喻＋Codd/Abiteboul DB单一来源→跨任务co-emergence规范预测；Bayazit子网定位扩到特定任务。RECONSTRUCTED：用跨测量不一致生长出新对象，并以因果隔离和CoT的额外预测补强，而非只展示gap。
4. **实验：** OLMo3-7BIT 105checkpoint，五关系各46事实共230，六任务每10改写，candidate轮换，首正确token chance-normalized概率>.6，task有25%事实达到才算competent。1031可测试fact-task中47.9%未按预期共出现；.4/.8阈值近似。失败prerequisite失效的pair排除是作者限定的总体，不能当所有题漏学比例。
5. **机制：** OLMo2 7/13+Gemma2 9，共两族；五关系437targetfacts，baseline各任务阈值筛后、每模型各数据集去掉表现最差3/10prompt再5train/2eval。mask按随机task顺序强制互斥，优化nec+suff+spec+spar；subject用xx替换，清洁task激活patch恢复，副作用限制otherfacts/sametask及samefact/othertask。约2200 GPU·h/MI325X（256GB），不是轻量harness。
6. **结果与界限：** 示例officiallanguage OLMo7目标accuracy相对降29–89%，其它≤8%；恢复69–102%是lost-accuracy归一率，非原始accuracy。辨别task entanglement .21 vs生成.11；CoT恢复自身mask损失、依赖其它task组件更多，但cross取每fact最坏其它task。CoT先筛全task高准确事实，≥.99基线，不代表难题总体。
7. **解释强度：** 测到可隔离的功能计算，支持(fact,task)组织，但disjoint mask由训练约束而来，不能说自然唯一存储就是独立KB。co-emergence依赖其competence操作化，ANOVA零interaction分解比“共享事实＋不同访问器”假说更强；不能从交互直接排除所有共享状态。指标还允许top1前缀/3token substring等格式容差；std acrossfacts，不是多seedCI。
8. **对我们：** 跨用途任务gap/修复不迁移已有强ownership。我们的潜在距离是固定权重、同一自然源的增量角色修订中，目标文本的source-writing与后续消费可能相反，并产生未经询问关系的后果；不是改名字再说task-specific。借联合对象和“如果机制为真，CoT另一种损伤应改变”式预测，不能因此关闭语法/上下文修订领域。E66→E68对称路径是尚待判别的例子，E67角色全图未到不能讲源语义被破坏。
