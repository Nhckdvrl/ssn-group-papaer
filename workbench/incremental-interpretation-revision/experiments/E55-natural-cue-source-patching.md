# E55：自然线索句的问句前位置替换（2026-10-07）

- **状态：** DONE（完整三族/4层/3位置/双向干预及统计）
- **类型：** PILOT；I03/I04/C06–C09/P13–P14。生成器返回E431，任何运行前改用本线预留E55。
- **对应：** I03/I04、C06–C09、P13/P14；关系跨用途与选择性，而非工具效果本身认证novelty。
- **问题：** 无问句/答案参与的源句状态替换，能否改变同一句的多个原有问题，并在反向替换时破坏相应正确关系？当前不是新颖性或“有/无parse”的二分判决。
- **来源：** E54可见性未有跨族选择性恢复，且一些gap缩小来自cue受损。Hanna的有限feature null和HMM/CBM跨用途证据要求区分状态可用、状态被用及干预分布变化。直接有限activation patch优先，不用梯度近似筛位置。
- **阳性对照：** 原cue源支持表现；self donor替换数值等价；两方向配对；已有一句修订指令的E54对照保留。弱cue cell只描述。
- **噪声地板 + MIE：** FP32/eager、同布局self patch max LP差<.001，源前缀hidden与完整prompt对应S位置差<.001；5pp仅信息量参考，cluster CI与修复/损伤分别决定追问。
- **决策表（跑之前写）：** 跨位置与用途有一致方向且正常关系不坏→独立留出/功能干预；只改变初始No→回答偏好仍竞争；只大面积损坏→工具不具语义选择性；null→不推无表征，结合完整E53与下一问题组合，最多再1次局部追问，不以无限位置扫描找赢家。

## 数据与资格

复用E54原1014 QA的全部已有定位组，不按E54效果或任何模型正确率筛选。使用同source/同S既有一致T2歧义span和消歧word属性，原S/Q/gold不改。difflib的相同word顺序匹配只用于位置映射；歧义区域按原词逐个映射，不把cue插入的that/was当作同词。消歧词/句末词也必须同词唯一对齐；每个对应词的token数量相同才可直接替换，否则整对在该模型机械排除。资格及实际n在科学forward前保存，全部排除报告，NPVP换序不硬对齐。

固定三族Qwen3-8B/Gemma3-12B-it/Llama3.1-8B及原权重，G2源支持规则、两选项顺序×letters/words全留。ALL与same-gold、initial/final及相同源句多用途分项；不更改E59/E54原结果。

## 干预与对象

4个事前分位层：decoder layer index floor(f*(L−1))，f=.25/.5/.75/1.0。三个源位置：既有歧义词区、消歧词、句末词。操作是该层block输出residual整向量替换，对每个相同词对应的token逐一替换。

- BASE：完整原因果原输入，prefix-only单token评分。
- PAIR：GP接收同题cue donor；cue接收GP donor。两方向均保留，不只展示修好GP。
- SELF：仪器阶段以自己截断源前缀中的相同位置做替换，证明实现不因截断/索引/布局产生效果；不把SELF当新科学样本。

Donor仅forward到最后源token，缓存对应block输出；问句、选项、答案绝不进入donor。每个S在所有用途共用同一donor，不按问句训练、筛层或调强度。完整recipient中source对应前缀须与截断计算等价；prompt无重复BOS。替换只作用源位置，其他query rows不变，没有非因果mask。

该pilot是跨用途机制入口：原有initial/final问题不是全新任务，不能称已完成独立下游泛化；整residual还含语义以外因素，反向效果也不自动证明只替换了关系。与Hanna/Knowing Without Saying/Tang/Guo的具体增量须由后续新预测与干预后果建立。

## 读数与成本

每层/位置/族/构式/目标/读出分报GP和cue绝对gains、gap变化、错→对/对→错，两mapping先各自统计转换。按预先连接lexical cluster平均，10k bootstrap95%CI。全部层/位置报告，不选最佳层估计总体；与E54只比较相同输入覆盖的BASE，概率是答题条件概率。

