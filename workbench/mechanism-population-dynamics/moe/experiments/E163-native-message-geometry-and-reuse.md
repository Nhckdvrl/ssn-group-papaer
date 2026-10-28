# E163：成熟职责中的消息几何、方向结构与跨背景重用（2026-10-28）

- **状态：** RETRY_READY（原设计19f6f3a5；读数归约修复c31e4b0e，条件不变）。已取得真实cal/旧LM控制；尚未读新held几何条件。
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

Gram构造在实数下保留u的norm、对背景的投影和b+u的norm；实际BF16加法次序与误差实测。它保留的是**两个输入相关标量**，仍可能承载丰富信息。即便恢复，不能称无语义/无需计算shared/信息论最小维数；本诊断仍计算原u。即便失败，也不自动证明语义独占。

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

真实模型结果尚未获得。已完成`e163_geometry/run/analyze/verify/selftest.py`与冻结plan。CPU：三源×FP32/BF16六种原生身份/zero/恢复通过；实际三源27格cross的多token、padding、严格前缀、重排与对角均精确通过；独立旧数据fixture核对29650项数值、1376项元数据，最大差7.105e−15。见`results/e163/CPU_geometry_test.json`、`CPU_statistics_fixture.json`和`plan.json`。启动前只调整了数值identity、设备放置与源码依赖清单；未读新held效果。第一次prepare读取正在更新的CPU测试字段而退出，未创建科学结果/占卡；随后重做准备、所有19份冻结源码SHA一致。配置草稿保留在耐久raw的`pre_freeze_design_draft/`，不是实验条件或科学失败。

**16:05 UTC工程校对：** F真实参数/buffer、cal/repeat/截获及三种zero精确通过，旧native/zero的LM64窗口全部精确重放。72条真实cal向量独立NumPy重建最大相对误差1.284e−7，BF16 norm/projection/实际残差norm最大误差.001215/.000540/.000855。进入RC旧条件q0/R-zero时精确检查退出；定位出首token KL漏用旧E155/E162的FP64归约（FP32乘积后double sum）。c31e4b0e修复这一读数，新增100352词表CPU检验：旧FP32 sum误差4.857e−7，新归约与独立NumPy之差0；原生六案例与27格cross再通过。重跑时将LL/first-KL检查分开，进一步核实是否只有该问题。

F失败92.109 GPU秒计入原1小时上限，PAB尚在CPU、0GPU时主动停止以统一版本。原plan/19份源码、cal/proposals、监督/退出码和迁移凭证分别保留在`results/e163/attempt_1_KL_reduction/`与耐久raw同名子目录；没有新held几何读数，不改变条件/数据/seed/统计读数/预算。新plan显式记原计划SHA及修复来源，20份当前源码冻结。CPU I/O先让F就绪的562.507秒结束后已自动恢复PAB，不是科学条件选择。
