# E14：跨语言与模型的选项顺序混杂审计（2026-10-03）

- **状态：** DONE
- **类型：** REPRO / D2 measurement control；不以prompt效应作能力证据。
- **对应：** C01、P03；给E02/E07/E08的maxim/literal差与elicitation对照划边界。
- **问题（一句话）：** 已观察的读数差在实质选项位置平衡后是否保留，还是答案符号/位置主导了测量？
- **设置：** 已固定revision的Qwen2.5-3B、Qwen3-4B两模型×四语言，每格原300题×四cyclic rotations×native/format两readout；第三Qwen1.5-14B同四语言作尺度/旧parent对照，不称独立family。A–D轮转，E none-of-the-above固定在末尾，避免改变above语义；其余字串保留。n每格2,400，共28,800读数；每original item只有一份独立刺激。无新数据、label、训练或judge。
- **读数：** restricted letter概率映射回原semantic choice；原各240maxim/60literal分别报四position accuracy、均值、semantic argmax invariance、format paired变化。按原item bootstrap2000 draw seed0；rotation不是随机训练seed。rotation0与E08原读数逐项核对（第三14B无旧E08），不将不一致静默合并。
- **阳性对照：** 全项逐内容permutation/inverse断言，gold按mapping正确迁移，rotation0 prompt字节不变；每job固定首末项batch1/8 prob delta<1e-3，不通过停止。FP32/TF32关闭，thinking关闭；旧结果不覆盖。
- **噪声地板 + MIE：** 无解码采样，位置变化是测量读数；CI以原item为单位。只有控制后的可重复领域结构值得后续，位置偏差本身不是论文贡献。
- **混杂审计：** MCQ symbol probability仍metalinguistic；E固定让E正确项不能全位置平衡，必须分开报告其比例。不把literal错选当FA，不用异构任务差计算SDT。格式指令为现有E06控制，既可能改变输出倾向也可能改变解释，不能称纯format干预。
- **决策表（跑之前写）：** A原排序/两侧差与format变化保留 → 削弱单纯位置解释，仍需语义/难度/许可审计；B变化被order平均吸收/反转 → 降级受影响的读数解释，优先测量边界；C只个别语言/模型 → 保留全部格，找边界，不救单点故事；D gate/mapping失败 → 技术失败，不能升级finding。
- **算力预算：** 8卡先两模型×四语言，完成后4卡接原14B；每卡独立≤80GB，总≤1GPU·时。E12下载队列重新排在已运行jobs之后，不抢同卡；实际runtime保存在config。

## 结果
跑前冻结。此次用现有权重填上下载等待的空档；问题是检验现有测量是否可信，不能为了占卡虚构实验。
