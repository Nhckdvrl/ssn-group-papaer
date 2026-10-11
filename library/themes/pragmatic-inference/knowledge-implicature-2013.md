# Knowledge and Implicature — Goodman & Stuhlmüller, Topics in Cognitive Science 2013

[原出版页](https://onlinelibrary.wiley.com/doi/10.1111/tops.12007) · [公开出版PDF](https://sites.socsci.uci.edu/~lpearl/courses/readings/GoodmanStuhlmuller2013_LangSocialCogImplicatures.pdf)。全文12页（含模型、两实验、拟合、讨论、参考）已读；原WebPPL/人类raw未复现。

- **idea来源 DOCUMENTED：** 把言语看作有信息目标的行动，听者反演说话者在其知识状态下的表达选择。不是从benchmark低分找gap。
- **科学对象：** 共享speaker access怎样改变some与numeral含义；不是统一的“无知识就不推断”。部分知识可以完全或部分取消具体含义。
- **方法：** Eq1 Bayes listener；Eq2对speaker belief下utility取期望后softmax；Eq3 literal listener surprisal；Eq4把未知观察按hypergeometric边缘化。Some literal≥1，numerals lower-bound，alternative set决定可推断部分。语义假设不是所有语境下的gold。
- **实验与ownership：** 两组各50人、六自然场景，先下注prior，再speaker access+utterance、world-state bets、知识check；knowledge方向threshold70过滤后分析，另用全部人的prior/knowledge扩展拟合。access2/one只支持not3，而不必排除2。全部数据拟合RMSE8.36/r.95；过滤版本RMSE9.01/r.96；这是同数据拟合，不是held-out一般化或机制证明。
- **阅读改变：** speaker说one≠直接给出了观察到恰好one的事实；在lower-bound语义下，把access2/one的not3全当literal deduction是错的。必须区别“知道exact观察结果”的hypergeometric事实更新和“听到一个可选表达”的RSA沟通证据。EPITOME沿用此区分；候选2/3不能强制共同negative。
- **近邻距离：** 原2013已拥有knowledge×pragmatics的细粒度交互；EPITOME已对LLM复现与detect/use。我们不能claim发现knowledge gating或第一次RSA测LLM；可能增量需真实stage改变条件证据结构、跨现象与读数边界。
- **工具风险：** ProbLang教学章节给sample-belief与expected-utility两个实现变体，与论文Eq2不能不核对就混称原模型。模型缺乏可用表达的知识状态/zero-support需要查原实现，不擅加epsilon作gold。当前未拟合一个“pragmatic ability参数”。
