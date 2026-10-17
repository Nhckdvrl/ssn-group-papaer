# ReflAct（EMNLP2025 main）

来源：[正式全文](https://aclanthology.org/2025.emnlp-main.1697/)，已读方法、Table2与附录D.3/I的state-only、goal-only、state+goal+thought及prompt变体；未复现模型实验。

**DOCUMENTED / idea来源：** ReAct行动导向推理会脱离当前state/goal；让agent显式反思“自己在哪/持有什么/与goal距离怎样”再行动。ALFWorld/ScienceWorld/Jericho等环境、开源与闭源模型，官方正文包含强enhancement comparison。

**已有对照：** 不只是多一个reflection：state/goal单独、组合、额外Thought、instruction paraphrases、任务类型和token长度分析已做。不能把“先报当前位置再选择”作为原创方法，也不能只比裸ReAct。

**对我们：** 可以排除P02默认推理模式/位置整合解释。若被一条state-goal反思吸收，保留校准并转自然NPC利益决策；若还有真实、可预测的状态条件或玩家利益冲突，才是候选增量，必须另有独立证据。
