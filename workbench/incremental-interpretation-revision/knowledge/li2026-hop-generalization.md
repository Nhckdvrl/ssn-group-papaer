# Scaling Reasoning Hop Exposes Weaknesses（ICLR2026，作者v2主文）

证据：作者[arXiv v2](https://arxiv.org/html/2601.21214v2)主文§1–6完整；AppB/C、F1–4文字与G1–4/G6–9设置结果已读，D任务例子与长H图未逐项深读。OpenReview接收稿搜索页核对Published ICLR2026，正文用作者v2（2026-05-01）。HTML外置SHA2b641719b02acaf48bb63319bb64085c3b14f1e5f7189ca0a9a63488898f8d88。

1. **形态：** 错误类型定位→机制竞争→动态干预方法，最终用完整任务收益接回机制。
2. **压力：** 同一种技能增加hop后失败，error accumulation只描述结果；逐token机制工具不知该看哪一token，直接全CoT定位难。既有rule-finetuning/looped架构成本或适用条件不同。
3. **改变前提：** 错误并非均匀，每任务少数特定操作承受失败；已学正确计算和错误捷径竞争，可能通过减掉错误影响来恢复，而不必重训整个大模型。
4. **idea来源（RECONSTRUCTED）：** Dziri compositional error accumulation→Anil/position-length/RULE学习→将长轨迹投到可判对错的关键操作→IOI/Geva factual extraction与CoT circuits的写答/处理分工→发现跨错误类型可用同一head knockout→训练选择器把post-hoc干预变成推理时方法。关键动作是把可解释的失败入口连接到端到端后果，不是先找head再给它命名。
5. **近邻距离：** Dziri给现象，此文追因果入口；Dutta/Cabannes给CoT机制，此文连接机制与失败条件；Geva factual recall为工具祖先，不是新任务发现；DoLa改logits，此文处理路径；LOFIT任务适配，此文错误操作训练、迁移新任务。未据相近部分关闭研究空间。
6. **方法/规模：** 七任务Parity-NL/LLC/MDM/MOAS/CLF/NumS/ObjC，重新随机实体数值，Qwen2.5-7B/Phi3/Llama3-8B/Qwen3-8B。先按具体操作错误分类，≥30%为key。定位集合通常每侧10，另测100错/300对。aw-head为局部residual减去head后的normalized logit-lens概率差；processing为all-token head-zero后最终概率变化。选择8–10候选head，Qwen2.5-0.5B LoRA分类器，5任务各约20k生成筛错误/可修复标签，ID留500、OOD200。熵>.3触发，top3 head分别重算多数票；不是单forward免费干预，也不是完全无训练。
7. **结果/边界：** 主表每任务100题、3seed，Q2平均41.7→48.5，oracle61.3；Phi+4.9、Llama+6.4、Q3+1.6pp，Llama ObjC−1/MDM仍0。Big-GSM仅Q2/Phi +1.7/+1.4pp；附录14B及R1-distill +4pp（每任务10错误定位、任务特定head、阈值.4），不等同主训练selector。invalid direct answers被排除，范围不可拿来认证全部自由CoT能力。高熵均值不等于错误detector精确，Q3 LLC对/错熵同为0；head“正确/错误”由行为影响定义，信息解释还依赖logit-lens。主文本hop→竞争加强仍称假说，input规模/中间状态同时增长，不能当完全独立hop因果因素。
8. **可借动作：** 先选择有语义地位的错误操作，减少搜索维度；一个核心causal recovery后再做有用方法，借held-out任务使定位获得后果。不必复制完整head网格，我们的E70先找哪些源断言改变，E71只切一条后续消费路径。
9. **对我们：** 一般“模型有正确候选却被错误路径压住”已有owner。待证新问题必须是自然解释修订的依赖结构：正确的局部表达何时成为下一关系错接的来源、修订时到底应撤销哪种绑定。若证成，方法可由这个边界长出，而非把TCR换GP数据称创新；现在仍是假说。
