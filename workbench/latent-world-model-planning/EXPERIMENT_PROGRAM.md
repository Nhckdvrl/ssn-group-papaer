# Experiment Program — problem-led latent world-model mining

更新：2026-10-02。  
**Experiment card 是跑前 authority；本文件规定 shared substrate、mine gates 与多 GPU 排程。**  
资源见根目录 [RESOURCES](../../RESOURCES.md)：多独立 GPU、弱网络/弱 I/O/弱跨节点；single-GPU / single-node independent runs优先。

科学入口：
1. [FIELD_PROBLEM_MAP_2026](FIELD_PROBLEM_MAP_2026.md)
2. [RESEARCH_MINES](RESEARCH_MINES.md)
3. [PAPER_LINEAGE](PAPER_LINEAGE.md) / [POSITIONING](POSITIONING.md)

当前 science claim = 0。

---

## 0. 当前优先级

### Tier A1 — M3 / I09：behavior trajectories → controllability semantics
**第一主 pilot：E14。**

问的是：在 environment dynamics 不变时，改变真正的 generating behavior policy，trajectory-derived planning supervision 是否把 behavior route / tempo 写进 deployed reachability / progress semantics，并影响 candidate ordering / MPC？

不是“data distribution matters”；必须把 coverage/local-support explanation拆开。

### Tier A2 — M2 / I08：predictive computation placement
**第二主 pilot：E13。**

不是二分“explicit vs implicit谁强”，而是 continuum：

```text
one-step explicit rollout
↔ direct arbitrary-horizon prediction
↔ policy-occupancy / successor abstraction
↔ amortized planner / policy
↔ hybrid short-model + learned policy/value
```

寻找可预测的 regime frontier，而不是 leaderboard。

### Tier B — M1 / I07：observable goal ≠ control belief
**cheap conditional pilot：E11。**

P75/FIRM/UWM/Branch-JEPA 已占 broad hidden-state / belief / multimodal-future story。只有 **finite history 后仍存在 action-relevant ambiguity**，且造成 candidate regret，才 E12。

### Shared instruments
- E02：known decision-alignment calibration；
- E06：oracle bottleneck ladder；
- E08：M3 中 heuristic negative 的 zero-training semantic audit；
- E09/E10：只有 E08/E14 指向 negative-role mechanism 才触发。

旧 E03/E04 保持 VOID；I01/I02 parked；I05 已被 I07 supersede。

---

# 1. Shared substrate

## S0 — 原生系统先跑通，不先重写

### compact explicit WM side
- LeWM / JEPA-WM family；
- Bai/Xiong **Temporal-Distance JEPA**；
- RC-aux；
- stable-worldmodel 做 environment/planner/replay substrate。

### implicit / long-horizon predictive side
- Bagatella **TD-JEPA (ICLR 2026 Oral)**；
- 后续 M2 若过 gate，再接 Universal Horizon Model / Jumpy WM / TD-MPC2 中一个代表，不一次全装。

### M1 conditional
- UWM-JEPA / FIRM-WM / Branch-JEPA 只有 E11 过 gate 才接。

**命名：**
- `bagatella_td_jepa`
- `temporal_distance_jepa`
- `decision_aligned_d_jepa`

禁止裸 `td_jepa` 作为跨 repo paper identity。

## S1 — Environment / data substrate

### M3 discovery substrate
优先：
1. **TwoRoom / maze topology**：shortest/geodesic 可做 oracle；
2. **OGBench Point/AntMaze generator**：官方就有 `navigate / stitch / explore`，可用于 discovery，但这些 regime 同时改变 horizon / goal schedule / occupancy，**只能作 broad stress，不作 clean causal identification**；
3. 第二阶段 contact-rich：OGBench Cube/PushT。

OGBench generator 已核对：
- locomaze: `path / navigate / stitch / explore`；
- manipulation: `play`（non-Markovian plan oracle）/ `noisy`（Markov closed-loop oracle + Gaussian/random actions）；
- dataset保存 qpos/qvel，可做 measurement-only support audit；
- 数据生成脚本公开且可重跑。

