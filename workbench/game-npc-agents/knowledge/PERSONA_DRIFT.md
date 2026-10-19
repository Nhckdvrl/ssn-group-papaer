# 人物、情绪、记忆和关系怎样随时间变化

更新：2026-10-19。人物不是固定标签。身份、价值、知识、当前目标、短时情绪、关系与表演会相互影响，也可能以不同节奏变化。这里把“漂移”放回更广的研究问题：**哪些变化有来由、符合人物与创作意图，哪些变化源于信息错误或失去约束，以及作者和玩家怎样理解与回应它们。** 本页为知识维护，不改变实验或研究状态。

## 1. 先区分变化的对象与来源

下表是分析区分，不预设角色必须遵循固定心理层级，也不要求每层各有一个分数。

| 对象／来源 | 可以合理发生的变化 | 容易混淆的问题 |
|---|---|---|
| 身份与价值 | 人物保有可辨认的背景、习惯和在乎的事；创作修订或故事经历也可改变部分价值 | 维持最初每句话，不等于保持人物；变化也不自动等于成长 |
| 知识与信念 | 根据亲历、传闻、猜测或新证据改变理解，甚至合乎角色地误解 | 世界事实、NPC所知、NPC说法与作者新设定不相同 |
| 当前目标与处境 | 在疲劳、危险、不同对象或场合中调整注意、计划与应对 | 行为不同不必是人格变化；目标变化也不必是情绪波动 |
| 情绪、调节与表达 | 愤怒、惊喜、忧虑，及重评、克制、隐藏、表达或寻求支持 | 内部感受、应对策略、身体/语言表达不能合成一个标签 |
| 对特定他人的关系 | 信任、尊重、亲近、熟悉与边界因经历和解释改变 | 暂时生气不必失去信任；信任也可能因一条关键反证迅速恢复 |
| 人物成长 | 逐渐理解自己、重新选择目标、改变对他人的态度或相处方式 | 不应只允许唯一发展弧，也不预设每次互动都需永久改变人物 |
| 作者修订与重新理解 | 作者纠正表演、改写人物，或接受试演启发的新解释 | 世界内人物成长与创作层修改不同；新增设定不必全是污染 |
| 非合意漂移／信息污染 | 无关输入、错误摘要或无权声明覆盖了人物和历史 | 需要指出违反了什么事实、约束或创作契约，不能只统计与初始设定的距离 |

[角色／用户个性化综述](../../../library/themes/game-npc-social/papers/TWO_TALES_PERSONA_2024.md)区分角色化与用户适应；[ArcANE](../../../library/themes/game-npc-social/papers/ARCANE_2026.md)把人物阶段纳入评价；[ORIBA](../../../library/themes/game-npc-social/papers/ORIBA_2025.md)则给出作者通过试演修改、延展自己人物的使用证据。**作者原本认可的表演、作者被启发后接受的表演、玩家对人物的解释，应分别记录**，而不是事后悄悄改写唯一标准答案。

## 2. 情绪、关系与可解释变化有长期前史

[EMA](../../../library/themes/game-npc-social/papers/EMA_2009.md)把情绪联系到因果信念、目标重要性、可控性与coping；同一事件可因人物理解和目标不同而引发不同情绪，应对又会改变理解或行动。[FAtiMA Modular](../../../library/themes/game-npc-social/papers/FATIMA_MODULAR_2014.md)组织评价、情绪与社会认知，[Toolkit](../../../library/themes/game-npc-social/papers/FATIMA_TOOLKIT2022.md)提供作者编辑入口。理论模型或工具存在不等于心理学上已全面验证，作者工具可用也不等于真实游戏收益已经确证。

本轮补读的[OSSE／Ochs等2009](../../../library/themes/game-npc-social/papers/OSSE_SOCIOEMOTION_2009.md)已经区分触发情绪、当前情绪和表达情绪，维护非对称的喜欢、支配、熟悉与相似感，并用情绪来源和已有关系影响更新。关系到极端时更难改变也已有数值实现。因此，**状态记忆、衰减、有向关系和情绪—关系联动本身不能被写成新问题**。

OSSE也明确留下了边界：动作默认有意，目标、意图、记忆与事件推断主要外置；不同意图需作者拆成不同动作，行为与表达选择尚未完整验证，证据仅为两个手写情景。[Emotional Appraisal Engines for Games](../../../library/themes/game-npc-social/papers/APPRAISAL_ENGINES_2016.md)整理了另一类偏通用引擎/作者接口的路线。它是一篇主题书章，不是系统性综述；简单接口仍需有人提供角色在乎什么、事件意味着什么。

[PsychSim](../../../library/themes/game-npc-social/papers/PSYCHSIM_2005.md)用他人模型连接信念、动机与社会影响；[Talk of the Town](../../../library/themes/game-npc-social/papers/TALK_OF_TOWN_2015.md)记录观察、转述、误记和说谎的来源。由此形成的持续问题是：**谁见过、谁告诉谁、什么是推测、后来怎样重新理解，以及这些变化怎样影响对人的判断。** 记忆检索是一部分，不能代表全部关系过程。

