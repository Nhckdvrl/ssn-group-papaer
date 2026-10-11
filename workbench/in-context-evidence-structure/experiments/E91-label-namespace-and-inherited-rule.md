# E91：另一来源的标签词怎样改变当前来源的规则读取？（2026-10-10）

- **状态：** DONE（24 pilot→48新context确认；同引擎、无筛选）
- **类型：** PILOT；一个namespace反事实，无训练、无层/头选择
- **对应：** I04 / C16 / C20 / P17；直接连接E48的换词读出解释与E90的来源内继承效应
- **问题（一句话）：** 分开输出标签的作用是否只来自另一来源Value退出当前答案方向，还是也改变了当前来源的可访问表示及其检索Key？

## 科学缺口与最强解释

E48指定头的foreign-label DLA下降、attention大致不变是有效事实，但它只分析了直接读foreign位置的路径。E90已在整个query禁读B时测到B规则仍影响A。因而需要检验标签namespace在这条间接路径中的作用，不能再用一张foreign attention图解释全部收益。

简单“B的输出词投影远离A词表”的版本预期主要作用在Value/最终内容方向；只改变A的Key、保持A的全部Value与最终词表不变，不应充分转移这种作用。较强的contextualize-then-retrieve解释允许B的输出编码改变A的Key，从而改变读取A自身证据的程序。二者可以共存；结果不是强迫Task inference与copy二选一。

已经读/核对：Cho2025主电路和shortcut；Contextualize-then-Aggregate主文§3；How Few-Shot Examples Add Up§4–5/E.3的example Key与QK/V因果分离；Local Task Vectors官方主文；E48/E90原卡。**K/V分离、Key影响attention、label承载任务信息本身都有所有权。** 本实验的具体问题是“B的标签身份怎样改变raw不变的A的读取，以及是否越过完整query的Source过滤”，不是重新发明这些组件。运行前venue corpus lexical nearest结果弱，不能把它当没有近邻的证据；直接论文定位更重要。

## 设置（运行前冻结）

- Qwen3-8B revision b968826d9c46dd6066d109eabc6255188de91218，conda verl-clean，float32/eager。
- E56原MHS test池的24新contexts，seed91001；每Source各8demo，4新race+4新gender query，目标Source A。评论真实、来源规则受控，**不声称是真实人的原标注规则**。名字/角色与A的映射方向随机；A/B各自正负完全平衡。不复用E90挑出的成功contexts。
- source A始终用safe/toxic；B用同词或pass/flag（沿用E46/E48）。每词均单token，换namespace不改变序列长度/位置；A所有raw token保持相同。
- 每namespace有conflict/aligned两context，只翻B的8个labels，A及全部input/姓名/位置不变。所有B标签频率始终4/4。
- 每对运行native query与**entire-query A-only**：所有query位置只能读取A完整demo/header/query，B整块不可读，不只最后答案或label。接着在shared recipient缓存上，分别只把**A全部位置的K、V、K/V**换成far donor的对应缓存；B缓存保持shared但不允许读取，query/output仍shared。donor的B规则与recipient配对相同。
- 原生Namespace下的A-only K/V全换应精确复现far A-only，是数值阳性，不是独立科学条件。K-only中cached Value/最终label方向保持shared，但后续query状态允许正常演化，不伪称每层Q固定。
- 附加一条指令对照只运行shared native的两rule world：Use only the examples of the requested annotator to infer and apply that annotator's labeling rule. 不做prompt搜索。
- 读数与噪声字段见下。命令：`CUDA_VISIBLE_DEVICES=0 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/e91_label_namespace.py --out results/e91/qwen3_discovery --n 24 --seed 91001`。

## 读数、对照与决策

