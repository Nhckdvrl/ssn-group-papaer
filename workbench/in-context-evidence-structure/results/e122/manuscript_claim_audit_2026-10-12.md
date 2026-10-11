# 主文证据适配审计（2026-10-12）

**这是 paper-critical 文稿审计，不是额外原始数值审计或独立GPU复现。** 当前摘要和三项主文认识可以由现有有界证据支撑；没有发现必须新增实验才能保留这些措辞的决定性缺口。E120补上原生操作的条件贡献，E121补上自然文本中的可用私有规则，E122提供前瞻的整体功能政策比较。它们不把actual donor充分/部分重建升级为独占必要电路或无donor算法。C21 L3、C22–24 L2及workbench状态不由此改变。

本次对象：正式重组后的PAPER_DRAFT全文（重点摘要、§3–6、§7/9），PAPER_APPENDIX全文、C21–24及最近补记；E122冻结卡/完整干预与材料入口、8批raw/实际token/mask；已封E115–E121独立审计及相关卡/源。对E109/E111–E114主数采用既有独立审计和卡复核，没有在本轮重新执行其全部raw计算。另从E90第三独立批raw点检§2.2答案改变率与方向/幅度。主文/附录表与本会话独立派生结果核对284个数值呈现（含主文/附录重复），一致。

审阅快照：PAPER_DRAFT SHA256 `20627563ad411f9afff059c075336dc778f23d5b049af13a866582e2fe42f085`；PAPER_APPENDIX `5482124c6fe2ebaaee70702d1608b70a884bdb964e48fe669b23a4d2f65c601e`；CLAIMS `64ff5031322b619e123e51f77422cb04e457572acb43962fe05f7b0ca96dc81a`。后续新增E123尚无科学结果，不纳入这些结论。

## 两项必须准确处理的表述边界

| 问题 | 证据 | 缺项/文字建议与当前处理 |
|---|---|---|
| 材料总述不能将所有任务写成no/yes且方向严格平衡 | E90使用safe/toxic，第三批n32 reverse13/32；17.578125% [12.109375,23.828125]答案改变率从raw完全复算。其signed效应.154 CI跨0、幅度.734 CI正。它衡量B敏感性，不是统一正方向或准确率损失。 | 作者已将§2.1的no/yes与平衡限定当前sentiment/dual-aspect，并在§2.2注明Qwen3-8B/MHS/n32；z改为任务正/负输出margin。当前修正通过，不改原数值。 |
| 保留访问图不能等同数学固定其它上下文化信息；target/all-cross不是等强度mask | target只删除过去other-source answer-region→own-label；all-cross删整类跨源历史边。二者边数与attention mass不同，softmax重新归一化，所有后继状态重新形成。E122四模型native四个Food/Service code-response系数paired CI均负，但bias/FS有正负和跨0；这没有独立识别纯input过滤。 | 摘要/Discussion已改为“retaining/preserving other contextual access paths”。建议在§5政策解释或附录明确加一句：`The policies remove unequal sets of edges and attention mass; retaining an access path does not hold its activations fixed.` 这补齐比较范围，不要求新增匹配mask实验，也不撤回政策平均收益。 |

## 三项认识与证据的对应

1. **输出命名影响历史形成。** §3.1的冻结系数1以actual donor历史消息预测指定A-label namespace干预，K/KV、raw/rule双差和残差均有明确定义。§3.2将无donor原生阻断与有限图恢复分开：四checkpoint full-source阻断signed贡献1.649/1.054/.808/1.329 nats均CI正；A-only有限恢复正，而native恢复Qwen−.806、Llama−.233、Mistral+.140、14B CI跨0。当前文稿明确后继状态活演化、Mistral自身历史控制受损和Qwen cross-versus-within specificity CI跨0，故可以称conditional native contribution，不能称唯一、完全内容特异或固定加性中介份额。源/路径删边数不同的范围提示宜与上表一起补全。

2. **固定输出身份的消息有部分关联内容。** 同类/跨类配对保持B输出stream、Source、位置和评论多重集；完整与局部接口、full-source与A-only的读数分别保留。§4没有由namespace高r推导完整criterion程序，也没有把14B负signed交互改成所有模型正。§6 SST两私有方向实际single强：Qwen8 98.4/88.3%、Mistral99.2/96.9%、Llama97.7/99.2%、14B99.2/93.8%；固定词关系KV绝对超额均正而Llama signed −.109 [−.194,−.024]，正文如实保留。可以扩展自然文本的有界形成/关联机制，不能称真实个人标准部署；SST可能预训练见过、只用极性0/4等范围已披露。E120必要贡献在受控任务测得，不能替代在SST上未实施的必要性检验。

3. **形成与读取政策有不同功能后果。** E1228/8、192contexts/93696评分/9960原始复算比较max0支持§5主要表。确认target/native均值收益四模型+2.93/+3.42/+7.37/+2.78pp，四CI正；这是两来源请求均值，**不是同时正确率**。A/B并非所有CI严格正，Qwen8/14B gold一致分别−2.34/−3.61pp且CI负；另两模型一致组均值也负但CI跨0。query-only在Llama+12.06pp、14B+6.10pp，大于target/native，正文已说明。single双方面功能67.97–88.67%，不能叫原子满分；主均值Food函数占75%、Service占25%，不推出每criterion/world单独改善。当前策略对象由生成source真值给出，非源识别方法，亦非统一最佳repair。

