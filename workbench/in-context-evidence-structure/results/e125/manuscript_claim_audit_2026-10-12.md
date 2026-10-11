# E125 纳入主文后的 paper-critical 独立审阅（2026-10-12）

当前摘要—三项认识—主要证据链与已有实测范围适配；E125 增加了“私人输入–标签监督隔离时，共享什么公共关系能帮助实际输出”的功能证据。新增数字全部一致。没有发现当前有界措辞必须补一个新实验才能保留的决定性缺项；不由此宣称整篇研究问题已完全解释，也不自动改变主张等级、研究状态或投稿决定。

这是 **paper-critical 审阅，不是新的 raw/GPU 实验**。先前独立 raw 封版保持：E125六批144context/72,576评分，18,126数值比较最大误差0；全部63接口、私人方向、Actor/world、完整输出与other-word保留。作者 summary/report 再比18,130项max0、240表行/2,610数值呈现；它们是重复呈现，不构成新样本。最新报告已明确“历史形成中私人监督互不可达；joint query仍读两cache”。未独立GPU重跑。

本轮阅读全文 PAPER_DRAFT（重点摘要、Introduction三项、§3–7/9）、PAPER_APPENDIX新增G/H，并将新§6.3/6.4/G/H **184个数值呈现、12表行、9元数据项**与本会话先于作者analysis得到的E124/E125独立seal逐项核对，一致。旧§3–6.2数字沿用已完成E119–123独立raw与paper-critical报告，本轮没有从头再算E90/E109/E111–123全部raw，也没有新GPU复现。真token/实际mask/官方gold依据E124/E125既有独立全量审计。

审阅快照：PAPER_DRAFT SHA256 `bee46bd514f6dd94b1d5b9b1e769c28ec8dae66f7c57c08de60984f9c0c1afda`；PAPER_APPENDIX `00577dae3064f874aa0efbdf478be6ba27a8688ceba622c34f4dff78fa76ef5f`。E125冻结science `75f7566582cbaf7cf80dd130b409b32436df281a262884d8db381991437612b9`/a0a79918未改；报告script `b104122146291d6d0201cadcd97fe45621ee48250f2408cea5766b750c1fcbc9`、报告 `221fbba6870fa66e9168e29c205052082e300aa360746977681a1cb5b1965555`。 process/check为0ERROR、31历史WARN。

## 新证据与现文稿的适配

| 问题 | 已核证据 | 文字范围及缺项 |
|---|---|---|
| 共享公开关系是否只在query提供事实？ | true−unrelated的形成-only完整输出增益Qwen+26.66[23.05,30.47]、Mistral+7.71[5.08,10.45]、Llama+8.30[6.05,10.84]pp；整query不能读表、HEAD在表前、私人历史跨源全层禁止。两个global私人方向CI均正。 | 可说公开Source→词集关系经demo形成影响后续功能。表本身属于关系监督，不能称无监督或没有任何共享监督；后继private状态与attention归一化会变，不能称私人功能数学不变。 |
| 形成与直接读取是否可等同？ | 三checkpoint平均reading identity CI跨0，Mistral形成×读取full交互+4.10[2.54,5.96]pp；Qwen B reading identity+1.76[.59,2.93]pp。 | 主文准确限定“checkpoint-mean”并保留Mistral交互。未检出不等于严格无效/等效，更不能声称所有Actor/direct access无功能；F/R边数与mass不匹配，不是等强度内容分离。 |
| 正确表的优势是否证明swap主动wrong-space？ | true−swapped形成差+11.72[7.91,15.72]/+4.39[2.15,6.74]/+5.47[2.44,8.59]pp；**swap自身**full +16.99[13.77,20.31]/+6.05[4.10,8.11]/+2.64[.10,5.08]pp，other-word −18.75[−21.78,−15.92]/−4.79[−6.74,−2.93]/−3.22[−5.47,−.98]pp。 | 当前“net reduction”和“following the table alone不足”正确。不能从前一个CI正推主动错路由，也不能从净下降排除任何局部wrong-route或赋予唯一算法。swap与实际demo词空间冲突，gold仍从私人规则重算。 |
| 功能改善是否等于两私人程序无损组合？ | true F-only full79.98/60.45/61.33%，低于本批native95.41/94.63/95.90%；Qwen candidate95.12→91.31%，代价−3.81[−5.66,−1.86]pp。Mistral A true−unrelated+4.49[−.20,9.38]、Llama A+.20[−5.27,5.66]pp跨0；MistralF-only A30.47/B90.43%。 | 文稿已报告候选代价、非对称和非lossless。primary是两Actor请求均值，非同时正确率；“joint use”只能指读两cache的计算环境。single本批强但非所有方向满分；§6.4已改为“strong single-source private-function performance”，文字准确性修正通过，不加实验门槛。 |
| E124与E125是否构成名义身份→新binding组件？ | E124 names-only形成关系特异full Qwen+4.59pp、Mistral−1.07pp、LlamaCI跨0；E125公开词集关系三确认mean正，但swap也正。 | 两项是独立冻结的图/公开信息功能对比，未等call匹配两种表、不能作两种公共材料因果差值，更不识别bindingID。现文稿未作该过读，partial/model-dependent范围正确。 |

## 从研究问题与最强近邻看实际增量

