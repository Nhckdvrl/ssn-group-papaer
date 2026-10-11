# E128：共同形成背景是否影响判断标准选择，而不仅是标签约定？（2026-10-12）

- **状态：** RUNNING；5e9549ed首评分前冻结，E127八批完整封版、E128八批CPU/source独立通过，固定四checkpoint16→32全部启动。
- **类型：** PILOT / CLAIM；不新开研究线、不改formal状态。
- **对应：** C23/C24、I04、P17。
- **问题：** 多Source从示例推断“评价食物”或“评价服务”时，信息等价公共背景下的私人缓存组合，是否改变新输入应受哪项判断标准约束？
- **为什么现在做：** E127三个8B确认在同no/yes词集、相反私人约定下，coherent−mixed +8.89/+5.86/+.78pp且Source特异margin正；仅词集选择不足解释。但该自然SST函数仍可拆成同一sentiment能力＋不同label convention，不能直接称选择了不同criterion。已有E122/118提供能力阳性、两个独立输入方面的功能任务。本项把**来源条件的标签约定**与**来源条件的输入标准**拆开，不再加head/NameK微观矩阵，也不将本项设为旧C21/22的新资格。
- **强近邻/切入：** Cho去除任务无关信息、TR/TL空间/映射、Li ACL24 structured task composition、Feng/Dai/Mixing绑定均已有所有权。特别Li表明新label remapping并不自动是新语义能力；Dai ordering/position分离也不等于criterion表示。ICES增加的是多合法Source从demos推断的标准在形成与共同使用中怎样受到上下文约束，不声称首次task selection/binding。
- **设置：** 四固定checkpoint Qwen3-8B/Mistral-7B-v0.3/Llama-3.1-8B/Qwen3-14B，同pins、conda verl-clean、FP32 eager/no training。复用E122所用冻结双方面材料构造与truth：每评论food/service完整2×2、8A8B、8新query、A按food，B criterion×private code四world。16 seed128001 discovery→32 seed128101 validation，新词/措辞/Source别名；全部固定，不按E127各家族效应选择模型。
- **操纵：** 两Source完全共享no/yes。只改变公共Source→同word-set表的两行顺序；信息/词频/长度相同，private原global位置不变。历史跨Source private形成全层禁止，所有query位置/层不直读schema。分别形成两order，合成全private A/B K/V 00、11、01、10；每组合joint与own-only两个Actor都问。
- **配置：** 4world×4pair×2scope×2Actor=64主接口，native8、独立一句指令8、single A1/B4=5，共85×8=680/context；21prefill/85query图actual每层hook。无layer/head/强度搜索，不新增far词集扫（E127已直接测）。
- **读数：** primary **B按service且与A使用相同private code（origin）的food/service极性相反query**，两Actor平均的joint coherent−mixed完整词表准确率，context为采样单位。此条件让两个标准给不同答案，却不能靠不同输出词集或两Source固定code翻转解决。secondary全部四world/all query、每Actor/private方向/order、candidate/full、same/different criterion、same/opposite code。保留两个label logits；origin的criterion-selectivity T=.5 mean[(zA−zB)(f−s)]，f/s均由private A code定向、输入四格完整；共同项和food/service/bias/product响应全留。T是输出响应的投影，不是新probe/独立机制证据，不识别输入过滤或抽象program。
- **阳性对照：** same batch native、一句指令、single每criterion/private code、每Source/order own-only实际函数；不得借旧E122分数代替本批。coherent与pristine、mixed-own与其对应own-order z/full argmax一致；Bworld→A privatecache图零。actual4D mask全层实收；fullsplit/cached/default/native/no-op；所有材料/private gold/匿名名字/图/组合来源独立核对。own-only平衡coherence0仅设计恒等。
- **噪声地板 + MIE：** 同run FP32 floor .001；10000 context bootstrap seed910。pilot数值有效即四固定32确认，不按科学方向筛。跨GPU硬件复制误差单独报告，不冒充same-run数值恒等。不设置追80%任务，结果失败或弱就是认识更新。
- **混杂审计：** fixed food-before-service与templated language保留，不能称位置无关criterion程序。whole-cache改变多种表示；已有binding/竞争读取/状态校准仍可解释。公共表本身有Source-word关系监督、没有criterion说明或private input-label pairing；私人仅形成时隔离，query仍共读。same-code/different-criterion的Source特异功能比code remapping更强，但不等于CriterionState不检索证据。两coherent原order性能差、所有negative/Actor成本必须公开。
- **决策表（跑之前写）：**

| 完整结果 | 怎样更新认识 |
|---|---|
| criterion primary和T正，私人函数阳性 | 共同形成背景约束也涉及采用哪项输入判断标准，不仅词空间/Code convention；把它与形成来源、固定word关联、公共协调整合为一个有界计算解释 |
| private code条件作用但same-code/different-criterion弱，且criterion能力与Source区分可测 | 公共背景兼容主要对应output convention，不把E127泛称所有rule selection；保留有界namespace/功能类型差别 |
| criterion函数本身弱或joint floor | 当前任务/接口无法排除标准选择机制；真实报告，不无限扩词/指令追阳性 |
| 有Actor/家族/方向差或mixed更好 | 全保留，构造结果反驳统一coherence优势；按实际功能说明计算范围 |
| 图/gold/数值失败 | 0-score修正或VOID后重新freeze，同seed；不当科学阴性 |

- **算力：** 四checkpoint固定16→32、单卡独立；预计1–2完整run GPU·时。21/20已缓存Q8/Q14/M7，L8可一次暂存20复用；按空卡实际并行，Q14可同卡16→32顺序，最多12空卡授权不等于铺开后继矩阵。E127完整结果先回齐再首评分。

## 结果
0评分。该卡从E127已完成三个家族确认与全文阅读提出；四checkpoint已固定，完整E127（含14B）先封版，再独立CPU/source审核及前评分freeze。本项是从code约定走向标准选择的一次有限高信息量检验，不以任何结果都支持同一个故事，也不提前锁定ID解释。

**0-score实现核对修正：** native与一句指令条件均保留原生private形成，只改变提示句。此前从E127继承的`independent=policy!=native`会把instruction与完全形成隔离混在一起，首评分前改为两者`independent=False`；所有实际token/primary/85条件/21prefix数量不变，CPU材料无需改选。独立审核末版源SHA `f0a0146708e193e017eb33a1caf955d8e4d4bf22d91d73abb403b500be92265a`后freeze。E126/127冻结instruction仅作为“指令＋形成隔离”辅助条件保留，不能称纯一句指令恢复。核心缓存比较不受该条件影响。

**前评分独立seal：** 192ctx/4032实际prefix图/6144query owner-scope/6144Source合成/12288demo truth均过；origin各discord4、四world固定B labelstream/输入多重集与truth、Global位置与no公共relay、实际tokenizer、末版native/instruction原生形成均核。Gram8I、T等于discordant两Actor margin平均明确，不当独立第二机制证据。参见results/e128/independent_review_2026-10-12.{json,md}；模型四权重与六metadata在20暂存SHA全相同。freeze后首GPU评分，不按科学方向挑确认。

**执行：** 5e9549ed/f0a014…前评分freeze。21 GPU1/2 Q8探索/确认、GPU3 Q14顺序16→32；20 GPU0/1 Mistral、2/3 Llama探索/确认。确认仅等待首context写入（冻结源已assert数值/组合/graph），不依科学方向。七卡实际空闲复查后启用，21 GPU0外部作业不动；Q14顺序避免额外模型暂存，Llama20四权重/六metadata逐SHA核。操作helper不改science，phase/seed全定，run与所有异常日志保留。
