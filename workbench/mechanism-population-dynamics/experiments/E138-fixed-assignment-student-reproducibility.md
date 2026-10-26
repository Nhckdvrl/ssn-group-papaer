# E138：固定分配与总函数目标下，三个独立学生之间什么会重现（2026-10-26）

- **状态：** DONE（完整训练、读数与独立审计；原预登记协议保留）
- **类型：** PILOT / REPRO；回到跨训练对象，不再把teacher恢复当准入，不改E130/E135–137原读数。
- **对应：** P25：student–teacher的共同偏差与student之间的变异尚未分开；承接P23/P24。
- **问题（一句话）：** 同一teacher gate/总Y目标/缓存与预算下，独立重学模型的总计算会比实际expert分量更可重现吗，还是两者一起重现/一起变化？

## 固定有限cohort与训练
- **三个学生：** E136 seed1作为**已观察pilot复用**，另预定新增expert初始化seed0、seed2；三者不是全prospective样本。不得按任何拟合/职责分数选择、替换或丢seed，不再扩为5seed/追拟合阈值。
- **唯一新变量：** 新两seed的expert FP32初值（原TensorMoE init_std=.02、同构造器/顺序）；gate均为同native teacher BF16原值→FP32并冻结，保持64×1024、top8/no-renorm。seed1原初值与终点/预算不可改。独立记录各expert-only初值SHA及共同gate SHA，expert初值不同不是expert坐标置换。
- 原E135 cache manifest SHA `2c95a706ab9d70609de565e1d141b33a7ae0f7b5805686caf0165147ce7dfc43`；相同8,388,608 H/Y位置、相同四个seed135 epoch排列、4096更新/33,554,432 optimizer位置曝光。相同总Y/固定train-energy归一MSE+.01LB+.001z、expert-only fresh AdamW(.9,.95)/eps1e-8/wd.1/clip1/peakLR.0003/10% warmup/cosine。
- 原生public prefix/downstream全冻结，未监督逐expert输出/语义标签。与E136一样，aux无直接expert梯度，fixed gate与移除router/global-clip耦合是既定条件；这不是自然预训练。
- 每512步固定train/held MSE、完整4096、optimizer/RNG/gate检查与曝光记录；不换最佳中途checkpoint。不为了与teacher接近到某阈值延长或换超参。技术错误保留记录，不将错误seed静默筛掉。

## 主分析：精确三模型有限cohort分解
- **主群体：** 全Dolma held H32×16×512=262144位置，当前native support覆盖全部64专家；NN前向/actual BF16门值乘积/selected子batch/row order沿E137。只读联合forward是必要的，旧teacher-relative SSE不能重建学生之间cross inner-products。
- 对三个实际native输出Y_s，取等权1/3算术mean（仅统计reference，不是新部署ensemble）：
  `mean_s ||Y_s-Y_T||² = ||mean_s Y_s-Y_T||² + mean_s ||Y_s-mean_s Y_s||²`。
- actual gated component c_{s,e}也按相同1/3分共同teacher偏差和学生间变异。对每学生FP64 sum of actual BF16 components单独做reference，
  `Var_cohort(sum_e c_e) = sum_e Var_cohort(c_e) + cross_covariance`；BF16 native aggregate/FP32或FP64统计归约残差单列，不把rounding叫expert相互作用。
- 比较**同一vector单位**的collective变异与分量变异/协方差，不用rho除KL。teacher是fixed reference，不是第4个学生；不把3个共享seed pair当独立n，也不将1/3有限cohort量冒充全部seed总体方差。
- 每个初值/固定终点都联合测量（仅已有states，不训练新条件），保留全64 count/energy/误差/方差充分统计；无on样本记未定义，不删expert。原生gate/支持应逐项同teacher；不学新对应/旋转/gain，不做off-support完整64单专家注入作为看结果的前置条件。
- 同POS held512目标位置的vector分解为次要群体，用原B16 padded序列native子batch与精确Htarget，不以Dolma替代。POS experts42/51/52当前target-on=0，原始A恒0、row-centering会继承共同均值；报告coverage，不称64个独立内容证据，不事后删列改旧分数。

