# Sabre: A Narrative Planner Supporting Intention and Deep Theory of Mind

规范记录：`sabre_2021`；AIIDE 17(1):99–106。实际版本：正式会议PDF，8页。

**实际阅读范围：** 全文pp.99–106；形式定义、算法1、表1、消融与局限全部阅读

[原文](https://ojs.aaai.org/index.php/AIIDE/article/download/18896/18661/22662) · [发表／主源信息](https://ojs.aaai.org/index.php/AIIDE/article/view/18896)

**来源与范围：** 2021；AIIDE 17(1):99–106；正式会议PDF，8页。全文pp.99–106；形式定义、算法1、表1、消融与局限全部阅读。[Sabre: A Narrative Planner Supporting Intention and Deep Theory of Mind](https://ojs.aaai.org/index.php/AIIDE/article/download/18896/18661/22662)。阅读标记：new_full_read。

Sabre研究的不是自治聊天代理，而是全知中央规划器怎样在满足作者目标时，让各角色的动作对其自身效用与可能错误的信念也有解释。状态支持数值、ADL条件效果、观察触发器和任意嵌套信念；角色采取某动作须相信它能进入一个提高自身效用的非冗余计划，而且计划中其他角色的合作也要可解释。失败计划可以具有合理动机，正确结果不是唯一可信行为。

表1包含7个领域、17个实例：5个单实例领域、Lovers 10例中解出9例、Grandma 2例；表内Lovers统计仅9个成功实例。首次解耗时从1毫秒到Grandma平均6.2小时，BearBirdJr为14分钟。消融枚举到最短完整Sabre解的深度，比较只含意图或只含信念时多出的不合完整约束的计划。作者明确说这不是公平胜过其他规划器的实验，也没有本篇新玩家研究；相关人类偏好证据引用旧论文。

其重要贡献是把角色动机、错误知识、他人合作和剧情目标放到统一可执行语义里；但“深层心智”不等于不确定推理：角色必须选定信念，缺省还假定未声明的初始信念正确。领域动作、效用和触发器仍由作者编写，规模代价显著。它提供可检验的叙事约束思想，不证明开放自然语言NPC或真实玩家体验已解决。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [CPOCL: A Narrative Planner Supporting Conflict](CPOCL_2011.md) | CPOCL以非执行动作保留冲突中的人物计划；Sabre扩展数值状态和多层信念。 |
| [Glaive: A State-Space Narrative Planner Supporting Intentionality and Conflict](GLAIVE_2014.md) | 同属意图/失败计划谱系，Glaive强调状态空间启发式效率，Sabre提供更丰富语言与信念。 |
| [PsychSim: Modeling Theory of Mind with Decision-Theoretic Agents](PSYCHSIM_2005.md) | PsychSim是各角色基于不确定信念的决策模型，Sabre是全局作者视角叙事规划器。 |
