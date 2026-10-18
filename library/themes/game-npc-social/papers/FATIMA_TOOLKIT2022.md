# FAtiMA Toolkit: Toward an Accessible Tool for the Development of Socio-emotional Agents

规范记录：`NPC-PA12`；ACM Transactions on Interactive Intelligent Systems 12(1), Article 8。实际版本：Actually read arXiv 2103.03020v1, 2021-03-04, titled FAtiMA Toolkit - Toward an effective and accessible tool for the development of intelligent virtual agents and social robots; 2022 final publication identity verified, text not line-compared。

**实际阅读范围：** 约37页作者稿全文正文 §1–8及各用例，参考文献浏览；未将引用的Sueca原始研究冒称本轮全文阅读。

[原文](https://arxiv.org/pdf/2103.03020v1) · [发表／主源信息](https://researchportal.ulisboa.pt/en/publications/fatima-toolkit-toward-an-accessible-tool-for-the-development-of-s/)

**规范来源：** [FAtiMA Toolkit: Toward an Accessible Tool for the Development of Socio-emotional Agents](https://arxiv.org/pdf/2103.03020v1)。发表/阅读版本：Actually read arXiv 2103.03020v1, 2021-03-04, titled FAtiMA Toolkit - Toward an effective and accessible tool for the development of intelligent virtual agents and social robots; 2022 final publication identity verified, text not line-compared。

**阅读身份与范围：**新读 arXiv 2103.03020v1 的 §1–8 全部约 33 页正文，核心架构、显式对话表、作者界面和全部应用案例；参考文献浏览。https://arxiv.org/pdf/2103.03020 。正式 TIIS 2022 题名为 FAtiMA Toolkit: Toward an Accessible Tool for the Development of Socio-emotional Agents；本次未拿到正式版本逐句对照，以下以已读作者稿为准。

**实际机制：**独立库代替强制框架，meta-belief 可调用棋类搜索或其他算法并嵌入规则；角色有信念、他人视角、目标、情绪和事件记忆。对话图集中保存可选话语而由角色规则选择，兼容编剧熟悉的工作流。World Editor 定义动作效应；模拟器可操控任一角色并查看信念、触发规则、情绪及记忆；DFS 检查不可达对话状态。高层决策与动作/语音/表情实现明确分工，不能说情绪引擎本身实现全部具身控制。

**制作证据：**外部 PlayGen 开发 Space Modules Inc. 与 Sports Team Manager，前者让客户情绪影响服务评分，后者让个人能力、士气和关系影响组队并保存跨会话状态；开发者接引擎、教育专家填台词。还有六角色 Game Jam、Don’t Starve Together 模组、课程项目及 Sueca 机器人队友。这比概念宣传更具体，但文中没有统一的作者对照评估。Space Modules 的六学校约 1100 人是计划采用/评价，不能写已经实测获益；DST 从 1.8 天到 5 天是不同学生实现的描述，非控制充分的算法对比；机器人信任结果引用另文，不能据此认领已全文核查该试验。

**意义：**角色可信性、可组合工程、制作可控性三者是不同目标。传统认知方法已经支持角色私有状态、社会关系、情绪和动作后果；语言模型的新机会主要还包括自然语言输入、内容扩展与更低的规则制作负担，而非发明这些需求。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Towards Explainable Social Agent Authoring Tools: A case study on FAtiMA-Toolkit](FATIMA_EXPLAINABLE2022.md) | 专门补充可理解性测试和课程作者产物评估。 |
| [StoryVerse: Towards Co-authoring Dynamic Plot with LLM-based Character Simulation via Narrative Planning](STORYVERSE2024.md) | 后者由LLM导演安排剧情计划，本工具将社会情绪决策交给模块化显式架构。 |
| [Ontologically Faithful Generation of Non-Player Character Dialogues](../../../../workbench/game-npc-agents/knowledge/papers/KNUDGE_2024.md) | 固定图约束有共同关注，后者生成图并未接入社会决策运行。 |
