# Generating Personas for Games with Multimodal Adversarial Imitation Learning

规范记录：`multigail_2023`；IEEE Conference on Games (CoG) 2023; EA author publication page verified。实际版本：arXiv v1, 2023-08-15。

**实际阅读范围：** Complete main text I–VI, PDF pages 1–8; Algorithm 1, Tables I–IV; internal alpha-label inconsistencies noted; prior knowledge base had brief mention only

[原文](https://arxiv.org/pdf/2308.07598) · [发表／主源信息](https://arxiv.org/abs/2308.07598)

**稳定 ID：** `multigail_2023`。IEEE CoG 2023（EA作者发布页核定）；arXiv v1（2023-08-15）。**实际阅读：** 完整主文 I–VI（PDF 1–8），算法1、表 I–IV；此前知识库只有短条目，本轮为首次完整阅读，不计第二个版本。

MultiGAIL 的 persona 是供自动化试玩使用的行为风格。一个策略接收风格混合向量，多个判别器分别比较各类示范与策略行为，按混合权重提供奖励；同时保留到达目标的任务奖励。它把“怎么做”从纯奖励工程移到示范与条件输入，推理时可切换/混合风格，不必每种风格载入一个策略。实验是两个人工3D环境：竞速的谨慎/鲁莽加速转向，以及城市导航的跳跃、之字走、横移，最多三种风格。状态含目标与物体相对坐标、游戏专有量和5³语义体素图，并非原始像素开放游戏。

人类示范竞速约2万状态动作、导航约6万；每种评估混合权重运行30回合，未给多训练种子误差。与各风格独立AMP相比，竞速多数动作边缘分布散度更低，导航大致相当；并非所有指标都胜出，例如谨慎竞速Wasserstein为0.28对AMP0.26。与离散Policy Fusion比较，组合动作较丰富；连续权重与实际风格并非线性，等权不保证均衡。正文、表III/IV在α各维对应风格的标签上存在不一致，故不转录成可靠控制映射；若复现必须对作者代码核查。

价值在设计者可调的行为覆盖和示范接口，不是证明“人格一致的NPC”已经实现。论文用总体动作使用率/散度评价，未测给定情境下是否选择正确动作、复杂目标轨迹、不同人物价值取舍、真正玩家分布覆盖，亦无人类对自然度/易用性的对照实验。其目标是自动试玩，作者对玩家NPC用途仍属展望。知识库应保留“player persona／动作风格／社会人物人格”三个不同含义，防止因为名称相同就混为最近邻研究。

**主源：** https://arxiv.org/abs/2308.07598 ； https://www.ea.com/seed/news/seed-cog2023-multimodal-adversarial-imitation-learning

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [AMP: Adversarial Motion Priors for Stylized Physics-Based Character Control](PENG_2021_AMP.md) | MultiGAIL 将多个风格判别器显式混合到游戏动作选择；AMP 主要为物理运动分布提供风格先验。 |
| [Learning to Move Like Professional Counter-Strike Players](DURST_2024_MLMOVE.md) | MultiGAIL 人为定义慎重/鲁莽等可调玩法风格；MLMove 更重视固定战术模式中专业玩家移动分布。 |
| [Enemy Within: Long-term Motivation Effects of Deep Player Behavior Models for Dynamic Difficulty Adjustment](PFAU_2020_ENEMY_WITHIN.md) | Enemy Within 从当前玩家日志生成其镜像对手；MultiGAIL 从既有风格演示学习可控 persona，未做长期玩家研究。 |
