# StoryAssembler: An Engine for Generating Dynamic Choice-Driven Narratives

规范记录：`NPC-PA10`；Foundations of Digital Games (FDG) 2019。实际版本：Author-hosted 10-page published-layout PDF; DOI 10.1145/3337722.3337732。

**实际阅读范围：** 全文正文 §1–10、Figures 1–5文字，实际作者生产案例；参考文献浏览。

[原文](https://mkremins.github.io/publications/StoryAssembler.pdf) · [发表／主源信息](https://mkremins.github.io/publications/StoryAssembler.pdf)

**规范来源：** [StoryAssembler: An Engine for Generating Dynamic Choice-Driven Narratives](https://mkremins.github.io/publications/StoryAssembler.pdf)。发表/阅读版本：Author-hosted 10-page published-layout PDF; DOI 10.1145/3337722.3337732。

**阅读身份与范围：**新读作者稿全部正文 §1–10、五幅图的图注与对应机制说明；参考文献浏览。Garbe、Kreminski、Samuel、Wardrip-Fruin、Mateas；10 页，DOI 10.1145/3337722.3337732。来源：https://mkremins.github.io/publications/StoryAssembler.pdf 。

**方法及真实制作：**前向状态搜索与 HTN 式片段组合共同生成选项叙事。片段带前提、文本、选择、状态效应；Story Spec 规定要达成的叙事节拍或状态，玩家每次选择后重规划。外部小游戏持续改变黑板状态，使当前选项能实时变灰、出现或改变口吻。Emma’s Journey 由 6 名刚入游戏本科、程序经验有限的写作者制作 8 场景，气候研究者的职业和社交剧情与小游戏状态互相影响。这是具体制作案例，尚非随机作者实验或玩家效果试验。

**作者需求与失败证据：**可复用内容降低逐分支编写需求，却产生新的状态组合、因果顺序和调试负担。“no path found”、早期片段改变晚期条件、内容意外孤立让作者倾向收紧前提、退回静态链接。团队因此用自动试玩聚合的图展示实际路径、目标达成、复用片段和有效/无效候选，并允许作者选择哪些状态变量定义“同一节点”。编辑器原型无法覆盖复杂结构，最终仍使用 JSON；不能称为已完成的无代码工具。正文没有量化效率提升。

**横向意义：**生成能力超过作者的理解、验证与修改能力时，作品反而缩回系统最保守的用法。2019 年已有“可能性空间可视化”、按作者目标查看状态差异、实时玩法影响叙事等明确需求，现代 LLM 作者工具需要继承并重新验证这些需求。它说明完整作品制作所得的设计知识可独立有价值，也提醒“少写几行内容”并不等于降低总制作成本。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [FAtiMA Toolkit: Toward an Accessible Tool for the Development of Socio-emotional Agents](FATIMA_TOOLKIT2022.md) | 均重视库集成、状态和作者检视，后者集中社会情绪角色。 |
| [Elsewise: Authoring Open-Ended Interactive Narrative with Possibility Space Visualization](ELSEWISE2026.md) | 后者用LLM玩家和语义维度显示可能空间，前者图节点来自明确状态和片段。 |
| [Ontologically Faithful Generation of Non-Player Character Dialogues](../../../../workbench/game-npc-agents/knowledge/papers/KNUDGE_2024.md) | 生成对话图并做结构修订，但未测开发者编辑/生产工作。 |
