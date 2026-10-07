# E97：Belief-R一句简短输出要求，恢复可解释的真实答题读数（2026-10-08）

- **状态：** RUNNING（CPU三族1744原题通过，8slot等相应E96完成），生成器E431在任何forward前更名E97。
- **对应：** I07 / P20，E93完整Min族已见DIRECT1744/1744 cap/unknown，COT1715cap／仅1finalchoice；原图保留上下界，不当0%能力。E95 Minchanged大多Tie，不支持会判断正确解释但漏credit，不能预设更好故事。
- **问题：** 一句只交最终答案的输出要求是否恢复原社区任务的可用前向读数？该锚能区分格式／预算无答案和实际语用task失败，不给256思考cap加码，不猜截断中的推理结论。
- **数据：** 完整原E93 1744／204atomicseed，人类语用suppression Gold，Source/question/ABC字节与Gold完全不变，prior21NA照旧。0source审计/0API，raw scores复用原E93，未覆写原失败图。
- **唯一条件：** 原FORWARD_DIRECT正文／FORMAT后追加一句："Do not provide explanations; write only Final Answer [a], Final Answer [b], or Final Answer [c]."；原native chat／thinking=False，greedy／64cap及原parser保持。三当前模型各1744actual，共5232新输出。只这个format-recovery，不加入长CoT、第二个措辞或LP mapping控制。
- **读数：** 正常停且可parse的实际准确率与unknown/cap上下界，authorGold c/ab、prior更新/保持/NA、modus、agreement完整scope；对原同模型重建选择/Goldrankpaired差CI10000 seed97，完整1744为主。Author rowmacroBREU描述性同E93，不能把pragmaticGold叫classicallogictruth。原DIRECT/COT输出长度／失败也并列保留。
- **阳性对照：** input/baselinequestion/原候选／modelmanifestSHA；固定首题repeat outputtoken一致并要求stopped且parseable才开科学forward，解决E93仅检查重复却未检验有效答案的仪器漏项。若仍不能给finalchoice，本族只描述／停止此恢复块，不换措辞追分。
- **噪声地板：** BF16/eager/seed97固定，same native template／64cap不增；句式仅格式限定、不给grammar or inference hint，不以强制候选LP伪装实际行为。所有未停／未知按界限保留，不在看到数据后改parser。
- **决策表（跑之前写）：** 有效答案恢复而raw错奖→才在原任务Goldscope探索能力与credit的差；有效答案恢复但原task也弱或raw更好→修正I07外域范围；仍高cap/UNKNOWN→该family接口锚不可用，不作能力论断／不续输出控制。GP当前生成E96与E95其它族独立推进，不因单族null关闭线。
- **算力：** ≤3GPU·h估计，8独立slot按3Q/3G/2Min等该slotE96完成，再取共享锁；Min现在可直接启动，Q/G既有原任务不打断。只5232actual／无新LP／无新模型下载／无Source标注。08:55timer与每题/排队guard优先，09:00GPU硬停，不用追加长推理拖时。

原E93单族全scope支持的是接口未完成边界而非已证能力失效，错误已明确写入日志；这一步为恢复核心测量，不复制一串防御控制。

启动前data SHA5477a87d5a03b2382cddc54058b0a9787e35bdeb17d97ecfff83241c2c7ccf41，与E93字节相同；仅nativeuser末尾一句输出要求变化，cap64和原parser不改。各fixedinstrument必须停＋有效答案后科学forward，0API／0新LP。
