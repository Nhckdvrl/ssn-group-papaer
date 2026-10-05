# An Existence Proof for Neural Language Models That Can Explain Garden-Path Effects via Surprisal（ACL 2026 main，评审分数未核对）`[证据级别：正文 §1–7、Limitations；附录未读]`

[正文与公开代码入口](https://aclanthology.org/2026.acl-long.1694/)；PDF/hash见 READING_LEDGER。

1. **形态：** 理论操作化争议 → 构造反例 → 泛化与失败边界。
2. **压力：** 现成LM surprisal低估人类GP代价，究竟是理论错还是LM概率不合适？
3. **改变前提：** 不能以off-the-shelf LM的失败推断所有概率分布都失败。
4. **idea来源（DOCUMENTED）：** Huang等的两种解释中，直接检验概率估计这一竞争解释。
5. **近邻距离：** Huang系统检验失败；Kiegeland有reading-time训练方法；本工作用后者回答前者的理论问题。不是单纯换强模型。
6. **证据：** GPT2三尺寸，SAP三GP构式；23个LOO folds，诱发歧义动词/ROI词训练测试不重叠，ordinary-word拟合系数再测ROI；独立自然语料、BLiMP、跨构式迁移；SRC/ORC作为不易拟合的对照。
7. **短板：** 小数据、训练改变预测概率；general capability“保留”不等于完全不退化：Natural Stories GPT2-S perplexity53→80，BLiMP .82→.80。SRC/ORC部分large-model folds因收敛排除，不能默默写全运行一致成功。
8. **可迁移动作：** 不同解释必须对应不同实验；为正结果加“同方法理论上不应任意成功”的失败对照。讨论理论可证伪性，但主表先回答自然RQ。
9. **对我们：** 保持模型固定、解释对象明确；GP问答失败不能直接升级为revision算法失败。SAP原题/作者答案是比随意自构题更有价值的资产，正在E09复用。本文有训练不是我们现在要训练的理由。
