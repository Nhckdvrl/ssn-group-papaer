# Experiment Program — 多卡独立实验怎样服务于一个顶会问题

更新：2026-10-02。  
**Experiment card 是跑前 authority；本文件是共享 substrate + gate + 并行策略。**  
资源见 `../../RESOURCES.md`：多 GPU 槽位、弱网络/磁盘/跨节点；优先 single-GPU/single-node independent runs，不做跨节点大训练。

## 0. 目标不是“把表格填满”

工作台先回答：

> 一次 latent-WM planning failure 到底来自 data supervision、representation/metric、recursive dynamics、counterfactual action distinction、proposal/search、temporal target，还是 environment execution？

然后把 GPU 只给**会改变下一步科学判断**的比较。

当前优先级：
1. **I01 trajectory-factorization / route imprinting**
2. **I03 bottleneck regime law**
3. I04 measurement calibration
4. I02 support drift = PARKED，只作为 I03 diagnostic
5. I05 POMDP = PARKED

---

# 1. Shared substrate：一次建设，所有 lead 复用

## S0 Native baselines

首轮只装必要对象：

1. **LeWM**：TwoRoom smoke → PushT 或 Cube 至少一项正式 reproduction。
2. **RC-aux**：I01 trajectory reachability 直接对象。
3. **TD-JEPA**：I01 第二个 trajectory-derived planning supervision；官方 repo 已核对，且同仓含 LeWM / RC-aux variants、locked eval manifests。
4. **一个异质 baseline**：已有资产允许时 DINO-WM / JEPA-WM / PLDM 其一。
5. **local-geometry control**：I01 通过第一 gate 后优先 Temporal Straightening；若 CGS code 可用且接入便宜，则 CGS 更贴近“只看 local transitions”的 control。

不要一开始安装 SALT、AD-WM、Traj-LeWM、IMWM、SAGE、HWM、CompACT 全家桶。

