# E163：成熟职责中的消息几何、方向结构与跨背景重用（2026-10-28）

- **状态：** COMPLETE（2026-10-29）。四端点各16条件、LM64/RC128与实际消息27格全部完成；原设计19f6f3a5，数值源c31e4b0e，科学条件不变。独立29650项数值/1376项元数据复算通过，最大差1.42e−14。完整raw与来源见[manifest](../results/e163/manifest.json)，C14保持L2。
- **类型 / 对应：** PILOT；C14、P33。用户全局再定位后明确授权继续。
- **问题（一句话）：** 成熟历史与伙伴改变的R/S依赖和配套，能否由消息幅度/残差投影解释，还是仍需要输入条件的其余向量方向？

## 从母问题到本实验

已有实证不是只有routing：E155/E162同样成功的分担变化，E156性质载体与必要伙伴分离，E159同函数作用变化，E160实际S轨迹原配收益。它们尚未识别哪些消息特征需要配套。领域已有Monet的编辑、Standing Committee真实mask、stitching/LMC与Hydra/Dose/WISE条件干预；本项不重新发明这些一般概念，而是解释成熟组织下的实际角色和重用。领域位置/备选动作的取舍见[PAPER_SHAPE](../PAPER_SHAPE.md)。

新训练seed/更多层扫描不直接区分上述解释；单独旋转随机向量后网络受损也不够。因此本项同时保留native历史测量，以及同一S_P函数、同一输入的实际跨背景消息，后者是更有结构的重用检验。

## 固定资产、输入与范围

- 复用已核验P/A/B/F固定HF pin、架构/tokenizer/同active k；P/A/B为同声明谱系，F全程EMO，不当独立初始化总体或时机单变量。
- LM：E150原64窗口、512计分位置、20源文件簇；原target mask全部保留，不重选输入。RC：E153/E155原生物/数学各64题、4候选及原提示/评分。旧held是已探索输入，不冒充全新确认集。
- 两个独立cal序列使用E150原cal前2份128输入；与目标窗口/RC分开，固定可见位置mask。只估计各层R、S、R+S消息均值，不用held损失选proposal或超参。
- 每层proposal还包括两个固定Gaussian向量，seed163101/163102、跨模型同维度共用；它们是工具探针，不是训练seed。全部报告，不挑最好者。
- R/S均为16层函数套件，R+S为每层整个MoE增量，不声称已识别单expert或最小组。

## 干预：保留什么、替代什么

层内原始FFN后残差为`H + R + S`。选目标消息u为R、S或实际BF16的R+S；背景b为FFN前残差与未改分支之和。R/S替代保留另一支内生计算；R+S替代的b仅含FFN前残差。

- `norm_mean`：把固定cal均值方向缩放到当前原始u的L2 norm。
- `gram_mean`：用cal均值的b正交方向，保留r=||u||与p=<u,b/||b||>，构造`v=p*b_hat + sqrt(max(r²−p²,0))*unit(d−<d,b_hat>b_hat)`。
- `gram_random0/1`：同一构造，但d为两个预定Gaussian向量。
- u=0、b=0及d平行b用预定有限回退，保存次数；不以目标效果选回退。计算FP32后回到原dtype。`sqrt(r²−p²)`以原正交残量的norm稳定求值（实数等价）；proposal逐向量与witness完全相同时直接保留该向量以实现精确identity，规则不依赖效果或Tensor别名。退化方向只用固定basis/现有b，不泄漏u其余方向。

Gram构造在实数下保留u的norm、对背景的投影和b+u的norm；实际BF16加法次序与误差实测。局部参照来自当前路径的u/b，并未锁住clean全程norm轨迹或最终gain。它保留的是**两个输入相关标量**，仍可能承载丰富信息。即便恢复，不能称无语义/无需计算shared/信息论最小维数；本诊断仍计算原u。即便失败，也不自动证明语义独占或排除所有下游归一化作用。

## A：四条native历史、三种消息粒度

每模型16条件：native；R、S、R+S各运行zero、norm_mean、gram_mean、gram_random0、gram_random1。两随机与mean各自保留。LM/RC均全量。A块的r/p来自当前内生状态下实际u；上游及后续route可变化，不固定clean H。

主要读数：所有条件完整NLL/KL与任务四指标；相对同模型native的损伤；zero与几何保留替代的配对差。历史对比B−A、B−P、A−P、F−B为主，另保留F−A/F−P。zero损伤与替代损伤不解释为可加知识责任比例。R/S与R+S结果并列，避免从给定另一支可替代就推断整个MoE无方向内容。

## B：固定函数的实际消息重用