- **读数：** `z=logit(toxic)-logit(safe)`、A gold符号g。每context rule效应 `d_i=mean_q(g_q*(z_aligned-z_conflict))`，报告signed mean、mean absolute与答案改变率；先在context内对Input类型作contrast以去除constant-label bias。Namespace收益和K/V转移以paired margin/accuracy及rule-effect幅度差报告，**不除微小gap，不把positive T当完整rule程序转移**。
- **主对比：** shared_Aonly−far_Aonly的absolute rule effect；shared_Aonly−Kpatch以及shared_Aonly−Vpatch。另报告Kpatch/Vpatch与far_Aonly的逐context d误差和prediction/margin误差；两者的非加性并存允许报告，不寻找新的Shapley模型。
- **阳性对照：** shared native/Aonly复测E90的功能依赖；A K/V全换精确复原far_Aonly；默认causal 4D/split cache与整段前向一致。若工具对照失败则不读科学结果。
- **噪声地板 + MIE：** 数值最大差≤.001nats；24context paired bootstrap10000次seed910。namespace或K转移改变rule幅度约.15nats/准确率5百分点会改变投资判断，但不是自动判决。显著转移仍需新contexts确认，候选确认seed191001/n48，第一次结果前不启动。
- **混杂审计：** A原始信息、当前输出词表、位置长度、B标签频率配对固定。B词语义/先验改变正是变量，尚不能把任意词表编码推广为pure semantic similarity定律。A K/V donor改变其历史上下文化但不改变raw A内容；K-only会影响查询后续状态及attention归一化，不等于孤立新Task module。query禁读B后Value方向也可能经A的位置间接继承，故far效果本身不能证明Key机制或Source信息真的独立。单family、共享test池，全部样本保留。
- **决策表（跑之前写）：** 见下表；不论结果不扩词表、层或格式矩阵。

| 结果 | 科学更新 |
|---|---|
| far只在native减少B效应，A-only几乎无收益 | 这套换词的主要作用经直接foreign读取；不强造Task形成解释 |
| A-only也降低B效应，V足以转移而K小 | 有经A位置传播的内容/Value作用；原“读出分隔”需覆盖继承路径，不称独立rule表示已形成 |
| A-only效果可由K-only明显转移，cached Value固定 | Output namespace同时改变当前Source的读取几何；仅foreign Value投影解释不充分，围绕它建立新反事实预测 |
| K/V都有效或交互强 | 不预设单机制；决定哪种功能模型能解释原生namespace效果，而非继续找最大头 |
| 原生far作用弱/数值阳性不足 | 记录该设置的结果/限制，不把负结果自动贬低E48，也不铺更多别名 |

- **算力预算：** 单卡pilot≤1 GPU·时；只有明确功能分离才做同脚本新context确认≤1 GPU·时。
- **实际：** 24 pilot136.78秒＋48确认280.06秒，共.11579 GPU·时；数值max1.72e−5nats。模型退出析构的旧ResourceTracker警告原日志保留，exit0、全部rows/result完成；不是科学运行失败。

## 结果

源码/卡先提交6c14bf89后运行；raw contexts/behavior JSONL仅本地，小preflight/run/analysis入git。

### 24-context发现结果与48-context确认前附记

发现集`results/e91/qwen3_discovery/analysis.json`：A-only的rule幅度shared=.49798[.34987,.65478]、far=.13699[.09091,.18971]，配对下降.36099[.21228,.51885]nats。Value-only为.26635，配对下降.23163[.07099,.40687]；Key-only为.40568，配对下降.09230[−.11135,.28950]，**不能当Key无作用或Value唯一机制**。K、V各自与far的逐context d误差均明显非零；K/V合换复现far是工具阳性。

shared native accuracy56.77%→far67.19%，+10.42[4.17,16.15]点；A-only accuracy57.81%→63.02%，差CI跨零。规则独立性恢复不等同于已确认准确率收益。此次signed A-only平均.00298，仍有异质性；没有因signed平均零宣布没有依赖。

**确认在此附记及forecast文件提交后启动。** 使用原已登记n48/seed191001、同引擎SHA45d2f946473aae0d97f7a3269dbc903e9c111e7d111af4740fe3822f97db8321；不改变任务、模式、标签或主读数。关注原注册的namespace下降是否至少.15nats、V下降是否至少.10，以及K/V单独是否仍偏离far。保留K magnitude下降的不确定性，不把确认当Key零效应的等价检验。数值量级forecast是发现均值的冻结外推，**不是一个已提出的完整计算模型**；全模式与失败预测均报告。

