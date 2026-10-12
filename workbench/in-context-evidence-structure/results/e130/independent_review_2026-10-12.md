# E130首评分前独立CPU校对

2026-10-12；C23/C24、I04、P17。依EXECUTION §5，独立读卡/全部源、重构实际token和图，先封自己的计算，再执行作者observer。**四批CPU完整通过，未发现需要修复的真值、干预或数学blocker，可冻结末源并按固定四批执行。** 尚无任何科学评分，本报告不能代替后续raw校对。

科学源SHA `7ef59b3f853e1437dbffd11319ae1c1fe937ffa21723ac2b89bfe971e5a72973`；[完整JSON](independent_review_2026-10-12.json)保存全部context位置、每owner边数、输入/dependency/helper哈希。无GPU、科学源/卡/主张/文稿修改、commit/push或等级/状态决定。

| CPU批次 | contexts | prefix长度 | Cue长度 | targeted移边/ctx | independent移边/ctx | 私人方向False/True |
|---|---:|---:|---:|---:|---:|---:|
| preflight_llama_discovery | 16 | 365–381 | 8 | 128 | 30976–33856 | 8/8 |
| preflight_llama_validation | 32 | 381–425 | 8 | 128 | 33856–42400 | 16/16 |
| preflight_qwen14_discovery | 16 | 365–381 | 8 | 128 | 30976–33856 | 8/8 |
| preflight_qwen14_validation | 32 | 381–425 | 8 | 128 | 33856–42400 | 16/16 |

四批合计96 contexts：实际AST源构造并与独立numpy逐元素核对2016个prefix图、2304个Cue图、13056个body图；1152次逐元素核对E122原始normal/answer_cross_off/all_cross_off图。逐条重算6144个demo真值、178176个recipient/donor query gold槽；这些重复校验不是新增独立样本。最终每context确为21prefix、24Cue、136条件×8query=1088科学评分槽，固定全批计划104448槽，目前0。

实际token定位正确。每Source有8个首答案词receiver，每个sender块含答案词与紧随分隔符共2token；targeted双向只移除另一Source答案块严格过去→标签词边，总数128，self不动，与E122 exact定义一致。Independent移除全部private跨源严格过去边，native不移边；各图边数/attention mass未匹配，不能解释为同强度纯信息操作。每context完整receiver/sender位置与A/B计数见JSON，不只核总数。

四world B输入在同多重集内双射重排，标签stream/owner/长度/答案位置保持，A全文和gold不变；Food/Service/private truth均从实际文本词汇独立解析。8query覆盖四Food/Service格各2例、discord4例，bias/Food/Service/product为正交基。16→32词池全文无重叠；探索Alex/Sam、确认Robin/Jordan均有两owner排列与两private极性，shared no/yes只有2唯一词ID，不能由表面输出识别Source。

HEAD在全部私有材料前，独立形成不存在后续公共token relay。Cue完整8token `Annotator: name
Comment:`，无query正文或答案，允许读两Source，由name影响功能；无oracle先选Source。own body的全部query token/all层预定mask阻断直接A历史，却保留HEAD、B历史及整个Cue，所以它仍可经Cue获取A信息。原生/targeted早晚参照是同形成图的字段顺序；F0 early/late另改变Cue介导/直接读图。instruction使用native形成，是纯prompt控制。

另执行科学源实际patch的AST片段，在全部真实96context、4608个policy/recipient/world/Actor组合中做全层CPU mock：331776次K/V块赋值均只替换plen以后Cue，原F0 recipient全部prefix逐元素保留，cp与receiver/donor都不别名，seq相同。模拟缓存仅检验操作，不是模型forward/科学成绩。

完整synthetic observer核136条件×8context/8704 logit槽，先独立四格均值投影、显式2×2 det与10000 context bootstrap910，再执行末源analyze；20297个数字比较最大误差4.26e-14，投影误差1.78e-15。native/own两co-primary确为每recipient/context先det后平均，禁止换成平均矩阵det；12配对形成矩阵统计、96双gold配对performance、72固定code criterion-only/完整四基/两private方向、所有136接口full/candidate/margin/discordant与负/零均核。normalized每行norm>.001才保留，恰等.001置0，小norm乘积不误删，两recipient与policy的配对差先逐context再bootstrap。

CPU文件生成起点为796828…；随后在0分数期补上卡中预定paired performance/criterion-only observer与显式不别名assert，末源7ef59…。四份cpu_completion同时保存起点/末源与实际contexts/preflight SHA。这里已用末源AST重构全部真实token/图，完全一致，observer合成校验也使用末源，没有把旧源observer当成末源。

后续需核原始科学run的真实每层4D mask消费、FP32 split/full floor、self argmax、图零和全部136接口，再从raw独立复算后看作者analysis；本次没有GPU重跑，尚未把这些运行检查宣称通过。det单位nats²，.001 logit地板不是det阈值。形成→同名条件Cue的功能连接是有知识增量的检验，结果可以只部分响应或阴性；全层块还可改变检索/prototype/校准，不能仅凭det或政策差异宣布完整规则、bindingID、独立hidden模块、普遍task-vector首次发现。旧主张资格与研究状态保持。

本次阅读范围：E130完整卡/科学源；实际四CPU contexts/preflight/material词表与生成、真值、bootstrap依赖；E129冻结父源与既有E122 targeted定义；末源合成observer及字面AST patch。未独立加载模型或执行GPU。流程check为0 errors、31历史warnings。
