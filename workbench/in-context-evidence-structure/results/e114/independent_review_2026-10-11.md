# E113/E114 独立科研校对（2026-10-11）

**结论：新增跨家族关联路径与 native 形成作用通过独立复算，没有需要作废评分的算术、缺样或缓存硬问题。** E114 正常允许 query 读取全部 prefix 时，A 位置缓存的形成状态在两个 B 读取背景下都改变规则响应；有符号交互也为正，Qwen 0.7747 [0.1217,1.4244]、Mistral 0.3207 [0.1891,0.4578] nats，非加性证据不只来自绝对值。历史答案形成边解释部分 native namespace/关联作用；不能写成固定 reader、两个独立模块、独占中介或完整规则算法。

**必须补的实现说明：** Mistral 实际使用分块 tokenized prefix。SentencePiece 的独立 `enc('\n\n')` 为 `[29473,781,781]`，含前导 metaspace；B 答案 sender scope 共 32 token，Qwen 为 16 token。Mistral 全部 32 context 的分块 token 流与整段字面字符串的常规编码不同。条件间控制与同实际 token 流上的 native/split 校验仍通过，这不要求作废或追加控制；但必须注明实际序列化，不假称已验证普通整串 tokenization。

本次校对对应 C21/C22 的 native 扩展、拟 C23 与 P17；只新增本报告和 [独立复算 JSON](independent_recalculation_2026-10-11.json)，未启动模型/GPU、训练、新实验或微观控制。未改工作台状态、证据等级或论文计划。

## 1. 独立性与原始分母

先审 `e113_mistral_relation_content.py`、`e114_native_formation_reading.py` 与原始完整 run/preflight/contexts/behavior。初次读取时三批确认已完成；均先确认 run 存在和两种 JSONL 各 32 行，才读评分。未先读新增 analysis、实验卡结果、CLAIMS 或综合。独立计算冻结后才比较作者汇总及卡/当前形态。

独立 bootstrap 使用 **20,000 次、seed=20261012、percentile 95% CI，单位为 context**，同 context 的世界、条件和 8 query 保持配对；未调用作者 analyze/summarize。冻结值的 canonical SHA 记录于 JSON。作者采样次数/seed 不同，CI 端点小差别是预期。

| 完整确认 | seed | 条件/context | query/context | 总评分 | 与旧探索全部文本交集 |
|---|---:|---:|---:|---:|---|
| E113 Mistral | 113101 | 24 | 8 | 6,144 | 0 |
| E114 Qwen | 114101 | 43 | 8 | 11,008 | 0 |
| E114 Mistral | 114201 | 43 | 8 | 11,008 | 该家族无对应 discovery，不假称有一次重复 |

三批 ID 均 0–31，全部条件名称、有限 z、gold、姓名/抽象来源对应、每来源标签 4/4 与 private polarity 16/16 通过；context 内 demo/query 无重叠。E114 **全部 43 个预定条件名称**由独立集合核对一致。argmax label/correct 逐项从 token ID 重算通过，没有把非标签回答排除。

最后比较作者 E113 123 项、E114 每批 218 项，合计 **559 项**主要均值与重建数值，最大绝对差 4.77e−15。没有数字错误。读数定义/完整全部预测器见 JSON，不只列最好的一项。

## 2. F/R 交叉到底操纵什么

在每个 origin/cross 世界内，F=0/1 表示 **A 全部 prefix 位置的 shared/far 历史形成缓存**；R=0/1 表示 **B 全部 prefix 位置的 shared/far 上下文化缓存读取环境**。两条来源的原文和标签序列可保持对应，但 donor 由整个 prefix 形成；B 缓存也可能已含 A 信息。HEAD 原文和因果前缀状态一致。

F0R0 是原生 shared cache；F1R1 复制全部 A/B 位置后重建原生 far cache。交叉角 F1R0/F0R1 是诊断性缓存混合，不声称模型会自然进入这些状态。native 的含义是 **query 阶段允许读取全部 prefix，使用原生 attention 与冻结网络**；不是说每个混合 cache 都对应一个天然完整 prompt。

R 改变 B 可供查询的 K/V，还会改变 query 表示、竞争和后继读取；因此 **不能叫“固定 reader”或“只改直接 foreign 标签复制”**。F/R 的操作性因素也不是两个纯 Source 内容或两个独立全局阶段模块。历史答案 K-only/V-only 只表示该边不直接交换另一通道；后继活跃状态并未全部钳制不变。