预算三卡独立≤1 GPU·h/族（短批先实测）；所有源cache/data/config/prediction/code快照外置E55，git仅代码/卡/小摘要。先数值校验再全体，沿用GPU共享锁，不触碰既有服务。HF离线，仅镜像。

## 结果

三族各11440，总34320评分；FP32 GPU·h .2370/.3423/.2657，总.8450。BASE与E54同输入0hard flips，最大LP差.000143/.000029/.000066，全部当前source/self仪器通过。所有层/位置/readout/metric均报告，无胜者过滤。

探索性定位：MVRR initial/words/same-gold，预定前1/4层歧义区PAIR对GP的gains分别48.33pp [25,71.67] / 36.67 [16.67,56.67] / 26.11 [10,45]，各15连接clusters/23同题pairs。反向cue gains−54.44 [−77.78,−31.11] / −33.89 [−52.78,−16.11] / −25.56 [−45.56,−8.89]。GP错→对的mapping级次数27/22/11，当前切片GP对→错均0；这不是整体不破坏的证明。GP final对应歧义区gains+3.33/+5.00/−3.33，不能称已经跨新任务迁移；Llama不同readout方向还需保留。

NPZ同位置initial+40/+40/+50pp，但same-gold只有5clusters，不用于广泛能力/机制升级；NPS initial cue18.2%/22.7%/52.3%偏弱，不能借其null判断能力。位置效应主要出现在前1/4层，后层hard变化小，不等于没有后层语义：完整LP有非零变化。最后block后的源替换对当前答题没有后继计算路径，结构性零应作无路径控制而非发现。此限制补记于完整结果解读，原计划与全部输出保留。

完整external E55/natural-cue-patch-map-v1.json及cluster-effects、source-cache.pt和SHA；小摘要results/E55-natural-cue-patch-summary.json。当前证据：部分早期源区域对GP问答有因果作用，反向也成立；粗残差含不止关系成分，尚无指定高层角色变量或完整语法机制。C06–C09全L0，I03/I04 SEED，不宣布合格idea。由实际位置/层结构产生新猜想I05：问句是否过早消费源状态；E60用只切访问时机的实验检验，不重复调source mask，也不再走无限单模型位置链。

### 科学forward前数值仪器修正（2026-10-07）
首版Llama通过；Qwen/Gemma source-prefix对完整prompt的raw residual最大绝对差分别.001953/.109375，自替换LP最大差仅.000061/.000038，prefix评分实现差0。旧fail及代码全部保留，尚无科学替换输出。原向量绝对.001跨模型尺度不适用，改用每个位置的相对L2误差<1e-5，并仍要求self patch LP<.001；同时记录raw误差与向量尺度。校验扩到按输入排序固定4个不同S、全部readout/mapping；不用科学效果选择仪器输入/阈值。所有S/Q/gold、patch层/位置/强度/资格与读数不改。

扩大固定4-source校验后Qwen/Gemma相对L2通过；Llama最大raw差.000114且self LP差.000117，接近零范数位置相对比1.456e-5过严。最终校验采用逐位置绝对误差<.001或相对L2<1e-5的组合容差，并仍保持self LP<.001；保留所有raw/relative/scale。不据科学效果调整容差，不更换这4个source。

### 全体科学运行前盘点
数据322QA/161pairs/72GP源句/51多用途源句；三族token机械资格均220QA/110pairs/52GP源句/37多用途源句，构式GP-Q pairs为NPZ19/NPS47/MVRR44。51pairs因相同词token数量不等整对排除（包含cue标点），全部ledger保留；这是覆盖限制，不是胜者选择。每族4层×3位置×PAIR加BASE共11440评分。NPZ定位覆盖较窄、NPS cue弱，不作广泛机制或能力升级。全S/Q/gold及所有已有QA输出不改，不追加标注去追逐效果。

双向读数的解释边界（效果解读前）：PAIR的cue→GP与GP→cue是互为反向的两个干预；后者的cue损失可作方向性检验，不能照E54误当同一修复操作的副作用，也不能用两方向gap缩小认证选择性。保持性须看同一GP修复干预是否保住原正确/final关系。这个澄清不改已注册读数、层、位置或数据。
