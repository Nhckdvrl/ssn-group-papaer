# 角色学习与评价：人物知识、表达与情境表现

更新：2026-10-18。主要依据本轮角色综述、训练、评价论文的完整正文与指定关键附录；每项的版本和边界见[阅读总账](READING_CATALOG.md)。这里把角色表达当作NPC领域的一条重要研究线，同时保留其与动作、叙事和玩家体验的接口。

## 1. 先分开六种能力

| 能力 | 实际要回答的问题 | 不充分的替代证据 |
|---|---|---|
| 人物知识 | 记得原作／作者提供的哪些事实，未知时是否守住边界？ | 名字识别、口头禅、常识题总分 |
| 人物表达 | 语言风格、态度、关注点能否让人辨认角色？ | 任意讨喜、共情或有礼貌的回答 |
| 原创人物泛化 | 作者新建人物能否在给定资料与可接受适配成本下体现设定，并支持后续编辑？ | 只用预训练已知小说人物留出测试 |
| 情境决策 | 人物目标、私有信息和关系能否改变选择？ | 给出事后理由或量表自报 |
| 长程变化 | 经历如何形成可追溯记忆、情绪和关系更新？ | 将所有波动惩罚掉，或凭几轮自聊称长期稳定 |
| 可玩表现 | 玩家能辨认、理解人物，并在行动、情感或角色扮演中作出回应吗？ | LLM裁判给出“像角色”“有趣”的高分 |

[The Oscars of AI Theater](../../../library/themes/game-npc-social/papers/OSCARS_SURVEY_2025.md)提供数据、训练、架构与评价全流程分类；[Two Tales](../../../library/themes/game-npc-social/papers/TWO_TALES_PERSONA_2024.md)提醒角色是模型的人物，个性化则可能是用户画像，两者优化对象不同。[RPA评价综述](../../../library/themes/game-npc-social/papers/RPA_EVALUATION_SURVEY_2025.md)把模拟对象属性与下游任务分开，但明确排除有限动作空间，因此不能照搬成NPC全景。

## 2. 数据与训练是怎样演进的

**从角色简介到角色经历，再到共享角色模型。** [Character-LLM](../../../library/themes/game-npc-social/papers/CHARACTER_LLM_2023.md)把人物资料扩展为合成生活片段、思想、行动和对话，逐角色训练；[RoleLLM](../../../library/themes/game-npc-social/papers/ROLELLM_2024.md)分别构造角色知识与通用指令的角色表达，训练一个条件模型。两者都比只给名字更具体，但主要证据是角色采访／问答；合成经历也不等于真实历史或游戏事件。

**从强教师合成到自对齐，再到原创人物分布。** [Ditto](../../../library/themes/game-npc-social/papers/DITTO_2024.md)以同基座的阅读理解能力生成角色QA，跨四种模型规模比较16组监督关系，发现身份、知识、边界受监督能力影响不同。不过其Qwen基线是作者去掉角色SFT的版本，不能把增幅直接套到公开现成模型。[OpenCharacter](../../../library/themes/game-npc-social/papers/OPENCHARACTER_2025.md)将约2万合成人物与30.6万回答用于定制，比较保留答案事实的改写和直接生成。它拓宽了原创人物，但仍主要在200合成人物的问答式评价上验证。

**从QA转向文学情境和多人互动。** [CoSER](papers/COSER_2025.md)从771本书抽取人物、对话、经历和情境，训练角色表现并安排多人发言；原始对话和模型推断的思想／动作要分开。它为“人物此刻为什么这样说”提供比标签更丰富的数据，并显示结构化经历／对话检索可胜过原文片段检索。其环境反馈仍由模型叙述，不能称引擎行动验证。

**近期工作更直接地优化推理过程与场景化奖励。** [HER](../../../library/themes/game-npc-social/papers/HER_2026.md)把隐藏系统推理与可见人物思想分开，以场景依赖的原则形成偏好奖励；[Character-R1](../../../library/themes/game-npc-social/papers/CHARACTER_R1_2026.md)使用角色标签、焦点和参考回答构造可计算奖励。后者的exact match/BLEU可核算，但角色是否应该作某种心理判断未必有唯一真值。训练收益应看各维度，而不是把生成“认知焦点”直接当内部机制。

## 3. 基准扩大了什么，又没有扩大什么

