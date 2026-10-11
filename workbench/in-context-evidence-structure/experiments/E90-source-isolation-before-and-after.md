# E90：只读正确来源是否足以使用正确规则？形成阶段与读取阶段的来源隔离（2026-10-10）

- **状态：** DONE（24→48原读数；新增幅度读数在32独立contexts确认；single追加24→48）
- **类型：** PILOT；不新增idea，不做层/头搜索
- **对应：** I04 / C16 / C20 / P13 / P20；保留E48、E56、E85，不以新任务诊断替代它们
- **问题（一句话）：** 多来源ICL的规则干扰主要发生在示例表示形成时，还是query读取时；把后者做到oracle级来源选择，是否已足以解释E56的训练收益？

## 为什么现在做

E48换标签后另一人的答案方向贡献下降，但其位置仍被读取；E64来源处理覆盖整个query。E56的query-only模块明确在demo prefill关闭、只修改答案末位，已有冻结demo表示上的强阳性。它们使“来源信息在不在”“哪个token重要”不再是优先问题。

值得检验的桥梁是：**选择正确来源的位置，是否等于选择该来源的规则？** 先让规则不同的示例互相上下文化，再只访问目标来源，与在形成表示时就按来源分开，并非同一程序。这不是靠一个probe作归因，也不要求先证明全部能力已经完整存在。

最强近邻已在运行前核对：Contextualize-then-Aggregate主文§3.1–3.3已有跨示例任务信息传递；How Few-Shot Examples Add Up已有上下文化QK/V作用；Rethinking Invariance in ICL（ICLR2025）§2–3已有BoE与context interdependence、结构mask。**新mask、新阶段名称本身没有novelty。** 本实验检验的是这些过程在来源特定规则上的具体功能：另一来源改变规则、当前来源全部原始证据不变时，其影响是否越过了query的完整来源隔离。已有解释可兼容任一结果，但还没有给出本设置的效应量或充分性结论；不据此宣布新理论。

## 设置与读数（运行前冻结）

- Qwen3-8B，revision `b968826d9c46dd6066d109eabc6255188de91218`；conda verl-clean，float32/eager。
- 使用E56 Measuring Hate Speech原test池；24新contexts，seed90001；每Source 8demo，query为4新race＋4新gender评论。姓名随机，A的rule方向逐context随机；不选择种子/评论/成功context。A与B各自toxic/safe严格平衡。
- 每对context只翻B的8个单token标签：conflict时B与A相反，aligned时B与A相同；A的文字、标签、名字、全部位置、query均相同，两个context全局标签频率相同。只评价保持规则不变的A，避免把目标规则改变当干扰。
- 一个2×2设计：native；**early**（prefill时每条demo只能看同Source前文和初始header，query完整读取）；**late**（prefill原生，整个query所有位置只能读A/header/query）；**both**（两阶段均隔离）。阻断包含完整demo及其分隔符，不只label或最后答案位置。位置不压缩，保留同Source上下文化。
- 附带现有强阳性/解释参照：single（A独立prompt，位置长度改变，只作参照）；一条指令恢复；冻结E56 query adapter（不重新训练，prefill始终关闭）；adapter＋late。不是新的配置搜索。
- `z=logit(toxic)-logit(safe)`，A gold符号为g。主读数：来源规则margin `mean(g*z)`；B规则效应 `mean(g*(z_aligned-z_conflict))`，各条件独立报告。**late下的B效应**若非零，来自可访问A表示中已有的信息或其后续使用，而非query直接读B的位置；不是宣称该信息一定是完整抽象rule。
- 次读数：二候选准确率、全词表argmax正确率/是否label、early×late准确率交互、adapter相对both的差。24contexts成对bootstrap10000次，seed900；不对query先筛选，不用均值比的微小分母决定结论。
- 确认候选：如出现有解释价值的阶段分离，以seed190001的48新contexts确认同一科学脚本；pilot结果回来再冻结预测，不能先铺开后续。新context与原test池共享，不称独立语料。
- 命令：`CUDA_VISIBLE_DEVICES=0 /home/xiang/miniconda3/envs/verl-clean/bin/python scripts/e90_source_isolation.py --out results/e90/qwen3_discovery --n 24 --seed 90001`

## 对照、噪声与决策

