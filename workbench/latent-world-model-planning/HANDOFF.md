# HANDOFF — latent-world-model-planning

状态：**PROPOSED / literature-hardened / execution-ready / no local experiment yet**。  
本文件只保留交接 authority；完整启动词见 [LOCAL_AGENT_PROMPT](LOCAL_AGENT_PROMPT.md)，实验细节见 [EXPERIMENT_PROGRAM](EXPERIMENT_PROGRAM.md)。

## 0. 先不要重新找题

第二轮调查已经把 direct-neighbor ownership 和可执行矿层写进：
- [PAPER_LINEAGE](PAPER_LINEAGE.md)
- [PROBLEM_METHOD_MAP](PROBLEM_METHOD_MAP.md)
- [POSITIONING](POSITIONING.md)

本地 agent 的职责是**用真实 baseline/measurement 推翻、保留或发展这些 seed**，不是回到“想一个新 loss / 查一个 gap / 重新写综述”。

必须遵守根目录 `AGENTS.md`、`RESOURCES.md` 和全局 ACTIVE 容量；不得自行改本 workbench 状态。

## 1. authority 顺序

出现冲突时：
1. `AGENTS.md` / `workbench/EXECUTION.md`
2. experiment card 跑前注册内容
3. `POSITIONING.md` 的 claim ownership
4. `EXPERIMENT_PROGRAM.md`
5. 本文件
6. 早期 `LATENT_PLANNING_SURVEY.md`

论文 factual claim 回原文；二手总结不能覆盖原文限定。

## 2. baseline / environment 两层

**Native layer：** 每个官方 repo 独立环境，固定 commit/checkpoint/config，先复现官方 protocol。  
**Common audit layer：** 统一 manifest、candidate trace、oracle replay、result schema；只有 native baseline 可信后适配。

不要把“统一平台”理解成先重写所有模型到 stable-worldmodel。不要因依赖冲突破坏可复现原生环境。

## 3. 执行门

### Gate 0 — E00
只证明数据、checkpoint、planner、env、success checker 与资源成本可追溯。单 GPU、低并发；先 smoke，不跑满默认 epochs。

### Gate A — E01
至少一个 LeWM 正式 baseline + 一个 contact-rich task；candidate logger 是旁路；restore/replay 可测。得到真实 train/eval/I/O cost。

### Gate B — E02
复制已知 decision-alignment measurement：random/mid/elite candidates、real endpoint vs predicted endpoint、fixed-pool regret。工具测不到已知 effect 时不许做新机制 claim。

### Mining
- **I01:** E03 → E04（第一优先）。
- **I02:** E05；E01 logger 可信后可在另一独立节点并行。
- **I03:** E06 → E07；不做大 leaderboard。
- **I04:** 只是 E02 calibration asset。
- **I05:** PARKED，满足重开条件才动。

## 4. 最小 shared schema

run/episode 必须记录：
```text
code_commit, dependency_lock, hardware_id, model_family, checkpoint_sha256
train_seed, data_split_seed, eval_seed, planner_seed
dataset_revision, episode_partition_hash, local_transition_hash
one_step_window_manifest_hash, long_pair_manifest_hash
observation/preprocess, action_units/bounds, history, frame_skip/action_block
planning_horizon, replanning_interval, goal_source, success_checker
planner_type, samples, iters, cost_reduction, auxiliary_weights
success, task_native_cost, env_steps, wall_clock, model_calls, peak_vram, data_wait
```

candidate audit 额外保存：
```text
decision_id, planner_iter, candidate_id, proposal_source, action_seq
pred_cost, real_endpoint_latent_cost, real_task_utility
support/uncertainty/consistency scores (if defined), selected, elite_rank
```

## 5. attribution 规则

固定 candidate pool 时，优先依次问：
1. pool 里有没有真实好的 action？
2. encoded real endpoint 能否正确排序？
3. predicted endpoint 是否把排序翻转？
4. true dynamics 能否救？
5. nearby subgoal diagnostic 能否救？

因此：
- pool ceiling 低 → 不能只怪 score；
- real endpoint 排序坏 → 不能只怪 dynamics；
- true dynamics 仍坏 → 不能只怪 predictor；
- internal consistency 高 → 不能直接称 environment-realizable。

## 6. I01 识别要求

I01 的价值来自**控制 behavior geometry 与 environment geometry**，不是普通 dataset ablation。

E03：
- raw transitions 相同；
- one-step/local window manifest **hash 相同**；
- 只改 long-pair / episode metadata；
- RC-aux/TD-JEPA target 必须有预期 shift；
- LeWM local prediction作 negative control。

E04：
- shortest-ish / detour / route-mixture；
- environment dynamics 与 goal 分布相同；
- 尽量匹配 state/edge support；
- navigation 才可用 exact shortest-path oracle；
- 必须连接到 candidate ranking/regret/closed-loop consequence。

只有“head 学成了不同值”不够。

## 7. 多卡的正确用法

一个 checkpoint 训练完成后，可把：
- eval groups；
- planner budgets；
- goal-distance bins；
- candidate audits；
- dataset variants；
- train seeds

分派到独立 GPU。不要跨节点 all-reduce。数据先 stage 到 node-local disk，再逐步加并发测 `data_wait`；弱 I/O 下 GPU 多不等于 job 越多越快。

## 8. 什么时候方法化

方法只能跟随已证实 bottleneck：
- I01 → 优先 local/Bellman/quasimetric consistency、interval/multi-route target、connectivity/local structure；
- I02 → support-aware proposal/trust-region/uncertainty gate，但先看 PLDM/ACID 等简单 baseline 是否已经解决；
- I03 → 只有可预测 regime 才设计 adaptive rule。

任何方法必须另立 experiment card，并用 validation 选 hyperparameter。

## 9. 写回与人审

每次运行后：
- experiment card 结果；
- 真痛点才建 P##；
- 有证据才建/升级 C##；
- `logs/YYYY-MM-DD.md`；
- 小步 commit/push。

触发人审：首个科学 C##→L2、I01/I02/I03 出现决定性结果、需要改变 ACTIVE 调度、或两个 lead 连续被近邻/平凡 baseline 吸收。

**不要每跑一个 job 就停下来等指令。** 在卡片决策表范围内自主推进。