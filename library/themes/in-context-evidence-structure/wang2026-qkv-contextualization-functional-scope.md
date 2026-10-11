# How Few-Shot Examples Add Up：QK/V机制的功能范围（2026-10-11正文核对）

原文：https://arxiv.org/html/2605.16591v2 （ICML 2026；§5、§6、Appendix E.2–E.3、K、L）。

- 原问题：示例上下文化为何改善function vector？不是首次发现上下文化，而是routing/content之间的竞争。
- 证据：上下文化/无上下文化的QK与V做2×2交换；读取最终FV，再以跨层/强度扫描的最大注入准确率评估。QK因果贡献通常更稳定；V的效果随任务变化。§6发现示例变化能改变偏好哪些示例，query变化常改变总访问量。
- 重要方法限定：E.3的K/V只替换**最后token消费的消息**，不替换其它query位置所用K/V；Q也只在最后位置。不能把这套结果当整个示例形成程序已完整逆向工程，也不能由此声称ICES第一次区分QK/V。
- Appendix K：输入输出映射改变后仍可诱导相近FV效果，未必需要唯一task identity。Appendix L：在fixed routing下比较V的几何变化，属于探索性解释；不是各个来源的规则语义已被证明分开。
- 可学习动作（论证重建，非发现时间线）：先由attention分配提出routing解释，再用独立QK/V反事实让content解释竞争，最后反问对齐信号来自哪里。
- ICES距离：E91/E106是在query零访问B且A原文/标签固定时，检验B规则对A形成后的证据的功能依赖；E108以完整pre-label→label的阶段交换补齐评论内容路径的范围。共享输出下的来源边界，是具体增量候选；宽泛contextualization、QK/V、总mass/组内选择均归原论文，不重新命名。
- compression risk：若ICES只发现普通QK再加权，原文能吸收；需要说明Source条件化的证据形成如何使query选择与规则信息来源分离，并给出新反事实预测。
