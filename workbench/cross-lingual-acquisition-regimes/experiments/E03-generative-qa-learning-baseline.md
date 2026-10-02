# E03：英语生成式QA学习→德语迁移的有效基线（2026-10-02）

- **状态：** PLANNED
- **类型：** REPRO（第二种学习substrate，不为配额挂idea）
- **对应：** P04；E01仅NLI分类接口不足以支持生成/知识学习母问题
- **问题（一句话）：** MONOWEB模型能否真正学会生成式extractive QA，以便后续训练决策不只在分类头上验证？
- **设置：** FWB/MWB/MWB+P 34K原始LM，HF revision继承E01。SQuAD `7b6d24c440a36b6815f21b70d25016731768db1f`；XQuAD `51adfef1c1287aab1d2d91b5bead9bcfb9c68583`。SQuAD train按title分组，seed20261003打乱，前32 title为source holdout，取512例；剩余选16384训练例；全文+答案≤1024的训练/source dev例才入池，测试不按gold或长度筛选。排除XQuAD test context/ID重叠；EN/DE 1190同ID及EN原始SQuAD来源核对。全参数LM、答案token-only loss，固定 `Context/Question/Answer` newline模板，prefix/full token边界断言；greedy max64输出，按首newline/EOS停止。micro2×8 effective16，lr2e-5/wd.01、1024 updates/warmup102、clip1、FP32 master+BF16、seed17。FWB source pilot512 updates/8192例使用完整schedule前半，仅EN holdout；通过后冻结recipe，三条件从原始权重重跑全曲线0/2048/8192/16384例，target不选recipe。pilot可用Blackwell，主三条件同A100。
- **读数：** 主官方XTREME SQuAD F1，辅EM；固定同scorer用于EN/DE，明确仍只移除English articles。官方scorer源码commit `838c13b69daafb9328785d16caae2711e4012123`并记hash；不手写近似评分。全预算点EN/DE、source损失、answer cap/context overflow/空输出比例。终点补同一短指令“Copy a short answer from the context.” EN/DE恢复对照，主模板/读数不因它改变。所有超context测试项计0不丢弃。source和target分布CI用固定bootstrap10000，另报context cluster，初始仅seed17不升L2。
- **阳性对照：** FWB英语source F1≥50%、EM≥35%、training loss下降；标准scorer例子/完整prefix boundary/caching长度检查。该gate只判真实学习可测性，失败不说明整个语言能力不存在。pilot不解锁DE测试。
- **噪声地板 + MIE：** 512 source dev、1190 target，source article-disjoint但题目按context聚集，报cluster敏感性；seed17仅baseline，未有QA适配seed方差，不能从NLI SD搬过来。约3 F1或明确source/target代价是扩展优先级，不是判决；若要承接科学主张预注册29/43与独立任务干预。
- **混杂审计：** 原LM head共同训练，不把NLI classifier接回原LM head评遗忘；同数据、tokenizer/输入hash、训练recipe，真实generation而非冻结likelihood。源码/scorer/模型固定；目标不选停止规则、完整失败保留。单预训练family/seed与污染未控；source按title disjoint避免E01 premise重叠，不追改E01结果。prompt默认由终点一句指令对照界定，不将它单独当能力证据。
- **决策表（跑之前写）：** EN source通过→冻结仅EN recipe，开展同硬件三条件；EN失败→先修有效generative baseline，任何训练修订写amendment，不看DE挑；有效QA且E02出现有后果数据差异→将桥接干预接入第二任务，另卡明确识别量；没有区别→保留合理分辨率和能力范围，不局部优化分数、不关领域。
- **算力预算：** source pilot≤3 GPU·时，三条件seed17各≤4，总首阶段≤15 GPU·时；E02四卡外仅一空卡source pilot，总并用≤5，白天≤8。**实际：** 待测。

## 结果（仅追加）

数据准备完成：16384 train / 512 source dev / EN-DE 1190同ID。source article-disjoint及XQuAD英语原始来源全文核对通过；预先排除6条超过完整训练长度上限的单位。数据/scorer固定hash见 `results/e03_data_manifest.json`。准备过程中的来源核对字段误命名为xnli，训练前更正为xquad；不改变任何输入hash。尚未训练；不预设德语迁移方向或新idea。先source gate，再沿实际训练失败探索。