若确认成立，回到主问题：标签词是否只是答案的编码，还是同时影响来源内证据的形成？当前可排除纯粹直接foreign Value退出读出的充分解释；不能排除经A继承的Value/readout、普通上下文化或二者交互。无论确认结果如何不扩词表/层/头矩阵。

### 48-context独立确认

先提交5006c0ed中的附记与forecast，再运行seed191001/n48。结果`results/e91/qwen3_confirmation/{analysis,run,preflight}.json`，引擎SHA与发现完全一致，全部contexts保留；这是同test池的新context确认，**不是新数据集或全新评论语料**。`sanity_audit.json`逐项复算频率/gold/d、确认全行与数值；这是执行者自查，不冒称独立科研校对。

| entire-query只可读A；仅改变A缓存 | mean absolute B-rule effect（nats，95% CI） | 比shared下降（paired CI） |
|---|---|---|
| shared native A缓存 | .68334 [.53160,.84374] | — |
| A的K取far，V仍shared | .45562 [.31998,.61516] | .22772 [.09473,.36098] |
| A的V取far，K仍shared | .43576 [.33439,.54375] | .24758 [.10033,.40605] |
| far A缓存／K,V都取far | .19266 [.15703,.23151] | .49068 [.34106,.64469] |

K-only、V-only均与far不相同：幅度差分别.26296[.13079,.41923]、.24310[.14750,.34587]；逐context d误差分别.44909[.31365,.60641]、.37000[.28246,.46737]。故“只改Value足以解释完整namespace差异”不成立；发现集K下降不确定，确认用原已登记对比得到正效应，没有换主读数。K/V全换等于far是数值对照，不能重复计成新科学证据。

A-only的B-rule翻转引发答案改变率shared22.40%[16.93,28.13]、far7.29%[4.17,10.68]。但是conflict accuracy59.11%→60.42%，差+1.30[−2.86,5.47]点，**不声称独立性改善自动提高accuracy**。native binary accuracy54.43%→63.28%，+8.85[4.95,12.76]点；far native全词表label-valid94.27%、argmax正确60.68%，与强制safe/toxic二选一的准确率区分报告。A-only两种条件有效率≥99.74%。指令accuracy59.11%，rule幅度.84734，未观察到一条指令使本设置独立。

冻结发现均值外推完整保存在`forecast_audit.json`：namespace下降的预测.36099→确认.49068（残差+.12969）；K下降.09230→.22772（+.13542）；V下降.23163→.24758（+.01595）。本轮确认的是功能依赖与方向，没有将这个简单量级外推称为完整分布预测理论。

### 回到研究问题：这次实际改变了什么

**已支持的具体认识：** 分开B的标签，除了改变直接foreign词的读出，也会改变raw不变的A示例中可供读取的状态；作用同时经过A缓存的K与V。共享输出空间下，后置Source选择并不决定规则信息此前按什么边界整合。K-only保留全部cached A Value、query最终标签词不变，排除纯直接foreign Value投影的充分解释。

这是I04解释的实质扩展，保留E48直接DLA测量与E85预测；不把它们贬低。普通上下文化、QK/V功能分解都有文献所有权；本实验的增量是把它们用于检验**输出编码怎样改变不同来源规则的功能边界**，并给出不依赖直接foreign读取的因果证据。完整私有criterion、输入过滤、精确子空间或唯一算法均未识别，不为此追加一串门槛。

本轮范围只到Qwen3-8B、这个受控规则/真实评论池、一对词表。Key作用包括attention归一化与后续query状态，不宣称只改变组内Source选择；all-A缓存不是某个新单模块。native与A-only是不同计算程序，不把二者namespace效应相除、相减当互斥机制份额。跨Source影响未被自动定义为不合理，仍须区分任务间有用共享与私有映射干扰。

下一步优先将已有形成/读取证据组织为一个具体计算解释，检验它对“共享内容特征、不同来源映射”的新情形能预测什么；不再按token/头/更多别名扩展。C16/C20继续L1，未通过独立科研校对，不自动开关研究线。
