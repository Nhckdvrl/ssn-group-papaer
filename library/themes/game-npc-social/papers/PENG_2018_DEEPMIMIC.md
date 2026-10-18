# DeepMimic: Example-Guided Deep Reinforcement Learning of Physics-Based Character Skills

规范记录：`peng_2018_deepmimic`；ACM TOG 37(4), Article 143 / SIGGRAPH 2018。实际版本：Author-hosted final typeset PDF, August 2018。

**实际阅读范围：** Complete main text §§1–11, PDF pages 1–13; tables 1–6 and ablations; supplemental pages 15–18 and videos not read/viewed; Critical evidence table visually verified on rendered PDF page 11

[原文](https://xbpeng.github.io/projects/DeepMimic/DeepMimic_2018.pdf) · [发表／主源信息](https://xbpeng.github.io/projects/DeepMimic/)

**稳定 ID：** `peng_2018_deepmimic`。TOG 37(4), Article 143 / SIGGRAPH 2018；作者公开正式排版 PDF。**实际阅读：** 完整主文 §§1–11（PDF 1–13），表 1–6、核心消融与局限；补充材料 15–18 未通读，演示视频未观看。

DeepMimic 解决的是动画制作与物理响应的接口：给定角色骨架、短动作捕捉或关键帧片段和任务奖励，训练策略把身体状态、动作相位和目标映射到关节 PD 控制器目标，以 30 Hz 控制物理身体。奖励同时约束参考姿势、速度、末端和质心，并推动移动方向、击中目标或投球等任务。参考状态初始化让策略从动作中间的有效状态开始学习，避免“不会落地所以不敢起跳”；摔倒提前终止则防止训练容量耗在地上模仿动作。两者是训练任务定义的一部分，不是推理时多写一句提示。

正文展示人形、Atlas、霸王龙、龙四种形态和约 30 项技能配置，还比较最大值多片段奖励、显式 one-hot 技能选择与按价值函数选择独立技能三种组合方式。100 次测试中，投球的模仿+任务成功率为 75%，纯模仿仅 5%；纯任务为 93%，却学成持球跑向目标。这是“成功率不足以描述角色行为质量”的直接例证。动作追踪、扰动恢复和用户指定目标可以共同实现，但通常每种技能/角色/环境要分别训练数千万至数亿步。把人形动作重定向给 Atlas 是重新训练的结果，直接移植人形策略失败，不能写成零样本形态泛化。

对 NPC 的意义是角色能通过身体行动、受击恢复与具体目标产生可操作性，而不仅是播预制动画。证据主要是模拟动作、奖励与消融；多数统计仅来自一次训练运行，视觉自然度没有玩家盲评。动作相位线性前进限制时序调整，多片段方法只证明小集合，PD 增益与奖励权重仍需人工设计。论文自己把这些接口与代价说清楚，因此知识库应将它定位为“物理动作生成与控制底座”，不能把几十个运动技能扩写成自主玩法或社会角色能力。

**主源：** https://xbpeng.github.io/projects/DeepMimic/ ； https://doi.org/10.1145/3197517.3201311

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [AMP: Adversarial Motion Priors for Stylized Physics-Based Character Control](PENG_2021_AMP.md) | DeepMimic 跟踪带相位的参考动作；AMP 从无须时序对齐的动作片段分布学习对抗风格奖励。 |
| [ASE: Large-Scale Reusable Adversarial Skill Embeddings for Physically Simulated Characters](PENG_2022_ASE.md) | ASE 将低层技能压入可重复调用的潜变量并冻结供新任务使用；DeepMimic 主要展示任务/动作条件下训练的控制器。 |
| [Generating Personas for Games with Multimodal Adversarial Imitation Learning](MULTIGAIL_2023.md) | MultiGAIL 的风格是游戏动作选择方式，使用角色状态和离散控制；DeepMimic 面向刚体关节物理运动。 |
