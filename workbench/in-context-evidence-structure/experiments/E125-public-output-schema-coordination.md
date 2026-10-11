# E125：只共享Source–输出词空间，能否协调私人规则？（2026-10-12）

- **状态：** PLANNED，0评分；E124三家族确认/独立完整校对已到，六项最终CPU和独立pre-score通过。不是再换名字或层/头搜索。
- **类型：** PILOT / CLAIM，保持三条主文认识。
- **对应：** C23、I04、P17。
- **问题（一句话）：** 不交换任何私人输入–标签监督，仅共享Source对应的输出词集合，能否在形成期帮助独立规则共同使用？
- **为什么现在做：** E123私人函数/完整输出分离，E124名字共同上下文探索未给跨家族补救，确认正在封版。名字存在与Source–输出关系不是同一种信息。CTA§3.2已发现历史输出传任务/输出空间，TR/TL已拥有空间识别与空间内学习的分解；本项不重命名这些，而检验何种**非私人配对信息**可以共享以支持多规则形成/部署。仅在query给对词表属于已知读取cue；关键竞争是F1R0仍可协调还是只能R读取有用。
- **设置：** 冻结Qwen3-8B/Mistral-7B-v0.3/Llama-3.1-8B；同revision/conda/FP32/eager。SST5原文gold0/4，train demo哈希池/官方validation探索→test确认；n16 seed125001→n32 seed125101 `--materials validation`，新context与私人约定，不按科学方向筛模型；确认Source换Robin/Jordan。A no/yes，B pass/flag；B origin与A相反，cross相同；所有私人方向、两Actor8q都保存。
- **操纵：** 通用HEAD在公共表之前。表仅写`Output words: Alex: no, yes. Sam: pass, flag.`，不写哪种评论对应哪词、不写criterion。真实表、无关姓名表(同词/同row次序)、交换Source词空间表(同名字/同词多重集)三个counterfactual；全token数/位置/Source角色匹配，按实际Source名字排序与匿名角色配对。无关名字只按tokenizer在冻结Kim/Lee等池选，不看score。表的两词顺序不会规定私人正负。
- **形成/读取图：** 所有严格历史cross-source私人demo→demo访问全层关闭，保留各自历史与通用HEAD。F控制全部demo能否读公共表；R控制整个query能否直接读它。query仍读取两套私人缓存，原global positions不复用。公共表在所有监督之前，不含私人配对、不能从未来读监督；HEAD在表前，防关闭F时后续公共relay。三表×F×R×Bworld×两Actor=48；无表native4/independent4/single3/一句指令independent4，共63×8=504/context。
- **读数：** primary完整词表下一token准确率，context均匀两world×两Source×8query。冻结关键对比：true(F1R0−F0R0)减unrelated同形成增益；读取同理。true形成增益减swapped形成增益，用保持实际名字/词集的关系反转检查；F/R交互、true形成-minus-读取、A/B、same/opposite完整报告。辅助own-space候选、Source词率/other词率、正确margin、A对B约定halfresponse signed/abs。public词出现本身不作新意：unrelated含相同词/结构，只有Source关系不同。
- **阳性对照：** 每本批single函数、native与无表独立、同一句指令；default/native4D、自源mask no-op、cached/fullsplit≤.001；三表F0R0所有Source/HEAD缓存与argmax一致（表不可达）。每层实际17→21prefix配置、47→63query接口mask消费记录，不只末位。全部private隔离＋query-own-only Bworld→A图零；缓存独立/未污染、对齐geometry、gold与Source归属。
- **噪声地板 + MIE：** FP32 floor≤.001；10000context bootstrap/seed910。n16数值有效则三家族固定n32，不挑涨分model/seed；关键CI/效应与Actor/方向改变解释，不设任意80%修复门槛。无法显著提高且CI宽只作未定，不宣称等效。
- **混杂审计：** 不同表同长，private监督/raw/query不变；无表prefix短只作参照。mask重归一化与后继活演化，F差测特定图操作而非静态可用性。表是显式输出metadata，提供已有TR可用的线索；构造性结果不能证明天然模型本来就有相同binding ID，不能泛称新schema组件或全ICL模块化。swapped与private示例冲突是诊断反事实，不是两条合法标准都须采用。SST可在预训练见过，fresh私有方向/配对不等于新语义能力；新context而非新benchmark/所有query从未使用。名单和输出空间作用不能由不同损坏率硬拆成独立组件。
- **决策表（跑之前写）：**

| 结果 | 实际更新/下一步 |
|---|---|
| true F1R0特异改善完整输出，candidate强；swapped朝错误词空间改变 | 公共Source–输出关系可经形成后状态协调私人函数，无须私人配对交换；补充形成/使用的构造认识，按实际checkpoint边界接回主文，不新命名组件 |
| 只有读取有效 | 当前协调依赖显式query选择；不把形成期共享一般上下文好处归于此metadata，已有形成关系阳性保留 |
| true/unrelated共同增或弱/负 | 普通词曝光或该schema接口不足；停止此公共metadata支线的执行扩展提议，回到整体解释与近邻，不调十种header追80% |
| Actor/私人方向相反或candidate受损 | 全部保留，不能用平均称无损私人函数组合 |
| 数值/可达/gold失败 | 修实现记录0-score或VOID，重新封源；不筛科学分数 |

- **算力：** 独立空卡三家族16→32，预计0.8–1.8 GPU·时；仅缓存所在21/20，别人占卡不碰。关键依赖E124完整审计先回来；此卡准备不是铺开所有分支。没有训练、strength/head/layer矩阵。

## 结果
待CPU预检/首评分前源码冻结；0 GPU评分。

**0-score实现校对（封源前）：** 三表inert检查从硬编码unrelated改为当前roster，并直接assert完整argmax；只增强数值审计、不改图/读数。Mistral确认CPU缺token长度匹配的无关名字，0GPU评分，正在只按tokenizer扩充固定negative名字池；不改真实Source名、科学读数或按结果选择。

Mistral实际tokenizer确认Robin/Jordan表22tokens，原negative池表21或其它长度；新增固定Avery/Bailey同22tokens（无评分）解决。其它5批首匹配姓名不变，全部6预检用最终源再核。交换关系须另看swapped自身Source/other词变化，单凭true−swapped CI正不证明主动错误路由；原aux字段/完整primary保留。

**首评分前封版：** 科学源SHA256 `75f7566582cbaf7cf80dd130b409b32436df281a262884d8db381991437612b9`；builder沿冻结f02104…不改。独立CPU144ctx/2160token流/3024mask、三表/全query图通过，[pre-score audit](../results/e125/independent_review_2026-10-12.md)。公开Source→词集本身是关系监督；本项不交换的是私人input–label配对，不能称完全没有监督。三模型全部固定16→32，不按E124正负挑模型。
