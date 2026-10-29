# MoE 实验索引 E120–E163（2026-10-29）

这是证据导航，不是自动执行队列。E120–E142是受控平台阶段；E144–E163均已完成，E143未运行。E163来自集中整理后用户新的全局再定位授权，已取得全部数据并独立复算。现在整合核心论证/主图与封存，无自动后继。当前授权与资源见[AGENTS](../../AGENTS.md)和[唯一研究说明](../README.md)，总并发上限4卡、当前0卡。历史数字与等级保持原范围。

## 当前核心证据：成熟原生路径 E150–E163

| 实验 | 状态 / 对应 | 主结果 | 直接证据 |
|---|---|---|---|
| [E150](E150-native-mature-routing-protocol-cross.md) | DONE；C14/P32 | 完整MoE互换平均+.127787 NLL；B native裁剪代价低.738449，B router单独不转移此收益，D/R/S参与 | [summary](../results/e150/summary.json) |
| [E151](E151-native-pruning-selectivity-necessity.md) | DONE；限定C14/P32 | R-zero代价6.096/2.770，S-zero1.097/2.972；B random预算损伤.910，prefix仍优于random.433 | [summary](../results/e151/summary.json) |
| [E152](E152-native-budget-normalizer-counterfactual.md) | DONE；限定C14/P32 | full分母下自身prefix B−A损伤−.616580，B的prefix仍优于random.697330；削弱纯归一化解释 | [summary](../results/e152/summary.json) |
| [E153](E153-mmlu-domain-source-transfer.md) | DONE；C14/P32 | 同32槽mask下B比A任务正确率高9.38/10.94个百分点；低裁剪敏感性随功能包保留，完整质量仍依赖gate配套 | [summary](../results/e153/summary.json) |
| [E154](E154-native-parent-formation-boundary.md) | DONE；C14/P32 | P/A/B的R-zero损伤5.928/6.096/2.770，S-zero .740/1.097/2.972；成熟退火区间出现依赖与预算性质分化 | [summary](../results/e154/summary.json) |
| [E155](E155-native-task-branch-necessity.md) | DONE；C14/P32 | full P/A/B=37.50/41.41/39.06%，S-zero=32.03/33.59/20.31%；B额外S依赖+10.94pp，R仍必要 | [summary](../results/e155/summary.json) |
| [E156](E156-native-common-parent-function-cross.md) | DONE；C14/P32 | R_B可转移低预算NLL敏感性，完整质量并未一起保留；固定P D/G下仍有来源配套 | [summary](../results/e156/summary.json) |
| [E157](E157-native-task-subbank-reintegration.md) | DONE；C14 | 保留P其余96R、仅回插31R任务组，使B/P的full NLL相对整bank改善.055469；同源shared并非自动更好 | [summary](../results/e157/summary.json) |
| [E158](E158-native-factual-role-interchange.md) | DONE；C14 | 完整末位置R流支持同国家换属性，attention传递国家/答案更强；未完成的单层网格不当数据，原失败完整保留 | [whole-path summary](../results/e158/whole_path/summary.json) |
| [E159](E159-unchanged-function-partner-role.md) | DONE；C14 | 固定S_P与D/G换R_B，S移除NLL代价增加.338574；同函数的实际作用由伙伴共同决定 | [summary](../results/e159/summary.json) |
| [E160](E160-fixed-shared-signal-context-cross.md) | DONE；C14 | 相同S函数的生产/消费轨迹交叉有.260527答案NLL配套代价；固定信号后伙伴效应改变，产生与使用需分开 | [complete retry summary](../results/e160/retry_1/summary.json) |
| [E161](E161-crossed-entity-relation-composition.md) | DONE；C14 | 双因素R交换没有支持跨国家纯关系操作；多数为other，attention保留强完整donor阳性 | [summary](../results/e161/summary.json) |
| [E162](E162-full-course-native-division.md) | COMPLETE；C14=L2不变 | F/B完整raw都39.06%、文本NLL接近；F前缀损伤更低，同时S移除文本/任务NLL代价额外1.851/5.311；四模型同成功40题共同必要8/10/20/24。停止自动追加、转入整理 | [完整结果](../results/e162/summary.json)、[独立复算](../results/e162_independent_audit/report.json) |
| [E163](E163-native-message-geometry-and-reuse.md) | COMPLETE；C14/P33，仍L2 | 四端点各16条件和真实消息27格完整；raw/norm/Gram原配NLL代价.260527/.248472/.245925，几何校准只解除小部分，准确率改善未区分；独立29650数值/1376元数据通过，含失败2.109199 GPU时 | [完整结果](../results/e163/summary.json)、[主图](../results/e163/figures/actual_message_reuse.png)、[独立复算](../results/e163/independent_audit.json)、[领域位置](../PAPER_SHAPE.md) |