P的D/G和S_P固定，只改变R_P/R_A/R_B。对同一RC输入先捕获3条完整clean S轨迹。3生产者×3消费者分别运行raw回放、norm校正、Gram校正，共27格。raw全9格对照封存E160；新校正不改R/S权重。

norm/Gram使用消费者自身clean S轨迹的r/p，d来自指定生产者的实际同输入S轨迹；Gram的b为当前消费者内生残差+R。它是使用clean标量见证的受控诊断，不是无需接收者计算的部署方法。对角保持真实native/回放身份；离对角保存全部来源，预定比较每规则的6非原配均值−3原配均值及规则间差。匹配收益的减少不称唯一中介百分比。

## 读数、统计单位与次分析

- LM：逐token真实NLL、正/反向KL、argmax agreement；窗口等权，20文件簇成对bootstrap1000，seed163002。
- RC：raw/per-char accuracy、choice CE、真实答案token NLL，首答案整词表KL单列；学科等权、科内成对题bootstrap1000，seed163001。全部题为主。
- 固定原E162四模型共同完整正确40题只作次分析，保留学科计数，只报点、不补选择后CI；不根据新替代条件筛题。B块全128题为主。
- 预定几何诊断：各层/目标native平行能量比例、分支/合计norm及FP32/BF16匹配误差、回退计数。几何量不是预测重要性或知识份额。

## 阳性对照与工程可行性

- 原生CPU tiny的P/A/B源实现、FP32/BF16：native精确复现，三种zero对照原helper，解析Gram不变量与退化情况、readonly/hooks恢复。
- 真实GPU各native参数/buffer与旧canonical指纹、原生cal/repeat逐位复现；native及旧R/S/合计zero的实际预测对照封存E162/E155。P/A/B合计zero的LM是新条件，不伪造旧参考。
- B块原3生产者/9raw网格完整重放E160，捕获/目标前缀与全部候选token counts严格；题0候选重排。新操作仅使用因果可见消息/标量，proposal不读目标答案。
- Gram FP32相对norm/投影误差需≤1e−4；所有norm/Gram替代的BF16分支norm相对误差≤.01，仅Gram要求缩放投影误差≤.01、实际残差norm相对误差≤.02；逐条件/层/批次或题的最大误差全保留。误差超过先修工程，不读作科学阴性。zero不要求这些不变量。
- 实际cal消息探针保存向量切片；独立NumPy重建几何不变量。作者汇总与独立NumPy实现分别从raw复算全部主指标/区间，先过旧数据模拟fixture再读新held。

## 噪声地板 + MIE

native repeat/身份与旧预测重放给程序地板；既有FP32/BF16精度参照另列，新几何构造误差独立记录，不从效应线性扣除。NLL .1 nat、accuracy 5pp作解释量级参考，不作显著性/路线自动阈值。若只有随机方向破坏模型或校正效应不清楚，结果不足以认领新的消息机制；不加剂量/seed/层网格救它。

## 混杂审计

固定输入/出处/完整品质与所有来源；cal/held分离；两个proposal随机全保留；身份和zero正控；参数/buffer及hooks前后只读；score和content/geometry区分；输入bootstrap不当模型总体；局部RMS几何不冒充下游充分性；端点干预不冒充训练动力学。独立初始化和跨家族总体本项未控制，结论限定此公开成熟路径及接收者。

## 决策表（跑之前写）

| 观察 | 解释变化与科学决定 |
|---|---|
| native强zero损伤被geometry替代大幅恢复，R+S仍需方向 | 单支作用包含可被伙伴背景与低维见证维持的部分；合作整体仍承载方向结构，不把单支必要性当自治知识 |
| 强zero损伤保留为同等级geometry损伤 | 所测低维几何见证不足，方向结构有实际预测必要；仍不自动叫语义存储或唯一单位 |
| B块raw原配收益在norm/Gram后基本消失 | 原配依赖可主要体现为可校正的局部几何接口，不宣布新语义联盟；结合A解释训练分担 |
| B块实际跨背景消息的原配收益在Gram后保留 | 同函数/同输入的实际方向结构仍需来源背景，超出只调幅度/投影的解释；不以Gaussian负控替代这项证据 |
| mean可恢复而两个Gaussian不行 | 模型特有的input-independent scaffold方向有作用；不是任意几何proxy都足够 |
| 效应只在一个读数/学科或CI宽 | 保留全主样本和不同读数，判断信息量，不换任务求阳性 |
| native/source/误差控制失败 | 保存失败和费用，修工程；不形成科学结论 |

## 算力预算与执行边界

