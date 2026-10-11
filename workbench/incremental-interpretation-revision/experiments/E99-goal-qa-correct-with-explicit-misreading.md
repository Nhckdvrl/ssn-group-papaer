# E99：同源问答正确与明确角色误读的联合读数

- **状态：** DONE，自动E431在任何计算前更名E99。
- **对应：** I08 / P21；POST-HOC E65/E67完整图之后设计的新联合统计，0新模型输出。
- **问题：** 先前解释修订中，目标提高requested QA却增加明确GP关系错误，是否真的发生在QA成功的同Source，而不只是不同项目平均抵消？
- **数据：** 原E67全部356Source/178pair/四构式、三旧模型族，NONE/INITIAL/FINAL全部；完整T4-role-v2失败补全3033packet以及原复用E64标签。E65同源全部原问句/两个mapping/words-letters，原source-gold匹配与全Gold两scope并列。不选成功Source，不重审社区数据。
- **读数：** QA_all_correct、QA_correct_AND_explicit_GPwrong、QA_correct_AND_roles_correct、QA_wrong_AND_GPwrong，role lower/upper及cap/unknown；每Source先平均两个mapping，再paircluster bootstrap10000 seed99。三个Goal绝对值、INITIAL−NONE/FINAL−NONE，全四ct+pooled×GP-cue×两readout×两原Goldscope。不报后处理筛选的因果conditional rate。
- **阳性对照：** 输入SHA/所有QAcoverage/key去重，T4packet exactSource/P SHA；同SourceQA正确且角色正确也报告；未完输出保上下界不猜。
- **噪声地板：** 只现有固定deterministic输出；首次联合读数POST-HOC清楚标注，强制选项不是actualQA且唯一latentparse未证，当前E98actual用途独立继续。
- **决策表（跑之前写）：** 同源joint误读显著上升→强化具体cross-use异常；只有不同Source边际反向、joint无变化→弱化accuracy遮蔽误读故事；ct/model不同→限定；无新GPU/APIs及标签筛选。即使正向也不据此认证现代能力或完整合格idea。
- **算力：** CPU复算，0GPU、0API、0权重；resource硬截止不受影响。

05:02 完整6000panel，map6f29db10942a00f4b7d1700340a545fd8148fa92e990ce36e0867c3fc387ea22，0GPU/0API/0newmodel。matched GP words三族QAcorrect_AND_GPwrong lower增加Q17.23[11.58,22.88]/G12.43[7.34,17.80]/L29.94[23.73,36.16]pp；letters16.10[10.45,21.75]/16.95[11.58,22.60]/34.18[27.97,40.68]pp。NPZ/NPS同Source联合增加跨三族，MVRR/NPVP弱或不同；全Gold也方向正，matched原NPS一对无同GoldQA记structuralNA（不是删生成）。FINAL无共同收益、cue常损伤同报。完整输出/cap作为unknown上下界，不能使用posttreatmentconditional率作因果；旧QA还只是forced candidate，不认证当前actual任务。E98全actual三族继续；I08得到比边际反向更具体的行为关系，但未认证合格idea。
