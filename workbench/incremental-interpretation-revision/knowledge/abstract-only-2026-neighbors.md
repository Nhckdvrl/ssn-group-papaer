# 2026-10-12 仅摘要级核对的近邻（ABSTRACT_ONLY；每篇待主文读）

> 本卡集中登记本轮只读到摘要/检索片段的论文，避免制造多张空卡。每条写明已知内容、未知部分、与本对象的距离；升级为主文阅读后应拆为规范卡。

## Emura & Sugawara 2026 — A Dual-Task Paradigm to Investigate Sentence Comprehension Strategies in LMs（ACL 2026 main, long.552；arXiv 2604.26351）
- 已知：算术双任务使GPT-4o/o3-mini/o4-mini在合理/不合理句上的准确率差距扩大，解释为资源约束下转向合理性推断（Gibson噪声信道式）；代码 github.com/reiemura/llm-dual-task。
- 未知：是否含GP；项目数；每条件数字。
- 距离：谱系与Asami 2024相同（资源→启发式）。我们对象是晚到证据后的结构重写，不是资源；但其“工作记忆负荷操纵”可作为我们X1的对照条件（预测：负荷不改变替代依赖断言率，若改变则重建失败与资源有关）。

## Oh & Demberg 2026 — A retrieval conditioned rebinding circuit for dynamic entity tracking（arXiv 2606.08644，v2 2026-09-11）
- 已知：Gemma与Llama上用因果干预找到“检索条件化重绑定”注意力头电路；Gemma绑定信号在Q/K子空间，Llama主要在K向量。
- 未知：任务细节、数字。
- 距离：这是**显式状态变化**（实体被重新赋值）的重绑定机制；GP的替代依赖是**隐式**的（没有一句话说“其实是被动”）。可借其干预设计于X2（动词位置状态移植），并预测：显式更新有电路，隐式结构更新可能没有专门路径。

## Steele, Wen, Han 2026 — Belief-reality separation lives in routing over a shared value slot（arXiv 2607.11945 v2）
- 已知：信念与现实共用一个值槽，差别在查询位置的路由子空间；断言信念直接绑定，推导信念经可见性门控lookback；3B–7B间涌现。
- 距离：方法参照（路由vs内容分离），与我们“知道结构但不实例化命题”的分离可类比：框架信息可能存在但没有路由到断言。

## Futrell et al. 2019 — Neural LMs as Psycholinguistic Subjects（NAACL 2019；arXiv 1903.03260）
- 已知：大数据LSTM与RNNG同样在长跨度上维持句法状态；小数据LSTM弱。
- 距离：LLM-GP行为研究的起点之一（surprisal范式）；Li 2024、Amouyal 2025从它转向理解问句。

## Kim & Schuster 2023 — Entity Tracking in Language Models（ACL 2023；arXiv 2305.02363）
- 已知：盒子/物体状态变化任务；只有代码预训练的GPT-3.5零样本能追踪；微调T5可泛化。
- 距离：显式状态更新线的行为起点；Prakash 2026、Oh & Demberg 2026、Tang 2026是其机制后继。

## CASTLE — Causal Attention with Lookahead Keys（arXiv 2509.07301）
- 已知：让早期token的key随后文更新，保持自回归。
- 距离：架构层面对“早期表示不能被后文重写”的回应；可作为未来“架构是否是重建瓶颈”的判别对象，当前无可用checkpoint，不入实验菜单。

## Clark, Levy, Gibson 2026 — noisy-channel GP regressions（已有规范卡 clark2026-targeted-noisy-channel.md，CoNLL 2026 Outstanding）
- 本轮只核对与本对象的关系：人类回视到“可能出错的词”，推断错误而不是替代结构。对应我们E80 TRUST/NOISY的失败：模型的替代解释之一是“输入有错”，这与“重建被动结构”竞争。X1应加入一个“输入可能有错”对照以分离两者。