## 3. LLM新证据：合理变化已被研究，复杂机制仍需强参照

[Beyond Static Persona Consistency](papers/DYNAMIC_PERSONA_COHERENCE_2026.md)明确区分稳定身份与适应性状态，方向值得保留。但其Vanilla没有历史响应或状态记忆，每轮回到固定初始状态；加入累计状态的收益不能证明正常保留历史的强商业模型仍普遍不会情绪累积。PCC定义与表格汇总还有需澄清之处，详细审计留在唯一论文卡。

[ArcANE](../../../library/themes/game-npc-social/papers/ARCANE_2026.md)进一步比较同一人物在小说不同阶段的回应，已经直接研究“在正确时间像这个人物”。它提供的是从原作取得、截至当前阶段的发展信息；不等于玩家改变经历后形成尚未预写的成长机制。短ArcHint对两个基础模型接近完整发展弧，真正盲评又只覆盖一个角色；不能由自动阶段分数推成普遍的玩家关系收益。

[Chain-of-Emotion](../../../library/themes/game-npc-social/papers/CHAIN_EMOTION_2024.md)用完整历史加一次自然语言“感受与原因”更新，已有短时真人角色扮演证据；这是一种需要认真对待的普通两步系统。[CPM-MultiAgent](../../../library/themes/game-npc-social/papers/CPM_MULTIAGENT_2026.md)在强GPT-5.4上与普通提示、单体CPM比较，数值增量很小，人评对理由的偏好强于对情绪状态的偏好；尚未连接到真实游戏互动效果。两篇都不能只被概括成“多做内心推理有用”。

[MDRP](../../../library/themes/game-npc-social/papers/MEMORY_DRIVEN_ROLEPLAY_2026.md)以处境分面组织人物资料与固定历史，强底座上几乎没有均分增量。它不做在线记忆维护，却构成重要参照：收益可能来自信息完整或组织清楚，而不是新状态结构。[EmoLLM](../../../library/themes/game-npc-social/papers/EMOLLM_2026.md)则将评价与模拟用户后果用于训练；其主要奖励偏向用户积极情绪，商业对照限mini/nano/flash档，不能直接用于判断有自身意愿的NPC或复杂关系。

[Persona Dynamics／PANDA](papers/PERSONA_DYNAMICS_ACL2025.md)、[Agent Sociodrama](papers/AGENT_SOCIODRAMA_2026.md)、[CDT](papers/CDT_2026.md)分别研究属性—行为、团队人格配置调整与从故事归纳人物逻辑；[CoSER](papers/COSER_2025.md)和[HER](../../../library/themes/game-npc-social/papers/HER_2026.md)丰富情境、动机与思想。它们不应被拼成“人格成长已解决”，也不该被忽略后重新命名为同一种新方法。

## 4. 合理变化有依据，但不总有唯一正确轨迹

人物可能嘴硬、犹豫、误认、隐藏善意，作者也可能欢迎未预想到的表达。[RoleBreak](../../../library/themes/game-npc-social/papers/ROLEBREAK_2025.md)已经指出角色保持与当前提问的冲突，并允许叙事补写；其补写没有经过游戏世界事实确认。因此需要同时分清：有意虚构或世界内说谎、合意的共同创作，以及模型为了迎合输入而改写既定过去。统一拒绝和无限补写都不能替代这一区分。

[CoRE最新v3](../../../library/themes/game-npc-social/papers/CORE_EMOTION_CONCEPTS_2026.md)通过假设情境下的认知评价，发现模型的同类情绪表征更集中、不同情绪更易分开。其人类招募72人、过滤后有效41人；比较的是美国英语样本、跨情境的外显评价结构，不是神经结构、真实感受或游戏NPC表现。分类更清楚也可能适合某种风格化人物，不能直接判定“越像平均真人越好”。

对知识库的实际修正是：**把事件/知识与人物约束作为依据，保留多个合理解释，并观察哪个解释适合作者意图和玩家活动。** 这不等于给所有随机变化找借口；故意限定单一发展方向的作品也有其创作目标。[InCharacter](../../../library/themes/game-npc-social/papers/INCHARACTER_2024.md)、[CharacterEval](../../../library/themes/game-npc-social/papers/CHARACTEREVAL_2024.md)的量表与文本评价，可服务于部分人物维度，但不能单独判断合理成长、表演价值或关系是否成立。

## 5. 关系与表演怎样进入实际体验

[同伴研究](../../../library/themes/game-npc-social/papers/COMPANIONS_DISSERTATION2019.md)提供人物自主目标、独特性、关系发展与避免妨碍游玩的设计压力。[角色依恋研究](../../../library/themes/game-npc-social/papers/CHARACTER_ATTACHMENT_2019.md)显示保护、认同、信赖与敬重对手等多种关系意义，不能合成“更喜欢NPC”。其七种形式是质性主题，不是经验证的七维量表，也不是生成NPC干预结果。[Tali/Garrus研究](../../../library/themes/game-npc-social/papers/NPC_ATTACHMENT_MASS_EFFECT_2020.md)记录玩家为了关系意义调整游玩和补写角色生活；大量粉丝回复既不是同量独立人数，也不是按人前瞻追踪的长期研究。

