# 结果与复核入口

**实验保持暂停。** 整体解释见[项目报告](../PROJECT_PROGRESS_REPORT_2026-10-16.md)，主张范围见[CLAIMS](../CLAIMS.md)，跑前条件和完整结果说明见[实验卡索引](../experiments/README.md)。本目录保留最终统计、负结果、作废记录、来源/成本和必要审计，不把每个文件当一个独立发现。

## 最终统计

下表列主要结果入口。未列的同编号资格、分层、POST-HOC和审计JSON仍保留，可按E编号定位；同图分支、seed和调用不增加独立源图数。

| 研究阶段 | 主要结果 | 读数范围 |
|---|---|---|
| 早期原生测量 | [E14_light_native_aggregate](E14_light_native_aggregate.json)、[E15_intention_sampling_analysis](E15_intention_sampling_analysis.json)、[E22_access_belief_summary](E22_access_belief_summary.json) | 作者goal、抽样地板、访问控制及不支持结果 |
| 冻结PCSP/MeltingPot | [E34_checkpoint_0300](E34_checkpoint_0300.json)、[E38_native_policy_360_episodes](E38_native_policy_360_episodes.json)、[E41_complete_factorial_all_stages](E41_complete_factorial_all_stages.json)、[E42_all_240_native_episodes](E42_all_240_native_episodes.json) | 内部读出、真实策略与原奖励分别读，不恢复训练 |
| 校园后续 | [E49_complete_cross_role_commitments](E49_complete_cross_role_commitments.json)、[E49_all_24_independent_replay](E49_all_24_independent_replay.json) | 三条自然历史与局部干预，不作总体persona证据 |
| E50一致人物pilot | [E50_32b_coherent_pilot_complete](E50_32b_coherent_pilot_complete.json)、[E50_27b_coherent_pilot_complete](E50_27b_coherent_pilot_complete.json)、[E50_gemma_coherent_pilot_complete](E50_gemma_coherent_pilot_complete.json) | 40图发现性证据，非确认集 |
| E55独立确认 | [E55_32b_independent_confirm](E55_32b_independent_confirm.json)、[E55_27b_independent_confirm](E55_27b_independent_confirm.json)、[E55_gemma_independent_confirm](E55_gemma_independent_confirm.json) | C02；200独立图三seed |
| E56普通阶段对照 | [E56_32b_state_action](E56_32b_state_action.json)、[E56_27b_state_action](E56_27b_state_action.json)、[E56_gemma_state_action](E56_gemma_state_action.json) | 普通阶段结束说明解释旧无动作 |
| E57/E58互动与分量 | [E57_32b_native_interaction](E57_32b_native_interaction.json)、[E57_27b_native_interaction](E57_27b_native_interaction.json)、[E58_32b_components](E58_32b_components.json)、[E58_27b_components](E58_27b_components.json)、[E58_gemma_components](E58_gemma_components.json) | 人物、取得/消费与句子分量，不推完整利益 |
| E60/E61共同历史 | [E60_32b_common_commitment](E60_32b_common_commitment.json)、[E60_27b_common_commitment](E60_27b_common_commitment.json)、[E60_gemma_common_commitment](E60_gemma_common_commitment.json)、[E61_32b_common_history_direct](E61_32b_common_history_direct.json)、[E61_27b_common_history_direct](E61_27b_common_history_direct.json)、[E61_gemma_common_history_direct](E61_gemma_common_history_direct.json) | 计划与直接结构的信息表示不同 |
| E63任务/合作范围 | [E63_task_cooperation_scope_audit](E63_task_cooperation_scope_audit.json) | 目标物与其他物品分开；同轨迹共存与边际比例分开 |
| E65/E66规则范围与概率 | [E65_gemma_scope](E65_gemma_scope.json)、[E66_32b_competition](E66_32b_competition.json)、[E66_gemma_competition](E66_gemma_competition.json) | 实际轨迹与固定上下文canonical命令概率分开 |
| E67/E68实体与独立图 | [E67_32b_cross_summary](E67_32b_cross_summary.json)、[E67_gemma_cross_summary](E67_gemma_cross_summary.json)、[E68_32b_cross_summary](E68_32b_cross_summary.json)、[E68_gemma_cross_summary](E68_gemma_cross_summary.json) | C04/C05；41装备图、60其他物品图为109图子集 |
| E69同图任务 | [E69_32b_matched](E69_32b_matched.json)、[E69_gemma_matched](E69_gemma_matched.json)、[E69_source_coverage](E69_source_coverage.json) | 研究者任务指定、原作者动机与合法后续分别读 |
| E70–E74前提与后果 | [E70_32b_complete](E70_32b_complete.json)、[E70_gemma_complete](E70_gemma_complete.json)、[E71_32b_complete](E71_32b_complete.json)、[E72_32b_complete](E72_32b_complete.json)、[E73_32b_complete](E73_32b_complete.json)、[E74_32b_complete](E74_32b_complete.json)、[E74_gemma_complete](E74_gemma_complete.json) | 各编号另有Gemma结果；预测答案不作内部信念 |
| E75–E77推进与用途 | [E75_32b_complete](E75_32b_complete.json)、[E75_gemma_complete](E75_gemma_complete.json)、[E76_32b_complete](E76_32b_complete.json)、[E76_gemma_complete](E76_gemma_complete.json)、[E77_32b_complete](E77_32b_complete.json)、[E77_gemma_complete](E77_gemma_complete.json) | 固定历史/初态/当前人物与后果指派，不是两模块守恒 |
| E80响应玩家与技能 | [E80_32b_complete](E80_32b_complete.json)、[E80_gemma_complete](E80_gemma_complete.json) | 选择、技能实现与最终用途分别报告 |
| E81双方作者任务 | [E81_32b_complete](E81_32b_complete.json)、[E81_gemma_complete](E81_gemma_complete.json) | 普通强互动基线，不把物品交接当完整目的 |
| E83 Minecraft重建 | [E83_qwen_complete](E83_qwen_complete.json) | 单角色两路径，最终交换与条件履约分开；E82仅CPU见证 |
| E84独立目标与替代合作 | [E84_32b_complete](E84_32b_complete.json)、[E84_gemma_complete](E84_gemma_complete.json)、[E84_grounded_plans_POST_HOC](E84_grounded_plans_POST_HOC.json) | 32任务对/23图，所有成功/拒绝/不利后续保留 |
| E85真实转移/声称/新请求 | [E85_32b_complete](E85_32b_complete.json)、[E85_gemma_complete](E85_gemma_complete.json)、[E85_grounded_interactions_POST_HOC](E85_grounded_interactions_POST_HOC.json) | 18前史/9图，终局包含双方补交、自取和接取；问答不作内心读数 |