## 原生预测与任务作用
- 所有三个学生相对teacher及三个学生对的完整自然预测距离/GT NLL/top1，沿原Dolma BF16 logits→FP32与精确POS真FP32末位head两条精度路径，分开报告。不按距离大小决定是否做内容比较。
- POS自然贡献A作为辅助任务读数：seed1复用E136 fresh-A；新增两seed只需沿原full-row slot与no-renorm drop实际加权贡献采A，known identity对应预定且全保留，原cal word-offset/held隔离保持。无新cal-U/route/输出matcher网格，不为另做全部U注入消耗预算。解释时不把继承全expert均值的未覆盖列说成内容恢复。
- 原始逐序列/逐expert统计留本地，小摘要含全部学生/3对、输入/权重/代码SHA。POS word/Dolma file的1000次seed138输入cluster bootstrap只是给定cohort评测不确定性，不是seed CI；不从数据挑代表seed或输入。

## 已知答案、预算与解释分支
- 三个完全相同学生的变异应为0；三个共有偏差的相同学生可有teacher误差但cohort变异0；相反component偏差可有分量变异>0而sum变异0/负cross。CPU已知答案验证统计与行索引，实际copy/数值floor沿已有E137及新联合程序明确记录。
- **新增预算≤1.5 GPU·时（全部阶段加总）**，fvcrc21独立单卡作业并行最多4卡/全探索≤8；优先两新训练并行，数据/模型本地NVMe，独立E138 ledger，不动E135–137记录。不重建H/Y、不加LR/aux/seed/teacher-target网格。
- 若学生总Y/预测变异小、但实际分量变异由负cross抵消→这3个模型可以共享同一偏置近似的不同实现，仍不叫严格同函数或数学不可识别性证明。
- 若总Y与分量都重现→目前student–teacher差主要是共同偏差，给定分配/函数目标后可出现canonical近似内容；不将teacher未恢复误判成跨训练不重现。
- 若总Y也明显变化→函数与分解共同变化，保留有限预算/特征学习解释，不声称隔离出分解自由度，不自动延长训练。
- 所有结果均不自动开关线/升论文状态；单teacher/单层/有限cache/已施加组织信息限制完整保留。C07/C08原限定等级不变。

## 结果（运行后追加）
- 新seed0/2固定4096全部完整，held fixed-train-energy MSE=.156717298/.156534285；seed1复用E136=.156779633。
- Dolma mean teacher误差/共同bias/student variance（nativeTeacher能量归一）=.162563352 [.147391511,.177986028] / .148547890 [.134473783,.162628385] / .014015462 [.012754876,.015422240]。
- 同vector²单位component variance=.031208956 [.030497592,.031890822]，FP64 sum variance=.015947143 [.015449800,.016365020]，cross=−.015261813 [−.015859641,−.014598048]。POS相应=.036913420/.017823811/−.019089609；不与上述归一量直接相除。
- 三学生自然Dolma pair KL=.008730334/.008823162/.008845247，top1=.9594/.9591/.9589；identity A=.484816 [.379012,.570740] / .526466 [.404301,.604819] / .499266 [.315910,.622938]。POS42/51/52无target-on，原列全部保留、限制解释。
- 主文件`results/e138/readout.json` complete/errors空；`results/e138/independent_audit.json`独立复算统计、CIs、全部实际CP/exposure/逐步LR输入通过，无GPU复跑forward。全部4096 step/batch/LR三个学生逐项相同，gate不变、expert初值不同。
- 解释：teacher差主要是共同偏差，部分分量变异相互抵消；目前不是严格同函数自由度或唯一分工证明。C07/C08不变；按预定分支补匹配free cohort（E139），不追加恢复网格。
