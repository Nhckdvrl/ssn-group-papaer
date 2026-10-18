# StoryVerse: Towards Co-authoring Dynamic Plot with LLM-based Character Simulation via Narrative Planning

规范记录：`NPC-PA09`；Foundations of Digital Games (FDG) 2024。实际版本：arXiv 2405.13042v2, 2024-11-02; expanded author version, not identical to 4-page proceedings。

**实际阅读范围：** 全文正文 §1–5、Figures 1–4、两案例；没有人评/系统实验可另行核读。

[原文](https://arxiv.org/pdf/2405.13042v2) · [发表／主源信息](https://arxiv.org/pdf/2405.13042v2)

**规范来源：** [StoryVerse: Towards Co-authoring Dynamic Plot with LLM-based Character Simulation via Narrative Planning](https://arxiv.org/pdf/2405.13042v2)。发表/阅读版本：arXiv 2405.13042v2, 2024-11-02; expanded author version, not identical to 4-page proceedings。

**阅读身份与范围：**新读 arXiv 2405.13042v2 全部正文 §1–5、Figures 1–4 和两域实例；正式会议身份为 FDG 2024，DOI 10.1145/3649921.3656987。阅读 URL：https://arxiv.org/pdf/2405.13042v2 。这是较会议条目长的作者稿，不能把版长混在一起。

**问题和方法：**作者通过带先决条件、抽象目标及待实例化角色槽位的 Abstract Acts 表达戏剧意图；Act Director 在条件满足时安排情节，不满足时让角色按自身描述和记忆进行日常模拟。计划生成后分开检查连贯性、模拟环境可执行性和人物动机，最多两次修订。GPT-4-0125-preview 承担语言推断，环境代理维护状态变量并根据动作更新，玩家干预以直接改变状态来模拟。方法使作者不用枚举所有具体事件，又保留了剧情方向控制。

**证据与限制：**仅用 Ant & Dove、The Ville 两域展示“善有善报”的四幕转换，包括手动令蚂蚁死亡后换角色完成类似情节。两个展示中四幕都恰好连续执行，正文所述与自由模拟交替的更一般情况未有系统试验。没有玩家、作者对照或自动成功率评估，结尾明确把系统指标和用户研究留待未来。不能将“世界可执行检查”写成商用引擎整合，也不能将适配例子写成稳定的长期动态叙事能力。与 WhatELSE 应作为同一研究谱系的早期机制原型和后续人类小样本工具评价连起来，不能当独立重复证据。重要问题是作者怎样规定抽象边界并理解其具体展开；这是开放角色叙事的设计难题，而非单纯生成更多台词。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [WhatELSE: Shaping Narrative Spaces at Configurable Level of Abstraction for AI-bridged Interactive Storytelling](WHATELSE2025.md) | 扩展为可调抽象层级的作者工具并增加作者研究。 |
| [StoryAssembler: An Engine for Generating Dynamic Choice-Driven Narratives](STORYASSEMBLER2019.md) | 早期符号片段规划已有动态重排及状态变化，主要差异为内容表达与作者接口。 |
| [FAtiMA Toolkit: Toward an Accessible Tool for the Development of Socio-emotional Agents](FATIMA_TOOLKIT2022.md) | 提供可嵌入引擎的情绪/社会决策工具，目标不是全局Act生成。 |
