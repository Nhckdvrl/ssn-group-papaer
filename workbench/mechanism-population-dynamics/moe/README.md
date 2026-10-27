# MoE：任务、学习历史与专家职责的可组合性

**状态（2026-10-27，持续执行）：** E144–E157完成。成熟历史改变同题能力依赖，性质载体和回插配套受接收背景影响。[E158](experiments/E158-native-factual-role-interchange.md)缓存预检因BF16执行形状差异停止（最大KL .05994，尚无内容干预）；保留失败与费用；完整前缀数值检查已通过，但单层大矩阵实测超预算；完整R/S/联合与attention路径版1cdcb1a8已冻结推送、GPU0运行，复用真实组件缓存，保持原输入/读数与累计4h cap。E159伙伴作用已完整取得并独立复核；当前只有E158在GPU0评测。继续C14，成熟资产阶段零新训练；探索并发上限8卡，头线仍CLOSED，其他ACTIVE分配不变。

**持续维护约定（用户2026-10-26）：** 本页作为唯一简明研究说明。每批获得完整结果后，先更新“数字与区间→竞争解释→主张范围→下一项决定”，链接实验卡/源码/原始文件，保留阴性和技术失败记录；随后继续已授权的高信息量研究，不以一批实验结束或整理文档为停点。README≤200行，详细过程留在原卡、results与logs。

[已完成证据的四面板主图](results/e157/figures/mature_role_and_reuse_chain.png)：公开成熟谱系、共同成功题的依赖形态、函数性质转移与保留接收背景的作用；图中数据已实际获得，内容职责的E158仍在测量中。

**E148的新判断：** 同父等曝光的次序处理留下预测差异，共同后缀将A→B KL由.002751降至.000893 [文件95%CI .000676,.001218]，同流复跑逐位一致。但最后64步自身KL漂移为A .007116/B .007050，约为跨历史差异8倍；终点L9 bank互换ΔNLL为−.0000174 [−.0001937,.0001439]/+.0000873 [−.0000795,.0002739]，整L9也未检出损伤。当前证据是有限历史响应，**尚无稳定、不可组合的L9组织证据**，也未做严格等价检验。完整[汇总](results/e148/summary.json)、[主图](results/e148/figures/native_order_and_compatibility.png)。

**成熟资产优先（用户睡前补充）：** 优先可核验的公开成熟checkpoint、同父分叉、公开谱系/跨模型观察；不把从头多seed预训练当默认路线。当前三分支只有一个预训练父状态，repeat是地板，不能替代独立初始化总体证据。需要独立训练总体的问题若资产不足，就保留未决，不用输入CI或低成熟度自训凑样本。成熟资产可用性/训练阶段/能回答的层次逐项见[资产核查](ASSETS.md)。

**外推边界：** E148从已训练20B token的一个公开父状态短程继续学习，并非从头或独立seed；专家 bank互换的KL≈.000165，自身late bank≈.000201，置零层ΔNLL≈+.0473。gate/输入均可变化，仍不能把本窗口的小兼容性代价外推为原生专家普遍可互换，也不能维护“历史响应必然产生配套断裂”的解释。

**E149全网络结果：** 8格NLL=2.951985–2.952440；backbone×整套MoE的交叉−共源配对代价为−.00006069 [−.00050318,.00024186]，各预定损失交互区间均跨0。单个BAB比AAA差+.000455，但只比BBB差+.000054，不能挑一个参考制造配套结论。完整[8格与双参考](results/e149/summary.json)、[图](results/e149/figures/native_system_source_cube.png)。短程原生历史响应与强模块互换障碍在本例中分离。

**E150成熟原生结果改变了判断：** 在公开声明同父的标准/文档pool 50B退火终点，交换整套MoE的平均NLL代价为**+.127787 [.122068,.134908]**；router×路由专家、路由×共享专家的共源配对收益也分别为.074494/.113406。完整预测的配套边界跨越命名的路由专家，不能由短程E148/E149的弱效应代表。[全部48条件](results/e150/summary.json)、[主图](results/e150/figures/mature_source_and_restricted_compute.png)。

**受限计算性质也有明确差异，但不能只归给gate：** 固定前128输入选31路由+1共享槽，评分后续文本；各用自身selector时，A/B裁剪ΔNLL=1.215149/.476699，B−A=**−.738449 [−.914827,−.540059]**；完整→受限KL差−.733338 [−.901011,−.533052]。同一selector下B也更稳健。平均来源翻转中，B的router使KL敏感性增加+.239/+.206，而B的路由专家、dense骨干和共享专家分别减弱它；标签读数同样显示D/R较大的负效应。NLL与KL分开报告，不当机制责任比例。A的所有其他部件不动、仅换router时，支持覆盖由.506升至.529，但裁剪ΔNLL由1.215升至1.439，结构覆盖并不足以保证功能收益。

