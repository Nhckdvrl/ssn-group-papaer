# MoE：任务、学习历史与专家职责的可组合性

**状态（2026-10-27，夜间实际进展）：** E144–E151全部主读数完成、raw复核通过。E148/E149/E150/E151实际4.91620/.20238/1.12352/.33064 GPU·时；成熟模型阶段无新训练，峰值并发3卡≤8，头线仍CLOSED，其他ACTIVE分配不变。

**持续维护约定（用户2026-10-26）：** 本页作为唯一简明研究说明。每批获得完整结果后，先更新“数字与区间→竞争解释→主张范围→下一项决定”，链接实验卡/源码/原始文件，保留阴性和技术失败记录；随后继续已授权的高信息量研究，不以一批实验结束或整理文档为停点。README≤200行，详细过程留在原卡、results与logs。

**E148的新判断：** 同父等曝光的次序处理留下预测差异，共同后缀将A→B KL由.002751降至.000893 [文件95%CI .000676,.001218]，同流复跑逐位一致。但最后64步自身KL漂移为A .007116/B .007050，约为跨历史差异8倍；终点L9 bank互换ΔNLL为−.0000174 [−.0001937,.0001439]/+.0000873 [−.0000795,.0002739]，整L9也未检出损伤。当前证据是有限历史响应，**尚无稳定、不可组合的L9组织证据**，也未做严格等价检验。完整[汇总](results/e148/summary.json)、[主图](results/e148/figures/native_order_and_compatibility.png)。

**成熟资产优先（用户睡前补充）：** 优先可核验的公开成熟checkpoint、同父分叉、公开谱系/跨模型观察；不把从头多seed预训练当默认路线。当前三分支只有一个预训练父状态，repeat是地板，不能替代独立初始化总体证据。需要独立训练总体的问题若资产不足，就保留未决，不用输入CI或低成熟度自训凑样本。成熟资产可用性/训练阶段/能回答的层次逐项见[资产核查](ASSETS.md)。

**外推边界：** E148从已训练20B token的一个公开父状态短程继续学习，并非从头或独立seed；专家 bank互换的KL≈.000165，自身late bank≈.000201，置零层ΔNLL≈+.0473。gate/输入均可变化，仍不能把本窗口的小兼容性代价外推为原生专家普遍可互换，也不能维护“历史响应必然产生配套断裂”的解释。

**E149全网络结果：** 8格NLL=2.951985–2.952440；backbone×整套MoE的交叉−共源配对代价为−.00006069 [−.00050318,.00024186]，各预定损失交互区间均跨0。单个BAB比AAA差+.000455，但只比BBB差+.000054，不能挑一个参考制造配套结论。完整[8格与双参考](results/e149/summary.json)、[图](results/e149/figures/native_system_source_cube.png)。短程原生历史响应与强模块互换障碍在本例中分离。

**E150成熟原生结果改变了判断：** 在公开声明同父的标准/文档pool 50B退火终点，交换整套MoE的平均NLL代价为**+.127787 [.122068,.134908]**；router×路由专家、路由×共享专家的共源配对收益也分别为.074494/.113406。完整预测的配套边界跨越命名的路由专家，不能由短程E148/E149的弱效应代表。[全部48条件](results/e150/summary.json)、[主图](results/e150/figures/mature_source_and_restricted_compute.png)。

**受限计算性质也有明确差异，但不能只归给gate：** 固定前128输入选31路由+1共享槽，评分后续文本；各用自身selector时，A/B裁剪ΔNLL=1.215149/.476699，B−A=**−.738449 [−.914827,−.540059]**；完整→受限KL差−.733338 [−.901011,−.533052]。同一selector下B也更稳健。平均来源翻转中，B的router使KL敏感性增加+.239/+.206，而B的路由专家、dense骨干和共享专家分别减弱它；标签读数同样显示D/R较大的负效应。NLL与KL分开报告，不当机制责任比例。A的所有其他部件不动、仅换router时，支持覆盖由.506升至.529，但裁剪ΔNLL由1.215升至1.439，结构覆盖并不足以保证功能收益。

**E151强对照改变了解读：** 全R置零的ΔNLL A/B=**6.096/2.770**，全shared置零为**1.097/2.972**；同操作下的依赖配置明显变化，不能当知识责任百分比。B随机32槽也更稳健（代价**.910**，A **2.708**），所以预算优势不只出现在“精心选中”的组。但B仍需要R，且自身prefix比随机低**.432827 [.163812,.803882]** NLL、KL同向。一般鲁棒/依赖重组和有用选择并存，不能把“更好裁剪”直接当独立语义专家证据。[强对照图](results/e151/figures/native_necessity_and_selection.png)、[完整结果](results/e151/summary.json)。

**当前最有解释力的理解：** 组织约束改变了路由专家函数及其与始终激活计算的配套；功能分工包含全模型的预测依赖配置，而非只是一张gate图或命名的专家组。整体预测兼容性、一般删减鲁棒性和输入选择价值应分别测。现有证据支持这个正面研究对象，尚未识别唯一/最小语义单位或证明形成必要条件。归一化尺度与语义内容的作用仍需分开。

