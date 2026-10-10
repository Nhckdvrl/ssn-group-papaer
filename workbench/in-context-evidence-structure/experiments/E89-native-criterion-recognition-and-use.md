# E89：原生对话中识别标准与使用标准是否一致？（2026-10-10）

- **状态：** PLANNED，首次评分前冻结。
- **类型：** PILOT诊断。
- **对应：** I04 / C16 / C20 / P13。
- **问题（一句话）：** E88的隐式判断弱，首先是没推断出评判标准、没有有效使用它，还是raw接口使判断变弱？
- **设置：** 同Qwen3-8B revision与conda，float32/eager；16新contexts seed89001，复用E88 confirmation短语池（不是词汇独立确认），各source四极性demo、16新评论。采用模型原生chat template、enable_thinking=False；system要求推断并遵循requested source，评论只答positive/negative，标准问题只答food/service。base/criterion-flip/explicit/explicit-flip四条件，不训练，不选层，不进行新patch。
- **读数：** 标准识别accuracy（两Source，测试评论未给出）；评论判断四极性accuracy及相反极性accuracy、标准flip的双向logit响应。读取第一token，在每个合法词的大小写及leading-space单token变体上logsumexp；同时报全词表argmax是否为合法答案及其准确率，避免候选空间掩盖格式失败。按context bootstrap95%CI，10000次固定880。
- **阳性对照：** 显式说明各Source标准；原生chat system是一句明确推断/使用来源标准的指令（R8）。同context改变Source的标准，名字固定；类别和标签频率平衡。E88原始raw读数保持独立，跨接口对比不是只改变单一机制的因果实验。
- **噪声地板 + MIE：** 第一context batch-vs-single logits≤.01nats，否则VOID保留；MIE以识别/判断差≥10个百分点作为投资启发，不作科学有无的门槛。数值通过不代表能力已可靠。
- **混杂审计：** 列举food/service选择是提示行为测量，不能独立证明内部存在可部署criterion；识别问题和评论问题有不同输出词/计算需求，不据行为差异宣称因果桥梁已定位。新contexts全保留，不筛好seed；材料与E88确认共享词池、措辞风格仍受控合成，单模型；原生chat同时改变角色与指令，不将恢复归给某一prompt token。
- **决策表（跑之前写）：** 识别和判断都强→E88弱native不作不可组合证据，下一机制实验应在这个可正确完成的自然任务接口中检验标准/证据关系；识别强判断弱→具体的标准识别与执行分离线索，但需机制证据、文献正面对齐；两者都弱而显式强→先承认从demo推断困难；全部弱→限定材料/接口，不能研究已知规则部署。任何结果都不扩head/position矩阵，不改正式线状态。
- **算力预算：** ≤.25 GPU·时。**实际：** 待填。
- **命令：** `CUDA_VISIBLE_DEVICES=0 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/e89_native_criterion.py --model /tmp/ices_models/Qwen3-8B --out results/e89/qwen3_discovery --n 16 --seed 89001`

## 与主问题／已有解释的关系

E88得到的是有界迁移分离，隐式native在discordant query约51%，不能证明已可靠识别规则。E89用两种自然问题消解这个实际解释歧义，不把它设成整个ICES的新资格门槛。JIT/Lepori/TR-TL已经研究可识别与可用状态，单纯行为识别/执行差异不是新意；新规则从多个来源demo推断，须在可靠接口上进一步让来源标准与recipient证据给不同预测。

## 结果（运行后追加）

待运行；E87保持未运行。C16/C20不升级。
