# Interactive Narrative: An Intelligent Systems Approach

规范记录：`riedl_bulitko_2013`；AI Magazine 34(1):67–77。实际版本：作者公开的 in-press 稿，PDF13页，对应2013正式版本。

**实际阅读范围：** 全文PDF pp.1–13，包括全部正文§1–4与参考文献；图示文本可读，非系统性元分析

[原文](https://faculty.cc.gatech.edu/~riedl/pubs/aimag.pdf) · [发表／主源信息](https://onlinelibrary.wiley.com/doi/10.1609/aimag.v34i1.2449)

**来源与范围：** 2013；AI Magazine 34(1):67–77；作者公开的 in-press 稿，PDF13页，对应2013正式版本。全文PDF pp.1–13，包括全部正文§1–4与参考文献；图示文本可读，非系统性元分析。[Interactive Narrative: An Intelligent Systems Approach](https://faculty.cc.gatech.edu/~riedl/pubs/aimag.pdf)。阅读标记：new_full_read。

这篇综述以二十年交互叙事研究为对象，核心问题是玩家可改变事件走向时，系统如何保持可理解的因果结构与体验。它用三个独立维度整理领域：作者意图约束多强、角色离开剧情管理器后有多少自主性，以及是否学习个体玩家模型。这个区分防止把“拥有自主NPC”误当作唯一目标：模拟游戏可以接受涌现，教学或剧情体验则常需明确到达事件。

机制谱系从人工分支图，经过剧情点与先后约束、搜索/RL/案例管理，发展到根据动作领域理论在线生成后续情节。对玩家破坏原计划，文章区分干预阻止与接纳后重写，并指出两种做法各有作者意图和玩家能动性的代价。强故事与强自主性之间还有分层实现：管理器指定高层剧情，角色自主实现细节。

本文没有新的被试实验或统一榜单，不能从所列系统推断哪类更受玩家欢迎；它明确指出知识工程和非专家创作负担仍重要。领域价值在于给评测定坐标：连贯性、角色可信性、玩家影响力、作者可控性与个体适配并非同一分数。对当代LLM系统，也应分别说明谁拥有世界裁决权、谁能改剧情，以及角色行为能否让玩家理解其动机。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Declarative Optimization-Based Drama Management in Interactive Fiction](DODM_2006.md) | 把综述中的作者目标落实为对剧情点和管理动作的评价搜索。 |
| [Sabre: A Narrative Planner Supporting Intention and Deep Theory of Mind](SABRE_2021.md) | 聚焦人物意图与深层信念的形式规划，不是完整互动叙事综述。 |
| [HAMLET: A Hierarchical and Adaptive Multi-Agent Framework for Live Embodied Theatrics](../../../../workbench/game-npc-agents/knowledge/papers/HAMLET_2026.md) | 把蓝图、导演和在线演员重组为LLM框架，仍面对作者控制与角色自主权衡。 |
