# Unveiling the Limits of LLMs in Inferring Pragmatic Meaning from Non-Verbal Responses（ACL2026）

来源：https://aclanthology.org/2026.acl-long.2101/；公开review/分数未核对。

1. **形态 / 阅读：** benchmark+失败模式；intro、method、RQ1/RQ2/error、CoT/ICL/context ablation、conclusion/limits已读；logit-lens完整方法与附录A–C未全读，code未复现。
2. **压力：** verbal MCQ成功能否推广到silence、emoji、括号动作？全是文本输入，不是视觉模态替换。
3. **改变前提：** indirect verbal explanation→nonverbal surface。idea来源DOCUMENTED，非我们首创。
4. **方法 / 证据：** 5选项，错误包括abstract explanation/literal/contrastive misinterpretation；人类与model同faithful-engagement指令。小模型最大约59pp降幅，大模型仍有至32pp；CoT效应依family相反，fewshot效应依规模；移除faithfulness指令4模型都降。
5. **短板：** gold intent和faithfulness是交际规范，不是silence自然必有该意图；single next-option/CoT prompt差不等机制。logit lens不提供因果解释；ICL改善不自动latent能力已被恢复。
6. **最近邻 / ownership：** Hu fine-grained、Multi multilingual、PaCE overinfer、nonverbal context norm。表面形式改变造成under-inference与family不同CoT方向已拥有。
7. **可迁移动作：** 明确候选命题、忠实参与/未知参与两种norm，保留各类错误。测field boundary而非claim文本nonverbal首次。
8. **对我们：** 暴露global tendency可能不足，推断suppression不应以无声总有暗示为金标准。
9. **边界：** 未运行原code，不称baseline复现；完整global scalar因果未证实。
