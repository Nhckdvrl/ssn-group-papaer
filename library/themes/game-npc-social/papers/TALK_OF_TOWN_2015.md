# Toward Characters Who Observe, Tell, Misremember, and Lie

规范记录：`talk_of_town_2015`；AIIDE Experimental AI in Games Workshop, WS-15-21:56–62。实际版本：作者公开7页会议稿；会场为workshop，非AIIDE主会论文。

**实际阅读范围：** 全文7页；知识类型、证据强度/来源/修订机制、实现状态与相关工作

[原文](https://expressiveintelligence.github.io/papers/ryanEtAl_TowardCharactersWhoObserveTellMisrememberLie.pdf) · [发表／主源信息](https://ojs.aaai.org/index.php/AIIDE/article/view/12825)

**来源与范围：** 2015；AIIDE Experimental AI in Games Workshop, WS-15-21:56–62；作者公开7页会议稿；会场为workshop，非AIIDE主会论文。全文7页；知识类型、证据强度/来源/修订机制、实现状态与相关工作。[Toward Characters Who Observe, Tell, Misremember, and Lie](https://expressiveintelligence.github.io/papers/ryanEtAl_TowardCharactersWhoObserveTellMisrememberLie.pdf)。阅读标记：new_full_read。

Talk of the Town把知识传播、记错与说谎设计为玩法资源：玩家设想要在遗产宣读前识别秘密情人的外貌，另一方污染消息网络以躲过辨认。底层模拟先运行70年，生成城镇、家族、关系和约200名居民，再进入拟议游戏。NPC按效用选择工作、访问、成家等活动；人物外貌含24项，交往与显著性影响什么被看到、记住和传播。

核心表征将每个角色/地点的属性做成信念facet，记录候选旧信念、支持证据、强度、来源、时间与真实准确性。九种证据过程覆盖观察、自省、迁移混淆、虚构、谎言、转述、偷听、变异及遗忘。新证据的加权强度超过旧信念时才换信念；重述会加强自身确信，而证据随时间衰减。系统可以追溯一条错误信息如何形成和扩散，这是玩家理解后果的潜在工具。

必须保留论文自己的实现边界：社会模拟已实现，真正的双人玩法尚未实现；没有玩家实验或统一性能基准。说谎只是依关系概率触发、随机挑选错误内容，说谎者还不记自己说过的谎；目的性询问、策略欺骗、识破后关系修订是未来工作。领域价值在于把知识的来源与缺陷变成结构化世界过程，同时说明“可追溯的不可靠NPC”需让玩家看得懂，否则容易被认为是程序错误。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [PsychSim: Modeling Theory of Mind with Decision-Theoretic Agents](PSYCHSIM_2005.md) | PsychSim推理他人并选择沟通，Talk of the Town记录信念来源、遗忘和谎言传播。 |
| [Sabre: A Narrative Planner Supporting Intention and Deep Theory of Mind](SABRE_2021.md) | Sabre用作者指定的深信念做规划；后者强调模拟运行中分散知识如何产生。 |
| [Generative agent-based modeling with actions grounded in physical, social, or digital space using Concordia](CONCORDIA_2023.md) | Concordia可给不同观察与记忆，但该文并未验证同等细粒度的错误来源传播机制。 |