## 1. 母问题与当前窗口

> 在相同任务约束下，哪些专家职责和配套由任务/路由结构约束，哪些由训练历史选择；这些差异何时改变实际预测与组件重用？

固定原生OLMoE的一层输入/目标/下游是E134–E147拆开因素的窗口；E148已进入原生全网络继续学习，但仍只有一个预训练父状态。方向、历史证据与数学范围见 [RESEARCH_DIRECTION](RESEARCH_DIRECTION.md)。E120–E142的整体脉络见[逐项索引](experiments/INDEX.md)，所有旧结果保留。

## 2. 本轮真正增加的认识

| 实验 | 直接结果 | 对科学解释的更新 |
|---|---|---|
| [E144](experiments/E144-fixed-gate-recombination.md)：固定gate拆来源 | 24重组相对完整三学生，ΔNLL **+.002061**，交叉95%CI[.001759,.002517]；共同μ参考ΔKL **+.002441** [.002123,.002820] | 配套差异有真实预测后果；绝对损伤小，不只是欧氏求和恒等式，也不是能力崩溃 |
| [E145](experiments/E145-history-gate-bank-cross.md)：同一接收者交叉 | 共同gate下C_R/C_S=.055990/.037892；两配对的bank移植NLL代价S−R **−.005222**，文件CI[−.008375,−.002512] | 当前gate的直接读数不足以吸收历史相关差异；剩余体现在该接收者下的bank兼容性，含支持外调用 |
| [E146](experiments/E146-grouped-recombination.md)：训练Γ定组 | 一个8×8分组的ΔNLL=.000681，三个随机同大小组为.001690–.002151；Γ−随机均值 **−.001258** [−.001714,−.000793] | 保留哪些专家的共同来源有跨输入预测意义，超出纯组大小效应 |
| [E147](experiments/E147-gate-coactivation-group-control.md)：新增强gate-only对照 | gate-only−Γ的NLL差 **+.0000048** [−.000251,.000266]；gate-only也优于旧随机均值 | 未检出Γ的额外收益；不能将E146包装成发现超出gate结构的函数内容联盟 |
| [E148](experiments/E148-native-checkpoint-order-forks.md)：原生同父次序分叉 | 共同后缀后KL=.000893，但自身late→final KL≈.0071；终点L9 bank/ gate/整层互换NLL区间均跨0 | 历史响应不自动成为稳定的职责或配套断裂；局部学生现象没有被本原生窗口直接推广 |
| [E149](experiments/E149-native-system-source-cube.md)：全网络8格 | backbone×MoE配对代价−.000061 [−.000503,.000242]；两native角逐位复现 | 未检出强系统配套障碍；结论不限于事先选的L9，但仍仅本单父/短历史窗口 |
| [E150](experiments/E150-native-mature-routing-protocol-cross.md)：成熟协议终点16格×3预算 | 整MoE互换配对代价+.127787；native B裁剪代价较A低.738449，但B gate平均不携带这项收益 | 实际配套跨route/shared/dense；可重用边界和受限计算性质需直接测，不能由routing结构替代 |
| [E151](experiments/E151-native-pruning-selectivity-necessity.md)：必要性与随机32槽 | R-zero代价6.096→2.770、shared-zero 1.097→2.972；B随机损伤.910仍高于自身prefix.477 | 依赖配置/一般鲁棒性变化与有用选择并存；削弱“只靠routing集中”与“R已消失”两个单一解释 |

E144为8个独立来源basis×3平移；E146/E147为4 basis×3平移，全部保留。均是同64完整序列/32768位置/22实际文件簇，旧held探索输入；文件/来源区间不代表训练seed总体。E145仅2个expert-init配对、一个共享起点与共同接收者，R/S共享同一个trained seed1。

更有支持的假说是：**在固定接口学生中，路由组织提供可保持配套的有效边界，历史还影响同一接口下的兼容性。** E148表明这一判断还不能外推到本次短程原生历史处理；整体预测、组织稳定和组件兼容性应分别检验。尚未恢复分工诞生动力学、证明唯一或最小计算单位、语义自包含模块、或跨独立预训练规律。

## 3. 对照与证据等级

- teacher copy、三同源组装、四donor联合重标native对角、重复前向均逐位差0；组合实际BF16组件逐位等于来源。主效应按实际BF16程序报告；FP64sum cast路径KL约.00036–.00037另列为数值参照，两者不能直接线性相减。
- 原生块、全部学生、prefix/downstream只读检查通过；完整Γ满足C/V恒等式，并与E144同人口精确重合。raw的不同目标风险恒等式与四格能量关系另经CPU复算。
- CUDA可见卡在库导入后设置会沿用缓存映射，首次预检发现后修为导入前设置+UUID核对。held之前修复，首次记录/全部成本保留于[E147之前的设备审计](results/e145/device_visibility_audit.json)。
- [CLAIMS](../CLAIMS.md)：新增C10–C14均 **L1**；C13保留短程阴性边界，C14记录成熟窗口的实际配套与受限计算来源效应；C06–C09数字和等级不变。没有宣称独立L3校对或论文就绪。[PAIN_LOG](../PAIN_LOG.md)保留原判断及本轮范围更新。

