# Pragmatic Competence in LLMs: The Case of Eliciture (SCiL2025)

来源：[primary](https://aclanthology.org/2025.scil-1.39/)；公开评审/分数未核对。

1. **论文形态 / 阅读证据：** 全文4页已读；原刺激/code链接未找到，不假称资产齐。
2. **背景与压力：** 非强制性causal enrichment能否影响下游句法，而不只是模型说自己理解？
3. **改变前提 / idea来源：** Detection→use拆开：2×2 implicit-causality verb/relative-clause内容，与高低attachment continuation。DOCUMENTED：人类Rohde/Hoek范式。
4. **方法 / 数据 / 证据：** 60sets/240 detection句，5open GPT2/Llama1B/3B Base/Instruct、3closed；open测逗号and I do not know why continuation总logprob。Attachment测is/are；Llama四模型均有interaction/attachment趋势，closed只有GPT4attachment效应。
5. **短板与校对：** 固定相同续写长度有利控制，但2×2 interaction不能完全排除更高阶lexical统计；参数scale解释speculative，非显著不是无效。
6. **最近邻与claim ownership：** “知道vs用”或prompt/direct asymmetry不是新claim；可作跨现象probe，但未有资产前不伪造60套材料。
7. **可迁移研究动作：** reproduce → 同材料条件切片 → readout/知识check控制 → 跨model/stage。新颖性只做定位。
8. **对本workbench：** 与Hu/Levy、Wavelength、ALTPRAG/PaCE的距离按测量对象和证据区分，不能把这些parent的已有结论改个名字当贡献。
9. **阅读边界：** 上列已读部分明确，未读附录/原code不以PDF下载代替。
