# E34：Circa自然同问句的不同承诺强度

- **状态：** DONE
- **对应：** C02/P02；D1/D2原human驻留；E33补充自然条件边界
- **问题（一句话）：** 在同一个问题下，模型是否区分自然回答中的明确否定、可能否定和有条件同意，而不是把所有偏向同一方向的回答压成同一强标签？
- **设置：** 原Circa34268行全部CPU审计，取同context/Question、各自5/5原human一致的两原回答。三contrast：No/Probably no全部26question；Yes/Probably yes-sometimes yes原123取hash顺序首64；Yes/Conditional Yes原742取hash顺序首128。只按源标签/固定hash选，不看任何模型结果。每侧hash首一原回答，重复QA去重；pair manifest保留，不强造同utterance contextflip。原八选项/原human问法、bare/common-chat、原序/逆序。与E33同八stage/size端点，fullcommon tokenizer，FP32单sequence，关闭thinking。
- **读数：** 原序八数字raw restricted next-token概率、global候选support mass/argmax；逆序固定control一起报，不事后选择顺序。每类primary mean gold概率、argmax correctness、强/弱两个原label的相对概率；paired same-question weak-minus-strong probability变化。Conditional yes被误选Yes与Probably no被误选No单列，而PY含sometimes不称纯不确定性。bare/chat、顺序效应按question全报。
- **阳性对照：** 所有34268 id唯一/每项judgement长度分布/标签在原8类内，原strict gold majority规则全量复算；每个选中QA5/5一致。CPU全量digit1–8单token、render/token hashes同family相同；原human counter/permutation source不动；固定首末single-repeat概率差<1e-6后全量。
- **噪声地板 + MIE：** noTF32/FP32/batch1/无padding，重复gate；2000/seed0按question cluster（重叠question跨contrast同采样），不以不同原回答当独立question；No/PN26范围小明确，不用大量seed救。reverse只有一个control不称穷尽位置偏差。
- **混杂审计：** 同问句控制question内容，但两回答不同语义/长度/难度，不是单变量causal intervention。一致human subset不代表所有原population，也不等于世界事实真值。没有licensed/unlicensed二值gold，不作FPR/dprime。数字MCQ仍metalinguistic，原始support不足或order翻转先归readout，不能解读latent知识。Circa2020已报告PN69%误为No，通用overcommitment与新openweights排行不是贡献；新颖性要来自跨自然材料/真实stage的条件结构或重归因。
- **决策表（跑之前写）：** A强弱及条件同步改善→strong baseline，不维护bias故事；B同方向正确提升但weak/conditional向strong坍缩、两入口/两顺序稳定→继续追自然证据范围与跨family、未达finding；C只有一种原弱标签变化→报告边界，不能无限局部修prompt；D顺序或support主导→仪器/elicitation，退回territory的许可对象，不称能力。E33与E34无论结果不能直接合为同因果尺度。
- **算力预算：** 8独立单卡、每模型选中uniqueQA×4 atomic单序列，E33每模型完成后GPU锁接入；所有已下载权重，无训练/API/judge/子agent。原raw外置，错误保存不覆盖。

## 结果
实验开始前冻结三contrast/抽样/读数。保留原问句、人类counts、回答、context与pair manifest；原gold未重新标注。源语义强度与pop分歧不同，E34单独识别自然内容边界，不能把所有有条件同意当"不应该推断"。

首次CPU全量预检停止：20/34268原项只有4judge，34248项有5，不补人类标签。原gold majority(≥3)仍逐项核对；只在5judge项中选择5/5一致材料，原20id写审计文件。预检失败发生在任何GPU或模型结果之前。

CPU预检通过：34268原majority标签全部匹配；选中433 unique QA、218 contrast pairs、214 question groups。8端点/4入口原序与逆序/三family内actual input IDs一致，所有digits单token。


## 完成与证据限度

34268源majority逐条核对，20行仅4human判、全部保留audit但不入5/5unanimous抽样。433unique/218pairs/214questions、八端点1732/model完整。Q3 conditional chat原序weak正确4B/8B/14B=.9375/.9141/.9375，强baseline能保条件。负强度小端点巨大order effect：4B原序No正确.8077、ProbablyNo正确.1154，逆序.0385/.9231；不是可直接归latent over-inference的finding。完整source/gold/token/parity通过；自然两个回答同时变化内容/长度/难度，非单变量许可操纵。结果：results/E34-natural-paired-summary.json。

C01/C02仍L0；技术与原任务描述不升级为论文贡献。
