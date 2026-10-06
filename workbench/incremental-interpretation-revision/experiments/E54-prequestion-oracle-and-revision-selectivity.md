# E54：问句前的可见性干预与修订选择性（2026-10-07）

- **状态：** DONE（完整三族/全部预定读出及配对统计）
- **类型：** PILOT
- **对应：** I03 / I04 / C06–C09 / P13–P14。由工具生成后，在任何运行前改用本workbench已预留的E54编号；不是事后补卡。
- **问题：** 改变源句位置能看到的后文，能否在清晰源支持任务中恢复真实理解表现，并保住原本正确的关系？它直接操纵先前解释可否利用消歧证据，不是一般输出格式实验。
- **阳性对照：** 见下文数值等价、cue版本与一句修订指令；不通过时不作机制解释。
- **噪声地板 + MIE：** 下文FP32校验与paired cluster CI；5pp仅为信息量参考。
- **决策表（跑之前写）：** 见下文五个预注册结果分支，不要求每个分支都形成论文。

## 设置与数据（任何新模型运行前固定）

沿用E59最终1014 QA / 507 exact-question GP/cue pairs（data-v1 SHA 1ab5cce2…5377）。输入S/Q不改，明确G2规则：仅句中蕴含支持Yes，未断言/矛盾均No；这测源支持理解，不能自动称世界命题错误或内部错误parse。原O2/E52结果全部保留。

固定Qwen3-8B、Gemma3-12B-it、Llama3.1-8B三族和原下载revision，FP32、eager、seed54；两选项顺序、letters/words均全报。基线与E59 G2/R0逐字相同。4D causal、整句oracle、一句修订指令在全体资格QA运行；歧义/非歧义oracle仅用既有T2一致位置的源句及配对cue。

歧义位置是句子属性：从同source/相同sentence_sha256的已有非空一致T2取得操作锚点；可用于这句的其他已资格问句，记录原anchor item_id。原数据T2字段不改；正位置有冲突即不进入定位子集，不重新标注或按模型结果选择。GP→cue位置只在相同原词能程序对齐时映射，否则定位子集整对排除。全部排除/同句用途覆盖记入manifest，实际n在运行前机械盘点。

运行前机械盘点：全体1014 QA；定位322 QA / 161同题pairs，72独立GP源句，其中51源句有initial/final两种用途。定位构式NPZ/NPS/MVRR；NPVP换序cue不能按同词顺序对齐，定位子集排除、整句干预仍保留。输入/原gold逐字段不变；数据SHA c6807416…c13b4，manifest在external E54/data-v1.manifest.json。

## 干预

1. CAUSAL：原因果mask，用4D表示，其他设置不变。
2. SOURCE_ALL：只有源句token相互可见，所有源句位置都看不到后来的Q、选项或答案；系统/问句/答题位置仍因果。
3. AMBIGUOUS：仅既有歧义区query行可看到全源句，其他行仍因果。
4. NONAMBIGUOUS：同数源句非歧义query行可看到全源句；按固定输入顺序选位置并报告新增边数，不择效果。此对照不保证完全等新增edge预算，归因须保留这一限制。
5. INSTRUCTION：原因果mask，增加既有一句“Read the whole sentence and revise any initial interpretation before answering.”，落实提示行为的恢复对照。

不运行科学probe/patch，不把mask本身称理想理解oracle。整句放开可能造成分布变化；null必须结合cue控制和数值校验解释，不能直接否定架构贡献。

## 读数

- 正确率、正确选项归一化概率；按连接lexical cluster平均、10k bootstrap / 95% CI。
- 每模型/构式/初始或最终问题分别报GP与cue的绝对收益；主对比SOURCE_ALL−CAUSAL，定位对比AMBIGUOUS−NONAMBIGUOUS，另报INSTRUCTION。
- 错→对与对→错分开报告，两顺序的转换不先平均为一个hard verdict；最终问题/原正确关系的损伤不能被gap缩小掩盖。
- 保留全体与source_gold_matches_grounding敏感性，不能由改gold引起的变化解释内部修订。
- 多用途子集只按相同源句是否有initial/final原问句事前确定；它是跨用途机制入口，不等于已完成干预迁移或下游推论证据。

