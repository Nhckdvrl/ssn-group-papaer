# E09：qa-adaptation-reliability（2026-10-02）

- **状态：** DONE（全部训练、保持评测和统一分析完成；权重随后按用户授权清理）
- **类型：** REPRO（真实学习baseline的适配种子重复，不是冻结probe扩展）
- **对应：** P04/P05
- **问题（一句话）：** 源语QA真实学习相近但已有翻译代价不同，是否跨优化/数据顺序种子稳定，而不是一次任务适配的偶然副作用？
- **设置：** E03三原始完整LM及固定16384监督、source recipe/scorer/QA instruction对照全不变，追加适配seed29/43、所有三起点完整跑，禁止只选+P或MWB。直接调用byte-identical `scripts/qa_learning.py train --condition {baseline,monoweb,onlyparallel} --seed {29,43}`。A100独立单卡；保存完整LM和全部曲线。随后在E08相同Blackwell/FP32/400固定WMT16输入/primary+原固定一句instruction上测post，每次记before/current哈希。训练前不需要target选择。
- **读数：** 原E03所有预算点EN/DE F1/EM和终点instruction；三适配seed均值±SD，各seed完整读数。固定翻译集BLEU主/chrF辅、source copy/cap/overflow、post−同硬件before各seed与paired item CI；seed方差单独报，不能与预训练seed复现混同。不挑中间快照或把有利source表现当pure transfer。
- **阳性对照：** E03 source gate及所有三起点有效任务学习；先E08同硬件原模型校准，不让协议差异带入六训练。真实LM head与backbone共同训练，不重接旧head。
- **噪声地板 + MIE：** seed17是发现样本，29/43全量新增验证，不筛种子。三seed不足以严估尾部风险；实践优先级约3 BLEU/清楚照抄增加，不自动claim升级。单句恢复失败不证明知识删除。
- **混杂审计：** 适配recipe和训练集固定、只改共同训练种子；单预训练family/seed、数据质量与原始MT强弱差异仍未独立控制。主MT样本仍200 news/方向，不能外推所有语言/领域/模型规模。无“parallel防遗忘”先定因果解释；目标词表/输出语言偏置/copy技能与接口变化竞争。
- **决策表（跑之前写）：** E08环境差解释主要下降→不启动、写降级；代价保留→完整六次训练，不筛条件。跨seed实际代价稳定→最小同起点训练救援并与E07等实际决策参照比较；不稳定→保留P05为未定，不扩大评分/比例grid。只有基线/系统测量与定位后请人判断yield，不自主关线。
- **算力预算：** 六个独立A100学习各≤2 GPU·时，总≤12；六post各≤1，总≤6；训练/后测分开记账。白天总并用≤8，与E04/E07按空卡顺序推进，不杀其他作业。**实际：** 尚未运行。

## 结果（跑完后填写；不改上面的内容，修改需注明日期）
无新结果。卡写于E06发现之后、E08结果与新增训练之前，明确区分发现和验证；不是旧八轮的第九个冻结压力测试。

E08校准通过：primary1200/1200与legacy一致，MWB同instruction下降仍在。新增训练启动门槛满足；等E04已启动A100完整保存/退出后使用空卡。wrapper只顺序调用冻结core的29/43，启动前检查原A100设备/core hash；不改recipe。尚未新增GPU训练。

资源执行追加：E04全部完成后GPU1–3被其他作业占用，未杀归属未核实进程；排在fvcrc10 GPU0的E07后。`queue_qa_repeats.py`必须看到E07 core和wrapper两份完整保存记录、显存占用低于512MiB，才顺序运行全部三起点各29/43，不能按目标结果跳条件。等待不计训练GPU时间；queue仅启动门槛，不改变recipe或种子。尚未产生新种子结果。

空卡变化执行追加：后续实测fvcrc10 GPU1/2/3各15–16MiB且无compute进程，取消本题仍在等待的单卡queue，改为GPU1 baseline29→43、GPU2 monoweb29→43、GPU3 onlyparallel29→43。这是资源映射改变，全部六次/recipe/readout/停止规则不变，未读新增结果选条件。本题与E07及E10最多并用5张，未终止其他研究作业。旧单卡queue脚本保留但不再运行，避免重复训练。

完成与资产清理追加（2026-10-02）：三个起点的全部seed17/29/43 QA完成，新增六次MT的primary/instruction全部完成，队列输出ALL_LEARNING_REFERENCE_READOUTS_COMPLETE并退出；fvcrc10/fvcrc20相关Python进程核对均不存在。统一结果results/e09_qa_reference_analysis.json包含9组、72项聚合，results/e09_retention_reliability.json包含9组、24项聚合；保留逐seed/读数/不确定性，不筛选条件，不在此次存储清理中升级主张。用户要求完成后删除，故最后9个完整LM checkpoint亦已清理；数据、原始预测、曲线、hash和完成记录保留。总GPU时间尚未统一核算，不将包含评测/I/O的elapsed当纯训练GPU账。

验证价值摘要：三适配seed的MWB primary英→德BLEU变化均值-2.92、适配seed SD0.56；德→英-4.04、SD1.07。同instruction均值-2.49/-4.42、SD0.15/0.94。三组德语QA F1均值FWB/MWB/+P为63.10/63.30/63.55。支持P05并非仅seed17偶然结果，不识别一般alignment损失或parallel因果保护；固定单预训练family/seed、extractive QA、每方向200 news仍是边界。只有有限重复验证价值，没有新论文idea，不据此追加训练。
