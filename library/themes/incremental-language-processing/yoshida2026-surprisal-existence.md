# An Existence Proof for Neural Language Models That Can Explain Garden-Path Effects via Surprisal（ACL 2026 main） `[证据级别：正式全文主文]`

来源：[正式会议稿](https://aclanthology.org/2026.acl-long.1694/)。读完整§1–8、Limitations、附录A参数/B能力表/C跨构式图；没有把参考文献逐篇读过。作者Tokyo/NINJAL/NII/MBZUAI；公开评审分数未核对。

1. **形态与压力：** 理论可证伪性＋训练干预。现成LM的surprisal只解释少量人类GP减速，不能由此推出整个surprisal理论不成立。
2. **改变前提：** 不再只检验off-the-shelf分布，而检验是否存在可学习且能外推的分布。不是声称当前强LLM已正确理解GP。
3. **idea来源：** DOCUMENTED：Huang2024等严重低估→概率估计失败与理论失败两个解释→借Kiegeland2024人类阅读时微调验证前者。RECONSTRUCTED：把“当前模型没做到”改成可构造的existence问题，贡献主要来自研究对策和理论视角，不是新优化器。
4. **近邻距离：** Hale/Levy提供计算理论；Huang/SAP提供可复现反例；Kiegeland提供RT训练；vanSchijndel/Linzen提供低估现象。增量是GP专项训练、词汇无重叠外推、跨构式与自然阅读外推，并讨论理论的约束。
5. **方法/数据：** GPT2 S/M/L（一个族），SAP三构式各24pairs，排一组错误后23folds；每fold留三组，训练歧义动词/ROI词不重叠，平均1645训练词。每batch以非ROI ridge拟合RT再对全部位置误差反传，并约束ridge系数防止通过压低非ROI surprisal抬系数作弊；500步。自然阅读NaturalStories/Brown/UCL，BLiMP/PPL；SRC/ORC无spillover任务检验另一类困难。
6. **关键读数：** GPT2small ROI1人类减速解释比例MVRR/NPS/NPZ由7/19/15%到73/83/73%；跨构式训练也外推但较弱。SRC/ORC最好只解释22%，自然RT拟合多下降。GP训练后NaturalStories PPL53.04→80.08、BLiMP .821→.803；不能把“能力保留”写成无代价。误差条为fold SE，不是独立训练seed CI；RC GPT2large两fold不收敛排除，作者披露。
7. **强度/限制：** 支持所定义训练方案的存在性及有限外推，不是证明人脑采用该LM，也没测内部parse/QA/角色恢复。训练目标本身促surprisal增加，所以“更惊讶”不能等同“更会修订”。用uniform PPL作保留底线很宽。
8. **可借动作：** 把失败的理论与失败的代理分开；用受监督改变同一对象后看另一用途是否改变。不是再做自然surprisal相关性就算新机制。
9. **对我们：** E55有效wholevec不证明parse、E65目标收益不证明整体语义；若想把察觉→重析→撤销连起来，必须看自然关系的功能变化。一个有兴奋度的方向是对可塑的错误发现/正确关系建立与旧关系撤销找不同因果入口，不能仅借“73%”包装能力提升。现有实验未达到。
