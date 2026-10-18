# PsychSim: Modeling Theory of Mind with Decision-Theoretic Agents

规范记录：`psychsim_2005`；IJCAI 2005。实际版本：作者公开会议稿，6页。

**实际阅读范围：** 全文6页、§1–4与表1；PDF部分公式/否定符抽取乱码，本文记录不转录这些符号或表中精确条件

[原文](https://people.ict.usc.edu/~pynadath/Papers/ijcai05.pdf) · [发表／主源信息](https://www.ccs.neu.edu/home/marsella/publications/abstracts/PynMarsIJCAI05-abstract.html)

**来源与范围：** 2005；IJCAI 2005；作者公开会议稿，6页。全文6页、§1–4与表1；PDF部分公式/否定符抽取乱码，本文记录不转录这些符号或表中精确条件。[PsychSim: Modeling Theory of Mind with Decision-Theoretic Agents](https://people.ict.usc.edu/~pynadath/Papers/ijcai05.pdf)。阅读标记：new_full_read。

PsychSim把社会互动建模为各自具有效用、有限观察、关系和递归心智模型的决策代理。行动不只改变物理状态，也改变旁观者对力量、可信度与动机的判断；消息可信度综合历史一致性、接收者利益、说话者利益、信任和支持。有限前瞻与对他人的简化刻板策略兼顾计算成本和有限理性，课堂例中采用两层嵌套信念，而非无限递归最优博弈。

完整例子是欺凌者、受害者、围观群体与教师四个角色/群体。作者改变三类欺凌动机、三种教师干预、两种同伴模型与三种教师模型，表1合并列出参数组合的模拟后果；这不是54间真实教室或被试实验。成功标准只是下一次不攻击，非长时间教育效果。权重还可拟合指定的初始行为，因此产生合乎直觉的案例，不等于独立验证社会心理理论。

领域位置是社会训练与社会仿真邻接研究，不能称为成熟可玩NPC产品。它对NPC的重要贡献是把同一外在动作的意义系于动机、别人怎么理解以及后续激励：惩罚并非普遍奏效，消息也非事实数据库覆写。其局限包括手工状态/动力学/权重、有限模型集合和校准不足；适合提供可解释机制与反事实设计参照，不适合直接预测真实人群或声称理论心智已普遍解决。

## 与最近邻的距离

此表是当前比较视角，包含后来工作；不把它们均视作本文发表时的基线。

| 近邻 | 方法、对象或证据的区别 |
|---|---|
| [EMA: A process model of appraisal dynamics](EMA_2009.md) | EMA以因果解释形成评估和应对，PsychSim着重递归他人模型与信息可信度。 |
| [FAtiMA Modular: Towards an Agent Architecture with a Generic Appraisal Framework](FATIMA_MODULAR_2014.md) | FAtiMA把情绪/动机等组件可组合化，PsychSim以决策理论状态与预测为核心。 |
| [Toward Characters Who Observe, Tell, Misremember, and Lie](TALK_OF_TOWN_2015.md) | 后者保存消息来源和错误记忆的社会传播，不以POMDP求解沟通策略。 |
