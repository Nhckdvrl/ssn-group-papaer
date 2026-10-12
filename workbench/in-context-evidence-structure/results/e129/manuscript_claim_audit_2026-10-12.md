# E129 paper-critical新增文稿独立审计

2026-10-12；对应C23/C24、I04、P17。审Discussion两句、附录L与主张边界，区别于[完整4/4 raw审计](independent_raw_review_2026-10-12.md)。没有独立GPU重跑、科学源/主张/文稿修改或状态判断。

当前新增表格与叙述通过校对。两模型确认的两个co-primary均CI含0；Qwen3-14B小正J .00160[.00024,.00300]nats没有被隐藏，也没有冒称正确部署两个标准。独立复算对照新增两表6行/20统计格/60数字呈现，全一致。本文段没有把Cue接口不足推广成默认模型无criterion信息，也没有撤回既有历史形成阳性。

快照PAPER_DRAFT SHA `1c87eecd1780130484566ac9bbaa6d1d345e96071da41760395a22a34cb9a69d`；PAPER_APPENDIX SHA `413a509dc13dba04c851449d3475953912054e217fa4eebeef6a7e83345ed8ed`。原始E129 runs摘要 `376865666b6ad982b1d65bf85b4d918d22af286a156016bfa483027d0064d4d5`保持。

det表含两phase/两checkpoint全部正负，没有用Llama探索差矩阵正替代CueB本身或确认结果。det是逐recipient/context算后等权平均，不能换成平均矩阵的det；同样不等于latent rank。CueB matching两方面方向与donor实际表现仍保留完整报告。私有码定向、同receiver B/两recipient/own主图、joint secondary及CueAll非oracle准备的界限准确。

功能表的Food single使用**B在food_positive world**，Service使用B origin，并非用更弱/更强的A single替代B primitive。early/late各self实际正确率取同Food/Service冲突4query，范围正确；相对于E128，E129这一控制是跑前既定读数。Native early/late是纯字段次序参照，independent early/late还改变Cue介导/直接读取图，附录明确。Q14纯instruction candidate84.38%/full44.14%以及由raw argmax归类的in-label55.08%全部一致，不能描述成恢复完整实际输出。

全部四run的最高full-token/cached差为Q14 discovery `5.53131103515625e−5`nats，附录5.5313e−5正确；两确认上界才是1.5258789e−5。graph/self0、96ctx/49152评分/.413184 GPU时、20580独立复算及58752/27648/221184逐层prefix/Cue/body记录均一致。复算计数不增加独立样本，也没有独立GPU重跑。

必须保持的范围现已写清：donor来自独立私人形成，native early/late的完整前向参照没有移植native形成的Cue；因此这次结果不支持完整criterion×code Cue运输，不能证明没有早期task信息、criterion只能输入后形成或所有原生接口都失败。小criterion-only与J响应可是真实部分功能，不能以双det未确认自动抹掉。整多层KV块还可能改变检索policy/校准，name×world与固定方面顺序仍在范围内。

Discussion两句准确将它用作task-state解释的边界，三项认识仍是Source关系的形成、内容与部署。新增实验没有把解释对象变成寻找完美task-vector胶囊，没有为旧C21–23附加资格，也不将与Hendel/JIT/Dong兼容自动判作无增量。当前新增段无需补新实验；若要进一步解释默认形成如何准备Cue，那个尚未测的问题可按[独立高层切口评价](formation_cue_followup_design_review_2026-10-12.md)另行检验，而不是改写本轮primary。

阅读范围：当前Discussion与附录L全文、新增表与对应冻结raw/独立JSON、E129源/card及authorreport/四panel图；其它正文/附录旧数字沿用已封E128/E127及更早审计，本次没有再次全量重算。近邻的实际已读章节见既有E129设计/后继切口记录，未独立复现外部代码。只核证据适配，不宣布整体论文意义或投稿完成。
