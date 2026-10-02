# E07：translate-train-reference（2026-10-02）

- **状态：** RUNNING（CPU审计通过；E04首格完整保存退出后使用空A100）
- **类型：** REPRO（标准translate-train竞争基线，不是新方法）
- **对应：** P03/P04
- **问题（一句话）：** 同一任务内容和有限更新预算下，直接把部分新任务监督翻译成目标语，比先提供无标签桥接能获得怎样的实际源/目标学习与保持代价？
- **设置：** MWB34K同起点。E03固定16384训练ID，每ID只出现一次；从E05预先审计合格的15442个官方德语译例中，用固定20261007随机顺序选择8192个，把对应英语单位替换为德语，其他8192保持英语。训练顺序用seed17，同E03 max1024、1024更新、micro2×8=16、lr2e-5/warm102/wd.01、FP32 master+BF16；答案only CE，无新的target-dev选择。先CPU产pool/manifest，GPU在同A100空卡上独立跑完整学习曲线。只跑一个标准50/50参照，不搜索比例。参数种子17，不是预训练种子复现。
- **读数：** E03相同0/128/512/1024更新点EN-dev/EN-test/DE-test官方generation F1/EM与item/context CI；终点相同一句instruction恢复。逐语言input/answer loss token、唯一ID/context、译料结构筛除、墙钟/保存时间分开。若比较MT保持，另记录原始完整LM、固定E06同协议并注明追加测量；不可装旧LM head。零CPT与E04额外CPT不是等总计算预算，不报虚假的成本最优。
- **阳性对照：** E03有效QA source baseline已通过；同scorer/tokenizer/hash；目标span非空且包含于全文、完整训练单位≤1024，不按测试表现选样本；source EN-dev终点F1≥50%作为有效学习门槛而非target门槛。有限loss与真实完整LM保存。
- **噪声地板 + MIE：** 单seed参照，不以item CI替代训练种子不确定性；约3 F1或清楚源语/保持代价为后续资源优先级，不自动升claim。所有曲线保留，不筛快照。
- **混杂审计：** 独立任务ID/语义覆盖与总更新数固定；50%英语监督被替换是实际预算选择，不是等英语exposure因果量。逐语言token/答案长度不相等，显式报告；机器译文与答案语义正确性未人工全面核对。过滤只用事前结构/长度，不用模型分数；父预训练single family，QA属extractive不能外推general reasoning。已有translate-train/XLDA ownership明确，无novelty升级。
- **决策表（跑之前写）：** 结构/哈希失败→不开GPU，修审计；完整source gate失败→参照未跑通，先审监督/优化，不据此否定翻译监督；正常学会且优于E04→无标签桥接必须面对这个竞争方法；源语或保持退步→记录真实多目标代价，再决定是否有足够价值设计最小训练救援；仅小差→不扩比例grid、不将其命名为idea。E04无论结果如何，本参照只用于建立有效竞争底座。
- **算力预算：** CPU准备；一次完整单A100训练≤2 GPU·时，白天总并用≤8。**实际：** 尚未运行GPU。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
尚无结果。实验卡写于CPU准备及GPU执行之前；没有因E04 target快照选择此参照。

CPU准备完成：同16384唯一ID，EN/DE各8192；input token1800246/2265387，answer loss token60412/63223。总input4065633，比E03全英语3588633增加13.29%，不是等token比较。manifest `results/e07_translate_train_data_manifest.json`，完整输入 `artifacts/qa_translate_train/data.json`；尚未GPU训练。

执行追加：fvcrc10 GPU0在E04 new_paired完整保存、原进程退出、显存15MiB确认后启动，PID78399；wrapper调用冻结E03 core，仅替换已审计的数据路径和真实哈希。上述“尚未运行GPU”是启动前记录，不是当前状态。暂未产生终点结果。

终点前追加测量承诺：标准50/50参照的完整LM，按E06/E08同Blackwell/FP32/全部400固定输入与primary/原一句instruction测MT保持，逐方向BLEU/chrF、照抄/cap/empty/overflow与同协议MWB适配前后比较。无新prompt，不挑QA快照；同句paired bootstrap2000、训练seed仍只有17。另用≤1 GPU·时，等E10全部post及空卡之后测；不是与E04等总token/计算预算，也不能据此宣布方法创新。此承诺写于E07终点和任何本参照MT结果之前。