## 预测配套与原生桥接 E144–E149

| 实验 | 状态 / 对应 | 主结果 | 直接证据 |
|---|---|---|---|
| [E144](E144-fixed-gate-recombination.md) | DONE；C10/P31 | 固定gate拆来源ΔNLL+.002061、ΔKL+.002441；正交叉CI | [summary](../results/e144/summary.json) |
| [E145](E145-history-gate-bank-cross.md) | DONE；C11/P27–29 | 同接收者bank代价S−R=−.005222；共同gate C_S/C_R=.037892/.055990 | [summary](../results/e145/summary.json) |
| [E146](E146-grouped-recombination.md) | DONE；条件满足后执行 | Γ定8×8组ΔNLL=.000681，3随机同大小组.001690–.002151 | [summary](../results/e146/summary.json) |
| [E147](E147-gate-coactivation-group-control.md) | DONE；新登记强对照 | gate-only−Γ NLL=+.0000048 [−.000251,.000266]，未检出Γ额外优势 | [summary](../results/e147/summary.json) |
| [E148](E148-native-checkpoint-order-forks.md) | DONE；C13/P32 | 原生次序响应KL由.002751降至.000893，小于末期自身漂移约.0071；L9互换NLL区间均跨0 | [summary](../results/e148/summary.json) |
| [E149](E149-native-system-source-cube.md) | DONE；C13/P32 | 全网络8格，backbone×MoE配对代价−.000061 [−.000503,.000242]，未检出交互 | [summary](../results/e149/summary.json) |

E144–E147无新训练；全量来源、donor、分区均保留。新C10–C12仅L1，旧C06–C09数字与等级不变；范围与当前解释见[README](../README.md)。本轮发现并在held之前修复CUDA库导入后的可见卡缓存问题，全部预检与成本保留。E147在E146结果之后、运行前新登记，没有倒写E146预设对照。

旧[摘要重算](../results/discussion_2026-10-26/reanalysis.json)仍为POST-HOC；新GPU结果和它分开。后续按证据与问题推进，不排日期或自动扩训练网格。

## 历史受控窗口 E120–E142

