# E36：原自然配对的一句强度指令恢复控制

- **状态：** DONE
- **对应：** C02/P02；R8先审elicitation，不在negative-strength局部反复修prompt
- **问题（一句话）：** E34自然解释强度/条件的错误能否被一句平衡的语义匹配指令恢复，还是仍主要由位置/入口控制？
- **设置：** E34同433 unique QA/218pairs/214questions/8端点/bare-commonchat/两个既定顺序。只加固定一句：Match both the yes/no direction and the strength or conditions of the answer; do not add or remove certainty or conditions. 原condition/Question/Answer与八label/hash抽样不动。原E34作为已完成paired parent，不新增数据、judge或挑26弱侧。
- **读数：** E34原全部metrics与support/ordering、paired strict-minus-original，按question分组；不挑恢复更好的readout/condition，也不改gold。不把指令后准确率当latent knowledge读数。
- **阳性对照：** E34 source audit/hash相同；原prompt差恰一固定指令，CPU all433×4×8、samefamily actual IDs一致；digit8单token；原FP32single sequence repeat首末gate1e-6，全量raw保留。
- **噪声地板 + MIE：** batch1/noTF32，同原2000/seed0/question CI。格式指令与语义指令不同，无generation/seed重复当独立样本。
- **混杂审计：** 指令可能shift任何label prior而非能力，应同时报告strong/weak accuracy、两个order及global支持质量。在同一subset不能从错误恢复推出普遍能力；自然humanlabel与finegrained语言区别仍须源语义分析。
- **决策表（跑之前写）：** Astrong/weak及两个order联合改善→削弱固有语用缺陷，记录instruction-accessible结果；Bweak升但strong降或单order升→bias/readout，不称恢复；C不恢复且顺序巨大→测量未识别，不继续在此局部换prompt/换label救story；D跨两自然材料/入口仍有稳定条件结构→后续第三family边界，当前不得升claim。
- **算力预算：** 8独立GPU锁×1732single序列，现有权重；FP32，无API/training/judge/子agent；≤2GPU时。Mistral权重下载等待不称实验。

## 结果
探索性后续由E34发现强顺序效应，但此对照的指令/全部选择/读数在运行前冻结；不修改E34原主读数。R8规定必须有一句恢复控制。此次控制有界：若仍是order/readout，无论数字多漂亮都不升能力claim，也不再靠修同一prompt持续局部优化。

原433源/preflight同family一致，通过后开跑。


## 完成与证据限度

八端点全部完成，1732/model，original/strict每条源字段、实际prompt SHA与token SHA全量复核，两个order共同汇报。负强度Q3-8 chat原序strict−original：强侧正确+.5769 CI[.3462,.8077]，弱侧正确−.5000[−.6923,−.3077]，弱被判强+.4615[.2308,.6538]；这不是恢复。14B强侧+.3077[.1538,.5000]、弱侧0，但order/入口仍影响。固定一句指令控制完成，不继续局部救分prompt。结果：results/E36-instruction-recovery-summary.json。

C01/C02仍L0；技术与原任务描述不升级为论文贡献。
