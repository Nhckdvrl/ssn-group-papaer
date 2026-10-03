# Debiasing LLMs toward Social Factors through Prompt Knowledge Tuning（arXiv2026）

[原HTML](https://arxiv.org/html/2603.27057v1)。引言/related work/方法/数据与setup、主要表、跨语言/温度/order/模型分析已读；全文末尾部分/完整图、补充label definitions、代码/raw未核对，不计全文或已接受论文。

- **形态 / idea来源（DOCUMENTED）：** 从灾害社交媒体零样本分类错误与attribution theory出发，将文本的context与用户goal分别生成后作为CoT提示辅助。改变前提是任务需不同社会信息，而非只依通用CoT。
- **距离：** context injection、label definitions、zero-CoT早已有；其claim是同一模型自动生成instance-specific social-attribution aids，再接reasoning/classification；三7–8B模型、八event/language设置，原资料需接受后发布。不能claim首次social attribution、目标与环境区分或忽略已有恢复方法。
- **对象/证据：** Intent help-seeking/offering、theme detection的MacroF1，natural TREC/CrisisLex tweets；bias主要由分类表现与任务层prompt preference测。原论文承认goal aid更有信息量等替代解释；提高F1不唯一识别dispositional/situational机制。自主生成goal不是新的已知因果事实，可能有错误或答案泄漏风险，原raw未审。
- **对我们 / 可借：** 不局限语义学素材，真实应用中理解用户为什么说话也重要；但要把原始语料事实、生成解释、目标规范分开。用独立真实证据干预区分信息增加与attention/response policy，比再加一次“考虑动机”指令有信息量。
- **规模/训练判断：** 模型family和任务性能不同不自动贬低整个问题，也不能自动叫机制差异；应对相同可读信息与成功控制比较条件响应，再跨source。目前我们只是定位，未在此数据造新结果。