[Bickmore与Picard2005](../../../library/themes/game-npc-social/papers/RELATIONAL_AGENTS_2005.md)提供一个月跨会话随机比较：脚本、菜单、历史引用和多模态关系行为，改善了部分bond、喜欢和继续互动意愿。**它是健康运动教练研究，不是玩家关系研究；继续互动意愿不是实际留存，关系条件也未显示总体运动行为优势。** 它说明关系价值不必等待生成模型才出现，同时没有证明开放NPC长期成长已解决。

角色的内部情绪与表达可以不同；玩家本人、玩家所扮演角色和NPC也可能各有不同情绪。对情绪的克制、掩饰和复杂表达，应结合交流目的来理解，不能要求所有模态永远显示同一个标签。[OSSE](../../../library/themes/game-npc-social/papers/OSSE_SOCIOEMOTION_2009.md)已有felt/expressed区分；[情绪镜像试验](../../../library/themes/game-npc-social/papers/AFFECTIVE_MIRRORING2025.md)的10人先导主要支持人控条件与语境适切性，自动镜像效果很有限，机械复制还可能削弱人物独立性。

[IVA2018口语情绪系统](../../../library/themes/game-npc-social/papers/SPOKEN_EMOTION_2018.md)的全文债已补：小样本开启情绪条件使用更久，但信息解锁规则也随之改变，不能把时长单独当投入。[VR互动](../../../library/themes/game-npc-social/papers/PRESS_WAVE2024.md)和[语音NPC](../../../library/themes/game-npc-social/papers/DIALOGS_GENAI2026.md)进一步提示声音、空间、打断和时序的重要性。角色表达与关系感本身可以有价值，不必一律转成任务成功；声称内部机制有效时，又必须连接到玩家实际能感知的表达、应对或互动。

## 6. 进入研究时应排除哪些普通解释

以下是未来比较原则，**本轮未运行比较**。先给强商业模型同等人物资料、已知世界状态、完整历史、可靠摘要/检索与普通工具反馈；再比较自然语言appraisal、处境分面、短阶段提示、单体CPM和普通复核。成熟脚本／有限状态关系系统也应得到同质量表达层与事件信息。不能以缺历史、缺目标或较弱模型的错误，替新机制证明必要性。[Chain-of-Emotion](../../../library/themes/game-npc-social/papers/CHAIN_EMOTION_2024.md)｜[CPM](../../../library/themes/game-npc-social/papers/CPM_MULTIAGENT_2026.md)｜[MDRP](../../../library/themes/game-npc-social/papers/MEMORY_DRIVEN_ROLEPLAY_2026.md)｜[OSSE](../../../library/themes/game-npc-social/papers/OSSE_SOCIOEMOTION_2009.md)

如果显式状态改善的只是内部评分，最终表演没有变化，不能声称玩家体验增量；如果移除状态后仍表现良好，也可能是完整历史已能重新推断。应分辨额外信息、压缩记忆、解释清晰度和真正的状态控制作用。若普通强系统已经足够，就承认方法空间缩小；角色创作、合理变化的测量与玩家体验仍可能产生不同形态的新认识。

可继续问：什么新证据会改变哪个人物判断？暂时情绪与持久关系何时分开？作者改写与世界内成长如何协调？防漂移会不会抹掉合理惊喜？同一历史为什么允许多种可信表演？玩家能否理解自己对角色的影响？这些问题可支持训练、表示、因果分析、作者工具或玩家研究，不必一律做新的“漂移benchmark”。

## 7. 对应矿区与后续阅读

| 矿区 | 本页向其连接的独立问题 |
|---|---|
| [B：可塑造、可延展的角色扮演](../mine-b-character-enactment/README.md) | 作者怎样创造、修订并重新理解人物；变化怎样成为可辨认的表演 |
| [D：可理解的情绪与关系演变](../mine-d-affect-relationships/README.md) | 事件评价、应对/调节、表达意图与共同经历怎样改变具体关系 |
| [C：共同改写的叙事](../mine-c-shared-narrative/README.md) | 人物与关系变化怎样参与故事的共同发展与改写 |
| [E：玩家可理解的互动自由](../mine-e-player-agency/README.md) | 玩家怎样发现、理解、预期并回应这些互动与变化 |

四个矿区共享经历和解释来源，但不需要各建一套互相矛盾的状态或重复任务。当前均为知识／问题矿区，未进入实验立项。

RoleBreak与ArcANE已经补读正文，旧的“仅摘要”阅读债在此撤下。仍需补系统性appraisal／emotion regulation理论综述、人物创作长期实践、真实跨会话玩家关系、非亲密关系、多语言文化和联合语音／身体证据；单一书章、粉丝回忆或短时模型评价不能替代这些工作。[广域角色综述](../../../library/themes/game-npc-social/papers/OSCARS_SURVEY_2025.md)与[阅读总账](READING_CATALOG.md)提供继续追索入口，不作为领域阅读完成的证明。