## 阳性对照与噪声地板 + MIE

- 每族固定第一批源条目：4D causal与独立2D打分、单token prefix与joint序列LP核对（FP32差<1e-3）；因果mask中future禁用、oracle只允许S范围，padding不提供信息。检查源句前的token计算不依赖Q字节。
- cue控制正确率接近地板的cell只描述，不用于能力/机制归因；不删除该模型或寻找更好prompt。
- 参考E52原FP32/BF16+layout波动；当前全部FP32，仍保存batch布局和数值差异。5pp是首轮信息量参考，CI和实际错误/保持变化决定追问，不作自动科学裁决。

## 混杂审计与决策表（跑之前写）

| 结果 | 新认识或不确定性 | 下一步 |
|---|---|---|
| SOURCE_ALL在至少两构式/三族高cue控制上选择性恢复GP、final/cue不坏；AMBIGUOUS超过matched rows | 问句之前利用后文有实质作用；尚不是单一旧状态机制 | E55同词/位置因果修补，比较新用途迁移，不能只复现编码/使用gap |
| SOURCE_ALL有效但定位两条件相似，或多用途响应不同 | 整体额外访问/任务组装仍竞争 | 位置级干预与跨用途检验，不连续mask超参优化 |
| 减少gap主要是cue/原正确final下降，或与一句指令相同 | 尚无选择性关系修订支持 | 优先I04，区分破坏与恢复，不升级能力 |
| oracle null且数值正确、cue也受损 | 可能分布变化，不能判断没有正确关系 | 转用自然cue donor的E55；最多两次局部追问 |
| oracle null、cue保持好、指令也不恢复 | visibility alone不够，后续定位选择/组装 | E55，更新完整假说表，不称“GP没有path” |

## 算力与记录

预算：三卡独立FP32，首轮估计每族≤1 GPU·h，先实测短批数值/显存再铺全体；已有GPU服务不触碰。数据/模型/source SHA、脚本snapshot、每项prompt/score/region/edge量、失败全部外置E54/；git仅代码/卡/小摘要。实际n和GPU·h运行后填。HF离线推理，仅镜像资产。

## 结果

三族各14712评分，共44136；FP32 GPU·h分别.3007/.4393/.3381，总1.0781。三族所有当前数值/未来Q泄漏及source未来可见阳性控制均通过；与E59 G2/R0原输入逐字相同，hard flips均0，LP最大差.000651/.001128/.000288（eager/SDPA及batch布局差，非候选未来泄漏）。不能把跨后端最大LP差与当前校验阈值混报。

注册same-gold/words/全部literal类别的MVRR initial（各30clusters），SOURCE_ALL的GP gains为−4.72pp [−10.56,0]/−1.11 [−6.11,3.33]/−3.89 [−16.94,9.17]，cue−8.89 [−18.89,0]/−3.33 [−14.44,6.67]/−1.94 [−13.33,8.33]。未见跨族选择性修复。它与E59 NEITHER29clusters的展示分层不同，不混报样本。Gemma NPZ initial gap缩小14.29pp [7.65,21.68]，但GP+3.83 [−.51,8.67]、cue−10.46 [−16.33,−5.36]；Llama NPZ final gap缩小15.73 [6.74,25.28]也包含cue−10.67 [−17.98,−3.93]。定位子集的正负混合、全部letters/probability、错→对/对→错及多用途子集均保留，未据单cell选模型/构式/位置。

完整external E54/prequestion-oracle-map-v1.json及cluster-effects，小摘要results/E54-prequestion-oracle-summary.json。源码/仪器失败/模型/数据SHA全留。结论只限这个可见性干预：它不证明模型无正确解析或无修订path。按预注册分支改用自然cue donor的E55，不连续mask超参优化。I03/I04仍SEED，C06–C09全L0，暂无合格idea。
