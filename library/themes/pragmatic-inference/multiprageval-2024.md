# MultiPragEval: Multilingual Pragmatic Evaluation of Large Language Models（GenBench 2024）

**证据：正文、related work、数据、prompt与主要结果/关键附录已读；上游CSV/README已核对，原inference代码未发布。** [原文](https://aclanthology.org/2024.genbench-1.7/) · [代码](https://github.com/DojunPark/MultiPragEval)

1. **形态：** multilingual benchmark。
2. **压力：** 英语/只看pragmatic成功遗漏literal及文化依赖。
3. **改变前提：** Quantity/Quality/Relation/Manner与literal并列，四语言adaptation。
4. **来源 DOCUMENTED：** Grice maxims、跨语言语用表达与原parent英文局限。
5. **最近邻：** Hu fine-grained英材料、Sravanthi更广pragmatic suite；本工作拥有multilingual/literal tension，不能claim首次注意literal。
6. **协议：** 300原row×四语言=1,200 test units；每category60，ABCDE各60；T=.5三trial单H10080GB。Table5只平均四maxim240项，literal在Figure1；原Qwen1.5-14B maxim英/德/韩/中53.33/43.06/49.72/50.00%，literal93.33/85.00/87.78/94.44%。
7. **短板：** 原code/system/top_p/top_k/max_tokens未发布，只能显式重建。文化adaptation有不同情景，非相同语境严格翻译；gold E=None不是literal；错误可能contradiction、irrelevant、unsupported。没有逐选项inference标签与human baseline。
8. **动作：** 原protocol复现、literal与maxim分开、format control、解析审计后再slice。
9. **对我们：** 适合轻量smoke和instrument，不能拿1−literal accuracy直接算FPR。原14B下载未完成；现代3B结果不是论文原模型复现。
