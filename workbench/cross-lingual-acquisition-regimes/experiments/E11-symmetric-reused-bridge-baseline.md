# E11：symmetric-reused-bridge-baseline（2026-10-02）

- **状态：** PLANNED
- **类型：** REPRO（修复不完整的桥接竞争基线，双向训练不是新方法）
- **对应：** P03/P05
- **问题（一句话）：** 修正单向桥接的方向偏置后，同内容双向paired或split训练对真实新任务学习与双向旧能力各有什么收益和代价？
- **设置：** 原MWB34K同起点和E04固定reused池4096独立context、每条两遍、总8192；第一遍EN→DE、第二遍DE→EN，恰好替换原第二遍的顺序，两个语言的每个token/唯一ID/总预算不变。只做symmetric paired/split两条件，不增加新内容覆盖/比例grid。两条件的每条顺序、位置、labels、seed17的shuffle完全相同，仅attention跨文档连接开关不同。相同256 CPT更新、max2048/micro1×32/lr2e-5/warm26/wd.01/FP32 master+BF16；之后冻结E03全16384英语监督、1024更新及全部曲线/一句恢复，真实LM head共同训练。QA评测和recipe不改，target结果不选配方。
- **读数：** CPU逐ID/语言token/重复与输入hash核对；双向mask检查及128固定holdout的双向conditional NLL（仅诊断）。完整CPT/post LM保存后，按E06/E08同Blackwell/FP32/固定400句/primary与原一句instruction测双向BLEU主、chrF辅、照抄/cap/empty/overflow；同句paired bootstrap2000。QA同官方generation F1/EM、0/128/512/1024曲线、item/context CI及EN绝对表现。报告paired−split、E04同内容单向条件和零CPT参照的绝对数；不筛快照，不报只看旧能力的保持比。
- **阳性对照：** 已有E03有效QA学习、E08同硬件协议1200/1200复现；每个语言顺序下split logits对前文扰动不变、paired有影响。CPU内容/预算任一不一致不启动训练。终点EN-dev F1≥50作为工具gate，不是科学判决。
- **噪声地板 + MIE：** 仍为单CPT+适配joint seed，E09适配种子噪声与本卡不可混用成CPT CI；约3 BLEU方向代价/3 F1学习代价决定下一训练干预优先级，不自动升claim。item CI不替代训练seed，news/extractive单任务边界保留。
- **混杂审计：** paired/split内文本、位置、预算、loss mask控制；与E04 forward-only相比语言位置及条件方向共同改变，不能说只操纵抽象alignment。attention FLOPs未相等、reused来自同域且非所有dev标题排除、MT语义未全人工核对、单parent family均保留。无语言标签/translation instruction加入，不把plain-document CPT说成现代MT instruction baseline。JGP已研究方向反转失败、OpenSeal/JGP用双向组织、NiuTrans有多路重复退化；本卡只是必要竞争底座。
- **决策表（跑之前写）：** 双向baseline明显改善旧方向但新QA不变→确认重要训练选择的分工，面对标准replay/译监督再做最小训练干预，不命名现象；双向仍有明显适配代价→时序/任务目标干预比更多frozen prompt优先；若QA/MT都受损→审计完整loss、优化与数据格式，用有效parent配方继续修baseline，不宣布领域失败；若仅小差→不扩这个顺序grid。任何结果均不自动抢novelty或关闭workbench。
- **算力预算：** 两个单A100 CPT→QA pipeline各≤2 GPU·时；四完整LM MT测量各≤1 GPU·时，最多8 GPU·时（含预留I/O）；白天并用≤8。**实际：** 尚未运行。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
卡写于E10完整结果之后、任何本卡数据准备/训练之前。E10是选择修复direction基线的发现依据，不能把本卡回写为其事前预测。没有新idea或claim升级。
