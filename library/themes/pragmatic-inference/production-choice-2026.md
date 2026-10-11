# Surprisal Minimisation over Goal-directed Alternatives Predicts Production Choice in Dialogue (ACL2026)

来源：[primary](https://aclanthology.org/2026.acl-long.1814/)；公开评审/分数未核对。

1. **论文形态 / 阅读证据：** 正文§1–7、limits与附录A–D全文/方程/表已读；图未独立逐点核对。2026-10-03原文所列productionchoice repo网页404、git clone无法公开读取，代码/数据未取得，不称复现。
2. **背景与压力：** 说话者cost仅相对哪些备选才有意义；固定goal的paraphrases和context可说但goal不同不是一套选择集。
3. **改变前提 / idea来源：** goal-directed vs goal-agnostic替代集明确，cost解释依赖集合。DOCUMENTED：production choice/RSA/信息论cost压力。
4. **方法 / 数据 / 证据：** Switchboard1342候选→309contexts，GPT4o生成12360备选、400人工judge校准98.75%；stratify length/globalUID后6335generated。原GPT2surprisal；human minsurp53.4%goal-directed vs15.2%agnostic，均不同chance；pairwise logistic context-cluster。
5. **短板与校对：** 生产样本1/context，不是同一个人完整policy分布；LLM生成与judge定义备选集，过滤/匹配会影响解释。总cost不等价实际speaker内在effort。
6. **最近邻与claim ownership：** 预测性好不能说明某未说出的表达在当前goal可替代。备选集与goal的区别已有ownership；我们的许可对象不能脱离明确候选q。
7. **可迁移研究动作：** reproduce → 同材料条件切片 → readout/知识check控制 → 跨model/stage。新颖性只做定位。
8. **对本workbench：** 与Hu/Levy、Wavelength、ALTPRAG/PaCE的距离按测量对象和证据区分，不能把这些parent的已有结论改个名字当贡献。
9. **阅读边界：** 上列已读部分明确，未读附录/原code不以PDF下载代替。

**深读后的研究逻辑：** 其idea不是再换一个cost，而是使同一个cost在两种选择集合下承担不同解释。§2指出LM surprisal常被同时叫speaker effort和listener effort；§3先固定choice point和goal，再给竞争预测。附录D.2的goal-matching比例4.7/6.2/15.2%随history增加，说明goal-agnostic并非goal完全随机，更不能把其高expectedness直接当同goal备选可用性。AppendixC的context-cluster及D.6无stratification重复，分别处理伪重复和匹配样本依赖，不能靠更多近似图当独立验证。

**需保留的边界：** paraphrase one-shot例含新事实/限定，原goal-directed集合依赖GPT-4o判同义与400例人工校准，不是穷尽所有同goal可用表达；不据示例宣布最终集合错误。AppendixD conditional-logit的fit不是人类完整policy观测；不同集合基数的likelihood不能不加说明横比。Limits明确未建listener interpretation、把communicative effectiveness近似常数。我们若研究speaker选择能否约束listener，就必须独立验证解释成功和goal可替代性，不能只把其production predictor当真实speaker机制。此对象与RSA已有联系，增量仍需自然材料上的可迁移预测，而非首次联合speaker/listener。