0新训练/模型下载，已有venv与耐久P/A/B/F缓存；先代码/CPU、独立fixture与plan冻结再GPU。PAB含B块预计1.5–3 GPU·时、cap4；F预计.25–.75、cap1，合计cap5 GPU·时含失败/预检。至多2张并发卡，绝不超过用户总上限4。CPU/I/O另记，不占卡等待。2026-10-28启动前检查发现97.9GiB节点20/21均有其他作业，改用空闲80GiB节点：native逐个上卡，B块P完整+A/B仅实际参与的routed专家上卡，原参数共78.274GB，其余源参数留CPU；不改变前向、dtype或来源。运行前检查空卡/UUID/锁，峰值实测不凭估算保证。耐久监督、退出码/账本完整；无自动后继实验。

**同日15:13 UTC资源更新：** fvcrc21的0/2卡空出，11同时被其他任务使用。旧结果来自RTX PRO 6000 Blackwell，为保留跨运行精确重放，主动中断A100上尚在CPU装载的两进程（退出−15、无budget/preflight、核对GPU apps不含本PID），0 GPU秒、0新cal/held读数；完整监督/日志留`results/e163/attempt_0_CPU_A100/`。同一冻结19f6f3a5/plan在21的PAB=2、F=0重启，未改变科学条件。见`execution_restart.json`。NFS有界128MiB读检查约15.8/24.7MB/s，不额外复制整套资产来重复源I/O。

## 结果

**运行前实现记录：** 已完成`e163_geometry/run/analyze/verify/selftest.py`与冻结plan。CPU：三源×FP32/BF16六种原生身份/zero/恢复通过；实际三源27格cross的多token、padding、严格前缀、重排与对角均精确通过；独立旧数据fixture核对29650项数值、1376项元数据，最大差7.105e−15。见`results/e163/CPU_geometry_test.json`、`CPU_statistics_fixture.json`和`plan.json`。启动前只调整了数值identity、设备放置与源码依赖清单；未读新held效果。第一次prepare读取正在更新的CPU测试字段而退出，未创建科学结果/占卡；随后重做准备、所有19份冻结源码SHA一致。配置草稿保留在耐久raw的`pre_freeze_design_draft/`，不是实验条件或科学失败。

**16:05 UTC工程校对：** F真实参数/buffer、cal/repeat/截获及三种zero精确通过，旧native/zero的LM64窗口全部精确重放。72条真实cal向量独立NumPy重建最大相对误差1.284e−7，BF16 norm/projection/实际残差norm最大误差.001215/.000540/.000855。进入RC旧条件q0/R-zero时精确检查退出；定位出首token KL漏用旧E155/E162的FP64归约（FP32乘积后double sum）。c31e4b0e修复这一读数，新增100352词表CPU检验：旧FP32 sum误差4.857e−7，新归约与独立NumPy之差0；原生六案例与27格cross再通过。重跑时将LL/first-KL检查分开，进一步核实是否只有该问题。

F失败92.109 GPU秒计入原1小时上限，PAB尚在CPU、0GPU时主动停止以统一版本。原plan/19份源码、cal/proposals、监督/退出码和迁移凭证分别保留在`results/e163/attempt_1_KL_reduction/`与耐久raw同名子目录；没有新held几何读数，不改变条件/数据/seed/统计读数/预算。新plan显式记原计划SHA及修复来源，20份当前源码冻结。CPU I/O先让F就绪的562.507秒结束后已自动恢复PAB，不是科学条件选择。

### 全量科学结果（2026-10-29）

**主要识别来自实际消息，而非任意方向破坏。** 全128题的同S_P、同输入、实际生产者/消费者交叉，6个非原配−3个原配均值：

| 读数 | raw | norm | Gram |
|---|---:|---:|---:|
| 真实答案token NLL | .260527 [.222147,.298600] | .248472 [.212989,.282988] | .245925 [.209580,.281916] |
| choice CE | .684293 [.409607,.987217] | .676953 [.414603,.972351] | .653392 [.395101,.955933] |
| raw准确率损伤（pp） | 3.776 [.130,7.292] | 3.125 [−.260,6.250] | 3.385 [−.130,6.771] |
| per-char准确率损伤（pp） | 7.682 [4.167,11.068] | 7.943 [4.554,11.198] | 7.682 [3.776,11.201] |

Gram−raw的NLL差−.014602 [−.024973,−.004968]，norm−raw为−.012055 [−.021626,−.002399]；Gram−norm为−.002548 [−.007525,.002677]。校正有小幅NLL收益，但保留了大部分原配代价；不能说几何完全无用，也不能说它解释了主要重用障碍。原始9格、所有384条实际S轨迹指纹与E160精确重放；本卡区间用预先冻结seed163001，与E160原CI的轻微差异来自重采样，不改旧结果。

