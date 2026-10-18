# Player-Driven Emergence in LLM-Driven Game Narrative

规范记录：`NPC-PA03`；IEEE Conference on Games (CoG) 2024。实际版本：arXiv 2404.17027v3, 2024-06-03; CoG publication confirmed by Microsoft Research。

**实际阅读范围：** 全文正文 §I–VII，Tables I–IV、Figures 1–3文字；独立补充玩家日志未取得/未读。

[原文](https://arxiv.org/pdf/2404.17027v3) · [发表／主源信息](https://www.microsoft.com/en-us/research/project/emergence/)

**规范来源：** [Player-Driven Emergence in LLM-Driven Game Narrative](https://arxiv.org/pdf/2404.17027v3)。发表/阅读版本：arXiv 2404.17027v3, 2024-06-03; CoG publication confirmed by Microsoft Research。

**主源与范围**：[作者 arXiv v3](https://arxiv.org/pdf/2404.17027v3)，2024-06-03，正式去向由[Microsoft Research项目](https://www.microsoft.com/en-us/research/project/emergence/)核实为CoG2024。正文§I–VII、全部表I–IV与图1–3全读；未下载其独立补充玩家日志，因此不冒称逐个日志复核。

Dejaboom是TextWorld确定世界加GPT4自由语言层：六主要地点、两隐藏房、五名静态NPC，每30步爆炸重置，玩家保留知识；NPC提示含背景、性格、按序目标和揭示条件。输入先分动作/话语，动作交引擎，失败再由GPT4润色，聊天按NPC提示和游戏历史生成。28名美国RPG玩家（24男、3女、1未报）一小时单条件体验，6人拆弹成功、25人说享受，56%愿重玩；约40%提到15秒延迟，亦有失忆、重复、泄密过易。没有脚本/强模型/不同规则对照，正负体验不能归因为某一组件。

用GPT4将日志转策略DAG，与作者通关图比较得到53个新节点、43独特；表II显示这些包括能骗出情报，也包括NPC说出不可加入库存的手电筒、分散Merlin注意后偷工具仍失败。因此“涌现节点”度量是未预想的玩家策略/愿望，**不是引擎实现的新机制或可完成路径**。它的实质贡献是把玩家尝试作为设计反馈，帮助作者发现想要的对象、社会策略与路线。创意偏好相关性很弱：6名自报创意玩家仅2人产生节点；5.5个/人的最高值仅在这2名成功产生者中计算，两人也都选了掌握型，不能声称创意玩家普遍更会涌现。长期乐趣、作者据反馈改造的实际收益、不同游戏文化与模型均未验证。该文有价值地提示生成NPC可支持共同探索设计空间，同时把运行时可玩性与事后设计灵感之间的鸿沟直接暴露出来。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Conversational Interactions with NPCs in LLM-Driven Gaming: Guidelines from a Content Analysis of Player Feedback](VAUDEVILLE_FEEDBACK2024.md) | 商业玩家反馈也观察到虚构地点和角色不可靠，但数据为自选评论。 |
| [Ontologically Faithful Generation of Non-Player Character Dialogues](../../../../workbench/game-npc-agents/knowledge/papers/KNUDGE_2024.md) | 专业对话树重在设计规范与知识披露，非游玩后发现新策略。 |
| [DiaryPlay: AI-Assisted Creation of Interactive Story Vignettes for Everyday Storytelling](DIARYPLAY2026.md) | 日常故事先定关键事件，玩家偏离用于重新引导，目标不同于拆弹路线探索。 |