主读数为每 context 的 `D(F,R)=mean_q gold*(z_cross−z_origin)`。以下“幅度”是 `mean_context |D|`，不是 query 绝对差平均。形成条件效应为 D0R−D1R；交互为 `D11−D10−D01+D00`。同时报告有符号及绝对幅度统计；**绝对值本身可创造交互，不能单独证明原始计算不加性。**

## 3. native 形成、读取与交互

| 规则幅度，nats | Qwen | Mistral |
|---|---:|---:|
| F0R0 | 5.7701 | 3.0120 |
| F0R1 | 2.0131 | 1.1098 |
| F1R0 | 3.6724 | 1.7743 |
| F1R1 | 1.2544 | 0.4262 |

F1R1 的有符号平均仅 Qwen 0.5163 [0.0219,0.9944]、Mistral 0.0784 [−0.1051,0.2544]，幅度仍非零；不能用符号抵消宣布功能来源依赖为零。

| 配对条件效应/交互，nats | Qwen 幅度差 | Qwen 有符号差 | Mistral 幅度差 | Mistral 有符号差 |
|---|---:|---:|---:|---:|
| A 形成，B shared | 2.0977 [1.3625,2.8868] | 2.0977 [1.3625,2.8868] | 1.2377 [1.0364,1.4600] | 1.3281 [1.1125,1.5647] |
| A 形成，B far | 0.7587 [0.2768,1.2680] | 1.3230 [0.8202,1.8501] | 0.6836 [0.4637,0.8999] | 1.0074 [0.8059,1.2232] |
| B 读取环境，A shared | 3.7571 [2.6846,4.8345] | 3.9309 [2.7993,5.0626] | 1.9022 [1.2663,2.5372] | 1.9262 [1.2828,2.5736] |
| B 读取环境，A far | 2.4181 [1.6147,3.3121] | 3.1562 [2.1846,4.2452] | 1.3481 [0.8280,1.8803] | 1.6055 [1.0117,2.2125] |
| 总 namespace | 4.5158 [3.7217,5.3244] | 5.2539 [4.1660,6.4165] | 2.5858 [2.0668,3.1175] | 2.9336 [2.3269,3.5555] |
| 交互 | 1.3390 [0.5396,2.2198] | 0.7747 [0.1217,1.4244] | 0.5541 [0.2773,0.8735] | 0.3207 [0.1891,0.4578] |

因此，在这些因子和规则 margin 反事实中，平均响应不能由形成与读取环境的简单相加效应概括。它不证明网络的全部算法一般非加性，更不识别唯一模块数。两背景的条件效应应保留，不能用相除、相减自动分配“形成占总作用多少”或中介份额。

准确率只作功能后果另报：shared origin Qwen 86.719%、Mistral 71.094%，far origin 98.438%/93.750%；single A 99.609%/98.828%。origin 一句指令 89.453%/73.047%。这是受控私人情绪规则，不能直接推广为真实 annotator 的自然错误率或一个部署方法的改善预算。

## 4. 冻结系数 1 的 native namespace 预测

对每个 B 读取背景分别以 F0Rr 为 baseline，历史答案形成边 K/KV/V 的 delta 预测 **A label 接口**及 **全 A 形成接口**的 delta；origin/cross 同时保留。以下全部为逐 query 的 rule 双差分，**没有拟合系数或筛通道**；raw namespace 的完整 RMSE/r/CI 同存 JSON。

| target / B 背景 / 形成边 | Qwen r | Qwen RMSE | Mistral r | Mistral RMSE |
|---|---:|---:|---:|---:|
| label / shared / K | .8647 | 1.7499 | .9184 | .5469 |
| label / shared / K/V | .8995 | 1.5605 | .9591 | .3877 |
| label / shared / V | .7658 | 2.1631 | .7400 | 1.0277 |
| label / far / K | .8955 | 1.0729 | .9070 | .6193 |
| label / far / K/V | .9303 | .8678 | .9679 | .3963 |
| label / far / V | .7038 | 1.6474 | .7789 | .9268 |
| 全 A / shared / K | .7876 | 2.4024 | .9326 | .6704 |
| 全 A / shared / K/V | .8078 | 2.3181 | .9658 | .5135 |
| 全 A / shared / V | .7043 | 2.7723 | .7373 | 1.2748 |
| 全 A / far / K | .8048 | 1.5142 | .9094 | .6670 |
| 全 A / far / K/V | .8541 | 1.3204 | .9654 | .4541 |
| 全 A / far / V | .6474 | 1.9467 | .7601 | 1.0040 |

零预测 RMSE：Qwen label shared/far 3.3879/2.3158，全 A 3.9258/2.5384；Mistral label 1.3596/1.3241，全 A 1.6104/1.3913。全部通道的幅度、逐 query 差异和 CI 要与高相关一起看；共同减 baseline 不能靠相关单独证明因果解释。