## S1 Candidate trace schema

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
real_terminal_obs_hash, real_task_cost, success      # audited candidates
```

## S2 Dataset / training manifest

每个 checkpoint：
```text
dataset_revision
raw_transition_multiset_hash
episode_partition_hash
local_transition_hash
history_window_manifest_hash
long_pair_manifest_hash
behavior_policy_tag
state_occupancy_summary
edge_occupancy_summary
goal_distribution_hash
code_commit, dependency_lock, resolved_config, seeds
```

**I01 没有这些 hash 就不能写因果解释。**

## S3 Oracle / replay harness

在 simulator 验证：
1. snapshot/restore 或 deterministic reset+replay；
2. same candidate 重放波动 floor；
3. env RNG、planner RNG、data RNG 分开；
4. privileged simulator state 只写 diagnostic，不进入 pixel method input；
5. true-dynamics candidate execution 和 model prediction 使用同 action units/repeat。

## S4 Common result table

raw parquet/jsonl 不进 git；git 存摘要+manifest：

```text
model, checkpoint, train_seed, eval_seed, planner_seed
task, goal_source, goal_distance, horizon, action_block, replanning
candidate_budget, planner_iters
success, task_cost
plan_real_rho, elite_rho, candidate_margin, candidate_regret
pred_vs_real_endpoint_gap
support_or_fidelity_if_defined
wall_clock, model_calls, peak_vram, data_wait
```

---

# 2. Gate 0 / A — E00 + E01：先证明 baseline 与 instrumentation 可信

## E00 resource/native smoke

目的：
- dataset/checkpoint能加载；
- action/goal/success semantics 对；
- 完整 env→encode→plan→act 闭环；
- 测真实 peak VRAM / train step / planner decision / env render / data wait。

单 GPU、低并发；不跑满默认 100 epochs。

## E01 baseline parity + logger

通过条件：
- official checkpoint 原生 protocol 落在公开结果合理范围，或 protocol差异已定位；
- 至少一项从头训练能解释；
- candidate logger 开/关不改变相同 seed 的 planner behavior；
- replay/oracle harness通过；
- 一个 contact-rich task可运行；
- 有实际 GPU-hour / I/O 数字。

**只有 Gate A 后才做多 seed / 大 sweep。**

---

# 3. Gate B — E02：复制一个已知 decision audit，校准测量

不是 novelty。

按 Decision-Metric Alignment / AD-WM 相关定义：
- random candidates；
- mid-CEM candidates；
- elite candidates；
- fixed pool。

同一 candidate 保存：
1. real environment utility；
2. encoded real endpoint latent cost；
3. predicted endpoint latent cost。

读数：
- Plan-Real / stage-wise rank；
- selected-action flip；
- candidate margin；
- fixed-pool regret；
- dynamics-induced ranking flip。

注意：DA-LeWM/AD-WM 已经观察到 elite-stage alignment/regret很关键。**复制成功只是说明我们的工具可用。**

---

# 4. I01 主线 — trajectory-factorization dependence

## E03a：split-only sanity（可选、极便宜）

同 raw transitions，把一条长 trajectory 在合法 boundary 切成多 episode，但不做跨 route splice。

作用：
- 检查 method 是否对 logging segmentation敏感；
- 校验 long-pair sampler/target确实由 episode metadata决定。

**单独有结果不够 paper。** 它只是 E03b 的 smoke。

## E03b：valid cut-and-splice refactorization（核心 identification）

### 构造

在 navigation state graph 找共享 junction (x)：

```text
A: p1 -> x -> s1
B: p2 -> x -> s2
```

构造另一种合法 factorization：

```text
A': p1 -> x -> s2
B': p2 -> x -> s1
```

要求：
- 所有 adjacent transitions 都来自原始数据；
- raw transition multiset一模一样；
- fixed-history/one-step training-window multiset一模一样；
- 只有 long-range within-trajectory pair membership / temporal gaps 改变。

如果 history window 跨 junction 会改变，则**删除或 matching 两边 junction-crossing windows**，直到 manifest hash 一致。不能只说“转移一样”。

### 方法

- RC-aux
- TD-JEPA
- LeWM negative control
- local-geometry control（TS / CGS，有可靠实现后）

### 读数

Data:
- pair membership flips；
- temporal-gap shifts；
- cross-trajectory-negative status flips。

Model:
- (R_phi(z,z',h)) / (d_psi(z,z')) paired shift；
- environment shortest-distance/reachability calibration。

Decision:
- fixed-pool rank；
- elite rank；
- selected-action flip；
- candidate regret；
- closed-loop pilot。

### Gate

只有 **target → learned geometry → decision** 至少到 fixed-pool decision level成立，且 LeWM/local controls稳，才 E04。

只 head 变、decision null → 不扩。

---

## E04：natural behavior route intervention

E03 是人工但合法 identification；E04 测真实 data-collection semantics。

同 MDP / rendering / goal distribution：
- shortest-ish behavior；
- systematic detour / loop；
- route mixture。

尽量匹配：
- state occupancy；
- local directed edge support/frequency；
- action marginal；
- data amount。

Navigation exact oracle：
[
d^*(s,g), qquad R_h^*(s,g)=mathbf 1[d^*(s,g)le h]
]

比较 observed (Delta_β) 与 (d^*)，再看 learned geometry 与 decision。

### E04 通过后才方法化

按简单→复杂：

1. **multi-route aggregation**：同 pair 多条 observed route，避免一条 behavior path 直接定义 cost；
2. **interval / lower-bound target**：observed gap 是 upper bound，不当 point truth；
3. **local Bellman / quasimetric consistency**：用 local dynamics 约束 long-range geometry；
4. **graph-local connectivity / shortest-path surrogate**（仅数据可合法构图时）；
5. **data reweighting**：降低 route frequency 对 geometry 的支配。

每个修复必须：
- 在 validation 上降低 A/B trajectory-factorization sensitivity；
- 不看 test success 选 hyperparameter；
- 保持或提升 real candidate/control consequence；
- 和 QRL/quasimetric思想区分清楚：我们的 contribution 不是“发明 quasimetric”，而是 latent-WM planning objective 的 invariance failure + repair。

---

# 5. I03 第二主线 — bottleneck relocation / regime law

## E06：oracle bottleneck ladder

先：
- 2 tasks（一个 topology/navigation，一个 contact-rich）；
- 3 goal-distance bins；
- 2 candidate budgets；
- LeWM baseline。

必要时只加一类 method per layer：

- metric/geometry: TS/CGS 或 RC-aux training-only
- dynamics: SALT / direct-horizon method
- counterfactual action: AD-WM only if code/checkpoint可得
- proposal: GC-IDM / IMWM / SAGE 中一个

每格 oracle ladder：

```text
candidate-set oracle ceiling
encoded-real endpoint ranking
predicted endpoint ranking
true-dynamics scoring
nearby-ground-truth subgoal diagnostic
end-to-end closed loop
```

Failure signature：
```text
R = representation/metric
D = dynamics/rollout
A = action discrimination
P = proposal/search
H = horizon/target interface
M = mixed / unidentifiable
```

## E07：只做最有信息增益的 interaction

E06 先产生 hypothesis，再挑一个 2×2：
- geometry × dynamics
- dynamics × proposal
- geometry × proposal
- action-discrimination × proposal

不是三向全因子。

### I03 升级条件

- 少数 observable variables（goal distance / candidate margin / planner-reachable fidelity / data support 等）跨 task 预测 signature；
- intervention ranking 按该变量规律切换；
- 至少两种 substrate/model families；
- 能导出 deployable/adaptive rule 或 training principle，而不是 oracle 事后选方法。

否则 I03只是 diagnostic map，不包装 paper。

---

# 6. I02 / E05 — PARKED idea 的 conditional diagnostic

由于 **A Control Theory of Predictability** 已直接 formalize planner-reachable/off-manifold divergence，且 offline MBRL model exploitation已有经典文献，E05 不再是独立主线。

只有 I03 需要判断“search 是否进入 unsupported region”时运行：

- stage-wise behavior action support；
- planner-reachable fidelity；
- ensemble uncertainty；
- predicted vs true plan-cost discrepancy；
- false elites；
- regret。

若 P40 fidelity / PLDM uncertainty已解释现象，就停止，不发明新 detector。

---

# 7. Baseline 加入条件

| Baseline | 何时加入 | 为什么不是首轮 |
|---|---|---|
| TD-JEPA | **I01 首轮** | official repo已核对、同 LeWM stack |
| RC-aux | **I01 首轮** | direct trajectory reachability target |
| Temporal Straightening / CGS | E03/E04 local-geometry control | 只需一个先行，避免装方法大全 |
| QRL / multistep quasimetric | I01 repair/理论对照 | JAX/不同 framework，可概念+原生对照，不强迁移 |
| Traj-LeWM | I01 path-supervision扩展通过后 | source-only，full-trajectory preference会引入额外变量 |
| SALT | E06 dynamics gate | 最新 preprint，先确认 code/runtime |
| AD-WM | E06 action-discrimination gate | 直接占 counterfactual story，不作为初始 idea |
| PLDM | E06 uncertainty/data gate | 原生 protocol/framework不同，分表 |
| GC-IDM / IMWM / SAGE | E06 proposal gate | 同类只先一个 |
| ACID / MEND | verifier/detector diagnostic | internal score ≠ environment oracle |
| ALeWM / AnisoWM / PSG-JEPA | specific representation/capacity confound | 不为“更多 baseline”而加 |
| CompACT / World-In-World / GeoWorld | venue/邻域 anchor | training更重/范式不同，不适合首轮 substrate |

---

# 8. 多 GPU 调度：parallel scientific throughput

## 可独立并行

- A/B paired dataset variants；
- train seeds；
- evaluation manifests；
- goal-distance bins；
- planner budgets；
- candidate audits；
- confirmatory baselines。

## 并发前 I/O gate

每节点：
1. dataset stage 到 node-local disk；
2. hash；
3. 1 job 测 data_wait；
4. 2–4 jobs；
5. 并发翻倍；
6. GPU util下降 / data_wait明显上升就停，不用更多 GPU掩盖 I/O。

跨节点只同步：
- code
- small configs
- manifests
- metrics
- summary tables

默认不做跨节点 gradient communication，也不在研究室↔实习地点随意搬内部数据/checkpoint。

## GPU 优先级

1. 已有 checkpoint 的 diagnostic/eval
2. 1-seed decisive pilot
3. positive/negative controls
4. lead通过后 3–5 train seeds
5. 最后才跨 benchmark铺开

---

# 9. 统计卫生

- candidate 不是真独立 n；bootstrap unit = start-goal / planning decision；
- train-seed variance 与 eval episode CI分开；
- Spearman undefined pair计数；
- A/B data intervention必须有 manifest hash；
- exploratory seed/manifest 与 confirmatory新 seed/manifest分开；
- success threshold/test goals 不事后改；
- compute matched：model calls + wall-clock 两种口径都报；
- method tuning在 validation；
- failed runs、load mismatch、renderer mismatch不静默删除。

---

# 10. Local agent 的执行顺序

1. 读 README → PAPER_LINEAGE → LITERATURE_LEDGER → PROBLEM_METHOD_MAP → POSITIONING → 本文件 → HANDOFF。
2. `python3 tools/process/check.py`。
3. 资产盘点，不重复下载。
4. E00。
5. E01。
6. E02。
7. **E03a smoke（可选）→ E03b valid refactorization。**
8. E03b过 gate → E04。
9. 同时可在闲置独立节点做 E06 的小 oracle ladder；**不自动跑 E05**。
10. 每个结果按 card decision table自主推进，不每 job回来问人。

完整启动词：[LOCAL_AGENT_PROMPT.md](LOCAL_AGENT_PROMPT.md)。