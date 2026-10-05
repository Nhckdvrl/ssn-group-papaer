# Fundamental Problems With Model Editing: How Should Rational Belief Revision Work in LLMs?（2024）

[primary摘要](https://arxiv.org/abs/2406.19354v1)，[HTML](https://arxiv.org/html/2406.19354v1)。摘要/定义问题已读；23页正文尚未全读，不能冒充全篇audit。

提出12个model editing开放问题，涉及编辑的远端后果、概率性蕴含标签、agent simulators的belief、模型是否有可编辑belief等；semi-synthetic Wikidata/Bayesian-agent gold提供可比较标准。

对我们：续写概率不是直接belief oracle；“不assert”和“排除”必须区别，未约束的separate activity没有正误gold。I01若声称event-local correction，需要明确修改对象与允许的影响范围，不能拿任意probability shift当修订能力失败。本文研究parametric editing，与当前frozen自然文本行为不同；不因为广泛理论owner就判当前问题死刑。
