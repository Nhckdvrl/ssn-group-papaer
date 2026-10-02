# HANDOFF — latent-world-model-planning

状态：**PROPOSED / literature+code-hardened / execution-ready / no local GPU result yet**。  
完整启动词见 [LOCAL_AGENT_PROMPT](LOCAL_AGENT_PROMPT.md)，实验细节见 [EXPERIMENT_PROGRAM](EXPERIMENT_PROGRAM.md)。

## 0. 不要重新 brainstorm

领域与直接近邻已经硬化到 P01–P64；更重要的是，**代码审计已经实际杀掉过一个原本看起来很漂亮的实验**：I01/E03 的“只改长 episode factorization、保持 short windows不变”对 pinned TD-JEPA/RC-aux 的主要 short-window loss结构上几乎不可见，因此 E03/E04 未运行即 VOID。

这说明本 workbench 的原则是：**先读真实实现，再花 GPU。**

当前：
- **I06 first priority**：semantic negatives vs geometric regularization；
- **I03 second priority**：bottleneck regime law；
- I04 = E02 calibration；
- I01/I02/I05 = PARKED。

## 1. authority

1. root AGENTS.md / workbench/EXECUTION.md
2. experiment card 跑前内容
3. POSITIONING.md
4. EXPERIMENT_PROGRAM.md
5. PAPER_LINEAGE.md / LITERATURE_LEDGER.md
6. 本文件
7. 旧 LATENT_PLANNING_SURVEY.md

任何 manuscript-critical事实最终回原论文/官方代码。

## 2. native layer 与 common audit layer

**Native layer**：官方repo各自环境，固定commit/checkpoint/config，先复制官方protocol。  
**Common audit layer**：统一candidate trace、sampler manifest、oracle/replay、result schema。

不先把所有method重写到一个framework。TD-JEPA official repo因为已含 LeWM/RC-aux variants，是 I06 **工程上优先的共同起点**；但其中variants是否精确等价于各原论文，必须另做provenance核对。

## 3. 执行顺序

### E00
1 GPU smoke + resource/I/O measurement。

### E08（dataset能读后即可开始）
**零训练。** instrument pinned TD-JEPA/RC-aux真实 negative sampler，测 semantic validity。

这是当前最便宜、information gain最高的科研pilot，不需要等baseline训练全部完成。

### E01
baseline parity + candidate logger + replay/oracle harness。

### E02
复制 known decision-alignment / fixed-pool regret，顺便控制 H/K/scoring-index。

### I06
E08过gate → E09。  
E09证明 semantic role 与 regularization role可分 → E10。  
否则按卡片stop rule park，不硬救。

### I03
E01/E02后，小规模 E06 oracle ladder；只有出现跨task predictive signature才E07。

E05只有E06明确指向 off-support/search层才触发。

## 4. I06 实现事实：必须记住

### TD-JEPA pinned code
- loaded short clip；canonical history 3 + num_preds 5；
- temporal positives在clip内 i<j；
- cross negatives用 batch row permutation；
- loss不查询 environment connectivity；
- paper明确说 false negatives possible when trajectories share reachable states；
- published component ablation又显示去掉 cross-trajectory hinge伤 planning。

### RC-aux pinned code
- history 3, num_preds 5 / reach horizon 5；
- positives + same-window temporal hard negatives；
- cross negatives也是 batch permutation；
- cross negatives被BCE标 unreachable；
- temporal hard negatives才使 budget h identifiable。

### 因此 I06 不能写成
“cross-trajectory negatives are wrong.”

必须问：
> semantic correctness 与 global representation/optimization regularization，各贡献了多少 planning utility？

## 5. sampler audit schema

E08每个 sampled pair至少保存：

```text
method, code_commit, dataset_revision
batch_seed, batch_idx, row_idx
src_episode, src_step, goal_episode, goal_step
src_state_or_position, goal_state_or_position
negative_type
budget_h_or_margin_m
observed_relation_if_any
oracle_status = reachable / out_of_budget / unknown
oracle_distance_or_bound
```

如果HDF5 loader没直接返回episode_idx/step_idx，就用 stable-worldmodel clip_indices映射；不要为了方便丢 provenance。

## 6. candidate/decision schema

E01/E02至少：

```text
decision_id, task, goal_distance
H, K, frameskip, action_block, scoring_index
planner_iter, candidate_id, proposal_source
pred_cost, encoded_real_cost, real_utility
candidate_margin, selected, elite_rank
model_calls, wall_clock
```

P57已证明H/K/time-index本身能造成巨大差异；不记录这些就不能归因world model。

## 7. attribution rules

- negative sampler语义错，但decision null → 不是planning finding；
- FULL > NO-XNEG，不代表negatives semantic正确；
- oracle filtering后变差，不代表 false negatives有益；先 count/gradient/dispersion match；
- fixed candidate pool本来没有好plan → 不只修metric；
- encoded-real score就排不好 → 不只怪dynamics；
- true dynamics仍失败 → 不只怪predictor；
- H/K control能救 → 先标protocol layer；
- internal consistency/uncertainty高 ≠ environment-realizable。

## 8. 方法什么时候出现

I06只有E09决定机制后才能方法化：

- semantic contamination伤害 → unknown/censor/certified-negative方向；
- false negatives语义错但其repulsion有益 → **separate semantic channel + geometry regularizer**；
- count才是关键 → count-matched semantic sampler；
-现有simple baseline已经解决 → 用simple baseline，不造复杂模块。

E10 deployable方法不能用privileged oracle。

I03同理：没有regime law不设计adaptive router。

## 9. 多卡

优先：
1. E08 CPU / released-checkpoint diagnostics
2. 1-seed E09 variants
3. positive/negative controls
4. 通过后多 train seeds
5. contact-rich + second objective
6. 最后才大矩阵

同节点先stage local data并测data_wait；不要跨节点DDP。

## 10. 写回 / 人审

每次运行：
- 实验卡结果
- P## only if real observed pain/success
- C## only with evidence
- logs/YYYY-MM-DD.md
- small commit/push

触发人审：
- E09机制方向明确；
- E10出现可投级方法/主张；
- E06/E07出现跨task regime；
- science C##→L2；
- 需要改ACTIVE调度；
- 连续两个lead被强近邻/简单baseline吸收。

在预注册决策表范围内自主继续，不每跑一个job就停。