例如 Qwen label K/V 在 shared/far 的 r CI 为 [.8189,.9434]/[.8628,.9611]，RMSE CI 为 [1.2366,1.8867]/[.6932,1.0707]；Mistral 对应 r [.9455,.9728]/[.9519,.9791]，RMSE [.3140,.4601]/[.3418,.4485]。K/V 相对零预测 MSE 降低：Qwen label 78.8%/86.0%、全 A 65.1%/72.9%；Mistral label 91.9%/91.0%、全 A 89.8%/89.3%。**它们是误差比较，不是原生中介百分比。**

native 重建明显弱于旧 gated 子图，尤其 Qwen 的全 A 接口。可写“形成边在 native 读取环境中仍有预测力/近似或部分重建”，不能把旧 gated r=.969/.985 当本项全部 native 机制的精度。预测依赖 actual donor 状态，不是无 donor 的完整新 query 算法。

## 5. 固定标签关联：跨家族 gated 与 native 范围

E113 Mistral 保持全部 B 标签词、Source、标签位置、输入多重集，cross 与 within 均移动 8 个 B 输入。A-only query 下，cross−within 的 context 幅度差：全 A gate **1.0829 [.8212,1.3435]**，A label 接口 **.9807 [.7728,1.1923]**，历史答案 K/V 形成边 **.40425 [.31384,.49999]** nats。其有符号差依次 1.2253、1.0742、.4302，均 CI 不跨零。

E113 cross 形成边 K/V 幅度 .46457 [.36893,.56497]，V .47678 [.37505,.58731]，K .10194 [.07129,.13781]；K/V−V=−.01222 [−.04338,.01849]。这在 Mistral 支持与 E111 相同的**部分关联路径**，不证明 V 与 K/V 等价。完整 label cross 与答案 K/V 仍差 .7065 [.5479,.8730]；逐 query label 关系预测 K/V r=.9131、RMSE=.9375，零预测=1.4490，系数 1 未完整重建。

E113 私人能力阳性：正向 126/128=98.438% [96.094,100]，反向 122/128=95.313% [91.406,98.438]。不是 100%；不沿用旧 Qwen 饱和值，也不以其少数错误否认干预中的明确阳性。

E114 **正常可读全部 Source** 的固定标签 cross−within：

| native 关联幅度差，nats | Qwen | Mistral |
|---|---:|---:|
| 完整原生查询 | 5.2111 [4.4257,6.0273] | 2.8611 [2.3704,3.3704] |
| A label 接口 | .4540 [.2063,.7262] | .3187 [.1894,.4575] |
| 历史答案 K/V 形成边 | .24081 [.14945,.34827] | .26254 [.19740,.32947] |

答案 cross K/V 与 K 幅度差分别 .21443 [.12185,.31943]、.24061 [.18630,.29702]；V 仍明显比 K 更能产生该关联作用。**但 native 不能照搬“V 与 K/V 无差”：** Qwen K/V−V 幅度 −.03557 [−.08198,.01114]，有符号差 −.08916 [−.13300,−.04488]；Mistral 幅度 −.03356 [−.06680,−.00362]，有符号差 −.04168 [−.07411,−.01290]。应写 V 较强/承载部分关联作用，保留通道交互，而非严格同一机制或互换等价。

审稿式 POST-HOC 诊断（不替换主读数）：native 答案 K/V 逐 query 预测完整 A label 关系差的 r 为 Qwen .6657、Mistral .8250，RMSE 1.3157/.5230，零预测 1.6665/.8556。完整 native 的 5.21/2.86 幅度也远大于该边 .24/.26 的超额作用；不称完整关系程序，不把任何比值当可加中介份额。

## 6. 实现/混杂审计与实际 token 序列

