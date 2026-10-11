# E129 首评分前独立源码/CPU封存

结论：四批CPU实际token/源码mask全部通过，可冻结当前科学源并按既定两checkpoint16→32执行。科学SHA `a177434cf425889df1fcc8b3607e6d5057a26080ad467e7999d002e6504b00bd`；首评分前尚0科学分数。本校对不执行GPU、不修改科学卡/源码/claims，不决定状态或级别。

共96contexts、1632实际prefix streams与同数形成mask、768Cue mask、6144query mask集合（每集合8query）、1536整层K/V合成Cue交换；独立核6144demo真值与73728recipient/donor query gold槽。全部四world、两个owner排列、私人正反及新别名实际覆盖。

| CPU批 | n | 实际prefix | Cue | query集合 | Cue K/V交换 | prefix长范围 | Cue长 | 私人方向 | owner排列 |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| llama_confirmation_preflight | 32 | 544 | 256 | 2048 | 512 | 385–425 | [8] | {'False': 16, 'True': 16} | {"('Robin', 'Jordan')": 16, "('Jordan', 'Robin')": 16} |
| llama_discovery_preflight | 16 | 272 | 128 | 1024 | 256 | 365–381 | [8] | {'False': 8, 'True': 8} | {"('Alex', 'Sam')": 7, "('Sam', 'Alex')": 9} |
| qwen14_confirmation_preflight | 32 | 544 | 256 | 2048 | 512 | 385–425 | [8] | {'False': 16, 'True': 16} | {"('Robin', 'Jordan')": 16, "('Jordan', 'Robin')": 16} |
| qwen14_discovery_preflight | 16 | 272 | 128 | 1024 | 256 | 365–381 | [8] | {'False': 8, 'True': 8} | {"('Alex', 'Sam')": 7, "('Sam', 'Alex')": 9} |

实际源码枚举32 Cue交换＋28 B参照＋4 A参照＝64条件；4 private隔离＋4 native＋4纯instruction＋4 singleB＋1 singleA＝17prefix；四world×两Cue身份＝8准备块。正文/卡的计数一致，不增加条件。

独立从材料lexicon解析Food/Service，核完整2×2、8A8B与两Source各8条私人监督、B评论双射/输入多重集/labelstream、所有world的code真值；所有A token、Source名字、答案位置及private global位置固定。两私有方向均衡，discovery/confirmation材料文本无交集。no/yes恰2个unique词ID，不能由表面词归Source。HEAD位于全部私人监督之前，没有晚公共relay。

直接AST提取末版prefix/field/body/early/late及mask构造，只有device从cuda换CPU；未调用模型。其每个prefix/Cue/query的tensor mask逐项与独立numpy因果图比对。private跨Source strict-past全层不通、self/同Source保留；Cue所有token可读两Source，未用oracle选B；body own每个token禁直接A但可读Cue与HEAD。query left padding的keys不可被有效token读取，global position保留。Cue可能携带A-origin信息，故own不等于来源信息纯隔离。

科学patch只替每层keys/values的plen:整Cue块，recipient所有prefix由逐元素assert保护；CPU以每层/每K,V/每world/每Actor不同标签存储核1536组合。源码的真实prefix/Cue/query hook检查模型收到的4D mask，query deepcopy检查ptr/seq，self swap还检查argmax与logit，full-token CueAll/bodyOwn、native默认causal与single图no-op均已静态核。**这些GPU数值与实际消费尚未执行，本文件不声称其通过。**

独立synthetic observer检验：8合成context×64条件×8query=4096合成logit槽，完全不是模型科学评分。cell-mean投影、显式2×2 det、10000 context bootstrap910先封存再运行源码analyzer；5145数值项max误差3.55e-15，cell投影误差4.44e-16。逐recipient/context先det再两recipient均值与私人方向bootstrap全部一致；特设mean(det)≠det(mean)反例，防误替读数。两行各norm>.001才能归一化，精确.001置0；两行.002即使norm乘积<.001仍保留，signed负/零保留。两rank1差det正而CueB本身det0的例子由第一个co-primary正确拒绝。

patch recipient和donor gold的full/candidate/margin/discord4均独立核，避免把忠实执行donor导致recipient准确率下降误判运输失败。Food/Service/bias/product及私人方向保留；两个correct-code行selectivity与实际function仍要随未来raw报告，det正不单独证明成功criterion部署。

native early/late同prefix/形成/读取图，确只换字段次序；independent early Cue读两Source而body own，independent late全query own，差值也含可达图变化。pure instruction普通native形成，非旧E124–127复合instruction接口。CueA辅助name差只消加性world不变词法主效应，不能排除name×world；整个多层块与非线性functional det不识别独立latent/ID程序，也不排除criterion-conditioned retrieval。

[JSON完整实际计数及四批SHA](independent_review_2026-10-12.json)；[前次设计与近邻范围审阅](design_independent_review_2026-10-12.md)。下一步仅按原卡执行既定run后再核实际消费/数值地板并先raw后summary；没有新科学资格或GPU矩阵。
