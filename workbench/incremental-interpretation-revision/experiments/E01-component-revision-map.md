# E01：跨构式 revision structure 系统测量（2026-10-05）

- **状态：** RUNNING
- **类型：** MEASUREMENT / residency
- **对应：** C01 / C02 / P02 / P03 / P06
- **问题（一句话）：** cue、blocker、歧义延长对最终解释与初始解释支持的作用，是否随读数和阅读任务的先后顺序出现可解释的结构？
- **用户修订：** 2026-10-05 人明确取消先前停步gate，要求通过系统实验发现有价值的新叙事；保留E00–E06结果，不追认旧对照通过，不以校准失败阻止本实验。new.py生成E08后改为DATA_PLAN预留E01，编号说明不隐藏。
- **设置：** 已下载Qwen3-8B固定revision、FP32 frozen、native chat thinking off、无训练。Jurayj固定90个component lexical sets、626 canonical sentence variants、2672候选QA；Step5逐句逐题审计后以已核对行进入测量，原字节和审计不确定行全保留本地。
- **条件：** NPZ GP/comma/direct-object-or-other-blocker/intransitive × short/extension；NPS GP/that/lexical substitution × short/extension；MVRR GP/unreduced/morphological substitution × short/intervener。不得把词汇替换当同义结构操作；NPZ非宾语blocker单列。
- **任务：** 句先/题先；neutral/upstream-reg0 fixed demos；无/一句generic revise，八个配置全部报告，直接使用native assistant boundary，不附My answer is。NPZ/NPS final-role问句锚定实际main/embedded verb phrase；MVRR final-role只问relative modifier，避免把voice判断塞进role任务。保留final semantic、initial semantic诊断；NPS/MVRR initial semantic没有强制No gold，按支持概率观察。
- **至少两个解释：**
  1. commitment/reanalysis：extension在GP放大initial支持，而早cue或有效slot-blocker削弱此作用；cue能同时提高final并降低initial。
  2. semantic completion：初始语义关系支持主要由词汇/世界知识决定，即使cue明确、role正确仍存在，甚至nonGP也存在；词汇blocker效应不同于相同词汇early cue。
  3. task-driven evidence use：query先到时cue/extension作用改变，可能反向；system demos/一句revise会改变某种读数而不改变另一种。若差异只来自模板默认值，下一实验通过query内容/位置作干预，不把它当能力机制。
- **读数：** construction×condition×extension×question type×system×order×instruction的P(Yes)、accuracy（仅有可用gold）、choice mass；lexical-set配对bootstrap CI；cue−GP、blocker−GP、extension−short，以及extension×cue、cue×query-order交互。最终roleYes且initial-roleYes、最终semanticYes且initial-semanticYes的逐set响应组合，明确是分开调用的行为组合，不是内部表征共存证明。
- **阳性对照：** explicit cue是否改善对应role/semantic读数；nonGP/lexical控制的分项；两种任务极性的简单读数；全量报告，不作为停止整个探索的硬门槛。
- **噪声地板 + MIE：** FP32相同prompt重复0 flips/max drift约2.6e−5；prompt order/system/instruction的变化本身作为研究对象，报CI和效应量，不设80%等任意通过线。
- **混杂审计：** 相同lexical set配对；extension语义/附着、blocked配价由Step5逐条审核，不由agent自判gold；API最多8并发，完整ID/hash/finish_reason覆盖检查，不把timeout算OK。没有根据结果删行，审计版本随run保存。每家族单列，不把NPS/MVRR语义兼容命题记为错误。
- **决策表（跑之前写）：**
  - cue/extension作用跨query发生明显有结构的改变 → 下一实验拆query提出的初始解释、query位置与证据到达顺序，区分问题诱导和被动遗忘。
  - role与semantic随cue不一致 → 用自然相同词汇的comma/that/unreduced对照追语义补全与attachment修订，进入下游解释使用后果。
  - 只出现已知GP/recovery → 查最相关论文ownership与局限，选择能改变解释的一个新增对照，不包装novelty。
  - 读数呈模板/坏数据伪影 → 定位具体伪影后改读数继续测，保留完整原结果；不停止驻留，不扩无目标模型sweep。
