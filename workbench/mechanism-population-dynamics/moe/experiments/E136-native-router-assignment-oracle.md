# E136：固定原生分配的oracle对照（2026-10-26）

- **状态：** COMPLETE（固定训练/全部读数及独立审计、归档完整）
- **类型：** PILOT；单个组织信息对照，不是新蒸馏方法、优化器调参或新seed网格。
- **对应：** P23：E135已见函数/职责部分恢复，但剩余函数差与联合学习分配的困难尚未分开；承接P22。
- **问题（一句话）：** 给出原生teacher的实际gate/支持、保持相同expert初值和总函数监督后，拟合与自然承担的可对应性会怎样变化？

## 动机与唯一处理（结果前锁定）
- E135单学生固定终点held能量归一化MSE=.169350，Dolma/POS KL=.042466/.044719，cal-U→held U/A=.099435/.103208（初值.016880/.004488）；完整复制oracle为0误差/ρ1。不能由这些剩余差异判断同函数自由度，也不因未到某KL值延后所有职责分析。
- **唯一新臂：** 读取E135 `initial.pt`，逐expert保留相同seed1 FP32初始权重、expert顺序；仅gate替换为原生teacher gate的精确BF16值→FP32存储，并**全程冻结gate**。所有expert可训练。逐expert初始tensor hash必须和原E135匹配，gate hash在训练前后相同。
- 它提供了组织信息并移除router优化/其aux梯度，是**assignment-oracle条件的总体作用**；不能唯一称边界学习困难，更不能将对应增强当自然任务自发决定唯一分工。不提供逐expert输出/语言标签/职责ID目标，仍只拟合总Y。
- 原E135自由router结果完整保留作参照，不重跑/选seed，不新增random-router、gain、LR、aux或2×2网格。

## 固定数据、目标、预算
- 原生teacher/cache完全复用E135已SHA归档资产：8,388,608个H/Y位置、同1024缓存batch、同四个seed135无放回epoch排列，4096更新/33,554,432 optimizer位置曝光；原262144 held位置与E124 cal/held POS人口不变。
- 损失仍 `mean((Yhat-Y)^2)/fixed_train_energy + .01 LB + .001 z`，同能量.0005764026773。gate冻结后aux对expert没有直接梯度，明确记录常量作用；相较E135还移除router梯度参与全局clip的耦合，均计入oracle总体作用。不改变标签/混合/输出增益。
- Expert-only AdamW beta(.9,.95)、eps1e-8、weight_decay=.1、clip1、peakLR=.0003、10% warmup和同4096 cosine；fresh optimizer，对应E135原初始状态。没有因看到效果延长、选最佳中途终点或调参。
- 保存初值、固定每512步train/held MSE、4096终点、RNG/optimizer/全部曝光与梯度记录；持续核对gate不变。oracle初值的自然预测和A也测量，避免把共享支持诱导的对应误称学习出的内容。
- **成本封顶：** 新臂预备/训练/固定读数共≤1 GPU·时，fvcrc21独立空闲卡，必要时初值只读测量可与训练并发；另本机E131继续，合计并发≤8。新ledger与E135分开记账，不重建/复制70GB H/Y。实际吞吐决定资源报告，不设MSE/KL准入线。

## 阳性对照、已知坐标与读数
- 原E135 teacher/copy画像、真实完整预测复制0误差为已知答案参照；新gate精确同teacher后，还须核对actual full-row top8 indices/weights/selected masks与teacher相同。不是用gate相似代替功能证据。
- **主：已知坐标下的自然A。** teacher gate的行被精确提供，专家槽的identity是预先施加的对应；在原row-center/cal-word-offset之后，对initial-oracle与final-oracle各自测held A(identity)及固定map的词形CI/raw幅度。报告所有列、未定义和support基线，不挑更高的对应；初值A不能简单相减当作已经扣除support的纯专精。
- **兼容：** 原cal-U Hungarian→held U/A完整保留；另identity U也报告，形成预定两种对应（已知接口identity、原cal-U），不是再搜索一组更好匹配。global U仍是在共同原生public教师背景的1/8单专家注入，A为各condition自然全位置背景的实际贡献移除。
- **初值U可耦合复用：** Oracle只换gate，expert函数、共同U背景、输入、alpha均和E135 initial完全相同；因此可以引用其已存U/zero/background/Htarget/Hcal，必须核对expert-only hash与源NPZ SHA并显式标reuse。Oracle initial的A/normal NLL/所选门值必须新采，不能复用旧随机gate的A。final U/A均新采。
- 原Dolma与精确POS held人口的自然预测双向KL/top1/GT NLL差，沿E135两条精度路径（Dolma BF16 logits→FP32；POS真FP32末位head）；文件/词形CI不是单学生总体CI。held block MSE与所有旧剩余误差连续并列。
- 固定终点c/r/zero/recompose/native五干预按E135/E134同算子和teacher baseline，仍无gamma，预算内全保留；不称知识占比或同稀疏算力方法。

