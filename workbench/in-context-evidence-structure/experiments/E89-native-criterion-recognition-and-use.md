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

## 初版结果与明确请求／完整回答协议（再次评分前冻结）

初版源码`f6e72024…`（d54e2605），原结果`results/e89/qwen3_discovery/`保留；数值误差.000217、139.34秒。但人工读实际argmax发现，explicit的256个评论请求里181个首token为food/service大小写变体。system同时定义两种回答类型、user只写`Label:`，形成真实的请求类型歧义，不能把22.3%的合法Label argmax准确率当标准应用失败。仅第一token也不足以测完整回答。隐式识别50%，显式96.9%的初读数暂只作诊断，不升claim。

修订使用同16contexts/seed89001，全部条件保留，不换幸存seed；输出`results/e89/qwen3_clear_request/`。system仅要求从示例推断各人的标准、回答用户问题；每条application显式问“What is Alice's judgment of this review? Answer exactly positive or negative.”，recognition显式问该姓名评判哪方面、只答food/service。原生chat、thinking关闭不变。

每条请求完整greedy生成最多32新tokens；保存原文与EOS截断标记。读数增加完整回答accuracy：只出现一个合法候选词类型时识别其内容（大小写无关），两个都出现/都不出现记unknown，所有context仍入分母；另保存exact-word与第一token，报告parse和截断比例。未完成/unknown不能直接当能力缺失。protocol中的原读数继续报告，修订是POST-HOC诊断，不称独立确认。追加预算≤.25 GPU·时，整卡≤.5。

命令在原命令上加`--clear-request --generate`，out换为上述新目录。先冻结修订再运行，不由prompt恢复直接声称新机制。

## 完整回答的预算续完（运行前冻结）

明确请求版本完整生成后，base/flip/explicit/explicit-flip的评论回答分别23.05%/28.52%/8.20%/9.77%仍在32-token上限截断。实际样例是正常的分析前言，尚未输出判断；不能把它们计成能力错误。标准问答均完成，但表现依请求而变，初版explicit 96.9%的first-token识别在修订请求下不保持。不给“知道却不用”主张升级。

此次只将所有未完成的回答续到最多512新tokens；same16contexts、全部条件、greedy、同原prompt与原batch分组。重新执行含截断样本的原batch，要求新的解码文本以旧截断文本为严格字节前缀；已完成的旧回答保持，不筛正确性、不生成新材料。完整保留32-token原结果。输出`results/e89/qwen3_completed_answers/`，剩余截断仍报告unknown/未完成，不推出能力缺失。这个前缀控制是文本字节检查，未保存旧token IDs，不冒称token轨迹严格证明。

预算追加≤.65 GPU·时、整卡≤1.15；脚本`complete_e89_answers.py`首次运行前提交。最终只做完整读数汇总及研究判断，不在本卡继续增加请求变体或位置控制。
