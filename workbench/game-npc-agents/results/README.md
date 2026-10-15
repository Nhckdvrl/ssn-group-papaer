# 结果清单

当前入口为[E69同图任务报告](../PROGRESS_REPORT_2026-10-15_MATCHED_TASKS.md)与文末最新结果。E50–62为已完成基线和诊断，阶段裁决不是预设论文故事。旧 [进度报告](../PROGRESS_REPORT_2026-10-14.md) 为历史暂停时的状态，旧小模型RL与全图漫游冻结。

- E50：[360原图实体资格](E50_native_snapshot_qualification.json)、[32B三seed一致人设](E50_32b_coherent_pilot_complete.json)、[32B阶段四格](E50_32b_cross_pilot_complete.json)、[27B阶段四格](E50_27b_cross_pilot_complete.json)。独立N=40图，不把分支数当独立样本。
- E50白盒：[27B native](E50_27b_stage_geometry.json)、[32B native](E50_32b_stage_geometry.json)、[27B同字段](E50_27b_common_readout_geometry.json)、[32B同字段](E50_32b_common_readout_geometry.json)。统一字段改变32B方向几何，角度不替代因果干预。
- E50：[渠道差异POST-HOC定位](E50_32b_memory_interaction_inspection.json)、[免费OpenCode盲检](E50_opencode_blind_quality.json)。Step5用于200 confirm数据v2构造和质检，构造/澄清盲检已完成。


- E55：[32B独立200图](E55_32b_independent_confirm.json)、[27B](E55_27b_independent_confirm.json)、[Gemma](E55_gemma_independent_confirm.json)，各5600分支/三seed；[自然请求与盲检数据](E55_natural_requests.jsonl)。
- E56：[32B同历史/阶段/事实](E56_32b_state_action.json)、[27B](E56_27b_state_action.json)、[Gemma](E56_gemma_state_action.json)，各2000原生分支与1200事实读数；阶段禁止动作范围能解释多数旧无行动。
- E57：[32B完整互动](E57_32b_native_interaction.json)、[27B](E57_27b_native_interaction.json)，各39世界×两P×三seed，目标事件与伙伴反向完成独立报告。消费实体不可逆，食物能量0不计生存收益。
- E58：[32B角色分量](E58_32b_components.json)、[27B](E58_27b_components.json)、[Gemma](E58_gemma_components.json)、[科研图](E58_persona_components.pdf)，各200图×六一致pack×两结构；只性格句仍影响物理交付。
- E59：三个模型各400固定未来历史更新、400独立事实读取及盲文本DATA标注均完成；raw `cache/runs/e59_*_fixed_future/`，不将I obliged/gave in等自动算物理完成。

E33：[完整四格收益](E33_single_interest_control.json)、[静态图](E33_utility_four_cells.svg)。60原生episodes／CPU55.84秒；单项C编辑的相对利益选择性两route均5/5base为正，但9/10均值单元low输入同时胜两目标、1/10相反，无明确偏好交叉。不是新机制证据；不追加明确句矩阵。短训练／身体相关性尚未排除。

已获得真实本地NPC模型与原生world结果；**C01为可行性；C02已独立确认至L2，C03仍为渠道交互pilot**。完整raw/权重不进Git，缓存为 `/home/xiang/.cache/game-npc-research/`，从各E##卡与scripts重建。阴性/作废/POST-HOC校对均保留。

