# E108：自由belief写入与实际读取中的修订credit（2026-10-08）

- **状态：** PLANNED；自动E431在任何GPU/API/统计前改E108。09:00后不占GPU、不重下模型，等人提供新资源。
- **类型：** PILOT；I07/P20，E107后的最高信息量迁移，原句的结构重析保持核心对象。
- **对应：** I07/P20；检验结构修订的反馈后果能否迁移到自由belief写入与消费。
- **问题（一句话）：** 从两句复述改为自由belief更新后，是否仍有完整正确关系可生成、但完整观察重建偏初始误关系，并影响后续使用？这可推翻memory credit故事，不继续调窗口。
- **设置：** 原E96全部50发表pair、原GP/control/问题/Gold/48clusters不改、不bulk审计。三当下族及原revision。新writer与E91重建上下文一致：空prior、读下一句的action、观察、自由更新；不限制两句，不给示例或未来Q。这是实验适配，不称完整ABBEL作者pipeline或RL训练。
- **候选：** GP j0greedy+j1–7固定seed，temperature.8/top_p.95/96cap全部保留；唯一R8一句完整观察修订提醒的greedy j8、control观察greedy j9只作参照，不入八候选主池。官方generation defaults记录，不按效果调参。
- **实际消费：** 每个P只给原已注册Q，reader不再见原Source；另原GP/control文本直接读取。actual greedy64cap/明确YesNo，unknown/cap上下界保留。writer不见Q，teacher不见Q/Gold/分数/seed/政策。
- **读数：** 全Source WHOLE/T2-suffix/GREEDY/UNIFORM/池完整依赖可获得率；新P按E107五维完整双遍+第三，explicit与合理implicit分开。原Q Source支持和实际成功率，不把全部GoldNo当世界虚假。exact Source-copy另标不剔除，文字faithfulness不单独认证理解。secondary固定same-pool explicit-vs-initial credit，eligible覆盖/NA全报。
- **阳性对照：** 原发表GP/control pair；固定首源sample重复tokens完全一致、LP重复完全一致；all8同target/offset、before+suffix=whole。reader固定首Source的Gold-independent题两遍tokens一致且valid final才bulk；单族instrument失败UNAVAILABLE不记0能力。
- **噪声地板 + MIE：** 同96cap、seed冻结、不筛幸存种子；Source→cluster bootstrap10000。关注真实操作失配、可比Source数量与使用后果，不把全族CI正或完整训练作为探索价值自动门槛。
- **混杂审计：** writer合同改变是此pilot对象，不声称唯一神经因果。Source事实/问题固定，reader只看P；Source-copy的使用与文字有效性分别报告。未训练只是内容reward analogue；同一Step不是独立人类GT，不自动升L2。
- **决策表（跑之前写）：** 新belief接口仍有完整候选/反修订排序/使用损失→I07实践后果更强；接口解决且WHOLE可选→两句限制/表达是重要边界，收紧；只少承诺→回I06新依赖建立；无good候选→proposal瓶颈优先；混合全报，不续writer措辞/窗口网格。
- **算力预算：** 约1–2 GPU·h，三独立单卡可串行，不需8卡；实际0/队列0。API仅新P需标注时Step Plan step-5-preview，批≤5/全局8/high，Source不审。权重需新资源授权后复用公共共享资产或国内镜像恢复，当前guard拒绝GPUrun。

入口：scripts/free_belief_contract.py build（CPU冻结数据）；scripts/run_free_belief_pool.py（generation/score/实际消费）。先准备源码、数据和tokenizer核验，不发新API、不加载权重；现有GPU hard-stop不绕过。
