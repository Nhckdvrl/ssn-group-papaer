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
| E14 | 真实人类脚本+原作者NPC独立目标12图×3seed运行中；首2条通信adapter错误已降级并保留，修复后全量重跑 |

E06是统领基线准入卡，实际执行由E07–E14记录；旧E00/E02–E05不恢复。每个结果需要使用对应作者场景、模型、接口与度量口径，不能把所有动作数混作独立样本。
