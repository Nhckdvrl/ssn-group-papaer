# Enemy Within: Long-term Motivation Effects of Deep Player Behavior Models for Dynamic Difficulty Adjustment

规范记录：`pfau_2020_enemy_within`；CHI 2020, Paper 296, pages 1–10; DOI verified。实际版本：Author accepted version with CHI 2020 typesetting。

**实际阅读范围：** Complete main text Introduction through Conclusion, PDF pages 1–8; architecture, sample sizes, Tables 1–4 and limitations

[原文](https://www.smeddinck.com/files/papers/EnemyWithin.pdf) · [发表／主源信息](https://doi.org/10.1145/3313831.3376423)

**稳定 ID：** `pfau_2020_enemy_within`。CHI 2020，Paper 296，DOI 10.1145/3313831.3376423；作者接受版 PDF。**实际阅读：** 完整主文 Introduction 至 Conclusion（PDF 1–8），状态接口、样本与表 1–4、明确局限；参考清单不算追读。

该文提供少见的真实游戏中期证据：在 Aion 私服上线 Eternal Challenge 四周，171 玩家进入 776 次；30 人自愿完成问卷。前半副本含启发式难度调节的不同敌人：刷新速度、血量、干扰技能随胜负变化；击败主敌后再遇到模仿自己的 DPBM 对手。DPBM 依三位资深玩家访谈设计状态特征，记录双方状态与近期技能，将过去各次战斗训练到小型 5×10 隐层 MLP，输出玩家技能分布；移动仍用规则、冷却/法力不合法动作由规则过滤。它捕捉技能轮转和情境应对，不是完整人物心智。

30 人反思问卷中，DPBM 兴趣享受均值6.17，相比三种 HPT 敌人4.00/4.04/4.78；努力重要性也较高，配对比较经 Bonferroni 校正。副本四周每日访问高于另35种副本，略去首周仍领先；少数开放回答自发提到敌人学了自己的连招、促使重新思考战术。技术上每入场训练平均约2秒，80/20数据划分动作预测平均约60.6%，但这不是未来局策略保真度或难度准确度的完整测试。

必须把生态效度与因果效度一起记录：HPT 和 DPBM 共处一个副本，外观、功能和出现顺序不同，没有随机只含一种机制的独立组；访问日志反映整个新副本，无法将留存提升独立归给 DPBM。问卷仅30名自选响应者，IMI原用于单次体验而这里回顾四周，作者明确提出需独立控制组复现。因此可信结论是“学习个人打法的敌人能带来可感知而受欢迎的变化，值得重视”，不能说已普遍证明深度模型提高长期留存。该方向关心的是玩家不断成长时对手怎样形成新的可理解挑战，其评价必须兼顾挑战、成就感与行为变化，而非只预测动作或维持胜率。

**主源：** https://www.smeddinck.com/files/papers/EnemyWithin.pdf ； https://doi.org/10.1145/3313831.3376423

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Adaptive Game AI with Dynamic Scripting](SPRONCK_2006_DYNAMIC_SCRIPTING.md) | 两者都研究难度适应；Enemy Within 提供人类动机与四周日志，但其镜像、属性调节和关卡效应并未被完全分离。 |
| [Learning to Move Like Professional Counter-Strike Players](DURST_2024_MLMOVE.md) | Enemy Within 观察真正游玩中的动机；MLMove 的明确人类证据主要来自盲评视频，实际人机游玩探索仍不确定。 |
| [Generating Personas for Games with Multimodal Adversarial Imitation Learning](MULTIGAIL_2023.md) | Enemy Within 拟合个体玩家技能习惯，MultiGAIL 的 persona 是预定义风格的可控组合，个人化和风格化不是同一问题。 |
