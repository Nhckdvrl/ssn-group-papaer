# I08：任务答得更对，是否掩盖更错误的解释？（SEED）

- **来源：** P21／E65与完整E67，三族pooledGP requestedQA↑但明确错关系↑19–21pp，未认证当前强模型/机制/合格idea。
- **RQ：** 非assertive的阅读目标问题，是否能提高任务correctness同时损害对原文的faithful关系表达？为什么target看似帮助“理解”，却更容易补成问题暗示的错误事件？
- **若为真为何兴奋：** 通常用任务correctness判断读懂和训练内容credit，但目标condition本身可能改变我们当作证据的关系；形成答案不等于形成可依赖的解释。它把自然GP的revision问题连接到query-aware处理／agent state formation，而非一般LLM偶尔误读；不是宣告RL训练失败。
- **旧证据：** E67完整更正版3a8b7bcde6fe75a1c6f65b215263ac5f336607a9a5d49e46acfc232cb8c15f81，explicit GP而非OTHER增加；旧QA仍forced-choice且各构式不同，要保留全部地图。原input initialTrue有17NPZ，不能先叫全部questionfalse。C等级不变。
- **研究动作：** 实际QA＋未经询问的free interpretation作为两个用途，固定同Sourceprefix；一句question/evidence分离是核心R8，不扫更多Goal/窗口。如果新模型不出现，就改适用范围而非守旧故事。
- **定位：** Hu/Levy的任务读出差、Hanna的多parse、false-presupposition QA和query-awarecompression都有ownership。一般QA不等于understanding／memory不可靠不新；拟增量须是明确输入干预导致accuracy和错误关系反向，并有同Source与可恢复的操作边界。其它人做过邻域不关线，尚未全文核对新QA近邻，持续阅读。
- **下一：** E98原既有50发表pair／三当前族／actualYN＋freeP，GOAL/NATIVE/QUESTION_ONLY；Gold未知保留，所有Source/GP-cue/construct并列。未找到结果前不先设计昂贵训练，也不按完整paper的全控制门槛拖探索。

E99首次POST-HOC同源joint已核：旧三族word QAcorrect且明确GPwrong增量17.2[11.6,22.9]/12.4[7.3,17.8]/29.9[23.7,36.2]pp，letters同正，主要NPZ/NPS。map6f29db10942a00f4b7d1700340a545fd8148fa92e990ce36e0867c3fc387ea22；更具体地排除仅不同Source边际平均抵消，但旧QA仍forced-choice，不能取代E98当下actual用途。

2026-10-08T06:48:43.674159+08:00 当前完整Q实际输出同S joint+20.83[10.42,33.33]pp/GP角色正确−29.17pp CI负，但QA收益CI0；完整Min无QA增益。因而具体保留目标干预使明确误角色更多、原已正确QA不保护外化解释；收紧“普遍问答收益与忠实度代价”强叙事，不追加Goal字词/R8网格。E98剩余Gemma全范围待封版。

2026-10-08T07:14:58.219678+08:00 E98全当前三族最终SHA1d996c75：实际QA共同收益未成立（Q/G GP+2.08/3.13ppCI0，Min0）；同S joint Q+20.83ppCI正，G/Min较弱CI0。收紧current普遍悖论，不用更多Goal/YN/cut控制救故事，不据此自动关线；旧E99三族是另一个保留范围。
