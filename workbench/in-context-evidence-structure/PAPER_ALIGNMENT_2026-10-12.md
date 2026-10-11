# ICES 整篇论文对齐：研究问题、主张与实验递进

**对应C21–C24、I04、P17；2026-10-12。** 上轮有限矩阵完成并不等于整篇研究完成。本页按原论文可辨认的论证步骤比较，不声称重建作者真实发现顺序，也不以实验编号或固定claim数量判定论文质量。

## 1. 主问题与三条主文认识

**多个来源共享输出时，当前来源的证据怎样形成，随后怎样约束新输入？** 即使模型答对，形成与使用仍然是待解释的计算。输出词共享是使不同来源关联发生联系的变量，而不是论文唯一研究对象。

| 主文认识 | 对应账本 | 它改变的推断 | 目前直接证据 |
|---|---|---|---|
| MC1：来源位置访问不确定所用关系的来源；输出命名参与历史证据形成 | C21、E90/E91 | 按Source读取不等于Source关系隔离 | 固定A、query禁B仍有B-rule作用；历史答案K子图逐query预测namespace反事实 |
| MC2：这条历史消息不仅是静态答案偏置，也能传递学到的关联 | C22 | 固定label words不等于固定证据内容 | 同label stream/multiset的跨关联配对与同类移动竞争；V/KV部分内容作用 |
| MC3：原生判断使用已形成的证据，并依赖完整读取环境；关联运输与具体criterion功能不能等同 | C23/C24 | 一个局部反事实高r不确定整套来源规则如何执行 | native formation×reading crossing；criterion×私人约定完整功能矩阵、prospective方向测试 |

C24是MC3的功能分辨率检验，不为了claim数再单独包装一项贡献。旧I04为现象入口，E85均值预测和负结果保留。主文要给读者连续的计算解释，不能只列四种接口有差异。

## 2. 与相关工作的实验链实际比较

