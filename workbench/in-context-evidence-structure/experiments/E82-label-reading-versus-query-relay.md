# E82：位置收益经由示例标签读取，还是query内的信息传递？（2026-10-10）

- **状态：** PLANNED；先32新context pilot，结果决定是否独立确认，不铺模型/任务矩阵。
- **类型：** PILOT。
- **对应：** I04 / C16 / C20 / P13 / P20。
- **为什么现在：** E81在固定实际来源码carrier分布时，whole-query全attention移植仍比carrier-only提高13.3[9.4,17.2]点。这个差已证明其它读取重要，不再重做组外效应。现在需要判断一个具体计算解释：prefix是否主要改变了示例Label读取，还是还依赖query位置间传递条件状态。Cho的提前计算/shortcut、Wang2026的示例驱动重权重已有所有权，不能把“不是只在末位计算”或QK/V区别重新命名为新机制。
- **问题：** 固定prefix来源码读取后，示例Label的读取与query内部读取分别替换为prefix分布，哪一项/哪种合作能转移位置收益？仅在最后receiver移植Label是否足够？
- **设置：** Qwen3-8B固定revision b968826d9c46dd6066d109eabc6255188de91218，float32/eager，conda verl-clean，GPU0。E81相同可识别分类材料，32全新contexts seed82001；4自然query；所有错误donor保留。Tag/prefix token多重集、长度、物理sites相同。原生两布局及一句Source指令作为行为对照。
  - 先收集native Tag/prefix所有36层/head/有效query receiver的attention和稳定log概率。recipient固定为Tag；V/demo cache保持Tag，query V/残差/MLP随干预运行。
  - G为16个实际来源码载体（Tag的Tag位，prefix的prefix位）；其它producer分成L=16个demo Label、Q=当前query的全部因果可达token（含自身）、O=其它历史/模板token。按demo角色交换donor Tag/prefix列；**不交换query列/receiver**，不改变因果mask。
  - 固定G为prefix donor的完整概率。对非G分布，计算原生Tag与角色对齐prefix的条件log概率r=log softmax(logits excluding G)。2×2重放：L列取own/donor、Q列取own/donor，O列始终取own；混合后在非G上重新softmax，乘(1−donor mG)。不独立钳制L/Q的概率质量，避免质量之和不可行。这个干预同时改变被换组的组内权重和相对预算；重新归一化会改变其它组质量，因此**不是纯路径中介份额**。
  - `frozen_base`=(own L,own Q,own O)；`label`、`query`、`label_query`为2×2另三格。`full`所有非G都取donor，重建E81完整重放阳性。`label_final`只在末位receiver替换L，其余receiver保持frozen_base。`carrier_live`保留当前recipient活的非G条件分布，核对固定native与活反馈的差别，不混用两个baseline。
  - `self`全部own重放，应重建native。full attention self、前4contexts整段前向核对缓存。只做这些预定结构分组，不按观察到的成功挑层/头。
- **读数：** 每条件correct logit margin、strict二候选accuracy、output Source-ranking（非内部选择），s与|b|输出几何；context bootstrap4000 seed820。主对比：full−frozen_base、label−base、query−base、label_query−base、full−label_query、label−label_final；2×2交互及对称Shapley。辅助保存carrier/label/query的质量、Label按requested Source与input kind分配，分all-query/final。全头均值只描述，不替代因果效果。
- **阳性对照：** CPU混合log概率归一化、组完全分区、全donor重建、相同布局self、G完整目标概率不变；行和≤2e−5、mask mass≤1e−7、self/full-forward≤.01nats。稳定logsoftmax，禁止对下溢概率直接取log。valid receiver以外保持原生，padding/future列始终mask。全部context、错误donor和失败运行保留。
- **噪声地板 + MIE：** 数值对照如上；pilot margin差≥.15nats或accuracy≥.05且CI不跨0可作为确认线索，不是整项目准入条件。不用不稳恢复比例挑优；主报告绝对差与CI。
- **混杂审计：** 已控制token/数量/位置、context筛选及因果可达性；未控制query列的结构角色变化（物理对齐，不能向未来移植），donor可能含答案相关选择，固定attention仍让recipient query V演化。跨组归一化及全层重放不等于原生电路的纯边中介。因此本实验是结构化反事实重放，不输出独立模块/中介百分比/抽象算法已迁移。
- **决策表（跑之前写）：**
  - label近似转移full收益、query增益弱：后续优先建立来源条件化的Label读取解释；不能据此声称所有历史Value都无关。
  - query有收益，或label_query明显非加性：信息在query内传播参与此接口收益；下一步问它传的是来源条件、映射/答案还是模板状态，不把query机制泛称首次发现。
  - label胜过label_final：当前收益依赖早于末位的Label读取；把C16与新的来源选择读数联系起来，而非另立能力关卡。
  - full明显而label_query弱：SourceName/input/Mark等其它producer重要；本两组解释不足，回样例/已存native读数找具体问题，不立即追加十种分区。
  - frozen_base与carrier_live差大：重放固定组外权重改变了反馈程序；限制分组因果解释并报告这个结果，不把两baseline效应相加成机制贡献。
  - 所有差小/CI不确定：承认此分组未推进解释，不继续用更多配置追“修复”。控制失败则VOID，同seed修复重跑，不换材料。
