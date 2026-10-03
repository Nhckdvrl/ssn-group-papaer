# LLM Beliefs Are in Their Heads（ACL2026 main）

**阅读：完整main§1–6/related/limitations及关键附录A1prompt、A3split；35页A4各模型所有图未逐项读，代码/原数据/steering未复现。** [论文](https://aclanthology.org/2026.acl-long.1905/)，[代码入口](https://github.com/Supersheep7/beliefs_llms)，公开评审未核对。

1. 形态：哲学构念×可操作标准×机制测量。六模型family（GPT2/Yi/Pythia/GPTJ/Llama/Gemma，部分Base/Instruct），four criteria Accuracy/Use/Coherence/Uniformity，在residual与head两个层级测。不是一个probe acc+机制故事。
2. 压力：truth线性可解码不证明belief，需要是否被用于断言、跨逻辑一致、跨domain同构；以minimal functionalism明确论证范围，拒绝意识/有精神生活主张。
3. premise变化：以多个共同必要要求检查构念，每项使用相应测量：supervisedlinearprobe、mass-mean steering+randomdirection、isotonic calibrated pseudoprobabilities的逻辑约束、crossdomain validation。
4. 来源DOCUMENTED：Herrmann/Levinstein2025 beliefs criteria、Marks/Tegmark2024 truth方向、Burns2023、Bürger2024 polarity confound。把哲学标准变成可驳的共同预测，不只复刻已知truthprobe。
5. 与最近邻：已有truthrepresentations→多标准；已有residual→定位heads；已有negation coherence failure→丰富训练集后仍中等并明确边界。与我们的“归给说话者的commitment”是不同对象，不能因model自身有truth方向推speaker attribution解决。
6. 设置：accuracy5fold；heldout50%做Use，其中100探索grid、fullpartition报告（探索子集含报告，非完全independent）；coherencepaired logical versions同row 70/30、5seeds；uniform75/25domain10seeds。只top3residual>80%模型进入后3标准，不能外推全部六families都满足。GPTJsteering弱；Llama/Gemma IFT更敏感，head方向通常更有效。
7. 限制：层/head按accuracy选最佳，fewshotselfreport是恢复过的reader，对logits/probe入口不完全同；steering方向对比含clip at.05、strengthnorm与随机baseline，effect大小可有不同含义。Appendix单run图与mainseed汇总区别。true/false数据简单，线性probe可能tracking correlatedfeature；steering不能排除全部语义混杂。无需把这些判paper无效。
8. 可迁移动作：为scientific object定义多个行为应共同满足的条件；用条件依赖、使用对照、独立泛化检验缺哪一环，机制必须随机方向与输出policy对照。泛化失败信息量高于+smallaccuracy。
9. 对我们：不会立刻训probe“找到pragmaticneuron”；当前先做自然context/head无关的行为边界。belief-like真值、speaker attribution、人群norm、合适沟通动作四类不能混。与Pan/Bergen2025在定义上并不矛盾，模型有某种functionaltruth结构≠可以预测人类所有projection。
