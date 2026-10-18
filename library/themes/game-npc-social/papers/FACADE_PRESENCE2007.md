# Presence and Engagement in an Interactive Drama

规范记录：`NPC-PA08`；CHI 2007, pp.1475–1484。实际版本：Author-hosted proceedings PDF; DOI 10.1145/1240624.1240847。

**实际阅读范围：** 全文正文、Table 1、图说明；参考文献浏览。未读取36小时原始录像。

[原文](https://www.cs.cmu.edu/~spdow/files/AEL-PresEngage-CHI07.pdf) · [发表／主源信息](https://spdow.ucsd.edu/research/)

**规范来源：** [Presence and Engagement in an Interactive Drama](https://www.cs.cmu.edu/~spdow/files/AEL-PresEngage-CHI07.pdf)。发表/阅读版本：Author-hosted proceedings PDF; DOI 10.1145/1240624.1240847。

**阅读身份与范围：**新读作者公开稿全部正文、Table 1 的分组及访谈分析；参考文献浏览。Steven Dow 等，CHI 2007，1475–1484。来源：https://www.cs.cmu.edu/~spdow/files/AEL-PresEngage-CHI07.pdf 。研究复用 Façade 的自主角色与婚姻冲突剧情，比较桌面键盘、桌面语音、在实体公寓内呈现角色的增强现实。语音转写及部分 AR 动作输入由研究人员代做，不能称为完整自动语音系统的性能验证。

**设计与实际发现：**12 人，各体验三版本，共 36 次、每次平均约 19 分钟；六种顺序平衡。研究以约 36 小时录像、访谈作质性分析，不是大样本量表因果检验。8 人认为 AR 最有挑战，8 人认为键盘最易用；首选为 AR 6 人、键盘 5 人、桌面语音 1 人。研究者归纳 6 名 story、4 名 meta、2 名 deserter 型参与者，这些是事后分析类别，不是随机分组或可普遍推用的玩家类型量表。更强临场感会使一部分人投入角色冲突，却使另一些人更难以夸张、恶作剧或扮演不同于自己的角色。键盘允许回看和修订输入、边听边组织话语；语音更自然的同时可能增加即时回应压力。

**领域认识与限制：**“像真人”“在场”“投入”“能自由行动”是不同目标。表现通道本身会改变同一角色系统的体验，不能把新模型或自然输入的效果全部归给智能水平。玩家还会用戏剧情境解释程序异常；这既说明解释空间有设计价值，也不能把容错式理解当作系统正确率。样本小、场景特殊、体验短、Wizard 输入减少了真实识别错误；没有证明 AR 或语音普遍优于键盘。应保留其机制与设计观察，避免拿它支持现代 LLM 的通用提升。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Press A or Wave: User Expectations for NPC Interactions and Nonverbal Behaviour in Virtual Reality](PRESS_WAVE2024.md) | 后来的VR期待研究同样表明真实互动必须配合可读性和玩家控制。 |
| [A Voice-Controlled Dialogue System for NPC Interaction using Large Language Models](VOICE_CONTROLLED2025.md) | 用可点击/语音选项比较补小样本定量，但剧情及动作空间不同。 |
| [Dialogs with GenAI NPCs: Exploring Player Interactions with Speech Agents in a VR Game](DIALOGS_GENAI2026.md) | 在VR中引入生成模型，不能把新颖和沉浸自动归因于生成组件。 |
