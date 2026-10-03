# E63：原知识理由怎样传播到瞬时与持久评价（2026-10-03）

- **状态：DONE。** 完整卡先于source展开/CPU gate/GPU；E61完成后汇总用于解释，E63独立parent协议不预押方向。
- **类型：REPRO / D2。** C02/P02/I01；不是新metric或机制贡献。
- **问题：** 同一off-topic回答，其原知识自述改变时，模型对当次交流和持久人物评价是否按人类条件结构改变？同时检查是否准确读到了改变的自述。
- **设置：** Beltrama/Papafragou2023原E2的scene1–14×Ina/Unw×High/Low=56场景条件；原四trait问句/1–7 scale。E62在任何模型输出之前发现scene15缺reason分隔、scene16缺informativeness括号，暂不展开；全16human norm保留，不按effect择项。source1–14的reason/body/info分别按原PDF markup展开，公开拼写错误保留；仅移除版面引号、+Info标签与折行；scene6原缺respondent标签，根据intro明确为Ken，记录添加。这是公开规格的声明迁移，非原运行UI精确复现。
- **读数：** 四traits complete numeric+EOS probability、mean rating、human norm距离；主读数原Ina−Unw条件差，以及durable−temporary两trait的reason差的差。n=14 scene bootstrap2000seed0，按informativeness分开/平均均报，不以更多rows冒充n。另每条件对两种reason原字串分别问“是否确实说了这句”，Yes/No，完全平衡阳/阴用于原字串读取，**不把它冒称语义知识能力**。六targets×56×原/单句×bare/common-chat=1344natural/model，加36number/binary reference-copy=1380，8共11040。
- **阳性对照：** 原人类source差异/四字段/count全部核对；每条件两原reason quote controls与copy1–7/Yes-No。单句固定E61 impression指令，两入口/all条件全报。原trait四问分别限定in-conversation/as-person，保留construct差异。完整tokenizer/native backend/source/numeric FP32batch1/eager/noTF32 gates；每alias/interface/kind首末独立full logits及repeat。
- **噪声地板 + MIE：** LP/prob差<.001、repeat<1e−6；rating条件差与human差≥.25且sceneCI支持才改变解释优先级，非自动判决；单checkpoint无training seedCI。human发布每cell20–30人；不把其rater异质性当模型内在confidence。
- **当前解释：** A合理地按理由/评价目标区分；B不区分实际证据、主要用表达/人格先验；C能读字串却目标评价映射不同；D入口/尺度/候选不支持任务。C不自动证明知道但不用，quote读取不是完整reason语义理解。
- **混杂审计：** reason改变的是目标证据本身，off-topic body/info固定逐项hash检查。无照片/增量7秒UI、原人类问题顺序与模型独立query不同；public规格不完全等于运行字串；跨实验lexical差异不合并因果。stage算法/数据/budget共变、family不同，均不单因果归RLHF。完整candidate质量与null分字段报告，词汇prior/人口分布不等于内在belief。只用E2内配对，不把E1/E3独立participant当同人。已读人类文献拥有conditional target结构；仅迁移模型不足新颖性。
- **决策表（跑之前写）：** A结构保留且读数可靠→记录成功，查独立precision/实际知识证据迁移；B/C跨family稳定且读取成功→先同尺度human/query与理解语义审计，再对独立现象检验边界；D质量失败或单句翻转→报告未识别，不加第三prompt救此substrate；source gate失败→0实验预测，修技术或停相应source，保留失败。结果都不自动升C02/I01，不以训练相关性宣布机制。
- **算力预算：** 八独立cached模型/单卡锁，≤4GPU·时，0训练/权重下载/闭源judge；不杀已有进程、不覆盖旧run。

## 结果
11040/八模型完整，2.90012GPU·时；256独立full-logit/repeat数值控制通过，source/actualinput/全概率算术校对通过。[完整结果](../results/E63-violation-reason-summary.json)。

原chat Ina−Unw四trait人类差：Knowledgeable−.1248 CI[−.3105,.0572]，Considerate+.5497[.2924,.7988]，Competent+.5700[.3659,.7586]，Likable+.5446[.3706,.7226]。OL SFT/DPO/最终的Considerate差分别−.3629[−.6398,−.1211]、−.3338[−.6391,−.0530]、−.3659[−.6756,−.0782]，Competent−.9506/−1.0127/−1.0138；原/单句、full/content同向。MistralInstr原chat Considerate−.6885[−1.0478,−.3600]，QwenInstr+.1284[.0341,.2465]。这些是实际理由条件下的不同评价响应，不是没有任何变化；Qwen的成功方向也保留。

解释未识别：原chat字串quote准确 OL三post-stage .500/.518/.509、QwenInstr .554、MistralInstr .688；不证明成功读懂后误用。Mistral单句full quote .964但完整mass仅.185、content quote .884，不能挑full最高作语义gate。全部chat copy对，但copy不足验证自然控制。Base读数支持低，stage算法/数据仍共变；trait词/frame与原UI迁移等限制不变。

按D/B记录候选条件现象而非机制升级。E64用全部相同common-chat实际prefix直接生成（原/单句、全场景与四trait/两quote），验证restricted likelihood/terminal与实际回答，不换第三prompt、不救此source排名；若相同quote控制仍不可靠，回源语义/UI核查，不继续优化本probe。C01/C02仍L0；C03仅独立E59任务观察L1，没有E63能力/机制claim。

跑前技术补充：第一次CPU gate因PDF的Jeﬀ连字与Jeff人名不一致阻断，0模型预测。统一NFKC还原印刷连字（不改语词/拼写），列入rendering指纹；不把PDF提取伪影当模型理解错误。trait null按场景保留同原人名/问句共224框架，只作量尺先验诊断，不声称已消除先验。quote两个原字串均保存，literal-reading不是理解动机语义的充分控制。

解释边界补充：两种trait同时改变属性词与momentary/durable frame，不能把差的差单因果归“过度泛化到人格”。primary scene CI未bootstrap人类rater（原same人16scene相关）；公开human counts保留，正式推断需要subject/item双来源校对。不给多切片显著性自动升级。

汇总前补充（未读取任何E63效应）：增加secondary human participant bootstrap2000/seed0，按93个人整体重采样保留同人跨scene相关；与primary scene CI分别报告，不冒称joint/训练种子CI。四traits的reason人类差、fixed-model差及Brier敏感性保留；target-interaction尚无对应raterCI，不据此formal机制推断。
