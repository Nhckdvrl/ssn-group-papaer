# If We May De-Presuppose（*SEM2025）

`[正式主文及方法/结果附录精读]` [正式稿](https://aclanthology.org/2025.starsem-1.20/)，Dipta/Ferraro，UMBC。14页PDF SHA1f9cc81295b0b6885808eac2b2e1c1504c9edb9e8437f27f7f95716eef81f788；main1–5及limitations pp1–5全部，AppA1–7 pp7–14全部；主表/完整结果/数据表 pp3/10/14视觉核。References仅定位入口；代码未读/未复现。

- **idea来源（RECONSTRUCTED）：** claim分解有时改善验证，有时无效→生成的问题自身把未核实成分当背景→再拆成存在/条件问题→reasoner基于证据逐步验证。最近邻是subclaim/QA分解，不是首次发现false presupposition；研究动作是分析分解接口引入的假设，而非增加更多自由推理。
- **方法/对象：** question decomposition→de-presupposition→verification，QwQ32B/Qwen3-32B/o4-mini，三种验证提示；不是训练新policy。App分解prompt只显示claim，而主文说使用claim和evidence：实现未核，保留这一不确定。生成问题覆盖率由Qwen3-32B judge对已有WiCE subclaim评估，提供evidence消解名词指代，不是独立人工证实所有问题无预设。
- **数据尺度：** WiCE358/247supported/111refuted（partially supported合并）；BioNLI5073/3962/1111；balanced BioNLI300；FEVER6605。主指标balanced accuracy；多数三次，full BioNLI及o4昂贵设置两次，标准差不是CI。
- **结果边界：** BioNLI可获较大提升，但WiCE在SG1/SG2去预设相对仅分解会下降；FEVER基本无收益。不能把“全部一致提升”当数据事实，也不能把方法与only-reasoner的提升全部归去预设。答案模块多数损伤，作者解释为中间错误传播，尚无唯一机制证明。
- **与I08距离：** 已拥有“问题假设污染证据处理／去预设能改善验证”的叙事。我们的普通Yes/No问题未必语言学上有同样存在预设，不能强贴术语；若只有问题诱导更错，增量弱。待测的是目标使requested accuracy改善同时同源自由解释中的明确错角色增加，以及一句问题/证据区分能否保收益、减损伤。这是尚待E98检验的定位，不是自动novel判决。
- **可迁移动作：** 同时记录目标任务结果与中间产物的错误关系，研究目标选择的代价；不照搬问题分解/多prompt刷点。一般question contamination已有owner，必须从完整数据提出更具体、重要的认识。