| 实验 | 小结果与范围 |
|---|---|
| E01 | [source contracts](E01_source_contracts.json)，历史CPU检查，不是自然模型样本 |
| E07 | [CPU8/8](E07_cpu_controls.json)、[首个本地episode](E07_local_episode.json)、[6原生episodes](E07_six_native_episodes.json) |
| E08 | [来源pins/hashes](E08_sources.json)、[PCSP训练与split审计](E08_pcsp_protocol.json)，fixture gradient不冒充trained policy |
| E09 | [Qwen32](E09_qwen32_summary.json)、[Gemma12](E09_gemma12_summary.json)、[literal格式校对POST-HOC](E09_qwen_location_format_audit_POSTHOC.json)；单句location恢复解释不稳定 |
| E10 | [现代模型18episodes](E10_native_episode_summaries.json)、[parser递归归因POST-HOC](E10_parser_root_audit_POSTHOC.json) |
| E11 | [自然quest来源](E11_quest_source_summary.json)、[原生事件资格](E11_native_event_gate.json)；6执行/4材料，随机失败与非法分开 |
| E12 | [原生tool CPU控制](E12_native_tool_cpu_controls.json)、[12episodes](E12_native_episode_summaries.json)、[root归因POST-HOC](E12_parser_root_audit_POSTHOC.json)；普通强提示首次48/133→92/135，不是新机制 |
| E13 | [公开PCSP政策闭环](E13_pcsp_native_summary.json)；480动作+精确重放，分布内，不冒称unseen角色 |
| E14 | [36原生episodes](E14_light_native_summary.json)、[图簇汇总](E14_light_native_aggregate.json)；266/273合法，36/36作者目标event执行；首2条通信adapter错误已降级并保留 |
| E15 | [意图采样校准](E15_intention_sampling_analysis.json)、[成本](E15_intention_sampling_summary.json)；1152calls，意图差异未超过独立动作抽样噪声 |
| E16 | [共享消费资格](E16_resource_qualification.json)；8对原作者冲突图6对通过，无匹配human demo |
| E17 | [原生烟雾](E17_native_smoke.json)、[seed42](E17_readout_only_seed42.json)、[43](E17_readout_only_seed43.json)、[44](E17_readout_only_seed44.json)；冻结政策仅训练读出部分恢复 |
| E18 | [focal/joint/peer归因](E18_focal_attribution_summary.json)；原helper逐byte正控制、单pair/一trained seed，不宣称漂移 |
| E19 | [三训练种子同ID控制](E19_three_policy_aggregate.json)；白盒动作似然读出高于原η，Full/NoConsist平均差区间跨零，不是独立人物语义效度 |
| E20 | [36双角色资源episodes](E20_native_resource_summary.json)；70/70合法，36个消费事件/72个角色机会；0speech引出协议控制，不当人格失败 |
| E21 | [36episodes](E21_native_dialogue_summary.json)，78/78物理、102/102speech合法；36消费/72角色机会，不是新因子分解方法 |
| E22 | [权限/动作独立分支](E22_access_belief_summary.json)，704calls；权限机制未获支持，负向字段neutral正控制失败，联合证据降级 |
| E23 | [原500编码资格](E23_encoding_context_gate.json)，500/500余弦≥.999988；480行padding pool，正确pool消除跨batch变化，非新算法 |
| E24 | [原生utility](E24_encoding_native_utility.json)，6政策/6条件/3seed；fixed128收益约降2–14%，Full/NoCons无一致排序 |
| E25 | [cost/gradient gate](E25_cost_gradient_gate.json)、[30iter evaluation](E25_corrected_gradient_route_evaluation.json)，NoCons/仅η policy与utility同一，η1%→5%；Full8.667%，utility差CI跨零 |
| E26 | [public语义控制](E26_public_semantic_utility.json)、[正确短pilot](E26_corrected_pilot_semantic_utility.json)、[编码gate](E26_semantic_encoding_gate.json)；两政策均顺序敏感，已有强近邻，不称新发现 |
| E27 | [code/body归因](E27_code_body_attribution.json)，固定code削弱动作trait读出，C含state仍高；语义控制与环境信息并存 |
| E28 | [Full](E28_full_feature_frame.json)、[NoCons](E28_no_feature_frame.json)，真实辅助步坐标补偿utility效应小/CI跨零，负结果 |
| E29 | [原生成式NPC物理目标准入](E29_native_generative_npc_gate.json)，CPU16/16，单local episode安全饮用；6call、5/6合法，非人格机制证据 |

E06是统领基线准入卡，实际执行由E07及后续卡记录；旧E00/E02–E05不恢复。每个结果需要使用对应作者场景、模型、接口与度量口径，不能把所有动作数混作独立样本。

