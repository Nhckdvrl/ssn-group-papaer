# Dialogs with GenAI NPCs: Exploring Player Interactions with Speech Agents in a VR Game

规范记录：`NPC-PA19`；International Journal of Human–Computer Interaction; online 2026-02-02。实际版本：Published online PDF; DOI 10.1080/10447318.2026.2620647; implementation dates May–July 2023。

**实际阅读范围：** 全文正文 §1–8、Table 1、图表结果说明、Limitations；参考文献浏览，外部补充问卷/编码本未读。

[原文](https://ris.utwente.nl/ws/portalfiles/portal/522572838/Dialogs_with_GenAI_NPCs_Exploring_Player_Interactions_with_Speech_Agents_in_a_VR_Game.pdf) · [发表／主源信息](https://ris.utwente.nl/ws/portalfiles/portal/522572838/Dialogs_with_GenAI_NPCs_Exploring_Player_Interactions_with_Speech_Agents_in_a_VR_Game.pdf)

**规范来源：** [Dialogs with GenAI NPCs: Exploring Player Interactions with Speech Agents in a VR Game](https://ris.utwente.nl/ws/portalfiles/portal/522572838/Dialogs_with_GenAI_NPCs_Exploring_Player_Interactions_with_Speech_Agents_in_a_VR_Game.pdf)。发表/阅读版本：Published online PDF; DOI 10.1080/10447318.2026.2620647; implementation dates May–July 2023。

**来源与阅读。** Zargham 等，IJHCI，2026-02-02 在线，DOI 10.1080/10447318.2026.2620647。通读正式开放 PDF 正文 §1–8、Table 1、图表文字说明；参考文献浏览，外部补充问卷/编码本未读。实现时间是 **2023 年 5–7 月**，并非测试 2026 年前沿模型。Inworld 包办 ASR、记忆、生成，底层模型和语音设置未公开。

**任务与方法。** Office Whispers 为 Unity/Quest 2 办公室解谜，4 个静止 NPC、10 道谜题，自由语音询问与拾取物件，进度清单标出完成任务；NPC 不能彼此交谈，也不具完整实时世界状态接入。两版本交换 NPC 的性别/声音与职位映射，保留基本兴趣与人物动机。**N=48**（加拿大 20、荷兰 28；21 男、26 女、1 diverse，平均 23.58 岁），便利招募、每人 20 分钟。不是 LLM 对规则系统、语音对文字或 VR 对桌面的比较。先导另有 2 人，用来将回答限到 50 字；访谈录音损坏 2 人，实际质性样本 **46**，正文部分百分比仍除以 48。

**结果。** 所有 PXI 均值高于中点；总体体验 5.75/7、愿玩同类 5.73/7。性别映射版本各 PXI 差异不显著，BF10 0.29–1.41 是弱证据范围，不等于证明等效。未记录客观解谜成功率或完成时间。37 人报告语音识别问题，24 人把问题归因自身口音/发音；13 人提及虚构信息妨碍进展，14 人批评无用回答，16 人喜欢自由表达；6 人反而享受不确定性。喜欢角色的理由常为有帮助/友好，也有 3 人喜欢说谎、2 人喜欢诚实。角色吸引力与交互享受相关，但外观、声音、响应质量等未分别控制，不能作外貌因果论。

**解释与边界。** 主要贡献是把语音自由、角色社会归因、任务可用性、身体动作和交互修复放在真实短时游玩中观察。ASR 把办公室词误听为船航词后，角色持续采用海盗口吻，说明输入错误会累积为人格偏移。玩家需要接话、插话、主动性、位置/过去行为感知；部分人又有意省掉寒暄迅速推进。它支持“社会体验与功能可靠性共同构成人物评价”，未证明生成式语音因果提升 agency/沉浸，更不能由两站点差异推断文化差异或商业留存。模型未公开、实现老旧、无性能基线，使其适合作为交互设计证据，不能用于判定当前商业模型技术上限。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Press A or Wave: User Expectations for NPC Interactions and Nonverbal Behaviour in Virtual Reality](PRESS_WAVE2024.md) | 玩家对身体/空间行为的期待可解释本研究静止角色的失配。 |
| [Gaming with Etiquette: Exploring Courtesy as a Game Mechanic in Speech-Based Games](ETIQUETTE2024.md) | 早期规则语音办公游戏有礼貌开关控制；本研究没有生成性开关。 |
| [Conversational Interactions with NPCs in LLM-Driven Gaming: Guidelines from a Content Analysis of Player Feedback](VAUDEVILLE_FEEDBACK2024.md) | 商业评论显示类似幻觉与进展问题，但无法直接比较发生率。 |