**E151强对照改变了解读：** 全R置零的ΔNLL A/B=**6.096/2.770**，全shared置零为**1.097/2.972**；同操作下的依赖配置明显变化，不能当知识责任百分比。B随机32槽也更稳健（代价**.910**，A **2.708**），所以预算优势不只出现在“精心选中”的组。但B仍需要R，且自身prefix比随机低**.432827 [.163812,.803882]** NLL、KL同向。一般鲁棒/依赖重组和有用选择并存，不能把“更好裁剪”直接当独立语义专家证据。[强对照图](results/e151/figures/native_necessity_and_selection.png)、[完整结果](results/e151/summary.json)。

**E152归一化反事实：** 固定旧5份mask，保留全部127个router logit的softmax分母后，自身prefix裁剪代价A/B=.965038/.348459，B−A=**−.616580 [−.761489,−.450344]**，KL差−.607907 [−.748924,−.445529]；B的prefix相对random仍省.697330 [.486551,.948480] NLL。优势并非仅靠池内门值放大。幅度规则有实质作用：随机mask在full分母下A/B损伤3.884179/1.045789，且A的两个prefix对改规则反应方向不同，不能把它当统一校正项。[完整22条件](results/e152/summary.json)、[图](results/e152/figures/fixed_mask_denominator_counterfactual.png)。

**E153将认识推进到任务计算：** 生物/数学各64题，在相同selectorA/selectorB预算下，B比A的raw正确率高**9.38 [1.54,17.21] / 10.94 [3.91,18.75]个百分点**；完整模型A/B为41.41%/39.06%。仅移B gate时没有携带同样的预测保持性质；B的D/R/S功能包配A gate时，首答案token裁剪KL仍低（.275/.252，A为1.389/.794），但完整正确率降至35.16%。低预算敏感性与完整任务质量由不同配套共同决定，这为研究职责组织提供了直接任务证据。[12条件与分学科](results/e153/summary.json)、[来源效应](results/e153/source_effects.json)、[图](results/e153/figures/task_source_transfer.png)。数学raw基线较弱，主要正确率优势来自生物；两学科与raw/per-char口径均全报。

**E154把分工变化定位到成熟训练后期：** 父P/标准A/约束B的全R零化ΔNLL为**5.928/6.096/2.770**，全S零化为**.740/1.097/2.972**；B−P分别−3.157944 [−3.754613,−2.588519]、+2.231770 [1.971234,2.509166]。自身prefix损伤P/A/B=1.125172/1.215149/.476699，随机损伤2.285598/2.707941/.909527；两个后代的完整NLL都优于P。成熟阶段之后的历史改变了计算依赖与预算性质，并非B只保留父状态既有优势。[三阶段完整结果](results/e154/summary.json)、[图](results/e154/figures/public_parent_dependence_profiles.png)。

**E155：选择性部署改善伴随不同的能力依赖。** P/A/B全模型正确率37.50%/41.41%/39.06%；去R后17.97%/19.53%/22.66%，去S后32.03%/33.59%/20.31%。B仍需要R，同时去S的正确率损伤比A额外高**10.94 [2.34,18.75]个百分点**、比P高13.28 [4.69,21.88]。D-only为19.53%/17.97%/17.19%，剩余骨干不能解释原能力。部署子集有效与R功能自治是两种性质；下一步直接测试哪些学到的函数能够共同重用。[全部12格](results/e155/summary.json)、[图](results/e155/figures/task_branch_dependence.png)、[独立复算](results/e155_terra_audit/NOTE.md)。

**同样成功，依赖形态发生了什么变化？** 在三模型都答对的44题中，D失败且去R、去S各自都失败的题数为P/A/B **8/11/21**；仅D+R能保持则为20/18/3，仅D+S能保持2/0/3。P原20道仅D+R能保持的题，在B有13道变成共同必要、只有1道变为仅D+S能保持。它更支持新增共同依赖，而非shared简单接管R。该POST-HOC分析全报8类与逐题转移，等学科macro共同必要比例B−P=+.2292 [.1111,.3889]、B−A=.0903 [−.1181,.3057]；44题并非独立确认。[逐题图](results/e155/figures/common_success_dependency_patterns.png)、[完整结果](results/e155/dependency_patterns_posthoc.json)。