- **算力预算：** GPU0/1/2/3四独立单卡，按family×system分块，预计合计<2 GPU·h；复用现有venv/模型/cache。实际待记录。API审计并发≤8，数据为公开上游许可材料与衍生问题，不上传密钥或私有资产。

## 结果（跑完后填写；不改上面的内容）
- 外审探索层更新（该批推理之前）：此前用户明确授权opencode免费模型逐条审计；Step5因402不可用时，另冻结MiMo-v2.6-flash-free完整外部预审行，机械检查输入/hash/ID/normal finish与覆盖。只纳入源lexical-set序号≤3的已返回变体（事前源序号，不看推理结果；缺失逐项报告），与Step5 cohort隔离。全部gold=null，仅报告PYes、choice mass与配对概率效应，不能计算能力正确率或据此升级C01/C02。语义裁决来自外部模型，agent不自行标注；后续Step5复核仍必要。free模型质量尚不确定，不称等同人审。
- 执行范围更新（首次E01推理之前）：Step5完成3/626句变体、13QA（NPZ:1 GP/cue short + MVRR:1 lexical/extended），随后返回HTTP402 quota_exceeded。先运行这13条已核对的104个任务检验读数；全量measurement保持待审，不把未完成行当OK。n=1的lexical-set contrast只报点值、不报虚假零宽CI，不能升级稳定结构主张。已异步告知人补充额度；此前授权opencode继续外部预审，与Step5最终标签分开。
- 数字（含CI）：Step5层13QA/104任务（3变体，单lexical组contrast CI=null）。free外审snapshot1共25变体104QA、101 eligible/808任务，88.12s / 0.02448 GPU·h、全部gold=null；13共同问题的外审答案13/13相同、certainty相同，这只是很小覆盖的审核一致性，不是全量质量证明。NPZ前两source sets句先cue−GP final-role PYes短+97.98 pp [96.40,99.57]、extended+66.88 [43.80,89.95]；GP extension−short initial semantic +97.12 pp [94.41,99.82]，显式cue约0。blocked/unambiguous extension也可降低role支持，须追读数/NP引用而非只选GP好看的故事。n=2区间不能代表已证成稳定结构。
- 结果文件：[Step5层](../results/E01-partial-summary.json)、[free概率层](../results/E01-opencode-snapshot1-summary.json)、[外审来源与缺失](../results/D0-opencode-exploratory-snapshot1.json)、[free scores](../results/E01-opencode-snapshot1-scores.csv)、[config](../results/E01-opencode-snapshot1-config.json)。
- 按决策表执行了什么：
- 主张变化：
- POST-HOC：

### Snapshot2更新（本批推理之前）
- 仍使用事前登记的各family源序号≤3，不按Qwen结果选择；完整外审覆盖54/60变体、232候选QA、228eligible，gold全部null。新增外审返回补齐更多NPS/MVRR和NPZ配对，未审/timeout六变体仍保留缺失记录，不当作语义无效。
- 8个既定配置全跑，共1824任务；snapshot1结果与输入原样保留。新增行允许追三family的cue/blocker/extension读数结构，但每family最多3词汇组，区间只是小样本描述，不能称跨词汇稳定机制。
- 输入SHA256 `32756bdc1f60848ab0764e4ae900ed5025f6f5cdc512b3198f862c06d7764a52`；审计与来源见[D0](../results/D0-opencode-exploratory-snapshot2.json)。

### Snapshot2结果
- 完整1824任务/228eligible QA，189.35s、0.05260 GPU·h，前3源组每family最多3lexical sets，缺失的6变体仍未补标。全部正确率字段null。neutral/reg/base NPZ final semantic short GP≈1、cue=1；原role short GP=.0134 [.0000,.0360]、cue=.6681 [.0043,1.0000]。NPZ cue extension−short role −21.69 pp [−56.20,+1.17]，semantic约0；nonGP role −44.63 [−88.05,−1.21]（n2），semantic约0。不是“语义理解无损”的全能力证明，只是这些独立调用对原句中最终事件的支持。
- MVRR long−short final semantic +48.69 pp [≈0,+97.39]（n2），role基本near floor；与NPZ长句方向不同，不能预设所有构式extension=更深承诺。NPS GP long仅一组、CI=null。更多组到来前不把方向差作为稳定跨构式finding。
- [summary](../results/E01-opencode-snapshot2-summary.json)、[scores](../results/E01-opencode-snapshot2-scores.csv)、[config](../results/E01-opencode-snapshot2-config.json)。全八prompt保留；C01/C02不升级。按原决策追读数具体异常：E11外部head/full-NP/isolated审计已启动；不追加赢家prompt。


