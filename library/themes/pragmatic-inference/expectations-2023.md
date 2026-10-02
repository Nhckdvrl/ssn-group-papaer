# Expectations over Unspoken Alternatives Predict Pragmatic Inferences (TACL2023)

来源：[primary](https://aclanthology.org/2023.tacl-1.50/)；公开评审/分数未核对。

1. **论文形态 / 阅读证据：** 正文1–12页、within/cross README、run_bert.py与关键analysis notebook已读；GloVe/concept完整重回归未复现。
2. **背景与压力：** 人类scalar inference在同一some和不同lexical scale间大幅变化。过去用单一strong词当备选；本文提出concept-level备选分布。
3. **改变前提 / idea来源：** 不是全局语用能力，而是先有相关备选表达，再排除说话者未选择的表达。来源DOCUMENTED：词汇预期与scalar diversity的人类实验。
4. **方法 / 数据 / 证据：** Within原BERT插入some,but not[MASK]；cross GPT2强词region5及WordNet备选/GloVe概念加权。原Switchboard human1363名义项，公开输入与human unique实际1362，148 unique lexical scales分布在4资料集。E13逐项8alternatives匹配率1、maxsurprisal差<3.72e-5；human Pearson−.4001 CI[−.4383,−.3628]。
5. **短板与校对：** 字符串within相关不能替代concept across-scale主结论；BERT看右context，因果LM不看。原code cosine+1与formula权重须复核；一些multiword TSV被shell分文件，E18保留缺失表。
6. **最近邻与claim ownership：** 已拥有alternative availability→SI关系和两阶段理论。我们需检查语境何时使未说出的备选成为证据，并与可预测性区分；只换现代模型不是论文。
7. **可迁移研究动作：** reproduce → 同材料条件切片 → readout/知识check控制 → 跨model/stage。新颖性只做定位。
8. **对本workbench：** 与Hu/Levy、Wavelength、ALTPRAG/PaCE的距离按测量对象和证据区分，不能把这些parent的已有结论改个名字当贡献。
9. **阅读边界：** 上列已读部分明确，未读附录/原code不以PDF下载代替。