## 4. 当前推进与研究判断

E144–E147已经区分真实配套、当前gate读数、历史兼容性以及分组的强竞争解释；现在按[E148](experiments/E148-native-checkpoint-order-forks.md)继续推进原生学习窗口：同父完整网络、相同batch集合次序pulse、长共同后缀及同流repeat，保存参数/路由快照。最重要的缺口是：**当gate本身能持续变化、模型以真实语言目标继续训练时，哪种配套边界还能保持或形成？**

E148/E149完整完成后，不追加LR/剂量扫描。[E150](experiments/E150-native-mature-routing-protocol-cross.md)复用公开EMO 1T预训练后标准/文档路由约束50B退火的成熟终点，检验充分学习后的组织来源兼容性，不新训seed。实际原生接口是127路由专家选7+1共享专家，故按dense骨干/router/路由专家/共享专家四因素交叉16格；不能把共享计算混入专家组解释。官方同父脚本已核查，完整batch/optimizer起点未取得，不冒充严格自控分叉。当前CPU/变长输入测试通过、108.55GB公开权重下载中，新模型读数尚未获得。E143仍为备选。

现有材料可以形成论文贡献的三个候选支点：真实预测配套、历史相关的合法兼容性、结构边界与gate-only强对照。恒等式、置换匹配和一般router–expert耦合均非新点；若不能跨自由gate/原生训练窗口重现，贡献仍是局部受控发现。详见[定位表](notes/POSITIONING_2026-10-26.md)。

## 5. 代码、复算与资产

- [只读driver](scripts/e144145_run.py)、[统计](scripts/e144145_analyze.py)、[E146](scripts/e146_grouped.py)、[E147](scripts/e147_gate_control.py)。复用`~/.venvs/mechpop`（torch2.8.0+cu128、transformers4.57.6），未安装新环境；E144–E149仅用原有缓存，E150新增公开成熟资产取回。
- E148：[冻结训练实现](scripts/e148_native.py)、[预定移植/统计](scripts/e148_readout.py)、[GPU统计适配层](scripts/e148_analyze_gpu.py)；FP32 master/BF16 forward，全部6.919B参数可训练，峰值56.319GB。共1,998,848训练位置含repeat，使用FA继续学习而非原optimizer；[plan](results/e148/plan.json)锁定源码、软件、输入与协议，[grafts](results/e148/grafts.json)锁定所有合法变体raw。已耐久复制核验72文件、237,114,164,566 B，详见[archive](results/e148/archive.json)。
- 从本工作台执行：`~/.venvs/mechpop/bin/python moe/scripts/e144145_analyze.py e144`（E145改e145）；`... e146_grouped.py analyze`；`... e147_gate_control.py analyze`。这些从封存raw重算，模型driver拒绝覆盖既有raw。
- 每项`results/eNNN/`的`manifest.json`锁定代码SHA、来源/输入与raw SHA；[8终点/公共模型校验](results/e144/asset_preflight.json)、[selected](results/e144/selected.json)、[来源表](results/e144/source_maps.json)可追溯。图：[预测与历史](results/e145/figures/recombination_and_history.png)、[分组与强对照](results/e147/figures/group_control.png)。
- 大权重沿[ASSETS](ASSETS.md)原位置；新raw在`~/mechpop_cache/e144_prediction_recombination`、`e145_history_cross`、`e146_grouped_recombination`、`e147_gate_group_control`，未放入Git。没有重建71.7GB训练H/Y cache。
- [本日日志](../logs/2026-10-26.md)、[历史阶段快照](notes/GPT_PHASE_SUMMARY_E120-E142.md)、[导师原问](notes/ADVISOR_2026-10-23.md)。当前解释以本页/方向文档/完整结果为准，历史暂停与过宽判断均保留来源。

**下一研究决定，限两项：** 先在论文原始任务/独立输入上验证native性质及少量预定来源格，确认语言窗口结果何时涉及能力层面的分工；再做保留full-softmax原门值的预算干预，区分支持选择与重新归一化/尺度适应。不扫层或预算、不默认新训多seed。公开preanneal父权重是后续形成阶段资产，独立初始化总体仍未取得证据。

**E150工程与范围：** 两终点各13,568,641,024参数，cal FP32→BF16 KL A/B=.000706/.000892单列，主读数统一实际BF16。全部native角逐位复现、参数/buffer只读通过；主运行峰值81.857GB，4044.6885 GPU秒=1.1235246 GPU·时，含全部预检/I/O/读数。raw点值与来源对比复核最大误差1.11e−16。[复核](results/e150/raw_verification.json)。一个作者声明同父的协议包、20输入文件簇CI，非独立seed总体；不是原论文MMLU复现或从零形成机制。
