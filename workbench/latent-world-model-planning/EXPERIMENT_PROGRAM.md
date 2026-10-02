# Experiment Program — 多卡独立实验怎样服务于一个顶会问题

更新：2026-10-02。  
**Experiment card 是跑前 authority；本文件是共享 substrate + gate + 并行策略。**  
资源见根目录 RESOURCES.md：多 GPU 槽位、弱网络/磁盘/跨节点；优先 single-GPU/single-node independent runs。

## 0. 现在真正要挖什么

**以 [RESEARCH_MINES](RESEARCH_MINES.md) 为科学 authority。** 当前不是围绕一个 loss 做局部优化，而是同时保留三个 problem-led pressure regions：

1. **M1 / I07 — Observable goal ≠ control state**：partial observability / observation aliasing 什么时候真正改变 action choice，point/history latent 什么时候不够，belief 什么时候 load-bearing。
2. **M2 / I08 — Explicit rollout vs implicit predictive abstraction**：predictive computation 应放在 train-time amortized representation/policy，还是 test-time explicit rollout/search；寻找可预测的 regime boundary，而非排行榜。
3. **M3 / I09 — Behavior trajectories ≠ environment controllability**：planning-aware supervision 是否把 behavior-policy geometry 写进 deployed planning semantics。
4. **I06** 降为 M3 的低成本 sampler/negative-role 子诊断；**I03** 是所有 mine 共用的 oracle bottleneck tool，不先当论文。

旧 I01 原 E03/E04 仍保持 VOID：它只改变 long-episode factorization而不改变 pinned methods实际读取的 short-window supervision，treatment结构上不可见。

第一轮资源分配按 **information gain / cost**：
- E11（M1）与 E14（M3）优先做 problem-existence intervention；
- E08 可并行作为 M3 cheap diagnostic；
- E13（M2）在 common substrate 稳定后启动 matched pilot；
- 哪一条先出现 natural failure + decision consequence + clean intervention leverage，再集中多卡扩展。

---

# 1. Shared substrate：一次建设，所有新 idea 复用

## S0 — Native baselines

首轮只装必要对象：

