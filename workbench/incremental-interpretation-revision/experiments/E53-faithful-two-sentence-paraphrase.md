# E53：先前误读是否进入自由复述？（2026-10-06）

- **状态：** RUNNING
- **类型：** CLAIM + MEASUREMENT；EXECUTION_BRIEF §2明确允许与E52并行。
- **对应：** I02 / C06–C09；P13问句语义、P14广度。旧I01不重启。
- **问题（一句话）：** 相同GP/control原句的YN低分是否伴随复述中明确的初始错误角色，完整重读能否选择性消除这个错误？
- **与先前解释的修订关系：** source前缀暂支持旧角色、后文迫使改析；评估生成是否仍把旧角色写成原句事实。Yes倾向、分句格式或可能的额外事件不充当结构修订失败。
- **设置：** 固定E52 published-v2全部needs_revision原句，按sentence SHA合并完全相同输入、保留全部source/QA关系，不按行为选句。P-A沿用Amouyal2025附录H四个分句例子（原例4的The拼写保留）；P-B同任务零样本原生chat。每prompt测R0单句、R1完整重复、R8单句加E52同一句恢复指令。原问题/选项不出现在生成prompt中，原句字节不改。
- **模型与版本：** Qwen3-8B、Gemma3-12B-it、Llama3.1-8B-Instruct，同E52三族確認字节；原生chat、Qwen thinking-off、vLLM隔离环境BF16、greedy seed52、cap256、TP1单卡。关联QA用同模型BF16地图，FP32确认单列，不把引擎差当修订机制。
- **Step5 T4：** 唯一step-5-preview/Step Plan，每批2、两遍独立打乱、分歧第三遍rationale，失败单项最多2次，共享≤8调用。只给source和final复述，不给QA/gold/模型/reading/分数。三类CORRECT_ROLES（主要事件及角色忠实，省略原连接词不自动算错）、GP_MISREADING（明确把初始错误角色写进复述）、OTHER（关键事件/角色缺失、其他不忠实、冲突或不可判）。新旧角色同时出现仍记GP_MISREADING并备注；兼容的额外事件不称逻辑矛盾，只判断是否忠实复述source。source/output联合SHA回显；完全相同source/output只标一次，固定用于全部条件，不按标签择版本。
- **读数：** 主：配对两侧source grammar合格的CORRECT_ROLES和GP_MISREADING比例及gp−control差，R1相对R0选择性恢复、R8一句恢复。source资格固定为该句全部原QA的两遍T3均acceptable且无第三遍降级，不按T4结果挑某个QA的grammar。OTHER/cap/空输出/两句格式/found-verb全报；主任务成功按全部预选输入分母，不把所有失败称GP误读。自动NP与V1同句仅作作者指标的描述校验，不能替代Step或证明角色。
- **统计：** 生成没有问题，故按source pair×NPZ subtype配对，condition内相同sentence SHA只计一次，不要求原QA问句相同；这使NPVP等不同原问句也能检验同一角色复述。用E52连接的lexical cluster，10000次cluster bootstrap/95%CI，按模型/构式/prompt全切片；条件比较取相同输入、配对两侧都覆盖。与E52逐题QA关系POST-HOC报告，不据公开No约定定义T4正确；finding仍需后续因果证据。
- **阳性对照：** 每构式作者control忠实角色比例；NPS补语/MVRR被动能否正确分句；四个source例子的格式/角色。control或格式低的切片只描述，保留全部输出。
- **噪声地板 + MIE：** P-A/P-B差、T4两遍一致率与未知；关注可分辨≥5pp选择性变化，启发式而非自动判断，不筛seed或重采样。
- **混杂审计：** 忠实复述指source断言内容，不是开放世界NLI；grammar边缘项单列；例4拼写/少样本与native格式分报；不按输出选材料/gold，不把复述正确直接推为内部parse共存。
- **决策表（跑之前写）：** QA约定低但复述正确→E3增加、E59明确题域/角色；QA与复述均旧角色且R1特异改善→E4/E1开放、E54/E55；R1无效且合理性梯度明显→E2增加、probe及因果校对实际可用性；格式/OTHER主导→报任务限制、E59角色选择；异质→保留全图、不挑一族局部连锁。
- **算力预算：** 三模型1–3 GPU·h，实耗看config；共享E52八个flock slot，保留既有常驻服务。Step持续审计，不设省API筛选；资产外部`/data1/xiangding/work/incremental-interpretation-revision/E53/`。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）

