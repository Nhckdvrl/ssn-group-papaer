# E43：crossed-truth-commitment-parent（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / D1–D2，原human理论实验的LLM协议迁移，不預设failure
- **对应：** C02/P09
- **问题（一句话）：** 同一自然utterance中，两层事实证据怎样分别改变literal/implicit speaker commitment与总体trust；模型是否能保留原human的目标对象区别？
- **设置：** OSF unmy6 Exp2原8dialogues×四truth corners；八图逐一目视转写，保留source typo与turn order，原context/actual event/问题，E40 703human/64commitment条件逐字段匹配且原lm系数parity。十既有端点、八GPU锁，完整same-family tokenizer/bare-chat。原64commitment+32trust=96ratings×original/一句balanced clarification×两入口；初始无event的8comprehension及两层actual-event truth verifier各32，共528calls/model、5280全部。FP32单sequence/noTF32，greedy/max16，完整raw/ID/LP；不是new gold或judge。
- **读数：** 整串整数numeric：commitment1–100，trust0–100（原PsychoPy trust tick0–100）；原human均值/valid全行上下界、四corner与每target simple effects按8item bootstrap2000 seed0。comprehension/verifier整串Yes/No casefold，不从prose抽取；invalid单列。保留人类原条件化correct-understanding norm，不据模型错误过滤样本。不是同一proposition的通用SDT。
- **阳性对照：** 初始comprehension原pretestYes/No与actual-event两个层次的source真值程序gold；原source/human64逐字段对齐、所有corner齐全、703原norm、同familyactual输入SHA相同。首末numeric及每binary task首末重复IDs/LP<.001；prompt逐项hash。
- **噪声地板 + MIE：** fixed greedy无samplingseed，8item数量限制必须报告，CI只材料。complete numeric可用性优先，不把invalid变能力错误；不会只选成功case计算效应。source图转写尚无独立人类校对，最高L0观察，不能L3。
- **混杂审计：** 文本迁移省略截图UI时间/图形，不称精确human原实验重演；source摄影图只含两个text bubbles，无自造semantic。输入原Excelcontrol/newline可见显示解码，raw source保留；不按gold补造对话。原human commitment后才问trust，本LLM freshcalls，history不同须记录。Implicit commitment问题用预试dominant interpretation（原human正确解释后），这项是retrospective attribution，不自动测prospective intent或action planning。truth verifier给明确target含义只校背景事实读取，不喂到初始comprehension。后训练bundle不能因果拆SFT/RLHF。
- **决策表（跑之前写）：** A背景fact读取和初始理解有效、分target条件结构人类一致→保留强成功baseline；Bverifier正确但目标分离不同且两入口/一句控制稳定→候选observations，再Exp3更广材料/独立转写/ownership审；C一句指令恢复或numeric unavailable→elicitation边界，不能力finding、不继续prompt修复；Dsource/verifier不成立→不解释commitment差异。任何结果都不自动关territory。
- **算力预算：** 5280独立greedycalls、16token上限、十模型按八卡锁，与E41/E42共享锁；已有模型，无training/API/judge，预计<3GPU·时。先CPU完整输入/源审计，后GPU；不是为占满卡复跑已有数据。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
开跑前协议补充：balanced clarification 固定为“Evaluate the requested target separately: what the speaker committed to conveying, whether the reported facts are true, and how reliable the speaker is are distinct judgments.” 不指示结果方向。事实 verifier 的两条 target claim 直接取原 true/true actual-event 的两个分句，仅送进 verifier，不送进 comprehension 或 ratings；这是事实读取对照，不是新语用 gold。重新查看全部八张原图，转写一致；仍无独立人类校对。逐段核对 PsychoPy 的实际 Flow，trust 原锚点为 0 (No) / 100 (Yes)，已在 GPU 开跑前更正；旧 CPU preflight 保存在外部资产中。源准备/CPU gate进行中，尚未模型结果；C01/C02仍L0。

分析协议（摘要计算前冻结）：整串合法但未EOS的数字单列，主四corner效应必须全部八材料完整结束；有缺失则报告全八项上下界，不筛材料作点估计/CI。CI仅原八材料bootstrap；不包含人类参与者不确定性。全部目标/clarification/入口联合报告，探索性多比较不能当confirmatory finding。

2026-10-03 十端点5280calls全部完成，source/fullinput/raw-parser/config/重复gate通过，见 results/E43-commitment-parent-summary.json。聊天Q3-14B facts64/64、初始meaning7/8；OL SFT61/64、8/8，DPO57/64、7/8；Q25Instr60/64、4/8。MistralInstr理解8/8但facts仅53/64、原literal/meaning/trust complete numeric仅2/1/11（各32），不能计算筛后科学效应。Q3-14B分target四corner全32有效；balanced clarification改变评分幅度，尚无两入口/跨family可靠能力结论。全部缺失bounds、所有条件/八itemCI保留，未筛材料救故事；初始Mark理解错误也保留。原human literal truth对implicit commitment在implicit true时效应21.34 CI[8.85,32.84]，因此不能把human规范写成两层完全独立，或把模型任何跨层效应都叫脑补。C01/C02仍L0。
