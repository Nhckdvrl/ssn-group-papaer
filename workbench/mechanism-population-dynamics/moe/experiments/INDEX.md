# MoE 实验索引 E120–E147（2026-10-26）

这是已有证据与新设计的导航。E120–E142 是已有结果；用户在讨论后确认 [当前方向](../RESEARCH_DIRECTION.md)，本轮用户进一步授权执行，E144–E147已完整获得新读数（E147为E146后新登记的强对照）。E143 保留备选。大模型、缓存和原始数组以原卡及归档清单中的路径为准；下列历史数字不因新设计而更改，主张等级不变。

## 已有实验 E120–E142

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
| [E142](E142-shared-random-router-cohort.md) | 共享一个未训练random gate能否稳定本cohort → S组componentVar=.043262，介于R=.072467与T=.032818/F=.031209；只新增Dolma，不新增POS/A，S/R共享已观察seed1；卡片、读数、三份审计与归档均为DONE。用户要求暂停新增实验。 | [`readout_table.json`](../results/e142/readout_table.json)、[`independent_audit.json`](../results/e142/independent_audit.json)、[`archive_manifest.json`](../results/e142/archive_manifest.json) |

**解释边界：** 上列E138–142的变异是同一teacher/层/cache/有限训练预算下三个学生的有限cohort统计；文件/词形区间是输入评测不确定性，不是seed总体或协议处理效应区间。E141的XOR是观察到的支持分账，不是替换mask的因果效应。所有工作仍属已结项头线之外的人授权MoE驻留，未自动形成论文或新工作台状态。

## 本轮执行与备选

| 实验 | 状态 / 对应 | 主结果 | 直接证据 |
|---|---|---|---|
| [E143](E143-cross-model-routing-division.md) | PLANNED；备选 | 未执行模型测量，不进本批 | 原协议保留 |
| [E144](E144-fixed-gate-recombination.md) | DONE；C10/P31 | 固定gate拆来源ΔNLL+.002061、ΔKL+.002441；正交叉CI | [summary](../results/e144/summary.json) |
| [E145](E145-history-gate-bank-cross.md) | DONE；C11/P27–29 | 同接收者bank代价S−R=−.005222；共同gate C_S/C_R=.037892/.055990 | [summary](../results/e145/summary.json) |
| [E146](E146-grouped-recombination.md) | DONE；条件满足后执行 | Γ定8×8组ΔNLL=.000681，3随机同大小组.001690–.002151 | [summary](../results/e146/summary.json) |
| [E147](E147-gate-coactivation-group-control.md) | DONE；新登记强对照 | gate-only−Γ NLL=+.0000048 [−.000251,.000266]，未检出Γ额外优势 | [summary](../results/e147/summary.json) |
| [E148](E148-native-checkpoint-order-forks.md) | DONE；C13/P32 | 原生次序响应KL由.002751降至.000893，小于末期自身漂移约.0071；L9互换NLL区间均跨0 | [summary](../results/e148/summary.json) |
| [E149](E149-native-system-source-cube.md) | DONE；C13/P32 | 全网络8格，backbone×MoE配对代价−.000061 [−.000503,.000242]，未检出交互 | [summary](../results/e149/summary.json) |
| [E150](E150-native-mature-routing-protocol-cross.md) | DONE；C14/P32 | 完整MoE互换平均+.127787 NLL；B native裁剪代价低.738449，B router单独不转移此收益，D/R/S参与 | [summary](../results/e150/summary.json) |
| [E151](E151-native-pruning-selectivity-necessity.md) | RUNNING；C14/P32 | 无新训练，全R/全S零化与3固定随机32预算；结果待完 | [plan](../results/e151/plan.json) |

E144–E147无新训练；全量来源、donor、分区均保留。新C10–C12仅L1，旧C06–C09数字与等级不变；范围与当前解释见[README](../README.md)。本轮发现并在held之前修复CUDA库导入后的可见卡缓存问题，全部预检与成本保留。E147在E146结果之后、运行前新登记，没有倒写E146预设对照。

旧[摘要重算](../results/discussion_2026-10-26/reanalysis.json)仍为POST-HOC；新GPU结果和它分开。后续按证据与问题推进，不排日期或自动扩训练网格。