- **阳性对照：** E56冻结adapter在同任务新contexts应保留明显规则响应；single与aligned native提供任务读出参照。不是只有能力缺陷才允许研究。
- **数值阳性：** 默认4D causal mask与2D/default完整前向一致；double阻断时改变B标签应精确无作用。float32最大差≤.001nats，否则停止科学判读、记录数值失败。不是用理论零效应当科学发现。
- **噪声地板 + MIE：** 数值≤.001nats；pilot内容效应以paired CI报告。late剩余B效应≥.2nats、oracle隔离/adapter差≥5百分点会改变投资判断；这些是判断尺度，不是自动关线标准。
- **混杂审计：** 原始输入、目标Source标签、token位置、标签频率配对固定。early改变contextualization和attention归一化，late改变可读范围及归一化，所以准确率涨幅不单独证明纯Source模块；B标签反事实才界定其功能信息影响。single长度不同；adapter额外监督计算存在且词表依赖，不能叫天然能力上界。无current query答案出现在上下文、无训练、无对层选优。

## 决策表（跑之前写）

- **决策表（跑之前写）：** 以下五个分支在pilot前已写；后续追加读数与运行另注明提出时间，不改变原分支。

| 实际结果 | 认识更新与下一步 |
|---|---|
| late去除几乎全部B效应，early额外贡献小 | 干扰主要通过直接跨Source读取；既有label retrieval解释在此够用，不包装新encoding缺陷。转向为什么训练的query读取超过简单Source门控的具体计算，而非继续切层 |
| late仍留明确B效应，both去除且规则使用改善 | 读取正确Source与隔离规则信息可分；追能够预测这条间接路径的机制解释，不称已有CTA不存在 |
| early隔离反而损害规则使用 | 跨Source上下文化可能支持规则形成；不能把隔离一概当修复。根据aligned/conflict与margin区分真实信息作用和整体表示扰动，再回到论文/自然问题 |
| adapter显著超过both，但both已完全排除B信息 | E56的收益不仅是避免另一Source干扰；已有表示的额外内容检索/读出计算是待解释对象。不要再叫“只打开Source开关” |
| 阳性不足或效应方向不清楚 | 记录有界结论，不展开位置/格式矩阵，不把该pilot升级为研究资格门槛 |

- **算力预算：** 单卡≤1 GPU·时pilot；只有明确认识增量才做同脚本确认≤2 GPU·时；不使用多卡联合训练。
- **实际：** 待填写。

## 结果（运行后追加）

尚未运行；不能把候选解释写成结果。原始contexts/behavior JSONL保留本地，小preflight/run/analysis入git。

## Pilot结果与确认前更新（原设计不改）

24新contexts全部保留，脚本hash748c497f…，数值最大差5.72e−6nats，144.17秒。native准确率52.60%[44.27,60.42]；late61.46%[55.73,67.19]；both57.81%[49.48,65.62]；adapter92.19%[86.46,96.88]，adapter＋late91.15%[86.46,95.31]。

B规则效应native+.95181[.64948,1.22843]，late仍+.43633[.04581,.87977]nats；both为数学预期的0，不能把这个0当发现。early没有稳定准确率收益，both−late=−3.65[−11.98,+4.17]百分点；**不支持把early isolation叫作修复**。late存在间接B影响与adapter−both=+34.38[25.0,43.75]点值得在48新contexts确认。冻结预测见`results/e90/confirmation_forecast.json`，继续原脚本/原15条件，不选层、任务或样本。

### Pilot后提出、追加运行前冻结：单来源上的同一query模块

adapter比both高不单独说明它在完全无B信息时也有效，因为两个条件的cache不同。为检验“模块是否仅通过避免B干扰而成功”这个具体桥梁，追加最小的native/adapter paired single-source测试：相同24 pilot contexts的A，**prompt根本没有B**；不新训练，不改评论/标签/姓名/顺序。两候选准确率、margin与全词表格式按原定义；用原single结果作no-op数值校对≤.001nats。额外脚本`scripts/e90_single_source_adapter.py`，本条是在看pilot后提出、实际追加运行前写，不冒称原始预注册或独立确认。

若单Source也有明确收益，模块至少执行超出Source排除的读出计算，但可能仅增加anchor访问/改善内容读取；不会自动叫新抽象rule或输入过滤。若无收益，则mixed上下文关系可能是模块行为的条件，需要重新解释上述gap。无论结果，不展开层/attention条件大全。额外预算≤.5 GPU·时，与独立确认可在不同单卡并行。

## 48-context确认：原方向预测没有确认，下一观测在新批前冻结

原源码hash748c497f…不变。native54.17%[50.26,58.33]，late55.47%[51.82,59.64]，both59.90%[54.95,64.84]，adapter91.15%[87.76,94.27]。late的foreign signed effect=.15742[−.14629,.45000]nats，**原pilot的正方向预测未确认**；early隔离也未提供稳定修复，不继续据此扩上游层/头实验。adapter−both仍+31.25[25.0,37.5]点。

单Source追加24contexts：native57.81%→adapter90.10%，paired +32.29[23.96,40.63]点，native no-op完全一致。追加比较是pilot后提出而非原始注册；只是明确模块收益超出排除另一Source，尚未反推完整新算法。

