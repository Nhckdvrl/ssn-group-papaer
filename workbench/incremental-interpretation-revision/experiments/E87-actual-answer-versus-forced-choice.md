# E87：现代模型实际作答与强制二选项读数（2026-10-07）

- **状态：** RUNNING；生成器E431在任何效果前改E87。
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