§5.3/C24的criterion×private-code响应属于请求A时B关系引起的功能对象。14B native Food/Service相对选择性.282/.404、within-context normalized determinant .410和gated .190支持受限“同一功能方向只换增益”解释之外的响应；不能解释成独立latent程序。历史答案KV的r=.668/RMSE=.646 vszero=.746明确针对**actual label接口**，不是重建整个native criterion反应。label负det、gated label小正rotation、edge小正det及跨0均在附录，不将不同接口结果过读成不同隐藏算法。固定Food先Service、位置选择竞争和多重比较范围保留。

## 近邻所有权与阅读范围

本次回看主来源：[CTA §3.1–3.3](https://arxiv.org/html/2504.00132v2)、[Cho §3/4、§5.1–5.2/A.7](https://arxiv.org/html/2410.04468v3)、[Crosbie §7/Limitations](https://arxiv.org/html/2407.07011)及[正式条目](https://aclanthology.org/2025.findings-naacl.283/)，并核[How Few-Shot Examples Add Up §4–5及范围讨论](https://arxiv.org/html/2605.16591v2)。没有本地复现这些论文、重审其所有附录/数据/代码，也没有把此次措辞审查伪装成完整新颖性搜索。§7其它论文主要依赖本仓库指定章节论文卡与已有定位，未逐篇独立全文重读。

CTA已经拥有跨示例上下文化的因果作用、input/output/task关系信息沿边传输；Cho已有label合并/检索和必要作用消融且承认bypass；Crosbie已有具体操作与整头参与的区别；Add-Up已有上下文化QK/V的分解与功能向量作用。因此宽“上下文化传关系”“QK/V不同”“形成后再读取”不能独占。当前§1/7将增量限定**合法多来源关系的provenance、输出身份依赖的冻结接口预测、以及形成/读取政策的功能后果**，且不称首次routing/representation分离，适配已有证据。不同任务设置本身不证明新颖性，也不构成自动撞车/关线结论。

## 交付范围

这不是有限矩阵结束即整篇完成的判断；本轮逐项检验了正式主文的核心论证链，旧paper-critical两缺口已有新的直接证据。按上述文字边界，可以保留当前三项认识。没有由当前文本必然要求的新决定性实验；E123是另一个已经冻结的科学任务，待其自己的实际single/whole-policy读数审计后才可纳入。未修改science、cards、claims、论文、状态或旧封版；未运行GPU或commit/push。E122完整raw/几何审计见[独立报告](independent_review_2026-10-12.md)与[JSON](independent_review_2026-10-12.json)。

## 追加：C22/C23 的 §3/4/5 独立覆盖判断

作者另请求独立核对已有证据是否满足L3默认范围；此追加不修改CLAIMS、状态或科学读数。上文首次快照的等级登记仍是当时登记；本次判断依据新材料的直接实验，不以模型数量机械升级。

**C22的有界“固定输出身份时历史答案区域消息传入部分关联”、C23的有界“native判断依赖形成后的本来源证据与其它来源读取背景”，现已满足EXECUTION §3的L3默认覆盖目标。** controlled restaurant sentiment与official SST5 Movie-text benchmark是两种直接实测材料/benchmark，Qwen与Mistral至少两家族均有独立n32确认、CI、完整§4配对/采样/工具/方向与残差披露，并完成§5 raw独立复算；[E121独立审计](../e121/independent_review_2026-10-12.md)提供原始数据路径和数据provenance。C23还测E116真实MHS的功能margin；MHS private能力弱限制应用解读，不抹去已测条件margin效应。

C22 SST原生固定word答案KV的cross-vs-within绝对超额：Qwen .492799 [.279862,.764384]、Mistral .128272 [.056454,.212571] nats；signed分别+.330365 [.071195,.645114]、+.189633 [.116343,.274591]。Llama绝对超额正而signed为−.108988 [−.193868,−.023740]，不能把幅度改写成均匀正确修复。C23 SST signed formation×reading交互：Qwen **.767169 [.283069,1.244155]**、Mistral **.523852 [.377849,.672640]** nats；较大同族/其它家族方向与跨0完整保留。两类主张均有受控与自然材料的直接证据，不是由namespace成功或single能力间接外推。

若仍选L2，需明确这是更严格的人为范围判断：将两个benchmark的同sentiment范式只算一个任务家族。不能解释成没有跨benchmark实测或没有自然native/关联实验。§3写的是“≥2个任务/benchmark”，不要求必须换成完全不同语义范式；默认targets也不是自动判决器。采用L3时claim本身应写进controlled+SST及这些直接证据，而不是只改等级保留旧单材料主行。

L3范围**不包括**完整criterion运输/成功source isolation、真实人私人标准部署、所有checkpoint同一signed方向、唯一必要电路或无donor行为算法、普遍自然双来源政策repair。E122只支持冻结双方面任务中的政策功能结果；E123尚未完成独立raw校对，不能提前提供自然政策泛化。C24的固定Food-before-Service双方面criterion功能仍是单任务有界L2，本次不随C22/C23上调。grade不决定research状态、candidate/投稿资格，也不要求追加新实验关卡。

**作者修正复核：** §5.2现明确“selective and complete masks remove different numbers of edges and do not match attention mass”，并将比较限定policy-level functional consequences。上表第二项文字建议已处理；原始数值/科学范围不变。
