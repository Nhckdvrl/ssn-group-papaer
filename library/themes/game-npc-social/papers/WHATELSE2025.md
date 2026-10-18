# WhatELSE: Shaping Narrative Spaces at Configurable Level of Abstraction for AI-bridged Interactive Storytelling

规范记录：`NPC-PA06`；CHI 2025。实际版本：Author institutional PDF; DOI 10.1145/3706598.3713363。

**实际阅读范围：** 全文正文 §1–9、Tables 1–3、Figures 1–8文字/说明；PDF没有文中提到的提示附录，外部补充未读。

[原文](https://www.research.autodesk.com/app/uploads/2025/02/WhatELSE.pdf) · [发表／主源信息](https://www.research.autodesk.com/app/uploads/2025/02/WhatELSE.pdf)

**规范来源：** [WhatELSE: Shaping Narrative Spaces at Configurable Level of Abstraction for AI-bridged Interactive Storytelling](https://www.research.autodesk.com/app/uploads/2025/02/WhatELSE.pdf)。发表/阅读版本：Author institutional PDF; DOI 10.1145/3706598.3713363。

**主源与范围**：[Autodesk作者全文](https://www.research.autodesk.com/app/uploads/2025/02/WhatELSE.pdf)，Lu、Zhou、Wang，DOI10.1145/3706598.3713363。正文§1–9、表1–3、图1–8说明全读；独立补充材料未获取，正文所称prompt appendix不在此18页PDF内，未冒称读取。

作品不是单一故事，而是作者愿意让玩家经历的可能性空间。作者以具体范例为pivot，用不同抽象层级outline约束结构，再查看生成variants，调整、删除与重概括。执行器给GPT4o世界状态、动作schema和人物记忆，先提动作计划，再经LLM连贯性/动机批评和模拟环境的动作可行性反馈迭代。12名AI有经验但叙事创作几乎零经验的机构参与者，以顺序平衡方式比较系统与聊天式LLM助手；在同一6角色/5地点/6动作童话域，用两个指定寓意创作并试玩。作者报告控制感中位7对5、寓意对齐6对4、生成事件满意6.5对4.5等差异，但样本小、多项量表检验，且工具UI和运行规划同时改变，不能将效果全部归给抽象滑杆。

作者观察到具体变体有助发现意图偏离、抽象纲要帮助有意改变范围；这对传统逐分支写作和纯提示之外的创作接口有实际意义。技术测试以词汇具体性与ROUGE距离代理抽象/多样性；死亡角色不再出现的比例1.00对0.85，是简单死亡状态持续性的证据，不是完整因果正确率。玩家影响试验只用固定两幕、杀害/求助两类干预及每类20条续写；技术段对50/100个LLM outline的叙述也不一致，应保留原文限制。作者自己将专业作者、复杂作品、独立玩家长期体验、实际外部游戏引擎部署列为后续。整体价值在将作者意图的表达、可视审阅和受约束运行组合起来，不能把试玩满意或词汇差异直接升级为成熟产品的玩家能动性增益。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [StoryVerse: Towards Co-authoring Dynamic Plot with LLM-based Character Simulation via Narrative Planning](STORYVERSE2024.md) | 同属抽象剧情约束加角色仿真，后者只有原型案例。 |
| [DiaryPlay: AI-Assisted Creation of Interactive Story Vignettes for Everyday Storytelling](DIARYPLAY2026.md) | 同样预定故事核心并处理玩家偏离，后者服务个人日常分享。 |
| [Elsewise: Authoring Open-Ended Interactive Narrative with Possibility Space Visualization](ELSEWISE2026.md) | 后者重点可视化不同模拟轨迹，而非提高/降低剧情抽象层级。 |
