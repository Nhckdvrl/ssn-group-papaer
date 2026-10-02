# Surprisal Minimisation over Goal-directed Alternatives Predicts Production Choice in Dialogue (ACL2026)

来源：[primary](https://aclanthology.org/2026.acl-long.1814/)；公开评审/分数未核对。

1. **论文形态 / 阅读证据：** 正文§3–7与limits已读；intro全部与appendix未全读；productionchoice repo未复现。
2. **背景与压力：** 说话者cost仅相对哪些备选才有意义；固定goal的paraphrases和context可说但goal不同不是一套选择集。
3. **改变前提 / idea来源：** goal-directed vs goal-agnostic替代集明确，cost解释依赖集合。DOCUMENTED：production choice/RSA/信息论cost压力。
4. **方法 / 数据 / 证据：** Switchboard1342候选→309contexts，GPT4o生成12360备选、400人工judge校准98.75%；stratify length/globalUID后6335generated。原GPT2surprisal；human minsurp53.4%goal-directed vs15.2%agnostic，均不同chance；pairwise logistic context-cluster。
5. **短板与校对：** 生产样本1/context，不是同一个人完整policy分布；LLM生成与judge定义备选集，过滤/匹配会影响解释。总cost不等价实际speaker内在effort。
6. **最近邻与claim ownership：** 预测性好不能说明某未说出的表达在当前goal可替代。备选集与goal的区别已有ownership；我们的许可对象不能脱离明确候选q。
7. **可迁移研究动作：** reproduce → 同材料条件切片 → readout/知识check控制 → 跨model/stage。新颖性只做定位。
8. **对本workbench：** 与Hu/Levy、Wavelength、ALTPRAG/PaCE的距离按测量对象和证据区分，不能把这些parent的已有结论改个名字当贡献。
9. **阅读边界：** 上列已读部分明确，未读附录/原code不以PDF下载代替。
