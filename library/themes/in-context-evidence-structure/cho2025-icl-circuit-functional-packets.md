# Revisiting In-context Learning Inference Circuit（ICLR 2025）[补充正文核对：§3.1、§4.1、附录C；2026-10-11]

原文：https://arxiv.org/html/2410.04468v3

- §3.1 forerunner在当前label出现之前形成输入表征，先前demonstration可增强这种表征；因而“输入编码完全独立于过去例子”不是原文解释。
- §4.1错误label不改变forerunner→label attention的copy选择，但在label token上文本feature与label语义的重叠有加强/抵消；这是较具体的label-denoising候选，不能把“label改变表征”本身称ICES新发现。本文证据主要为attention/centroid/kernel alignment及后续电路消融，几何相互作用解释并非完整因果分量分解。
- 附录C在单任务实验里用attention图及删除/替换分隔符支持分段；不应将“block interference”宽句读成来源特定规则已经绝对独立。当前ICES的真实增量候选在于合法多源规则的信息边界，不能以这句宽话造虚假的反常。
- 可学习研究动作：将不同步骤的测量相互约束，区分copy操作与复制内容、预训练label语义与先前demo形成的规则。
- E91已验证raw A不变时B输出namespace改变A的K/V，不能从这个事实直接选择“原输入编码改变”或“后续label-conditioned prototype改变”；两种形成阶段还都可能。E102解决Source-field功能接口的地址/内容解释，不能单独分解A缓存的形成。先等待这次有阳性的机制反事实，再按具体竞争预测设计内容实验，不自动增加门槛。
