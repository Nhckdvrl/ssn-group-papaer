# Autonomous Agents Modelling Other Agents: A Comprehensive Survey and Open Problems

规范记录：`albrecht_stone_2018_survey`；Artificial Intelligence 258:66–95。实际版本：arXiv v2, 2018-02-09; author accepted manuscript。

**实际阅读范围：** Abstract and complete main text §§1–6, Appendix A, PDF pages 1–37; references not individually followed; Tables 2–9 captions/assumption axes read; text extraction misaligned cells, not all survey-table entries visually verified

[原文](https://arxiv.org/pdf/1709.08071) · [发表／主源信息](https://www.cs.utexas.edu/~pstone/Papers/bib2html/b2hd-AIJ18-Albrecht.html)

**稳定 ID：** `albrecht_stone_2018_survey`。AIJ 258:66–95；所读 arXiv v2（2018-02-09），作者接受稿。**实际阅读：** 摘要及全文 §§1–6、附录 A（PDF 1–37）；参考文献清单未逐项追读；表 2–9 的逐行 yes/no 排版经文本提取错位，未声称每个调查条目均视觉复核。

这篇不是专门讨论 NPC 的游戏综述，但提供了比“给 agent 增加记忆/反思”更稳固的上位结构：策略重建、基于类型的推断、分类、计划识别、递归推理、图模型、群体建模回答的是不同问题。策略重建预测可观察行动；计划识别追踪目标与部分有序计划；分类把行为映射到预设风格；递归推理显式处理“他如何看待我”。它将方法假设按伙伴是否变化、是否知道决策因素、行为是否相关、目标是否共同，以及可观测性、离散/连续接口和行动顺序排列，说明“对人建模”不能只报一个预测准确率。

最重要的可靠性提醒是：贝叶斯类型后验只在候选集合内相对归一化，即使所有候选都错，也会对其中一个十分自信。安全回应因此需在利用预测与最坏情形防护之间调节；主动探测伙伴则既获取信息，也会改变对方行为，不能把探测当无成本查询。多层信念与联合行动的计算量迅速增长；实际游戏的代理计算还要与渲染、物理争用预算。该综述假定已能识别对方行动，不覆盖从原始视觉识别动作，因此不能替代具身感知研究。

这里的证据是专家方法综述，非统一基准的定量元分析；不能把所列九项“2018 年开放问题”原样称为 2026 年未解决问题。本轮后续论文正好逐项修正它：FCP/MEP/HSP 用训练分布制造伙伴先验，CooT 等测试历史条件适应，CEC 扩大环境多样性。领域位置是知识库的概念主干，可帮助分别记录伙伴目标、技能、惯例、可观测性和模型不确定性，避免把不同难点揉成“智能不足”。

**主源：** https://www.cs.utexas.edu/~pstone/Papers/bib2html/b2hd-AIJ18-Albrecht.html ； https://arxiv.org/abs/1709.08071

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [On the Utility of Learning about Humans for Human-AI Coordination](CARROLL_2019_HUMAN_AWARE.md) | 综述按假设和模型类别组织他者建模；Carroll 在具体共享奖励游戏中检验人类行为模型是否改善最佳响应。 |
| [Collaborating with Humans without Human Data](STROUSE_2021_FCP.md) | FCP 不显式推断当前伙伴类型，利用冻结行为池学稳健响应，提供显式他者建模以外的路线。 |
| [Learning Zero-Shot Cooperation with Humans, Assuming Humans Are Biased](YU_2023_HSP.md) | HSP 的隐藏效用主要用于合成伙伴分布，不等同从真实玩家行动中识别其内在目标。 |
