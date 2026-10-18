# The AI Economist: Optimal Economic Policy Design via Two-level Deep Reinforcement Learning

规范记录：`ai_economist_2021`；arXiv 2021实读版本；后续Science Advances 2022论文题名不同，未取得并核完正式全文，不冒记为已读2022版。实际版本：arXiv:2108.02755v1，提交2021-08-05，PDF内部日期2021-08-24，34页；是2004.13332的扩展但本轮只算一项。

**实际阅读范围：** 完整第1–31页正文与全部Methods，含税制、拍卖、奖励、训练与统计；第33页来源声明及第34页完整算法；第32–33页文献条目非独立读书目

[原文](https://arxiv.org/pdf/2108.02755v1) · [发表／主源信息](https://arxiv.org/abs/2108.02755)

**来源与范围：** 2021；arXiv 2021实读版本；后续Science Advances 2022论文题名不同，未取得并核完正式全文，不冒记为已读2022版；arXiv:2108.02755v1，提交2021-08-05，PDF内部日期2021-08-24，34页；是2004.13332的扩展但本轮只算一项。完整第1–31页正文与全部Methods，含税制、拍卖、奖励、训练与统计；第33页来源声明及第34页完整算法；第32–33页文献条目非独立读书目。[The AI Economist: Optimal Economic Policy Design via Two-level Deep Reinforcement Learning](https://arxiv.org/pdf/2108.02755v1)。阅读标记：new_full_read。

**问题与机制。** 制度不能只在固定行为代理上比较：税制改变劳动、交易和跨期收入安排，制度设计者又应适应代理反应。AI Economist把经济代理与社会规划者同时训练，两层PPO，先学习劳动/市场，再用逐渐增加劳动成本、税率范围和规划者熵控制共同学习的不稳定性。代理共享网络但各有技能、位置、局部观察与循环状态；规划者看资产市场、看不到技能。真正世界由显式资源、撮合拍卖、建房、劳动成本、税收与均分转移账本定义，非法行动被屏蔽，语言不是必要环节。

**任务、对照与结果。** 100代理单步经济先检验已知理论；动态Gather-Trade-Build为4/10代理、每局10税年×100步，2种拓扑组成6配置（Open-Quadrant两人数，Split-World四种技能/资源分配）。比较零税、2018美税率风格基线、Saez公式与学习税制；Saez并非随便默认参数，每配置/福利目标网格调最优弹性。单步5种子匹配理论最佳；4代理开放象限，学习税制较Saez加权效用>8%、平等×产出>12%，10代理约2%/8.6%。Open-Quadrant10种子，其他5种子，每种子末3,000训练episode均值再跨种子统计；不是把几千回合作独立训练重复。Split-World-5,6某福利目标对US基线差异不显著，不能称所有条件都显著胜出。

**新理解。** 高技能建造者税率上升会减少其买料需求，进而降低未进该税档采集者的收入，证明群体后果不能拆成互不影响的单人收益；代理还能把工作在税年之间移动以少缴税。分工、税制响应、机会分配是互相作用的系统，具有游戏经济/派系制度建模的横向价值。

**限制与版本。** 本版本明确没有第三方行为数据或真人实验；只粗校收入形状、假设共同货币效用与劳动厌恶，不能等同真实玩家/社会行为，亦无全局最优或所有均衡的保证。“规避Lucas批评”只是在模型里允许行为适应，并未验证真实适应正确。阶段一训练表25M、正文50M，4代理minibatch表600、正文400，存在复现口径冲突。代码声明有GitHub环境、其他数据需请求，本轮未核运行包。它是制度/群体机制的邻接研究，不能计作已实现可玩人物NPC；正式2022版和早期版本人类实验应单独补读。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Cooperate or Collapse: Emergence of Sustainable Cooperation in a Society of LLM Agents](GOVSIM_2024.md) | 一个改变可执行税收激励并重学行为，一个考察语言规范维持固定公共资源机制。 |
| [Empowering Economic Simulation for Massively Multiplayer Online Games through Generative Agent-Based Modeling](../../../../workbench/game-npc-agents/knowledge/papers/MMOAGENT_KDD2025.md) | 二者都产生经济分工，MMOAgent添加画像语言和P2P交易但未共同学习制度。 |
| [A Parallelized Framework for Simulating Large-Scale LLM Agents with Realistic Environments and Interactions](AGENTSOCIETY_2025.md) | AgentSociety该论文强调大量代理的运行设施，AI Economist强调小规模经济里制度—行为共同适应的辨别。 |
