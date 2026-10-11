# Finding Alignments Between Interpretable Causal Variables and Distributed Neural Representations（CLeaR 2024）[证据：正文§3–5核对]

原文：https://arxiv.org/html/2303.02536v4

1. **形态：** 因果抽象方法＋受控机制验证。
2. **压力：** 神经元坐标逐个搜索会漏掉分布式变量；一处patch失败不能判断算法不存在。
3. **改变前提：** 在可学习正交基内做interchange，保留未对齐分量；冻结主网络和符号模型，优化对齐。
4. **idea来源：** DOCUMENTED为localist alignment局限；不将文章顺序当作者探索时间线。
5. **近邻距离：** 原局部interchange→分布式subspace interchange；不是发现一个新任务能力。
6. **关键链：** Hierarchical equality两个中间变量；MoNLI negation与lexical relation；错误high-level models、localist/brute-force、random network参照。
7. **最值得学：** §5.3用子结构interchange发现“lexical entailment”可分解为两词身份数据结构，因果alignment成功仍不等于抽象关系已被算出。§4.4随机大网络能获得非零干预预测，提醒方法有搜索容量。MoNLI表报training数据与best of3，不能照搬成独立确认规范。
8. **迁移研究动作：** 当整体packet运输符合一个关系预测时，重新设计让存储参与对象与已计算关系给出不同结果。
9. **ICES：** E101阴性不能否认分布式标准；E94阳性不能将来源身份packet称完整program。先做E102 donor规则×recipient证据的内容对照，再考虑功能变量对齐。DAS若在这里成功，仍需原生必要性/恢复与独立context，不能把训练目标制造的修复当原生算法。
