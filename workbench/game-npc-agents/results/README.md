# 结果清单

已获得真实本地NPC模型与原生world结果；**新科学增量仍0，C01仅L1可行性**。完整raw/权重不进Git，缓存为 `/home/xiang/.cache/game-npc-research/`，从各E##卡与scripts重建。阴性/作废/POST-HOC校对均保留。

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
| E25 | [三路完整训练iteration资格](E25_cost_gradient_gate.json)，NoCons/仅η policy逐byte同一；30iteration pilot运行中 |

E06是统领基线准入卡，实际执行由E07及后续卡记录；旧E00/E02–E05不恢复。每个结果需要使用对应作者场景、模型、接口与度量口径，不能把所有动作数混作独立样本。
