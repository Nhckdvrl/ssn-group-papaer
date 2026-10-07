# E105：增加同源候选预算，会奖励更好的修订还是更好的误读？

- **状态：** PLANNED；自动E431在统计前更名E105。
- **对应：** I07/P20；E103所有新P/LP已完整而盲T4未封版前预注册的新功能问题。
- **问题：** 同一观察best-of-N重建奖励是否随更多proposal上升而内容忠实度不升甚至下降？如果池里忠实解释更可获得，却未被高分选中，则是实际compute选择后果，不只是两P的nats诊断。
- **数据：** E103同原50GP源/三当前族/全部1200原候选，j0原greedy+j1–7固定seed采样，原LP/T4均不改；增加proposal是固定prefix {j0}→{j0,j1}→{j0..j3}→{j0..j7}，预算1/2/4/8，顺序在看label前固定，不选最佳subset/种子。k1有greedy，不称独立同分布pass@k。
- **条件：** 固定WHOLE或原T2后缀REVISION_EVIDENCE argmax，每k最大并列取最小j；UNIFORM每池等权/greedy作原基线，ORACLE_ROLES只量忠实P可获得性上界。不增加窗口/权重/提示网格，不为得到效果重采。
- **主读数：** 每budget下selected CORRECT_ROLES/GP_MISREADING/OTHER/unknown/cap上下界、ORACLE availability、reward最大值；WHOLE与suffix各k相对k1、相邻新增预算的paired质量差和reward差。三模型全50及MVRR/NPZ/NPS完整报，Source→48原cluster10000bootstrap seed105，差上下界保留cap/unknown，不能按池已有好P筛主表。
- **阳性对照：** k8 WHOLE/suffix/UNIFORM逐项等于封版E103；k1等于greedy；最大reward随着增加池非递减是算术验证，不当科学finding。只有内容是否被选对才是发现。E103固定first-seed/token/LP重复与context/target offsets验证复用。
- **噪声地板：** 只一套固定七seed，不能从固定prefix曲线冒称所有random seed分布定律；T2是oracle，unknown明示；更多budget包含相同贪心候选，greedy优势/采样差异不隐去。
- **决策表（跑之前写）：** 可获得good增长但WHOLE质量降/错解释升而suffix较稳→有后果的反修订选择压力，值得形成探索叙事；WHOLE正确随预算涨→收紧早先负面结论，更多proposal能缓解；两者都不行且pool无good→主要proposal瓶颈，不做score调参；混合→保留模型/构式边界，不挑曲线。原E103主结论不被本图替换。
- **算力：** CPU固定候选/已封版标签，0GPU/API/新output/下载，等待原E103完整三族审核，不读partial labels作科学效应。
