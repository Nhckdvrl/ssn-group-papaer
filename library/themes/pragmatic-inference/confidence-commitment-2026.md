# Reported Confidence in LLMs Tracks Commitment More Than Correctness（arXiv2026）

[原v1](https://arxiv.org/abs/2606.29490v1)。**阅读范围：** 引言、核心残差论证、主要reasoning/activation结果、discussion、Methods全文pp19–27、Fig9完整caption p37；其余补充表/代码/数据未核对，未复现实证。PDF53页已下载不计53页全文。

1. **压力/idea来源 DOCUMENTED：** 人与动物的post-decision opt-out实验＋LLM verbal confidence作为可靠性读数的惯例。旧问题是信心准不准；新问题是同一信号更接近正确性还是随后是否把答案交给用户。两阶段拆开，confidence调用不给abstention任务信息，后续调用不展示confidence报告，避免直接照抄分数。
2. **近邻距离：** ICML2026 cached confidence拥有报告产生位置；NMI2026拥有信心驱动行为；本篇重新解释报告的意义。四非reasoning×两集、四reasoning×四集、格式/neutral prompt与probe/steering形成多条证据，非另一个accuracy表。自己的answer commitment与E43归给他人的social commitment不是同一变量。
3. **方法与边界：** 对两结果用同trial AUROC、paired bootstrap，比较Cal-LP与两类VC；残差、两因素ANOVA、交叉验证probe、held-out steering。reasoning LP来自95%或100%trace另一次强制格式询问，非原生无prompt概率。HLE用API judge，不能直接作为我们主评估模板。
4. **深度校对：** 核心账户在正文与Fig9明确让D阈值作用于VC=zT+noise，却称移除zT后noise不预测D。[E48](https://github.com/Nhckdvrl/ssn-group-papaer/blob/2738b95a579a4e4c2c1211d8c2f3461cd4a647f2/workbench/pragmatic-inference-calibration/experiments/E48-confidence-identifiability-audit.md)的oracle代理反例表明这一步需要额外因果放置假设；残差预测决策不能仅凭改名区分估计噪声与policy成分。不否定原行为/steering观察，也不宣布整篇无效。
5. **机制证据范围：** PA probe预测未来决定，但steering实际加在下一阶段AC位置；证明方向可以影响决定，不等于同一forward的完整自然信息流。正确性/decision probe方向近正交不自动说明独立因果模块。QUD、成本、正确性与报告产生位置要分别控制。
6. **如何发展 RECONSTRUCTED：** 借同材料多结果与先测信号后决策的顺序，不能借“残差=policy”的解释捷径。我们要的是说话者表达选择如何约束听者具体推断；generic VC与correctness分离已拥有。先让E49互相约束的预测接受检验，之后才考虑representation。
