# 结果导航：三条主张怎样复核

当前科学结论见[MoE入口](../README.md)，证据等级与解释修订见[CLAIMS](../../CLAIMS.md)。本页只定位结果文件。

| 要复核的论证 | 主要完整文件 | 原始数据/来源 | 独立公式复核 |
|---|---|---|---|
| 相近品质、选择部署与R/S依赖分离 | [E162 summary](e162/summary.json) | [manifest](e162/manifest.json)、[plan](e162/plan.json) | [报告](e162_independent_audit/report.json) |
| 低预算性质的载体与完整质量 | [E156 transfer contrasts](e156/transfer_contrasts.json)、[全来源](e156/summary.json) | [manifest](e156/manifest.json)、[plan](e156/plan.json) | [报告](e156_independent_audit/report.json) |
| 相同函数的伙伴作用 | [E159 summary](e159/summary.json) | [manifest](e159/manifest.json)、[plan](e159/plan.json) | [报告](e159_independent_audit/report.json) |
| 相同函数实际消息的原配关系 | [E160正式summary](e160/retry_1/summary.json) | [正式manifest](e160/retry_1/manifest.json)；父目录保留首轮中断费用 | [报告](e160/retry_1/independent_report.json) |
| 局部几何能否解释实际消息重用 | [E163 summary](e163/summary.json) | [manifest](e163/manifest.json)、[继承范围](e163/native_inheritance.json) | [报告](e163/independent_audit.json) |
| 性质来源与实际路由通路、新55学科范围 | [E164完整矩阵](e164/summary.json) | [manifest](e164/manifest.json)、[plan](e164/plan.json)、[退出/成本](e164/execution_complete.json) | [报告](e164/independent_audit.json) |
| 增益、性质与伙伴作用的干预分离 | [EMO矩阵](e166/emo_summary.json)、[OLMoE矩阵](e166/olmoe_summary.json) | [plan](e166/plan.json)、[退出/费用](e166/execution_complete.json)、两个family manifest | [报告](e166/independent_audit.json) |
| 另一成熟谱系的整机趋势与组件性质反向 | [E165完整矩阵](e165/summary.json) | [manifest](e165/manifest.json)、[plan](e165/plan.json)、[退出/成本](e165/execution_complete.json) | [报告](e165/independent_audit.json) |

[四面板主图](e163/figures/research_spine.png)对应[逐项来源SHA/JSON路径](e163/research_spine.json)，不新增统计检验。完整任务正确率、NLL、KL、两学科、全部来源/方向和预锁成功次集仍在各summary中。

E164/E165分别用`reproduce.py E164 all`、`reproduce.py E165 all`复现；E166也已全量完成，入口`reproduce.py E166 all`。两个family manifest与`execution_complete`中的恢复监督确认完成；原CPU-only中断链保留失败事实。旧四项核心spine保持原组成与来源。CPU复核：`~/.venvs/mechpop/bin/python -B moe/scripts/reproduce.py spine verify`；从本工作台根执行，说明见[scripts](../scripts/README.md)。

## 读文件时的约定

