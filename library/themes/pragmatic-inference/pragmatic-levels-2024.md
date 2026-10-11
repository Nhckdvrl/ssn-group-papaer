# Communicating with Speakers and Listeners of Different Pragmatic Levels（EMNLP2024 main）`[证据级别：正文全文；原图/代码未独立审计]`

[原文](https://aclanthology.org/2024.emnlp-main.1213/)，Naszádi/Oliehoek/Monz；正文§1–7全文、方程与表已读，references仅浏览，Figure2曲线未数字化、[原代码](https://github.com/naszka/rsa_backward/)未审，不称数值复现。

- **idea来源 DOCUMENTED：** 人类speaker-specific sophistication＋已有RSA通常把pragmatics加在固定lexicon之上。改变“literal语义表示与递归推断可分训练”的前提，比较训练时参与递归与只在推断时升级。
- **结果与边界：** 原假设matching更好并未简单保住：S1更长、更明确，对L0/L2都更有利；不完美lexicon让聪明listener仍受益于显式语言。Table2同lexicon L0/L2接S3为80.5/81.2，接S1为85.5/85.6。不仅匹配层数，还有学习数据的信息量。
- **研究动作：** 可控真实generative strategy，固定lexicon后变推断与不同lexicon训练后变伙伴分开；观察相同平均成功的不同过程。与Mayn2025直接相接，但这里CNN/RNN ShapeWorld而非LLM或自然人类判断。
- **限制/ownership：** 有限1–2word、cost=.6、N=5/Corr=1选为最大speaker-type effect，原文公开；fixedseed不是training多种子，图所示十环境不是十training seeds。无穷自然alternatives未解决。RSA depth mismatch和language-learning integration已有，不claim首次发现角色不对称。
- **如何从中发展 RECONSTRUCTED：** 需要区分语义掌握、预期表达选择、实际listener推断。E49/E50只有文本任务，不能从joint Bayes距离倒推RSA深度。若各角色得分都高，仍需可迁移的条件预测来识别联系；失败/方向改变首先限定测量，不另加局部条件救story。
