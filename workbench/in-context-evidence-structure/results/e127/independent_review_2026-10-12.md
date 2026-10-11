# E127 独立评分前校对（2026-10-12）

**八批实际CPU几何与最终PRE-RESULT观察完整通过，可冻结当前源执行。** 未见必须修的namespace/word-ID/cache/gold/图错误，不添加科学资格或新矩阵。此时0独立科学评分，未GPU重跑，实际层mask消费与数值控制尚待作者完整run后审计。

几何审阅source SHA `cef7952d4ef556abad45c9c2e6d6f351e3b0a1b3fffa9232b9eb728806c943de`；builder `f02104a87b9e67dec413c9c642c107a0f90a7d1046421306e8c4202c59da94ec`、truth `95a574892e7609a25146f730f7843d176fe27487353f2ad7c9fa7fd01971e9a5`。源码完整静态审阅后，从固定官方SST Arrow/contexts/tokenizer独立重构，未读任何科学analysis。

八批192context、4224条实际prefix与4224组prefix mask、6144组query scope/owner图、6144组双KV整Source选择检查通过。覆盖shared/far、两个owner名排列、两world、两row order、两private方向与新confirmation Source。

| 批次 | n | schema tokens | prefix流/mask | query scope/owner组 | private全局位置 |
|---|---:|---|---:|---:|---|
| llama_confirmation_preflight | 32 | [15] | 704 | 1024 | 两namespace/两order一致 |
| llama_discovery_preflight | 16 | [15] | 352 | 512 | 两namespace/两order一致 |
| mistral_confirmation_preflight | 32 | [22] | 704 | 1024 | 两namespace/两order一致 |
| mistral_discovery_preflight | 16 | [19] | 352 | 512 | 两namespace/两order一致 |
| qwen14_confirmation_preflight | 32 | [15] | 704 | 1024 | 两namespace/两order一致 |
| qwen14_discovery_preflight | 16 | [15] | 352 | 512 | 两namespace/两order一致 |
| qwen3_confirmation_preflight | 32 | [15] | 704 | 1024 | 两namespace/两order一致 |
| qwen3_discovery_preflight | 16 | [15] | 352 | 512 | 两namespace/两order一致 |

shared两Source同用no/yes，仅2唯一label IDs；far no/yes与pass/flag为4。Source gold先从官方物理sentiment与private polarity/两world独立重构，再用当前namespace word IDs编码，不随schema order或其它namespace变。shared/far评论、私人pairs、label class-index、query、Source名字完全同一context；ns差只在schema和B答案word ID，全部私人anchors/角色/global位置一致。

公共事实只在同namespace两order之间相同；namespace crossing本身改变B词集、词先验与集合区分度。shared表两个名字都对应同集合，可保留身份次序作用，但不能将表面word辨认成Source。代码shared other_source_word全部False且source_from_word_identifiable=False，必须同时报告不可识别，0不是无泄漏/正确Source选择。in_requested_word_set是词集membership而不是provenance证据。

query/score使用main循环当前namespace的word_ids与namespace变量，调用同步、无异步闭包保存；每namespace重置a_reference，各world donor cache只由该namespace/world两order产生，并在组间释放。整Source所有private K/V逐层替换、HEAD/不可读表取order0；两Actor/两scope复用同组合cache后query深复制，保护指针/长度。原始private word class-index不受label-ID重合污染。

两namespace各11prefill/43query：4schema(world×order)、4native/instruction、3single，共22prefill/86query，每条件8query即688评分/context。全层prefill与query 4D mask实收hook已静态核，不声称未运行的实收已验证。strict past跨Source私人访问禁止、self保留；HEAD在表前无late relay；整query全token R0禁止所有schema，own scope再禁止全部foreign私人位置，padding不relay。

shared/opposite primary准确对应origin world两Actor八query的context平均`.5[(00+11)−(01+10)]`完整词表accuracy；shared同约定/cross world及far/namespace contrast都是冻结secondary，未按结果重选。own-only balanced0由A00=A01/A10=A11和B00=B10/B01=B11恒等而来，不能称新科学双分离；逐Source/order函数将由本批实测，不借E126能力自动声明。

Qwen14使用40c069824f4251a91eefaf281ebe4c544efd3e18本地tokenizer与config，40层；Source metadata通过model路径14B辨认revision，CPU路径满足该分支。Qwen8/14与Llama表15token，Mistral19/22；Mistral独立分隔符3tokens保留。官方0/4 gold、train hash奇偶demo、validation→test query、5–64token、8A8B与8q、B跨类无固定点双射和两阶段文本重叠0全部核。未排除benchmark预训练见过。

新增2/4 unique label logits属于0评分时的PRE-RESULT观察，primary/materials/graphs/接口不变。far LSE(A两词)−LSE(B两词)及两请求的slope/common bias可测相对空间mass；shared opposite的goldA导向Source差能与common code分开，当前shared common采用goldA导向，raw逐query logits全保留，并在逐query取abs后平均，避免正负平衡抵消。最终cef7952…已静态核其shared末维2/far末维4及取槽顺序；8个metadata的新增logit IDs与定义一致，去除这两字段后旧preflight SHA恢复相同，contexts字节未变。因此已验证全量token图复用成立，可以冻结当前source。

独立helper首次缺Qwen14本地映射，修正审计helper后8/8完成；这不是科学源故障、0GPU评分受影响。环境ResourceTracker退出stderr保留（exit0），没有改science/card/claims/论文、状态或commit/push。

[JSON](independent_review_2026-10-12.json)保留所有材料/contexts/preflight SHA、模型word IDs、示例两order schema、逐context几何/边数和范围；实际raw完整后先独立seal再比作者analysis。

最终PRE-RESULT数学范围：far的M是两label集合相对mass，不是整个词表输出概率；common logit offset在同query的M中取消。shared specific等于opposite世界两Actor的平均gold-oriented margin，是现有输出的明确投影，不是独立新机制证据。own-only的specific/common线性配对项可恒等0，但common_absolute先组合两Actor再abs，本身可产生非零2×2；它不构成图失败或latent相互作用。所有raw query logits保留，actual GPU消费/数值仍待运行。
