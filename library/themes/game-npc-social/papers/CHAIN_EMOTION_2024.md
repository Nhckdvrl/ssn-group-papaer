# An appraisal-based chain-of-emotion architecture for affective language model game agents（PLOS ONE 2024）`[证据级别：完整正文]`

规范记录：`chain_emotion_2024`。Maximilian Croissant、Madeleine Frister、Guy Schofield、Cade McCall；PLOS ONE 19(5):e0301033，2024-05-10；早期预印本2023。**实读：正式PDF完整正文pp.1–18、全部正文图表；参考文献用于追溯。S1独立ZIP和OSF原始数据未完成核查，不冒充全文附属资产审计。** [正式全文](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0301033) · [PDF](https://journals.plos.org/plosone/article/file?id=10.1371%2Fjournal.pone.0301033&type=printable)

## 1. 论文形态与背景

情绪理论启发的简单LLM架构加三种评价。作者已经明确区分“角色自己的情绪”与“适应玩家情绪”，并认为不必先解决全部心理学争论才能制作有说服力的虚构人物。

## 2. 改变的前提与 idea 来源

**DOCUMENTED（§2–3）**：由appraisal与Chain-of-Thought/Generative Agents记忆得到启发，每轮先自然语言说明角色此时如何感受及为什么，再把这段情绪描述和对话一起写入历史，第二次调用生成台词。没有新增训练、固定情绪数值或多代理审议。它是新研究必须配备的**简单情绪摘要/全历史基线**，不是只有静态persona提示的旧研究。

## 3. 数据、模型、对照和结果

全部使用2023年GPT-3.5-turbo、temperature 0。实验1为42题STEU各条件一遍：无历史24/42、带前面题答31/42、appraisal提示35/42；不是42个游戏或多模型能力边界。实验2是同一个咖啡馆分手情境的固定输入，按输出句子进行LIWC分析；句子不是独立剧情。

实验3有5人pilot和**30人正式within-subject研究**，2023-07-25至08-14招募。玩家要结束恋爱、NPC想继续关系；每人体验三种条件，顺序平衡。正文一处写六次interaction，后面游戏结束规则写**8次玩家消息+8次NPC响应**，需保留此口径区别。角色外观有5,184种组合，只用于视觉随机化，不能当5,184种独立人设或情境。

CoE相对保留全历史的Memory，在“反应自然”与“对他人情绪敏感”项的报告后续检验分别为p=.05、p=.04；“响应我的输入”的显著比较只明确落在无历史条件。温暖、友好、能力、胜任均无显著差异。LIWC authenticity只在固定输入有差异，实际玩家对话未重现；玩家对话中tone有差异，不能把情感词数或LIWC分数解释成角色真正经历复杂情绪。

## 4. 报告限制与可核疑点

1个场景、1个模型、短时便利样本，没有跨会话关系发展或商业强模型复核。Table 3说明每项0–6，均值却出现6.29、6.54、6.38；不能默默修正为另一量表。方法称within-subject ANOVA，但正文报告F(2,84)、若干Welch样式自由度的后续t检验；重复测量单位、缺失数据和多重比较处理需原数据进一步确认。结论可作为初步玩家证据，数值不能作为稳定效应尺度。

## 5. 与最近邻的距离

| 近邻 | 区别 |
|---|---|
| [EMA](EMA_2009.md) | EMA有明确因果信念、可控性与应对；CoE用语言模型隐含知识生成情绪解释。 |
| [CPM-MultiAgent](CPM_MULTIAGENT_2026.md) | 后者把评价拆成多个模块；CoE已经有简单状态历史和真人演绎场景。 |
| [Dynamic Persona Coherence](../../../../workbench/game-npc-agents/knowledge/papers/DYNAMIC_PERSONA_COHERENCE_2026.md) | DPC数值状态/自评修复不等于CoE的自然语言情绪历史；比较前者不能省略后者。 |
| [角色依恋研究](CHARACTER_ATTACHMENT_2019.md) | 依恋研究区分不同关系体验；CoE主要测自然/响应/感知EI，没有证明信任、敬重、关怀等关系都改善。 |

## 6. 可迁移的研究动作与对我们

先测**普通完整历史**，再测**情绪自然语言历史**，最后才问更复杂状态或学习机制是否带来额外价值。让玩家实际扮演分歧角色，而非只阅读文本，是有价值的做法；新矿区需要扩展其人物、事件和关系跨度，同时保留表达本身可有价值、不必硬加物品任务的边界。