### M2 common substrate
优先 **OGBench Cube-single / pixel**：
- Bagatella TD-JEPA official repo原生支持 OGBench Cube/Scene/Puzzle；
- stable-worldmodel / LeWM ecosystem也原生有 OGBench Cube；
- 同 environment 可比较真实 task utility。

但 task specification **并不天然公平**：
- explicit image-goal planner通常得到 goal observation；
- Bagatella TD-JEPA official evaluation对每个 task 从 replay buffer采样约 10k states，利用 OGBench privileged `physics` relabel reward，再做 reward inference。

因此 E13 必须把 **query information budget** 单独记账，不能把“一个 goal image vs 10k reward-labeled samples”当作只差 inference compute。

## S2 — Candidate / decision trace

每个 planning decision至少：

```text
decision_id, episode_id, step
start_obs_hash, goal_or_task_id
H, K, frameskip, action_block, scoring_index
planner_iter, candidate_id, proposal_source
action_seq_hash
pred_cost / implicit_policy_score
encoded_real_cost (when defined)
real_task_utility
candidate_margin
elite_rank, selected
env_restore_id
model_calls, wall_clock
```

M3额外：

```text
behavior_regime
state_coverage_bin
action_coverage_bin
local_transition_support_score
route_class / path_efficiency
observed_temporal_gap
oracle_shortest_or_bound
```

M2额外：

```text
task_spec_type
task_inference_samples
task_label_calls
train_steps, train_gpu_hours
deployment_model_calls
deployment_search_budget
```

## S3 — Oracle ladder

### M3 pair / route oracle
优先三态：

```text
CERTIFIED_REACHABLE_WITHIN_BUDGET
CERTIFIED_OUT_OF_BUDGET
UNKNOWN
```

能严格算 shortest-step/geodesic才记 D*。

### Common decision oracle
固定 start/task + candidate pool：
1. candidate-set environment utility；
2. encoded-real endpoint ranking；
3. predicted endpoint ranking；
4. true-dynamics scoring；
5. H/K / running/prefix cost control；
6. action-discrimination check；
7. selected-action regret；
8. closed-loop success。

### M1 aliasing oracle
同/近同 observation + matched available history 下：
- hidden state / parameter不同；
- 完全相同 candidate action set；
- environment utility vector；
- best-action flip / regret。

---

# 2. E00 / E01 — infrastructure gate

## E00
单 GPU、低并发：
- dataset/checkpoint load；
- env reset/state restore；
- action / goal / success checker；
- encode→rollout→plan→act；
- one train step；
- VRAM / planner time / env time / I/O wait。

不跑满默认 epochs。

## E01
形成后续共用资产：
- 至少一个 compact explicit native reproduction；
- candidate logger旁路；
- replay/oracle harness；
- fixed eval manifests；
- TwoRoom/topology + OGBench Cube/contact-rich 入口；
- resolved config / code commit / data hash。

E01 没过，不做大规模跨方法比较。

---

# 3. E14 — M3 第一主 pilot：behavior policy真的改变 planning semantics 吗？

## Stage A — cheap discovery，不作因果 claim
可以利用 OGBench 公开 behavior regimes：
- maze `navigate / stitch / explore`；
- manipulation `play / noisy`。

目的：找 sensitivity，不是论文证据。  
这些 regimes 明显改变 trajectory length / goal schedule / occupancy / action noise，所以只回答：

> 哪些 planning-aware objective 对 behavior regime 最敏感？

## Stage B — clean intervention
若 Stage A 有信号，在 topology env 做自定义 matched generation：

- 固定 environment；
- 固定 start-goal manifest；
- 固定 episode count / transition budget；
- 至少 direct / detour-loop 两种 policy；
- 最好加入 mixed route；
- 记录每条 trajectory 的 path efficiency = observed length / oracle shortest length。

优先做 **local-support matching**：
- state occupancy bins；
- action bins；
- one-step `(s,a,s')` support / nearest-neighbor density；
- transition count；
- start/goal distribution。

