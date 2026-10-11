# How Few-Shot Examples Add Up：QK/V机制的功能范围（2026-10-11正文核对）

原文：https://arxiv.org/html/2605.16591v2 （ICML 2026；§5、§6、Appendix E.2–E.3、K、L）。

- 原问题：示例上下文化为何改善function vector？不是首次发现上下文化，而是routing/content之间的竞争。
- 证据：上下文化/无上下文化的QK与V做2×2交换；读取最终FV，再以跨层/强度扫描的最大注入准确率评估。QK因果贡献通常更稳定；V的效果随任务变化。§6发现示例变化能改变偏好哪些示例，query变化常改变总访问量。
- 重要方法限定：E.3的K/V只替换**最后token消费的消息**，不替换其它query位置所用K/V；Q也只在最后位置。不能把这套结果当整个示例形成程序已完整逆向工程，也不能由此声称ICES第一次区分QK/V。
- Appendix K：输入输出映射改变后仍可诱导相近FV效果，未必需要唯一task identity。Appendix L：在fixed routing下比较V的几何变化，属于探索性解释；不是各个来源的规则语义已被证明分开。
- 可学习动作（论证重建，非发现时间线）：先由attention分配提出routing解释，再用独立QK/V反事实让content解释竞争，最后反问对齐信号来自哪里。
- ICES距离：E91/E106是在query零访问B且A原文/标签固定时，检验B规则对A形成后的证据的功能依赖；E108以完整pre-label→label的阶段交换补齐评论内容路径的范围。共享输出下的来源边界，是具体增量候选；宽泛contextualization、QK/V、总mass/组内选择均归原论文，不重新命名。
- compression risk：若ICES只发现普通QK再加权，原文能吸收；需要说明Source条件化的证据形成如何使query选择与规则信息来源分离，并给出新反事实预测。

### E114设计对应的正文再读（§5 / E.3）

原文2×2在两种V背景都测QK条件作用，反向亦然。学习点是背景依赖必须实际测，而不是先假定贡献可加；不是仅复制一个factorial术语。E114相应交叉A位置的形成缓存与B位置上下文化环境，report signed交互而非只对absolute差值作解释；固定B缓存并非固定live query。两模型新词句signed交互.775/.321、历史答案KV预测原生label效果保持，为Source功能来源问题补齐native联系。它不是原论文的FV-QK/V变量，不能写首次分解路由/内容或一般非加性。

本次venue corpus nearest（关键词in-context learning label contextualization function vectors）返回本论文为最强直接accepted近邻；arXiv新检索未提供精确撞车证据，但不能将检索阴性当首次证明。最强对齐依据仍是指定全文的实际实验对象/接口与claim范围，而非摘要匹配。

### E117→E118：由附录K的弱task identity解释逼出功能竞争

再次核正文Appendix K（映射改变、Q patch、FV注入准确率）：相近QK对齐未必说明相同input→output task。E117已确认A-label反事实令Food/Service同增，不能由此挑一个方面命名criterion运输；single A本已有Service偏好。E118正交B criterion与其private code，在固定B输出stream与内容多重集时测代码反转是否跟随指定方面，并在相同recipient比较形成后的label/历史答案边。这个实验既允许task-specific关系，也允许共同语义增益胜出；一般semantic manifold/QK解释归原文，新的实测对象是Source历史关系的功能来源。
