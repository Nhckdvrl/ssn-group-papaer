# The Influence of Prior Semantic Knowledge in Noisy Channel Interpretation（QJEP2025 online / 2026 volume）

来源：[最终论文](https://journals.sagepub.com/doi/pdf/10.1177/17470218251383526) · [原OSF](https://osf.io/k5vqj/)。作者公开稿SHA b339adceaa951c96bc5ef0b1a5ac107922a79a1329542a68021225bfd6de37c2。

1. **阅读：** 正文背景、两实验、by-trial分析、讨论/notes完整读；公开data_analysis.R主要数据管线/模型/参与者分布已读，图未独立视觉校对、MCMC未重跑。
2. **压力 / idea来源：DOCUMENTED。** 旧meaning-prior证据也可能由实验长度、适应与参与者策略解释。已有结果仍值得进一步区分，不因前人做过就缩题。
3. **改变前提：** 固定长度与critical句，只改变exposure的语义合理性，并以更多参与者独立复核。
4. **证据短板：** 524名retained的两轮结果支持条件变化；trial-level不是每个效应都显著，更新幅度机制未识别。不能把literality增加自动叫理解退化。
5. **对我们 / E54：** 公开csv已去Qualtrics元数据，但原脚本仍删前两行并取首行prompt；材料正文缺失，直接照搬会把response当prompt。重复ID跨条件须按原全局规则核对，不能逐文件过滤后声称parity。原数据在本地，语言材料导出只留白名单字段。
6. **增量方向：** 先重建可用原source与norm，再检验训练是否学会区分“信号受损”和“世界可能很奇怪”；这是待研究对象，不是此论文没做LLM就自动novel。
7. **研究动作：** 审计最简单替代解释→等条件复核→动态边界。值得借鉴的是解释的识别，不是增加benchmark数量。
