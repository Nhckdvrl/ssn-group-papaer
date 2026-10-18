# “Other-Play” for Zero-Shot Coordination

规范记录：`hu_2020_other_play`；ICML 2020; PMLR 119:4399-4410。实际版本：official PMLR PDF。

**实际阅读范围：** Complete main text sections 1-8, PDF pages 1-9; negative-results appendix not systematically read

[原文](https://proceedings.mlr.press/v119/hu20a/hu20a.pdf) · [发表／主源信息](https://proceedings.mlr.press/v119/hu20a.html)

**来源与范围。** [ICML 2020 正式论文](https://proceedings.mlr.press/v119/hu20a.html)，PMLR 119:4399–4410；正式 PDF 主文 §§1–8 完整阅读，未系统核读负结果附录。

**问题与机制。** 各自训练的合作策略会形成互不兼容的约定。Other-Play 把已知、保持动力学与收益不变的状态/动作重命名独立施加给各玩家，优化对这些对称变换的稳健性。Hanabi 里随机置换颜色，避免把某个颜色提示私下编码为特定动作；它无须人类示范，但假定环境对称性由设计者给定。形式结论还依赖无外部语义标签、双方都按相应零样本准则构造策略，不能外推到任意伙伴。

**证据与边界。** Hanabi 四种网络结构各三种子；每一配对评 1 万盘。SAD 自博弈约 23.97 分、跨配对仅 2.52；加 OP 跨配对 15.32，结合 AUX 达 22.07。20 名熟悉而非专家级玩家各与两种机器人玩一局，OP 平均 15.75、自博弈对照 9.15；炸局率仍分别为 45% 与 85%，且炸局保留已得分。人类实验选取跨配对最好的模型，是小型初步证据。颜色置换也未消除所有暗语，例如“所有颜色都指向第五张牌”。

**领域位置。** 这提供一种与“把伙伴心智描述得更详细”不同的路线：改变训练问题，让约定本身更容易共享。它最直接影响协作谜题、规则提示与信息不对称队友；不能证明通用 NPC 会理解玩家意图，也不能把同一训练算法的跨种子成功当跨文化/跨能力人类泛化。应分别报告同伴分布、外部语义先验、语言渠道和真实人类测试。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Collaborating with Humans without Human Data](STROUSE_2021_FCP.md) | Other-Play 通过已知奖励不变对称性限制私有约定；FCP 通过多种行为和能力的训练伙伴提高兼容性。 |
| [Benchmarking the Limits of In-Context Reinforcement Learning for Ad-Hoc Teamwork](JING_2026_ICRL4AHT.md) | ICRL4AHT 要从有限历史应对未见伙伴和局部观察，未给出能消除分布变化的已知环境对称性。 |
| [ZSC-Eval: An Evaluation Toolkit and Benchmark for Multi-agent Zero-shot Coordination](WANG_2024_ZSC_EVAL.md) | ZSC-Eval 评价哪些伙伴要求不同最佳响应；Other-Play 本身是利用对称性训练协调策略的方法。 |
