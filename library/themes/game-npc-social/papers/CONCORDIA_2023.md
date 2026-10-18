# Generative agent-based modeling with actions grounded in physical, social, or digital space using Concordia

规范记录：`concordia_2023`；arXiv preprint; no archival venue verified。实际版本：2312.03664v2, 2023-12-13, 32 pages。

**实际阅读范围：** 完整正文 pp.1–23及全部实现附录 A pp.23–26；参考文献仅按相关条目核读，不等同代码审计

[原文](https://arxiv.org/pdf/2312.03664v2) · [发表／主源信息](https://arxiv.org/abs/2312.03664)

**来源与范围：** 2023；arXiv preprint; no archival venue verified；2312.03664v2, 2023-12-13, 32 pages。完整正文 pp.1–23及全部实现附录 A pp.23–26；参考文献仅按相关条目核读，不等同代码审计。[Generative agent-based modeling with actions grounded in physical, social, or digital space using Concordia](https://arxiv.org/pdf/2312.03664v2)。阅读标记：new_full_read。

Concordia用“我是谁、这是什么处境、我这样的人在此会做什么”的适切性逻辑组织代理，而不要求每次显式最大化数值效用。身份、情绪、目标、计划、感知等组件从关联记忆生成当前工作上下文，可由LLM或普通程序更新。代理只提交行动尝试，GM另行决定发生了什么、谁看到、金钱/物品/投票等变量怎样改变。Python硬状态、经典动力学与自由文字可混合；手机子GM把行动翻译成指定函数、参数和返回结果，还可嵌套不同时间尺度。它确立了角色解释、世界裁决与观测分配的清楚接口，不等于自然语言本身拥有任意行动权。

论文是框架与理论阐释，所列6个示例包括两人日历安排、5人选举/城镇、4人困在酒吧争执、豆子交易、Cyberball；没有系统样本量、强基线、人类逼真度或可控性比较。身份特质是否真正展现明确仍待验证，并发行动可能产生不一致也由附录指出。文中的神经科学和社会建构解释是建模视角，不是经该系统实验确证的心理理论。计划未来加入叙事关键帧以约束偏航，说明架构表达力与可控结果应分开。

其广域用途是把社会关系、制度、工具和物理后果放进同一建模语言；机构还可作为宏观代理，未必逐个模拟职员。重要的方法论贡献是要求每种应用重新验证人群保真度，以未受训练污染的新数据/真实干预优先，理论相容与提示稳健性不能替代外部效度。对NPC开发可作为世界—角色边界参考，对社会科学则只是待验证模拟工具；两者成功标准不能混用。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [A Parallelized Framework for Simulating Large-Scale LLM Agents with Realistic Environments and Interactions](AGENTSOCIETY_2025.md) | AgentSociety并行框架把城市交通/通信规则落实成专门环境；Concordia是通用组件与GM裁定架构。 |
| [SOTOPIA: Interactive Evaluation for Social Intelligence in Language Agents](SOTOPIA_2024.md) | Sotopia默认把自由文本追加为状态；Concordia显式分开行动尝试、裁定事件及各人观察。 |
| [HAMLET: A Hierarchical and Adaptive Multi-Agent Framework for Live Embodied Theatrics](../../../../workbench/game-npc-agents/knowledge/papers/HAMLET_2026.md) | HAMLET的GM/导演服从戏剧蓝图，Concordia组件可用于社会或数字工具情境且不固定剧情终点。 |
