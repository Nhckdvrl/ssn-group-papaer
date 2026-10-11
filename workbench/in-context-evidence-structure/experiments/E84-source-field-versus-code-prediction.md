# E84：冻结读取预测跟随Source字段，还是它的码词代理？（2026-10-10）

- **状态：** DONE；32新context pilot与64新context确认完成。
- **类型：** PILOT；不训练新参数，不增加模型或能力门槛。
- **对应：** I04 / C20 / P20；E83预测模型的可识别性检验。
- **为什么现在：** E83冻结R在64新context产生+.376nats Source contrast，B无益；R/RJ与oracle的平均作用接近，但逐context相关仅约.25。更关键的是natural query中Source-match=code-match。成功不识别抽象来源字段还是词码代理。需要让两预测分歧，而非继续换自然query画同一张图。
- **问题（一句话）：** 用E83原样冻结R，按Source字段或按query code定义匹配，哪一个能预测新反事实中Tag→prefix的Label读取变化及其输出作用？
- **设置：** 相同Qwen3-8B固定revision、float32/eager/conda，32新context seed84001。demo Source↔code关系保持一一对应，码置换/方向/顺序全部随机保留；4自然query加4仅将code翻号的冲突query，Source/input不变。两个布局；各query token数/多重集布局检查，未以donor正确性筛选。
  - R_field使用真实Source字段的S；R_code把S定义为query code匹配demo code（等价由context码置换解析出的Source），K/位置/全部旧系数相同；B保持旧预算/位置。自然4query两R预测应逐位相同；冲突4query预测分歧。
  - 全部系数使用E83冻结文件sha db40ec4e2a50c2b8e23f6a0d08b0da05941bf1d50ec06691f276c5b2b9fd006d，不看新数据重新拟合。接口同E83末位Label log权重修正、G own Tag完整概率保持；其它query receivers重放native，demo缓存/V保留，末位状态活反馈。
  - native Tag/prefix、R_field/R_code/B、oracle Label delta重放、self，两布局一句Source指令；oracle只作阳性，预测器不读取donor输出。
- **读数：** 主要是conflict上的两R条件mass加权allocation MSE差、两R与oracle输出作用的margin效应RMSE，以及Source字段/码词分解。自然query保存strict accuracy/margin；**冲突query不当能力失败**，因两种冗余身份不一致，不宣称唯一合理任务语义。
  - 对每Input，四格z(source A/B,code A/B)分解：field=(zAA+zAB−zBA−zBB)/4；code=(zAA+zBA−zAB−zBB)/4；以同Input Source-A原规则的标签方向规范符号。自然Source contrast=field+code，统计恒等不等于两个独立模块。
  - 交互/共同输出项照实保存；所有差按context bootstrap4000 seed840。预测误差分natural/conflict，不拿总体平均掩盖冲突。
- **阳性对照：** natural R_field/R_code预测与行为逐位一致；code字段解析与码置换严格一致；所有自然/冲突/布局保持长度与因果mask；self/full-forward≤.01nats，carrier概率误差≤2e−5、行和≤2e−5、mask≤1e−7；已知四格输出分解CPU重建。全部context/错误donor保留。
- **噪声地板 + MIE：** 上述数值控制；两R预测误差差CI不跨0且输出field/code作用有可解释差异才值得一次新context确认；不规定accuracy恢复门槛。主报告绝对差，不追最佳层/head或极端样例。
- **混杂审计：** 新冲突改变两身份的一致性，可能触发策略切换，不能当同一任务能力测试。R_code也不是证明exact lexical copying：碼是context关系代理，可能有非字面编码；R_field也不是binding ID因果子空间证明。两R来自相同自然数据，系数没有唯一算法身份；scope限布局引起的末位Label读取变化，非全部来源计算。
- **决策表（跑之前写）：**
  - R_code优于R_field并跟随native code分量：E83的Source匹配增益实为code关系/位置敏感的可预测读取变化；Source字段原生路径与码路径应分别描述。
  - R_field优于R_code：更支持来源字段定义的规则条件进入Label读取变化；不依赖同词码匹配才能解释。
  - 两者都弱或分别预测不同读数：单一selector解释不够，考虑多线索的有限混合，但不立即训练调分；保留当前反事实限制。
  - 只改善MSE而行为效应不吻合：不把拟合好当机制已完成；报告已失败的预测，不加feature。
  - 控制失败则VOID，同seed修复；oracle无清楚作用则限接口，不把它升为整项目关卡。
- **定位：** Mixing Mechanisms §3.1–3.4已有位置/词汇/指针的分歧反事实；本实验不是首次发现lexical retrieval。具体目标是Source字段与其码代理在多规则ICL中如何共同约束读取，而非将共线的预测误认为独立Source路由。
- **算力预算：** 单卡≤.2GPU·时；关键结果前不铺后续分支。**实际：** 待填。
- **产物：** E84脚本与小analysis/run/preflight；raw JSONL/native特征留本地。先写此卡再运行，命令/hash在CPU preflight后记录。

