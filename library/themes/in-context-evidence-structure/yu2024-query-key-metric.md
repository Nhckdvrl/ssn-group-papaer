# Query and Key Matrices are Two Towers for Metric Learning（EMNLP 2024）`[主文§3–5；附录未逐项复核]`

[官方论文](https://aclanthology.org/2024.emnlp-main.192/)。Zeping Yu、Sophia Ananiadou。

1. **问题与idea来源（RECONSTRUCTED）：** 先定位影响任意标签的头，再解释映射翻转及频率/顺序偏置。Key承载demo特征、Value承载输出词，Query含输入及上下文特征。
2. **证据：** GPT-J/Llama，五种分类任务；头消融、投影读数、标签翻转、顺序与数量变化，并以定向读出修正测试解释。attention变化与Value词方向的比较主要是观测分解，不能当独立移植的充分性证明。
3. **已有所有权：** label→Value、demo→Key、QK相似度、上下文影响Query，均非ICES新构件。语义标签与任意标签的TR/TL划分也不应直接套作我们的两类来源规则。
4. **对E91：** 模型读取A时可能继承B信息，因此“禁读B”不预设能隔离规则。我们要检验B的namespace是否改变A自身读取，而非重做Key/Value解释。
5. **设计学习：** 有用的机制解释应对映射翻转、数量和顺序同时产生可检查预测。定位头只是起点。
