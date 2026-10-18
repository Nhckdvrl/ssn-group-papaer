# On the Utility of Learning about Humans for Human-AI Coordination

规范记录：`carroll_2019_human_aware`；NeurIPS 2019。实际版本：arXiv:1910.05789v2, 2020-01-09。

**实际阅读范围：** Complete main text sections 1-8, PDF pages 1-9; Appendix A, F-H; end of Appendix E, PDF pages 13,17-19

[原文](https://arxiv.org/pdf/1910.05789) · [发表／主源信息](https://arxiv.org/abs/1910.05789)

**来源与范围。** [原文](https://arxiv.org/abs/1910.05789)，NeurIPS 2019；读 arXiv v2（2020-01-09）主文 §§1–8，附录 A、F–H 及 E 的后半；其余训练超参数未系统细读。

**问题与机制。** 强自博弈策略能否直接成为人类队友？作者用共享收益、六种离散动作、完整符号状态的五张 Overcooked 地图隔离合作：PPO-BC 把行为克隆的人类模型放进环境，再学其最佳回应；对照有自博弈 PPO、PBT、直接模仿，以及每一步重新联合规划的分层 A*。它研究的是共同目标下的可配合性，并非自利人物、语言协商或关系发展。

**证据与边界。** 每图约 12–17 条经过筛选的人类双人轨迹，拆成两个模型训练集；模拟每条件五种子、100 回合。60 人在线研究支持 PPO-BC 总体更适配，但附录 H 很关键：正文排除了“故意挡路、观察 AI”等不合作轨迹；保留这类轨迹后，对 PBT 仍显著，对自博弈则 p=.06。模型式规划只跑两图，而且为降复杂度把人类模型确定化、100 步成绩乘四，不能当完整理性上界。作者观察到人类迁就固定路径，使真实人类成绩缩小模拟差距。

**领域位置。** 价值在于拆开“个人技术强”“伙伴预测准确”“人类愿意/能够配合”。作者已经提出扩大环境多样性可能替代显式人类建模；后续 FCP、HSP、CEC 应被读成对这一替代解释的逐步检验，不能把本文结论固化为“人类数据永远必要”。玩家试探 AI 在游戏中也可能是正常玩法，而非纯粹噪声。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Collaborating with Humans without Human Data](STROUSE_2021_FCP.md) | Carroll 依赖人类演示建立训练伙伴；FCP 用自博弈种子和历史检查点替代这些人类数据，再做独立真人验证。 |
| [Learning Zero-Shot Cooperation with Humans, Assuming Humans Are Biased](YU_2023_HSP.md) | HSP 用事件偏好生成更异质伙伴，并加强早期方法的实现；它不沿用固定人类行为克隆作为核心假设。 |
| [Building Cooperative Embodied Agents Modularly with Large Language Models](ZHANG_2024_COELA.md) | CoELA 增加语言沟通、部分观察和显式空间执行模块；Carroll 主要隔离完整状态下的非语言共享目标协调。 |
