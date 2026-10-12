# iGRPO: Self-Feedback–Driven LLM Reasoning（NVIDIA，2026作者v1）

证据：[作者全文](https://arxiv.org/html/2602.09000v1)主文§1–6完整；附录C/D全文、E文本/表格已读，A完整推导与B大规模实验未深读。SHA40e618a037bc788a21258ba81aabc5e7948c2dab4c4c327604ce9f748d1f848e。会议接收未核对。

1. **形态：** 方法题；改变训练所见上下文分布，保持GRPO式目标。压力是独立rollout没有利用模型自己的较好尝试。
2. **idea来源（RECONSTRUCTED）：** Self-Refine/Reflexion提供迭代改善，STaR提供验证后自举，GRPO提供低成本相对奖励→将当前policy高奖励draft作为下一组rollout的训练上下文→强基线、多尺度、多benchmark验证简单接口改动。相对Critique-GRPO不额外要求生成critique，相对Self-Verification不让同一policy兼任主要奖励来源。
3. **机制：** Stage1采N个draft，外部scalar reward选最好者，不对这一阶段求梯度；Stage2原题加draft采G个refinement，只有这组接受GRPO更新。训练中动态自条件，推理仍由原题直接单次产生。它不是两阶段test-time算法，也不是全无外部反馈的自纠错。
4. **规模与结果：** MATH7500/AceReason9400，五个7/8/14B主比较模型、六数学benchmark，同总8次采样。相对GRPO宏平均增益NemotronH8B +3.96pp、DeepSeekQ7 +1.58、OpenMath7 +1.05、DeepSeekQ14 +1.73、OpenMath14 +1.27；8B相对最强critique基线+1.65。AIME评估64次、其余8次，pass1；训练cap4096、评估cap65000。DAPO/GSPO wrapper分别+1.19/+1.11，强起点实验另报告GPQA/MMLUpro迁移。数字是作者结果，不是我们复现。
5. **成本与文内不一致：** AppD单独cap2048测量，GRPO/iGRPO 83.3/94.1 GPUh、0.41/0.34 samples/s、峰值54.9286/54.9349GB；相同采样数不是相同时间。主文batch1024、AppC global128；主文binary accuracy reward、AppC accuracy与format各权重1，复现需核对代码。DeepSeekQ7表列base Avg61.93与六列算术均值67.8167不符，不能复制该base gain。
6. **证据尺度：** 1−(1−V)^N仅证明给定policy成功率增加时best-draft期望奖励上升，不证明整个优化或原题推理单调改善；较慢entropy collapse是相关读数，不因果认证增益来源。更少Stage2可求梯度rollout、更长条件输入仍有成本差。
7. **可借研究动作：** 新方法不必靠复杂新损失；可以精确改变一个错误发生的接口，然后证明对强基线的收益跨模型/任务存在。对我们，若找到局部修订对后续解释的规律，要针对实测路径设计干预；当前没有证据支持直接开RL或数学新线。
