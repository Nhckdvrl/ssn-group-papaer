# E106：不借人工消歧位置的正观测增益，能否选择忠实修订？

- **状态：** DONE；自动E431在任何新forward/统计前更名E106。
- **对应：** I07/P20；E101/E102三族、E103同源池和E105预算问题后的一个自动评分pilot，不宣称发明对比likelihood/positive clipping。
- **问题：** 前缀产生的反向credit能否在无需T2位置的规则下被避免？将内容reward从整段拟合改为相对空belief的逐token正预测增益。若只有位置oracle有效而自动增益无效，说明尚无自动方法，而不是继续调窗口。
- **数据：** 原E103全部50GP源×三族×八候选/1200候选不改，所有1050新P及greedy/j0仍原版本；新增三族各50个No-new-belief baseline LP。既有Source/Gold/原角色T4完全沿用；空belief为原context已使用的固定“No prior information.”，仅评分参照不当候选或待审生成数据。
- **唯一规则：** POSITIVE_INNOVATION=sum_i max(0, LP_i(observation|candidate)-LP_i(observation|No prior information.))；0 cutoff不调，全部target token，不用T2/Gold/Teacher。WHOLE_GAIN=sum差仅恒等检查，sameSource baseline是常数故其argmax必须等于原WHOLE，不假装是另一个修复；E103原T2 suffix仅已有上界参照。score并列取最小j，不挑已有good的Source。
- **读数：** 全50/三ct/三族selected CORRECT_ROLES/GP_MISREADING/OTHER及unknown/cap上下界；相对原WHOLE、GREEDY、UNIFORM及既有T2 oracle的paired质量差；逐候选positive/negative增益分解只辅助机制。Source→原cluster10000bootstrap seed106，未知不删。
- **阳性对照：** NoP同firstSource LP重复exact；同target token/offset与E103全候选一致、context/prompt SHA重建；positive+negative=wholeGain；wholeGain rank必须等于原whole；已有1200输出SHA/角色labels封版后才读效果。
- **噪声地板：** NoP是固定评分context基线，不是独立trainedcritic或原ABBEL复现。positive token credit可能也奖励初始错误的copied词，不预设修复；0 cutoff只有本规则，不能用效果挑另一个baseline/阈值。没有T2不等于成功泛化或完整RL训练。
- **定位：** CTRL-RAG已token对比贡献/全局threshold与gate，TRLM已reverse likelihood best-of-N，ARC/IG等一般gain已有；我们只用此pilot判断特定revision credit cancellation能否导出自动选择动作，机制/预测和实际后果才是拟增量。
- **决策表（跑之前写）：** 自动规则恢复actual角色且跨族/构式方向稳→值得追的自动内容credit入口；suffix好但positive-only不好→位置信息重要/无方法证据，保留探索机制，不再扫gain定义；pool无good→proposal瓶颈；全null或混合→完整报告，不用最好ctor曲线保叙事。
- **算力：** 150新teacher-forced评分，3既有独立H20 slot，估<.1GPUh，0新P/API/模型下载；既有队列/每Source guard与08:55释放timer优先。科学分析等E103完整三族盲审，CPU可续。

2026-10-08T07:14:58.219678+08:00 三族baseline150LP/.016798616GPUh已完成，0新P/API，E103目标token边界preflight全50/族通过，原scorerseed91/repeat0/离线模型不改。待完整E103role才读效果；baseline差的wholeGain只恒等检查、不叫另一个方法。

2026-10-08T07:20:00.395734+08:00 在任何E106新选择效果读取前，prospective次序修订：已封版的完整Min E103 cohort可先生成独立INTERIM指导探索，其余两族固定candidate/NoP/规则不改，三族默认主图仍待全E103。不是选Source/成功model；首完整由原固定流水线就绪次序决定。旧CPUwait在0新统计前退出，原code外置封存，main与INTERIM不同路径，0 cutoff不调。

2026-10-08T07:57:25.298407+08:00 完整三族150额外LP/.016798616GPUh、492panel，0新P/API，mapba791147f901a72fe4c42117d972d2f92b65390be3bbedd1cd603a2b5dacf15a。POSITIVE_INNOVATION−WHOLE正确lower Q−2.08[−6.25,0]/G+2.08[0,6.25]/Min+2.08[0,6.25]pp，无稳健共同自动修复；相对原T2suffix三族均更低。完整Min先读的INTERIM ca36131e保留，唯一0 cutoff不调；其它规则/窗口不续局部网格。