## 结果（不改上方读数）

CPU/token/feature检查通过，科学源码SHA256 `d5932b6af16274b6a7d0a21f91c965d77c295d4b61d2854c1e5fdcac1fee32a1`；所有自然query的两个R预测逐位相同、冲突query分歧。冻结系数hash与E83相同。基于Cho的forerunner读取与Mixing Mechanisms词汇路径，运行前预计R_code更能预测冲突中的布局读取变化；若R_field更好或两者均差，按决策表修正。

命令：`CUDA_VISIBLE_DEVICES=0 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/e84_source_code_prediction.py --model /tmp/ices_models/Qwen3-8B --reader results/e83/frozen_reader --out results/e84/qwen3_discovery --n 32 --seed 84001`。

### 32-context pilot：读取变化更跟随code代理，但完整行为预测仍不足

seed84001全部32contexts/9条件/8query保留，63.543s=.01765GPU·时。self0、natural R_field/R_code行为差0、full/cache≤2.68e−5nats，G概率误差0、行和≤5.97e−7、mask0。结果`results/e84/qwen3_discovery/{analysis,run,preflight}.json`。

native输出field/code两分量Tag .3736/.2327、Prefix .5696/.5163，两类身份都被使用；不支持“prefix只看码、不看Source字段”。自然Source contrast分别.6063/1.0860。oracle Label重放分量.4937/.4298；R_field .6917/.3026，R_code .5137/.4805。自然query两R作用完全相同，冲突才能区分。

冲突上的code−field条件mass加权allocation MSE差−1.5897[−1.6474,−1.5266]；读数支持R_code。对实际Label重放的冲突输出效应预测，MSE差−.1468[−.2739,−.0305]，code也优于field。但**两者都没有很好重建逐query作用：RMSE field .719、code .609，B更低.490**，相关field−.152/code .114/B .239。不能把“胜过竞争Source解释”写成“已得到完整预测模型”。这触发原决策表的有界支持与行为不足两项，不加feature追gold。

**实际更新：** E83的S项在此布局变化中主要跟踪code关系代理，不能把它直接归因到独立Source字段寻址；native Source字段效应仍在。输出分解是统计四格，不识别两个独立模块；TF prefix的冲突也可能改变输出条件语义，不当能力失败。

### 确认前固定预测

同源码/冻结系数/全部条件，64全新contexts seed184001。预计conflict R_code的加权allocation MSE低于R_field；效应预测MSE也较低（CI若跨0，按未确认报告）；native Tag与Prefix的field、code两分量都为正，不是code取代Source字段。同时预期两R的逐query效应仍不充分，不把确认变成拟合最好模型的搜索。自然两R完全一致的质量控制必须继续成立。

命令同pilot，改out=`results/e84/qwen3_confirmation`、n64、seed184001。Source-code冲突问题在E83读取输出前已有卡内限制说明；E84预定具体读数/竞争预测，不声称完全预见E83。

### 64-context确认：代理变量定位复现，完整效应预测失败也复现

seed184001全部保留，112.108s；pilot+confirm175.651s=.04879GPU·时。科学源码/依赖/冻结系数hash一致；self与natural预测器差0，full/cache≤1.72e−5nats，row≤5.97e−7，G/forbidden mass0。结果`results/e84/qwen3_confirmation/{analysis,run,preflight}.json`。

冲突code−field加权allocation MSE差−1.5386[−1.5714,−1.5041]，效应MSE差−.1651[−.2750,−.0711]，两个竞争预测方向确认。native Tag field/code .3601[.3113,.4093]/.2582[.2143,.3029]；Prefix .5944[.5169,.6716]/.5825[.5232,.6456]，两分量正值确认。oracle Label重放field/code .5090/.4888，R_code .4998/.5107，R_field .6819/.3286；code模型的平均分量更接近oracle，不宣称统计等效。

逐query效应仍差：conflict RMSE field .741、code .620、B .527；相关field−.179/code .116/B .060。**R_code赢过另一Source解释，却未赢过简单预算模型的逐query效应误差。** 不加新feature追gold，不叫完整机制模型。下一项E85回原生NameK×LabelKV路径，检验名字影响与码影响的依赖；目标是具体因果计算关系，非再绘一次代理相关图。

工程记录：在科学运行仍活跃时曾提前启动analyzer，因run.json尚未产生而失败；等运行exit0后原样重跑成功，没有读取/改动部分科学结果，没有改变评分/样本/代码。保留此备注，科学运行不作废。
