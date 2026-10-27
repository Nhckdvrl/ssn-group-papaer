# E158：事实输入区别由哪些专家路径传递（2026-10-27）

- **状态：** v2缓存工程预检失败、未读内容干预；v3完整前缀数值检查通过但单层矩阵超预算；v4完整路径方案准备中，仍无内容交换/移除结果。旧源码cc078995、plan和失败raw保持不变。
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

## v2实际工程结果与v3前瞻修复（内容干预前）

三模型canonical参数/buffer/旧cal通过；全部288条native查询的快速缓存/原生缓存整分布和逐MLP输出逐位一致。实际uncached→cached最大KL=.0599446054，P/A/B各有1/0/1条argmax变化（96条/model），最大KL超过事先.005阈值，因此原程序在大干预矩阵前停止。失败成本3213.197228 GPU秒=.892554785 GPU·时，纳入原4小时总cap；完整baseline、BF16分量及日志留在原raw，SHA见failed_cached_preflight.json。未运行任何内容交换/匹配移除，不做职责阴性推断；失败路径未到最后source hash，不能称其完成全部事后只读检查。

v3不放宽阈值，不换输入/来源/读数/层：用原生use_cache=False的全前缀计算，保留各expert完整token批形状，只跳空专家。每query整层所有位置MLP输出与全词表末token分布须逐位恢复原生。末token读出用原生logits_to_keep=1，使不同长度的source/target读出同为一行；另实际测量原生keep=0→keep=1 KL/argmax，仍以原.005/5%门槛核对。旧schema的cache_*和uncached_*字段仅兼容数值统计，明确标注为此readout对照，绝不宣称缓存数值问题已通过；v2失败永久保留。

只替换指定层末位置；每个decoder之后将更早位置恢复到该query的原生状态。这是数学上冗余的因果前缀保持，避免末位置改变后续专家批大小引起BF16舍入反向污染更早位置；它是本轮干预定义，不称无clamp的自由整段干预。R/S/联合及三类移除/正控的科学含义不变。完整CPU原生实现×dtype检查含自然/干预下fast对照、不同长度source residual身份、全部更早位置保持和forward恢复。

单卡复用原三权重，预算仍4 GPU·时累计包含v2失败。先用固定最长canonical输入（并列取最小query索引）做32次同源身份计时；1.5倍27648行估算必须小于剩余预算减300秒，再跑完整矩阵。计时不读改变输入的结果。v3文件/plan单列results/e158/full_forward与raw/full_forward，不覆盖原协议；数值程序重新冻结后启动。

## v3实际结果与v4完整路径修订（未读内容干预）

v3三源全部参数/buffer/旧cal、288条原生查询的full-native/fast整分布及逐MLP检查、288个固定同query单层身份全部通过；最大实际full-head→last-only-head KL及argmax差见full_forward/failed_full_preflight.json，原缓存失败不抹去。最长canonical输入的32次同源身份计时.751789秒/forward，原27648行的1.5倍估计31178秒，超过剩余7867秒，因此按预定计时门槛退出，没有内容交换或匹配移除。v3费用3319.568724秒，加v2累计6532.765952秒，仍保留原14400秒总cap。失败路径未到事后source hash，明确不声称已完成该项。

**修订的科学理由：** 原逐层方案测单层局部敏感性，弱效应不能区分跨层累积与整条路径没有携带内容。ROME全文的跨层恢复也提示这是实际竞争解释。v4直接问完整末位置R流、S流、联合流传递哪种输入区别，放弃未实际取得的层定位和层均值，保留全部24国家/两关系/三场景/三模型、原来源映射/标签对照和读数。这项选择发生在任何内容干预读数前，依据科学单位与实测成本，不按显著层/种子/国家优化。

**干预：** 每个decoder层末位置都交换指定分量；换R时保留该步当前H下计算的S，换S时保留当前R，联合时替换两者。未被替换的路径与后续attention/route内生变化，不把多层中的另一分量固定成旧target向量。每层更早位置仍恢复到target的原生decoder状态，保持v3的因果前缀定义。三类匹配移除也在全部16层同一末位置同时执行。它测完整路径中介和支撑，不能称单层责任或知识存储比例。

**原生资产复用：** v3已保存的真实BF16 R/S/末位置H/final residual和baseline另列SHA作为输入；新加载模型仍须canonical参数/buffer/cal一致。每条query只重放原生，逐层末位置H、全部选中token LP、top10和final residual须精确恢复旧记录；不重做无必要的全词表基线/分量采集。全部96query同时做source=target的完整RS身份；两个固定canonical query额外测R/S身份。源组件和非替换路径含义不同，代码/CPU oracle必须区分。

主路径仍为R/S/RS；在本次运行前另加入完整末位置attention流A作为机制比较，三类source和同位置zero-A都报告。ROME先验提示最终输入位置attention值得比较，不能仅靠构造的final-residual身份判断MLP窗口是否有内容动态范围；不把A保证为阳性。A原生输出在新native重放时直接采集，无需额外源前向。主数据为1728次内容交换（3model×3scenario×4path×2relation×24country）+576次匹配移除，共2304新读数。另432最终residual正控；全部288query完整RS/A身份及12固定R/S身份为工程控制。源/对照排名、LP、真实gold top1/top10及整词表KL定义不变；删除层轴/层平均，只报完整路径、A−P/B−P、S−R在entity/attribute的差及其历史差。country配对bootstrap1000、seed158001，all主与共同native target+实际source成功次分析不变。

继续原baseline共同top10门槛8/24、原readout地板.005/5%；新旧失败与费用保持不变。用固定最长canonical输入做同query完整路径身份计时，1.5倍(2304新读数+432正控)须装入剩余总预算减300秒才继续；不增资源cap、不新训练。新源码/plan/raw在whole_path单列，冻结后运行；v3完整层扫描未测。
