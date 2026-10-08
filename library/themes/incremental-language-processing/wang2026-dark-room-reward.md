# The Dark Room in the Reward Channel（作者v2，独立研究者预印本）

`[证据级别：主文精读＋指定方法附录]` [原文](https://arxiv.org/abs/2607.21273v2)。Yu Wang independent；35页，SHA8db5746b001a2634f1f05b42f501a603cdf84bd36a09619dcaa203bbc626bc8e。Under review；不按作者声望直接判质量，也不假定已顶会接收。代码/74arm ledger历史尚未独立核。

1. **形态/问题：** agent RL失败机制与信号传递比较，不是新world-model recipe。差分next-observation预测reward在std-normalized GRPO中形成预测率1/任务率0的吸收行为；安全的loss delivery收益可能来自aux更新而非正确内容。
2. **idea来源（RECONSTRUCTED）：** 原本加dense reward补sparse学习，意外全部collapse；对接active-inference dark room，再从return有界与advantage归一化分离找到条件系数抵消。用同信号换delivery，把救援效应归属到optimizer而非“更懂世界”；由placebo结果发展第二个叙事。
3. **近邻距离：** PBRS/Dr.GRPO/dense prediction已有；这里将特定policy-dependent difference signal、all-fail/低task spread及pooled step normalization串成可检验失败路径。兼容RWML/VAGEN只说明不矛盾，未证其它方法被同机制覆盖。
4. **理论/实现关键：** Φ是policy自己的预测准确率，λ(Φt−Φt−1)虽episode telescope但不是policy-independent PBRS保证。normalizer实际在同group全step samples池化，n≈4×50而非仅4条trajectory，优势仍有限上界约14，不是真数学无界。λ抵消仅shaping spread支配penalty/ε时；penalty主导也λ-invariant，所以sweep本身不能独立证明shaping占比。
5. **训练/规模：** Qwen3 1.7/4/8B单家族，verl-agent，batch32 trajectories、150步/arm、lr1e-6、KL.01、aux β.1、prompt1536/response512；4/8B八96GB卡约18–24h/arm，74arms包含running/queued不是74完成解释。ALFWorld、WebShop小/全、synthetic HiddenRule；ScienceWorld未完成不贡献结果。
6. **主要结果：** 三规模std预测reward崩溃；去std ALF4B52.9 vs无signal同normalizer57.9、CI重合。gold aux formal3seed68.6/57.9/52.1，对baseline42.9/40.7/48.6；placebo s0 shuffled81.4/randomvocab87.1，不支持gold content更好，但有限seeds不能认证“任何任意target都有收益”。8B gold2/3锁死、1/3逃脱85，另一环境aux正负分叉，scope如实缩小。
7. **质量/限制：** formal seen140、unseen134被fixedloader pad到140有6重复，Wilson binomial忽略依赖/seed variance；大collapse可信，细排名弱。next prediction spread占比未记录，只有均值及knockout；criterion为variance trajectory+hackability，necessary观察不等于sufficient定理，anchor-QA over-warning、progress差分改为positiveclip后非telescoping保留。对外论文成功兼容不是独立prospective test。
8. **阅读范围：** main1–7 pp1–17全部、repro statement p18全部；AppC setup p23全部、E methods p24全部、N p34–35全部；其它inventory/curves/provenance只定位未全读。formal表4 p16视觉核；未运行作者代码，不声称 independently reproduced。
9. **对我们与尺度：** 一般predictability reward误导/GRPO归一化danger已有owner；E101/E103是固定观察content reconstruction与argmax选择，未训练GRPO，不能借本文collapse当我们的RL结果。可学的是一项改变解释的决定性比较→机制边界→有价值方法入口，而不是把74arms照搬成我们的必要门槛。我们的具体语义修订credit竞争仍需自身证据，不因近邻自动关线。
