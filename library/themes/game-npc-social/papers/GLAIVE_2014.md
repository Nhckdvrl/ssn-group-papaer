# Glaive: A State-Space Narrative Planner Supporting Intentionality and Conflict

规范记录：`glaive_2014`；AIIDE 10(1):80–86。实际版本：正式会议PDF，7页。

**实际阅读范围：** 全文pp.80–86；算法1、意图路径/可能世界/启发式定义与表1全部阅读

[原文](https://ojs.aaai.org/index.php/AIIDE/article/download/12712/12560/16229) · [发表／主源信息](https://ojs.aaai.org/index.php/AIIDE/article/view/12712)

**来源与范围：** 2014；AIIDE 10(1):80–86；正式会议PDF，7页。全文pp.80–86；算法1、意图路径/可能世界/启发式定义与表1全部阅读。[Glaive: A State-Space Narrative Planner Supporting Intentionality and Conflict](https://ojs.aaai.org/index.php/AIIDE/article/download/12712/12560/16229)。阅读标记：new_full_read。

Glaive处理由作者统一协调、但每个角色必须有自身行动理由的叙事。它把快速前向状态搜索与因果历史结合：某个步骤只要在一个可能后续中能合理服务于角色目标，就可以解释另一条最终导致该目标失败的分支。因而协作不等于所有人共享作者目标，冲突也不必是反派无故捣乱。意图目标图用于提前排除不可能获得动机的动作，启发式取作者目标距离与未解释动作成本的最大值。

表1的独立单位为8个固定叙事规划问题，时间平均10次重复；6GB内存、3.5GHz i7。完整启发式解出6/8，改为普通Fast-Forward启发式解出4/8；前者5个问题低于1秒、Western约28.41秒，BLP-Die与Heist均未解。这里“FF”是同一Glaive框架换启发式，不是随意规划器或现代LLM。Aladdin对旧IPOCL的12小时到64毫秒比较跨论文/实现，不能冒充严格同环境随机对照。

它证明显式叙事约束未必只带来额外成本，适当搜索结构可以同时缩小无意义方案空间；但仅有8个领域实例，无本篇玩家研究，也不处理自由语言、不确定信念或真实引擎感知。两条失败案例提醒，规划器具备形式能力与达到交互延迟是不同评测层次。代码和领域在作者站公开的说明是可追踪入口，本轮未运行。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [CPOCL: A Narrative Planner Supporting Conflict](CPOCL_2011.md) | 延续可失败但有动机计划，主要推进搜索组织与启发式。 |
| [Sabre: A Narrative Planner Supporting Intention and Deep Theory of Mind](SABRE_2021.md) | Sabre扩大规划表示至深层信念和数值条件，其效率不能直接同跨论文旧时间比较。 |
| [Declarative Optimization-Based Drama Management in Interactive Fiction](DODM_2006.md) | Glaive搜索人物行动计划，DODM搜索管理者干预而把玩家策略作为环境。 |
