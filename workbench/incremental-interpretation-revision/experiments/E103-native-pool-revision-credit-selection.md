# E103：同一原观察的自然候选池，评价器会选择哪种解释？

- **状态：** DONE；三族8分片已通过原prompt/LP/T2全50预检并启动，blind T4 finisher在途。
- **对应：** I07/P20；E101/E102完整三族之后的新功能后果，原问题需撤回早期角色关系。
- **问题：** prefix reward抵消修订证据是否影响真实内容选择？同原GP观察生成候选，WHOLE重建与T2后缀oracle选择的自由解释忠实度谁更高？不声称自动reward方法/训练收益。
- **数据：** E96固定50已发表GP源/三当前族，MVRR17、NPZ8、NPS25，所有Source沿用、不改句/问题/Gold、不做Source重审。每Source8候选：j0原E96 native greedy P及原GP-target LP逐字复用；j1–7同一原S、原Amouyal指令/4例、原native nonthinking模板，temperature .8/top_p .95/max96，hashSource×model×j固定seed，全部七种seed保留，无幸存筛选。3×50×7=1050新P+1050新score，150 greedy完整原样保留。
- **条件：** 同池WHOLE argmax；REVISION_EVIDENCE从原唯一共识T2消歧词起argmax（唯一oracle，0更多cut/权重）；GREEDY j0和UNIFORM_POOL每候选等权作基准；ORACLE_ROLES仅已封版标签给上界、不作实际策略。并列最高分选最小j（效果前固定），不按Teacher或stop质量排除候选。
- **标注：** 仅Source/P主要关系T4-role-v2，原匿名prompt/语态澄清、Step Plan step-5-preview、batch≤5/shared8、两独立遍/分歧第三遍；Source/P exactUID复用原已封版validaudit，新P/Role必要才标，不给Goal/reward/model/seed/Gold。所有1050及greedy候选参与，不只审被选样本；cap/未完成按UNKNOWN上下界留，原文本不改。
- **主读数：** 被选P CORRECT_ROLES/GP_MISREADING/OTHER与unknown/cap上下界，REVISION_EVIDENCE−WHOLE正确关系pp与错关系pp、两者对GREEDY/UNIFORM、samePool oracle上界、正确P可获得率。全部50+各ct、3独立fam，Source→原paircluster10000bootstrap seed103，不筛有good候选的Source作为主读数。
- **阳性对照：** 原j0输出/评分SHA/模型revision链接；固定首源j1同seed重复tokens完全相同、同task LP完全相同；token/offset复建与E101一致，before+suffix=whole；seed不进入Teacher。原cueP质量只作为E96既有外部能力参照，不进入本池，也不借其错位任务分数。
- **噪声地板：** BF16/eager，每候选独立固定seed，原96cap不增加，Teacher一致率/unknown完整报告；T2是位置oracle而非自动发现机制；同池选择改善只证contentselection，非learnedpolicy/RL训练已改善或唯一内部parse。
- **决策表（跑之前写）：** 池有忠实P、WHOLE常选GPwrong而suffix跨族/ct提高selected正确关系→有功能后果的revision credit cancellation；只有Cue来源旧池有效、本原S池无good候选→原先依赖proposal可获得性，收紧；有good候选但两个评分都无改善→区域LP优势不兑现，不继续调窗口；模型/ct混合→保留边界，不挑种子拼统一规律。
- **算力：** 估≤3GPUh，八既有独立slot Q3/G3/Min2，全已释放旧科学任务后启动，0新model/下载。既有持久08:55timer/09:00硬stop及queue/per-source guards覆盖，CPU/API可完成既有数据审核。目标是探索高价值idea，今晚不补完整训练论文。

2026-10-08T06:37:02.629845+08:00 GPU三族8分片全完成：1200候选assignment中150原greedy重用，1050新增采样P+1050新GP-target LP；.412222494GPUh，无queue/GPU仍在途。原source/context/offset/all8target一致验证通过，全部分片first-seed生成tokenexact和LPexact。T4完整族blind流水线仍RUNNING（首Min163新distinct packet，其余同packet复用），不读partial teacher效果；原09:00deadline/timer保持。

2026-10-08T07:20:00.395734+08:00 E103首完整Min同原S八候选（50源/400assignments），mapa1518b8d1db14a89348f776005e70948ee5e5a342063a0668456fd0ba68d27d3，.078246924GPUh/163新packet两遍/32裁决/80.368%agreement/0unresolved。全50greedy正确roles42.71%，whole43.75%，suffix52.08%，pooloracle60.42%；suffix−whole正确+8.33[2.08,16.67]pp、GPwrong−12.5[−22.92,−4.17]pp，已有实际selection后果。NPS正确+16[4,32]pp/GPwrong−20[−36,−7.9]pp；MVRR correct无改善且greedy=pooloracle47.06%，没有新增good候选，不能把cue-source对上的原MVRRoracle收益直接迁移到sameSourcepool。NPZsuffix=whole，greedy差CI0，所有异质保留；还不称三族/两构式合格finding。

2026-10-08T07:57:25.298407+08:00 完整三族1200原候选assignment、243新distinct packet，两遍/46第三裁决/0unresolved；900panel/.412222494GPUh。主map3651682f64f571660779a386bbd2dd0581d41e5ca9aa9be318ec5c4ddba2f333。原T4角色criterion下 suffix−whole正确lower Q+2.08[−4.17,10.42]/G+6.25[0,14.58]/Min+8.33[2.08,16.67]pp；Q有1cap，point difference不能替代lower bound。GPwrong lower变化Q−6.25[−14.58,0]/G−6.25[−14.58,0]/Min−12.5[−22.92,−4.17]pp。不能写全三族共同显著。所有当前收益尚不是完整source意义修复：看到完整Min的4positive例子含bareunderstood/discovered/noticed something，E107另POST-HOC维度将分明确依赖/语篇隐式/未绑定，旧T4有效范围不重写、不把implicit自动错。
