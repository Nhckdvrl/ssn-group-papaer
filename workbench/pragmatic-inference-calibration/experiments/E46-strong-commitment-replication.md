# E46：strong-commitment-replication（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / D1–D2；E43更强同族配对边界，非新benchmark
- **对应：** C02/P14
- **问题（一句话）：** E43的分目标变化在第二个强14B家族是否可测，并能与事实读取、初始意图理解、格式遵循区分，还是目前只有一个可用强端点？
- **设置：** 原OSF unmy6 Exp2八对话、四actual-event角、64commitment/32trust human cells、703原human responses；完全复用冻结E43原问题与唯一balanced clarification。Qwen2.5-14B Base/Instruct官方pinned E41 manifest，完整共用Instruct tokenizer。每端点literal64/meaning64/trust64/binary72 source rows各分一GPU，bare/chat各一次：共1056greedy预测、八独立作业，锁后接入。FP32/noTF32/single/max16，无thinking/API/新标注。
- **读数：** 完整EOS且whole integer有效才评分，literal/meaning/trust分开，全八材料×四角效应与bootstrap2000/seed0；缺失全行bounds，不筛正确model材料。初始理解8及actual facts64各独立报告，事实正确不等于语用能力。reuse source conditional human norm，不将任何跨目标效应自动称over-inference。
- **阳性对照：** 原703人类join/原OLS舍入已E40通过；本轮CPU 264source全量、两个checkpoint actual full-token逐接口相同、264分组无交叠/遗漏。每作业/接口首末重复生成IDs精确一致、LP<.001；全部八作业通过才出全矩阵。source/shard/token/script/dependency SHA原raw保留。
- **噪声地板 + MIE：** greedy重复只查实现；八材料bootstrap是材料不确定性，非训练总体。先查事实读取、初始理解错误、所有ratings可用性；无差异大小预设，不能依赖某一goal一次显著CI。
- **混杂审计：** 同家族同输入但Base的chat训练支持不保证；不单独RLHF归因。强家族比较不是共同训练population。human根据正确初始理解筛选，model不筛；trust的人类前序commitment vs独立model调用差异保留。人工root图像转录无独立审核，不能L3。retrospective commitment不是prospective action，不可根据后来事实声称原意图不存在。已有Braun/Shetreet、SDA、ICLR目标模型拥有相关claim。
- **决策表（跑之前写）：** A第二强端点可用且相同分目标结构跨唯一clarification保存→记录候选边界，下一步独立来源/自然材料和ownership；B任务成功但结构不同→支持分对象解释，削弱单一criterion；C初始理解/事实/格式失败→仪器不适用，0能力升级，不增加恢复prompt；D人类也有相同结构→parent复现，不把human-normal效应称model缺陷。
- **算力预算：** 八单GPU短generation，预计<2 GPU·时；所有模型已由E41完整下载，不再下载模型；实际wall各config。不能为了占卡多加seed或人工改语义。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
跑前记录：尚未运行GPU。C01/C02均L0；不预注册方向、不宣称已找到论文贡献。

2026-10-03执行记录：CPU 264全源/全部shard/token gate通过，八作业已接入锁。固定placement造成空卡等忙卡时，只停止无GPU子进程的coordinator并r2按可用GPU拿锁；完成预测不重跑，未改任何数据/runner/评分。实际日志ROOT/E46-queue.log与E46-queue-r2.log都保留。

**调度校对：** 上句“无GPU子进程”判断错误：`/proc/pid/task/pid/children`只查主线程，漏掉另一个线程启动的Base literal child；退出coordinator释放锁时child仍运行，r2 Base trust模型加载OOM、0预测。Base literal最终完整保留，未重跑。失败目录/日志留ROOT/runs/E46-commitment-Qwen2.5-14B-trust-failed-oom-r2与同名log；r3只补trust，七个完整shard跳过。加实际显存检查防有进程但锁已释放，不改变scientific runner/条件。不是模型语用negative。


全八shard1056预测完成，source/token/script/完整数值gate全部通过，见 [summary](../results/E46-strong-commitment-summary.json)。Base bare理解8/8、facts64/64、两个条件三个目标各32/32完整；Base chat理解与facts均0完整正确、numeric原0/1/0、clarification0/0/0。Instr bare理解0/8、facts5/64、numeric全0；Instr chat理解6/8、facts58/64、所有numeric32/32。Instr的两个理解失败是nonEOS解释，不偷偷解析首词；6个fact错误完整EOS No。不能以两端点各自最好入口作干净stage因果。

Instr chat原literal own-truth effect在meaning假/真时21.875 CI[11.25,36.25]/52.5[41.25,62.5]；meaning评分的literal-truth跨目标效应8.625[.5,18]/26.875[13.75,40.625]；单句clarification后对应3.75[0,11.25]/29.375[14.375,44.375]，并非统一消除。人类同样有部分cross-layer效应，不能叫pragmatic hallucination。全目标、八材料、不筛理解/fact错项、CI与缺失bounds都保留。决策表B/C/D：第二强端点读数可用，但未共同通过基础理解，且关系依目标/角落；不升级scientific claim、不追加prompt救分。C01/C02仍L0。
