# Thought Anchors: Which LLM Reasoning Steps Matter?（预印本）[主文§2–6、8]

[原文](https://arxiv.org/html/2506.19143)。2026-10-11实际读上述方法/结果/限制，未完整读附录或代码。

1. **形态：** reasoning过程测量；方法拥有权不属于ICES。
2. **压力：** 强制早停答题会漏掉规划句对后续推理的影响；最终会写出的算术句又可能高度过定。
3. **前提改变：** 从同一prefix生成语义不同的后续，测最终分布与后续步骤，分别看轨迹组织和答案信息。
4. **idea来源：** RECONSTRUCTED论文链条；不冒充研究日志。
5. **距离：** CoT faithfulness、句删除与fork resampling；将resampling、receiver attention、句间干预并列核对。
6. **方法：** R1-Distill-Qwen14B、MATH40正确/错误轨迹；每句100续写，温度.6/top-p.95。语义不同续写的条件KL；attention suppression测后续token KL。MMLU扩展使用Qwen3-30B-a3b。
7. **边界：** 原问题按25–75%难度挑选且大规模扩展聚焦正确轨迹，不能沿用为无筛选能力证据；少量语义不同续写方差大；attention受位置影响，mask会造成分布变化。单看reasoning文字不是该论文的因果证据。
8. **研究动作：** 区分一个结论被写出来、它改变后续计算、它只决定最终输出。让后续继续运行，而非立即强制答案。
9. **对ICES：** E95的错误文字显示局部标准与共同约束有冲突，只作线索；若研究Goal选择的推理程序，需让标准/私人偏好/新review给出不同预测并干预后续。Qwen3.5有linear-attention状态，不能将只改full-attention边当完整删除。
