# Vox Deorum: A Hybrid LLM Architecture for 4X / Grand Strategy Game AI -- Lessons from Civilization V

规范记录：`vox_deorum_2025`；arXiv预印本；截至本轮主源仍写Under review，FDG 2026模板及占位DOI不是录用证据。实际版本：arXiv:2512.18564v2，2025-12-25，17页。

**实际阅读范围：** 完整正文第1–9页；附录A.1系统提示第10–11页全部，A.2状态样例首段第11页/末段第16页，B第16–17页全部输出；第12–15页长状态转储未逐行读

[原文](https://arxiv.org/pdf/2512.18564v2) · [发表／主源信息](https://arxiv.org/abs/2512.18564)

**来源与范围：** 2025；arXiv预印本；截至本轮主源仍写Under review，FDG 2026模板及占位DOI不是录用证据；arXiv:2512.18564v2，2025-12-25，17页。完整正文第1–9页；附录A.1系统提示第10–11页全部，A.2状态样例首段第11页/末段第16页，B第16–17页全部输出；第12–15页长状态转储未逐行读。[Vox Deorum: A Hybrid LLM Architecture for 4X / Grand Strategy Game AI -- Lessons from Civilization V](https://arxiv.org/pdf/2512.18564v2)。阅读标记：first_full_body_after_existing_partial_card。

**问题与机制。** 把LLM放在4X帝国的宏观战略层，成熟Vox Populi算法负责军队移动、城市生产与战术搜索。LLM选胜利路线、经济/军事策略、下项科技和政策，调外交persona权重，经原AI的flavor数值影响真实游戏行动；论文所测版本的外交宣战/条约仍由算法做，尚未实现自然语言与人类商谈；当前项目的后续变化见本卡资产段。每轮给同可见权限世界状态、前轮事件与上次策略理由，系统提示约989词元，无复杂反思或长期记忆。这个结果说明合理的责任划分及可靠技能能大幅改变对LLM能力的判断。

**实验与结果。** Civilization V＋Vox Populi 5.0.0-alpha3，固定tiny Communitas地图、4玩家、43文明随机；玩家0分别VPAI919局、GPT-OSS-120B983局、GLM-4.6425局，另3玩家均VPAI，总2,327个完成局。存活97.3/97.5/97.6%；控制文明后的胜率边际效应−2.65百分点(p=.182)、−1.61(p=.534)，分数比亦不显著。应写“未检出差异”，不是已通过等效/非劣效检验。共同战术层不意味着LLM没作用：OSS优势偏征服、GLM更偏文化，政策路径、策略改变率确有差异。未比较当前商业顶级模型或不同多方LLM组合。

**范围与限制。** 这是一个商业游戏规则体系内的大样本，不是2,327独立游戏品类；崩溃与连续15轮以上API失败局被剔除，无法从完成样本推总体运行100%可靠。30%局缺token日志。14.8秒是依据外部硬件基准与token数推算的每轮延迟，非实际完整游戏延迟；正文另一处误写每局，不应沿用。第5页称输入二次/输出线性增长，第6页又称输入线性/输出基本恒定，也需保留版本矛盾而不择优引用。未有真实玩家、自然协商、人格偏好或更少作弊补偿的实验证据。

**领域位置。** 价值在可保持竞争力的不同长期策略风格和可干预宏观控制，紧邻策略游戏对手/顾问而非角色对白。开放问题包括世界越来越复杂时如何压缩信息、可靠改弦更张、宏观意图怎样经战术执行仍达成，以及玩家能否理解并协商这些策略。不能把文本宣称的外交合作设计愿景列作已验证玩法。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Empowering Economic Simulation for Massively Multiplayer Online Games through Generative Agent-Based Modeling](MMOAGENT_KDD2025.md) | 都将高层语言决策接到数值状态，但Vox用成熟商业游戏AI，MMOAgent是简化经济模拟器。 |
| [The AI Economist: Optimal Economic Policy Design via Two-level Deep Reinforcement Learning](../../../../library/themes/game-npc-social/papers/AI_ECONOMIST_2021.md) | AI Economist优化制度及代理激励，Vox让LLM选择既有帝国策略并由算法执行。 |
| CivRealm: A Learning and Reasoning Odyssey in Civilization for Decision-Making Agents（非本轮独立全文记录） | Vox正文直接以CivRealm为邻接比较：前者保留完整战术AI，CivRealm提供FreeCiv细粒度学习/推理环境；CivRealm正文尚未完成独立阅读，列为跨游戏控制方向的阅读欠账。 |

## 官方资产与历史核查范围

[Vox Deorum当前项目](https://github.com/vox-deorum/vox-deorum) · [玩家与互动外交说明](https://github.com/vox-deorum/vox-deorum/blob/main/docs/players/playing.md) · [系统架构说明](https://github.com/vox-deorum/vox-deorum/blob/main/docs/developers/architecture.md) · [互动外交开发说明](https://github.com/vox-deorum/vox-deorum/blob/main/docs/developers/diplomacy.md)

2026-10-18完整阅读当前作者README及playing、architecture、diplomacy三份文档；README自报0.13.6 Beta。文档将语言表达的diplomat、决定条款的negotiator、可交易范围检查、提议账本与游戏结算分开：提议可以接受、拒绝、修改或撤回，跨回合保留对话；接受时重新检查提议与条款，调用Deal:Enact／Player:SetPromise，写入可追踪结果。承诺类型限定为底层AI已有对应处理的military、expansion、border、no digging与cooperative war，并非任意自然语言承诺都会获得执行语义。

这些是论文所测版本之后的作者技术文档所述实现，不再只是2025论文中的外交愿景。这里未独立审完对应源代码，也未运行验证可靠性、各种条件变化后的履约或玩家收益；不将新功能回填为论文的2327局实验结果。架构文档还说明按玩家回合暂停与背压，不能把接入真实游戏等同于无等待实时运行。 历史核查细节与固定文件身份见[此前规范卡](https://github.com/Nhckdvrl/ssn-group-papaer/blob/c3af2a785368632ebcce5bc8cfce8994ecc56eb3/workbench/game-npc-agents/knowledge/papers/VOX_DEORUM_2025.md)。
