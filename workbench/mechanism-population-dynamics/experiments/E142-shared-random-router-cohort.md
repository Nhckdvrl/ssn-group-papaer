# E142：共享一个随机路由起点是否也稳定专家分解（2026-10-26）

- **状态：** RUNNING；04:48:46 UTC新增seed0/2已启动，预登记在新初始化/训练前；E139–141完整并独立审计。
- **类型：** PILOT；一个新初始条件，非拟合优化。
- **对应：** P29/C09：共同native初态同时提供共享起点与native特定几何，二者尚未分离。
- **问题（一句话）：** 让独立expert初值共享同一个未训练random gate、继续联合训练，是否也能稳定本有限cohort的实际分解？

## 设置与配对
- 新组S的expert seeds固定0/1/2；seed1完整复用已观察E135，只新增0/2，全保留不筛种子。S/R共享同一seed1整模型，cohort和三对不能当独立seed样本。
- 0/2取对应R(E139) initial.pt的全部expert FP32值与各自torch/numpy/python/CUDA初RNG，只将gate换成E135 seed1 initial.pt的原始FP32随机gate。逐值证明expert/RNG不变、共同gate完全相同；不统一三个RNG，不copy训练过的expert，不将旧seed1伪造为新运行。
- 同原生OLMoE L9 frozen prefix/downstream/总H→Y，cache manifest SHA `2c95a706ab9d70609de565e1d141b33a7ae0f7b5805686caf0165147ce7dfc43`；8,388,608训练位置×4原epoch顺序，4096更新/33,554,432位置曝光。原全参数normalized MSE+.01LB+.001z，AdamW(.9,.95),eps1e-8,wd.1,clip1,peakLR.0003,10%warmup/cosine；gate全程trainable，9固定MSE事件，不取最佳/续训。
- 对照R各自random gate、T共同native gate可训练、F共同native gate冻结均引用原运行。S只检验这一份seed1 random gate，不泛称所有随机起点。S−R改变共享关系/具体gate值；S−T改变random/native具体初态，尺度、margins、边界与语义信息仍未分离。

## 读数：原Dolma人口，单一cal规则
- 主群体原Dolma held262144位置/512序列/32文件，native full B16×512 gate/selected子batch/actual BF16乘积。初态/最终4096都报告无对齐的nativeY teacher误差=共同bias+cohortVar，以及actual componentVar、FP64sumVar、cross及数值floor。三学生1/3，teacher不作第4学生。
- 只用原training-native Hcal8192整批B16×512，actual gated-component未中心化/缩放平方距离Hungarian到本组seed1；每phase一次，held锁定映射，仅数据轴重标。全64 cost/count/tie/零承担保留，不加U/route/gain/旋转mapper，锚定不穷尽所有对应。
- 从原raw作S−R、S−T、S−F点差与1000次seed139同file配对输入CI，非seed处理效应CI；旧分数/区间不变，不用CI重叠作判断。
- 原Dolma自然预测teacher→三学生及三student pairs双向KL/NLL/top1全报，沿BF16 logits→FP32 logsoftmax、固定窗口/targets，不设函数恢复准入。此次新增人口仅Dolma，旧POS/A保持。
- 辅助gate变化相对本组共同初始random gate：top8集合重叠、actual gateweight L1、支持counts，按物理expert行，不混用finalcal身份。全参数/源/数据/映射SHA及曝光保存。
- S/T各自内部稳定不单独证明它们是彼此不同的最终组织，更不证明同函数多解；本次先回答共享起点是否足够，不加cross-mapper/第四gate/温度网格。

## 阳性对照、噪声地板 + MIE、混杂审计、决策表（跑之前写）
- CPU：expert/RNG逐值同各自R初态，仅gate替换；gate精确等原seed1 random初值；fresh optimizer、tiny完整/断点一致、gate可更新、旧资产不变。向量/cal/variance/pairedCI沿已审E139定义，copy/归约floor单列，无科学分数/MIE门槛。
- 若S也较低变异：这一个共享random起点已能稳定本学习问题，native来源不是本例中稳定的必要解释；不外推所有gate或不同最终分解。
- 若S偏R而T较稳：这一个native起点有额外作用，保留尺度/margin/边界等解释，不独归语义知识或立即加网格。
- 若中间/反向/函数拟合也变：连续报告联合差异，不设等价带/恢复线、不挑seed；任何分支不自动开关线/升论文状态。
- **算力预算：** 新增≤1.5 GPU·时，独立E142 ledger（全部阶段含失败加总）；fvcrc21两独立单卡/原NVMe cache，最多4卡/全探索≤8；旧seed1/模型/HY均引用，不进git。

## 结果（运行后追加，以上预登记保持）
- 训练源`e142_train.py` SHA `155001f774c76ad906e40f5571163411243d9f260c9575a5f6d992c2b1e12829`冻结。CPU完整/断点已知答案与node21两实际初态预检通过；各自expert/RNG保留，只替换FP32 gate，fresh全参数Adam，旧状态不变。
- 04:48:46 UTC在fvcrc21 GPU0/1实际启动seed0/2，PID895454/895455；独立ledger `/tmp/xiang-moe-20261025/e142_budget.json`，原seed1不重训，原4096终点不变。尚无新终点结果。
- 这是看到E140/141后的新前瞻控制，非修改旧主读数。
