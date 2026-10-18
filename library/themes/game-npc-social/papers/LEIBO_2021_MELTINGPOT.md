# Scalable Evaluation of Multi-Agent Reinforcement Learning with Melting Pot

规范记录：`leibo_2021_meltingpot`；ICML 2021, PMLR 139:6187–6199; official proceedings。实际版本：Official PMLR main-paper PDF, 13 pages; standalone appendix not included。

**实际阅读范围：** Complete main text §§1–9, PDF pp.1–9; all benchmark protocol, substrate descriptions, baseline setup and conclusion; Main-paper Figures 1–5 inspected through text/captions; per-cell values of dense visual score grid not transcribed; Independent detailed substrate/implementation appendix was not in retrieved 13-page PDF and was not read

[原文](https://proceedings.mlr.press/v139/leibo21a/leibo21a.pdf) · [发表／主源信息](https://proceedings.mlr.press/v139/leibo21a.html)

**稳定 ID：** `leibo_2021_meltingpot`。ICML 2021，PMLR139:6187–6199正式13页主论文。**实际阅读：** 完整主文§§1–9（1–9）；原文所指独立详细附录不在本PDF内，未阅读；不混用Melting Pot 2.0的更大规模。

Melting Pot把社会评估的基本单元写成“世界机制+背景群体=测试场景”。21个底层游戏、约85场景，2–16玩家，覆盖纯竞争、团队共同利益、社会困境、资源分配和约定形成；本代明确未覆盖语言沟通、回合制和物理技能。训练可无限使用底层机制，却不能接触测试背景伙伴；测试把被测群体放入少数访客、多数居民或全员同一策略的三种位置。独立采样每名队员会惩罚依赖预排固定分工的脆弱专才，要求现场可重新组成可用团队。其社会角色与规则结构远宽于“给定任务大家都努力完成”。

背景bot由事件奖励训练和程序串联技能产生，例如别人清理时才清理河流，再用10–30回合检查是否真的表现目标行为；训练bot可读特权事件，而被测策略主要从像素和真实个体回报学习。这样减少手写复杂背景行为的成本，但评价场景仍需要作者选择事件、行为、群体组合与质控，绝非自动覆盖现实社会。评价首要指标是被测群体人均收益，背景群体收益/不平等另列为外部影响指标；高分不自动代表对玩家或其他居民有益。

A3C、V-MPO、OPRE及共享群体奖励的prosocial版本，各底层游戏训练N个体，每个10亿步；主文未提供多独立训练种子置信区间。V-MPO总体较强，但排名受场景权重影响。某些自我合作得分高的prosocial策略在陌生背叛者面前很差，而Clean Up只有prosocial显著超过随机；“自利比合作更好”不是其结论。直接在测试场景训练的exploiter也不总最高，因为强bot难以探索或自利奖励妨碍协作，不能当精确性能上限。全部算法在两烹饪底层连训练都未成功，相关测试失败不能专门归因为社会泛化。

这篇给知识库的是独立评价轴：同一物理世界换一组居民就可能变成新问题；自身效用、他人影响、在多数或少数位置下的可行性和固定分工脆弱性都应分开。它不是持久人格NPC或人类玩家实验，具体结论仅为这些合成场景下的学习行为，不能把trust/forgiveness等结论词当已经独立测量的心理机制。

**主源：** https://proceedings.mlr.press/v139/leibo21a.html

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [ZSC-Eval: An Evaluation Toolkit and Benchmark for Multi-agent Zero-shot Coordination](WANG_2024_ZSC_EVAL.md) | Melting Pot 将世界机制与背景群体组合为场景；ZSC-Eval 更精细衡量共享目标伙伴所需的不同最佳响应。 |
| [Human-level performance in 3D multiplayer games with population-based reinforcement learning](JADERBERG_2019_QUAKE.md) | FTW 证明一个团队竞争游戏中强像素控制；Melting Pot 更广地比较多种社会收益结构，但不是人类可玩 NPC 验证。 |
| [“Other-Play” for Zero-Shot Coordination](HU_2020_OTHER_PLAY.md) | Other-Play 利用预先识别的环境对称性解决约定冲突；Melting Pot 用多样背景群体测试更一般的社会泛化。 |