当前三认识的链条不应缩成“缓存包含上下文”或“标签集识别与分类不同”。E109–121先在输出身份依赖的**指定actual接口**建立系数一预测、残差与无donor原生条件贡献；固定label-stream反事实测部分关系内容。E122/123前瞻比较完整形成/query政策并保留平均收益、同标签损失、另一词空间输出及private弱方向。E124/125再表明：禁止私人例子之间传递并不使可用证据只由自己的input–label对决定；公开Source–词集关系能够通过形成阶段改变实际词表使用，且正确/交换表有不同但非简单反向的作用。这是同一关系provenance/功能问题的可测推进，不能只靠“两来源是新任务”论证新颖性。

| 近邻已拥有的内容 | 本文可保留的具体距离与开放问题 |
|---|---|
| [CTA §3.1–3.3](https://arxiv.org/html/2504.00132v2)已因果展示跨demo上下文化、输出空间与部分函数信息沿历史边传递，且上下文化改变歧义证据的后续使用。Cho/Add-Up的label合并、上下文化QK/V与Crosbie的操作特异性见已有E119/E122审阅。 | 不抢“先形成再聚合”“历史label传任务/空间”。具体新增是合法多来源的关系provenance、输出身份反事实的冻结接口预测、原生操作/两Source实际功能政策，以及私人隔离下公共关系形成的实测；不是穷尽ICL算法。 |
| [Feng §3/4.1](https://arxiv.org/html/2310.17191v2)已提出因子化、位置独立binding IDs，并用entity/attribute两侧向量算术检验协调；[Mixing](https://arxiv.org/html/2510.06182v2)允许位置、词汇等机制共存。 | Source→词集也是已有binding框架能容纳的关系。E125没有解出ID子空间/两侧ID算术；单独true−swap也不能据此认独立组件。其增量是公开关系在私人规则形成图中的功能作用与反字面表预测；保留既有binding/词先验解释。 |
| [TR/TL §4.2](https://arxiv.org/html/2509.24164v3)已通过head/输入消融区分label-set识别与集合内映射。 | own-word率与candidate/full差不能重新命名成首次TR/TL分离。本文测请求Source下空间使用的历史形成条件，未定位新的TR组件。 |
| [PCW §2](https://arxiv.org/html/2212.10947)已有独立窗口形成、共同query读取；[CacheBlend §3.3/4](https://arxiv.org/html/2405.16444v2)明确预存块缺跨块上下文化，复用KV可能失真并以选择重算融合。 | 不能宣称首次独立cache可一起读/首次不可天然组合。这里保留原global positions，不做长context效率方法，重点是私人规则/共同公共关系的功能依赖。完整Source隔离降低full而candidate仍强只是具体任务事实。 |
| [SADA §3/4.4](https://aclanthology.org/2026.acl-long.1046.pdf)学习context→低秩参数映射，通过hidden/logit/task目标与全context状态对齐；[Zellige作者技术报告§3.5/4.6/5.5](https://zellige.ai/research/kv-injection-structural-alignment)讨论cross-session模板/边界KV注入并做全栈与分带patch。 | 一般“内部对齐/结构兼容”已有明确对象。SADA是训练的压缩/适配、后者是作者技术报告（未核接收或独立复现），不能当唯一机制权威。本文仍为冻结模型中的公共关系形成/私人功能实验；需要给cache-composition扩展保留这些近邻，不能以改术语取得first。 |

本次实际新读上述primary的指定章节，Feng含position-independent与两侧算术，TR/TL含分离消融，PCW含图/位置，CacheBlend含缺跨块上下化及选择重算，SADA含结构/训练与alignment ablation，Zellige含矩阵/patch与报告限制。未逐篇全文/代码复现，未核Zellige接收，也没有把这次scope复核写成完整新颖性检索。其它旧§7文献沿用既有论文卡与E119/E122/E123审阅的阅读范围。

## 剩余科学问题与本次交付边界

现有actual donor重建只说明该接口预测；E120提供指定原生operation条件贡献而非独占必要通路；E125不能由public F-only的full改善直接反推出独立潜在程序。正文已明确残差/路径、mask live状态、私人方向、固定方面顺序、自然任务范围与multi-comparison。这些限制未吞掉原有有界阳性，也不构成新head/layer/seed资格。

**E126在本轮评分前**是明确开放问题：事实、私人pairings、词集、private global positions保持不变，等价schema行序形成的整Source cache以2×2组合，能否出现joint非加性交互。其设计可抵消单缓存加性quality差；own-only balanced对比0是数学控制。即使有阳性，仍不能区分binding坐标与非加性attention/KV尺度、位置/词汇上下化，更不能首次宣称KV memories有context依赖。它不是E125阳性/旧C21–23保留的前置条件，尚无科学结果可引用。

没有要求新增决定性实验。本报告完成的是当前文稿的数字/必要范围/近邻所有权适配，整体来源规则如何可靠组合仍是开放研究问题；不能用有限矩阵结束自动宣布完整逆向已完成，也不能据非SOTA/非完整程序关闭线。保持已授权E126冻结执行和其独立raw校对即可。

未改science/card/claims/论文/状态，未GPU评分，未commit/push；E115–124封版保持。只同步E125独立报告的作者report SHA与最终文稿校对链接，其raw runs/geometry对象hash未变。详见[独立raw审计](independent_review_2026-10-12.md)、[JSON](independent_review_2026-10-12.json)与[E126评分前审计](../e126/independent_review_2026-10-12.md)。
