# Orchid-Creator: An Authoring Tool Supporting LLM-Driven Interactive Narrative Creation

规范记录：`NPC-PA14`；CHI 2026。实际版本：23-page author-hosted Version of Record; DOI 10.1145/3772318.3791426。

**实际阅读范围：** 全文正文 §1–10、两用户研究与六个月案例，图表统计文字；未逐像素读取箱线图，未取得原始研究数据。

[原文](https://xrim.hkust.edu.hk/static/publications/orchid-creator/3772318.3791426.pdf) · [发表／主源信息](https://xrim.hkust.edu.hk/static/publications/orchid-creator/3772318.3791426.pdf)

**规范来源：** [Orchid-Creator: An Authoring Tool Supporting LLM-Driven Interactive Narrative Creation](https://xrim.hkust.edu.hk/static/publications/orchid-creator/3772318.3791426.pdf)。发表/阅读版本：23-page author-hosted Version of Record; DOI 10.1145/3772318.3791426。

**阅读身份与范围：**新读正式 23 页 PDF 全部正文 §1–10，方法、Figure 10 统计说明和六个月案例；不把图片里的未提取数值冒称逐项读取。https://xrim.hkust.edu.hk/static/publications/orchid-creator/3772318.3791426.pdf ；DOI 10.1145/3772318.3791426。

**机制和研究：**卡片定义世界、角色、事件、叙述方式、输入和全局变量，组成故事图；GPT-4o 生成叙事，GPT-3.5-turbo 从文本更新布尔/数量/语义变量，再用确定条件转场。有 RAG、历史、回退和测试界面，但变量真值仍靠模型读文本，不能称为独立物理世界核验。研究一 8 位相关领域创作者；研究二招 20 人、统计排除 1 人（跨条件评分过于相似），实际 N19，Latin square 顺序对比 Twine/AI Dungeon。三工具平均体验 30/20/40 分钟，而且 Orchid 有 Zoom 研究者支持，基线自行录屏；模型能力和支持时长并未匹配。

**正负结果：**结构试验、部分创造力/控制和回报评分较好，叙事连贯性没有显著差异。不能引用摘要把“更连贯”写成已验证结论，也不宜反复引用正文前后不一的均值。六个月与一位艺术家共同制作的 Let the Monsters Speak 更接近真实创作：约二十轮迭代、明确角色、拆小阶段、缩减复杂输入才稳定。展览 23 名完成者作答，15 觉得有惊喜/愿重玩，只有 11 觉得连贯流畅；不是全体访客转化率或受控玩家收益。

**领域意义：**工具带来结构、试验与创作新形式，同时会限制创作者：艺术家放弃实体积木与手势，转向系统较能支持的自然语言。玩家要求线索逐步累积、各 NPC 观点有联系、性格有区分，不能仅靠很多开放回答。案例为制作研究提供真正正反面证据；多模态输出、引擎整合、长篇质量与专业工作流仍欠验证。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Elsewise: Authoring Open-Ended Interactive Narrative with Possibility Space Visualization](ELSEWISE2026.md) | 两者都有作者可控LLM叙事，后者着重模拟轨迹可视化和预测。 |
| [WhatELSE: Shaping Narrative Spaces at Configurable Level of Abstraction for AI-bridged Interactive Storytelling](WHATELSE2025.md) | 后者以示例/抽象/变体组织空间，本工具以卡片/事件变量组织。 |
| [Towards Explainable Social Agent Authoring Tools: A case study on FAtiMA-Toolkit](FATIMA_EXPLAINABLE2022.md) | 共享作者心智模型问题，显式配置界面不等于作者理解运行原因。 |
