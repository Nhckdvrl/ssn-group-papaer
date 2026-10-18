# Cooperate or Collapse: Emergence of Sustainable Cooperation in a Society of LLM Agents

规范记录：`govsim_2024`；Advances in Neural Information Processing Systems 37, NeurIPS 2024 Main Conference。实际版本：arXiv 2404.16698v4, 2024-12-08, 45 pages。

**实际阅读范围：** 完整正文 pp.1–10；完整机制/提示/运行协议与主消融附录 B–E pp.16–32；全部子技能定义/提示 pp.32–35；附录曲线与会务checklist未逐项读

[原文](https://arxiv.org/pdf/2404.16698v4) · [发表／主源信息](https://proceedings.neurips.cc/paper_files/paper/2024/hash/ca9567d8ef6b2ea2da0d7eed57b933ee-Abstract-Conference.html)

**来源与范围：** 2024；NeurIPS 2024；arXiv 2404.16698v4, 2024-12-08, 45 pages。完整正文 pp.1–10；完整机制/提示/运行协议与主消融附录 B–E pp.16–32；全部子技能定义/提示 pp.32–35；附录曲线与会务checklist未逐项读。[Cooperate or Collapse: Emergence of Sustainable Cooperation in a Society of LLM Agents](https://arxiv.org/pdf/2404.16698v4)。阅读标记：new_full_read。

GovSim让五名代理逐月私下选择开采量、同步执行后公开结果并自由沟通；真实规则使剩余资源加倍、低于阈值崩溃。鱼、牧草和污染三个叙事共享同一数学动力学，不能算三种独立经济结构。每模型/场景5次、12月，指标分开存活、收益、效率、平等和过度开采；记忆/反思/沟通架构与2024年开闭源模型一起比较。它把制度形成连接到可追踪资源后果，优于只问代理愿不愿合作，但没有真实玩家实验。

正文摘要最佳53.3%存活是默认条件：GPT-4o鱼场已经5/5，草场1/5、污染2/5。加入明确“如果人人超过F将令资源下降”的记忆后，附录表8/10/12的GPT-4o三个场景均5/5，Qwen-110B也全部存活；这同时给予关键数值阈值和后果，不是仅有抽象道德口号。故该文不能证明强模型在合理支架下仍普遍不会合作。移入贪婪新人降低默认模型总体存活，但新人任务还改变自利目标。沟通消融增加过度开采，附录报告总体存活时间差未显著，且各模型/情境效果不同；“必须沟通才能存活”过强。子技能相关性不是因果分解，三情境同构与小种子数限制外推。

领域位置是公共资源、群体规范与政策扰动的邻接环境：群体成功不能只看单人任务分数，稳定与公平也可能冲突。其有效待研究尺度包括异质利益、资源冲击、规则例外、执法及人类参与；本研究尚未检验这些扩展。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Emergent social conventions and collective bias in LLM populations](NORMS_2025.md) | GovSim有资源再生和私利冲突，命名游戏研究无实质利益冲突的约定收敛。 |
| [The AI Economist: Optimal Economic Policy Design via Two-level Deep Reinforcement Learning](AI_ECONOMIST_2021.md) | AI Economist学习可执行税制来改变激励，GovSim主要由语言协商形成资源规范。 |
| [Empowering Economic Simulation for Massively Multiplayer Online Games through Generative Agent-Based Modeling](../../../../workbench/game-npc-agents/knowledge/papers/MMOAGENT_KDD2025.md) | MMOAgent生产交易与充值经济更具体，但没有同等系统的资源崩溃/规范强基线分析。 |