| 原论文与核对范围 | 论证递进（非真实构思时间线） | 可学的尺度 | ICES对齐程度/缺项 |
|---|---|---|---|
| [Cho2025](https://arxiv.org/html/2410.04468v3) §3–5、bypass/连接消融段 | 输入编码→label合并→query读取→连接消融→主路径外旁路 | 用完整计算链解释已有现象，消融与匹配控制检验操作 | 阶段与native功能已连接；原生历史形成操作阻断/恢复需直接补 |
| [Cho2026](https://arxiv.org/html/2509.21012v4) §3–4.4、指定附录 | unseen-label挑战复制解释→训练低秩filter检验→原生子空间动态→denoising-head消融 | 一个解释应在竞争机制不同预测时检验，不只涨分或定位 | 固定word关联/完整方面响应有竞争预测；必要操作与自然文本功能仍需补 |
| [CTA](https://arxiv.org/html/2504.00132v2) §3.1–3.3 | aggregation限制→跨示例状态功能交换→歧义任务→上下文化路径恢复 | 必要信息流与任务功能接上，而非每个token新名字 | 源关系的形成预测已新测；不能用donor重建替代原生operation检验 |
| [AddUp](https://arxiv.org/html/2605.16591v2) §3–6、E.3/K/L | FV可加重建→因果注入→歧义QK对齐→QK/V交叉→信息来源扰动 | 预测、功能与直接因果路径分开，保留背景依赖 | 系数1逐query预测/native crossing齐；本项target为历史形成而非其末位FV，接口不同不自动等于新算法 |
| [CoSToM](https://aclanthology.org/2026.acl-long.421.pdf) §3–4、A.2/E/F | activation→心理状态QA→浅层encoder训练/decoder冻结→同接口对话用途 | 三RQ、两模型两域，五基线；QA改进与下游用途直接连接 | 三家族＋更大同族及多种材料已足；形成机制的实际功能需有自然任务阳性，不必强仿训练修复 |
| [Crosbie](https://aclanthology.org/2025.findings-naacl.283.pdf) §4–8/Limitations | 标准ICL与pattern任务→整head ablation→具体pattern操作knockout | 组件参与不确定哪项操作承担功能 | 直接启发E120；阅读Findings是方法比较，不改变本仓库不投Findings要求 |

CoSToM主文明确报告3RQ：解释、steering、对话使用；两个开放模型、谈判/说服两个域，生成评价N100/N200和人工/模型评判。这个量级参照不是要求ICES也有相同模型数、训练方法或评分者。Cho/CTA的贡献同样不由实验表数决定。当前ICES已有多个家族与确认材料，缺的是能支撑更强原生操作解释的环节，不是总体配置太少。

## 3. 当前证据够到哪里，为什么仍继续

1. **数量：** E00–E119远超最低“几个实验”，但前期不能全部算到现在主旨。C21–C24各有独立确认，E115–119的24批/576context不是novelty本身。
2. **主张：** 三个主文认识足够形成论文，不再凑新claim。关键是“历史答案路径能够重建”是否可以进一步解释“原生模型需要怎样形成关系证据”。
3. **递进：** 现象→功能来源测量→形成子图→关联内容→原生使用→criterion功能已有顺序，但操作必要性缺环。自然MHS文本的single较弱，不能替代有功能阳性的自然材料。
4. **意义：** 具体知识增量是输出命名在query检索前改变Source特定证据的关系内容，并可因果预测这一形成过程。已知上下文化能容纳它，故不宣称推翻CTA；也不因相容就自动撤回这项具体解释。

[独立整篇主张审计](results/e119/manuscript_claim_audit_2026-10-12.md)确认上述两项缺口，同时独立点算全A target仍有部分重建，未将旧阳性贬成恒等label替换。摘要中criterion重建的target将明确为actual label接口，不能指向whole-history响应。

## 4. 现在执行的两项关键实验

| 卡 | 直接缺口 | 竞争预测 | 执行后要做的判断 |
|---|---|---|---|
| [E120](experiments/E120-operation-necessity.md) | 原生形成操作的必要贡献与受限图恢复 | 真正承担关系形成→阻断后选择性减少、仅恢复答案到label可部分带回；构造路径/冗余→donor预测好但native作用保持；一般扰动→自己规则也同样受损 | 更新原生操作解释，区分native/gated，不要求全网络恢复或继续搜head |
| [E121](experiments/E121-natural-sentiment-mechanism.md) | 有private能力阳性的真实文本机制泛化 | 学到的关联→固定词的配对作用跟随B private方向与新query情绪；静态word偏置/文本扰动→共同偏移或within同样大 | 明确自然语义的功能范围，不按逐例正确筛数据或补许多benchmark |

两项先做独立pilot，数值有效即按已冻结设计在新材料确认，不按阳性挑模型。独立问题并行，确认原样执行；当前没有追加字段/头/层矩阵。之后回到MC1–MC3逐句检查证据、理论增量与叙事，完成主文图和复现资产，不把新残差自动转成下一关。

## 5. 目前不能声称已完成的事

E120/E121全部16→32确认与独立raw审计已完成，直接补上原生操作贡献和功能阳性的自然任务两项环节；不能由有限恢复声称全网络唯一算法。没有证明一个独立、位置无关的criterion程序，也不需要把它设为全部旧形成结论的资格条件。是否形成最终候选由人决定；本次用户已明确授权继续完成科研执行和论文对齐，不以标题或内部状态审批为理由停下。


## 6. E120/E121后的整篇认识与正在执行的整体预测

原生形成操作阻断四checkpoint减弱跨来源规则作用，有限路径恢复在A-only正、native依模型负/正/跨零；历史共享不能只写为错误混合。自然SST5 single正/反均有明确能力，冻结namespace路径KV r .931/.948/.930/.966，固定输出的关联abs均确认；Llama signed负完整保留。两项均填原证据链缺口，不以多两张表自动保证acceptance或novelty。

下一步[E122](experiments/E122-source-preserving-formation.md)在首评分前5b166d73冻结：对称保护来源答案形成，保留一般上下文化，与全跨Source形成隔离、仅query隔离竞争；两个Actor使用同一prefix缓存。primary是两个Actor平均准确率并分别核A/B，不是同一query“两人同时答对概率”；agree/disagree是两人gold是否相同，不是两函数是否相同。四criterion×code world完整，single各函数/instruction/图零均保留。四模型16→32正在跑，不因探索分数改policy或筛模型。

主文依旧三个认识，正在把它们写成连续过程：来源访问≠关系来源 → output-dependent形成的预测与native操作 → 固定word的关联内容 → 正常/自然功能使用 → 整体Source规则与criterion功能的边界。E122决定构造性预测是否成立，不把每个残差升成新必过关卡。

### 主旨升级前再次核对的直接近邻

2026-10-12重读上述CTA/AddUp关键定义，并回到下面三条已存在论文卡的原文段落。不是事后发现术语相近就撤回形成阳性，也不把设定不同自动判为novelty。

| 最强近邻 | 所拥有的解释 | ICES增量所需的实际证据 |
|---|---|---|
| [Yang/Cho/Inoue TR/TL](https://arxiv.org/html/2509.24164v2)；正文定义和H.4前轮已读，本轮再核 | label空间识别与空间内映射；串行任务跨头作用 | 两合法Source共享同label空间，固定A原监督却改变它所携带关系；不是把TR重命名为Source识别 |
| [Demonstration Conflict](https://arxiv.org/html/2603.04464v1) §4.3.1–4.3.2；预印本接收状态未核 | 少数污染、query forerunner位置敏感、早期创建/晚期解决及head消融 | 两规则都合法，output命名影响prefix中关系形成；操作级阻断与冻结效应预测、保留一般共享的整体使用，而非首次早/晚分离 |
| [Jurisdiction](https://arxiv.org/html/2609.27603v1) §3/§5；预印本接收状态未核 | context规则是否有权覆盖现实知识，训练选择性使用demonstrations | 不争论现实知识优先，两Source约定都应可用；正交Source关系/输出代码并测原生形成与功能来源，不泛称首次证据适用性 |

这些工作应在主文清楚引用。检索对应accepted/rejected地图；限定venue查询未召回、arXiv搜索阴性均不能当first证据。最强compression risk仍是“已有上下文化加label retrieval足以容纳”，回应须用已经确认的关系来源测量、output-dependent子图预测和新整体反事实，不能靠新组件名或更细接口。


## 7. E122完成后的三认识与下一自然用途预测

四checkpoint平均使用收益+2.93/+3.42/+7.37/+2.78pp，targeted比all-cross形成+11.91/+9.81/+12.65/+13.33pp；两gold冲突收益更大，一致goldQwen/14B有显著成本。独立raw/真值/图/数值与主文呈现审计已封，上一审计的两项paper-critical缺环已填。没有把共同平均当每Actor都显著或joint正确，也没有将保留访问当固定其它信息。

C22/C23依据SST真实benchmark＋controlled餐馆、两家族以上n32/§4/§5实测达到有界L3；C24仍单双方面task L2。主文三个认识约3200词＋附录约2400词，图从计算解释到功能反事实递进，不以claim数或实验数自动保证接收。正式候选状态不改。

[E123](experiments/E123-natural-source-function-policy.md)是进一步有信息量的整体验证：同样源函数政策在strong-private真实SST能否发挥作用，输出namespace是否改变收益；它让“output-dependent关系形成”与一般attention扰动在新材料产生不同预测，非再加层/头/alpha。已经首评分前freeze，四family全部16→32执行；不把它未出的结果记入当前主张，也不把E122已有阳性绑在其成功上。


## 8. E123封版后：整篇的具体增量与实际覆盖

自然SST两Source政策全部四checkpoint16→32确认，shared平均+7.32/+5.37/+9.47/+7.42pp，两ActorCI均正；私有single、指令、same/opposite、within movement、全词表全部保留。far candidate/full差揭露完整规则使用中的wordspace功能，但不把它首次命名为TR/binding；Feng实体-属性匹配与Mixing多机制已有所有权。headroom/wordpriors解释限制ns政策对比，不撤回C21实际消息预测、C22固定word或E120 native作用。

与Cho/CTA/CoSToM学习的链已经具体落到：自然问题→错误推断的反事实测量→冻结形成子图预测→原生操作/受限恢复→固定词关联→正常使用→双方面及真实文本的构造性政策预测。英文主文三认识、完整技术附录、四checkpoint/新材料确认、50,848项独立复算均具备，量不是主张升级或novelty的自动判据。核心增量是合法多Source监督的功能来源与output-dependent形成，而非只定位某个token、首次上下文化或完美修复。当前未识别整个模型唯一算法；这不应自动成为发表具体机制认识的新门槛。

最近全文回看：Feng§3–5/G、Mixing§3反事实接口，已补对应定位与论文卡。最新nearest corpus得到TROVE/SelectiveInduction/检索记忆等词汇近邻，web精确关键词主要召回不相关provenance/旧induction，不以未召回证明first。最强机制近邻继续以实际正文CTA/Cho/AddUp/Feng/Mixing/TRTL为参照。正式候选状态由人判断；本轮最后的独立整篇审阅专门检查新主文三认识与已有证据是否对齐，不自动派生新实验矩阵。


**最后整篇核对已完成：** [E123 paper-critical审阅](results/e123/manuscript_claim_audit_2026-10-12.md)核原三认识及新增304项数字、最强近邻所有权，当前有界措辞与证据适配，无必须追加GPU实验的实质缺项；两处namespace总述/均值排序语言已修。主文SHA3d2cbd06…/附录f8aa1d89…与审阅snapshot一致。该结论是证据适配，不是接收预测、唯一机制或所有未来文献无重叠的保证。