学科不能混为一谈：raw→Gram的答案NLL代价，生物.320627→.291345，数学.200427→.200504；相应差为−.029282 [−.043641,−.015659]与+.000077 [−.014455,.014342]。choice CE为生物1.103830→.998753、数学.264756→.308030，宏改善CI含0。raw准确率校正变化CI也含0，不声称任务能力恢复。不同消费者的变化方向并不一致；所有27格、首token完整词表KL、分科和两评分规则在[summary](../results/e163/summary.json)，主图为[实际消息重用](../results/e163/figures/actual_message_reuse.png)。

**Native块给出必要背景。** 下表均为相对native的文本NLL损伤；Gram/mean不是唯一proposal，全部norm/两个Gaussian与区间分别在[文本图](../results/e163/figures/native_LM_geometry.png)、[任务loss图](../results/e163/figures/native_task_geometry.png)、[正确率图](../results/e163/figures/native_task_accuracy.png)及完整summary。

| 端点 | R zero / Gram-mean | S zero / Gram-mean | R+S zero / Gram-mean |
|---|---:|---:|---:|
| P | 5.928 / 7.947 | .740 / 2.211 | 8.823 / 11.254 |
| A | 6.096 / 8.124 | 1.097 / 5.017 | 8.673 / 10.777 |
| B | 2.770 / 9.983 | 2.972 / 7.076 | 8.489 / 10.114 |
| F | 2.510 / 5.451 | 4.823 / 7.750 | 10.427 / 7.556 |

所测全部方向代理均未恢复原生预测；F的合计Gram/mean确有部分恢复，仍损伤7.556。不能把“所有几何保留都比zero差”写成结论。四端点S Gram/mean的任务答案NLL损伤为1.753/4.938/7.770/8.720；预锁40题共同成功次集及34/6学科构成保留，只报点/计数，未重新筛题。

**解释与母问题：** 训练组织下可迁移的性质、原生必要伙伴和实际可重用消息确实可以分离；同函数甚至同输入并未消除消息使用的背景条件。E163进一步削弱“这种配套主要就是所测幅度/残差投影不匹配”的解释。它没有定位语义独占、最小维数或不可训练对齐的基本障碍；当前局部见证也不等于锁住clean全程norm/最终gain。主张的价值是识别哪些模块性读数不能相互替代，继而解释何种计算需要共同保留，不是把随机旋转损伤重新命名。

### 完成核验、继承边界与费用

- 每端点真实native/cal/repeat/zero与旧LM64/RC128逐项精确重放，9个新规则对角与因果候选前缀/计数/题0重排全部通过；新worker结束时源参数/buffer/hooks恢复核对通过。
- PAB首轮完成全部native块后，cross q0因轨迹指纹键`0…`与旧E160的`layer0…`契约不同退出；PAB原worker终态参数hash**未取得**。续跑器只转换指纹键，20份数值源不变；fresh canonical/cal/所有proposal数组精确一致，并把全部16条件各4个LM窗口、RCq0及重排逐位复现，再完成全cross和新worker终态核对。三份native完整raw继承而非重跑，来源/未观测项在[native_inheritance](../results/e163/native_inheritance.json)、[cross_resume](../results/e163/cross_resume.json)及`attempt_3_hash_schema/`；不把新worker终态校验冒充旧worker的终态观测。
- 全量独立NumPy复算29650项数值、1376项元数据，最大绝对差1.421085e−14；72条真实cal向量/模型另作独立几何重建，误差界均通过。[independent_audit](../results/e163/independent_audit.json)。这是独立公式实现，非新研究团队/初始化复现，C14仍L2。
- PAB共5988.833854 GPU秒，F共1604.284289，合计7593.118143秒=**2.109199484 GPU·时**，含3703.446324/92.109081秒两次失败；各组末次退出0，实际运行区间无重叠、峰值79.318603GB，0新训练/下载。CPU装载、资源guard中断及等待均在CUDA前，0GPU秒单列；全部监督、失败和账本保留。
- 数值源c31e4b0e，冻结plan SHA `7493cb8207480a2773adb3147f1295f1e872a6d71bc127f648bce5deca4870cb`；资源等待器与指纹续跑器另有源码SHA。五份raw路径/SHA和实际监督退出见[manifest](../results/e163/manifest.json)。CPU入口：`~/.venvs/mechpop/bin/python -B moe/scripts/reproduce.py E163 all`。

**本批决定：** 三条核心论证已有实测与最近邻定位，本项补上了一个主要竞争解释的直接检验；先形成论文论证、关键图和可复现封存，不自动追加E164、adapter优化或另一轮层/方向网格。更广成熟谱系与形成分叉仍是实质缺口，按其能否改变核心解释决定未来动作，见[PAPER_SHAPE](../PAPER_SHAPE.md)。