| 代表 | 实際单位与评价 | 关键边界 |
|---|---|---|
| [InCharacter](../../../library/themes/game-npc-social/papers/INCHARACTER_2024.md) | 32角色、14量表、开放访谈；93名熟悉角色的标注者 | 80.7%是16P逐维准确率；同项全维度一致44.8%。静态标签不等于游戏行为 |
| [CharacterEval](../../../library/themes/game-npc-social/papers/CHARACTEREVAL_2024.md) | 77中文人物、1785对话、11376样本；人工训练奖励模型 | 按样本切分，非完整对话隔离；“行为”多为括号文字动作；知识维相关低于总体 |
| [PersonaGym](../../../library/themes/game-npc-social/papers/PERSONAGYM_2025.md) | 200合成人物、150情境池、10000问题、五维评分 | 情境是题目条件，非持久规则世界；高分天花板与拒演会影响模型排名 |
| [CharacterBox](../../../library/themes/game-npc-social/papers/CHARACTERBOX_2024.md) | 10作品×10场景、2–4角色、模型叙述者更新世界 | 多人动态文本很有用，但叙述者不是独立因果真值；指导／反思训练用了不同规模底座 |
| [CoSER](papers/COSER_2025.md) | 200文学场景、三个重复；人物／故事等分开评 | 保持原作剧情与容纳玩家改写可能冲突；200场景不等于200可玩游戏 |
| [RPGBench](../../../library/themes/game-npc-social/papers/RPGBENCH_2025.md) | 生成可达游戏，规则检查数值和条件，再随机选择动作模拟 | 机械有效与趣味不同；无确定执行器强参照；20游戏的人机趣味相关很弱 |

这些基准不应按“离引擎越远越无价值”排序。它们分别研究表达、人物识别、情境模拟和机械一致性。错误在于用其中一种证据作另一种主张。

## 4. 强模型与强普通系统的实际教训

在HER自己的统一评委下，训练后的Qwen3-32B为53.12，所测Claude Opus4.5、Gemini3Pro、GPT5.1分别为62.43、61.80、61.10；因此不能只报从弱基座的增幅而忽略同协议强对照。与此同时，原CoSER的59分和HER重评中的35／27分并非性能跨时间退化，而是评委和格式更换。[原表与范围](../../../library/themes/game-npc-social/papers/HER_2026.md)

PersonaGym中GPT4.1和Llama3-8B都为4.49，只说明在该高分、聚合且带拒演差异的协议上同分，不能推出模型规模无效，更不能推出现代API不会改善NPC。OpenCharacter还将PersonaGym原双评委改为单GPT4o，其绝对分不能与原论文横比。[PersonaGym](../../../library/themes/game-npc-social/papers/PERSONAGYM_2025.md)、[OpenCharacter](../../../library/themes/game-npc-social/papers/OPENCHARACTER_2025.md)

**信息、历史和知识结构是必须认真给足的普通参照。** [Dynamic Persona Coherence](papers/DYNAMIC_PERSONA_COHERENCE_2026.md)的Vanilla没有历史响应和状态累积；[CDT](papers/CDT_2026.md)把同一知识树线性化成普通提示后已很接近完整树方法。它们支持结构／记忆可能有用，也使“特殊机制不可替代”的主张需要更强比较。

## 5. 值得形成的整体认识与研究问题

角色学习正在从“让模型听话扮演”扩展到**作者新建人物、知识边界、情境动机、长程经历、可解释约束和群体表现**。已有数据、训练和评测提供了可复用基础；研究价值不必靠重新发现小模型容易失忆。

更具信息量的问题包括：同一人物知识在完整提示、检索、SFT和结构化规则下的覆盖与可编辑性如何不同；作者独特文风、沉默、含糊、不讨喜态度和披露节奏能否保持并低成本修改；角色训练是否牺牲任务能力或作者设定之外的常识；人物变化怎样由事件推动且能被玩家理解；评价中的高分是否预测新的情境决策与实际行动；多个有自身立场的角色怎样共同构成可理解的互动。它们需连接相应证据层，不能仅加一项“人格一致性”总分。

与这些问题相接的路线见[人格变化](PERSONA_DRIFT.md)、[叙事与社会](SOCIAL_SIMULATION_AND_NARRATIVE.md)、[玩家与作者](PLAYER_EXPERIENCE_AND_AUTHORING.md)。当前欠账包括RoleBreak/ArcANE等已有摘要来源的完整阅读、更多跨文化原创人物、语音／身体联合表达、跨会话真人长期研究；不因本批数量增加就标为完成。
