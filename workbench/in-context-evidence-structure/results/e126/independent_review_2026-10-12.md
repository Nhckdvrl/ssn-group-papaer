# E126 独立评分前校对（2026-10-12）

这是 EXECUTION §5 的独立源码与真 token/图审计，**CPU_PRE_SCORE_ONLY**。当前源可以冻结执行：未发现需要修正的私人真值、Source 所有权、组合切片或预定 mask 错误。科学评分与 GPU 层 hook 尚未发生，本报告不提供科学阳性/阴性、不声称独立 GPU 重跑。

科学源 SHA256 `ad2c6f7af7ab81966ea1253a80e7006747f3485b182fddd1453ffbb1ceb45975`；材料 builder `f02104a87b9e67dec413c9c642c107a0f90a7d1046421306e8c4202c59da94ec`，truth 源 `95a574892e7609a25146f730f7843d176fe27487353f2ad7c9fa7fd01971e9a5`。读实验卡、整个 E126 source、冻结 builder/truth 依赖，并从 SST5 官方 Arrow gold 和六批 contexts 独立重构 tokenizer 流。未读取作者科学 analysis（此时没有科学 raw）。

六批、144 context 独立核 1,584 条实际 prefix 流与 1,584 组 prefix mask；2,304 组 query scope/owner 图和 2,304 组逐层双 K/V 存储选择检查通过。覆盖两个匿名 owner 排列、两种正确表顺序、origin/cross 两 world、两私人方向和 discovery/confirmation 的新 Source 名字。

| 批次 | context | schema tokens | prefix 长度范围 | 独立 prefix/mask | query scope/owner | 整 Source 选择 |
|---|---:|---|---|---:|---:|---:|
| llama_confirmation_preflight | 32 | [15] | [491, 787] | 352 | 512 | 512 |
| llama_discovery_preflight | 16 | [15] | [436, 831] | 176 | 256 | 256 |
| mistral_confirmation_preflight | 32 | [22] | [600, 900] | 352 | 512 | 512 |
| mistral_discovery_preflight | 16 | [19] | [487, 885] | 176 | 256 | 256 |
| qwen3_confirmation_preflight | 32 | [15] | [544, 772] | 352 | 512 | 512 |
| qwen3_discovery_preflight | 16 | [15] | [436, 804] | 176 | 256 | 256 |

两种 schema 是同样两行正确关系的逆序，事实、名字/word 多重集与 token 数一致。A/B 私人内容、标签 stream、角色、label anchors、全局位置在同一 world 的两 order 间一致。Source 名字按 owner 反查，未将排序索引误当 A/B；Qwen/Llama 表各15token，Mistral discovery19/confirmation22token。官方 train 哈希奇偶 demo 分区、validation→test query、gold0/4与两私人代码方向通过；同家族 discovery/confirmation 文本重叠为0。

历史每个 Source 只能读本 Source 私人历史与 HEAD/公共表，跨源私人 past 边在完整角色集合上去除；self 保留。HEAD 严格在表前，不能携带后续表信息。整 query 所有位置都禁止读全部 schema tokens，own scope 再禁止所有 foreign Source tokens；padding keys 不可达。公共表形成的信息可经私人缓存被 query 消费，正是被测对象，不应称删除信息或纯 input filtering。

组合从 order0 深复制，再按 pair 两位逐 Source 替换每层 keys/values 的全部私人 token，包含评论、名字、标签与分隔符；两 donor 属于同一 world、拥有相同全局位置。HEAD 与 schema cache 保留 order0，schema 对 query 不可读；HEAD 在两 order 下相同。00/11 与各自 pristine 的数值一致、mixed own-only 恒等、graph-zero 及全层 prefill/query 实收 mask hook 均已在代码中设置，实际消费与误差值待 GPU 完整运行后审计。

冻结 primary 是 context 配对 `.5[(00_joint+11_joint)−(01_joint+10_joint)]` 的完整词表 accuracy，均匀两 world、两 Actor、八 query，43×8=344 次评分/context；11 prefill/43 query 接口全部保留。该2×2抵消 A/B 单 cache 加性 quality 差，若有差异可支持指定形成背景与联合非加性交互。它不能排除非加性 attention 竞争、KV尺度、位置与词汇显著性解释，也不独立识别 binding ID/共同坐标/模块。逐 order/Actor/private 实际功能、00–11差、native/instruction/single与全部零负结果仍需呈现。

own-only 的 balanced coherent−mixed 为数学恒等式：A00=A01、A10=A11；B00=B10、B01=B11。它只作组合与图控制，不能以0读成新的科学双分离；尚未产生任何 joint 科学结果。一般 KV 上下文化与非天然可组合已有 CacheBlend/PCW 及其它近邻讨论，本设计不构成首次发现该普遍对象。

CPU 进程 exit0；环境末尾 ResourceTracker 析构 AttributeError 保留，不影响本次断言和完整结果落盘。本审计未改 science/card/claims/状态、未占用 GPU、未提交或推送。

[JSON](independent_review_2026-10-12.json)保留六批 contexts SHA、官方材料 SHA、逐 context 长度/边数、实际前两例表、所有范围与控制。后续 raw 完整后另先复算，再比作者 summary。

评分前独立结论发回后，作者以 `377de6c4` 冻结同一科学SHA并启动三家族discovery；本CPU报告仍不将后续未审raw算作已完成科学结果。
