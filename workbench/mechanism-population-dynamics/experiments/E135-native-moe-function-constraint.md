# E135：固定原生MoE块函数后，专家承担仍能不同吗（2026-10-26）

- **状态：** REGISTERED（资产准备/实现前；未启动训练）
- **类型：** PILOT；单个学生的固定函数约束实验，不是自然预训练或性能修复网格。
- **对应：** P22：不重现的指纹是否触及任务重要计算；E134显示受控bank与原生OLMoE的均匀分量必要性关系不同。
- **问题（一句话）：** 给定原生联合预训练OLMoE L9的实际输入→输出函数，一个随机同容量MoE重学后，会恢复怎样的预测与专家作用对应？

## 固定对象与数据（运行前锁定）
- **教师：** E134已核验的公开OLMoE main，完全相同权重pin/三shard SHA、tokenizer、HF 4.57.6、L9（64×1024、top8、no-renorm）。它自己的prefix/downstream全冻结；只学生L9可训练。E130 CE cohort和C07不改，不并行q0教师版本。
- **函数目标：** 原生块输出Y(h)，不是原dense函数，也不是语言标签/教师专家编号/门值。拟合中间函数比只匹配最终预测更强；实际自然预测分布仍须单独测。
- **训练cache：** 从原cover512M训练池，按E128无放回窗口机制、order_seed135、新stream从头取1024个batch（每批16×512），保存每个实际L9输入H和原生Y的BF16位模式；N=8,388,608个位置。记录完整输入窗口keys/token链、数据/teacher/prefix/source SHA、逐文件曝光与重复。不是笼统“8M全不同文本”；同窗口无重复不保证token内容各异。
- **评测：** 原Dolma held512窗口/262144 targets，训练/held文件隔离；H/Y held cache与自然模型评测同源。另固定E124 plan cal512/held512 POS人口、顺序、targets/last/hash，专家对应只在cal拟合。public Hcal使用E134自己的native-prefix8192，不能混dense H。
- **cache资产：** 原生H/Y约68.7GB训练＋约2.15GB held；都在fvcrc21本地NVMe。只读小manifest进git，不把大数组放NFS训练或git。预备同时核对actual dtype/shape；不因NLL/MSE好坏筛窗口。

## 学生与固定训练预算
- **架构/初始化：** 同64×1024、top8、no-renorm；TensorMoE FP32参数、BF16 autocast；单student seed1、init_std=.02，训练前记录实际初值tensor SHA。教师保留原BF16权重；用其复制到学生算子的阳性对照测真实dtype/算子地板。
- **4096个更新：** 原1024个cache batch，每epoch按预定RNG135无放回排列，固定4epoch，总33,554,432个位置曝光；保留batch内部顺序，不把它写作十进制32M。所有cache位置恰见4次，标签/held不参与选序。
- **损失：** `mean((student_Y-teacher_Y)^2) / mean_train(teacher_Y^2) + .01*LB + .001*z`；分母为整个training cache的单个固定能量，不逐输入/专家归一化，不拟合输出增益。复制教师的forward可表示性不保证它是此含aux目标的驻点。
- **优化：** 沿用E130 AdamW beta(.9,.95)、eps1e-8、weight_decay=.1、grad_clip1、peakLR=.0003；沿用base.lr_at，steps4096、warmup_fraction=.1、余下cosine到0。这是预定pilot设置，不叫与512M CE等算力/等统计问题。
- **保存：** init、每512步固定training/held MSE事件、4096固定终点及完整曲线/optimizer/RNG；不选最佳checkpoint替代终点。数值异常保留失败与原始状态，不修LR/aux/温度网格。

## 阳性对照、主读数与资源
- **真实copy oracle：** 原生块复制权重在真正cache批次上执行，测输出MSE/自然预测KL与U/A测量地板；BF16专家分组/GEMM归约可有误差，不预宣称严格0。另保留初始随机学生作拟合前参照，全部条件报告。
- **主功能读数：** 教师、初始学生、固定终点学生各自采U/A，沿E124相同1/8单专家注入、自然selected贡献移除、行中心化+cal词形offset，**仅cal-U一对一映射→held U/A**，199 cal词形内置换/199随机map保留。共同U背景现在是原生public教师，明确不同于E130的dense背景；自然A其它位置用各自模型，不能把自然KL直接当U约束。
- **全函数/任务读数：** held输出MSE与相对教师能量误差；原Dolma完整自然双向KL、top1、GT NLL配对差（BF16 logits→FP32）；精确POS held人口的自然完整分布用真正FP32末位head，词形CI。文件/词形CI仅固定模型评测误差，不是单学生训练总体CI，不设函数等价或性能准入带。
- **资源：** 预备＋训练＋固定读数合计≤4 GPU·时，优先fvcrc21空闲单卡，source在本地NVMe；不打断E131 GPU0/2，所有探索总并发≤8卡。先做实际吞吐/内存与copy控制，预算不足明确incomplete，不换成最佳中途结果。

## 混杂审计与事先决策表
- 已控制：教师与输入/下游、精确architecture、cache/held身份、固定预算/初始化、cal/held分离、全体条件与原始读数。未控制：一个学生/教师、有限8,388,608 H覆盖及4次重复、具体优化器/aux；不能因拟合不佳断言架构不可表示或计算分解唯一。
- 预测分布较初始接近且held U/A也更对应→在此训练目标/预算中有函数约束组织的迹象，不推出唯一职责。
- 预测分布较初始接近但held U/A仍弱→提供原生计算函数约束下的候选自由度证据，连续报告剩余差距；不叫严格同函数或任意语言分工。
- 仅训练MSE改善、held/自然预测仍差→本pilot只说明该cache/学习问题的有限泛化，不能从中作分解结论；不自动延长或开参数网格。
- 全部结果与E134原生偏差必要性并列；它不能证明差别单因归冻结，亦不能把output MSE模型冒称自然从头预训练。没有结果自动关/开线或论文状态升级。

## 结果（运行后追加）
- 尚未运行。主张不变；E131原终点继续。
