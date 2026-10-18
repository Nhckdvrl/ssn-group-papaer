# 人物、情绪、记忆和关系怎样随时间变化

更新：2026-10-18。人物并不是一个固定标签：身份、价值、知识、短时情绪、当下目标、对他人的关系和身体表达可能按不同速度变化。研究应解释这些变化怎样发生、怎样被作者控制及玩家理解，而不把“越稳定越好”当统一目标。

## 1. 四种现象必须分开

| 现象 | 可以合理发生的情况 | 需要证明的问题 |
|---|---|---|
| 身份／价值持续 | 职业、背景、核心立场在无关输入下保持 | 无依据丢失、互相矛盾，是否跨情境影响表现 |
| 合理成长与关系变化 | 经真实经历、获知信息、任务进展后改变信任或目标 | 变化是否有来源、幅度合适、能被人物与玩家理解 |
| 短时情绪和表达波动 | 受挫、惊喜、疲劳、语境和身体信号变化 | 是否与事件和人物相合，而非把波动本身算漂移 |
| 非合意漂移或污染 | 玩家声明被误当历史、错误摘要固定了新身份 | 来源／权限错误怎样持续并影响后续行为和关系 |

这个区分连接[角色／用户个性化综述](../../../library/themes/game-npc-social/papers/TWO_TALES_PERSONA_2024.md)、[动态人格](papers/DYNAMIC_PERSONA_COHERENCE_2026.md)与[同伴体验](../../../library/themes/game-npc-social/papers/COMPANIONS_DISSERTATION2019.md)。适应玩家与保持独立人物也可能同时有价值。

## 2. 传统情绪和社会架构提供了什么

[EMA](../../../library/themes/game-npc-social/papers/EMA_2009.md)把情绪看作对因果信念、目标重要性、可控性和应对策略的评价过程。它不是让角色多使用正面词语；同一事件可因不同信念和目标引发不同情绪，后续应对又更新解释。[FAtiMA Modular](../../../library/themes/game-npc-social/papers/FATIMA_MODULAR_2014.md)进一步把通用评价与应用情境拆开，[Toolkit](../../../library/themes/game-npc-social/papers/FATIMA_TOOLKIT2022.md)让作者编辑知识、目标、情绪与社会决策。其模型或应用存在不代表心理学上已全面验证。

[PsychSim](../../../library/themes/game-npc-social/papers/PSYCHSIM_2005.md)用决策理论和嵌套他人模型连接信念、动机与社会影响；[Talk of the Town](../../../library/themes/game-npc-social/papers/TALK_OF_TOWN_2015.md)让角色观察、转述、误记和说谎，保存信息传播来源。它们提醒记忆不只是向量检索：谁见过、谁告诉谁、哪种内容是猜测，以及如何修正，会改变角色互动。

Generative Agents把记忆、反思和计划用于小镇社会模拟，是LLM长时角色的重要基础；前轮完整正文与关键消融也记录了采访式评价、部分物体状态由LLM更新及过度接受邀请等边界。[原阅读](FIELD_REVIEW_2026-10-18.md#4-角色行为与社会模拟从文本像人到可核后果)

## 3. 本轮新证据怎样改变“动态人格”判断

[Beyond Static Persona Consistency](papers/DYNAMIC_PERSONA_COHERENCE_2026.md)明确区分稳定身份和适应性状态，是应保留的方向贡献。但其Vanilla每轮只得到人物、当前事件和固定5.0初始状态，没有历史响应或状态记忆。加入累计状态的收益不能证明正常保留历史的强商业模型仍普遍不会情绪累积。

原文PCC定义与若干表格汇总还存在需澄清的不一致；不能仅凭接近满分的结果认定心理状态模型充分有效。这里区分作者提出的概念、相对该基线的效果，以及尚未排除的普通记忆解释。具体数值和附录位置保留在单篇卡。

[Persona Dynamics / PANDA](papers/PERSONA_DYNAMICS_ACL2025.md)研究人格属性在文本游戏中的作用；[Agent Sociodrama](papers/AGENT_SOCIODRAMA_2026.md)根据社会动态与任务诊断重选团队人格配置并重开任务；[CDT](papers/CDT_2026.md)从故事提取角色逻辑。这些分别关注属性—行为、团队角色与人物决策，不应拼成一个“人格成长已解决”的叙事。

[InCharacter](../../../library/themes/game-npc-social/papers/INCHARACTER_2024.md)、[CharacterEval](../../../library/themes/game-npc-social/papers/CHARACTEREVAL_2024.md)的静态量表／文本评价可用于某些身份维度，但不能直接判成长。[CoSER](papers/COSER_2025.md)和[HER](../../../library/themes/game-npc-social/papers/HER_2026.md)增加情境、动机和思想，同样主要在文本演绎中验证。将这些方法接到可执行角色时，语言、动作、关系、作者和玩家读数仍须分别连接。

## 4. 关系和身体表达如何进入玩家体验

同伴研究显示玩家重视人物自己的目标、独特性和关系发展，同时厌恶挡路和反复保护弱队友。它提供设计压力，不证明某一种记忆模块能解决。[237人研究的作者改写章](../../../library/themes/game-npc-social/papers/COMPANIONS_DISSERTATION2019.md)

[情绪镜像试验](../../../library/themes/game-npc-social/papers/AFFECTIVE_MIRRORING2025.md)中理想人控镜像更受欢迎，而自动镜像受自然表情识别限制；机械模仿玩家表情也可能抹去角色独立情绪。[VR互动研究](../../../library/themes/game-npc-social/papers/PRESS_WAVE2024.md)与[语音NPC研究](../../../library/themes/game-npc-social/papers/DIALOGS_GENAI2026.md)说明视线、距离、打断、发音和回应时序会改变玩家对人物的归因。文本人格不是身体表现的充分代理。

## 5. 可形成一般认识的问题

什么事件应改变哪个人物层次？同一历史下，状态更新、简单摘要、全历史提示和显式社会模型有何差异？为了防漂移而加入的纠正是否抹掉了合理成长？人物变化能否预测未见情境的行为，也能被玩家理解而非只被评委识别？知识来源错误怎样沿关系传播，又怎样被更正？

这些问题可以支持训练、记忆／表示、因果分析、作者工具或玩家研究；不必一律做新的“漂移benchmark”。仍需补完整RoleBreak／ArcANE等已有摘要、更多原生行为人格、跨会话长期玩家、多语言文化及联合语音／身体证据。[角色综述](../../../library/themes/game-npc-social/papers/OSCARS_SURVEY_2025.md)和[广域总账](READING_CATALOG.md)只是继续追原文的入口，不代替这些阅读。