**E156把必要性与性质载体分开：** 固定P骨干/gate，R_B单独移入即可使受限答案NLL降低**.188177 [.115456,.264140]**、裁剪KL降低.346267；S_B单独移入未携带同样的低敏感性。但R_B的full NLL升高.080179 [.014375,.147310]，受限raw正确率29.69%低于P/P的32.81%，没有转移准确率优势。B原生shared作用很大，并不意味着预算性质主要由shared函数携带。[全部九格](results/e156/summary.json)、[直接迁移对比](results/e156/transfer_contrasts.json)。

**完整预测的配套与子集品质也分开：** 排除P/P身份角，A/B同源R/S的full答案NLL收益**.078011 [.058093,.097971]**，受限收益−.008672 [−.042489,.023435]未保留。R/S共同迁移的受限NLL仍比native B高.172633 [.124870,.218918]，接收者D/G具有实际作用。当前正面结果是可转移的预测性质和有后果的来源配套；恢复donor的预测品质仍受接收接口约束。下一步直接测试已有可部署子集能否在保留其他专家的全系统中作有用回插。[来源矩阵图](results/e156/figures/e156_source_cross_all_questions.png)、[独立3576项复算](results/e156_independent_audit/report.json)。

**E157：保留接收背景，重用代价可以降低。** 只回插任务组31个R、其余96R保留P，B/P的full NLL比整bank替换改善**.055469 [.014209,.095237]**；相对P的代价由.080179降至.024710 [−.028562,.078179]。raw正确率35.16%对P的37.50%，未证明完全无损。donor shared同行没有自动更好：四类固定partial R的NLL点值均以S_P最低，A的co-donor S有明确额外代价，B的差区间含0。外国S四格仍有同源收益.042064，但比整bank小.035947 [−.053404,−.019559]。配套是实际背景中的关系，不是固定的组标签。[完整新12格](results/e157/summary.json)、[新full与继承受限值](results/e157/figures/e157_on_domain_transfer.png)、[实验卡](experiments/E157-native-task-subbank-reintegration.md)。

**当前的正面科学判断：** 学到的分工包括专家函数、始终激活计算及其预测配套，训练历史会改变这套组织及其可重用边界。E144的拆来源、E150的成熟原生交叉和E153的独立任务已经共同提供实际预测证据；路由集中、选择价值、预算稳定性和完整能力质量则是相关而不同的性质。下一步要解释这些性质如何形成、哪些共同计算能够携带它们，而非停留在给某个裁剪指标找理由。唯一/最小语义单位和跨独立初始化的普遍规律仍是开放问题。

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
| [E152](experiments/E152-native-budget-normalizer-counterfactual.md)：固定mask改分母 | full分母下B−A自身prefix损伤−.616580，B选择收益.697330，两CI方向明确 | 优势不只依赖重归一化；规则效应随模型与mask而变，不能当统一尺度伪影扣除 |
| [E153](experiments/E153-mmlu-domain-source-transfer.md)：独立任务G×功能包 | 同32槽mask下B比A正确率高9.38/10.94个百分点；B功能包保留低KL，但完整质量受gate配套影响 | 组织差异进入实际任务；预算稳定性与完整任务质量的性质来源可以部分分离 |

E144为8个独立来源basis×3平移；E146/E147为4 basis×3平移，全部保留。均是同64完整序列/32768位置/22实际文件簇，旧held探索输入；文件/来源区间不代表训练seed总体。E145仅2个expert-init配对、一个共享起点与共同接收者，R/S共享同一个trained seed1。

更有支持的假说是：**在固定接口学生中，路由组织提供可保持配套的有效边界，历史还影响同一接口下的兼容性。** E148表明这一判断还不能外推到本次短程原生历史处理；整体预测、组织稳定和组件兼容性应分别检验。尚未恢复分工诞生动力学、证明唯一或最小计算单位、语义自包含模块、或跨独立预训练规律。

## 3. 对照与证据等级

