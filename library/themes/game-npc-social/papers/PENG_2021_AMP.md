# AMP: Adversarial Motion Priors for Stylized Physics-Based Character Control

规范记录：`peng_2021_amp`；ACM TOG 40(4), Article 144 / SIGGRAPH 2021。实际版本：Author-hosted final typeset PDF, August 2021。

**实际阅读范围：** Complete main text §§1–9, PDF pages 1–13; tables 1–3 and ablations; appendices and videos not fully read/viewed; Critical evidence table visually verified on rendered PDF page 12

[原文](https://xbpeng.github.io/projects/AMP/AMP_2021.pdf) · [发表／主源信息](https://xbpeng.github.io/projects/AMP/)

**稳定 ID：** `peng_2021_amp`。TOG 40(4), Article 144 / SIGGRAPH 2021；作者正式排版 PDF。**实际阅读：** 完整主文 §§1–9（PDF 1–13），表 1–3 与消融；附录任务公式、超参数、全部曲线未通读，视频未观看。

AMP 把角色的任务与动作风格分别放进任务奖励和学习出的动作先验。判别器看连续两个身体状态及显式速度，区分模拟运动与动作数据，不依赖示范者的控制动作，也不要求用相位严格追踪某一段动作。因此，跑向目标后出拳、遇障碍下滚等技能时序组合可在任务优化中形成，不必先人工写片段选择器。最小二乘对抗损失、梯度惩罚、历史重放和有效的身体特征是实现稳定性的具体条件；“无手工动作跟踪误差”不等于完全无需设计输入与奖励。

最大片段集为 8 位演员、56 段、约 434 秒；实验每项通常 3 个训练种子、每模型 32 回合，策略训练 1–3 亿样本、约 30–140 小时 CPU。论文对照纯任务 RL、预训练潜在技能空间和 DeepMimic 式跟踪。加入丰富运动先验后更易在目标速度间切换步态，且角色运动更自然；但任务分数并非普遍优于其他方法，潜在控制器的下游学习有时更快。单片段追踪误差多数仍由显式跟踪方法更低，AMP 的前空翻还会停在向前挪步的局部最优。这里的优势是低负担利用多片段和任务相关组合，不是每个指标全面胜出。

它为 NPC 提供可独立调整的身体行为风格，例如同一导航任务下的潜行或僵尸步态；这种 style 是身体运动统计，不是价值观、目标或社会人格。动作先验在实验中仍为每个策略重新训练；虽然不直接输入目标，判别器负样本由特定任务策略产生，迁移并非自动保证。模式崩塌可能只保留少数动作，现有证据集中在时间组合，不能证明同时做多件动作的空间组合。该文应与 DeepMimic、ASE 连续阅读，理解从片段追踪到可复用技能的真实变化。

**主源：** https://xbpeng.github.io/projects/AMP/ ； https://doi.org/10.1145/3450626.3459670

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [DeepMimic: Example-Guided Deep Reinforcement Learning of Physics-Based Character Skills](PENG_2018_DEEPMIMIC.md) | AMP 放松逐时刻模仿和动作相位要求，但单片精确跟踪并非其优势。 |
| [ASE: Large-Scale Reusable Adversarial Skill Embeddings for Physically Simulated Characters](PENG_2022_ASE.md) | ASE 对 AMP 加入互信息与潜变量结构，目标包括多技能覆盖和跨任务重用，而非每个任务重训风格先验。 |
| [Generating Personas for Games with Multimodal Adversarial Imitation Learning](MULTIGAIL_2023.md) | 两者都有对抗模仿；MultiGAIL 通过多个指定风格判别器调配游戏玩法 persona，不能直接套用物理运动自然度证据。 |
