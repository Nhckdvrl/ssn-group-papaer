# Dramamancer: Interactive Narratives with LLM-powered Storylets（UIST Adjunct 2025，Demo）

**证据级别：完整短稿；非主会完整研究论文。** Tiffany Wang、Yuqian Sun、Yi Wang、Melissa Roemmele、John Joon Young Chung、Max Kreminski。正式 demo DOI [10.1145/3746058.3758995](https://doi.org/10.1145/3746058.3758995)，UIST Adjunct 2025，5 页；实际读[作者正式版 PDF](https://johnr0.github.io/assets/publications/UIST25-dramamancer-demo.pdf)全部正文、8 幅图说明、参考文献，视觉核对 pp.2–4 界面。另读 [Wordplay 2025 三页设计短稿](https://mkremins.github.io/publications/Dramamancer_Wordplay2025.pdf)全部 §1–5 和参考文献。阅读日期：2026-10-19。

**版本去重。** 同题 *Design Techniques for LLM-Powered Interactive Storytelling: A Case Study of the Dramamancer System* 的 [arXiv:2601.18785v1](https://arxiv.org/pdf/2601.18785v1)，2026-01-26，再存三页稿与 Wordplay 版本提取正文逐行相同，仅增加 arXiv 水印。本卡合并系统及设计短稿，**不增加一篇“2026 最新完整研究”或一组独立实证**。

## 1. 论文形态与背景压力

系统 demo 与设计反思。作者希望用自然语言表达作品边界，玩家希望以自然语言行动；模型在两者交集中生成作品，而非要求作者逐句穷举。

## 2. 改变的前提

保留作者可表达、可编辑的 storylet/场景结构，同时将玩家自由文本映射为事件触发及故事演绎。作者和玩家是两个有不同权限的角色，玩家输入主要代表故事内人物行动。

## 3. Idea 来源

**DOCUMENTED：**storylet、Drama Llama、AI-bridged authoring 与 WhatELSE。三页稿提出评价角度，未验证新评价量表。**RECONSTRUCTED：**作者控制、事件正确触发、叙事实际表达以及玩家输入时机应分别观察。

## 4. 系统机制

作者定义视觉/文本风格、角色、场景、固定开场白和事件。事件可根据自然语言条件触发，也可在指定玩家回合数后发生；效果可留在场景、换场景或结束。作者可获取条件建议，玩家可获取行动建议。内部图像生成是作者资产制作功能，不能当作玩家叙事效应证据。

三页稿补充两模块：每次玩家输入后，interpretation 判断当前场景全部事件条件；instantiation 根据历史、角色、设置和触发结果产生下一行及是否暂停等玩家输入的布尔值。结果可跨多行自然表达；即使没触发事件，也要求响应玩家。明确要求不代写玩家角色行动。不是形式验证的世界模拟器。

## 5. 数据与证据

正式 demo 报告内部已积累 **8 位作者的 15 个互动故事**，含少量模板。这是内部部署规模，论文未报告随机作者比较、独立玩家人数、长期体验效果、负担节省或触发准确率。三页稿中的作者风格/角色/场景/事件/结果以及玩家响应/时机/反思/投入指标均为评价建议，**没有新实验结果**。运行模型具体名称未清楚报告。

## 6. 重要限制

论文直接宣称兼顾控制/能动性及减少作者负担，其设计确实实现相关可操作接口，但经验性效果尚未得到本文对照验证。时间事件保障推进，也可能减少玩家改变节奏的能力，需按作品目标检查。与 Drama Llama 同研究脉络，不能作为两份相互独立的玩家价值证据。未核得公开评审分数。

## 7. 与最近邻的距离

| 近邻 | 区别 |
|---|---|
| [Drama Llama](DRAMA_LLAMA_2025.md) | 前序 trigger/action 架构与 6 作者研究。 |
| [StoryAssembler](STORYASSEMBLER2019.md) | 明确状态与重规划的故事片段系统，有完整作品制作案例。 |
| [WhatELSE](WHATELSE2025.md) | 用抽象纲要和变体支持作者塑造叙事范围。 |
| [Bonsai](BONSAI_2026.md) | 不把发布后输出视为一次性材料，持久保存分支、编辑及规则。 |
| [共同创作视角历史](COAUTHORSHIP_EMERGENT_NARRATIVE_2021.md) | 提醒区分玩家作为角色与作者的创作权限。 |

## 8. 可迁移的研究动作

把作者 UI、运行规则、玩家输入权限与效果证据分开；真实考察“何时暂停让玩家介入”；让作者看到意外触发而非只看到好看的最终故事。

## 9. 对矿区 C

完整自然语言导演/场景/storylet 已存在，是必须认真构造的普通系统参照。潜在贡献不能停在同类界面拼装；需要解释作者、人物与玩家如何共同改写作品，以及哪种可控性支持了有价值的意外。本轮未调用其服务或运行实验。