如果 exact matching不可行，至少 propensity / stratified matching并报告 overlap。

## Stage C — methods
先 1 seed：
1. LeWM non-temporal control；
2. Temporal-Distance JEPA；
3. RC-aux（若第一objective effect成立再接）。

主 readout：
- temporal/reachability semantics vs D*；
- same fixed candidate pool rank / regret；
- closed-loop success；
- one/multi-step prediction guard；
- geometry/path imprint；
- behavior-regime classifier probe只可作辅助，不可当结论。

### E14 gate
- effect完全由 coverage/support解释 → M3不升级；
- learned score漂但 decision null → 不升级；
- non-temporal LeWM同样漂 → 先解释普通 data shift；
- planning-aware methods出现更强 route imprint，且 local fidelity接近稳定 → strong signal；
- 第二objective / 第二task structure复现 → E15或更精确 identification。

---

# 4. E08 / E09 / E10 — M3 子机制：negative semantics

dataset ready 后 E08 可立即并行，主要 CPU。

### E08
instrument **真实** Bai/Xiong Temporal-Distance JEPA / RC-aux negative sampler：
- source/goal original episode；
- step；
- margin/budget；
- oracle reachability；
- false-negative / unknown；
- cluster CI by source episode/batch。

E08 只判断 mechanism 是否值得追。

### E09
只有 E08 + E14 指向 cross-negative role 才训练：

```text
FULL
NO-XNEG
ORACLE-VALID / CENSOR
COUNT-MATCHED VALID
conditional REPULSION-CONTROL
```

拆 semantic correctness vs count / gradient / scale / dispersion。

### E10
只有 E09 确证 role conflation 后，才做 oracle-free role separation。  
不使用 privileged shortest-path oracle作为 deployable training signal。

---

# 5. E13 — M2 第二主 pilot：predictive computation放在哪里？

## 5.1 不能直接横比原论文数字

Bagatella TD-JEPA official OGBench pixel：
- 1M train steps（OGBench）；
- batch 256；
- DrQ encoder 256d；
- official evaluation每个 task约 10k inference samples；
- reward inference使用 replay-buffer next-state `physics` 经过 OGBench task relabeler。

DMC pixel default 2M train steps、batch 512。

explicit JEPA-WM / LeWM 则通常拿 goal observation做 MPC。

因此至少三种预算分开：

```text
training compute
task/query information
deployment compute
```

## 5.2 第一 common substrate
**OGBench Cube-single / pixel** 优先，因为两边原生支持。

先保留 native protocols，另建 common audit：

### Axis Q — task/query information
- goal observation only；
- full known reward/relabel function；
- limited reward-labeled inference samples N；
- 如果能公平实现，再考虑 interaction-based task inference。

注意：OpTI-BFM 已在 ICLR 2026 研究 behavior-foundation-model 的 reward task inference data burden；不要把“TD-JEPA需要reward samples”本身当 novelty。

### Axis H — horizon
near / medium / far goals。

### Axis D — environment change
same dynamics vs layout/dynamics shift（只在 native baseline稳定后）。

### Axis C — deployment compute
explicit planner candidate/model-call budget；
implicit policy forward cost；
如需 compute-matched comparison，按 wall-clock + model calls两种方式报告。

## 5.3 成功标准
不是“谁平均分高”。

只有出现：
- 少数可观察变量预测 explicit / direct-horizon / implicit / hybrid 哪类更合适；
- relation跨至少2 task structures；
- hold-out regime也能预测；
- compute/query-information confound已拆；

才升级成 M2 paper。

如果差异只由 train compute 或 task-information优势解释，记录并停止扩矩阵。

---

# 6. E11 — M1 conditional pilot：只验证还有没有值得做的问题

P75/FIRM/UWM/Branch-JEPA之后，不再把“hidden state matters”当发现。

E11只问：

> 在 **相同可用 history** 下，是否仍存在 action-relevant hidden ambiguity？

