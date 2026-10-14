# 实验脚本接手说明

**用户要求本轮收尾后暂停实验。** 这里用于读数据和复现定位，不是自动启动清单。先读 [进度报告](../PROGRESS_REPORT_2026-10-14.md) 和对应 [实验卡](../experiments/)；模型、source pin、种子、数据与hash以卡片和raw manifest为准。

| 用途 | 当前入口 | 范围 |
|---|---|---|
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

运行环境：NPC和Mini-Inzoi复用 `/home/xiang/miniconda3/envs/fgvd/bin/python`，NPC overlay `/home/xiang/.cache/game-npc-research/deps`。CPU回放显式设 `CUDA_VISIBLE_DEVICES=''`、BLAS线程1。缓存位置为 `sources/`、`runs/` 和HuggingFace snapshots，详见实验manifest。暂停后不启动训练／新推理；将来恢复时先核GPU空闲，白天总量≤8，禁止云fallback。