- `manifest.status=complete`及监督退出记录共同确认完成；raw在外部耐久缓存，manifest给绝对路径/SHA/bytes。大权重和原始数组不进Git。
- `plan`绑定输入/配置/源码；`summary`是统计；`artifact_seal`绑定精确源码/输入/结果包和恢复。精确位置见[ASSETS](../README.md#资产与恢复)。
- `attempt_*`、失败源码、旧budget与监督是证据，保留原事实。E163 PAB完整native继承，旧worker终态未观测；fresh校准/抽样/完整cross和新worker终态校验的范围在原卡，不能互相替代。
- E160/E163相同raw点值的CI有轻微差异：各用自己预先冻结的重采样种子，不改写旧区间。输入bootstrap不是训练seed。
- 早期受控结果按[实验索引](../experiments/INDEX.md)查找；E143未运行，E158原逐层网格未取得，不能从编号或缓存目录猜完成状态。
- `directory_cleanup_2026-10-29.json`只记本轮目录/文档/生成缓存整理；前一批约222.47GB重复副本清理仍见[原凭证](cleanup_2026-10-28.json)。科研原始资产未因文档整理删除。

## 审计与预检目录的说明

原来各目录下的 `NOTE.md`，11-24 并入此处。

### e153154_terra_audit

*原文件 `moe/results/e153154_terra_audit/NOTE.md`；原标题：E153/E154 独立 CPU 复算（C14/P32）*
- E153 的 12 条 raw/per-char 正确率与首答案 token KL 点值与作者汇总一致；例如 BBBB/selectorB32 raw=0.3750 [0.2967, 0.4533]。BABB 的 A/B selector 首 token KL=0.2751/0.2519。
- E154 全目标 B−P：routed-zero ΔNLL=−3.157944 [−3.754613,−2.588519]，shared-zero ΔNLL=+2.231770 [1.971234,2.509166]。后代−父状态各条件 ΔNLL 与作者表点及区间最大差 8.9e−16。
- E153 固定两个学科、各 64 题，按学科分层配对 bootstrap 1000 次；作者与本复算同 seed 但随机数顺序不同，已核对项 CI 端点最大差 0.01196。E154 以 20 个 (source,file_id) 簇为单位重采样并按各簇原序列数加权；区间均是输入抽样区间，不是训练种子总体区间。
- E153 真实答案文本作为 continuation，目标位置从 prompt 长度减一处起逐 token 评分，计数与记录的答案 token 数核对；测试题 question+choices 哈希与 calibration 集交集为 0。dev 五例共享为上下文，不能据此排除预训练污染。
- 四格顺序为 D/G/R/S：AAAA、ABAA、BABB、BBBB；body 包含 D/R/S，因此改变隐藏状态及其后路由，不能当作隔离的专家权重效应。两个 native task selector 在所有 hybrid 上固定，不对 hybrid 重选。
- E154 的 P 是公开 Preanneal，A/B 为两封存成熟后代；后代 native/零化/随机取 E151，两个固定 prefix 取 E150，mask 与 P 一致。公开谱系声明不等于已核验逐 batch/optimizer 的因果链。
- BF16：P 的两条 calibration FP32→BF16 KL 为 0.000665/0.000343；重复和全槽精确。A/B 有各自 preflight。推理前后参数及 buffer 哈希不变为运行记录与代码证据，本审计没有重新执行模型或复核全部权重字节。
- 交互、加减恒等式及观察到的依赖差异不能单独证明训练形成机制或跨初始化普遍性；上述具体读数仍有效于所测输入和固定模型。
- 过程检查 0 error、33 个既有 warning。本审计未修改主张等级，未重跑 GPU；可执行复算与完整结果见同目录 script.py、report.json。
- 补充复算 192 项（12 条件五项指标、六种来源对比及相对同格 full 的变化）：作者预定 subject-major bootstrap 的点值与 CI 端点最大误差 2.22e−16。report 保留 subject-major 和 replicate-major 两种区间；后者的有限次重采样差异不是数值 bug。
- 例如 AAAA/full 的 choice CE=3.9182 [2.9334,4.9676]、正确答案 token NLL=1.9877 [1.7767,2.2239]。selectorA 下平均 gate/body 来源的同格 full 相对 choice CE 变化分别 +0.4517 [0.1257,0.8096] / −3.7441 [−5.1513,−2.4495]；body 效应包含 H 与实际 routing 的变化，不能归因于单一组件。

### e155_terra_audit

*原文件 `moe/results/e155_terra_audit/NOTE.md`；原标题：E155 独立 CPU 复算（C14/P32）*
- 三状态 raw accuracy（P/A/B）：native 0.3750/0.4141/0.3906；R-zero 0.1797/0.1953/0.2266；S-zero 0.3203/0.3359/0.2031；both-zero 0.1953/0.1797/0.1719。
- accuracy 的 R×S 对比 P/A/B 分别 0.0703 [−0.0156,0.1563]、0.0625 [−0.0313,0.1484]、0.1328 [0.0156,0.2500]；choice CE 的相同对比为 2.0924 [0.7355,3.6554]、3.2740 [1.5653,5.0684]、4.1137 [1.8369,6.7048]。
- 全部 P/A/B × 四条件的 raw/per-char accuracy、四选项 CE、正确答案 token NLL、首 token KL，及相对 native、R×S、A−P/B−P/B−A 配对比较均列在 report.json；accuracy 相对 native 使用干预减 native，方向与作者 accuracy drop 相反。
- 128 题含两个固定学科各 64 题；每统计均以 seed 155001 从学科 0 后学科 1 各重采样 1000 次，等权 macro，CI 是配对题目区间，不是模型种子或学科总体区间。
- 与作者 summary 165 项点值和 CI 端点最大差 1.67e−16；三份 raw 的 SHA256 与各自 manifest 一致。A/B native 的 128×4 候选 LL 与 E153 的 AAAA/BBBB full 逐项精确相等，输入标签和长度也相同。
- 检查 driver：轴顺序为 native、routed_zero、shared_zero、all_moe_zero；R-zero 保留 D+S，S-zero 保留 D+R，联合零化保留 D。R×S 是指标上的差分对比，不是知识的分摊比例；固定两个学科和预训练模型不能推出种子总体或训练形成机制。
- 本次仅 CPU 读既有 raw、manifest、summary 与实现；没有运行模型或更改主实验、旧结果与主张等级。可复算脚本及完整结果在同目录。
- POST-HOC 共同成功子集仅按 P/A/B native 全答对选定，共 44 题（生物 36、数学 8）；两科等权配对 bootstrap，seed 155101。shared-zero 正确率 B−P=−0.3681 [−0.5974,−0.0970]，B−A=−0.3403 [−0.5347,−0.1736]；routed-zero 对应 +0.0417 [−0.1458,0.2292]、+0.1389 [−0.1111,0.3682]。
- 这是看完全矩阵后提出的条件分析，不是独立确认，不能替代全样本；native 全正确的条件排除了干预纠错。各条件的正确率、翻转率、分科计数及区间见 common_success_posthoc.json。
- E155 依赖形态独立复算入口为 dependency_patterns_review.py，结果及作者表对照见 dependency_patterns_review.json；重跑报告 SHA256 不变。

### e156_independent_audit

*原文件 `moe/results/e156_independent_audit/NOTE.md`；原标题：E156 独立 CPU 原始结果审计器*
依据实验卡与原始存储字段独立编写；本次未重新读取或复用作者分析实现，也未读取正在运行的科学结果；此前在静态接口审阅中曾接触该文件。
真实审计应待完整 raw、summary、manifest 和预算全部 complete 后，由主 agent 手动执行：

```sh
~/.venvs/mechpop/bin/python -B moe/results/e156_independent_audit/audit.py \
  --raw "$HOME/mechpop_cache/e156_common_parent_cross/scores.npz" \
  --summary moe/results/e156/summary.json
```

程序先验证预算/manifest完整、raw路径和SHA及summary绑定，再逐项对比各格及native的 raw/per-char准确率、choice CE、真实答案token NLL、预算损伤、PP差、AB配对对比、分科与等权macro的1000次配对bootstrap CI。校验PP复用和共同成功集由原native full计算且36/8。无任何写入；不一致会返回非零并列明差异。

局限：raw只保存全词表首token KL标量，未保存概率分布；可复算其汇总和对比及CI，不能独立从概率计算该KL或确认模型前向。四选项 score KL可从raw重算。

CPU合成最小自检：`~/.venvs/mechpop/bin/python -B moe/results/e156_independent_audit/audit.py --self-test`；覆盖已知分数/答案长度、KL恒等、AB方向及排除PP、双科等权bootstrap。未运行真实结果审计。
实际运行：E156预算complete且原进程退出后，从完整101,431 B raw复算3576项点/配对CI/来源对比，最大误差1.7763568394002505e−15，全部通过，见report.json。原生参数/buffer/cal身份由原manifest控制另行核验；本CPU检查不从未保存的全词表概率重建KL，也不称盲法设计审计。

### e156_terra_preflight

*原文件 `moe/results/e156_terra_preflight/NOTE.md`；原标题：E156 静态预检（2026-10-27）*
- 未发现必须修复的实现错误；尚未从本次审阅确认 GPU 控制通过。
- P/A/B 对应模型索引 0/1/2；`n.assemble(...,(0,0,r,s))` 固定 P 的 dense/gate，分别选取 R/S 来源（`e156_run.py`、`e150_native.py`）。
- 常数 oracle 覆盖九格 R/S 来源和 shared 系数；三个 gate 相同，不能仅凭该 oracle 验证 P gate，来源由 `assemble` 代码和调用元组确定。
- 全词表首答案 token KL：相对 P 原生 full；预算 KL：各格自身 full 相对自身 masked。四候选 choice-score KL 分开报告（`e156_run.py`、`e156_analyze.py`）。
- P/P 先检查真实 cal 组合身份，逐题复用 native P；9×2 + 3×2 − 2 = 22 个不同条件。
- selector 仅由 P 和逐 subject validation cal greedy 生成，固定用于全部来源；相关 context manager 和收集 hook 均在 finally 恢复（`e153_data.py`、`e153_harness.py`、`e150_restricted.py`）。
- 真实前置检查包括各源参数/state_dict 和 buffer hash、旧 cal 逐位一致、full mask 身份及全部 native 逐题 LL 重放；结束恢复模块并复核 hash。是否实际通过以运行记录为准。
- 分析器核对 3×3×2×128×4、native 3×2×128×4、来源次序、两科各64及预先固定的共同成功集 36/8；A/B对角线与非对角线对比符号与实验卡一致。

### e157_independent_audit

*原文件 `moe/results/e157_independent_audit/NOTE.md`；原标题：E157 独立 CPU 审计器*
依据实验卡、冻结plan及run的存储接口独立实现，本次未阅读或复用E157分析源码；不是盲法设计审计。语法和合成已知答案自检通过，未读取E157科学raw或运行模型。

重算范围：全部12个固定组 full、subject标签构成的on/off复合、native重放；每格相对PP、同S下P_R及整bank的成对差；A/B同源/异源符号和相对整bank配套差；仅on-domain引用E156旧masked数据。每项在128全体和固定44题（36/8）上计算subject等权点值及seed157001、1000次subject-major成对bootstrap CI；校验来源身份、任务字段和native重放逐位相同。

真实使用须E157预算和manifest完整，先校验plan、E157 raw及E156 reference SHA，再读数据。主agent提供无数值summary字段后已接入逐项自动比较；差异返回非零。合成内存完整schema比较通过7020项，并验证故意篡改CI会被发现；真实结果仍未审计。首token全词表KL只存标量，不能重算词表分布，只能核对其汇总、差值与CI。

```sh
~/.venvs/mechpop/bin/python -B moe/results/e157_independent_audit/audit.py --self-test
```

完成后人工运行（不自动写结果文件）：

```sh
~/.venvs/mechpop/bin/python -B moe/results/e157_independent_audit/audit.py \
  --raw "$HOME/mechpop_cache/e157_task_subbank_reintegration/scores.npz" \
  --previous-raw "$HOME/mechpop_cache/e156_common_parent_cross/scores.npz" \
  --summary moe/results/e157/summary.json
```
真实完成后运行：7020个点/宏平均与分科CI/来源对比误差≤1.7763568394002505e−15，全部通过（report.json）；此前7020合成检查与本次真实审计严格分列。首token KL只复核raw标量汇总，on-domain masked仍是E156继承，并非本次新前向。

### e157_preflight

*原文件 `moe/results/e157_preflight/NOTE.md`；原标题：E157 静态预检*
未发现阻止冻结的实质代码问题。每层沿旧mask选择31个donor R、其余R及gate取P，shared独立取P/A/B；12新full格与3个native重放的轴与统计schema一致。

代码按两个固定题分别核对empty/all与旧full、on-domain masked部分组与整bank同算子及旧E156读数；所有题的native LL与首token KL重放。参数、buffer、原生cal、输入、mask和冻结源码均有哈希或逐位校验；off-domain masked未测。

上述为只读静态推断；真实GPU的身份、hook恢复、数值、内存与执行结果尚待正式运行。两题masked结构控制不等于重新测量全部题；gate参数固定不保证隐藏态或实际路由固定。

### e158_independent_audit

*原文件 `moe/results/e158_independent_audit/NOTE.md`；原标题：E158 独立 CPU 审计器*
依据预注册卡、封存数据接口和此前静态审阅独立重算；不是盲法设计审计。未调用作者统计函数、未读取成熟raw或运行模型。

重算内容包括所有来源/场景/路径/层的source排名特异性、对照赔率、source/target LP、命中及KL；固定国家成对bootstrap（seed158001、1000次）、等权关系与16层均值、历史差及实体/属性S−R差。另核同层匹配移除的target NLL/top1/KL、层均值、历史与S−R对比；共同成功集只报告各关系点估计与计数。baseline-only不生成patch值，检查native和最后residual正控。

真实raw仅在预算、manifest 和 plan/data/raw SHA 校验通过后人工调用。v3 只接受累计预算中完整保留的先前 cached 失败和一个已完成的 full-forward 尝试，并校验失败记录 SHA。已按主agent提供的无数值summary结构实现自动逐项比较；合成比较器差异检测通过。真实结果尚未读取或审计。首token KL只保存标量，不保存词表分布，因此可核汇总与CI，不能从分布重算。

```sh
~/.venvs/mechpop/bin/python -B moe/results/e158_independent_audit/audit.py --self-test
```

真实结果完成后人工调用：

```sh
~/.venvs/mechpop/bin/python -B moe/results/e158_independent_audit/audit.py \
  --raw "$HOME/mechpop_cache/e158_factual_role_interchange/full_forward/scores.npz" \
  --data "$HOME/mechpop_cache/e158_factual_role_interchange/data.npz" \
  --summary moe/results/e158/full_forward/summary.json \
  --manifest moe/results/e158/full_forward/manifest.json \
  --plan moe/results/e158/full_forward/plan.json \
  --budget moe/results/e158/budget.json
```

v3 的 `uncached_*` 与 `cache_KL` 是兼容字段名：分别记录完整词表读出和仅最后位置读出的原生全前缀对照，不使用 KV cache。先前 cached 预检失败单独保留。

### e158_preflight

*原文件 `moe/results/e158_preflight/NOTE.md`；原标题：E158 静态预检*
- 未发现必须修复的数值逻辑错误；CPU测试及成熟GPU验证的实际状态以运行结果为准，不构成L3设计审计。
- 每步深复制prefix KV，最后位置设length−1；逐query逐层核对fast/native MLP输出与cached预测位相同。
- R/S为原生加权专家输出直接tap；固定q0/q48逐层以原生S-zero、R-zero和both-zero核验，R+S逐位重构。固定query同源替换及所有source的final-residual正控覆盖预设条件。
- target、三类source与匹配对照从封存data索引取值；control保留source标签频数，不用模型读数选择。
- 内容数组3×3×3×16×2×24×38，移除3×3×16×2×24×38；循环各格填一次，共27648行。baseline gate失败时不分配虚假patch/removal数组。
- budget与设备锁在CUDA张量分配前进入；临时forward与hook使用finally恢复，结束核对参数/buffer哈希。
- 精度边界：成熟每步只核原cache长度，原cache字节hash只在CPU tiny测试；不能称成熟逐次cache字节已核对。统计和schema核对详见report.json。

### e158_whole_independent_audit

*原文件 `moe/results/e158_whole_independent_audit/NOTE.md`；原标题：E158 v4 完整路径独立 CPU 校对*
对应 C14、E158 v4。基于实验卡与原独立审计公式实现，未读取作者 v4 统计器、未读取 v4 新数据或加载模型。`audit.py --self-test` 使用合成读数校验排名平局、国家配对、关系等权、模型/路径轴、S−R 和历史对比以及预算拒绝条件。

实际运行仅在主实验进程退出且预算记账完成后：

```sh
~/.venvs/mechpop/bin/python -B moe/results/e158_whole_independent_audit/audit.py --audit --output moe/results/e158_whole_independent_audit/recomputed.json
```

读取科学 raw 前核预算原样保留两次失败及第三次完成、累计 ≤14400 秒、plan/manifest/源码/数据及引用 SHA、参数/buffer/cal 身份、旧完整原生预检、执行方式与地板；核输入映射、baseline 引用、共同 top10 门槛及阳性残差身份。门槛未通过时只输出 baseline；通过时输出全部四路径和三场景的八项指标、固定国家配对 bootstrap 及所有预定对比、共同成功集点值计数和匹配移除。R/S 单独身份仅两个固定查询，所有查询检验的是联合 RS 和 A；不声称全查询单独 R/S 身份。

`cache_*` 兼容字段实际为继承 v3 的完整 head 与 keep=1 原生读取对照，不使用 KV cache。KL 只封存完整词表 KL 标量，不能从已保存数据重建词表分布。输出无层轴，也无层均值；完整路径非定位与知识比例。主汇总比较器已接入；实际命令加 `--summary moe/results/e158/whole_path/summary.json`。合成结构与故意篡改掩码的检测均通过，尚未进行正式独立校对。

### e159_independent_audit

*原文件 `moe/results/e159_independent_audit/NOTE.md`；原标题：E159 独立 CPU 校对*
对应 C14、实验卡 E159。独立实现 `audit.py`，未依据主分析器实现计算；当前仅运行合成小数据自检，没有读取 E159 科学 raw，也没有产生科学结果。系统 Python 无 NumPy；使用已有 `~/.venvs/mechpop/bin/python`，只导入 NumPy 和标准库，不加载模型或使用 GPU。

运行 `~/.venvs/mechpop/bin/python moe/results/e159_independent_audit/audit.py --self-test`：验证来源轴与方向、所有 8 个二进制依赖形态、恒定差值配对 bootstrap、33 题统计逻辑。实验完成并获执行信号后，用 `--output <输出路径>` 执行；它先验证 complete manifest、全部预算尝试状态和总费用、plan / 代码 / 模型小文件 / 任务 / 继承参考 / raw 的 SHA，再核对维度、来源、分科、固定队列、P 重放与参考身份。科学计算的 CI 为每学科内题目配对抽样 1000 次，seed 159001，学科等权；所有对比由同一题级抽样得到。次分析为固定 33 题，报告 pooled 与等学科权重及分科 8×8 转移，不给 CI。

输出中指标轴依次 raw accuracy、per-character accuracy、choice CE、真实答案的每 token NLL；主格轴为 R、S（P/A/B/zero），对比保留 A−P、B−P 的符号。准确率支撑为 full 减移除，损失支撑为移除减 full；balance 为 shared 支撑减 routed 支撑。所有模式均要求 full 成功，位 4/2/1 分别代表 D-only、仅 R、仅 S 正确；模式 0 是 D 和两条单路径均失败。

主分析器汇总结构与数值尚未提供，因此比较器尚未连接，尚不能声称独立校对通过或升级主张。此审计不区分参数固定时输入状态和下游路径的变化。

已独立复算 E155/E156 继承端点并比对 `known_border_posthoc.json`：4 指标、3 来源、完整质量及原生与移植支撑均一致；最大点误差 1.78e-15，分科点及总体/分科 CI 最大误差 3.55e-15，固定 33 题所有计数一致，三源参数和 buffer 哈希匹配。结果见 `known_border_review.json`。复现命令：`~/.venvs/mechpop/bin/python moe/results/e159_independent_audit/audit.py --known-border-review --output moe/results/e159_independent_audit/known_border_review.json`。这是事后重用旧端点，零新 forward，不能隔离固定 D/G 下伙伴替换的效应；未读取 E159 新 raw。

完整 E159 汇总比较器已按预先提供的无数值 schema 接入：在正式执行命令加 `--compare-summary <汇总JSON>`。比较全部预注册主表、支撑、固定伙伴、对角与原生对比，以及 33 题点值、模式和转移；输出最大点/区间误差与计数匹配状态。合成映射自检包含故意修改一个对比以验证能检测不一致；尚未读取任何 E159 新原始数据。

E150/E151 旧语言模型端点独立核对见 `known_lm_border_review.json`：所有点估计完全一致，20 文件簇 bootstrap CI 最大误差 1.78e-15；两源原生逐 token 重放、参数/buffer 哈希和有效掩码一致（30,994 个目标）。命令：`~/.venvs/mechpop/bin/python moe/results/e159_independent_audit/audit.py --known-lm-review --output moe/results/e159_independent_audit/known_lm_border_review.json`。背景包含 D/G 和另一分支，不能单独解释为伙伴作用；零新 forward。

**当前真实完成状态（2026-10-28）：** E159 report.json 比较已通过：3824个数字、707项计数，点/CI最大误差3.55e−15，全部计数一致。前面未读/未接比较器措辞为准备阶段记录，以本完成条目为准；不是L3升级。

### e160_independent_audit

*原文件 `moe/results/e160_independent_audit/NOTE.md`；原标题：E160 独立 CPU 校对*
正式raw尚未完成。CPU完整汇总集成fixture发现并修复独立比较器的一处符号错：准确率的matching cost按预定定义为对角减非对角，loss为非对角减对角。原冻结作者统计与模型driver未改。`check_integration.py`单独导入作者统计生成合成汇总，`audit.py`仍以独立公式计算；3828数字/3565计数匹配（≤4.45e−16），故意损坏点、CI、计数、空学科None均被拒绝。`integration_test.json`记录源码SHA；该CPU测试没有读取正式干预数组。

对应 C14、E160 固定共享信号实验卡。独立实现消费者×生产者九格、共享支撑、固定生产信号后的受控 R 支撑、自然参照、固定生产者及固定消费者对比、固定 P 信号与自然伙伴效应差、非对角减对角完整质量、R 删除时保留生产信号的恢复量。四种指标均保留；全部题目按两学科各 64 道等权、学科内成对 bootstrap 1000 次，seed 160001。

次分析在九格完整结果均 raw 正确的题上，输出点值/计数和全部 8 模式及固定生产者/消费者转移；学科为空时宏平均为 null。S-replay-only 使用 R 存在时产生的 S 轨迹，不是自然 S 独立能力。受控 R 支撑不是 R 总知识量；恢复量不是唯一中介比例或无需 R 计算的部署证明。

```sh
~/.venvs/mechpop/bin/python -B moe/results/e160_independent_audit/audit.py --self-test
```

合成自检覆盖轴与符号、固定信号和自然对比、八模式、空学科、预算拒绝。未读取新 E160 科学原始数据、未加载模型或运行 GPU。正式输入/继承哈希校验及无数值 summary 比较器已接入；正式运行加 `--audit --summary <summary.json> --output <report.json>`。当前尚未读取正式数据，未声称独立校对通过。

### e161_independent_audit

*原文件 `moe/results/e161_independent_audit/NOTE.md`；原标题：E161 独立 CPU 校对*
对应 C14 与 E161。独立重算固定国家/关系交叉映射，校验四个答案 token 不同；根据真实全词表 top1 将结果分为原答案、实体混合、关系混合、完整 donor、其他五类，不使用四候选子集 argmax。输出五类比例及相对自然基线变化、四标签 LP 增益、KL、关系/实体混合相对 donor 的偏好、R 与 attention 偏好差和所有指标的 A−P/B−P。24 国家成对 bootstrap 1000 次、seed 161001、两关系等权；共同四查询在三模型均 top1 正确的次集仅报点和计数。首 token 与固定探针的范围不外推为完整事实生成能力。

CPU 合成自检：`~/.venvs/mechpop/bin/python -B moe/results/e161_independent_audit/audit.py --self-test`。涵盖四标签映射、类别分割与词表外 other、路径轴、偏好符号、配对统计和预算。没有读取 E161 新数据、加载模型或运行 GPU。

完成后以 `--audit --output <审计输出>` 重算；读取 raw 前检查完整预算与 cap、plan/manifest、源代码/数据/参考/暂存清单哈希、旧轨迹和参数/buffer/cal 身份，读取后核对 outcome map、原生选中 LP/top10、共同 top10 门槛和 source 正控。KL 只存全词表 KL 标量，不能从封存数据重算分布；工程身份以 manifest 声明及封存引用复核。汇总比较器已接入，正式运行时附加 `--summary <summary.json>`；当前尚未读取正式数据，不能声称独立校对通过。

### e162_independent_audit

*原文件 `moe/results/e162_independent_audit/NOTE.md`；原标题：E162独立公式复算*
本目录`audit.py`不导入模型或作者统计代码。由保存的候选LL独立重建四种任务指标，以文件簇重采样的计数权重实现LM bootstrap，并逐项比较所有主条件、历史差、预算规则、共同成功形态和转移。题目使用162001、文件使用162002，均1000次；条件选择后次集只核点/计数，不补CI。

`check_integration.py`是单独CPU测试入口，允许导入作者汇总来检查两套实现的契约。它只用旧B模拟F，不是新F预测；5114个数值/133项元数据检查匹配到约7.1e−15，故意改坏点值会被拒绝。报告在`integration_test.json`，同时锁作者/校对/fixture源码SHA。早期样例误用了历史mask字段名，已改为读取E152封存mask；没有改实验driver或F结果。

正式调用只接受complete manifest、完整预算和匹配源码/输入/raw SHA，再复算。KL仅保存逐token或逐题标量，无法从这些标量独立重建未保存的整词表分布；运行时来源身份及前后只读控制按封存记录核对。

这是单独NumPy实现的统计与接口复算，不等同于新训练、另一个团队的独立复现或L3科学审阅。实际F数据尚未完成前，不能把CPU样例通过写成实验完成。

正式F运行已于2026-10-28完整完成：5114数值、133元数据最大误差1.421e−14，`report.json`全部通过。预先样例与实际结果明确分开；原实际监督退出0与预算在E162目录。

### reading_terra_code_check

*原文件 `moe/results/reading_terra_code_check/NOTE.md`；原标题：论文与作者代码接口核对（2026-10-27）*
- **Myth Fig.6：** 同一读出 MoE 上比较不同生成器轨迹最符合图和设定，但论文未明确写出重放实现；不能当成已经直接证明。未见跨独立权重专家匹配的定义（论文 p.8–9；附录 p.15，29）。
- 单条观测为某层两条 rollout 的高频专家集合 Jaccard；原文为 30 题、60 个 reasoning 生成模型、4 seeds；图按 Qwen3、ERNIE、gpt-oss 分面（p.8）。
- 三种比较固定两轴：同题同 seed 改生成模型；同生成模型同 seed 改题；同题同生成模型改 seed。题对与平均权重细节未披露（p.8 §5.1）。
- Eq.13 对每条序列按 token 访问次数统计专家频率；Eq.18 取累计质量 ≥P 的最小高频集合，Eq.19 求交并比；Fig.6 P=.8，Fig.25 附其他 P（p.15、29）。prompt 是否进入该指标未确认。
- **MoE Lens PPL：** 调整所有 MoE 层 top-k 后重新运行完整模型，最终 logits 计算右移 next-token CE，再 exp；不是逐层 LogitLens（`moe_lens_pplx_source.py` 48–53、114–155、163–189）。
- 图 3 的域内曲线是等样本平均 log(PPL) 后对 k 做 min-max，不是原始 PPL 数值（同文件 296–319、346–359；论文 p.4）。长样本按 2048 token 独立块运行，丢失跨块上下文及边界预测。
- 完整模型推理保留 shared experts 和层残差；当前 DeepSeek 官方配置 `norm_topk_prob=false`，故 top-1 至 top-6 均保留全专家 softmax 原权，不对选中专家重归一化。官方模型代码 L245–280、321–369、802 起；配置 L13、22–26、33。
- 本次只核对当前公开模型源码；notebook 没有锁 HF revision，历史运行所用 revision 未确认。
- 局部读出另行从原始前向取各专家输出和门权，截取 top-k 后求和；可加 attention 后残差，但排除 shared，直接 lm_head，不传到后层（`moe_lens_logit_source.py` 303–325、380–439）。截取权重无二次归一化；整数 ID 特殊分支赋权 1.0。
- 论文 p.3 Eq.3–4 写 LayerNorm；局部组合函数直接 lm_head，另一个 helper 仅对 2D 输入做无学习权 RMS 归一化；各代码路径不能一概等同论文公式（同文件 26–36、438–439）。
- 可借鉴：分别报告 shared、残差、门权及后续传播条件；区分序列路由频率与功能损伤。详细出处与未确认项见 `report.json`。