- teacher copy、三同源组装、四donor联合重标native对角、重复前向均逐位差0；组合实际BF16组件逐位等于来源。主效应按实际BF16程序报告；FP64sum cast路径KL约.00036–.00037另列为数值参照，两者不能直接线性相减。
- 原生块、全部学生、prefix/downstream只读检查通过；完整Γ满足C/V恒等式，并与E144同人口精确重合。raw的不同目标风险恒等式与四格能量关系另经CPU复算。
- CUDA可见卡在库导入后设置会沿用缓存映射，首次预检发现后修为导入前设置+UUID核对。held之前修复，首次记录/全部成本保留于[E147之前的设备审计](results/e145/device_visibility_audit.json)。
- [CLAIMS](../CLAIMS.md)：C10–C13保持 **L1**，C14经[12项混杂审计](results/e154/claim_audit.json)升至本设定内 **L2**；C13保留短程阴性边界，C14记录成熟谱系的实际配套、任务效应与后期依赖重排；C06–C09数字和等级不变。没有宣称独立L3校对或论文就绪。[PAIN_LOG](../PAIN_LOG.md)保留原判断及本轮范围更新。

## 4. 当前推进与研究判断

E144–E147区分了真实配套、当前gate读数、历史兼容性和分组强竞争解释；E148/E149已完成原生短程历史边界。E150/E151把研究推进到成熟自由gate模型：真实配套跨routed/shared/dense，预测依赖配置、一般鲁棒性与有用选择同时变化。当前关键问题是：**哪些可重用功能需要这些计算共同保留，哪些预算优势依赖推理规则而非独立语义单元？**

成熟资产两终点已完整核验并缓存，共108.55GB公开FP32权重，原生127选7+1共享接口已实测。E152全部22条件完成；同层H上选择规则一致，整网H/后续路由可以因上游幅度变化而变。全部pool逐token NLL精确复现封存E150/E151，源参数/buffer只读，CPU点复核误差0；实际.486391 GPU·时、单卡81.857GB。旧结果不改，E143仍为备选。

E153采用原任务RC逻辑：5-shot dev示例、validation全部61题逐层greedy选专家、test数学/生物各64题；cloze答案文本teacher forcing，报告raw/per-char accuracy、choice CE和首答案token真实KL。固定AAAA/ABAA/BABB/BBBB四格与两native task mask，不让hybrid重选。全部12条件完成；源码/原生cal/因果前缀/候选重排/参数buffer只读通过，CPU268项点复核最大误差2.23e−16，实际1.092477 GPU·时。当前是固定两学科的任务证据。

[E154](experiments/E154-native-parent-formation-boundary.md)已完成P的9个新条件，A/B读数从封存raw重建；CPU258项点复核误差0，实际.329930 GPU·时、峰值54.822GB。P公开54.28GB权重逐文件核验并缓存。公开谱系声明与严格batch/optimizer链分开；[E155](experiments/E155-native-task-branch-necessity.md)已完成D、D+R、D+S与完整计算全部12格，实际1.343427 GPU·时。

当前可发展的完整科学叙事是：学习历史选择实际计算的分担与配套，预算稳定性、完整任务质量和重用条件由不同关系共同决定。关键证据已有成熟来源交叉、独立任务和父状态阶段比较；同一44道共同成功题在去S后仅保留33/31/17题，具体展示了相同成功与不同路径依赖。九篇相关工作已全文复核，它们提供架构压力、表征稳定和合作机制的连接，而非本题贡献的上限。详见[当前研究判断与完整比较](notes/POSITIONING_2026-10-26.md)。

## 5. 代码、复算与资产

- [只读driver](scripts/e144145_run.py)、[统计](scripts/e144145_analyze.py)、[E146](scripts/e146_grouped.py)、[E147](scripts/e147_gate_control.py)。复用`~/.venvs/mechpop`（torch2.8.0+cu128、transformers4.57.6），未安装新环境；E144–E149仅用原有缓存，E150新增公开成熟资产取回。
- E148：[冻结训练实现](scripts/e148_native.py)、[预定移植/统计](scripts/e148_readout.py)、[GPU统计适配层](scripts/e148_analyze_gpu.py)；FP32 master/BF16 forward，全部6.919B参数可训练，峰值56.319GB。共1,998,848训练位置含repeat，使用FA继续学习而非原optimizer；[plan](results/e148/plan.json)锁定源码、软件、输入与协议，[grafts](results/e148/grafts.json)锁定所有合法变体raw。已耐久复制核验72文件、237,114,164,566 B，详见[archive](results/e148/archive.json)。
- 从本工作台执行：`~/.venvs/mechpop/bin/python moe/scripts/e144145_analyze.py e144`（E145改e145）；`... e146_grouped.py analyze`；`... e147_gate_control.py analyze`。这些从封存raw重算，模型driver拒绝覆盖既有raw。
- 每项`results/eNNN/`的`manifest.json`锁定代码SHA、来源/输入与raw SHA；[8终点/公共模型校验](results/e144/asset_preflight.json)、[selected](results/e144/selected.json)、[来源表](results/e144/source_maps.json)可追溯。图：[预测与历史](results/e145/figures/recombination_and_history.png)、[分组与强对照](results/e147/figures/group_control.png)。
- 大权重沿[ASSETS](ASSETS.md)原位置；新raw在`~/mechpop_cache/e144_prediction_recombination`、`e145_history_cross`、`e146_grouped_recombination`、`e147_gate_group_control`，未放入Git。没有重建71.7GB训练H/Y cache。
- [本日日志](../logs/2026-10-27.md)、[历史阶段快照](notes/GPT_PHASE_SUMMARY_E120-E142.md)、[导师原问](notes/ADVISOR_2026-10-23.md)。当前解释以本页/方向文档/完整结果为准，历史暂停与过宽判断均保留来源。