## 来源、成本与可靠性

- `*_freeze.json`、`*_qualification.json`、`*_input_check.json`记录原数据/代码/模型及首运行前的资格；`*_audit.json`、`*_native_state_readback.json`记录独立核对。旧无效版本与失败不能当科学结果，亦不删除以制造幸存样本。
- 每轮`*_cost_accounting.json`、`*_resource_account*.json`及合账文件记录真实调用/载入/中断/等待；项目报告按原口径分段汇总，不编造全历史精确总账。
- E85最终完整结果只取四个recover目录；旧profile/partial只保留谱系和成本。独立复算见[E85统计审阅](E85_statistical_independent_review.json)、[32B全流核对](E85_32b_complete_audit.json)、[Gemma全流核对](E85_gemma_complete_audit.json)。
- 图保留PNG预览和PDF向量版；已有两种格式的同图SVG已清理。仅有SVG的历史图继续保留。

## 原始资产与代码

完整raw、每次模型输入输出、世界、source/model pin与权重在`/home/xiang/.cache/game-npc-research/`，通常为`runs/e<编号>_*`；具体路径以实验卡和manifest为准。GitHub的轻量结果不是完整raw备份。

当前复算代码见[scripts](../scripts/README.md)。已冻结的旧执行代码、一次性启动器和旧阶段报告不再堆在工作树；其精确清理前版本可由Git `af7564ff`恢复。原manifest中的SHA继续指向当时原文件，不会为了目录整理重写科学输入或哈希。
