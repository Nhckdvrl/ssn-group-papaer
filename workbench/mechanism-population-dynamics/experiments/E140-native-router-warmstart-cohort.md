# E140：同一原生路由初态，允许继续学习是否仍稳定分解（2026-10-26）

- **状态：** RUNNING；04:04:20 UTC三新seed在独立GPU启动；预登记在初始化/训练前，E139已完整独立审计。
- **类型：** PILOT；只补一个区分机制的条件，不追拟合分数。
- **对应：** P27：E139的teacher-gate/frozen与random-gate/trainable协议差，尚未分开共同初始组织与持续冻结的作用；承接P26、C08历史选择问题。
- **问题（一句话）：** 完全相同的原生gate/随机expert初态下，解冻gate继续联合学习，是否保留固定分配组的跨训练分解稳定性？

## 设置：三个全新prospective运行、一个新条件
- 只新增teacher-gate initialized **trainable** cohort，expert seeds预定0、1、2，全保留不筛选；参考fixed三学生(E136/E138)、free三学生(E135/E139)明确复用旧运行。新组以seed1为预定公共对齐锚。
- 逐seed从对应fixed **initial.pt的完整FP32参数值**初始化（step0、fresh optimizer、未训练expert）；expert和gate逐值证明与对应fixed初态相同。gate允许梯度/更新，不加router-KL、teacher逐expert监督或额外loss。恢复该初态的RNG并记录；全部参数fresh AdamW。
- 同原生OLMoE L9 frozen prefix/downstream、64×1024/top8/no-renorm，同cache manifest SHA `2c95a706ab9d70609de565e1d141b33a7ae0f7b5805686caf0165147ce7dfc43`，8,388,608训练位置×4固定epoch=33,554,432位置曝光，4096更新。相同原E135全参数训练：固定train-energy normalized MSE+.01LB+.001z，AdamW(.9,.95),eps1e-8,wd.1,clip1,peakLR.0003,10% warmup/cosine，9个固定MSE事件，不取中途最佳，不续训或加超参条件。
- **混杂审计：** 新组vsfixed有完全相同初始参数，差异为允许router梯度/aux与full-parameter clip/decay的**解冻协议**；不称只有边界变化的纯机制。新组vsfree同时改变共同gate初始化与teacher-informed初始化，不能把二者拆开归因为教师信息本身。单模型/单层/有限cache/三模型有限cohort，非自然预训练结论。

## 读数：沿已冻结E139真实程序，无新matcher
- 原Dolma held262144位置为主，原POS held512目标为次；actual full-row gate/selected子batch/BF16乘积，native aggregate与FP64 component sum的数值floor分列。
- 给定三学生等权1/3，先报告不依赖对齐的native总Y teacher误差=共同bias+跨学生variance，及完整自然预测teacher→学生、三学生对KL/NLL/top1。POS真FP32末位head，Dolma BF16 logits→FP32 logsoftmax分开，全部结果保留，无函数距离或恢复准入线。
- 只用原training-side native Hcal8192整批B16×512，以actual gated component（当前未选为0）未中心化/缩放的平方距离，Hungarian到本组seed1。固定cal映射到held；仅统计重标，不物理重排参数，不另试U/route/尺度/旋转标准。全64 cal cost、支持/零承担/局部tie保留；该锚定不是全joint最优或穷尽所有对应。
- 主向量读数为同单位component cohort variance、FP64 sum cohort variance、cross covariance，报告与fixed/free两组的连续点差及同输入file/word cluster的1000次seed139配对bootstrap区间，非seed总体CI，不以区间重叠作判决。沿E139原定义和输入权重，不将全expert行中心化后的A当内容向量。
- 完整初态与E139 fixed initial逐值相同，因此**预先允许SHA耦合复用**其initial cal maps/raw component统计（同Hcal/held/physical program/全参数），明确注明复用而非新forward；final需全部fresh采集。旧fixed/free final raw以SHA引用，CPU重加对照，不重跑旧模型。
- 辅助final POS自然贡献A全部三个新学生fresh采，只有上述final cal-component映射。对照旧fixed/free相同映射A，fixed identity另保留；zero-target支持明确报告，不删列或称64个独立内容证据。initial A不作为新增前置要求。
- 辅助路由变化沿原施加的物理expert行解释，不能把final cal component映射当自然路由身份。
- 辅助路由状态：固定cal/held上与初始teacher的实际mask重叠、应用门值差和各自支持覆盖；无预定阈值判断“gate几乎没变”。用于解释分解，不以路由代替内容。

## 阳性对照、噪声地板 + MIE、决策表（跑之前写）
- CPU已知答案：初态全张量/无optimizer状态/曝光0；复制fixed初态的forward/统计可耦合复用；tiny完整/断点训练及gate确实可更新；不同支持零散射、cohort variance双恒等式和paired输入CI沿E139自检，原复制/归约floor保持。
- 不设任意MIE/性能/rho门槛；报告三组完整函数差、分量差及区间，有限cohort描述不冒充所有初始化总体。
- 若新组分量稳定性接近fixed，且路由确有变化：初始共同组织可能已足以约束本预算内的分解，不需全程严格冻结；仍不能分离共同随机gate与teacher特定信息。
- 若新组向free靠近：持续固定组织约束有作用，不能概括为只提供初始信息；router优化/aux/clip耦合仍需保留。
- 若只总函数误差/variance随协议变化：分配与内容/函数共同变化，不隔离同函数自由度。任何混合/反向结果都保留，不追门值尺度/epoch/LR/seed网格。
- 所有分支都不自动升级主张/论文状态或开关线；下一动作按证据/问题决定，不为凑覆盖运行。
- **算力预算：** 新增≤1.5 GPU·时（训练+读数+失败尝试并发加总），独立E140 ledger；fvcrc21空闲GPU三条独立单卡训练，最多4卡/全探索≤8，数据/权重本地NVMe，共享原cache，不复制70GB H/Y进git。

## 结果（运行后追加；以上登记保持）
- `e140_train.py` SHA `1b1c81afa1e2177029c3296324bc6be3dd7c53ad304fcde694ecbd5d81c02f07`冻结；CPU tiny完整/断点/三个真实schema fixture通过，node21三个实际初态的CPU预检通过，继承RNG都含一个visible CUDA state。
- 04:04:20 UTC在fvcrc21 GPU0/1/2实际启动seed0/1/2，PID884887/884888/884889；独立ledger `/tmp/xiang-moe-20261025/e140_budget.json`，原缓存/六旧模型/旧预算不变。首批真实更新均正常，无设备故障；固定4096/全部终点仍在运行。
- E139有限cohort结果用于提出本区分问题，非E140结果。
