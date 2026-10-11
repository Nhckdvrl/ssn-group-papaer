# E125 评分前独立校对（2026-10-12）

**仅CPU / 0科学评分，尚非raw科学结果封版。** 当前source SHA256 `75f7566582cbaf7cf80dd130b409b32436df281a262884d8db381991437612b9`与六批CPU材料/可达图适配，可以冻结并按原实验卡执行；这不是对阳性方向的预判。未独立GPU重跑，未修改科学源/cards/claims/论文/状态，未commit/push。只写本审计与/tmp独立助手。

独立核3家族×16/32的144 contexts、2160实际prefix token流、3024形成mask配置。官方SST gold/训练text SHA奇偶与dev/test query、私人两方向、匿名Source配对和实际分块token序列均核；discovery/confirmation原文交集0。来自每context的真实资料重建，没有把preflight的自述布尔字段当校对依据。

| CPU批次 | n | 三表token长 | unrelated姓名 | prefix长度范围 |
|---|---:|---:|---|---:|
| Qwen discovery | 16 | 15 | Kim / Lee | 464–728 |
| Qwen confirmation | 32 | 15 | Kim / Lee | 491–718 |
| Llama discovery | 16 | 15 | Kim / Lee | 430–752 |
| Llama confirmation | 32 | 15 | Kim / Lee | 491–707 |
| Mistral discovery | 16 | 19 | Pat / Max | 562–837 |
| Mistral confirmation | 32 | 22 | Avery / Bailey | 517–814 |

表长与范围最终以[JSON](independent_review_2026-10-12.json)逐批记录为准；尚无任何模型accuracy/CI。

## 真值、关系反转与可达图

- 用实际匿名姓名反查owner再按名字排序，true的每个Source恰好对应本Source输出集合；unrelated沿同row/词集顺序替换姓名；swapped保持真实姓名和词多重集，只交换name→词集。表无SST评论/criterion描述/正负配对，私人逆转不改变公共词集合。A no/yes、B pass/flag始终固定。
- B origin私人code与A相反，cross经8B评论的无固定点双射使code相同；标签流/评论多重集/Source/位置保留，A原文不动。actual private supervision的gold、请求Source和正确词ID不随错误公共表改变。swapped与示例词空间冲突是诊断反事实，不把它当另一合法标准。
- 完整HEAD在表之前。全层关闭严格历史cross-source private demo访问，self/own-source保留；F0所有demo关闭整个公共表，R0整个query关闭全部表token，padding不能relay。CPU因果传播确认F0R0公共表不可到Source缓存或query，F1R0只能经私人demo形成到query，没有晚公共HEAD绕路；公共表不可能读取未来监督。
- 每ctx15实际token流、21prefix配置与63query接口。两Actor共各(prefix,world,table,F)缓存；R/Source query仅deepcopy后消费、原cache seq与指针保护。prefill和whole-query所有层的实际4D mask hook均覆盖。GPU run的数值floor、cached/fullsplit、inert、graph-zero与真实消费计数仍待运行后独立核，未把静态代码等同GPU实测。

## 两项0-score工具修正已核

初始`a1cd6…` inert query比较在swapped循环仍硬编码unrelated，且没有full argmax assert。最新源已跟随当前table并直接核argmax；Source/HEAD缓存本来已按当前table比较。它修补阳性工具验证，图与full primary、冻结F/R与true−unrelated/true−swap公式没有改变。

Mistral确认的真实Robin/Jordan表为22tokens，原控制池Kim/Lee、Jamie/Taylor、Dana/Chris、Pat/Max分别21/23/21/19，CPU无法匹配、0GPU科学评分。仅按tokenizer追加Avery/Bailey=22解决，两个row-owner顺序均匹配；其它五批首匹配控制与contexts保持，未用模型分数挑姓名。preflight现按context保存无关名单，独立与实际contexts逐项一致。这不是阴性科学结果，也没有改真实Source/词集/读数。

## 读数与解释范围

Full next-token准确率是primary，每phase均匀2world×2Actor×8query；`both`是请求平均，不是joint成功。保留A/B、same/opposite、两个global private方向、candidate、own/other词率和margin。true−unrelated形成/读取增益是匹配图对比；true−swapped正区间本身只说明两个关系条件功能不同，不能单独说明swapped主动推向错误空间。后者必须直接读swapped自身F1R0−F0R0或F0R1−F0R0的other-word/source-word率；最新源已将原辅助other-word字段汇总到phase/contrast，未换full主读数。

公共表是显式Source→词空间信息，是一种公开关系监督；没有私人input-label配对不等于没有任何监督。R-only可作为已有空间识别/读取cue，不能据此独占新意；F-only阳性则限定为这种公共内容经过指定形成图后的功能后果，不推出天然binding ID、新TR模块或全部ICL程序。表名/姓名embedding/词先验、F/R边数与attention mass不匹配、后继状态活演化均保留；无表baseline较短只作功能参照。SST可在预训练中见过，新context与Source名不是新benchmark。

E124已独立6/6封版；本项不设为旧C21–23的新资格，不改变I04/ACTIVE或等级。不按任意修复百分比或pilot方向挑模型、种子、head/layer。本审计建议冻结当前已核的图/真值/读数；科学判断须等待全部原定raw完整。
