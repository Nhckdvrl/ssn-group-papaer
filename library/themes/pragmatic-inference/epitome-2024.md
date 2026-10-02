# EPITOME: Comparing Humans and LLMs (TACL2024)

来源：[primary](https://aclanthology.org/2024.tacl-1.45/)；公开评审/分数未核对。

1. **论文形态 / 阅读证据：** 正文intro/related、全部methods、SI/IR关键results/Discussion/limits、Appendix A/B已读；FB/RM/ShS/StS细results未逐段全读。OSF sn7gj 的SI/IR目录公开可读，代码/CSV与原SI评分已核对。
2. **背景与压力：** 单一ToM任务无良好convergent validity；要比较相同材料上的human与model条件效应。
3. **改变前提 / idea来源：** 把mental-state表征能力与用其作pragmatic inference的表现分开，distributional baseline控制。DOCUMENTED：六人类心理范式而非新synthetic挑bug。
4. **方法 / 数据 / 证据：** 5GPT3系列模型，主t-d-002非RLHF；SI40templates×knowledge access×some/number，242humans原分布；IR16pairs×aware/unaware×implicit/explicit知识，69人。SI2部分access的a2,n1也可排除3，不是全局ignorance⇒不推断。
5. **短板与校对：** SI1some的observed-vs-total歧义作者承认；原code knowledge check实际删143+267=410human trials，论文文字143+247不一致；human filtered SI1=.5617/SI2=.7296，原t-d-002=.25/.454167复现，model不删；Appendix A Table2 Δbet符号与正文存在不一致，必须以原src核对，不盲照表重现。IRcorrect描述同写unaware疑typo；公开raw16items仅6有critical utterance，原src dropna，不能称16item复现。
6. **最近邻与claim ownership：** 已拥有LLM知道mental state却使用不足、human residual knowledge effects。只重复2024 failure不新；同任务clean stages若改变条件结构，才可能重新归因post-training。
7. **可迁移研究动作：** reproduce → 同材料条件切片 → readout/知识check控制 → 跨model/stage。新颖性只做定位。
8. **对本workbench：** 与Hu/Levy、Wavelength、ALTPRAG/PaCE的距离按测量对象和证据区分，不能把这些parent的已有结论改个名字当贡献。
9. **阅读边界：** 上列已读部分明确，未读附录/原code不以PDF下载代替。
