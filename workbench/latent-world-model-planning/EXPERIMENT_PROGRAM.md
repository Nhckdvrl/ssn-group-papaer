# Experiment Program — 给本地 agent 的“可大量铺开但不乱扫”执行图

更新：2026-10-02。  
本文件把文献地图变成可执行 workbench。**实验卡是 authority；本文件是调度/复用设计。**  
资源约束读 `../../RESOURCES.md`：单卡/单节点独立 job 优先，不能依赖跨节点 all-reduce 或高速共享盘。

## 0. 总目标

先建一个可以回答下面问题的公共日志层：

> 一次失败究竟发生在 data supervision、representation metric、recursive dynamics、candidate proposal、search selection、temporal target，还是 environment execution？

然后只对有信息增益的轴并行，不跑全笛卡尔积。

---

## 1. 第一阶段共享 substrate：一次建设，后面所有 idea 复用

### S0 原生复现
- LeWM：TwoRoom smoke → PushT / Cube 至少一项正式 reproduction。
- 一个异质 baseline：优先官方 DINO-WM/JEPA-WM checkpoint，或 stable-worldmodel 已可直接接入的 PLDM。
- 直接 successor：RC-aux（因为 I01 要用其 trajectory reachability）。
- 若代码就绪且接入成本低：TD-JEPA。
- SALT/Temporal Straightening/IMWM/SAGE 等按具体 lead 接入，不在 S0 一次性全装。

### S1 candidate trace schema
每个 planning decision 输出：
```text
episode_id, step, start_obs_hash, goal_obs_hash
planner_iter, candidate_id, proposal_source
action_seq, action_bounds_ok, action_norm, action_smoothness
pred_terminal_latent_hash, pred_goal_cost
(optional) reachability/TD/ACID/uncertainty/support scores
selected, elite_rank
env_restore_id
real_terminal_state/obs_hash, real_task_cost, success   # audited candidates only
```

### S2 train/sample manifest
每个 model checkpoint 保存：
```text
dataset_revision
episode_partition_hash
local_transition_hash
one_step_window_manifest_hash
long_pair_manifest_hash
behavior_policy_tag
state/edge occupancy summary
code commit + resolved config + seeds
```

没有这些 hash，I01 不允许写因果解释。

### S3 oracle execution harness
在 simulator 上验证：
1. snapshot/restore 或 reset+replay deterministic enough；
2. 同 candidate 重放得到 task cost 波动 floor；
3. planner RNG 与 env RNG 分开；
4. privileged state 只进入 diagnostic file，不进入 pixel model input。

### S4 common result table
episode-level parquet/jsonl（大文件不入 git），摘要 CSV/markdown 入 `results/`：
```text
model, checkpoint, train_seed, eval_seed, planner_seed,
task, goal_offset, horizon, budget, replanning,
candidate_source, success, task_cost,
plan_real_rho, elite_rho, candidate_regret,
pred_real_gap, support_score, wall_clock, peak_vram, data_wait
```

---

## 2. Gate A — baseline parity（E00/E01）

**不追求同时复现所有论文。**

通过条件：
- 官方 checkpoint 原生 protocol 能跑闭环；
- 一项重新训练能落在作者 variation/合理误差区间，或明确记录无法对齐原因；
- candidate logger 与 restore harness 通过阳性/重复性检查；
- 得到真实单卡 train/eval/I/O cost。

只在 Gate A 后启动大规模 seed/sweep。

---

## 3. Gate B — decision audit replication（E02）

目的不是创新，是校准工具：
- 按 DA-LeWM 定义在 random / mid-CEM / elite stage 复现 latent↔real rank。
- fixed candidate pool 同时算 real-endpoint latent cost 与 predicted-endpoint latent cost。
- 记录 candidate margin：top candidates 的 real-cost gap / latent-cost gap。
- 先 LeWM，后 RC-aux（training-only 与 planner gate 分开）。

如果连已知 alignment gap 都测不到，先修 harness；不要直接开始 I01/I02。

---

## 4. Mining lane I01 — behavior-policy geometry contamination

