# Beliefs and Behavior in Language Models（2026年9月预印本）

[作者v1](https://arxiv.org/pdf/2609.07943)：主文p1–14完整，AppA1–5/B/C/D方法与图注；后续原始prompt目录未全读。Alex Smolin（Toulouse School of Economics）、Bryan Wilder（CMU ML）。正式接收未核对。外置33页PDF SHA55c0456d6cb28f2310c6b8e2045e3974496d300d16e8ec6f9756540e9b2198b3，不在git分发。

1. **问题尺度与idea来源（重建）：** 旧研究展示probability/行动不一致，不能据此决定“belief”是否有用，因为人也有frame bias。把哲学属性争论变成可检验问题：受限制的一维latent能否跨新行动、新case、新frame、新domain预测输出？经济学discrete choice＋心理测量latent与LLM行为交汇；贡献不是又一种问概率提示，而是预测标准及其外推。
2. **数据/方法：** CKD原NHANES、原Werewolf游戏、社会实验材料，各500case×16prompt×9模型，temperature1。16输出=1数值概率＋2ordinal＋13decision（1基础＋4threshold/4bet/4cost）。每model-domain严格全部16可解析才保留，保留率63–100%，Llama Werewolf63%不能忽略。case split64/16/20；所有16输出用于训练拟合观察模型，测试只用一组预测另一组，目标不进测试posterior。不是整个task zero-shot，进一步held-frame/domain才是。
3. **关键操作：** latent z[0,1]，数值概率Beta(zφ,(1−z)φ)锚定尺度；binary sigmoid(αj+βj logitz)，β>0，ordinal proportional odds。7点先验联合MLE，128点Gauss–Legendre，validation早停。限定单调/简单映射防一实数任意编码行为。choice threshold可与指令不一致，所以共享可预测结构≠语义遵从。二维和单调spline敏感性AppA4无明显提升，是这些任务/拟合规模结论，不是内在状态一维定理。
4. **结果与边界：** 主文强模型预测concordance约.8–.95、R².6–.9；新frame/domain R²约.6–.8。最好模型单次数值概率保留>90%超chance预测signal。此处是学过各输出映射后预测，不是概率报告直接执行规则正确。branch两模型×3domain×30case×5prefix×5response=750/cell，ICC约.5；行为branch用20prefix，same-prefix优于same-case不同prefix，说明instance文本状态有额外预测价值，非hidden机制因果定位。AppD outcome-sufficiency用all-response posterior含被预测decision，核平滑同testcase拟合/评估，不能等同主文严格held-target预测或证明latent正是belief；真值疾病也非我们要研究的医疗题。
5. **与近邻距离：** 相比Pal/Zhu等不一致研究，把一个违例从“无belief”改为限制latent的held-out预测测试；相比truth activation探针，不声称内部线性方向。Macar Thought Branches已有reasoning-prefix分枝，本文增量是跨行动预测与probability sufficiency。质量：清楚的任务/统计建模/外推，缺少source-level因果干预与机制认证，且parse complete-case选择影响模型比较。主文所谓较弱模型/早期模型也不应一概历史能力定律。
6. **对我们：** GP单题/联合答案不同，不足以证明多个矛盾的内部解释；一个共同关系状态加不同consumer映射也可能产生差异。可迁移的是“解释要预测另一个实际用途”，而非再拟合二十种提示。一旦E70/E71有关系特定后果，可用已有关系读数预测自然后续绑定，并通过干预区分共同源约束与答案串联。E73只检验直接首答案路径，不能据cut有效就推出latent解释。该跨领域近邻没有完整覆盖GP修订，也不自动排除选题；重要增量应是修订的关系操作与后续失效规律。
