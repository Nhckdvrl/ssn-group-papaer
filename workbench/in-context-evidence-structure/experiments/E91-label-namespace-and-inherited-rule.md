# E91：另一来源的标签词怎样改变当前来源的规则读取？（2026-10-10）

- **状态：** PLANNED
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
- **实际：** 待填写。

## 结果

尚未运行；源码/卡先登记。raw contexts/behavior JSONL仅本地，小preflight/run/analysis入git。
