# E142：共享一个随机路由起点是否也稳定专家分解（2026-10-26）

- **状态：** DONE；训练、全部Dolma读数与独立审计完整。用户随后要求暂停新增实验并整理，原预登记保持。
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
- 04:48:46 UTC在fvcrc21 GPU0/1实际启动seed0/2，PID895454/895455；独立ledger `/tmp/xiang-moe-20261025/e142_budget.json`，原seed1不重训，原4096终点不变。启动时尚无终点结果；最终完整结果见下文。
- 这是看到E140/141后的新前瞻控制，非修改旧主读数。

### 最终结果与独立核对（暂停快照）
- 两新seed0/2均4096完整，held固定train-energy MSE=.170330199/.170648526；seed1复用E135=.169350162。全部9事件、所有seed保留，没有续训或取中途最佳。
- 三组独立证据齐：`initial_independent_audit.json`逐值证明只替换gate、192expert及各自四类RNG保留；`training_independent_audit.json`核实际新终点/Adam状态与11个不同运行的固定orders/LR/exposure；`independent_audit.json`重算cal、raw组件双variance恒等式、三组paired输入CI、6预测pair和route rows。全部在`results/e142/`，非作者CPU审计，无主统计导入/GPU重跑。
- 读数源`e142_components.py` SHA227fa786…570e9f2、`e142_readout.py` SHA3680818b…f80af999冻结；完整终点preflight在run()内、select_gpu之前执行一次。`readout.json`全components/predictions complete、errors空。新增只测Dolma，没有新增POS/A。
- 初态R/S componentVar=.129445689/.129586911；最终S=.043261927 [95%文件输入CI .042166570,.044191263]，FP64sumVar=.016036914；cross=-0.027225013。S−R componentVar=−.029205269 [−.031120653,−.027909625]，sumVar=−.001832563 [−.001951869,−.001744559]。
- S−T componentVar=+.010444301 [.009505025,.011338638]，S−F=+.012052972 [.011278556,.012870387]；完整原始差值与所有seed/文件读数都保留。输入CI只给定这份cohort，不当seed总体/处理效应CI；R/S共享同一个trained seed1。
- nativeTeacher能量归一的S平均teacher误差=.176265554、共同偏差=.162165321、学生间方差=.014100233；R teacher误差=.176401906。相近平均拟合不能声明函数等价。S三学生对Dolma KL=.008179565/.008318280/.008336895，teacher→学生=.042678496/.042465585/.042750894。
- 最终cal maps的identity数为60/62；相对共享random初gate的top8保留=.221588/.222526/.224545。该保留率按原物理expert行计算，不能据此断言忽略初终全局置换后的分区重组，也不拿它代替主要终点cal对齐读数。
- 实际总1312.509864 GPU秒：**2次新增训练+1次readout，共3成功作业**，无失败，seed1没有重新训练。完整durable archive位于`~/mechpop_cache/e142_shared_random_router`；清单`results/e142/archive_manifest.json`，大模型/HY与旧R/F/T只引用。
- C09等级保持L1。共享这一份random起点降低本cohort的actual分量变异，尚不证明所有共享gate、S/T之间不同最终组织、严格同函数或普遍语义分工。用户要求暂停，后续方向与未执行用途讨论待人决定，不自动继续。
