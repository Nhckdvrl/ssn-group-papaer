# 结果清单

E33：[完整四格收益](E33_single_interest_control.json)、[静态图](E33_utility_four_cells.svg)。60原生episodes／CPU55.84秒；单项C编辑的相对利益选择性两route均5/5base为正，但9/10均值单元low输入同时胜两目标、1/10相反，无明确偏好交叉。不是新机制证据；不追加明确句矩阵。短训练／身体相关性尚未排除。

已获得真实本地NPC模型与原生world结果；**C01保持L1，探索结果与基线证据分别记录**。完整raw/权重不进Git，缓存为 `/home/xiang/.cache/game-npc-research/`，从各E##卡与scripts重建。阴性/作废/POST-HOC校对均保留。

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

E34：[三个seed的30轮固定读数](E34_checkpoint_0030.json)，100／300轮运行中；严格fresh AEC与原helper3200帧byte同一，不把早期方向变化当淘汰依据。E36：[同角度功能响应](E36_latent_response_i30.json)，CPU2.94秒，距离收缩、整体gain和方向响应可出现不同组合，保留逐人物差异继续研究。

- E35完整原三人NPC：[结果](E35_original_cast_complete.json)，1200帧／129本地calls／完整独立回放一致，成功与未观察的承诺分开。
- E37：[功能机会图](E37_functional_opportunities.svg)与[事后完整解释](E37_reward_opportunities_posthoc.json)，没有删去利益相容的状态。
- E39：[30轮](E39_direction_transport_i30.json)／[100轮](E39_direction_transport_i100.json)，跨角色方向与原生利益的局部因果诊断，不是自然文本能力或长期效用。
- E38：原生MeltingPot恢复及同seed剩余随机性见E38_native_cpu_v5.json；CNN完整默认预算三seed×Full/No训练中，0付费API。
