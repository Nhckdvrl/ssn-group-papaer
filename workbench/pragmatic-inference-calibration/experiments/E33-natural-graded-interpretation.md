# E33：自然间接回答中解释方向与解释强度

- **状态：** DONE
- **对应：** C02/P02；D1/D2原human substrate驻留，不把校准指标当贡献
- **问题（一句话）：** 真实训练阶段或更强端点改善间接回答的yes/no方向时，是否也更接近人类对definite/probable解释强度的判断？
- **替代解释：** A方向理解改善与强度一致性共同提升；B仅更容易选definite且方向未改善；C方向与强度改变不同，依赖原自然来源；D词汇/结束token/聊天入口主导，读数无法支持能力归因。
- **设置：** Potts作者2011 IQAP公开更新版215项，原150 DEVELOPMENT全部源序，65 EVALUATION不送模型。30原human responses/item，四原选项definite/probable×yes/no。原Question/Answer逐字、保留removed Prefix仅metadata、不复原带前缀文本。8端点Qwen2.5 Base/Instruct、OLMoE Base/SFT/DPO、Qwen3-4/8/14B，原pinned weights；两个入口bare/common-chat，完整common tokenizer固定于每族。原human问法加一句完整解释句格式要求；不是2010论文224项/5类、不是原Web算法复现。
- **读数：** 主读数四完整原解释句+terminal suffix总logprob归一分布；保存content-only LP（预定次读数）与缺QA的固定null词汇诊断，不用null结果重新挑主读数。yes方向概率、human同方向分布、模型/人类definite总概率及conditional-on-human-majority-polarity definite概率（仅human该侧>0.5，ties单列）、四类Brier/JSD、polarity MAE/正确率；不把human意见分歧、模型输出概率与speaker含义强度当同一不确定性，不作SDT/FPR。
- **阳性对照：** 原150完整计数皆30、Item唯一，原sum/类别/source hash全量检查。CPU预检所有prompt/四completion严格prefix以及content boundary、family actual IDs parity，不使用数字选项。两接口首末单序列重复full/content LP差<1e-6才允许全量。主推断始终单sequence/no padding，避免已知MoE batch组成混杂。源最大一致项仅instrument对照，不删除错误、不中途换prompt。
- **噪声地板 + MIE：** FP32/noTF32、batch1；首末数值重复gate。CI bootstrap150item（同Source重复的依赖另报告source cluster敏感性，不能把30人独立重复模型），2000/seed0；每来源CNN/Yahoo/Switchboard/Hirschberg全报，no挑最好来源。干净stage内paired delta，size端点不是纯scale因果，无训练replicates。
- **混杂审计：** 这是metalinguistic human-task readout，不是latent next-token语言知识。2011版去掉Uncertain会强迫选择，不把人群分歧叫不存在意图。原选项语言/顺序固定且同族target IDs/长度不变；suffix读数与content-only、null、bare/chat须一起解释。common chat不等于base原生熟悉协议；两个家族不等于8独立families。2024 TACL已拥有Circa人类标量校准/模型大小排序，2026 Social Meaning已拥有方向/强度分解；此矩阵仅寻找原对象边界，不claim新measurement。
- **决策表（跑之前写）：** A两入口方向与强度同步改善→记录strong baseline，不救criterion故事；B方向改善同时definite偏离且两入口/content都支持→待跨自然材料验证具体条件，不立刻机制；C来源/阶段反转→回到自然关系与证据条件，拒绝统一倾向；D仅suffix/null/入口变化→仪器或elicitation证据，不把强度偏差升级能力。任何漂亮effect先全量源/LP/human counts审计。
- **算力预算：** 8独立单卡任务×150×2×4完整序列，FP32 single sequence，GPU0–7文件锁，不用API/training/子agent；剩余E28锁释放后接上，不杀他人进程。

## 结果

2026-10-03解释校对：原候选“probably meant Yes”是对意图的解释确信度，不等于说者表达了“probably Yes”。不改变预先声明的读数；跨任务的speaker certainty解释不成立，须分别描述。
跑前冻结。原数据/PDF/完整token plans、预测置外部工作目录；代码与派生summary进git，保留所有失败。未知是自然解释方向与语义强度是否分离，不以某个hypothesis必须成立为目标。

CPU全量预检通过：8端点×150×4×2 strict prefix/content boundary、三family内actual token hashes完全相同；65 evaluation未送模型。


## 完成与证据限度

八端点全部完成150原DEVELOPMENT×bare/chat×4完整候选，65EVALUATION未入模型。Q3 chat polarity accuracy 4B/8B/14B=.6133/.7333/.8533，definite概率−human=−.5192/−.5064/−.0978。不支持统一过度确定。缺QA null：8B P(probable-yes)=.999915，14B P(probable-no)=.999140；完整terminal对Q25Instruct bare强度差+.1216变成content-only−.1367。full/content/null均保留，不选有利口径；人群分布不是单模型认识不确定性。完整结果：results/E33-natural-graded-summary.json（item bootstrap及Source-cluster同estimand敏感性）。

C01/C02仍L0；技术与原任务描述不升级为论文贡献。