## 解释分支与混杂审计
- 函数拟合改善且A(identity)比oracle初值更对应→给定组织信息有助于内容/函数恢复；因gate已施加，不能说任务独自选出组织。
- 函数差下降但A(identity)仍弱→固定支持下候选分解差异；仍保留剩余函数差、有限H覆盖和优化解释，不定义自动自由度通过线。
- A(identity)与cal-U→A不同→说明原全输入U匹配与已知支持对应是不同估计对象；不能用较高者替换E130/E135原主读数。若初值A本已对应，明确它包含共有支持/门值。
- 未改善拟合→说明此固定预算oracle未提供该益处，不推出结构不可能、原生函数不可表示或整条方向无意义；不自动扩grid。
- 主要未控制：一teacher/一初始化、finite8M H重复4次、teacher组织信息与router冻结/aux梯度同时改变；其它数据/表示/目标/初始expert与预算保持。门值已被监督的结果不冒称自然预训练。

## 定位与结果
- StableMoE/普通gate蒸馏、B-Distill已有固定/监督router思路；本卡用它作为函数与职责可对应性的oracle控制，不认领方法创新。原E135及所有失败/剩余差距照常保留。
- 尚未运行；C07及其它主张不升降级。

### 实际执行（2026-10-26）
- 训练源`e136_train.py` SHA `8c620871df90c2a10ea9be5b629727ce063164483ab8a0d22cb846e6f6841b55`；CPU exact-resume/expert初值/gate冻结/支持/预算隔离检查与真实资产preflight通过后冻结。23:22:56UTC在fvcrc21 GPU0启动PID841358。
- 4096固定终点完整，train/held同fixed-train-energy MSE=.135760/.156780；初始experts与E135逐项同，gate在训练中未改变，真实8192行支持/门值/logits差0。原free case .150627/.169350完整保留，不据此先判内容/唯一性。训练ledger730.23秒，新1GPUh总上限。
- 读数源capture SHA `bee7d9144e8e620e855f40f8c8890f0746d4c5aa27f6e5944c45a675adc73a1e`、readout SHA `276d7042fa8e82ead3b8a32cc65514ee7a4e362a6b7bc2ac300e0612ae7a4421`，CPU固定对应/cluster-CI/coverage-change与两端真实preflight通过后冻结。CI只在所有draw都定义且同有效列集合时报，否则明确不可用，不筛draw/word。
- 23:43:16UTC在fvcrc21 GPU1启动完整readout PID844954，source背景/teacher支持及coupled-U引用均核对SHA；独立ledger与E135隔离。尚无oracle职责/干预结论。

### 完整读数与独立核对（2026-10-26）
- complete/errors空，ledger训练+读数1572.83秒，未改E135的3883.97秒/7runs记录。模型/全部artifact已SHA归档`~/mechpop_cache/e136_assignment_oracle/`，指针`results/e136/archive_manifest.json`。
- known-identity：initial U=.005991 [词形CI −.019864,.030162]、A=.005147 [−.059347,.092965]；final U=.225511 [.192306,.249140]、A=.347197 [.250371,.401280]。
- 原calU：initial U=.016880 [−.005194,.038169]、A=.020315 [−.023635,.055280]；final U=.179074 [.135530,.213119]、A=.257223 [.184664,.312922]。free E135 final calU U/A=.099435/.103208完整保留；knownidentity与calU两种预定对应全报，不选高者改旧结论。
- 64列均定义、全部1000/seed136 word-bootstrap有效集合相同；独立NumPy/SciPy点值/CI误差≤2.78e−17。独立CPU逐值核对192 expert权重初值相同、gate为teacher BF16→FP32且final不变；actual1024条support/weights/masks全一致，unselected A全0，coupled-U八字段逐元素同源。`results/e136/independent_audit.json`。
- final自然预测：Dolma KL=.039673 [.03411,.04478]、top1=.910255、GT NLL差+.030986；POS真FP32-head KL=.041980 [.032598,.052332]、top1=.923668、NLL差+.047170 [.022650,.071986]。相较free，MSE/KL点略低，但POS top1低于.928391、GT差高于+.041736，不能概括为全面质量改善。
- final c/r/zero ΔNLL=.040768/.002757/.054889，native/recompose0；所选均值反事实和剩余函数差限制继续保留。
- **解释：** 给定assignment条件后出现更强的这套贡献模式对应；它包含组织信息、router冻结及clip耦合变化。初值A不是可相减的纯support null，A也可能受共同总函数恢复影响，仍未证明逐expert向量内容或唯一语言分工。下一项E137只做既定坐标on/off向量与component/aggregate误差结构，无新训练/匹配/gain。C07/C08不升降级。

### 2026-10-26覆盖解释校正（不改原分数）
E136–138复核发现：POS held512 teacher/fixed-gate experts42/51/52 target-on=0、raw A恒0；row-centering及cal-word去均值使这些列继承全专家均值变化。原“64个数值有效列”不可解读成64个独立内容承担，旧分数/全部列保留；free学生覆盖需按自身实际mask分别报告。`results/e131/controlled_target_support_audit.json`同时记录受控E130/E131全64有on但部分低覆盖；不得将有on自动当高信度内容证据。
