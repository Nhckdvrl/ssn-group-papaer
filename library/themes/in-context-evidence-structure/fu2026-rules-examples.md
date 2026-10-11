# LLMs Learn Better In-Context from Rules than from Examples（2609.03213v1）

**本轮阅读：** [主文§2–4、B.1/B.3](https://arxiv.org/html/2609.03213v1)；完整F prompts与全部模型数值未逐条校对。[作者页](https://xiangfu.site/publications/)称EMNLP2026 Main，本轮未核对会议正式proceedings。Seungmin Cho不是Hakaze Cho。

1. 问题：同一潜在任务由rules、examples或二者说明，何种信息形式更有效，哪些任务/模型因素改变结果？
2. 改变的前提：已有方法显示两种提示激活不同机制，但**机制不同不推出联合提供会有额外表现收益**。这个认识桥比增加模型表更重要。
3. idea来源（RECONSTRUCTED）：从common function vector/不同提示研究的应用推论，转到直接比较；五任务有不同先验预期，而非假定rules必胜。论文不是发现日志。
4. 方法：game、operator function、人工noun class、lexical category；规则说明迭代消歧，examples无额外任务说明，minimum coverage含primitives/labels/代表案例。Operator Function覆盖采样参数的argument permutations；coverage描述不等于任意假设空间下唯一可识别性。
5. 边界：rule控制显式约束更多，examples条件无任务族说明；不是严格信息等价的编码操纵，也未做白盒因果机制。学习模式优势随任务变，不是所有examples无用。
6. 对ICES：E77 direct100与inferred较弱、E78给code后改善的一般方向不能立novelty。本组明确公开两个候选函数，使各Source的2/7关系唯一辨认函数，减少任务族歧义；仍须证明Source选择/函数应用为何不同及其成立条件。

定位，非自动科学判决；增加表面新格式或再报一组rule superiority不能自动跨过贡献门槛。