- **LeWM**：TwoRoom smoke + PushT/Cube至少一项正式 reproduction。
- **Bai/Xiong Temporal-Distance JEPA**：M3/I06直接对象；official repo已核对，且同repo已有 LeWM / RC-aux variants、locked manifests。注意它不是 Bagatella ICLR'26 TD-JEPA。
- **RC-aux**：I06第二个 semantic-negative objective；official repo main已宣布 NeurIPS 2026 acceptance，本 workbench代码复现仍用 ASSETS pin。
- **一个 local-geometry control**：I06机制通过后，优先 Temporal Straightening / CGS其一。
- **Bagatella TD-JEPA (ICLR'26 Oral)**：M2 implicit-side核心资产；与 Temporal-Distance JEPA 名称严格分开。
- DINO-WM / JEPA-WM / PLDM 按 M2/I03需要接入；UWM-JEPA等只在 M1 gate通过后接。

不要首轮装 SALT、AD-WM、Traj-LeWM、IMWM、SAGE、HWM、CompACT 全家桶。

## S1 — Candidate trace

每次 planning decision：

```text
episode_id, step, start_obs_hash, goal_obs_hash
goal_distance_native_or_bin
planner_iter, candidate_id, proposal_source
action_seq_hash, action_norm, action_smoothness, bounds_ok
pred_terminal_latent_hash, pred_goal_cost
optional: reachability, td_cost, uncertainty, consistency, support
elite_rank, selected
env_restore_id
real_terminal_obs_hash, real_task_cost, success
```

## S2 — Dataset / sampler manifest

特别为 I06 增加 sampler provenance：

```text
dataset_revision
raw_episode_count, raw_transition_count
episode_idx / step_idx availability
clip_window_length, frameskip, history_size, num_preds
clip_index_manifest_hash
train_split_hash
batch_seed, sampler_seed
pair_sampler_name
negative_margin_or_budget
source_ep_idx, source_step_idx, goal_ep_idx, goal_step_idx   # audit sample
negative_label_type
code_commit, dependency_lock, resolved_config
```

## S3 — Oracle / replay

TwoRoom 优先利用 dataset/proprio/pos_agent + environment topology。

oracle 输出**三态优先**：

```text
CERTIFIED_REACHABLE_WITHIN_BUDGET
CERTIFIED_OUT_OF_BUDGET
UNKNOWN
```

只有能严格/可靠求 shortest-step 时才输出精确 D*。近似 geodesic不冒充 ground truth。

## S4 — Common result table

raw parquet/jsonl不进git；摘要保存：

```text
model, variant, checkpoint, train_seed, eval_seed, planner_seed
task, goal_distance, horizon, action_block, replanning
candidate_budget, planner_iters
success, task_cost
semantic_negative_precision, false_negative_rate, unknown_rate
latent_rank, latent_scale
plan_real_rho, elite_rho, candidate_margin, candidate_regret
wall_clock, model_calls, peak_vram, data_wait
```

---

# 2. Gate 0 / A — E00 + E01

## E00
只解决：
- data/checkpoint可读；
- action/goal/success checker语义正确；
- env→encode→plan→act闭环；
- 真正的 VRAM / step time / CEM cost / I/O。

单 GPU、低并发；不跑满默认 epochs。

## E01
把一次 baseline变成后续所有研究共享的 instrumentation：
- official checkpoint native protocol；
- 一项从头训练；
- candidate logger旁路无行为影响；
- replay/oracle harness；
- TwoRoom + 一个 contact-rich task；
- 真实 GPU-hour / I/O cost。

---

# 3. E08 可以很早开始：零训练 semantic-negative audit

只要 dataset + sampler 能跑，E08 可与 E01/E02部分并行。

## TD-JEPA code facts to reproduce exactly

Pinned repo：
- history size 3，canonical num_preds 5，训练 clip约8 observations；
- temporal positive pairs从 loaded clip内采 i<j；
- cross negative通过 **batch-row random permutation** 取 goal；
- loss本身不显式检查 original episode connectivity；
- paper把该项称 heuristic cross-trajectory negative，并明确承认 reachable false negatives；
- published Push-T ablation显示去掉 hinge会伤多个 planner settings。

E08 不重新发明 sampler，必须 instrument 这条路径。

## RC-aux code facts

Pinned repo：
- history 3，num_preds 5；
- reachability max_horizon 5；
- same-window positives / temporal hard negatives；
- cross negative同样通过 batch维 permutation goals；
- paper语义是 cross-trajectory negative label y=0；
- temporal hard negatives才使 budget h identifiable。

## E08 输出

按 budget/margin、source location、wall side、data region 分层：
- negative pair 是否同 original episode；
- observed connectivity evidence；
- oracle/certified reachability；
- semantic precision；
- false-negative rate；
- unknown rate。

**E08不训练模型，先看这个问题在真实 sampler里是否存在到足以值得训练的程度。**

---

# 4. Gate B — E02：known decision audit calibration

E02复制已有 decision-metric测量：
- random / mid-CEM / elite；
- real endpoint vs predicted endpoint；
- candidate margin；
- fixed-pool regret。

它不是 novelty，只为 E09/E10/I03 提供 downstream decision measurement。

同时必须固定/记录：
- planning horizon H；
- replanning/execution prefix K；
- scoring time index / cost aggregation；
- action block / frameskip；
因为 P57 Hidden Failure Modes 已证明这些 protocol变量本身可以巨大地改变结果。

---

# 5. I06 主线

## E09 — semantic correctness vs regularization utility

E08过 gate后，先 TD-JEPA：

```text
FULL
NO-XNEG
ORACLE-VALID
ORACLE-CENSOR
COUNT-MATCHED VALID
REPULSION-CONTROL (conditional, pre-registered)
```

再用 RC-aux验证是否是 objective-family层面的现象。

### 为什么 count-match 必须有

如果 oracle filtering后只剩少量 negatives，performance下降可能只是：
- loss magnitude变小；
- head没有global scale；
- encoder少了repulsion；
而不是“正确semantic negative不够好”。

所以要把：
**semantic correctness、negative count、gradient magnitude、dispersion**
拆开。

### 机制读数

- semantic calibration to oracle；
- head/latent scale；
- effective rank / pairwise dispersion；
- negative-loss gradient norm；
- TD/reachability scores；
- fixed-candidate rank/regret；
- closed-loop success。

### 最有信息的三种结果

1. **ORACLE-VALID > FULL**  
   → semantic false negatives确实有害。
2. **FULL > ORACLE-VALID，但 REPULSION-CONTROL恢复**  
   → published gain主要来自 non-semantic regularization；最强 reattribution。
3. **COUNT-MATCHED VALID ≈ FULL，calibration更好**  
   → quantity而不是错误语义本身是关键；可设计更干净 sampler。

---

# 6. E10 — role-separated objective

只有 E09真的分离出两个 role 才做。

设计原则：
- cross-trajectory pair默认 unknown，不给“不可达”语义；
- semantic channel用 observed positives、same-trajectory insufficient-budget hard negatives，以及 training-available local/certified bounds；
- separate geometry channel做 uniformity/dispersion/scale；
- 不使用 test oracle；
- 必须改善/保持真实 decision，不只 head calibration。

如果最终 oracle filtering很好，但没有无oracle办法，paper可以停在 diagnosis + reattribution，但方法贡献会弱；是否够顶会由后续人审决定，不能强造模块。

---

# 7. I03 第二主线 — bottleneck relocation / regime law

## E06 oracle ladder

先 2 tasks：
- topology/navigation
- contact-rich

3 goal-distance bins × 2 candidate budgets，LeWM baseline。

额外 protocol轴不是自由 sweep，而是**confound controls**：
- H planning horizon
- K execution/replanning interval
- scoring index / running-vs-terminal aggregation
- frameskip/action block

failure signature：

```text
R = representation / metric
D = dynamics / rollout
A = counterfactual action discrimination
P = proposal / search
T = time-index / replanning interface
H = horizon / target distance
M = mixed / unidentifiable
```

oracle ladder：

```text
candidate-set ceiling
encoded-real endpoint ranking
predicted endpoint ranking
true-dynamics scoring
prefix/running-cost protocol control
nearby-subgoal diagnostic
closed-loop success
```

P40 planner-reachable fidelity与P57 time-index mismatch都要做已知 control，避免重新发现它们。

## E07
只有 E06出现跨task可预测 signature后，挑一个2×2 interaction，不跑全因子。

升级条件：
- 少数observable variables跨task预测 bottleneck；
- intervention ranking随regime变；
- 至少2 substrates；
- 最好导出 practical adaptive rule / training principle。

---

# 8. PARKED / VOID

## I01
PARKED。E03/E04 VOID，未运行。不要把预注册 card删除，它们记录一次被**代码审计提前否定**的实验设计。

## I02 / E05
I02 PARKED。E05只在 I03需要定位 planner-reachable/off-support layer时条件运行，并首先比较 P40-style fidelity / PLDM uncertainty。不要独立扩seed。

## I05
POMDP/history等待 clean substrate，不做 context-length sweep。

---

# 9. Baseline 加入门

| baseline | 何时加入 |
|---|---|
| TD-JEPA | I06首轮 |
| RC-aux | I06首轮第二objective |
| Temporal Straightening / CGS | E09/E10 local-geometry control |
| QRL / CGCIVL / multistep quasimetric | I06 conceptual/method neighbor；优先原生对照，不强迁移框架 |
| Traj-LeWM | I06若扩到full-trajectory semantic negatives |
| LeWMRO / Hidden Failure Modes | I03 protocol/time-index control |
| SALT / Bilinear WM | I03 dynamics gate |
| AD-WM | I03 action-discrimination gate |
| PLDM | uncertainty/data gate |
| GC-IDM / IMWM / SAGE | proposal gate，三者先一个 |
| Do-JEPA / FIRM-WM | 只有需要 same-reset intervention oracle时 |
| CompACT / World-In-World / GeoWorld | venue/邻域 anchor，不是首轮训练 substrate |

---

# 10. 多 GPU 使用方式

可独立并行：
- train seeds；
- FULL / intervention variants；
- eval manifests；
- candidate audits；
- goal-distance bins；
- planner budgets；
- contact-rich confirmatory runs。

但每节点：
1. data stage到local disk；
2. hash；
3. 1 job测data_wait；
4. 2–4 jobs；
5. 并发翻倍；
6. GPU utilization掉、data_wait明显涨就停。

跨节点不做梯度同步；不同地点只默认同步 code/config/metrics/manifest。

GPU优先级：
1. zero-training audit / released checkpoint diagnostics
2. 1-seed decisive pilot
3. positive/negative controls
4. lead通过后3–5 train seeds
5. 最后才跨benchmark铺开

---

# 11. 统计卫生

- candidate不是独立 n；bootstrap cluster by start-goal/planning decision；
- E08 pair audit还要 cluster by episode/batch；
- train-seed variance与eval episode CI分开；
- false-negative precision报告unknown，不强行把unknown算false/true；
- exploratory与confirmatory seeds/manifests分开；
- published component ablation先复制方向，再解释新机制；
- test不调margin/budget/threshold；
- compute report model calls + wall-clock；
- failed runs/load mismatch不静默删。

---

# 12. Local agent 执行顺序

1. README → PAPER_LINEAGE → LITERATURE_LEDGER → PROBLEM_METHOD_MAP → POSITIONING → 本文件 → HANDOFF。
2. run process check。
3. 资产盘点，复用已有下载。
4. E00。
5. dataset/sampler一旦可读，**立即E08**；它不需要训练。
6. E01 baseline instrumentation。
7. E02 decision audit。
8. E08过gate → E09 → 条件E10。
9. 闲置独立节点可做小规模E06；I06没结果前不要把I03铺大。
10. 每个结果按experiment card decision table自主推进，不每个job回来问人。

完整启动词：[LOCAL_AGENT_PROMPT](LOCAL_AGENT_PROMPT.md)。