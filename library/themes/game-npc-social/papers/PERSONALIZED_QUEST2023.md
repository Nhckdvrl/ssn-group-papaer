# Personalized Quest and Dialogue Generation in Role-Playing Games: A Knowledge Graph- and Language Model-based Approach

规范记录：`NPC-PA21`；CHI 2023。实际版本：20-page author-hosted published-layout PDF; DOI 10.1145/3544548.3581441。

**实际阅读范围：** 全文正文 §1–8、Tables 1–11、生成示例与问卷图说明；参考文献浏览。未运行代码。

[原文](https://dragn.ai/wp-content/uploads/2023/03/Personalized_Quest_and_Dialogue_Generation_in_Role_Playing_Games.pdf) · [发表／主源信息](https://dragn.ai/wp-content/uploads/2023/03/Personalized_Quest_and_Dialogue_Generation_in_Role_Playing_Games.pdf)

**规范来源：** [Personalized Quest and Dialogue Generation in Role-Playing Games: A Knowledge Graph- and Language Model-based Approach](https://dragn.ai/wp-content/uploads/2023/03/Personalized_Quest_and_Dialogue_Generation_in_Role_Playing_Games.pdf)。发表/阅读版本：20-page author-hosted published-layout PDF; DOI 10.1145/3544548.3581441。

**来源与阅读。** Trevor Ashby、Braden Webb、Gregory Knapp、Jackson Searle、Nancy Fulda，CHI 2023，DOI 10.1145/3544548.3581441。通读 20 页作者 PDF 正文 §1–8、Tables 1–11、生成样例与问卷图说明；参考文献浏览。代码链接存在，但未运行。

**机制与可玩边界。** 玩家一句话与手建 Neo4j 中 NPC 的 need/want 关系做语义匹配，选图路径、深度约 2，再分战斗/收集/探索三种模板，GPT-2 生成任务名和介绍。所有输入都触发任务，**没有连续对话、任务执行或动态世界回写**；个性化是单次请求匹配，未学习长期玩家偏好。语言基线为 774M/355M GPT-2、82M distilled/backfill、既有 VS-MYS 与 WoW 人工任务；并无现代 instruction LLM。论文正文给训练 24,981 项，表内 medium 又写 8,638/34,450 子集，应保留数据口径不一致。

**评价与结果。** 208 名问卷参与者，200 人 18–24 岁，评价任务标题与对话流利、连贯、新颖、创造性，**不展示任务描述和独立游戏上下文**；“接近人工”主要依据 Likert 图，无等效/非劣检验。第二研究是其中 **124 人子集**，380 次输入/选择，不是新增 124 位独立玩家或 380 次游玩。比较本系统、随机 WoW 人工任务、4-gram：满意票 **125/197/58**，输入响应 **169/159/52**；整体满意度仍是人工作品更高。含 dragon 的 28 次输入中响应为本系统 21、人工 5、4-gram 2，而满意仅本系统 14 与人工 14 并列。这是事后关键词子集，不足以声称普遍玩家体验提升。

**实质启发。** 图覆盖不到输入、模板实体类型混乱（如把 gold 当击杀目标）、生成虚构地点/物件是实际失败源。词形重叠 relevance 指标复制任务能得满分，只能观察某种词汇关联，不能验证因果或世界一致性。作者也承认缺少游戏上下文让许多人只问“有任务吗”，此时人工任务的清楚冲突、可理解地点和文笔胜过机械响应输入。对领域的价值是早期把玩家意愿→状态约束→语言呈现分层连接，并明确扩展需求；其标题和结论中的沉浸/agency/共创承诺，应与实际单轮文本偏好证据严格分开。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [Ontologically Faithful Generation of Non-Player Character Dialogues](../../../../workbench/game-npc-agents/knowledge/papers/KNUDGE_2024.md) | 后者专业树和长知识约束、更强LLM，本研究仅三类任务和单句介绍。 |
| [A Framework for Exploring Player Perceptions of LLM-Generated Dialogue in Commercial Video Games](DISCO_PERCEPTIONS2023.md) | 后者原作熟悉玩家读台词，前者文本任务投票，均不等于完整游戏体验。 |
| [Player-Driven Emergence in LLM-Driven Game Narrative](PLAYER_EMERGENCE2024.md) | 后者有玩家真实执行与环境，可以暴露文本满足和可玩后果差距。 |