| E30 | [本地LLM规划与反思闭环](E30_local_goal_planner_gate.json)，plan_source=llm、18calls、4/5合法、首次safe drink；仅单episode来源准入 |

| E31 | [原人类双目标顺序资格](E31_human_goal_order_qualification.json)，1343配对/156同物品；145有≤4步见证、118三seed都有，非共同利益gold |

| E32 | [固定state语义选择性](E32_semantic_selectivity.json)，Full等义JS下降、保留90.7%不同角色响应；单训练seed，仅候选机制线索 |

E34：[三个seed的30轮固定读数](E34_checkpoint_0030.json)，100／300轮已全部完成；严格fresh AEC与原helper3200帧byte同一，不把早期方向变化当淘汰依据。E36：[同角度功能响应](E36_latent_response_i30.json)，CPU2.94秒，距离收缩、整体gain和方向响应可出现不同组合，保留逐人物差异继续研究。

- E35完整原三人NPC：[结果](E35_original_cast_complete.json)，1200帧／129本地calls／完整独立回放一致，成功与未观察的承诺分开。
- E37：[功能机会图](E37_functional_opportunities.svg)与[事后完整解释](E37_reward_opportunities_posthoc.json)，没有删去利益相容的状态。
- E39：[30轮](E39_direction_transport_i30.json)／[100轮](E39_direction_transport_i100.json)，跨角色方向与原生利益的局部因果诊断，不是自然文本能力或长期效用。
- E38：原生MeltingPot恢复及同seed剩余随机性见E38_native_cpu_v5.json；26训练与360完整episodes已完成，0付费API。

E34全部300轮：[完整三seed结果](E34_checkpoint_0300.json)。E36：[300轮局部响应](E36_latent_response_i300.json)；E37：[300轮固定状态](E37_matched_functional_i300.json)、[No300状态](E37_matched_functional_i300_states_no300.json)、[Full300状态](E37_matched_functional_i300_states_full300.json)；E39：[300轮全部方向交换](E39_direction_transport_i300.json)。全部预定seed/阶段保留。
E40：[身体反馈与C标签澄清](E40_need_dynamics_i300.json)，540个原生完整episode，无自设科学bar。E35：[原三人NPC自然重复](E35_natural_repeats.json)，两个额外1200帧episode，分别5/8自然对话。E38：[原编码数值资格](E38_embedding_qualification.json)，全部360政策episode评价完成。E41：[原训练路径byte控制](E41_original_path_control.json)，四条件三seed同预算300轮训练均完成。

E38：[全部26次训练来源](E38_all_training_completed.json)、[全部360原生episode](E38_native_policy_360_episodes.json)、[作者独立读出路径数值核对](E38_phase5_gradient_audit.json)。E41：[surface v1实现作废](E41_surface_v1_invalid.json)和[实际400训练改写资格](E41_actual_surface_encoding_qualification.json)；原错误不当科学零效应。E42：[CPU无损观测与物理控制](E42_cpu_interface.json)、[完整27B单局](E42_local_full_episode_pilot.json)，八卡强模型参考240局已完成。E37：[所有训练阶段科学图](E37_functional_opportunities_all_stages.svg)和[完整机会解释](E37_reward_opportunities_complete_posthoc.json)。

E42：[全部240完整原生episodes](E42_all_240_native_episodes.json)，48000本地决策／0fallback，四格逐角色和world保留；不单凭DD解释人物偏好。E41：[所有四条件／种子／阶段](E41_complete_factorial_all_stages.json)，12次300轮／9216万transitions完成。E44：[完整事实对照](E44_natural_context_complete.json)，三分支全部1200帧，不是新的论文题目。

