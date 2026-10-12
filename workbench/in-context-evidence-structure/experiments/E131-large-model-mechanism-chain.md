# E131：大小模型上的同一证据形成解释

- **状态：** PLANNED；18批独立CPU通过、末源封定，首评分前commit freeze。
- **类型：** CLAIM / 跨尺度核心机制检验。
- **对应：** C21–C24、I04、P17。
- **问题：** 能力更强时，关系证据的历史形成、随后读取与Source条件使用发生什么变化？已有answer→label形成解释能否在更大模型上用相同干预与读数成立，而非仅保留小模型结论？
- **为什么现在做：** 用户明确要求先核ACL/EMNLP/NAACL如何跨大小模型检验理论。Sun ACL25附录D/Table5在7/8/70/72B上验证关键阻断、表示与label-swapping等同一链条，层位置可变；CoSToM实际解释7/8B两个架构，70B为评判者，不算其大模型机制证据。ICES14B已有原生/自然文本/函数阳性，但不能仅凭它当更大容量已经统一；E129/130的Cue接口不改变C21–23理论对象。此项检验原论文的三个核心环节，不追加字段/头/层搜索。
- **最强解释：** Cho/CTA/AddUp拥有上下文化/输入标签合并/权重与V内容；Sun拥有映射PC/匹配/解码；本文候选增量仍是合法多Source监督的关系来源、输出依赖形成操作与实际Source函数使用。同一计算解释不要求相同层编号、相同效果量或所有模型保持错误。
- **设置：** Qwen3-32B post-trained与Llama-3.1-70B base，固定可核pins；同家族Qwen3-8B、Llama-3.1-8B在新确认材料作配对锚点，14B现有证据保留。FP32权重/缓存/eager/frozen，TF32矩阵乘加速同一操作并记录实际flag，无量化、无新增训练，单节点2卡/4卡连续层dispatch，不跨节点共同forward。官方70B与Nous镜像全部30权重SHA一致；复制完成后逐文件核。模型选择预定，不按分数更换。材料为既有受控与真实SST生成器；不是新benchmark。
- **固定协议：** 原E121的43条件形成/关系内容/系数1重建；原E120的64条件无donor原生操作与受限恢复；原E123的85条件真实文本两来源功能政策。原脚本与分析不修改；E131仅生成设备分派兼容副本，必要device-local mask比较/模型revision/计时/TF32flag如实记录。逐stage保留全部条件、namespace、查询scope、方向、single与一句指令。两大模型每stage16→32；两小锚点每stage32确认，合计18个完整run。发现池使用各stage旧固定seed；确认native/mechanism/function分别使用131101/131102/131103，validation材料，新确认在大小同family/可匹配tokenizer逐字配对，无旧模型效果筛材料。
- **读数：** 三环节的既有预定核心读数：E121原生A形成的B规则幅度差及label-interface系数1K/KV/V raw/rule-double-contrast误差（对照zero，所有通道/读取背景保留）；E120 full-source native cross-answer removal signed B-rule response及gate/native受限恢复、within/private controls；E123 shared两Source平均candidate/full准确率、selective/native/all-isolation/query-only配对CI及private/gold-conflict分层。新确认大小模型在相同context做配对差，用context bootstrap，不跨任务池假称相同样本。正确率无损不当机制消失；若大小读数不一致，先分形成与读取的原接口，不以换layer挽救主张。
- **阳性对照：** 同token单Source正/反私人规则、一句指令native、same-run完整token/cached、实际每层mask消费、pristine cache与noalias/seq；答词/分隔符/label实际位置与既有定义一致。多卡数值可达图与单卡科学含义相同；模型每层cache在对应设备，禁止CPU/disk offload与低精度。原有self与graph-zero保留。
- **噪声地板 + MIE：** 保留原.001nats cached/full与self floor（TF32误差也必须通过，不临场放宽），固定10000 context-bootstrap910；两大模型固定16数值有效即32，不按方向选确认；所有零效应、负向、接近完美性能及不可靠primitive同报。阶段计时为model-run wall hours，多卡device-hours另按实际卡数计；另记从首次模型装载到最后stage的连续驻留device-hours，含生成/分析/阶段间等待，不能继续将单卡或stage计时字段直接当总作业GPU时。
- **混杂审计：** 模型训练配方/数据与参数量同时变化，不称受控scaling law；完整对照是同计算对象在这些capacity-spanning checkpoints上的跨模型检验。两个家族非每个尺度全部架构。设备dispatch只变数值实现，需明确误差；不拿失败load/不正确graph当科学负结果。无头/层/强度调优。primitive强而最终correct时，关系影响仍可能在confidence；不将没有accuracy损失包装成没有形成机制。
- **决策表（跑之前写）：**

| 完整跨尺度结果 | 认识如何改变 |
|---|---|
| 大小模型同原生形成/固定重建/操作贡献，准确率不同 | 同一历史关系操作在不同能力下继续存在，实际使用后果可被读取补偿；用实测gate/full差判断，不靠错误持续性定义意义 |
| 形成作用保持、读取或函数政策不同 | 在同一形成机制基础上解释Source使用的容量差异；原先共享/隔离的功能预测有可测条件，不强求同一收益数字 |
| 大模型形成/重建/原生操作关键环节不成立且private函数可靠 | 现有解释不能完整覆盖这些checkpoint；检查预定形成/读取接口所区分的计算变化，回最强机制文献推理，不直接退成小模型缺陷或用局部新头救故事 |
| 只有primitive/数值/实际mask失败 | 明确不可识别范围/实现事故；不作对理论的科学判决，也不隐藏它 |

- **算力：** Q32在有缓存/空卡节点的2卡FP32，L70在同节点4卡FP32；large D/C可独立节点复用同pin材料，small锚点独立单卡。最多12张授权空卡，正在E130卡计入占用，不碰外部进程。源冻结前只有下载/CPU检查，未评分。

## 首评分前记录

当前论文正文/附录SHA1c87…/413a…保持。已停止优先压版式；本项直接围绕跨尺度理论，而不是给旧结论增加完美适用范围。所有结果都必须回主问题判断其认识增量；不自动关线、改状态、凑claim或以论文页数宣布novelty完成。

## 首评分前独立封源

[独立pre-score审查](../results/e131/independent_pre_score_review_2026-10-12.md)，JSON SHA `f704da0132cfe0a6565ce3a2bb47e6874be6bdd9cfe21adf3cb1f6b5df142098`：三engine整棵AST仅执行allowlist差、analysis相同；18批480ctx/5440prefix/12160图/30720 query masks/268800 gold槽通过。六个大小新32确认材料逐字相同；真实DynamicCache CPU字面patch48例、全layer K/KV/V/self848例通过。独立审查没有GPU rerun，actual多卡mask/cache/数值仍由首context检查。

末protocol SHA `550890014e6553290695f7fb6f35823a4b25ef06acca551649934a69d30b643f`、dispatch SHA `2e6d2d2ab1f38937408c0a60ce09c141f4ddb6abd303857311a263c1638508bd`，科学engine与父pin在manifest。Q32目标fvcrc20 /dev/shm/ices_models/Qwen3-32B逐shard已核，L70两个实际节点继续下载/核验；先提交推main才启动Q32与8B，70依同identity gate准备完执行。0科学评分、无效果筛选、三认识不改。
