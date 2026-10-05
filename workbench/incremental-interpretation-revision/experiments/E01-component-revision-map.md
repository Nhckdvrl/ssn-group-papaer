# E01：跨构式 revision structure 系统测量（2026-10-05）

- **状态：** PLANNED
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
- 数字（含CI）：
- 结果文件：
- 按决策表执行了什么：
- 主张变化：
- POST-HOC：