### E03：episode-partition invariance（最便宜、最干净）
同一个 raw transition store 生成两种 metadata：
- A：原始 trajectory boundaries/pairs；
- B：只改变 long-pair/episode partition 规则，**保持 one-step/local training sample manifest 完全一致**。

训练/finetune：
- LeWM local predictive baseline（negative control）；
- RC-aux reachability；
- TD-JEPA（代码可稳定时）。

先 1 seed × 1 navigation task 做决定性 pilot；若 effect > noise/MIE，再扩 3 seeds/多任务。

### E04：behavior path length vs environment distance
TwoRoom/maze 构造：
- shortest-ish policy；
- detour/loop policy；
- route-mixture。
目标是匹配 local edge/state support，而改变同 state-pair 的 observed temporal-gap distribution。

需要 environment oracle：
- directed shortest steps (d^*(s,g))；
- (R^*_h(s,g)=1[d^*le h])。

测：
- trajectory label 与 oracle disagreement；
- learned reachability/TD calibration to (Delta_eta) vs (d^*)；
- fixed candidate ranking；
- closed-loop planning；
- unseen route/stitch goal。

**扩展门：** 只有 navigation 中建立 identification 后，才把思想带到 PushT/Cube（continuous 任务没有精确 shortest path时，改用 paired behavior route + simulator candidate consequence，不伪称 shortest oracle）。

### 若现象成立，方法探索顺序
不先写“我们的方法”。按最小干预：
1. local-transition/Bellman/quasimetric consistency regularization；
2. pair label 从 point (Delta) 改成 lower-bound / interval / multi-route aggregation；
3. graph-local / connectivity supervision；
4. data reweighting，使 behavior route frequency 不支配 geometry。

每个修复先问：在不看 test success 的 validation protocol 上是否真的减少 behavior sensitivity？

---

## 5. Mining lane I02 — optimizer-induced support drift

### E05：CEM support drift / false elites
对每个 CEM iteration：
- 保存全 candidate（或可控 subsample）；
- support：behavior action-chunk kNN、BC log-likelihood；有 PLDM ensemble 时 disagreement；
- prediction score 与 environment true utility；
- false-elite：latent top-E 中真实 cost 落后于 pool 某 percentile；
- selected regret。

对照：
- random fixed pool；
- CEM；
- true-dynamics scoring；
- behavior-retrieval init；
- ACID/uncertainty gate（按可用性）。

先 PushT + TwoRoom（一个 contact，一个 navigation）。  
**判别重点：** support drift 是否随 iteration 单调/结构化，是否先于 optimism/false elite；不是只看最终 success。

### 若成立，方法方向
只允许围绕被证实的链条设计：
- support-aware proposal constraint；
- epistemic/consistency gate；
- validation-calibrated early stop / trust region；
- candidate set mixture（behavior-supported + exploratory）。
如果简单 PLDM ensemble uncertainty 已完全修复，则记录并 park，不造复杂方法。

---

## 6. Mining lane I03 — bottleneck regime / relocation

### E06：oracle bottleneck ladder
2 个任务 × 3 个 goal-distance bins × 2 candidate budgets：
- LeWM baseline；
- one geometry intervention；
- one dynamics intervention；
- one proposal intervention（有现成 checkpoint 才加）。

每格执行 oracle ladder：
```text
candidate-set ceiling
real-endpoint latent ranking
predicted-endpoint ranking
true-dynamics score
nearby-subgoal diagnostic
end-to-end closed loop
```

输出不是总分，而是 failure signature：
```text
R = representation/metric limited
D = dynamics/rollout limited
P = proposal limited
H = horizon/target limited
M = mixed / not identifiable
```

### E07：interaction probe
只在 E06 显示稳定 signature 后做 2×2：
- geometry × dynamics；
- dynamics × proposal；
- geometry × proposal。
看 improvement 是否 additive、redundant、synergistic 或互相伤害。

**升级成 paper lead 的条件：**
- signature 能由一个跨任务变量预测（goal distance / candidate margin / support 等）；
- intervention ranking 随该变量规律性切换；
- 至少两个 model families/substrates；
- 能导出一个比“oracle 选方法”更实际的 adaptive rule 或训练原则。

