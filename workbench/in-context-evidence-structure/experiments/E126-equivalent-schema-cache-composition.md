# E126：等价公共关系下形成的私人规则记忆能否组合？（2026-10-12）

- **状态：** DONE-CONFIRMATION；3家族16→32完成，独立raw/actual消费审计已封。
- **类型：** PILOT / CLAIM；不新增研究线、不改变formal状态。
- **对应：** C23、I04、P17。
- **问题：** 公共Source–输出关系的信息完全相同时，来源缓存是否仍依赖共同上下文下形成的兼容关系，还是可作为独立私人规则直接组合？
- **为什么现在做：** E125真实关系形成收益跨家族确认；交换关系表也提高完整输出、净减少other-source词，因此字面照表解释不足。Feng§4.1绑定IDs两侧对齐、Mixing位置/词汇多机制提供更强参照。本项从实际异常检验规则记忆的组合性，不优化table header或找新层/头。已有bindingID概念不作为创新。
- **设置：** 冻结Qwen3-8B/Mistral-7B-v0.3/Llama-3.1-8B，同revision、conda verl-clean、FP32 eager。官方SST5 gold0/4、既定train哈希demo分区/validation→test query；三家族固定n16 seed126001 discovery→n32 seed126101 validation，Source Alex/Sam→Robin/Jordan。A no/yes、B pass/flag，两私人方向，origin相反/cross相同；2world×2Actor×8query均匀平均。不按模型输出筛上下文、模型或方向。
- **操纵：** 只反转正确公共Source–word-set表的两行顺序，row0/row1包含完全相同的事实、名字/word多重集与token数，私人tokens/角色/global位置不变。表在HEAD后、所有监督前；所有历史跨Source私人demo访问全层禁止，各Source保留本Source历史、共同HEAD与公共表。query每个token、每层不能读公共表。分别编译order0和order1的cache后，整套A私人K/V与整套B私人K/V合成00、11、01、10；HEAD和不可读公共cache取0，query相同。00/11共同形成，01/10从等价上下文各取一Source。替换整个Source-owned所有private tokens的逐层K/V，不选head/layer、不拟合、不插值。
- **评分：** 4cache×joint/请求Source-only query×2world×2Actor=32接口；native无表4、single3、independent一句指令4，共43×8=344/context。11种prefill图、43query图各层实收hook。Source-only配对平均coherent−mixed必为0是图/组合恒等式，仅作实现控制；逐order/Actor实际私人函数能力才是阳性，不能把均值0称新双分离。
- **冻结读数：** 主读数完整词表accuracy，关键context paired .5[(00joint+11joint)−(01joint+10joint)]，均匀world/Actor/query；此2×2配对对比抵消两单缓存加性quality差，测联合读取中的非加性交互。辅助candidate accuracy、own-word/other-word率、gold-oriented margin；A/B、same/opposite、private方向、00与11差完整保留。A gold-oriented B-code halfresponse signed/abs保留。joint−own每cache单列。
- **阳性对照：** 同批single私人功能/native与一句指令，不假定完美；两coherent缓存相对各自pristine query z/fullargmax≤.001且相同，混合own-only与相应own-order原缓存同；default/native4D/cache no-op、首context整prefix/query等价评分≤.001。全层实际mask消费、缓存深复制/不污染；全部context A私人cache对Bworld改变为0。order1公开缓存替换成0不影响whole-query遮罩结果。gold/匿名Source/语义/private代码均重构。
- **混杂审计：** 行顺序可能改变位置绑定、词汇显著性或其它上下文化；正效应证明指定cache组合存在上下文依赖，不直接识别bindingID或唯一算法。整个cache移植改变多种表示，暂不把后续量化归于ID子空间。query保持普通来源名和两缓存读取、原global位置不重用。00与11能力差必须呈现，不能由劣质原记忆混合产生的损失冒称兼容机制。private监督只在历史形成中隔离，联合query仍能读取两Source；公共关系本身属于监督。新context/名字而非新benchmark，官方query池可与旧实验重用。
- **噪声地板 + MIE：** 数值floor .001；10,000 context-bootstrap interval种子910；n16数值有效后三家族固定n32、不按科学正向挑选。CI跨零为未定，不设任意80%修复线。
- **决策表（跑之前写）：**

