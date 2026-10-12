# Do large language models and humans have similar behaviours in causal inference with script knowledge?（*SEM2024）[证据级别：部分正文 + 上游资产审计]

[Primary paper](https://aclanthology.org/2024.starsem-1.34/)，Hong / Ryzhova / Biondi / Demberg。实际读取§1–3.2、§4.6、§5.1–5.2、§6–7及部分方法Table1；其余human统计细节/附录未完整核对，未复现。PDF本地cache 2,222,415bytes，SHA256 `733a19dd2b5c19a44efcf10f02067714b34d16dcdd3233a78a17f458942bc9dd`。

1. 形态：自然日常script刺激的人类阅读与LM条件预测对照。
2. 压力：模型是否由先前事件及脚本知识推断后续事件，是否只被相关词的提及触发。
3. 前提：事件A被肯定、否定、未提及，应对依赖A的事件B产生不同预期。
4. 来源（DOCUMENTED）：经典人类causal inference/阅读实验与LLM计划行为压力，作者明确讨论topic priming解释。
5. 距离：否定先决条件和省略先决条件的人机不对称；不是首次证明一条事实会影响后文。
6. 方法：21故事×3条件，A与B之间约70词；人类self-paced reading与多种LM surprisal。§5.2另问B前资源是否可用，允许cake decorations/sprinkles这类不同表面词引用。GPT3.5多数能够回答资源不可用，预测结果却不完全跟随。
7. 边界：**该文已经拥有state-QA/后文预测不一致、availability依赖与topic priming竞争**。不能将E38正确回答/不完全消失的续写效应卖首次知道/使用gap，也不能改几条cake故事叫全新因果benchmark。小21故事、读数用途不同。
8. 可迁移动作：用现成自然事件后果区分真实availability与叙事alternation，在同一个role-revision问题内增加功能读数；先独立审具体转化与gold。
9. 对我们：I01精确增量在同角色信息对旧/新event、同/不同action、同/不同actor的**方向与边界**，不是generic否定失败。若转向资源后果，必须保留关系修订与对照，而不能复制本论文已有结论。

资产已按license/revision/hash/stat审计在[记录](../../../workbench/incremental-interpretation-revision/results/D0-CSK-source-audit.json)，63原始行只在cache、零改写/零推理。HF pinned `d035c8d85d19e64be96acdaf2ca18b8f73f2bf10`，Apache2，镜像直连、无代理；CSV原字节含zero-width字符，暂保留不清理。代码repo与data独立revision，代码repo只有eval脚本，数据实际从HF取得。
