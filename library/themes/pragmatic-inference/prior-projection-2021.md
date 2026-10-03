# Prior beliefs modulate projection（Degen & Tonhauser, 2021）`[证据级别：全文]`

[作者原稿](https://alpslab.stanford.edu/papers/2021DegenTonhauser.pdf)，15页正文及A–D已读。数据核对借助NAACL2025原repo，不宣称重跑原混合模型。

1. 形态：自然语言的受控心理实验与理论压力。
2. 压力：projection常被视作predicate的二元语义属性，先前先验操纵结果冲突。
3. 前提改变：听者的主观背景信念可调节归给说话者的承诺；主观信念不要求真实，不能叫knowledge。
4. 来源DOCUMENTED：Mahler与Lorson不同材料/操纵的冲突；跨20内容、20谓词，个体内与独立组复制。
5. 距离：相比政治身份或姓名性别先验，显式20种背景属性；相比单一predicate，跨认知、情绪、交流、推理predicate。NAACL2025已将其用于LLM/RSA，首次world-prior影响LLM不是我们的claim。
6. 方法：Exp1保留286人，20目标题+6控制；Exp2 prior75人、projection266人。原Human高−低projection效应跨独立组复制，个体先验解释优于组均值。我们核对发布7436行=286×26，其中5720目标/1716控制，不是额外新样本。
7. 短板：20内容、英语、显式背景；人类slider与生成numeric并非同一反应过程。高−低不是推断许可positive/negative，不产生SDT gold。
8. 研究动作：将背景先验测量与含义归因分开，改变prior而保留utterance，独立人群复制以排除测量诱导；需要先写连接读数与构念的假设。
9. 对我们：E38/E39驻留原source。先问背景信念与speaker certainty能否被分别测出；不能把二者差异解释成knowledge-use gap，不能因拟合RSA就宣称显式神经belief必要。