顺序：
1. same RGB / different velocity：sanity；
2. 给 2–3 frame history；
3. history 足够则 STOP；
4. 只有 history仍不能 disambiguate 的 contact/friction/regime / stochastic branch，才测 candidate regret；
5. baseline planner确实选错后才 E12。

M1无强信号时快速 park，不消耗训练槽位。

---

# 7. E02 / E06 — common scientific instruments

E02复制已知 random/mid/elite rank、candidate margin、fixed-pool regret，仅校准 harness。

E06 oracle ladder在 M2/M3出现 anomaly 后定位：
- representation/metric；
- dynamics；
- action discrimination；
- proposal/search；
- H/K/time-index；
- target horizon；
- query/task interface。

若 E06自己形成跨 task predictive bottleneck law，才允许 I03独立升级。

---

# 8. Baseline gate

| baseline / asset | 加入时机 |
|---|---|
| LeWM | E00/E01 |
| Temporal-Distance JEPA | M3 E14 first objective |
| RC-aux | M3 confirm / E08 |
| QRL / multistep quasimetric / CGCIVL | M3 conceptual + native comparison when needed |
| Bagatella TD-JEPA | M2 E13 |
| Universal Horizon / Jumpy WM | M2 过 first gate后选一个中间 predictive object |
| TD-MPC2 | M2 hybrid control after regime signal |
| UWM-JEPA / FIRM-WM / Branch-JEPA | M1 E11过gate后 |
| Temporal Straightening / DA-LeWM / D-JEPA | common decision/geometry control when relevant |
| LeWMRO | H/K protocol control |
| SALT / Bilinear WM | dynamics oracle指向时 |
| PLDM | M3 data/uncertainty neighbor |
| AdaJEPA / ReDRAW / Feedback WM | shift/adaptation只作 control，不开新mine |

---

# 9. 多 GPU 排程

### Phase 1 — existence
同时最多：
- E14 Stage A/B；
- E13 one minimal matched pair；
- E11 oracle；
- E08 CPU audit。

每条 1–2 seeds / minimal conditions。

### Phase 2 — concentration
只给过 gate 的 mine扩：
1. decisive variants；
2. 3+ train seeds；
3. second task structure；
4. strongest nearest baseline；
5. hold-out regime；
6. method ablation（如果真的长出方法）。

### I/O
每节点：
1. dataset stage local disk；
2. hash；
3. 1 job；
4. 2 jobs；
5. 4 jobs；
6. data_wait / GPU utilization恶化就停。

不跨节点 DDP。不同地点默认只同步 code/config/metrics/manifest。

---

# 10. 统计与 claim 升级

- candidate-level样本 cluster by planning decision/start-goal；
- data-regime comparison cluster by episode/route seed；
- train seed 与 eval episode variance分开；
- exploratory vs confirmatory manifests分开；
- support overlap / effective sample size必须随 M3 主表报告；
- M2同时报告 train compute、task-information budget、deployment compute；
- oracle只作 measurement / upper bound；
- failed runs与load mismatch不静默删。

**L1前：** 至少一个真实 model behavior。  
**L2前：** controlled alternative explanation被拆。  
**L3前：** second method/task + nearest strong baseline。  
**L4因果/机制：** intervention chain完整。

---

# 11. Local agent执行顺序

1. README → FIELD_PROBLEM_MAP_2026 → RESEARCH_MINES → PAPER_LINEAGE → LEDGER → POSITIONING → 本文件。
2. `python3 tools/process/check.py`。
3. 资产盘点，禁止重复下载。
4. E00/E01。
5. **第一主：E14 Stage A/B**；dataset ready可并行E08。
6. **第二主：E13 minimal matched pilot**。
7. **conditional：E11**。
8. 出 anomaly 后用 E02/E06定位，不先加模块。
9. 只有 experiment card gate允许才进入 E09/E10/E12/E15或新增方法卡。
10. 每轮写回 evidence、confound、neighbor pressure、下一组最便宜决定性实验。

**不要把工程进度当科研进度；不要把卡多变成没有判别力的大矩阵。**
