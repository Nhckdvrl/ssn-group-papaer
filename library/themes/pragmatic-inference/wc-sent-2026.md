# Annotating Dimensions of Social Perception in Text: W&C-Sent（ACL2026 main / arXiv v1）

[公开v1](https://arxiv.org/abs/2601.06316v1) · [作者材料](https://github.com/nedjmaou/W_C_Sent)。39页v1：正文/Related Work/数据/实验/分析/局限已读；附录E定义及操作说明、P/Q输出处理深读；E所有举例、其余附录/图/代码与原数据未全审。作者主页及本地venue corpus确认main，但本次读取版本为v1，不当最终camera-ready。

- **论文形态 / 压力：** 构念引入＋自然数据。Warmth/Competence已有心理理论和词级lexicon，但句法/组合/讽刺及特定target不能由词的均值恢复。扩展的是文本描述中的社会评价，非通用语用理解scalar。
- **idea来源 DOCUMENTED：** 从Mohammad2025词级trust/sociability＋既有competence分量发展为sentence–target；不是因为LLM存在一个人工bug。继承SemEval stance自然文本，再选可谈论人的target并增加ABCDE语料。
- **最近邻距离：** Fiske心理维度、Abele的warmth分面、Mohammad词级norm、SemEval2016 stance提供genealogy；本文增量是自然sentence–target及三维逐条标注。Beltrama2023/2025研究听者从说者交际行为形成印象；本文标**作者向target表达何种印象**，两者不能直接互换gold。
- **数据/方法：** 1633 sentence–target pairs，七target，4–7 raters/dimension，215人；三维分开标降低负荷。-3…3；0包括neutral、not expressed、not applicable。依作者229个预标案例＋attention checks筛质量；60/20/20 split，BERTweet、TF-IDF/dummy和Gemma3-4B/Qwen2.5-7B/GPT4o系列ZS/FS。自然语料偏US争议议题，trait人口norm是culture-specific。
- **证据与风险：** 细粒度competence更难/IAA较低，文本可以同时传达低warmth、高competence。median/mean与coarsening不同；0合并“缺证据”和“中性”会限制我们对停止推断的解释。P描述regex/JSON修复与label映射，尚未代码校对，不将parser问题当模型能力。
- **可借研究动作：** 原natural corpus筛选＋独立target对齐，分开construct标注；保存个人rater分布、歧义、缺证据，不只保一个平均label；先明确单位是句子还是sentence–target，训练/测试需考虑同句多target泄漏。同词不同目标、同target不同证据可用于评估边界，但必须另审语料/labels。
- **对我们：** 数据规模是参考，不是“1633才够”的固定门槛；E61/E63只有6/14独立scene，更多queries不能补scene。可研究实际说者行为与别人显式评价的证据如何区别，但不能靠换target/prompt就自动形成novelty。暂不下载它铺榜单，它没有给我们明确inability操控或真实人格gold。
