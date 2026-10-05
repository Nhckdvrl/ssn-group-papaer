# DeltaLogic: Minimal Premise Edits Reveal Belief-Revision Failures in Logical Reasoning Models（2026）

[primary摘要](https://arxiv.org/abs/2604.02733v1)，[HTML](https://arxiv.org/html/2604.02733v1)。本次仅核对摘要/任务定义入口，未完整核对结果正文。arXiv comments标ICLR2026 Logical Reasoning workshop，未查正式proceedings。

从FOLIO/ProofWriter把固定premise推理改成initial conclusion→最小premise edit→判断应保持/改变的短episode。摘要报告Qwen3-1.7B 30-episode subset initial .667/revision .467，inertia .600；还有abstention/control稳定性压力。这些小样本不能外推普遍规律。

对I01：local minimal evidence revision、旧结论惯性、over-flip都已被邻域讨论。增量不能只是改一个自然句再看模型答没改；需要“哪个事件关系被什么后文重新使用/覆盖”的可预测结构。当前不把新近邻当territory关闭理由，也不自动转向训练/logic benchmark。