E45：[三个自然case全部12格](E45_complete_persona_context_factorial.json)、[10个新后缀独立回放](E45_all_ten_new_branches_independent_replay.json)、[原输入重复变异POST-HOC](E45_fresh_native_nondeterminism_POSTHOC.json)。E46：[真实计划进度两格](E46_complete_grounded_progress.json)；E47：[较宽发言预算两格](E47_complete_dialogue_budget.json)；E48：[显式计划渠道消融两格](E48_complete_plan_update_ablation.json)，128次本地调用／两独立1200帧回放。角色指令、承诺、agenda与实际行程分开，lecture/sketch文字不计物理任务完成。即时新任务受修订渠道影响，兼容原agenda的后续出行仍发生；单case不推完整中介比例。

E49：[全部24条跨角色结果](E49_complete_cross_role_commitments.json)、[24条独立回放](E49_all_24_independent_replay.json)，1173新本地调用、8852新后缀帧。三共享自然历史／两不同角色描述，不作为24独立自然样本；位置与活动文本分列。显式修订影响部分路线／时机，其他case的意图记忆仍进入动作；146/147后缀根级parser合法，129结构化解析失败全部保留。用户要求本轮收尾后暂停实验。PARTIAL文件只作历史快照，最终以complete结果为准。

- E59：`E59_{32b,27b,gemma}_fixed_history.json`；`E59_literal_claim_audit.json`保留原盲标签并另列词义/对象核对。
- E60：`E60_{32b,27b,gemma}_common_commitment.json`和三模型`E60_*_cpu_replay.json`；共同承诺后的全部原生物理结果。
- Raw E59/E60/E61：`~/.cache/game-npc-research/runs/e59_*`、`e60_*_common_commitment`、`e61_*_common_history_direct`；含全部输入输出、原生轨迹及失败，checkpoint/原始大日志不入git。

- E61：`E61_{32b,27b,gemma}_common_history_direct.json`；1200完整分支，同一明确历史的直接决策及动作族/recipient组别。
- E62：`E62_cpu_qualification.json`；三模型`E62_*_native_recipient.json`和`E62_*_recipient_probabilities.json`。102图全部204当前合法Give CPU执行；每模型4896原生选择及2448实际解码概率，中间层参数选择不是完整NPC能力。白盒/raw在`runs/e62_*_recipient_*`。

## 本轮E50–62检查入口

总览见 [2026-10-15进度报告](../PROGRESS_REPORT_2026-10-15.md)，统计按原world graph聚类；分支、seed、帧和调用不充当独立N。

| 结果 | 内容 |
|---|---|
| `E50_*_coherent_pilot_complete.json` / `*_cross_pilot_complete.json` / `*_geometry.json` | 40图三家族一致P/局部交叉/匹配白盒 |
| `E51_*_status_pilot_complete.json` / `E52_*_binding_patch.json` / `E53_*_direct_status.json` | 完成状态、N=1词位patch、外加错误状态竞争解释 |
| `E54_step5_blind_text_labels.json` / `E54_text_action_associations.json` | 盲文本语义与POST-HOC关联，completed标签非物理真值 |
| `E55_*_independent_confirm.json` / [200自然请求](E55_natural_requests.jsonl) | 三模型200图×三seed，全部固定样本与质量分层 |
| `E56_*_state_action.json` | 普通结束阶段/状态/强动作与独立事实回答 |
| `E57_*_native_interaction.json` | 真正双角色动作、严格goal与源reverse路径、food_energy=0 |
| `E58_*_components.json` / [科学图](E58_persona_components.png) | 完整包/性格句/责任关系句；PNG/PDF/SVG |
| `E59_*_fixed_history.json` / `E59_literal_claim_audit.json` | 同未来承诺；保留原盲标签与词义/对象复核 |
| `E60_*_common_commitment.json` / `E61_*_common_history_direct.json` | 同承诺的生成更新/直接原生选择 |
| `E61_source_motivation_data.json` | 源动机与请求支持主张的盲抽取，逐字引文，非效用金标 |
| `E62_*_native_recipient.json` / `E62_*_recipient_probabilities.json` | 动作族条件化下recipient与局部内部干预/实际概率 |
| [分项成本](ROUND_PROGRESS_COSTS_2026-10-15.json) | final GPU runtime与记录在案的Plan响应usage，失败/恢复透明 |
| [本轮完成核对](ROUND_COMPLETE_2026-10-15.json) | 结果hash/数量/sham/本地进程与现场GPU读数；科学goal未标完成 |

