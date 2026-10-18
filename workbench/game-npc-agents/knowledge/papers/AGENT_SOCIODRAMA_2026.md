# Agent Sociodrama: Social-Dynamics-Guided Persona Recasting for LLM Agent Teams

规范记录：`sociodrama_2026`；arXiv preprint; no peer-reviewed venue verified。实际版本：2610.15788v1, 2026-10-11, 20 pages。

**实际阅读范围：** 完整正文 pp.1–10；限制、状态更新、指标、任务、recasting算法及完整逐轮/消融/人类协议附录 A–G pp.14–18；p.19全数值表核读，后续图版未逐张分析

[原文](https://arxiv.org/pdf/2610.15788v1) · [发表／主源信息](https://arxiv.org/abs/2610.15788v1)

**来源与范围：** 2026；arXiv preprint; no peer-reviewed venue verified；2610.15788v1, 2026-10-11, 20 pages。完整正文 pp.1–10；限制、状态更新、指标、任务、recasting算法及完整逐轮/消融/人类协议附录 A–G pp.14–18；p.19全数值表核读，后续图版未逐张分析。[Agent Sociodrama: Social-Dynamics-Guided Persona Recasting for LLM Agent Teams](https://arxiv.org/pdf/2610.15788v1)。阅读标记：first_full_body_after_existing_partial_card。

Agent Sociodrama把固定人物倾向、动态情绪及有方向的好感/关系类别/事件记忆接到后续发言。每轮先独立决定紧迫度、公开/私聊/沉默，再按紧迫度发言；GPT-4o统一更新情绪关系，步幅限±.3。五个设计情境×六模型×五次九轮，共150团队轨迹；1350轮和6750人轮是嵌套观测，不是独立社会环境。人评13人、25片段，关系/情绪κ仅.288/.184；共识子集21/17项，LLM命中16/15，不能以76.2%/88.2%宣称全社会效度。共享评者有76%关系上升倾向，人类约40%，同一评者不保证相对排序完全无偏。

TPR据每种配置12次轨迹诊断，从五种性格库重配最多3次再运行；四固定任务是学生会隐藏信息、NASA/海难物品排序、太阳能谈判。后者243种协议枚举Pareto真值，其他输出按规则计分，并非全由LLM主观打分。跨六模型均值改善，且和配同样重配流程的Sotopia/AgentVerse有对照；但无社会动态消融同时改成固定顺序、全公开沟通，不能孤立归因关系轨迹。最醒目GPT-5-mini从16.7到100%的学生会结果，静态消融初始即100%；团队画像不等于基础能力瓶颈。最终分用最后配置、不回滚最佳，且未见独立保留任务转移验证。

这是一项团队设计/社会模拟邻接工作。价值在动态关系可作为诊断信号，并把沟通配置连接规则结果；尚未证明以该机制改善人类玩家的长期NPC关系。重配改变角色后重开，和让同一角色在世界中经历变化属不同问题，不能仅凭少一个字段就说互不覆盖，也不能把团队任务优化等同完整社会NPC。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Beyond Static Persona Consistency: Dynamic Persona Coherence in LLM Role-Playing](DYNAMIC_PERSONA_COHERENCE_2026.md) | 都来自情绪/人格动态控制线；Sociodrama另维护有向关系并反复重选团队人格。 |
| [SOTOPIA: Interactive Evaluation for Social Intelligence in Language Agents](../../../../library/themes/game-npc-social/papers/SOTOPIA_2024.md) | 以Sotopia/AgentVerse作部分任务基线，但终局目标和团队重新选角协议不同。 |
| [HAMLET: A Hierarchical and Adaptive Multi-Agent Framework for Live Embodied Theatrics](HAMLET_2026.md) | HAMLET围绕剧情旗标编排表演，Sociodrama围绕团队终局分数重置选角。 |
