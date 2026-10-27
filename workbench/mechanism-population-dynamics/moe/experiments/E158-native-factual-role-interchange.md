# E158：事实输入区别由哪些专家路径传递（2026-10-27）

- **状态：** READY；v2代码、统计、三原生实现×两dtype的CPU检查、静态预检和不可覆盖plan完成，未运行成熟模型条件。
- **类型 / 对应：** PILOT；C14；成熟公开父P与两退火终点A/B，无新训练。
- **问题：** 在能检出同一事实的模型中，实体变化与所问属性变化分别经R、S还是联合路径影响答案？训练历史是否改变这份实际分工？

## 科学区分

E155测必要性，E156测来源配套和性质载体，E157测子集回插。本卡把焦点推进到所传递的输入区别，而非追加预算解释。若历史改变不同输入区别的路径中介，支持具体职责组织可变；若只有一般损伤变化、没有源答案特异性，则更支持一般依赖变化。比较同架构成熟谱系，语义角色不靠专家编号或激活类别命名。

## 数据、条件与范围

- 官方LRE固定commit 1b9ec3cf2b8368e42bde7e80fcef384312a6ec07，两关系country_capital_city/country_language，共24个相同国家；保留全部样本，不按模型挑题。原JSON/SHA保留，两个capital字面Unicode转义在新输入中确定性解码并写纠错ledger，不改旧数据。
- canonical模板取capital普通模板1、language普通模板1；paraphrase取capital普通模板0、language普通模板2。四模板均来自官方，末词均is，避免把最后token身份变化当属性区别。零shot、无chat模板；不是论文全表复现。
- 两关系×两措辞×24国家=96条native查询；主target是canonical措辞48条。只评价数据给定的canonical答案首token，记录多token/别名限制，不称完整事实生成准确率。
- 对每个主target，三类固定source：entity为同关系、国家索引循环移11；attribute为同国家另一关系；paraphrase为同国家同关系另一措辞。前两类的期望首答案不同；全源映射在模型读数前锁定。
- 每场景/关系以固定seed158003的二分匹配选对照国家标签，保留原标签频数，对照token与target/source均不同；仅用原数据标签，不用模型输出。
- 在每个P/A/B内部交换last-input-token的R合成输出、S输出或联合R+S，逐一覆盖全部16层；其余token和层先保持原执行，后续H/route可自然变化。没有跨模型隐空间直接对齐。
- 在相同canonical target、相同层和位置另分别移除R、S或两者，记录原答案NLL增加、top1损伤和KL；这是与内容中介匹配的预测支撑读数，不把E155不同任务/全网scope直接当对应值。
- 缓存prompt最后token之前的KV，复制缓存后执行最后token；组件从同一cached native执行获得。单token等价实现只跳过空专家调用，按原expert索引顺序累加，在最后S相加前直接记录R及加权S，逐层检查R+S精确恢复输出；不是向量差近似。每query与未改的native cached执行逐位核对，再用于干预。CPU及固定真实查询的S-zero原生块调用另核R tap，所有临时forward恢复。

## 读数与统计

主读数是源答案相对对照答案的排名变化：在source关系的固定答案token集合中、除source/control/target以外的共同distractors，计算source与control各自胜过distractors的比例；干预相对native的两项变化之差。统一logits温度变化不改变此排名量。另报源−对照log概率差的变化、源/target log概率、全词表top1/top10转为源答案的比例及native→patched KL。paraphrase完整报告，不因不利而删除。

全部层/路径/场景/关系/模型曲线保留；不在结果后挑层。预定概括为16个单层干预效应的等权均值，不称计算责任比例。主历史对比B−P与A−P；另比较S−R对entity/attribute的差及其历史变化。联合路径另列，不以非线性交互命名语义AND。

匹配移除同样全报逐层、16层均值、历史差与S−R差；NLL支撑和内容排名是不同量纲，不相减成综合分。移除的次分析只按三native target均top1正确选取，与内容中介所需source+target共同正确集合分开。

