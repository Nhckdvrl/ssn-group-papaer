# CPOCL: A Narrative Planner Supporting Conflict

规范记录：`cpocl_2011`；AIIDE 7(1):97–102。实际版本：正式会议PDF，6页。

**实际阅读范围：** 全文pp.97–102；定义1–19、算法1、失恋例子与限制全部阅读

[原文](https://ojs.aaai.org/index.php/AIIDE/article/download/12428/12287/15956) · [发表／主源信息](https://ojs.aaai.org/index.php/AIIDE/article/view/12428)

**来源与范围：** 2011；AIIDE 7(1):97–102；正式会议PDF，6页。全文pp.97–102；定义1–19、算法1、失恋例子与限制全部阅读。[CPOCL: A Narrative Planner Supporting Conflict](https://ojs.aaai.org/index.php/AIIDE/article/download/12428/12287/15956)。阅读标记：new_full_read。

CPOCL把叙事冲突从剧情标签变成因果结构：一个角色的计划威胁另一个角色行动所需的条件。普通POCL会消除所有威胁；意图规划又要求每个动作属于某角色的目标计划，因而容易排除失败的追求。CPOCL保留失败分支，将部分步骤标为永不实际发生，只有会执行的步骤必须构成从初态到作者终态的因果有效序列。未执行步骤不能为真实执行步骤提供前提，却能解释角色原本为什么这样做。

原文主要证据是形式算法与一个三人婚姻竞争领域（五类动作）的逐步构造，没有大规模基准、运行时间表或新玩家实验。例子展示普通规划会让情敌主动送戒指，而要求所有愿望成功的IPOCL*无解；CPOCL保留失败求婚计划，让戒指丢失、另一人取得并结婚成为有解释的故事。这是表达能力证明，而非模型实测改善百分比。

论文主动承认它只允许冲突，不保证冲突精彩、必要或有特定结构；强行增加冲突反而可能伤害动机合理性。它也不决定失败后何时重规划、何时放弃目标。因此知识库应把“可解释的失败、对立计划与社会后果”视为叙事基础能力，同时保留作者知识建模和动态目标修订的独立问题，不能把所有角色未达目标都计为NPC错误。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Glaive: A State-Space Narrative Planner Supporting Intentionality and Conflict](GLAIVE_2014.md) | Glaive把意图与失败解释放进状态空间搜索并给有限任务计时实验。 |
| [Sabre: A Narrative Planner Supporting Intention and Deep Theory of Mind](SABRE_2021.md) | Sabre支持深层角色信念和数值效用，CPOCL的贡献主要是形式表示计划冲突。 |
| [Declarative Optimization-Based Drama Management in Interactive Fiction](DODM_2006.md) | DODM优化作者剧情质量并对玩家行动介入，CPOCL首先保证角色行动有意图解释。 |