---

## 7. Mining lane I04 — random→elite alignment gap（从属于 I02/I03）

DA-LeWM 已经定义 CEM-stage Spearman，所以不重新发明 metric。

复现后进一步记录：
- stage-wise candidate margin；
- support；
- disagreement；
- predicted-real error；
- ranking flip count。

若 (ho_{random}) 高而 (ho_{elite}) 塌，并且 candidate margin/support 可以预测塌陷，则把它并入 I02/I03。  
若只是重复 DA-LeWM，停在 calibration asset。

---

## 8. 扩展 baseline 的加入条件

| baseline | 何时加入 | 不加入的原因 |
|---|---|---|
| Temporal Straightening | I03 geometry gate | 不为“方法多”而加 |
| SALT | E06 dynamics gate，且代码可跑 | 最新预印本，先核实现实复现成本 |
| Fast-LeWM | 需要 prefix/direct-horizon 对照 | 它同时改 speed 与 dynamics，解释要小心 |
| PLDM | I02 uncertainty / offline data对照 | 环境/框架差异大时原生分表 |
| QRL/quasimetric | I01 方法/理论对照 | JAX 独立环境，不强迁移成 PyTorch |
| IMWM/SAGE/GC-IDM | E06 proposal gate | 三个里先一个，避免同类冗余 |
| ACID | I02 verifier control | inverse consistency 不是 oracle |
| Flow-JEPA | stochastic/OOD lead 才加 | 不把所有新方法一次装齐 |
| HWM/Dual-WM | 只有 temporal-scale lead 升级 | 长 horizon 已拥挤 |

---

## 9. 并行策略：把“卡多”变成 scientific throughput

### 可以直接独立并行
- train seeds；
- evaluation groups；
- planner budgets/horizons（共享 read-only checkpoint）；
- fixed candidate audits；
- paired dataset variants；
- method × task 原生复现；
- bootstrap/CI 与结果分析（CPU）。

### 不要同时打共享盘
每节点先：
1. stage dataset 到 local disk；
2. 一次 hash；
3. 启动少量 jobs 测 data_wait；
4. 并发翻倍，若 GPU util 降/data_wait 升，停止扩并发。

### GPU 排序
1. **已有 checkpoint 的 evaluation/diagnostic**；
2. 决定性 1-seed pilot；
3. 阳性对照；
4. 只有 lead 通过才 3–5 train seeds；
5. 最后才跨 benchmark 铺开。

不同地点只交换小 config/metrics/代码；默认不交换内部数据或大 checkpoint。

---

## 10. 统计与实验卫生

- success：episode-level paired result + train-seed variance 分开。
- candidate metric：每个 start-goal 先算 pair-level，再跨 pair bootstrap；不要把数千 candidate 当独立样本伪增 n。
- Spearman undefined pair 要计数，不静默删。
- dataset intervention 用 manifest hash 证明 local samples 是否相同。
- multiple sweeps：探索结果与 confirmatory rerun 分开；最终 claim 用新 eval manifest/seed。
- method hyperparameter 在 validation task/seed 选，test 不调。
- wall-clock 与 candidate/model-call budget 两套公平比较都记录。

---

## 11. Local agent 第一次进入时的硬任务

1. 读 `README.md` → `PAPER_LINEAGE.md` → `PROBLEM_METHOD_MAP.md` → `POSITIONING.md` → 本文件 → `HANDOFF.md`。
2. `python3 tools/process/check.py`。
3. 盘点本机已有 repo/data/checkpoint，填 `ASSETS.md` “已下载/已加载/已跑通”状态，禁止重新下载已有资产。
4. 执行 E00；获得真实成本。
5. E01 把 baseline + candidate logger + restore harness 跑通。
6. E02 校准 decision audit。
7. **优先 E03 → E04（I01）**；I02/E05 可在另一独立节点并行，但不因为卡多同时起十条 story。
8. 每个结果更新实验卡、CLAIMS/PAIN_LOG、当天 log；scientific claim 没有数据就保持 L0。

完整提示词见 `LOCAL_AGENT_PROMPT.md`。