以24个target国家为簇、成对重采样1000次、seed158001，保留关系/场景/层/模型配对；source映射固定，CI只是该固定探针下的输入不确定性，非独立seed/国家总体证明。主分析全部；次分析定义为三模型canonical target和相应source均在native top1正确，定义事先锁定、不使用patch结果，计数全报。

## 阳性对照与噪声地板 + MIE

- 三成熟模型canonical参数/buffer及旧BF16 cal逐位匹配，前后只读hash；所有临时forward/hook/cache均恢复。
- CPU tiny三原生实现/FP32与BF16测试cache复制、R+S重构、三类同源身份和最终residual替换。
- 真实96查询都记录uncached与cached首token分布KL、答案log概率与argmax差；主测量始终同cached程序，不线性扣除数值地板。若cache差异实质改变比较，先修工程，不读patch科学结果。
- 工程预警在新数据前固定为任一模型最大uncached→cached KL>.005或argmax差异超过5%查询；触发时保存完整baseline、修执行接口，不把它当职责阴性。此预警不替代逐query的native-cached/空专家跳过精确身份。
- 两个固定canonical查询(country0、两关系)逐层R/S/RS同query替换应精确恢复cached native首token分布。
- 对全部source-target场景，最后decoder层完整residual替换应精确恢复source native分布，证明工具可传递源预测；不把这个构造身份当新发现。
- 所有native基线先取得。若任一关系三模型共同top10命中少于8/24，只封存baseline和控制，不跑大patch矩阵、不宣称知识缺失或关闭方向。
- 排名变化.05与source-control log赔率.1 nat作解释尺度，完整CI/噪声同行；不以heuristic自动判方向生死。

## 混杂审计与决策表（跑之前写）

固定单父谱系，公开训练链声明与原始batch链分开；不是独立初始化。counterfactual中介不等于知识存储位置；首token不是完整答案。只介入最终输入位置而非全部序列位置，结论限所测路径。缓存KV不受该位置后续干预影响，每次复制、检查原缓存不变。不同措辞与token长度可能改变输入状态，paraphrase控制与同末token设计同时保留。

缓存核对范围：CPU tiny会对原cache做字节hash；成熟每步核长度并使用deepcopy，不将其称作成熟逐次cache字节hash。真实空专家跳过/原生cached的逐query逐MLP输出与整词表分布须位相等。

| 观察 | 对母问题的推进 |
|---|---|
| 同一可检出事实的源答案特异性在历史间转移R/S路径 | 识别具体输入区别的职责可塑性，连接配套和重用结果 |
| 必要性变化大、源内容中介未相应变化 | 重要性与所携带区别进一步分开，不用零化给专家贴语义标签 |
| 只有联合路径有效 | 支持所测区别依赖共同计算，保留各单体和全部层对照 |
| sham同样扰动或完整residual控制不通过 | 不宣称内容职责；判断非特异干扰或修工程 |
| native共同基线弱 | 封存可行性结果，不扩扫描追阳性 |

## 算力与当前结果

拟单卡共驻三BF16模型及小型KV/组件cache，预计<96GB；修订后预算4 GPU·时，含读取/cal/hash/全部失败。与E157并发时总探索卡数至多2，仍≤8；先完成代码/CPU预检/plan冻结才读成熟模型条件。复用mechpop、原HF权重与小型官方数据，无安装/新训练。raw ~/mechpop_cache/e158_factual_role_interchange/。

**任何成熟读数前的修订v2：** 原v1代码/plan在3ce1179b保存，旧plan另存plan_v1_before_matched_removal.json。原方案把旧任务/全网必要性与新局部内容中介并列，不能排除干预单位差异；本次补同层同位置分量移除，可直接检验预测支撑与内容传递的关系。额外6912缓存前向，总新行数27648，无新模型/数据选择或训练；资源上限3→4 GPU·时，避免冷I/O和新增条件挤掉完整测量。此时仍无E158成熟模型结果。

当前只是前瞻设计与API/数据实现，未取得E158成熟模型数据，C14等级不变。