### Snapshot3：扩大独立词汇覆盖（本批推理前登记）
- 核心信息问题仍是语言操作如何改变final/initial的role与assertion支持；不再加prompt模板。新用户授权免费opencode/Step均可标注，必要时Luna逐条补审。
- 截取当前**全部已完成**独立opencode逐variant审核，不以模型结果、构式效应或audit快慢选源组。冻结279/626变体、1189QA、1158eligible：NPZ121/NPS85/MVRR73；未完成/失效情况完整保留。源数据SHA `abc1ac0061ce91aa867d54cd8bc74914b07f5771650b90da56b8decb69cd14d8`，新snapshot SHA `b161273b173d2ff8b69773acb1af67acd4a936ef95d0069f0fbf71668cceff5b`。主分析只用两个条件共同具备的source-set交集，报告每项n/IDs；acceptable stratum一并报告，不补出不存在的完整pairs。
- 主要读数仍PYes与GP/cue/blocker/nonGP×extension及order交互；**新批次**次读数采用eligible、非diagnostic、certainty=clear的外部答案999个（Yes628/No371）。190个无label保留null，含语义兼容diagnostic；correct只是外部model annotation agreement，不称人类gold能力。此前snapshot1/2结果与null gold全部保持原样，不追改旧实验。本批Luna6超时补审另存，不混入这张固定MiMo cohort。
- 固定已使用的neutral/native、句先/题先×base/一句repair四配置，共4632独立任务。三构式分别在GPU0/1/6单卡并行，共同8B FP32/TF32 false/batch32，预算<.15 GPU·h；没有新增模型、训练/SAE/probe。组合器核对每个预期prompt hash、完整任务数、数据/模型/代码/choice token集合相同。
- 竞争解释与决策：GP特异extension损伤、cue也损伤的通用NP/问句问题、语义补全/兼容性与role不一致三者由对应配对交互区分。若role损伤同时发生于cue，按E11引用对照解读，不叫GP承诺；若final/initial的语言操作响应在更多源组仍分离，优先针对该语言依赖设计后续证据操作，不能将分离本身称新idea；若小样本方向不重复则如实降级线索，不搜索模板赢家。
- noise不作为停步gate；沿用FP32已知prob漂移且报告source-cluster CI。分项用于找下一决定性操作，不用单一显著项升级C01/C02。


### Snapshot3结果（完整四配置，不选赢家）
- 三family全部完成、4632实际新推理任务，总.097710 GPU·h；每个task的prompt hash/完整ID/模型dtype/token集合/代码commit机械核对，三个family无重复calls。旧snapshot1/2原样保留。
- NPZ同9源组initial-semantic extension GP−cue DiD：句先base +51.63 pp [21.60,84.02]、repair +40.98 [15.09,67.95]；题先base −20.29 [−53.11,9.93]、repair −10.66 [−32.92,.79]。不称统一digging-in；query-driven reading/readout/语义补全仍竞争。
- NPZ句先base原final-role nonGP extension −24.41 pp [−47.20,−3.46] n13，GP −30.36 [−60.26,−1.53] n10；无歧义下降重复而final-event多近ceiling，E11引用问题不能略去。
- NPS final-event下降why：eligible句先base DiD −8.49 pp n8，acceptable −.027 pp n7；差异NPS:7原had rode，long GP外审marginal/PYes=.3232，comma long≈1。两个strata均为跑前规则，原项目不删除、不悄改。MVRR句先base final-event DiD +17.45 [−.14,45.28] n7，尚非稳定机制。
- [解读](../results/E01-external-snapshot3.md)、[完整分项](../results/E01-external-snapshot3-summary.json)、[config](../results/E01-external-snapshot3-config.json)、[scores](../results/E01-external-snapshot3-scores.csv)。C01/C02仍L0，C03保留。下一步从语言信息而不是模板继续拆解释；尚无够支撑paper的idea。