- **采样：** tokenizer 几何匹配只按输入签名，不看模型输出；确认材料在 pilot 之后冻结，新词句与旧探索文本交集 0，但 confirmation 的不同 context 可重复用同一词/句式。CI 单位为 context，不是独立的 256 query；范围条件于这些固定词库/模板和模型。
- **token/位置：** 用 Rust tokenizers 在 CPU 独立重建 Qwen E114 和 Mistral E113/E114，每批 192 个 origin/cross/within×shared/far 流。长度、roles、label anchors、内容范围、答案尾部范围均通过；A raw token 不变，关系变化只在 B content，namespace 只在 B label anchors；标签 ID 与 preflight 一致。接收点为全部 8 个 A label，未选头/层。
- **Mistral 序列化：** 本地 base snapshot revision caa1feb0… tokenizer SHA=e553af6f…；`enc('\n\n')` 包含 metaspace 加两个 newline。因此 B answer scope 是 8×4=32 token，Qwen 8×2=16。Mistral 每个块的 Comment 前与 label 后出现额外空格；E114 首 context 分块为 351 token，整段字面串编码为 335。该差异在全部 32 context 固定存在，不破坏配对控制；native/full-split 检验使用同一实际分块流，不是整串文本编码对照。跨家族比例不据 token scope 大小作归因。
- **缓存/真实消费：** query 与 patch 都深复制 cache；源码在全部条件后校验五个原 cache 指纹。Qwen 36 层、Mistral 32 层的每个主 edge 模式均每层 32 次，自交换 1 次，所有层计数完全相同。hook 正确接到各架构 eager function，只接受目标 receiver 行的替代 attention output；其余 receiver 不直接改，但允许因果后继自然变化。
- **corner/数值：** E113 full-A-cross 与 cross-gate 的原始逐 query 数值可直接复算，max 差 0。E114 F0R0 原生 baseline 为同 cache 的 query；F1R1 与实际 far-native 每 context/world 都有源码断言。far-native 单独评分未写进 behavior，因此这里不假称从两个保存字段逐项复算了该 corner：使用源码、run 的聚合 bound 和因果 HEAD 一致性审查。run 的 max 数值差 Qwen=4.9591e−5、Mistral=7.6294e−6，包含 corner 与首 context 全 8 query 的实际同 token 流 full/split 校验；均显著低于功能效应。
- **静态/自交换：** 两实验的关系 donor 在所有 context 第 0 层 B answer K/V 差 0；edge self cache/query max 0，原 source cache 保持。排除被测试的静态 label/位置身份解释，不证明后续 V 是唯一的抽象规则表示。没有本会话 GPU 重放，明确区分记录的数值 controls 与独立 CPU 数字/几何复算。
- **读数/政策：** 固定 yes/no logit 差，无 condition 自校准；全部 signed/absolute 报告；single A 和一句指令保留。机制不是默认能力缺失的证明，instruction 与 single 的前缀范围不同也不作为同一阶段纯因果比较。
- **资产：** scripts 与 contexts SHA 均匹配 run，模型为固定 Qwen3-8B/Mistral-7B-v0.3 base、FP32/eager/transformers4.57.6。Mistral tokenizer 独立读取对应本地 HF snapshot；没有独立重 hash 远端模型权重，不假称重做了此前 E112 权重身份审计。

## 7. 可进入形态卡的精确范围及必须修正的措辞

**native 主张可写：** 在 Qwen3-8B 与 Mistral-7B-v0.3 的受控餐厅情绪/私人 yes-no 任务中，允许 query 正常读取全部来源时，A 位置的历史形成缓存与 B 位置的上下文化读取环境分别影响对外来源配对的规则响应，并存在已重复的有符号条件交互。历史答案→A label 形成边的 K/KV 反事实在两个读取背景下仍能预测部分 namespace 作用；固定标签的配对关联也能部分经答案 V 传入并影响原生查询。

这增强自然主旨：来源条件化检索消费的是已经经输出相关上下文化形成的关系证据。该形成→消费链不是 gating 人为制造的全部作用；同时 B 读取环境与剩余形成路径仍有较大作用。原生 Source 字段的选择机制仍依先前 E59/E64 的证据，本次没有重新操纵或独立复算该字段因果主张。

必须落实五点：**F/R 是位置缓存因子，非两个独立模块；native 不等于每个混合 corner 天然存在；signed 交互为非加性主证据；native 通道重建是部分/近似、实际 donor 的反事实预测；V/KV 有符号和幅度差如实保留。** Mistral 分块 token 序列化写入实现/资产说明，不能混称字面串编码。

家族范围可扩展至 Qwen/Mistral；**native 关联与交互目前仍为同一受控情绪任务**，没有本轮 native MHS/其它任务确认。C21 先前三个 model/task 组合保留其既定范围，不能把其中 gated 第二任务混入“全部 native 跨任务成立”。这不是要求新增任务或残差控制；在人审/形态卡中明确适用范围即可，不自动定级或决定 candidate 状态。

本次没有发现需要撤回关键评分的硬问题。E113/E114 卡当前对 donor 依赖、混合 cache、通道后继及宽泛 CTA/QK-V 所有权已有正确限定；无需新一轮微观实验。下一步应整合完整结果与上面这些范围，而不是把每个未解释残差写成新门槛。
