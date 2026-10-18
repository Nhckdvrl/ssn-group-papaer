# FAtiMA Modular: Towards an Agent Architecture with a Generic Appraisal Framework

规范记录：`fatima_modular_2014`；Emotion Modeling, LNCS 8750:44–56。实际版本：作者2014-12-13上传的12页未清稿；不是已核相同的正式13页章。

**实际阅读范围：** 公开作者稿完整12页；§1–6、伪代码和OCC对应表；p8 Figure ??、p10未完成文字使正式版差异仍待核

[原文](https://www.researchgate.net/profile/Samuel-Mascarenhas/publication/265033357_FAtiMA_Modular_Towards_an_Agent_Architecture_with_a_Generic_Appraisal_Framework/links/548c2a3f0cf214269f1dda7a/FAtiMA-Modular-Towards-an-Agent-Architecture-with-a-Generic-Appraisal-Framework.pdf) · [发表／主源信息](https://link.springer.com/chapter/10.1007/978-3-319-12973-0_3)

**来源与范围：** 2014；Emotion Modeling, LNCS 8750:44–56；作者2014-12-13上传的12页未清稿；不是已核相同的正式13页章。公开作者稿完整12页；§1–6、伪代码和OCC对应表；p8 Figure ??、p10未完成文字使正式版差异仍待核。[FAtiMA Modular: Towards an Agent Architecture with a Generic Appraisal Framework](https://www.researchgate.net/profile/Samuel-Mascarenhas/publication/265033357_FAtiMA_Modular_Towards_an_Agent_Architecture_with_a_Generic_Appraisal_Framework/links/548c2a3f0cf214269f1dda7a/FAtiMA-Modular-Towards-an-Agent-Architecture-with-a-Generic-Appraisal-Framework.pdf)。阅读标记：new_full_read_author_draft。

FAtiMA Modular将复杂情绪角色架构拆为可交换组件。核心循环读取事件、更新记忆、累积评价变量、推导情绪、收集行为候选并按优先级执行。评价与情绪推导分开，同一事件可被后续信息重新评价；情绪以事件和其评价变量组索引，因此新的喜悦可替换旧的痛苦，而不同理由的混合情绪不会粗暴抵消成中性。

实际描述的组件包括反应规则、基于目标的规划、OCC情绪映射、驱力、他人心智与文化。驱力改变目标效用，心智模块模拟事件对别人的意义，文化模块依自他影响计算可赞许性。五人晚餐例中病人收到他人药物后先产生喜悦，再因理解赠药者的自我牺牲产生敬佩，展示模块依赖和分时再评价。

这里必须标版本与证据：取得的是作者公开未清稿，相关工作仍有缺引用和未完成句，不能称为已核正式章节。它没有报告OCC与Scherer同条件玩家比较；结尾明确把实现Scherer和检验更自然的表现留作未来工作。其领域价值是可替换、可查因的情绪/动机架构与评价过程，而非某理论已获实证胜出。对LLM NPC可借鉴事件级情绪出处和影响行为的机制，但不能用论文中已有文化模块自动证明跨文化真实性。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [EMA: A process model of appraisal dynamics](EMA_2009.md) | 同属认知评估史，FAtiMA重点是可替换评估/情绪组件而非证明单一理论。 |
| [Beyond Static Persona Consistency: Dynamic Persona Coherence in LLM Role-Playing](../../../../workbench/game-npc-agents/knowledge/papers/DYNAMIC_PERSONA_COHERENCE_2026.md) | DPC以现代LLM表达人格状态，不能替代更早的稳定倾向与动态情绪分离前史。 |
| [Generative agent-based modeling with actions grounded in physical, social, or digital space using Concordia](CONCORDIA_2023.md) | 都强调组件组合，Concordia另把行动尝试交给GM决定世界后果。 |