### POST-HOC观察：平均方向不等于功能独立

探索保存的逐context规则效应后发现，48contexts的late效应29正/19负（阈值.01nats），signed mean .157但mean absolute .776；24pilot相应.436/.810。adapter也有正负效应，不能用它的signed mean接近0宣称已经排除B的信息。这些绝对值是**看到确认方向CI跨0以后提出**，仅探索结果，未确认，原signed结果不替换。

### 第三独立批运行前协议（不新增任务、不改源码）

为区分“消失”与“抵消”，原脚本再运行32contexts、seed290001，15条件/全部样本保留，含原signed readout。新主读数是每context先计算 `d_i=mean_q(g_q*(z_aligned-z_conflict))`，再汇总 `mean_i(abs(d_i))`；**不是每query先取绝对值**，因此去除constant label bias对两个Input类别的共同影响。另报signed mean、正/负context数（±.01阈值）、两context之间二候选答案改变率、bias变化。没有用这些指标替代准确率，也不把confidence变化直接叫性能损失。

至少native/late/adapter三条件的幅度、两阶段隔离的数值零对照和single native/adapter的独立追加均报告。判读：late幅度CI若明显高于.1nats、且支持两种方向，则source位置隔离不足以保证rule contrast对B不敏感；若幅度接近数值floor，则旧异质观察不迁移，不延长此线。adapter准确率高而幅度不低只说明正确行为仍可以依赖joint context，不自动称错误或纯粹泄漏；normative独立先验未直接告知模型，范围明确。第三批增加一个观测量而不是再切token/层，不追完美分解。

本批约≤.5 GPU·时，原脚本与追加single脚本均冻结；新分析脚本只用于读数。后续回到多规则学习的计算解释与文献，不用又一个显著绝对值当成paper novelty。

## 第三批与单来源独立确认：最终结果

32新contexts、seed290001，原引擎hash748c497f…保持，未筛成功样本。late signed effect=.15399[−.20600,.58962]nats，仍未支持统一正方向；新冻结读数mean absolute rule effect=.73394[.47362,1.08336]nats，16正/16负。只改B的标签时A的二候选答案改变率17.58%[12.11,23.83]。native相应幅度.93842[.76243,1.13362]；adapter幅度.81497[.62918,1.02276]，答案改变率7.42%[3.12,12.50]，conflict accuracy94.14%[89.84,97.66]。adapter＋late幅度.42835[.31720,.55019]；both数值零。

这确认**异质的功能依赖**，不将未确认的signed方向改说成确认；也不把mean absolute当准确率损失。当前Source全部原始证据保持、query完全不能读取B的位置，B规则仍可影响Input类别间的对比及最终标签，因此“读取谁的位置”不足以说明“谁的关系信息参与了判断”。发生在哪类表示/哪个算法仍开放，不能凭这项干预宣布新的Task-vector模块。跨Source信息也可能支持共同输入特征/任务先验，不能预设它全是错误。

单来源48新contexts的独立追加：native61.72%[57.03,66.41]→同一冻结query模块89.32%[85.16,92.97]；paired +27.60[21.35,33.85]点，margin +1.98611[1.60533,2.35013]nats，两者全词表argmax均为合法label，native no-op误差0。**Source排除不是E56收益的充分解释**；该模块仍是1.31M监督参数/20层，收益也可包含更多anchor访问或内容读出计算，尚未区分这些机制。E56成功事实保留，不能再称只有一个Source开关。

### 科学决策：结束这组测量，回到研究问题

当前有价值的区分是：raw Source位置选择、rule信息的功能依赖、最终准确率三者不同。E90不是“又发现一个重要token”，也不依赖最新模型永远不会做题。它为多规则ICL的解释对象提供了可检验约束。但“上下文化传播信息”“attention不等于解释”已被CTA/Atlas等讨论，**宽认识不是本项目的新意**；具体的Source-conditioned rule-use模型仍未完成。后续要解释何种跨Source信息是形成Task特征所需、何种是输出映射干扰，或检验分标签的收益在哪个阶段形成；不再扩大本组mask/层/头/格式矩阵，不把这三个显著数字自动当强论文。

C16/C20保持L1；E85的独立预测不撤回，E88/E89和原方向未确认结果都保留。原始JSONL在各run目录本地留存；analysis/run/preflight/rule_sensitivity、两份冻结forecast与图入git。三批主实验+两批single实际144.17+251.45+183.43+26.33+40.12秒，合计约.1793 GPU·时（计模型加载和GPU计算，不包含CPU库导入等待），本地卡均释放。

脚本退出后出现Python3.12 multiprocess ResourceTracker的析构AttributeError，exit code为0；全部行数、run文件、数值检查与分析完整，不影响科学前向。保留原日志，不为这个析构消息扩软件修复。
