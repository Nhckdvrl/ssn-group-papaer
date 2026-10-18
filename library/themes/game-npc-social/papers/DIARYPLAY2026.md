# DiaryPlay: AI-Assisted Creation of Interactive Story Vignettes for Everyday Storytelling

规范记录：`NPC-PA13`；CHI 2026。实际版本：arXiv 2507.11628v3, 2026-02-04; CHI DOI 10.1145/3772318.3790572。

**实际阅读范围：** 全文正文 §1–9、Tables 1–3、附录 A 参与者信息；外部补充提示未读。

[原文](https://arxiv.org/pdf/2507.11628v3) · [发表／主源信息](https://arxiv.org/pdf/2507.11628v3)

**规范来源：** [DiaryPlay: AI-Assisted Creation of Interactive Story Vignettes for Everyday Storytelling](https://arxiv.org/pdf/2507.11628v3)。发表/阅读版本：arXiv 2507.11628v3, 2026-02-04; CHI DOI 10.1145/3772318.3790572。

**阅读身份与范围：**新读 arXiv 2507.11628v3，全部正文 §1–9、技术比较 Tables 1–3 与 Appendix A 人口表；外置 prompts/研究材料未读。https://arxiv.org/pdf/2507.11628v3 ；DOI 10.1145/3772318.3790572。

**系统与目标：**把日常短故事变成可编辑环境、角色和事件，并在 Phaser 中产生三角色以内的互动。GPT-4o-2024-11-20 提前各生成一个玩家遵循关键事件和一个偏离事件时的 NPC 活动，用角色聊天和主角内心提示让分支汇回作者事件；可以暂时离题，但目标明确是保持同一事件骨架，而非让玩家改写结局。编辑中间结构、对话示例辅助刻画性格、可见路径和物件是具体贡献。

**人类证据分层：**形成研究 13 人；技术研究先 16 人各造场景，再另 16 名评价者阅读活动表，每人评 12 组、共 192 组排名，未实际玩这些条件。CD 平均名次 2.37 优于随机物件基线 4.00；与人类填表 2.58 的 p=.71 只能表示未检出差异，不能证明等效。CD 比只给剧情好，但对只给 persona 的 p=.14 不显著。随后作者/玩家互换研究另 16 人，创作平均 16 分钟、12 人重玩；没有其他创作工具对照或长期部署，14 人自述比通常社媒内容投入并非跨媒介随机试验。

**证据欠账：**人格当前心情静态、最多三角色/一个场所；作者希望情绪沿事件发展、改原文自动更新、回看玩家经历并区别人写与模型生成。核心信息传达由作者听玩家复述判断，正面且适合短篇，尚无职业创作成本或长期玩家效益。本文认真区分日常分享与商业叙事的不同控制需求；知识库应保留这种应用目标差异，不把统一“更开放”当作所有 NPC 的成功方向。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [WhatELSE: Shaping Narrative Spaces at Configurable Level of Abstraction for AI-bridged Interactive Storytelling](WHATELSE2025.md) | 两者都引导故事核心，但抽象故事空间与个人日常再现的作者目的不同。 |
| [Orchid-Creator: An Authoring Tool Supporting LLM-Driven Interactive Narrative Creation](ORCHID_CREATOR2026.md) | 同为非程序员作者工具，后者提供卡片/变量图及长时艺术家案例。 |
| [StoryAssembler: An Engine for Generating Dynamic Choice-Driven Narratives](STORYASSEMBLER2019.md) | 同有汇合/重规划结构，但前者LLM即兴、后者手写片段和显式状态。 |
