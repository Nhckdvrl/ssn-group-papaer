# Adaptive Game AI with Dynamic Scripting

规范记录：`spronck_2006_dynamic_scripting`；Machine Learning 63(3):217–248, 2006; institutional record verified。实际版本：Author-hosted manuscript, footer 2005-09-21; published 2006。

**实际阅读范围：** Complete main text §§1–7, PDF pages 1–40 and ending sentence page 41; algorithms 1–2, tables I–VI

[原文](https://ericpostma.nl/publications/Sproncketal2006.pdf) · [发表／主源信息](https://research.tilburguniversity.edu/en/publications/adaptive-game-ai-with-dynamic-scripting/)

**稳定 ID：** `spronck_2006_dynamic_scripting`。Machine Learning 63(3):217–248（2006）；所读作者公开稿页脚为 2005-09-21。**实际阅读：** 完整 §§1–7（PDF 1–40）及 41 页正文末句，算法 1–2、表 I–VI；不是只读摘要或 2004 年同谱系会议稿。

Dynamic scripting 从各职业的手工规则库按权重抽取战斗脚本，战后按团队胜负、个人存活等适应度调整实际触发规则权重，并重分配总权重。它把在线学习限制在开发者认为合理的行为组合内，保留默认规则兜底、可解释脚本和固定/自适应权重边界。作者提出速度、有效性、抗随机扰动、有限学习机会效率，以及清晰、多样、一致、难度伸缩八项开发约束。这些是当时作者结合行业沟通的设计框架，不是本文完成了每项玩家价值测量。

主实验在类似 Baldur’s Gate 的双队 CRPG 战斗：每队四角色，对手四基本脚本加三种切换组合；每种学习条件 100 次运行。滑窗连续占优的 turning point 平均 13–53 场，但个别达 480 场。用先验偏置规则权重可降至约 10–17 场；这依赖已有好规则，不能当任意玩法快速学习。与 Monte-Carlo 控制比较时后者仅用双方存活人数构成 16 状态，并有其他不同设计，结果不构成现代 RL 一般无效的证明。难度实验在 150 场中丢掉前 50 场适应期，以最后 100 场胜率检验约 50%；top culling 暂停最强规则，在八种脚本策略下均达到 45%–55%范围。

实际 Neverwinter Nights 自建战斗模块验证对原生 1.29/1.61 AI及扰动版的学习；三条件 50/31/21 次试验，平均 turning point 21/35/33；top culling 十次试验胜率由约79.4%至49.8%。这证明能嵌入真实引擎，不是随正式游戏发行的证据，也没有真人体验实验。作者特别建议难度调整允许关闭，因为强制势均力敌可能削弱成就感。领域价值是将学习、设计可控性、失误成本与难度目标一起考虑；未证明“胜负五五开最有趣”，也未解决新规则发现、罕见强策略、叙事人格或协作。

**主源：** https://ericpostma.nl/publications/Sproncketal2006.pdf ； https://research.tilburguniversity.edu/en/publications/adaptive-game-ai-with-dynamic-scripting/

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Enemy Within: Long-term Motivation Effects of Deep Player Behavior Models for Dynamic Difficulty Adjustment](PFAU_2020_ENEMY_WITHIN.md) | Dynamic scripting 以有界规则权重在线适应，并主要测试模拟战斗；Enemy Within 的复合 DDA 在真实社区进行四周玩家观察。 |
| [Learning to Move Like Professional Counter-Strike Players](DURST_2024_MLMOVE.md) | Dynamic scripting 用人工规则保证可读可约束，再改抽样权重；MLMove 用专家日志离线学移动，但仍保留规则瞄准开火。 |
| [Human-level performance in 3D multiplayer games with population-based reinforcement learning](JADERBERG_2019_QUAKE.md) | FTW 从大规模自博弈和元优化奖励学强对手；dynamic scripting 把受控在线速度与难度伸缩作为明确设计目标。 |
