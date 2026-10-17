# SPASM — 2026角色对话视角研究

- 原文<https://arxiv.org/abs/2604.09212>；作者<https://github.com/lhannnn/SPASM>；本地pin ee49b9288498688225405f2720b511261b306f50。PDF SHA1817f78a5c4f677ae28307edb52cb0950ead205c569960a223f6a643e001069e。
- 已读方法/主表、Appendix M机制解释、concat/ECP/human eval协议与公开资产；未复现模型数值。论文为角色对话一致性，非原生物理NPC执行。本文不作为投稿目标。
- **DOCUMENTED：** ECP将speaker-label历史转换为egocentric perspective以减少角色混合；50persona×3conv、temp0、20utterances。concerns/emotions/motivation自述embedding与初始profile比较。DeepSeek motivation差−.006、p=.46，不能一律称显著。human比较每pair50，κ=.729，总200且pair预算非完全对称。
- **SOURCE事实：** 当前public仓库主要dataset，DeepSeekV4Flash500×10资产，不是论文全部9模型实验generator；不可声称下载即完整再现。source/profiling自报不等于action-world。
- **RECONSTRUCTED：** 角色混淆可能由历史视角编码而非人格消失→变换历史视角，分别测自述和人工对话。这是已知视角/echo/self-feedback机制。
- **解释/未排除：** 原动机自述变化≠角色实际战略漂移；同会话自身台词priming已有owner。Appendix M是作者解释而非每条都独立因果验证，不用它给LIGHT行为直接定性。