| 结果 | 认识改变 |
|---|---|
| coherent联合优于mixed且逐Source/order函数仍强 | 独立形成的私人规则记忆不必天然兼容；共同形成背景影响组合。回到Feng/Mixing的两侧关系/多机制检验设计，不能称首次ID或独立抽象规则 |
| 两种组合等效或CI不明 | 当前信息等价row-order不支持共同参考结构假设；保留E125形成阳性，停止此假设的盲目模板扩大，回到整篇解释 |
| 私人order函数已坏/效果只一个Actor或方向 | 保留所有cost/非对称，按实际结果限制解释；不增加十种模板追阳性 |
| mixed更好 | 共同形成不是普遍优势；结果与预设兼容故事竞争，回读最强近邻，不改原读数 |
| 数值/geometry/gold失败 | 记录0-score修正或VOID后重新冻结，不把实现失败作为科学反例 |

- **算力：** 3缓存所在节点的独立空卡16→32，预计.5–1.2 GPU·时。仅在先决E125完整结果后执行；不因为可用12卡就扩展矩阵。
- **科学源：** `scripts/e126_equivalent_schema_cache_composition.py`；首评分前记录hash/commit。依赖冻结builder f02104…与truth函数不改。

## 结果
六批CPU均exit0/等价事实与私人几何通过，仍0科学评分；独立真token/可达图审阅进行中。科学源SHA256 ad2c6f7af7ab81966ea1253a80e7006747f3485b182fddd1453ffbb1ceb45975，评分前commit待审。ResourceTracker退出stderr保留（同旧环境，exit0），不改科学配置。

**评分前定位补充（0评分）：** CacheBlend§3.3/4已拥有一般独立KV块漏跨块上下文化的质量问题；SADA ACL26§3/4.4拥有训练的context→parameter内部对齐。新检索的Zellige作者技术报告（2026-04-24，未核投稿/代码）讨论cross-session chat-boundary结构与patch，不能由其模板涨分识别唯一机制，也不能忽视它已提出的普遍cache兼容对象。此项不声称首次缓存不可组合，仍检验public事实/私人监督完全相同、固定global positions的配对联合功能。nearest corpus词汇近邻多为multimodal composition/memory/SQL，未召回不作first依据。

**独立pre-score封源：** 科学源ad2c6f7af7ab81966ea1253a80e7006747f3485b182fddd1453ffbb1ceb45975。六批144ctx、1584实际prefix流/1584mask、2304query scope×owner与2304整Source K/V选择全部独立核对，无须修改真值/图；实验已有数值/actual hook待GPU实现验证。独立结论确认后才commit/执行，未用科学分数选条件。

**执行更新：** discovery三家族启动；Qwen首ctx数值8.20e−5、Llama2.48e−5，composition/graph0；三confirmation进程先预加载相同冻结模块，仅等各自pilot第一行通过已有全部数值assert才执行固定seed/materials，未按科学方向选择。辅助/tmp预加载启动器仅解决NFS环境import延迟，不改科学源/参数/读数。

**完整结果：** Q/M/L primary +23.49[20.80,26.07]/+10.40[7.96,13.04]/+5.42[4.00,6.79]pp，所有Actor/private/world均正；主要Source词空间使用，candidate仅+1.12/+.63/+.20pp。own实际约92–97%，平衡coherence0为恒等式。Q/M order11−00负、Q/M margin primary负点CI0与M A联合低全保留。6批144ctx/49536scores/.627887GPU时，12462项独立max0/1584token-mask/49536gold/实际52800prefix+206400query层消费，所有GPU exit0。未识别latent非加性/bindingID/无损规则组合。按决策表正向更新共同背景的joint功能依赖，仍需区分仅词空间使用与同词空间private rule选择；E127已设计0评分。C23补有界证据、等级不改。[报告](../results/e126/report.md)/[审计](../results/e126/independent_review_2026-10-12.md)。


### POST-HOC：选错Source词时与哪套规则相容

完整确认后新增既有argmax诊断，未加GPU/改primary，单独文件 `results/e126/posthoc_selected_code.{json,md}` 与 `scripts/posthoc_e126_selected_code.py`。仅origin反向private约定可区分两映射；所有contexts保留。coherent−mixed的“另一来源词且符合该来源私人gold” Q/M/L −23.73[−27.44,−20.02]/−10.06[−12.79,−7.42]/−4.88[−6.64,−3.22]pp。多数other-word错误与另一Source规则相容，不是请求code简单换词输出；输出相容仍不识别内部是否调用该规则。shared输出下能否约束规则选择留给首次评分前冻结E127检验。

**辅助control语义校正（不改冻结科学源/primary）：** 存储的instruction条件同时增加一句提示与完全阻断private跨Source形成，属于复合条件，不能将其相对native差称为纯一句指令恢复。该条件不参与主cache-coherence比较；数值保留，附录B统一披露。E128在0-score阶段将其改为只改变一句提示。
