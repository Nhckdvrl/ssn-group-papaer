# An Incomplete Loop（COLM2024；arXiv2404.03028v3）

**本轮阅读：** [主文§2–5](https://arxiv.org/html/2404.03028v3)，不是仅摘要；附录提示词/所有数据未逐条复核。作者页COLM2024记录，版本标题与作者页标题措辞略异。

1. 问题：few-shot预测、从examples推断instruction、给instruction后执行，能否互相预测？这是现有ICES E78的直接概念近邻。
2. 切入点：对相同函数/翻译任务同时测假设质量与预测质量，并把模型提出的假设再交回模型执行。额外构造true instruction阳性，拆推断错误与执行错误。
3. idea来源（RECONSTRUCTED）：已有自动instruction induction改善分数，不等于模型已内部学会同一规则；以闭环三种能力间的关系为对象。论文顺序不是原始发现顺序。
4. 方法边界：linear y=ax+b、简单人工语言、Kalamang；提出5 hypotheses，按外部MSE或语言模型打分选一个。概率评分用独立davinci；强先验/参数估计与筛选过程不能直接视作默认ICL算法。
5. 知识增量：规则归纳与ICL预测可以分离；正确instruction常提高synthetic任务，归纳出的instruction在复杂翻译未必改善。这些一般结论、self-generated instruction回交接流程都已有claim ownership。
6. 近邻距离：ICES控制每Source相同Input/Label边缘、四个独立operator，识别code在Input前跨query复用；但这只是受控诊断条件，尚非新的计算解释。不能将“会辨认却应用弱”包装成新认识。
7. 可迁移动作：同时测Rule-ID、numeric预测与code执行；不筛正确Rule-ID样本；先过true-code阳性。未来必须有Source特有的预测/因果机制，或说明旧解释在哪个组合条件失效。

定位，非关闭决定；此文没有ICES所需的Source白盒计算链，也没有因而保证我们能找到新的计算链。