- **定位：** [Cho2025 §5.2](https://arxiv.org/html/2410.04468v3)已有parallel/shortcut/direct-decoding路径；[Wang2026 §6–7](https://arxiv.org/html/2605.16591v2)已分读取预算与示例偏好，并有示例驱动的task-identity重权重。潜在增量限于多规则query需要条件选择时，哪类读取变化能转移Source contrast，以及末位Label视角何时不足；不是新attention数学。
- **算力预算：** 单卡pilot≤.2GPU·时；若出现上述可区分效果，再固定预测做64新contexts确认≤.3GPU·时。当前无其它分支并行。**实际：** 待填。
- **产物：** `scripts/e82_label_query_replay.py`、`scripts/analyze_e82.py`；小run/preflight/analysis入git，raw JSONL与native局部attention数组留本地。命令与实际算力跑后填。

## 结果（跑后填写，不改上方读数）

运行前CPU与token检查通过，重建误差5.96e−8；科学源码SHA256 `671b3bca5a931a1ee34012007f2e3f42058148140bf06e28329c8ea37be32a5d`。命令：`CUDA_VISIBLE_DEVICES=0 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/e82_label_query_replay.py --model /tmp/ices_models/Qwen3-8B --out results/e82/qwen3_discovery --n 32 --seed 82001`。

### 32-context pilot：Label读取贡献较大，额外query重放贡献小

全部32context/13条件/4query保留，83.648s=.02324GPU·时。self≤7.63e−6nats、整段/cache≤2.87e−5、全donor重建≤4.77e−7，carrier概率误差0、forbidden mass0；结果`results/e82/qwen3_discovery/{analysis,run,preflight}.json`。

| 条件 | accuracy | correct margin |
|---|---|---|
| Tag native | .5234 | .6317 |
| Prefix native | .6484 | 1.2437 |
| 固定G、活组外carrier_live | .5469 | .4927 |
| 固定G、原生Tag组外frozen_base | .5391 | .7622 |
| +全query Label读取 | .6172 | 1.2861 |
| +query内部读取 | .5469 | .7861 |
| +Label与query读取 | .6484 | 1.3518 |
| +末位Label读取 | .6094 | 1.2693 |
| 完整读取重放 | .7031 | 1.5071 |

Label−base margin+.5238[.3894,.6660]、accuracy+7.8[3.9,12.5]点；query−base margin+.0239[−.0062,.0521]、accuracy+.8[−1.6,3.1]点。Label−末位Label margin只有+.0168[.0082,.0266]、accuracy+.8[0,2.3]点，不支持把位置收益主要归到早期Label读取。Label×query margin交互+.0419[.0256,.0574]，虽可检出但幅度小，accuracy交互CI跨0；不包装成强合作模块。

full−Label/query仍margin+.1553[.1023,.2058]、accuracy+5.5[1.6,10.2]点，不能说两组解释全部收益。固定组外与活反馈差margin+.2696[.1320,.4030]、output排序+25.0[15.6,34.4]点；基线选择确实改变读取程序，禁止把它当纯边中介百分比。

**实际认识更新：** C16的原生Source-effect分布于整个query仍成立；E82问的是另一个反事实——怎样移植布局收益。当前两者不需要同一组位置承担：末位Label读取重放可转移大部分指定Label组收益，不代表原生Source程序只在末位发生。一般定位/改动位置区别已有Hase等文献；ICES应据此建立具体读取解释，而非增加一条通用新原则。

### 独立确认前写下的预测

同科学源码/条件/词库/名字/labels，64新contexts seed182001，未读取其数据：Label−base margin为正且>.3nats；query−base平均margin<.15nats；Label−末位Label平均差<.1nats。报告这些差的CI，不把点估计低于阈值等同统计等效零。full仍超过Label/query；固定组外的Source排序仍高于活组外。若不能复现，收窄该解释，不换seed/分区。确认只覆盖新context，不是新模型或词表迁移。

命令与pilot相同，改out为`results/e82/qwen3_confirmation`、n64、seed182001。
