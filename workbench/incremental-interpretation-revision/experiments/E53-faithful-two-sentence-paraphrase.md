# E53：先前误读是否进入自由复述？（2026-10-06）

- **状态：** PLANNED
- **类型：** CLAIM + MEASUREMENT；EXECUTION_BRIEF §2明确允许与E52并行。
- **对应：** I02 / C06–C09；P13问句语义、P14广度。旧I01不重启。
- **问题（一句话）：** 相同GP/control原句的YN低分是否伴随复述中明确的初始错误角色，完整重读能否选择性消除这个错误？
- **与先前解释的修订关系：** source前缀暂支持旧角色、后文迫使改析；评估生成是否仍把旧角色写成原句事实。Yes倾向、分句格式或可能的额外事件不充当结构修订失败。
- **设置：** 固定E52 published-v2全部needs_revision原句，按sentence SHA合并完全相同输入、保留全部source/QA关系，不按行为选句。P-A沿用Amouyal2025附录H四个分句例子（原例4的The拼写保留）；P-B同任务零样本原生chat。每prompt测R0单句、R1完整重复、R8单句加E52同一句恢复指令。原问题/选项不出现在生成prompt中，原句字节不改。
- **模型与版本：** Qwen3-8B、Gemma3-12B-it、Llama3.1-8B-Instruct，同E52三族確認字节；原生chat、Qwen thinking-off、vLLM隔离环境BF16、greedy seed52、cap256、TP1单卡。关联QA用同模型BF16地图，FP32确认单列，不把引擎差当修订机制。
- **Step5 T4：** 唯一step-5-preview/Step Plan，每批2、两遍独立打乱、分歧第三遍rationale，失败单项最多2次，共享≤8调用。只给source和final复述，不给QA/gold/模型/reading/分数。三类CORRECT_ROLES（主要事件及角色忠实，省略原连接词不自动算错）、GP_MISREADING（明确把初始错误角色写进复述）、OTHER（关键事件/角色缺失、其他不忠实、冲突或不可判）。新旧角色同时出现仍记GP_MISREADING并备注；兼容的额外事件不称逻辑矛盾，只判断是否忠实复述source。source/output联合SHA回显；完全相同source/output只标一次，固定用于全部条件，不按标签择版本。
- **读数：** 主：同题配对两侧grammar合格的CORRECT_ROLES和GP_MISREADING比例及gp−control差，R1相对R0选择性恢复、R8一句恢复。OTHER/cap/空输出/两句格式/found-verb全报；主任务成功按全部预选输入分母，不把所有失败称GP误读。自动NP与V1同句仅作作者指标的描述校验，不能替代Step或证明角色。
- **统计：** 同E52连接共享lexical cluster，10000次cluster bootstrap/95%CI，按模型/构式/prompt全切片；条件比较取相同输入、配对两侧都覆盖。与E52逐题QA关系POST-HOC报告，不据公开No约定定义T4正确；finding仍需后续因果证据。
- **阳性对照：** 每构式作者control忠实角色比例；NPS补语/MVRR被动能否正确分句；四个source例子的格式/角色。control或格式低的切片只描述，保留全部输出。
- **噪声地板 + MIE：** P-A/P-B差、T4两遍一致率与未知；关注可分辨≥5pp选择性变化，启发式而非自动判断，不筛seed或重采样。
- **混杂审计：** 忠实复述指source断言内容，不是开放世界NLI；grammar边缘项单列；例4拼写/少样本与native格式分报；不按输出选材料/gold，不把复述正确直接推为内部parse共存。
- **决策表（跑之前写）：** QA约定低但复述正确→E3增加、E59明确题域/角色；QA与复述均旧角色且R1特异改善→E4/E1开放、E54/E55；R1无效且合理性梯度明显→E2增加、probe及因果校对实际可用性；格式/OTHER主导→报任务限制、E59角色选择；异质→保留全图、不挑一族局部连锁。
- **算力预算：** 三模型1–3 GPU·h，实耗看config；共享E52八个flock slot，保留既有常驻服务。Step持续审计，不设省API筛选；资产外部`/data1/xiangding/work/incremental-interpretation-revision/E53/`。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

- 尚未生成，无能力结果或CI，C06–C09 L0。
- 生成器因菜单/历史文字引用跳到E64，跑前重命名为尚未占用的E53，未改历史编号。
