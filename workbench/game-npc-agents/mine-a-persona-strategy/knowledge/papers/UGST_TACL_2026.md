# Goal Alignment in LLM-Based User Simulators for Conversational AI — TACL 2026

- 来源：[正式论文及PDF](https://aclanthology.org/2026.tacl-1.38/)；[作者代码](https://github.com/Shuhaibm/user_simulator_goal_alignment)，pin `43acdde8de32e93a717a9394099c544f09e763b0`。本地PDF `/tmp/npc_ugst.pdf`，代码缓存 `sources/ugst_goal_alignment/`。
- 已读范围：正文§3–6、Table1–5、Appendix C/D的状态生成和更新协议、F评价入口；发布代码的goal tracker、计分函数、生成agent与interaction分支。未复现作者SFT/GRPO或其judge。
- 已有主张：将profile/policy、task objectives、requirements和preferences分开追踪，以当前goal state提示、冷启动SFT及UGST reward的GRPO改善用户模拟器。不能将“当前任务进度提醒／角色与任务分开”称新方法。
- 评价事实：profile/policy从ALIGNED不可逆变MISALIGNED；preference在表达后变ALIGNED；任务/要求按INCOMPLETE、ATTEMPTED、COMPLETE更新，后两状态都计成功，理由是模拟用户不应因代理／系统失败被罚。这不是外部世界任务已完成的口径。Table4人类与LLM最终状态总体一致85.7%、policy72.7%，不能替代实体动作真值。
- 源码事实：`eval/user_goal_state_tracker.py:get_user_goal_state_score`确认ATTEMPTED/COMPLETE同计通过，状态更新以对话和LLM分类为依据。发布`LiteLLMUser.act`仅有not-UGST生成分支；UGST flag构造tracker，但act没有对应返回；`BaseInteraction`该flag却期望response/state/score三元组。全发布Python搜索未找到另一User实现，未见训练脚本。
- 我们的解释：当前公开代码不足以直接恢复完整三阶段，但论文goal decomposition／progress steering／GRPO的主张归属仍成立。竞争解释：相关训练或生成分支可能未发布／在另一版本；未核对私人资产，不能借发布缺口否定科学结果。
- 与矿区A距离：profile/policy已含persona，进度提示也并非所有类别一致上升。我们的合法动作/world delta、承诺是否改变已有agenda是另一个证据层次；仅换环境或评价口径不能自动成为贡献。E46承认普通progress解释，E49需跨角色的实际因果链证据。
