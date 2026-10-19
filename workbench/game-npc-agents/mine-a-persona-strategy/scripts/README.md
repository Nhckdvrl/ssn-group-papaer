# 代码与复算入口

**矿区A已终止。** 本页只列历史代码与复核用途，不是启动队列；不运行模型、训练、引擎或API。条件、source/model pin、随机种子、schema和成本以[实验卡](../experiments/README.md)及raw manifest为准，失败复盘见[终止总结](../CLOSEOUT.md)。

## 当前保留代码

保留执行、最终统计、独立核对和共享模块的原文件名。2026-10-18整目录迁入矿区A，只有两份POST-HOC脚本为消除旧绝对路径而改用自身位置定位；其余148份程序保持原字节，未更改研究计算。历史冻结SHA仍按原Git版本复现，见[数据迁移说明](../data/README.md)。一次用过不等于无用：可重算最终读数、或被后期代码导入的文件保留。

| 用途 | 主要入口 | 范围 |
|---|---|---|
| 原生接口 | [native_actioncastle.py](native_actioncastle.py)、[native_tool_loop.py](native_tool_loop.py)、[strong_native_baseline.py](strong_native_baseline.py)、[viewpoint_control.py](viewpoint_control.py) | 早期文件仍是后期实际依赖，不能按年代删除 |
| 快照与一致人物 | [commitment_snapshots.py](commitment_snapshots.py)、[commitment_decisions_v2.py](commitment_decisions_v2.py)、[commitment_behavior_report.py](commitment_behavior_report.py) | 原图、阶段输入和配对读数 |
| E55–E62 | [native_role_confirmation.py](native_role_confirmation.py)、[native_state_readout.py](native_state_readout.py)、[native_components_report.py](native_components_report.py)、[native_recipient_report.py](native_recipient_report.py)、[native_recipient_probability_report.py](native_recipient_probability_report.py) | 独立确认、普通对照、分量与白盒正负结果 |
| 共享执行/状态 | [native_dependency_roles.py](native_dependency_roles.py)、[native_rule_execution.py](native_rule_execution.py)、[native_reciprocal_negotiation.py](native_reciprocal_negotiation.py)、[native_reciprocal_deathsafe.py](native_reciprocal_deathsafe.py) | 后期仍导入其client、健康/存活和执行函数；并非一次性包装器 |
| E67–E69 | [native_rule_cross_report.py](native_rule_cross_report.py)、[native_matched_task_execution.py](native_matched_task_execution.py)、[native_matched_task_report.py](native_matched_task_report.py)、[native_task_completion_report.py](native_task_completion_report.py) | 阶段交叉、任务指定与适应性控制 |
| E70–E76 | [native_request_precondition_report.py](native_request_precondition_report.py)、[native_consequence_report.py](native_consequence_report.py)、[native_retrieval_report.py](native_retrieval_report.py)、[native_fixed_dialogue_report.py](native_fixed_dialogue_report.py) | 保留执行、来源资格和最终读数依赖链 |
| E77 | [native_dialogue_outcome_execution.py](native_dialogue_outcome_execution.py)、[native_dialogue_outcome_report.py](native_dialogue_outcome_report.py)、[native_dialogue_outcome_report_fast.py](native_dialogue_outcome_report_fast.py) | fast是最终操作入口，原报告定义也保留 |
| E80/E81 | [native_interactive_execution.py](native_interactive_execution.py)、[native_interactive_skills.py](native_interactive_skills.py)、[native_interactive_report.py](native_interactive_report.py)、[native_cooperation_episodes.py](native_cooperation_episodes.py)、[native_cooperation_report.py](native_cooperation_report.py) | 响应玩家、可靠技能与双方原目的 |
| E82/E83 | [minecraft_native_cooperation.mjs](minecraft_native_cooperation.mjs)、[minecraft_npc_quest.mjs](minecraft_npc_quest.mjs) | CPU物理见证及明确角色任务重建 |
| E84 | [native_independent_goal_episodes.py](native_independent_goal_episodes.py)、[native_independent_goal_report.py](native_independent_goal_report.py)、[native_independent_goal_audit.py](native_independent_goal_audit.py) | 完整互动、读数和独立全流核对 |
| E85 | [native_partner_performance.py](native_partner_performance.py)、[native_partner_performance_compat.py](native_partner_performance_compat.py)、[native_partner_performance_report.py](native_partner_performance_report.py)、[native_partner_performance_audit.py](native_partner_performance_audit.py)、[native_partner_performance_grounded_readback.py](native_partner_performance_grounded_readback.py) | 原driver、最终兼容层与统计/全流核对都是复现所需 |
| 冻结线纯复算 | [meltingpot_policy_report.py](meltingpot_policy_report.py)、[pcsp_native_llm_report.py](pcsp_native_llm_report.py)、[pcsp_functional_opportunity_report.py](pcsp_functional_opportunity_report.py)、[penn_cross_role_report.py](penn_cross_role_report.py) | 只读既有raw重算，不恢复训练、漫游或采样 |

其他同族执行、报告、来源资格和图代码仍在本目录。模型/引擎代码与纯report须区分；文件存在不代表当前获准执行，不能盲目导入整个目录。统计定义、失败、分层与科学输出未因清理改写。

## 已清理的历史代码

73个旧入口已退出当前树：冻结PCSP/MeltingPot执行/训练36个，校园执行/回放/worker18个，旧版启动/续跑/preflight9个，已完成DATA生成/收集/补缺10个。最终JSON、成本、负结果、原数据和代码SHA保留；删除执行文件不等于关闭idea或否认原实验。

**精确清理前版本：`af7564ff2a8b74fc5ae0c8d9bda38d6e953414ef`。** 所有删除文件都来自已上传main的该版本，不另建archive目录。需要旧代码、旧阶段报告或旧接手页时，直接读Git：

```bash
# 只读某个原文件；文件名可替换为实验卡中的名字
git show af7564ff:workbench/game-npc-agents/scripts/pcsp_full_budget_finish.py

# 完整旧workbench导出到独立目录，不恢复到当前工作树
mkdir -p /tmp/npc-reproduction
git archive af7564ff workbench/game-npc-agents | tar -x -C /tmp/npc-reproduction
```

可用`git diff --name-status af7564ff..HEAD -- workbench/game-npc-agents`核对删除清单。旧卡/manifest中的路径和hash记录当时来源，不为目录整理替换成新科学输入。大raw与模型仍在既有cache，Git导出不包含这些资产。

## 环境与权限

环境、缓存、API与节点规则统一见[BASELINES](../BASELINES.md)和[AGENTS](../AGENTS.md)，不再重复维护。Step历史DATA调用脚本已退出当前树，最终数据/用量/raw指针仍保留。当前不启动模型、训练、引擎回放或API。