**同一函数的职责也依赖接收系统（E159前的旧数据POST-HOC）：** 同一套S_B权重在native B中的移除准确率损伤，比单独移入P背景时高11.72 [3.13,20.31]个百分点（固定128题）；预锁九格共同成功的33题里，移除后保留16/28题。答案NLL损伤差1.713744 [1.489787,1.971933]。graft零化端点继承已封存P S-zero的精确算子身份，无新增前向；两背景还同时改变D/G/R，接下来[E159](experiments/E159-unchanged-function-partner-role.md)只补4个未知零化端点、固定D/G隔离伙伴作用。[全部来源与分支](results/e159/known_border_posthoc.json)。

**相同函数集的背景作用也出现在自然文本：** 复用E150/E151，固定整套S_A/S_B时，背景B−A的零化ΔNLL分别增加1.124308 [.881004,1.423819] / 1.996441 [1.731348,2.337062]；固定R_A/R_B则下降3.440878 / 3.161046，两区间均全负。64窗口、30,994真实目标、20文件簇CI；权重函数不变，D/G/另一分支共同换背景。支持职责存在可直接测的系统关系部分，尚未隔离具体伙伴；这是旧端点POST-HOC组合、0新前向。[同函数作用图](results/e159/figures/e159_known_context.png)、[全部双向结果](results/e159/known_lm_border_posthoc.json)，独立点误差0、CI≤1.78e−15。

**E159新干预：伙伴足以改变未改函数的实际作用。** 固定P的D/G与S_P，仅换R_B，S的移除答案NLL代价增加.338574 [.235373,.443924]；固定R_P换S_B，R的代价下降2.609301 [2.387042,2.826923]。原始准确率效应区间较宽，未将loss效应当精确能力比例。预锁33个共同成功题中，固定S_P的共同必要由4变11题：8题由仅R可保持变为两支共同必要，1题反向。相同专家函数的使用关系可以被伙伴改变，shared始终调用且系数1，gate参数仍P，实际H/route内生变化。[配对效应图](results/e159/figures/unchanged_partner_effects.png)、[完整16格](results/e159/summary.json)。

**专家配对仍未携带全部原生依赖。** B的R/S同时移入P后，native B的S移除NLL代价仍额外高1.243731 [1.034762,1.460691]；这说明D/G背景也影响预测敏感性，不能直接叫作语义职责移动。所有来源/四指标/分科/8种形态保留；A伙伴对R的NLL与choice CE影响还存在符号差异，角色不压成一个无条件重要性分数。3824项独立数值、707项计数核对均通过，误差≤3.55e−15；实际1.365762829 GPU·时、单卡81.835589GB、0新训练。[E159卡](experiments/E159-unchanged-function-partner-role.md)。

**下一研究决定：** E158把同一事实的“换实体”和“换所问属性”输入区别在native P/A/B的R/S/联合输出间交换，固定自然语言事实与对照、逐层测真实源答案特异性。先把职责落到具体传递的区别，再判断其跨历史保持或迁移；不继续围绕预算分数扩网格。独立初始化总体仍需成熟资产，尚未回答。

**E150工程与范围：** 两终点各13,568,641,024参数，cal FP32→BF16 KL A/B=.000706/.000892单列，主读数统一实际BF16。全部native角逐位复现、参数/buffer只读通过；主运行峰值81.857GB，4044.6885 GPU秒=1.1235246 GPU·时，含全部预检/I/O/读数。raw点值与来源对比复核最大误差1.11e−16。[复核](results/e150/raw_verification.json)。一个作者声明同父的协议包、20输入文件簇CI，非独立seed总体；不是原论文MMLU复现或从零形成机制。
