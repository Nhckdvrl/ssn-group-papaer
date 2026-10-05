# Do Language Models Know Who Did What to Whom?（Open Mind2026）[证据级别：部分正文]

[Primary全文](https://pmc.ncbi.nlm.nih.gov/articles/PMC13379307/)，Denning / Guo / Snefjella / Blank；2026-07-07，接受2026-05-22。实际读摘要、Introduction及Experiment1方法（94 base、active/passive/角色互换、模型和human judgments），Experiment2只读引言概述，结果详细图/附录未完整核对，未复现。

1. 形态：语言内部角色意义与句法形式的表征对照。
2. 压力：next-word训练是否产生角色表征，不能用语法正确代替who-did-what。
3. 前提：role意义应在控制句法/词面后影响表征组织。
4. 来源（DOCUMENTED）：语言与其他thinking系统的区别，角色赋值是语言理解核心而非任意常识测试。
5. 距离：反转agent/patient、主动被动与近义改写；该文已经owns宽泛role representation问题。
6. 方法：BERT/GPT2/Llama2/Persimmon，刻意排除RLHF模型；human similarity与内部representation/attention分析。
7. 边界：embedding相似度不反映角色强度不等于没有任何角色知识；正确prompt回答也不等于通用隐藏表征。本文probe/attention方法不在我们的执行范围。
8. 可迁移动作：明确研究的是实际role使用的哪些条件，并固定句法／词面控制；不要把直接取出名字当mechanism proof。
9. 对I01：增量应在**同一角色证据跨event/action/actor的带方向迁移与竞争解释**，不是首次证明懂／不懂角色、QA/hiddenstate差异或追加现代模型。
