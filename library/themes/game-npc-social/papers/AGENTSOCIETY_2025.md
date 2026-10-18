# A Parallelized Framework for Simulating Large-Scale LLM Agents with Realistic Environments and Interactions

规范记录：`agentsociety_2025`；ACL 2025 Industry Track, 1339–1349。实际版本：Published ACL Anthology PDF, 11 pages。

**实际阅读范围：** 全部11页正文、表1–2及实现/替代模拟提示/指标附录 A–B

[原文](https://aclanthology.org/2025.acl-industry.94.pdf) · [发表／主源信息](https://aclanthology.org/2025.acl-industry.94/)

**来源与范围：** 2025；ACL 2025 Industry Track, 1339–1349；Published ACL Anthology PDF, 11 pages。全部11页正文、表1–2及实现/替代模拟提示/指标附录 A–B。[A Parallelized Framework for Simulating Large-Scale LLM Agents with Realistic Environments and Interactions](https://aclanthology.org/2025.acl-industry.94.pdf)。阅读标记：new_full_read。

本篇AgentSociety由Jun Zhang等作者提出，是11页ACL Industry系统论文，不能与Piao等同名75页社会仿真论文混计。系统把城市路网/地点/交通、可改变关系强度的社交消息网、雇佣/消费/存款/税收账本接到代理，实际世界状态与LLM叙述分开。Ray分组共享连接、异步消息及时间对齐使决策等待不改变模拟时钟：通常一轮代理相当于环境300秒。其价值不仅是“多代理”，而是互动与世界后果在可重复时序下维持。

24张A800、Qwen2.5-7B、一轮平均约348输入/62输出token，表1测10轮均值，3万代理8组约251.85秒/轮，约70.7次代理消息/轮；4组反而327.39秒，更多组因请求失败不能完成。不能把最佳配置推广为任意密集长对话的3万NPC实时运行。行为验证使用北京169位居民轨迹与意图数据，世界支持对照由LLM猜地点、距离和交通时间；表2运动半径误差0.427降0.023，意图序列指标0.241降0.094，同时比较TimeGeo、Movesim、Volunteer、DiffTraj、Act2Loc。环境合理约束确能显著改变行为分布，但这不是角色心理或玩家沉浸实验；指标误差具体函数与独立重复未充分展开。

领域位置是社会模拟基础设施邻接NPC世界运行。其账本已有税/利率调整，作者仍明确缺市场机制与企业决策，不可宣称完整经济。对游戏的可迁移认识是世界反馈质量、规模与交互密度必须一起报告；分布接近真实居民并不自动意味着有趣的生活NPC，反之有趣NPC也不一定以逐人社会预测为目标。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [CitySim: Modeling Urban Behaviors and City Dynamics with Large-Scale LLM-Driven Agent Simulation](../../../../workbench/game-npc-agents/knowledge/papers/CITYSIM_2025.md) | 两者城市仿真目标接近，但性能规模、现实校准任务和决策时钟不同。 |
| [Generative agent-based modeling with actions grounded in physical, social, or digital space using Concordia](CONCORDIA_2023.md) | 从通用GM架构对比可见，专门硬环境和稀疏通信是规模数据的解释条件。 |
| [Empowering Economic Simulation for Massively Multiplayer Online Games through Generative Agent-Based Modeling](../../../../workbench/game-npc-agents/knowledge/papers/MMOAGENT_KDD2025.md) | 两者都有经济状态；MMOAgent更细看交易决策，AgentSociety该论文重点是并行与交通环境。 |
