# E87：现代模型实际作答与强制二选项读数（2026-10-07）

- **状态：** DONE；生成器E431在任何效果前改E87。
- **对应：** C06–C09 / I02 / P17；先前解释修订的真假错误必须发生在实际作答，E86现代模型grammar cue接近全No，需要一个直接行为读数。
- **问题：** 同一原生提示的greedy实际答案，是否与强制Yes/No归一化选择一致？若不一致，E82/E86只剩候选LP而不能直接认证实际理解失败。不是新措辞/校准网格。
- **数据：** 原E82 892QA/356S及E86的356 grammar问题全复用，不修改S/Q/Gold，不重审，0新API。原QA_STRICT/QA_RECOVER/QA_PLAIN与GRAM_ACCEPT分别使用原prompt，words两个mapping，不增加letters或新提示。
- **条件：** 3当下模型族×(892×3+356)×2mapping=18192真实输出。E82/E86原强制选择LP全部缓存复用。实际QA_RECOVER是原一句恢复对照（R8），不因DIRECT失败单独认证能力。
- **主读数：** 实际首答案Yes/No正确率下界/上界、known-only描述分数、valid比例、cap、strict exact格式、与原强制argmax不一致比例；各族/四构式/GP-cue/QA目标和Gold分别完整报告，GRAM独立。无答案为UNKNOWN，不当语义No或错误。按冻结Source→lexical cluster paired bootstrap10000 seed87，所有格保留。
- **解析：** strip空白后开头明确Yes或No且后面为空/标点/空白才可判；附带解释保留原文并记录非exact；开头其它内容为UNKNOWN，不从解释猜答案，不把A/B改成Yes/No。生成32新tokens上限，cap独立记录。若cap且开头有label仍记录label但主成功下界要求终止；无终止不直接认定能力。
- **阳性对照：** 同原cue、两个选项顺序；完整prompt SHA比对母，首Source所有条件做输入/输出token预检；原LP来自固定两候选布局，不把生成单prefix first-token LP冒称BF16相同。greedy/do_sample=False/native closed nonthinking入口，EOS按原模型generation config。
- **噪声地板：** 全mapping不一致与paired cluster CI；不择高choice-mass或baseline正确子集，不做温度/词首空格扫网格。可描述已缓存Yes/No总mass而不按mass筛样本。
- **混杂审计：** 部分valid不是完整理解；实际答案生成与强制候选LP可受不同有限精度/候选空间/格式影响，差异不足单独证明认知机制。QA_PLAIN兼容事件问题与grammar任务弱对照仍保留；不将自报grammar当潜在parse。
- **决策表（跑之前写）：** actual与强制choice接近且错误保留→关闭测量疑点，回具体关系表达与源修订；actual救cue grammar和关系、强制choice大量不符→降级受影响的actual能力措辞，下一只选一个符合原生作答的真实机制读数；UNKNOWN/cap多→当前协议不足，不把失败包装能力；异质→完整保留范围，不单模型局部优化。
- **算力预算：** ≤8GPU·h，8独立H20 Q3/G3/M2，现有SHA核验离线资产，国内镜像；不影响已有小服务。先卡再预检，所有科学输出全闭合才读效应，外置E87，源码/摘要进git。

CPU三族6064原prompt SHA预检通过，8卡PID3202995–3203002已启动18192真实输出。脚本SHA806baf7ae9fe192dbe9286ad9eae23590c7baffe9492ebb68c4ad596d84fcc29，原生入口/数据原样，0新API。完整生成前不读partial科学效应。


## 完整结果与POST-HOC语义解析

18192输出/8分片全部闭合，1.008726GPU·h，0新API；完整2640格/216joint/96mapping原图v1 SHA6e27a4d0b670c32b117f0ad7d814fb9ef8ce773fdb356b3721a28fe8e898796a保留，是事前literal格式范围；不将UNKNOWN当理解错误。

完整输出中的literal未知全是A/B或“A/B. Yes/No”，没有含混解释。**POST-HOC**按题内原选项映射解析：bare A/B映射原选项；A/B. Yes/No须word与option一致，否则仍UNKNOWN。不改Gold/输出/提示，0GPU/0API。v2语义图SHA27c3c21025d7f6f99acd5ba6cda24dbcc9bac11bf12f222940cb6beda41779b7，全部18192答案明确、冲突0、cap0，correct上下界一致。v1依然描述literal指令遵从，不覆盖它。[完整摘要](../results/E87-actual-answer-summary.json)。

- words严格NPZ GP actual initial Q/G/M40.45[31.18,50.00]/72.47[63.48,80.90]/83.99[78.37,89.33]%，final78.37[70.79,85.39]/79.21[71.91,86.24]/27.53[20.79,34.83]%；正确initial不代表完整修订。普通QA NPZ actual initial30.62/45.51/71.91，final97.47/98.88/64.04；权衡保留，未建立共同joint恢复。
- actual与强制choice QA多数相近：完整条件/目标/CI全部保留。主格式Gram Q cue差异大：MVRR实际66.67 vs38.89，+27.78[12.96,44.44]pp；NPZ92.13 vs83.71，+8.43[3.93,13.48]；NPS97.22 vs94.44；NPVP65.38 vs50。所以E86 Q原bare候选接受概率不能当完整生成接受率，已明确限定。但Q GP grammar仍低，Min GP与若干cue实际全No，Gemma NPS actual100%接受而QA仍错。
- actual mapping最大Min NPS RECOVER GP25%、Min GRAM NPS cue25%，所有噪声与阴性同报。Q/G的格式选择是显式原选项，不能当UNKNOWN能力故障；也不能凭强制输出mass低直接判无理解。

自审：真正关系错误仍存在，不是单个强制评分伪影；语法自报仍不足解释。测量块结束，不增加词首空格/温度/提示校准。C06–08 L0/C09限定L1不变。按用户最新要求，下一聚焦可探索机制idea而非先补齐成稿标准：检验前面动词的论元框架是否没有利用晚到证据，不继续打磨本协议。
