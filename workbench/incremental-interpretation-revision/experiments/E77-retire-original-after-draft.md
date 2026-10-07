# E77：关系草稿消费时停止读取原Source（2026-10-07）

- **状态：** DONE；仓库生成器全局E431重命名本workbench E77，先卡后运行。
- **对应：** P17 / C09 / I03；GP旧解释修订后，外显关系解释是否能共同保持？
- **问题：** E76草稿能提高final却损伤initial，没有共同修复。已生成的草稿不能支持另一关系，还是Task继续读取原句造成重新组装/竞争？移除原Source后续消费是一个核心因果对比，不再扫prompt/位置。
- **数据：** 完整原E65/E76 892QA/356S/178clusters，MVRR27/NPZ89/NPS36/NPVP26，原S/Q/gold完全相同。FREE原E67 NONE1068完整生成、EVENT_FIRST原E76新1068完整生成直接重用；输入SHA和所有model manifest验证，无效果筛选。0新API、不重审成熟数据、不等草稿role标签；未审核草稿不称正确parse。
- **操作：** 逐token重建E76原提示与候选，NATIVE概率完整重用。CUT_SOURCE只在每层移除原Source所有token作为key、到Source最后token之后所有query的边；Source内部原生编码不变。Task全部规则、notes、Q与answer仍原位置/原文本/原candidate。所有后续位置均cut，避免Task前部绕行读Source；Source之前位置不含原S。草稿作为已有外显文本完整可消费，原gold评价S→草稿→答案总pipeline，草稿绝不当gold。
- **读数：** FREE/EVENT_FIRST各自CUT_SOURCE−NATIVE原QA correct/p_correct，initial/final/all及joint allQ；另各自CUT_SOURCE−DIRECT只作端到端参照。全三族四构式GP/cue，words/letters各两mapping，按QA→Source→lexical cluster等权、10000 bootstrap/seed77 CI95。无成功草稿/真假模式筛选。
- **阳性对照：** 完整E76 map SHA与raw闭合；每族每分片固定首Source所有条件native4D vs2D LP、与E76原LP差<.001，Source及之前全layer hidden变化0，cut边非空且只postSource query→Source key，没有未来边。完整8分片才读科学效果。
- **噪声地板：** mapping flip全部报告，paired cluster CI；不加seed重复。cue保留与本构式baseline强弱是归因限制，不强行叫阳性。
- **竞争解释：** CUT共同恢复initial且保留final/cue→原Source读取参与关系竞争，才对新增草稿原子审计、检验是否正确草稿被覆盖；CUT不恢复且相似取舍→不能用原Source消费作为充分解释，回草稿形成/新旧关系组装；只一族或cue同样改变→一般消费/模型策略，不能GP共同机制。损伤与null完整保留。
- **混杂：** 屏蔽源改变可用证据且mask非训练分布；源原QA gold仅评价完整pipeline，不说明草稿含正确答案。即使正效应也不能直接宣称训练/部署方法或正确parse。保留同文本/位置/Task只排除删除重排造成的混杂，不追加控制sweep。
- **算力：** ≤3 GPU·h，21408新QA条件，8独立H20；三族同manifest FP32/eager/offline/seed77，不杀原轻服务。原NATIVE/DIRECT零重跑，只有固定仪器小样本。资产外置E77，大文件不入git。
- **决策表（跑之前写）：** 本块为E76后一次核心追问，阴性/异质后停止局部Source/notes网格，更新完整假说与信息价值，直接接自然P1消费及原子关系证据；不改workbench状态/关线。阳性再审新增文本，不为使用原金标预先bulk审计。

## 结果

全三族8分片CPU逐条任务/prompt SHA/token/跨度通过，21408任务完整，最长414token。8H20已启动，PID见外置runner-pids-v1.json；未读科学效果。

## 完整结果与自审

全8分片/21408新QA条件/2688格已完整读，0新API，1.743138GPU·h；map SHA088c5dda6788337f03abc6273278539b767fdab11ef682d3f7ad4b0b84b7e608。资产外置E77，results/E77-retire-original-summary.json保留672主格并引用全map；全部SOURCE/DRAFT raw闭合。原Source及更早全层hidden差0，native4D/2D差0，E76 native复现LP最大.000328064；所有cut仅postSource→Source，无未来边。

- NPZ GP EVENT_FIRST cut−native words initial概率Q/G/L +4.41 [-0.35,+9.98] / +20.44 [+12.73,+28.57] / -3.32 [-7.63,+0.87]pp；final -0.28 [-0.75,-0.00] / -28.66 [-38.23,-19.70] / -6.58 [-12.03,-1.13]。没有共同修复；letters保留异质，G同样取舍，L joint letters +7.87 [+3.93,+12.36] 不能替代words joint -2.25 [-9.55,+5.06]。
- MVRR GP FREE cut−native words initial概率 +3.68 [-1.39,+11.75] / -0.11 [-5.17,+5.37] / +0.61 [-2.99,+4.06]；final +0.01 [-0.89,+0.91] / +7.12 [+0.93,+14.87] / -0.31 [-12.67,+10.60]。EVENT_FIRST G final +19.15 [+6.53,+32.99] 但initial -2.54 [-10.19,+4.62]、joint -1.85 [-11.11,+5.56]；三族整体仍无共同恢复。
- NPS G EVENT_FIRST initial +44.47 [+27.77,+63.84] 但final -27.52 [-41.84,-14.31]；FREE G initial +18.00 [+6.95,+30.49]、final +2.78 [-0.00,+8.33]，是一个族/弱cue构式，不能升级机制。NPVP与所有cue阴性完整保留；L MVRR FREE cue joint -24.07 [-40.74,-9.26]。
- 全192 mapping格报告，L words cut FREE翻转最高19.44%，letters两草稿最高55.56%，不可只报更好读出。新指令/生成cost不重复，这只是对已生成草稿的消费路径测量，不能由cut阴性证明草稿语义不存在。

自审：Source继续消费不是共同失败的充分解释；部分initial增益伴随final损伤，与一般信息撤除仍竞争。Task仍要求只判断原句，而mask使原句不可用，所以不把cut当部署方法，不认为它等于自然draft-only。本局部mask块到此收束，不扫新的Source/notes位置或层；E78在三族更强现成模型上测真实DIRECT/Source+draft/draft-only流程，验证哪一个完整行为对象值得追，0新API。E76−78块结束后统一更新hypothesis/interestingness。C06–08 L0/C09限定L1不变，尚无合格idea，无需人决定事项。
