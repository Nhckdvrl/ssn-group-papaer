# A Voice-Controlled Dialogue System for NPC Interaction using Large Language Models

规范记录：`NPC-PA02`；IWSDS 2025, pp.29–38。实际版本：ACL Anthology proceedings PDF。

**实际阅读范围：** 全文正文 §1–8、pp.29–37；Tables 1–2 与 Figures 1–4 的文字/说明；参考文献浏览。

[原文](https://aclanthology.org/2025.iwsds-1.4.pdf) · [发表／主源信息](https://aclanthology.org/2025.iwsds-1.4.pdf)

**规范来源：** [A Voice-Controlled Dialogue System for NPC Interaction using Large Language Models](https://aclanthology.org/2025.iwsds-1.4.pdf)。发表/阅读版本：ACL Anthology proceedings PDF。

**主源与范围**：[ACL 正式全文](https://aclanthology.org/2025.iwsds-1.4.pdf)。Wevelsiep、Walker、Wagner、Ultes，正文§1–8/pp.29–37全读，图1–4、表1–2与限制全读；参考文献扫读。

系统把“玩家以自己的话表达”与“剧情自由生成”拆开：Unity对话图维持预定义剧情；德语语音经Whisper、英译、Llama2-13B映射到简写选项或误解分支；NPC不任意生成事实。14名23–36岁德语母语者（男女各7、11名大学学历，私人关系网招募）做顺序平衡的语音与点击两次体验，游戏为帮助Felix找钥匙并关注其情绪，依共情选择进入三种结局。约90%的选项映射正确，但参与者经常接近原选项复述，这使数字不能代表任意开放语音理解。纠错按钮隐藏导致少用，也不应解读为无需纠错。

结果以描述性Likert统计为主：直接对比的乐趣均值5.43/7、自由表达5.07偏向语音；易用性3.07偏向点击，开放措辞增加认知负担，延迟、识别不确定与表情动画不足限制沉浸。沉浸正文一处写3.57，表2写4.36，应报告为原文存在不一致，不选有利数字；未见支持“显著提升沉浸”的明确组间推断检验。短时、同一剧情重复、同质小样本、先统一语音教程限制外推。该研究真正扩充的是可实现的中间设计空间：表达自由可在确定剧情结构内成立，但体验取决于纠错可见性、延迟、选项措辞与玩家愿不愿意承担表达成本，不能简化成开放生成越多越好。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Gaming with Etiquette: Exploring Courtesy as a Game Mechanic in Speech-Based Games](ETIQUETTE2024.md) | 同样有确定剧情和语音识别，后者把礼貌变成机制而非用LLM映射选项。 |
| [Dialogs with GenAI NPCs: Exploring Player Interactions with Speech Agents in a VR Game](DIALOGS_GENAI2026.md) | 改为开放Inworld生成和VR游玩，但没有点击基线。 |
| [Press A or Wave: User Expectations for NPC Interactions and Nonverbal Behaviour in Virtual Reality](PRESS_WAVE2024.md) | 手势和身体空间带来另一类可发现性/误识别成本。 |
