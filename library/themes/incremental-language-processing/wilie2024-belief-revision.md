# Belief Revision: The Adaptability of Large Language Models Reasoning（2024 v1）

[原文](https://arxiv.org/html/2406.19764v1)。实际读§1–4定义与数据构造/标注；结果表和附录未完整核对，最终发表状态未核对。

1. **形态：** frozen模型增量证据评估 + update/maintain tradeoff；与句法GP不同但同属修订领域定位。
2. **来源（DOCUMENTED）：** Byrne suppression task；新条件可被解释为additional requirement或alternative route。
3. **动作：** 先两premises/后第三premise；MP/MT、保持/更新与事件/mental-state区分。
4. **数据：** ATOMIC为seed、GPT4生成；五人conclusion标注、多数和4/5agreement过滤；另三人抽100quality核对。basic1912、三premises1744。不是每条formal逻辑gold。
5. **关键边界：** 原两个条件中的充分性，第三条件后被commonsense改读成必要性；文中承认此隐含步骤。保持/更新不是严格经典逻辑排斥，用人类判断定义的nonmonotonic阅读。
6. **对我们：** 晚证据改变回答、该改/不该改tradeoff、通用belief maintenance均有owner。不能用GP换皮讲“LLM不会更新belief”；更具体的语言证据传播和后果仍可研究。
