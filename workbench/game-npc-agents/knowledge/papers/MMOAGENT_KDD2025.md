# Empowering Economic Simulation for Massively Multiplayer Online Games through Generative Agent-Based Modeling

规范记录：`mmoagent_2025`；KDD 2025 Research Track，3366–3377（官方KDD清单及ACM DOI检索核实）。实际版本：arXiv:2506.04699v1，2025-06-05，12页，会议排版作者稿。

**实际阅读范围：** 完整正文第1–9页；附录A–E第11–12页全部资源/行动/参数/真人数据与评判协议；参考文献未逐篇查证

[原文](https://arxiv.org/pdf/2506.04699v1) · [发表／主源信息](https://kdd.org/kdd2025/research-track-papers-2/)

**来源与范围：** 2025；KDD 2025 Research Track，3366–3377（官方KDD清单及ACM DOI检索核实）；arXiv:2506.04699v1，2025-06-05，12页，会议排版作者稿。完整正文第1–9页；附录A–E第11–12页全部资源/行动/参数/真人数据与评判协议；参考文献未逐篇查证。[Empowering Economic Simulation for Massively Multiplayer Online Games through Generative Agent-Based Modeling](https://arxiv.org/pdf/2506.04699v1)。阅读标记：first_full_body_after_existing_partial_card。

**问题与机制。** 面向开发者在上线前研究MMO经济的仿真玩家，非有世界人物身份的可玩NPC。继承MMO Economist的经验、材料、代币、外部货币、能力、劳动状态与生产/升级/充值/市场，再加公私聊天议价的P2P交易；GPT模型的高层动作由DFS/A*或规则执行，拍卖/P2P细节用LLM，失败获游戏规则反馈。短记忆保留10步，长期记忆按数值状态相似度及成功贡献检索，定期反思调整获取资源的方法。自然语言交易确实导致资产变化，并非只口头成交。

**数据与对照。** 一个未公开名称的网易MMO，16,294玩家2024-03-04至10一周日志，8项特征聚5簇，再GPT-4写5种消费/活动画像；真实数据只用于原型初始化，未做留出玩家的行为或政策反应预测。性能实验同一模拟器3资源密度（70/50/30%）×10玩家×200步×5重复；主要GPT-3.5-turbo及Llama3-8B，比较随机、规则、MMO-economist RL、ReAct、Reflexion及记忆反思消融。GPT3.5能力121/80.4/75，对RL92.4/72.6/51.8；性能收益含可靠宏动作与状态记忆的组合，尚无当前强API基线。Diversity为动作熵，不是越高越好，也不直接代表真实玩家策略分布。

**社会/经济证据。** 每画像1,500步切15步片段，以GPT-4评与预设画像匹配得3.75–3.89/5；3人查20%宣称95%一致，但未给一致定义/误差条，不能等同真实行为95%复现。宏观研究30代理×200步，拍卖价6.86、P2P6.46，需求供给缺口与价格r=.67；显示本模型内部供需、分工与资源稀缺带来的充值/能力不平等反馈。200时间点具有依赖性，不能当200独立经济实验；宏观重复数量与现实校准不足。

**领域位置。** 强处是把社会语言接进生产—交易—能力提升的闭环，经济后果可由账本核。原文“准确镜像真实世界”的结论超出只比方向性经济常识的证据。真正重要的是验证同一制度变更对不同类型玩家、市场价格、机会分配与长期参与的预测，而非仅重现供需符号。作者声明Zenodo开放代码，本轮未运行或核全公开数据范围。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [The AI Economist: Optimal Economic Policy Design via Two-level Deep Reinforcement Learning](../../../../library/themes/game-npc-social/papers/AI_ECONOMIST_2021.md) | AI Economist联合学习制度与理性代理，MMOAgent通过语言画像和议价模拟游戏消费/交易。 |
| [A Parallelized Framework for Simulating Large-Scale LLM Agents with Realistic Environments and Interactions](../../../../library/themes/game-npc-social/papers/AGENTSOCIETY_2025.md) | 后者主测并行城市仿真，MMOAgent主测经济行为和画像符合。 |
| [Vox Deorum: A Hybrid LLM Architecture for 4X / Grand Strategy Game AI -- Lessons from Civilization V](VOX_DEORUM_2025.md) | 都用可靠底层执行承接LLM宏动作；一个是仿真玩家经济，另一个在商业4X中换宏观战略层。 |

## 官方资产与历史核查范围

[Zenodo代码归档](https://doi.org/10.5281/zenodo.15526912)

保留此前定向代码核查：124,339 bytes归档，SHA-256 ee82b807c38dd7b281467557c5960708eae3f02876a2e4e0acddc26ad6278182；读过README、MMOAgent.py的背景／决策／议价提示及Bargain.component_step，未重跑。该DOI是代码归档，不证明真实玩家原始日志或原表全部配置均已公开。本次未重新取得归档，不将访问失败写成资产消失。 历史核查细节与固定文件身份见[此前规范卡](https://github.com/Nhckdvrl/ssn-group-papaer/blob/c3af2a785368632ebcce5bc8cfce8994ecc56eb3/workbench/game-npc-agents/knowledge/papers/MMOAGENT_KDD2025.md)。