- 尚未生成，无能力结果或CI，C06–C09 L0。
- 生成器因菜单/历史文字引用跳到E64，跑前重命名为尚未占用的E53，未改历史编号。

### 生成仪器自审（T4效应解读前）
三族各3420任务，共10260，全部完整保存；Qwen8/Gemma12无cap，Llama8一个cap，空输出均0。实耗.0135/.0285/.0131 GPU·h（含加载，短输出高并发），原始config与prediction SHA外置。发现原辅助format parser将编号1./2.算成句子；从所有缓存统一剥编号重算，原文本/旧字段不改。四个source例子与inline-list机械校验通过，额外prose仍计入格式统计；新两句计数Qwen3205/Gemma3419/Llama3009，仅是格式、不是角色正确率。
T4仪器先用输入SHA排序固定前5个source、全部6条件的30输出（22不同source/output），仅核接口/回显/分类schema，全部标签固定复用于全量；不挑smoke中较好的输出或source。未闭合think只有中间推理、无final复述，保留未知而不把推理链送作T4 final；cap与明确角色内容另报。

T4-v1仪器发现我给该任务声明note≤35词，但共用校验器硬限制20词，导致合乎T4提示的响应错误拒收。v1在共享slot释放、HTTP调用结束后停止，无取消在途服务端调用；请求/响应/失败全部保留。v2只把T4校验恢复到原声明35词（D0仍20），对全部缓存按原请求/传输顺序机械重校验，10个既有包均通过；不看标签择优。原review留previous-reviews，原v1目录不改；运行规则仍优先原batch attempt0，再按既定单项attempt1/2，不采重复调用中的有利结果。未知/裁决失败仍不算通过。
E53统计仪器用独立合成三族×两构式验证：已知R1完全恢复得到+1且CI[1,1]、R8-null为0，两个QA复用同一句不增加cluster数；跨构式共享3个lexical cluster保持3而非6。合成资产不作为科学结果。

### native token政策纠正（全量T4启动前）
E52查到重复BOS后，核对vLLM实际prompt_tokens：Gemma12旧252 vs模板251、Llama8旧256 vs模板255，证实生成端默认也重复一次。旧6840输出完整保留；改为向vLLM显式传入已渲染模板的prompt_token_ids，两模型全部570×6任务在runs-native-v2重算，不按输出选择。Qwen模板无自动BOS、旧实际token完全相同，保留旧3420及其固定22项T4仪器标签。旧T4-full-v1尚未启动，只取消等待shell，无取消API在途调用；新全T4仅采用Qwen旧正确输入及两族纠正输入。原始字符串未改，输入策略/首8token另存，旧模型格式数字不作最终角色或格式结论。

### 重新思考后恢复（2026-10-07；T4效果仍未解读）
因用户明确要求继续深入探索，E53被用于I03/I04的另一自然用途：QA缺陷是否也进入角色表达。按原6条件、全部三族输出恢复双遍盲审和分歧裁决，原定义/批大小2/Step Plan step-5-preview/共8并发均不改；全部缓存与暂停记录保留。当前审模型新生成文本，不重审已完成的原句T1/T3，也不根据已有部分T4标签缩小范围。resume记录external E53/research-resume-v1.json，正在审核，尚无代表总体的角色数字。

- 2026-10-07 API算力优先级调整：完整数据与原双遍协议/缓存不变，两路driver各2worker，给新E63留4worker，共享总并发8。接管全部8请求槽、待返回/保存后替换driver，未取消HTTP；记录external E63/api-rebalance-v1.json。不是研究暂停或状态改变。

- POST-HOC T4语态/施事澄清：E63的固定顺序完整标注复核发现inchoative merge被主动形态误判施事（P15）。E53原完整双遍缓存继续保留；完成后所有MVRR输出按role-v2规则重新双盲，非MVRR有效相同packet复用，未解决技术失败重试，不根据旧类别选条。自动完整纠正/地图worker为finish_paraphrases_role_v2.py，PID652847；最终元数据qualified-v3已检查覆盖全部570源/member IDs。没有源句重审或生成重跑。
