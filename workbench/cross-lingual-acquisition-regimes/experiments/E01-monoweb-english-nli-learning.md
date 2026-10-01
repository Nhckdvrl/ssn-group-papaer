# E01：MONOWEB 英语 NLI 学习→德语迁移（2026-10-02）

- **状态：** RUNNING
- **类型：** REPRO（标准学习 baseline，不声称新 idea）
- **对应：** P01、C03
- **问题（一句话）：** 有效任务学习后，FWB/MWB/MWB+P 跨语言学习曲线是否有值得训练干预追究的差异？
- **设置：** MONOWEB 三组 34K revision `4a42093acef06af33d2d5fdf2c26000d4f81d779`；MNLI revision `da70db2af9d09693783c3320c4249840212ee221`；XNLI revision `b8dd5d7af51114dbda02c0e3f6133f332186418e`。MNLI train 内 seed 20261002 固定划出 4096 源语 dev 与 32768 训练池；不使用可能含 XNLI 来源的官方 MNLI dev 选 recipe。标准化 premise/hypothesis 排除重复及与 XNLI EN test 完全相同的训练/dev 对，报告数；预训练污染未控制。原生分类头 + 全参数微调，末个有效 token pooling；长度256、batch8、累积4、AdamW lr2e-5、weight decay .01、10% warmup、clip1、FP32 master + BF16 autocast。FWB 英语 pilot 8192例/256 updates；完整曲线0/2048/8192/32768例，单次一遍不逐预算重启；适配 seed17/29/43 同 seed 跨条件头与顺序相同，预训练只有一个 seed。
- **读数：** 主 accuracy EN/DE 绝对能力，辅 macro-F1、混淆矩阵、源语损失、配对 EN-DE 差值；dev4096，XNLI test EN/DE各5010同实例配对并验证label；不只报transfer ratio。pilot仅EN dev，recipe freeze后才解锁test。
- **阳性对照：** FWB 英语 dev accuracy ≥55%，高于固定 dev majority baseline，三类均有预测且训练损失下降。step0 是随机分类头，不是冻结 LM 能力。门槛只判工具可测性。
- **噪声地板 + MIE：** 单seed二项Wilson CI；最终配对bootstrap10000次seed20261002，适配seed方差另报。target2pp是优先追查读数，不自动升claim；近噪声补预注册seed，CI跨零不作等价。
- **混杂审计：** 噪声待多seed；工具先源语gate；划分固定；同损失label；非prompt默认策略；输入/tokenizer hash一致；全报失败/seed；同例/token预算另报时间；train/dev/test pair排重但预训练污染未控；不事后选切片；不以源语gate替代目标语gate；单家族、单预训练seed不泛化全部reasoning。
- **决策表（跑之前写）：** FWB pilot通过→保存仅EN recipe freeze后比較三条件；失败→不解锁DE，检查baseline，任何recipe修订先amendment再跑，禁止挑DE；有后果差异→完成适配seed并定位先行工作后做最小训练干预；不明确→报分辨率与源语代价，不追加冻结probe；工程失败→记录修复不作科学结果。
- **算力预算：** pilot≤2 GPU·时；三条件单seed各≤4 GPU·时；三适配seed上限36 GPU·时，先实测再扩展。独立单卡，白天九点后同时≤8张。**实际：** 待测。

## 结果（仅追加）

源语pilot完成；三条件与预注册适配种子比较进行中；无论文claim升级。

启动前补充（2026-10-02）：数据准备完成，MNLI train 排除134个重复对、与XNLI test完全重叠0个；实际4096 dev/32768 train/5010 EN test/5010 DE test，hash见 `results/nli_data_manifest.json`。pilot使用完整1024-update schedule的前256步，后续三条件仍从原始权重重新开始。同一份recipe不因测试成绩改动。命令：`python scripts/nli_learning.py prepare`；`CUDA_VISIBLE_DEVICES=3 python scripts/nli_learning.py pilot --condition baseline --seed 17`（fvcrc20，conda openslime）。metrics/pair标准化单元测试与语法检查通过。

源语结果：0/2048/8192例的独立EN dev accuracy分别32.84/50.02/77.78%；8192例Wilson95%CI[76.48,79.03]%，macro-F1 .7781，loss .5659，三类预测1519/1451/1126；majority34.94%。通过预注册工具gate。有效运行242.75秒（不含Python环境import），峰值GPU27.04GiB；完整loss/provenance/预测在 `artifacts/nli_learning/pilot_baseline_seed17/`，轻量结果 `results/nli_pilot_baseline_seed17.json` 与 completion。`results/nli_recipe_freeze.json` 锁定脚本hash、数据hash、仅EN开发读数及recipe；未用DE成绩选择。

按决策表启动三条件全曲线：fvcrc10卡0/1/2分别baseline/monoweb/onlyparallel seed17；fvcrc20卡3 baseline seed29；fvcrc10卡3 monoweb seed29。最多5张同时，占用现空卡。其余seed29/43在这些任务完成后复用空卡，不扩大Cartesian product。

硬件分配修订（2026-10-02，看到的seed29 Blackwell输出仅step0/训练前64步日志，未读取其训练后target成绩）：主分析九个cell统一使用fvcrc10 A100；已启动baseline seed29 Blackwell运行完整保留为hardware replica，不按成绩筛选。完成后单独命名保存，在A100复跑该cell。配置、输入、头、停止规则完全不变；分析器要求同硬件，额外一轮仅为分配匹配。

输入校对：另取原作者XNLI-1.0 ZIP，与HF5010条EN/DE的原文和label逐条精确对照，原始pairID序列一致且5010唯一。已通过 `scripts/audit_xnli_pairs.py`；结果hash见 `results/nli_xnli_pair_audit.json`，不只用label相同推断配对。

POST-HOC校对备注：固定pair-disjoint source holdout并非premise-group-disjoint；4096 dev有702条与train共享premise但hypothesis不同，XNLI EN test有3条共享premise，完整pair重叠仍0。开发集Wilson CI只作描述，不冒称严格独立premise泛化；source学习还在未用于recipe选择的XNLI EN test得到确认（seed17≥82%）。XNLI5010 pair对应1670独立promptID，原预注册item bootstrap保留，追加promptID cluster bootstrap为相关性敏感性分析，不据此改主读数或筛种子。