## 最新审计后的E63/E64

- E63：`E63_{32b,27b,gemma}_dependency.json`均完整，各200独立图/100其他资产配对/5400 episode；`E63_*_plan_analysis.json`为POST-HOC原生计划回放。主表保留，总请求交付的观察窗口不同，资产间需另看`request_before_original_goal_POST_HOC`。
- E64：`E64_{32b,27b}_reciprocal.json`各9独立图/108双角色episode，真实取得、双向Give、最终归属、伤害/死亡分开；`E64_32b_transmission_guide.json`和`E64_32b_guide_comparison.json`为54条普通通信指令对照。27B的2死亡和1协议失败不剔除。
- 数据与源例：`E63_native_dependency_qualification.json`、`E64_native_reciprocal_qualification.json`、`E64_bilateral_source_qualification.json`；`E63_gemma_native_examples.json`公开三个说明性源图的全部两P/三规则/三seed。全部raw仍在同一cache，不入Git。

- [完整GPU/调用成本](E63_E64_ROUND_COSTS_2026-10-15.json)：主实验/控制16470条，另72条profile，13.167GPUh/104883实际本地调用；全部中断与失败计入。
- [E63科学图](E63_task_cooperation.png)、[E64科学图](E64_native_negotiation.png)，均另有PDF/SVG；[模型×check交互](E64_model_cue_interactions.json)、[reserve图级重叠](E63_reserve_overlap_audit.json)明确POST-HOC。

## E65/E66完成结果

- [最新进度报告](../PROGRESS_REPORT_2026-10-15_CONSTRAINT_PROBES.md)：先实验，暂缓论文。
- [E65行为主表](E65_gemma_scope.json)：79图、2370新轨迹、1422历史参考，全部五规则/两P/三seed，世界簇CI、原生计划回放；[CPU使用许可见证](E65_native_use_permission_witnesses.json)。
- [E65动作去向](E65_action_destinations_POST_HOC.json)：明确POST-HOC，合法block与重复错误分开；不改引擎/主结局。
- E66：[Gemma](E66_gemma_competition.json)、[32B](E66_32b_competition.json)，各948上下文，canonical完整菜单路径概率/固定top10；各`E66_*probability_calibration*.json`保留全部数值校验。
- 科学图：[E65](E65_constraint_scope.png)、[E66](E66_action_competition.png)，另有PDF/SVG；[完整成本](E65_E66_ROUND_COSTS_2026-10-15.json)含全部载入和校验。
- E63新增范围核对：[同轨迹任务＋合作](E63_task_cooperation_scope_audit.json)、[asset−generic](E63_asset_vs_priority_audit.json)，0新推理。
- 原始完整模型输出/状态/计划回放仍在同一cache的`runs/e65_gemma_scope_s{0,1}`、`e65_gemma_scope_analysis`、`e66_{gemma,32b}_competition`，通过同研究室账号访问/rsync；大日志不入Git。


## E67/E68完成结果

- [完整报告](../PROGRESS_REPORT_2026-10-15_RULE_EXECUTION.md)；E67 79图/9480执行，E68 109独立保留图/5628执行，全部两模型三seed，0API。
- `E{67,68}_{gemma,32b}_cross_summary.json`：完整cells、配对图簇CI、拒绝/随机失败与actual calls；[预注册预测表](E68_prediction_readout.md)明确记录P2跨模型未成立。
- `E{67,68}_*_plan_paths.json`：原生计划回放与所有正反向配对；说明案例在cache、附路径/hash；`E67_*_historical_reference.json`仅作历史参照。
- [E68资格](E68_native_qualification.json)、[曝光核对](E68_reserve_exposure.json)、[Gemma续跑验证](E68_gemma_resume_validation.json)；全部旧调用与已完成轨迹保留。
- `E68_*_block_targets_POST_HOC.json`：阻挡对象身份；[32B原子目标/作者动机样例](E68_32b_negative_transfer_examples_POST_HOC.json)明确POST-HOC，不改主读数。
- [独立配对效应图](E67_E68_figures/E68_reserve_paired_effects.png)、[全109图](E67_E68_figures/E68_reserve_behavior.png)、[41装备图](E67_E68_figures/E68_reserve_equip_behavior.png)，另有PDF/SVG；[全成本](E67_E68_ROUND_COSTS_2026-10-15.json)为6.556GPUh/51631调用，含中断。
- raw：`/home/xiang/.cache/game-npc-research/runs/e67_{gemma,32b}_cross_s{0,1}`、`e68_{gemma,32b}_reserve_s{0,1}`与`e68_native_reserve/snapshots.jsonl`。统计入口`native_rule_cross_report.py`、预测整理`native_reserve_predictions.py`；原始大文件不入Git。


