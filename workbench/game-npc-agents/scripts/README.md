# 实验脚本接手说明

**用户已恢复，并冻结旧小模型RL和全图漫游线。** 本轮E50–62结果及范围见 [进度报告](../PROGRESS_REPORT_2026-10-15.md)。本表给复算入口，旧脚本存在不授权重新运行；模型、source pin、种子、数据与hash以卡片和raw manifest为准。

| 用途 | 当前入口 | 范围 |
|---|---|---|
| 原生冲突快照 | `commitment_snapshots.py` | E50公开source graph与两条实体路径；40/200/120拆分 |
| 一致人设／阶段交叉 | `commitment_decisions_v2.py`、`commitment_behavior_report.py` | E50短序贯、四渠道、图簇统计；v1原始结果保留 |
| 完成状态机制 | `commitment_status_intervention.py` | E51同承诺/状态，pending/completed及goal/state对照 |
| 三阶段白盒 | `commitment_residuals.py`、`commitment_residual_report.py` | E50 native/common action读出；非仅凭角度论机制 |
| 数据构造与盲检 | `step_plan_data.py`、`commitment_quality_review.py` | Step5固定Token Plan；OpenCode明确免费；不作NPC或runtime裁判 |
| 中断续跑 | `commitment_decisions_resume.py` | 精确匹配原调用cassette，不丢弃已生成seed |
| 独立确认/状态控制 | `native_role_confirmation.py`、`native_state_readout.py` | E55/E56，具体命令以卡片为准 |
| 角色分量与互动 | `native_persona_components.py`、`native_food_interaction.py` | E58/E57，原生物理后果与源目标 |
| 同一承诺 | `fixed_history_state.py`、`common_commitment_native.py`、`common_history_direct.py` | E59–61，事实回答不写回策略 |
| 接收者白盒/报告 | `native_recipient_patch.py`、`native_recipient_report.py` | E62全合法Give、原生状态，局部中间层交换 |
| 实际解码概率 | `native_recipient_probability_readout.py`、`native_recipient_probability_report.py` | E62恰好两叶的完整命令概率，与suffix语言分数分开 |
| 源动机DATA | `source_motivation_data.py`、`source_motivation_recover.py`、`source_motivation_collect.py`、`source_motivation_report.py` | E61盲抽取/逐字引用；仅补缺行，不定义效用或gold动作 |
| 成本复算 | `round_progress_costs.py` | final runtime分项及Step响应ID去重；不是整项目时长/独立账单 |
| 原生NPC接口 | `native_actioncastle.py`、`local_component_client.py` | 原parser与本地模型adapter；cloud constructor禁止 |
| 原三角色校园episode | `native_penn_social.py`、`penn_social_repeats.py` | E35原作者cast与1200帧；完整raw不进Git |
| 完整原记录回放 | `penn_strict_replay_complete.py`、`penn_branch_verify.py` | 零模型重放；不是重新采样 |
| 人物／原责任四格 | `penn_persona_goal_adoption.py` | E45三个原episode，conversation组件干预 |
| 当前计划执行位置 | `penn_plan_progress_fork.py` | E46；plan状态不是物理任务完成证明 |
| 发言预算控制 | `penn_dialogue_budget_fork.py` | E47；两路512，不等于所有actor都512 |
| 教授显式计划渠道 | `penn_plan_update_ablation.py`、`penn_plan_update_verify.py` | E48窄干预及同干预独立回放 |
| 两其他角色四格 | `penn_cross_role_worker_v2.py`、`penn_cross_role_commitments_v2.py` | E49六处境×四条件；每worker复用一个模型 |
| E49回放／报告 | `penn_cross_role_verify.py`、`penn_cross_role_report.py` | 前者零模型原生回放，后者只读JSON，不加载引擎／模型 |
| PCSP原300轮 | `pcsp_full_budget_finish.py` | E34；CPU快于单GPU的小MLP，不为占卡改变路径 |
| 普通覆盖／绑定对照 | `pcsp_coverage_finish.py`、`pcsp_surface_train_codes.py` | E41有效v2资格与四条件，三种子全300轮 |
| MeltingPot | `meltingpot_source_train.py`、`meltingpot_policy_episodes.py`、`meltingpot_policy_report.py` | E38；用现有lightwam与隔离overlay |

历史失败文件保留用于追溯，不作当前运行入口：E44 `penn_duty_context_fork.py`未覆盖freechat提醒，统一事实条件用`penn_duty_context_fork_v2.py`；E49 `penn_cross_role_commitments.py`／`penn_cross_role_worker.py`只做过CPU v1，Diego同帧切入失败，GPU一律使用v2。不能将失败实现的“零效应”当科学结果。

运行环境：NPC复用 `/home/xiang/miniconda3/envs/fgvd/bin/python`，overlay `e50-legacy-renderer:deps` 恢复旧LIGHT help对emoji1.7.0的依赖，不改变物理规则。CPU回放显式设 `CUDA_VISIBLE_DEVICES=''`、BLAS线程1。原始数据／模型缓存见manifest。启动前核GPU空闲，总量≤8，禁止云fallback；本表旧训练入口仅供历史重建，不授权恢复。
