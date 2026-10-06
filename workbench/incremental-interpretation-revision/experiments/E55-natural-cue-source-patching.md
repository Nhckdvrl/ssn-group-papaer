# E55：自然线索句的问句前位置替换（2026-10-07）

- **状态：** RUNNING（三族数值校验通过，全部预定位置/层执行）
- **类型：** PILOT；I03/I04/C06–C09/P13–P14。生成器返回E431，任何运行前改用本线预留E55。
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

尚未运行，未升级任何主张。

### 科学forward前数值仪器修正（2026-10-07）
首版Llama通过；Qwen/Gemma source-prefix对完整prompt的raw residual最大绝对差分别.001953/.109375，自替换LP最大差仅.000061/.000038，prefix评分实现差0。旧fail及代码全部保留，尚无科学替换输出。原向量绝对.001跨模型尺度不适用，改用每个位置的相对L2误差<1e-5，并仍要求self patch LP<.001；同时记录raw误差与向量尺度。校验扩到按输入排序固定4个不同S、全部readout/mapping；不用科学效果选择仪器输入/阈值。所有S/Q/gold、patch层/位置/强度/资格与读数不改。

扩大固定4-source校验后Qwen/Gemma相对L2通过；Llama最大raw差.000114且self LP差.000117，接近零范数位置相对比1.456e-5过严。最终校验采用逐位置绝对误差<.001或相对L2<1e-5的组合容差，并仍保持self LP<.001；保留所有raw/relative/scale。不据科学效果调整容差，不更换这4个source。

### 全体科学运行前盘点
数据322QA/161pairs/72GP源句/51多用途源句；三族token机械资格均220QA/110pairs/52GP源句/37多用途源句，构式GP-Q pairs为NPZ19/NPS47/MVRR44。51pairs因相同词token数量不等整对排除（包含cue标点），全部ledger保留；这是覆盖限制，不是胜者选择。每族4层×3位置×PAIR加BASE共11440评分。NPZ定位覆盖较窄、NPS cue弱，不作广泛机制或能力升级。全S/Q/gold及所有已有QA输出不改，不追加标注去追逐效果。

双向读数的解释边界（效果解读前）：PAIR的cue→GP与GP→cue是互为反向的两个干预；后者的cue损失可作方向性检验，不能照E54误当同一修复操作的副作用，也不能用两方向gap缩小认证选择性。保持性须看同一GP修复干预是否保住原正确/final关系。这个澄清不改已注册读数、层、位置或数据。