## E69完整收尾
112同世界任务配对/3个源案例，主分支2760、适应性144，27519新本地调用/2.828GPUh/0API。主结果[E69 Gemma](E69_gemma_matched.json)、[32B](E69_32b_matched.json)，[科学图](E69_figures/E69_matched_task_effects.png)。控制[Gemma](E69_gemma_completion_controls.json)/[32B](E69_32b_completion_controls.json)保留全部恢复分支和动作改变；三世界不当总体样本。
[完整成本](E69_resource_account.json)、[同源子集POST-HOC](E69_prior_subset_POST_HOC.json)、[顺序物理见证POST-HOC](E69_sequential_native_witness_POST_HOC.json)、[Gemma结构化阶段POST-HOC](E69_gemma_structured_stages_POST_HOC.json)/[32B](E69_32b_structured_stages_POST_HOC.json)。初始资格/hash见E69_native_task_qualification.json；原始输入输出在cache/runs/e69_*，不入Git。

## E70–E73完整收尾

[完整报告](../PROGRESS_REPORT_2026-10-15_REQUEST_PRECONDITIONS.md)：117源作者Give图、两模型/三seed、23868分支，125126本地调用/2解析失败保留/12.847GPUh/0API。所有格均完成，分支/调用不是独立世界。

- E70：`E70_{gemma,32b}_complete.json`为全部9条件主表/配对CI，`*_paths.json`描述实际原物品及其他资源路径，`*_persona_interactions_posthoc.json`明确事后补充交互，原登记三重交互不替换。资格`E70_native_request_qualification.json`、`E70_graph_units.json`及各输入/profile检查。
- E71：`E71_{gemma,32b}_complete.json`无人索要，`E70_E71_{gemma,32b}_joined.json`同图有/无请求；整体上下文差，不是单词效应。
- E72：`E72_{gemma,32b}_complete.json`同本人对话的原生/扩展候选，真实错误消耗预算并反馈；`E72_native_feedback_check.json`保留原生见证与成对输入核对。
- E73：`E73_{gemma,32b}_complete.json`原生菜单+统一初始反馈，包含与两种E72接口全部配对；`E73_initial_feedback_check.json`核对反馈源真值/输入一致。相同事实暴露不等内部信念。
- [成本](E70_E73_resource_accounting.json)包括15job载入/推理/观察窗口，profile精确复用只计一次；[全实体读回](E70_E73_native_state_readback.json)核对23868条、10486源Remove、14379源Give，0标记不一致，嵌套归属敏感性无漏记。
- [去向图](figures/E70_first_disposition.png)、[机制/priority/阶段控制](figures/E70_paired_controls.png)、[无人索要对照](figures/E70_E71_persona_by_context.png)、[候选效应](figures/E72_candidate_effects.png)、[初始信息对照](figures/E73_initial_information.png)，均另有PDF/SVG。

raw仍在`/home/xiang/.cache/game-npc-research/runs/`的`e70_*`、`e71_{gemma,32b}`、`e72_{gemma,32b}_s{0,1}`、`e73_{gemma,32b}`；源状态`e70_native_request_qualification/snapshots.jsonl`。统计/读回/成本脚本及参数入口见报告，完整数据与模型日志不进Git。
