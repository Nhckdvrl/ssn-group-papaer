# Expectations over Unspoken Alternatives Predict Pragmatic Inferences (TACL2023)

来源：[primary](https://aclanthology.org/2023.tacl-1.50/)；公开评审/分数未核对。

1. **论文形态 / 阅读证据：** 正文1–13页（含§7.2/7.3）、within/cross README、run_bert.py与两analysis notebook代码已读；refs主要谱系已看，GloVe/concept完整重回归未复现。2026-10-03重新取得最终17页PDF，SHA3bc7595d5ec3a7dc17035424ac031064e4518543e3ba33900f600700240fa8ca；正文全文不等于完整资产复现。
2. **背景与压力：** 人类scalar inference在同一some和不同lexical scale间大幅变化。过去用单一strong词当备选；本文提出concept-level备选分布。
3. **改变前提 / idea来源：** 不是全局语用能力，而是先有相关备选表达，再排除说话者未选择的表达。来源DOCUMENTED：词汇预期与scalar diversity的人类实验。
4. **方法 / 数据 / 证据：** Within原BERT插入some,but not[MASK]；cross GPT2强词region5及WordNet备选/GloVe概念加权。原Switchboard human1363名义项，公开输入与human unique实际1362，148 unique lexical scales分布在4资料集。E13逐项8alternatives匹配率1、maxsurprisal差<3.72e-5；human Pearson−.4001 CI[−.4383,−.3628]。
5. **短板与校对：** 字符串within相关不能替代concept across-scale主结论；BERT看右context，因果LM不看。原code cosine+1与formula权重须复核；一些multiword TSV被shell分文件，E18保留缺失表。
6. **最近邻与claim ownership：** 已拥有alternative availability→SI关系和两阶段理论。我们需检查语境何时使未说出的备选成为证据，并与可预测性区分；只换现代模型不是论文。
7. **可迁移研究动作：** reproduce → 同材料条件切片 → readout/知识check控制 → 跨model/stage。新颖性只做定位。
8. **对本workbench：** 与Hu/Levy、Wavelength、ALTPRAG/PaCE的距离按测量对象和证据区分，不能把这些parent的已有结论改个名字当贡献。
9. **阅读边界：** 上列已读部分明确，未读附录/原code不以PDF下载代替。

**idea从何处生长：** 背景不是“LM懂不懂some”，而是旧NLI/强词频数无法同时解释within与cross-scale的人类差异。作者先比较string与concept两种可区分前提，再用人类cloze accessibility作独立桥接；不是用相关最高的现代模型当能力赢家。§7.2明确其主要证据约束alternative determination，未直接识别ruling-out这一步。variable alternative sets与contextual prior/QUD能分别给出备选expectedness，前者不是唯一解释。

**对我们最重要的边界：** §7.2给start/finish同时刻例：高人类“Yes”可能仅来自世界先验，不是scalar reasoning；明显意义又可能因无需表达而低语言概率。作者的but-not template是在已经产生显式scalar contrast条件下预测表达，不能直接等同自然speaker发话policy。§7.3主动从categorical competence转向conditional variability；“第一次测何时推断”不是我们的ownership。我们需要独立world prior/goal/knowledge证据约束具体候选，而非把高字符串expectedness直接当推断许可。

**原实现待校对，未宣判：** 原notebook cosine weights平移+1，最终Eq2写未平移cosine；cross notebook把metric_value用exp(−value)转prob，而E18原SyntaxGym scorer已核对bits单位。完整concept复现应先分别冻结原code版本与单位一致诊断、取得原GloVe并核对published图/回归，不事后替换primary或宣称原核心结论失效。此处只是代码阅读发现的校对问题，尚无新定量实验/科学finding；不是我们下一篇paper story。
