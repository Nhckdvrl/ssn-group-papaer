# A Framework for Exploring Player Perceptions of LLM-Generated Dialogue in Commercial Video Games

规范记录：`NPC-PA04`；Findings of EMNLP 2023, pp.2295–2311。实际版本：ACL Anthology Version of Record。

**实际阅读范围：** 全文正文 §1–10、附录 A–G，方法、量表/界面、提示、结果统计；未运行开源界面。

[原文](https://aclanthology.org/2023.findings-emnlp.151.pdf) · [发表／主源信息](https://aclanthology.org/2023.findings-emnlp.151.pdf)

**规范来源：** [A Framework for Exploring Player Perceptions of LLM-Generated Dialogue in Commercial Video Games](https://aclanthology.org/2023.findings-emnlp.151.pdf)。发表/阅读版本：ACL Anthology Version of Record。

**主源与范围**：[ACL正式全文](https://aclanthology.org/2023.findings-emnlp.151.pdf)。Akoury、Yang、Iyyer。正文§1–10、附录A–G、全部方法表和玩家偏好图全读；没有运行网页系统。

作者从Disco Elysium提取约111万词、72,696句、110,484图节点，以Lua条件/变量/开发注释和相似台词构造遮盖填句。GPT4使用15–45个、平均33个示例，几乎填满8k上下文；这不是无提示裸模型。然而生成在实验前固定，也不依据每名玩家完整历史动态更新；附录C明确脚本提示缺少此前完整对话。评价系统执行Lua对话逻辑，但只重现核心会话，不是整个商业游戏。28名至少完成过一次英语游戏的Reddit玩家平均玩过82.6小时；先6人试用、2人观察改进界面，主研究对112个独特生成句收1,158次判断，100句至少3人评价，不能把1,158当独立场景。

玩家先选台词并解释，再看下句并允许改判。初判702/1,158（61%）偏好人工；按至少3人评价的实例多数票是人工64%、GPT4 23%、其余平，后验66%对23%。32%的生成句被至少一名玩家认为看后句后不合逻辑，不是32%的全部交互失败率。质性例子显示政治身份、同伴在场、行为语气、前后句因果十分重要，但相同句也会因玩家扮演风格不同而被合理地相反评价。结果支持“对话质量要在角色目标、后续回应和游戏语境中评价”，并不证明最新旗舰仍如此，也不能推出所有生成对话不如脚本。文中对话标注偏离游玩：要求穷尽选项；熟悉高文学性的特定游戏粉丝也限制一般化。对领域的持久贡献是状态依赖图、互动后验评价与扮演风格这三个评估维度，而不是2023模型排名。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Ontologically Faithful Generation of Non-Player Character Dialogues](../../../../workbench/game-npc-agents/knowledge/papers/KNUDGE_2024.md) | 同样来自专业RPG数据，后者测知识/任务约束与完整树生成。 |
| [Personalized Quest and Dialogue Generation in Role-Playing Games: A Knowledge Graph- and Language Model-based Approach](PERSONALIZED_QUEST2023.md) | 同样比较生成与人工文本，后者测试单句输入驱动任务。 |
| [Dialogs with GenAI NPCs: Exploring Player Interactions with Speech Agents in a VR Game](DIALOGS_GENAI2026.md) | 后者是真人现场自由语音游玩，本研究是熟悉原作玩家读替换台词。 |