| 实验 | 问题 → 已记录结果 | 主要证据 |
|---|---|---|
| [E120](E120-moe-measurement-synthetic.md) | 合成已知答案能否校准路由/专家读数 → N1残差通过主要已知答案；N2在正交特征情形假阳性，均值钳制也有假阳性。 | [`summary_k2.json`](../results/e120/summary_k2.json) |
| [E121](E121-olmoe-routing-organization.md) | OLMoE 路由组织及专家差异如何分布 → L9有组织信号；旧POS置换p值已撤回，后由E122复核。 | [`r12_main_N1.json`](../results/e121/r12_main_N1.json)、[`pos_audit_20261025.json`](../results/e121/pos_audit_20261025.json) |
| [E122](E122-moe-routing-function-bridge.md) | 路由相似能否代替功能相似 → L9路由/输出偏相关约.46，但路由距离对held替换损失的偏相关仅.027 [−.036,.087]。 | [`summary.json`](../results/e122/summary.json)、[`c06_independent_cpu_audit.json`](../results/e122/c06_independent_cpu_audit.json) |
| [E123](E123-frozen-moe-feasibility.md) | 32M随机MoE能否复现原任务 → 固定终点NLL 2.736（原dense 2.494），固定预算下仍有拟合差；单seed负结果不决定整个方向。 | [`training_summary.json`](../results/e123/seed0_final/training_summary.json) |
| [E124](E124-frozen-moe-functional-reproducibility.md) | 功能指纹工具是否保留已知置换 → U已知映射逐项差0；A存在实测BF16数值地板；原多种子部分转由E130执行。 | [`numerical_permutation_control.json`](../results/e124/numerical_permutation_control.json)、[`calibration_known_permutation_matched.json`](../results/e124/calibration_known_permutation_matched.json) |
| [E125](E125-frozen-moe-data-coverage-control.md) | 更多训练输入覆盖能否修复随机MoE → 覆盖改善NLL约.691，固定128M终点仍有拟合差，这些连续质量读数不作研究准入线。 | [`three_condition_summary.json`](../results/e125/three_condition_summary.json) |
| [E126](E126-equal-capacity-moe-granularity-control.md) | 同容量宽专家top1是否改善 → 固定终点NLL 2.590，较E125 M-cover差+.0163；未消除拟合差，未据此自动关闭方向。 | [`granularity_comparison.json`](../results/e126/granularity_comparison.json) |
| [E127](E127-fixed-endpoint-predictive-fidelity.md) | 固定终点质量与预测分布保真是否一致 → 四个128M控制和E123失败参照的NLL/KL按同输入评估；相近NLL不视为同函数。 | [`M-cover.json`](../results/e127/M-cover.json)、[`G8-top1-cover.json`](../results/e127/G8-top1-cover.json) |
| [E128](E128-adequate-ce-epoch-recovery.md) | 固定512M CE终点能恢复多少 → NLL 2.559310，距原dense +.065497；该连续性能读数不作后续准入线。 | [`finalization.json`](../results/e128/finalization.json)、[`predictive_fidelity.json`](../results/e128/predictive_fidelity.json) |
| [E129](E129-teacher-distribution-feasibility.md) | 教师分布目标能否改善预测保真 → 固定128M NLL约2.564、KL约.0706；改变目标/监督量，不能与自然CE组混同。 | [`endpoint_summary.json`](../results/e129/endpoint_summary.json) |
| [E130](E130-fixed-budget-expert-reproducibility.md) | 固定CE预算下专家作用是否跨初始化重现 → 五初始化、七模型、17对全保留；预定cal-U映射下held U=.0161–.0465、A=−.0107–.0068，限定C07=L2。order1另有.4041%曝光多重集合差，撤回“纯次序”措辞。 | [`batch_summary.json`](../results/e130/batch_summary.json)、[`full_independent_audit.json`](../results/e130/full_independent_audit.json)、[`order_stream_exposure_audit.json`](../results/e130/order_stream_exposure_audit.json) |
| [E131](E131-transient-order-history.md) | 同父短暂重排且后续相同时，终点作用会否不同 → 62500终点U/A=.043/.004，自身late≈.999/.953；限定单父C08=L1。 | [`functional_batch.json`](../results/e131/functional_batch.json)、[`final_independent_audit.json`](../results/e131/final_independent_audit.json) |
| [E132](E132-function-guided-bank-grafting.md) | 按U/router映射移植专家能否保留使用效果 → 完整五环；U匹配/router的损失增量约+.011742/+.009243，zero约+.117107。 | [`bank_grafting.json`](../results/e132/bank_grafting.json) |
| [E133](E133-support-weighted-output-alignment.md) | 输出/支持加权对齐能否改善移植 → 输出匹配/支持加权损失增量约+.008227/+.011264；低标量指纹不自动意味不可组合。 | [`output_alignment.json`](../results/e133/output_alignment.json) |
| [E134](E134-expert-uniform-component-necessity.md) | 均匀专家分量在受控与原生模型中是否同样必要 → 受控五模型c-only损失+.0025–.0032，公开原生L9为+.0640；两类设置不可直接互推。 | [`necessity.json`](../results/e134/necessity.json)、[`readout_table.json`](../results/e134/readout_table.json) |
| [E135](E135-native-moe-function-constraint.md) | 随机同容量学生能否学原生L9总H→Y → 单seed自由router部分恢复U/A（约.099/.103），Dolma/POS KL仍约.0425/.0447；不是同函数证据。 | [`readout.json`](../results/e135/readout.json)、[`functional_independent_audit.json`](../results/e135/functional_independent_audit.json) |
| [E136](E136-native-router-assignment-oracle.md) | 提供并固定teacher路由是否改变恢复 → seed1 known-identity终点U/A约.2255/.3472，仍有函数差；gate信息与冻结/aux耦合共同变化。 | [`readout.json`](../results/e136/readout.json)、[`independent_audit.json`](../results/e136/independent_audit.json) |
| [E137](E137-native-component-support-reconstruction.md) | 当前被选支持内的内容是否恢复 → on内容仍有差异，并见分量误差抵消；不把缺失全归支持外。 | [`components.json`](../results/e137/components.json)、[`independent_audit.json`](../results/e137/independent_audit.json) |
| [E138](E138-fixed-assignment-student-reproducibility.md) | 三个固定gate学生的总函数与分量有多可重复 → Dolma componentVar=.031209、FP64sumVar=.015947、cross=−.015262；旧E136 seed1是已观察pilot。 | [`readout_table.json`](../results/e138/readout_table.json)、[`independent_audit.json`](../results/e138/independent_audit.json) |
| [E139](E139-matched-free-routing-cohort.md) | 配对expert初值但自由gate的三学生如何变化 → componentVar自由/固定=.072467/.031209，sumVar=.017869/.015947；CUDA RNG技术失败尝试保留，修复后固定终点全完成，限定C09=L1。 | [`readout_table.json`](../results/e139/readout_table.json)、[`independent_audit.json`](../results/e139/independent_audit.json)、[`device_setup_failure.json`](../results/e139/device_setup_failure.json) |
| [E140](E140-native-router-warmstart-cohort.md) | 同完整native初态解冻gate是否仍稳定 → trainable cohort componentVar=.032818，接近固定组.031209；此为整套解冻协议差，不是单一gate边界效应。 | [`readout_table.json`](../results/e140/readout_table.json)、[`independent_audit.json`](../results/e140/independent_audit.json) |
| [E141](E141-support-discordance-content-decomposition.md) | 贡献变异落在支持XOR还是共同on → free=.024964+.047503=.072467，fixed=0+.031209，trainable=.000540+.032278=.032818；三组完整、独立NumPy复算。 | [`readout_table.json`](../results/e141/readout_table.json)、[`independent_audit.json`](../results/e141/independent_audit.json) |
| [E142](E142-shared-random-router-cohort.md) | 共享一个未训练random gate能否稳定本cohort → S组componentVar=.043262，介于R=.072467与T=.032818/F=.031209；只新增Dolma，不新增POS/A，S/R共享已观察seed1；卡片、读数、三份审计与归档均为DONE。当时暂停是历史授权记录，后已获用户明确恢复MoE执行。 | [`readout_table.json`](../results/e142/readout_table.json)、[`independent_audit.json`](../results/e142/independent_audit.json)、[`archive_manifest.json`](../results/e142/archive_manifest.json) |

**解释边界：** 上列E138–142的变异是同一teacher/层/cache/有限训练预算下三个学生的有限cohort统计；文件/词形区间是输入评测不确定性，不是seed总体或协议处理效应区间。E141的XOR是观察到的支持分账，不是替换mask的因果效应。所有工作仍属已结项头线之外的人授权MoE驻留，未自动形成论文或新工作台状态。

## 备选设计：未取得模型结果

| 实验 | 状态 / 对应 | 主结果 | 直接证据 |
|---|---|---|---|
| [E143](E143-cross-model-routing-division.md) | PLANNED；备选 | 未执行模型测量，不进本批 | 原协议保留 |
