# HANDOFF — latent-world-model-planning

状态：**PROPOSED / literature+code-hardened / execution-ready / no local GPU result yet**。  
完整启动词见 [LOCAL_AGENT_PROMPT](LOCAL_AGENT_PROMPT.md)，实验细节见 [EXPERIMENT_PROGRAM](EXPERIMENT_PROGRAM.md)。

## 0. 不要从一个 loss 重新找钉子

领域 hardening 已经证明两个事实：

1. compact latent-WM 不是缺“小技巧”，而是同时存在 **state definition、predictive abstraction placement、offline supervision semantics、planner interface** 等真实问题；
2. 一个看起来漂亮的实验若 treatment 对真实 implementation 不可见，应该在跑 GPU 前就杀掉。旧 I01/E03–E04 就是这样 VOID 的。

当前科学入口由 [NOVELTY_GROWTH_RULES](NOVELTY_GROWTH_RULES.md) + [RESEARCH_PROGRAMS](RESEARCH_PROGRAMS.md) + [RESEARCH_MINES](RESEARCH_MINES.md) 决定。

**五个 parent programs 全部保持开放：**
1. R1 Data & Identifiability；
2. R2 Predictive Abstraction；
3. R3 Specialization vs Reuse；
4. R4 State / Belief / Information Gathering；
5. R5 Trust / Repair / Bypass。

当前 6 个 active seeds：I09/E14、I12/E16、I08/E13、I10/E17、I07/E11、I11/E18。I06/E08–E10 与 I03/E06–E07 为 diagnostics。

**一个 seed被近邻吸收、null或简单baseline解释，只 park seed，不关闭 R#。** 只有经过强baseline、系统measurement和多个seed后的人类 scientific-yield review 才能暂停 program。

I01/I02 = PARKED；I05 = SUPERSEDED by I07；E03/E04 = VOID。

本 workbench 的原则不是“必须先有方法”，而是：

> **先找到 community-relevant 的 actionable failure / tension，再用最小干预理解原因；方法应该从问题中长出来。**

## 1. authority

1. root AGENTS.md / workbench/EXECUTION.md
2. experiment card 跑前内容
3. NOVELTY_GROWTH_RULES.md
4. FIELD_PROBLEM_MAP_2026.md
5. RESEARCH_PROGRAMS.md
6. RESEARCH_MINES.md
7. POSITIONING.md
8. EXPERIMENT_PROGRAM.md
9. PAPER_LINEAGE.md / LITERATURE_LEDGER.md
10. 本文件
11. 旧 LATENT_PLANNING_SURVEY.md

任何 manuscript-critical事实最终回原论文/官方代码。

## 2. native layer 与 common audit layer

**Native layer**：官方repo各自环境，固定commit/checkpoint/config，先复制官方protocol。  
**Common audit layer**：统一candidate trace、sampler manifest、oracle/replay、result schema。

不先把所有method重写到一个framework。Bai/Xiong Temporal-Distance JEPA official repo因为已含 LeWM/RC-aux variants，是 M3/I06 **工程上优先的共同起点**；但其中variants是否精确等价于各原论文，必须另做provenance核对。

## 3. 执行顺序

### E00 / E01 — shared substrate
先跑一个 compact explicit WM native闭环、candidate logging、environment replay/oracle。不要先统一所有framework。

### Wave A：最多同时2个

#### E14 — R1 seed: trajectory/data semantics
TwoRoom / topology的 behavior-route intervention。  
这只是在 R1 里测一个 hypothesis，不代表“R1 = route bias”。

#### E18 — R5 seed: trust/recovery oracle
优先 released checkpoint + resettable evaluation；对同一 planning state比较不同 recovery actions 的真实 utility lift。

E08可CPU并行作为 R1 局部diagnostic。

### Wave B

#### E13 — R2 seed: predictive-object frontier
不是“planning vs policy”，而是寻找 one-step / direct-horizon / successor/occupancy / hybrid predictive object 的 regime boundary。

#### E17 — R3 seed: query specialization vs reuse
控制 query placement与 seen→unseen query/planner transfer。

### Conditional / next-seed

#### E11 — R4 seed
actionable hidden ambiguity oracle；当前seed弱/不存在不关闭 R4。

#### E16 — R1 second seed
equal-budget experience composition：coverage / excitation / route diversity / counterfactual branches。

### Shared
E02 / E06 用于所有 programs 的 candidate / bottleneck attribution。

**任何 seed结束后：**
1. 写它改变了对 parent R# 的什么认识；
2. 回 RESEARCH_PROGRAMS；
3. 至少考虑 boundary / interaction / reattribution / method / data-compute scaling中的2种研究动作；
4. 再决定下一个 seed。

禁止写“论文X做过，所以R#关闭”。

## 4. I06 实现事实：必须记住

### Bai/Xiong Temporal-Distance JEPA pinned code
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

Phase 1 不铺大矩阵，同时GPU pilot≤2：
1. Wave A：E14 + E18；
2. Wave B：E13 + E17；
3. E11按R4资产触发；
4. E16在R1 evidence支持时展开；
5. E08 CPU / dataset audit可旁路。

过 gate 后才：
- 3+ train seeds；
- second task structure；
- strongest nearest baseline；
- hold-out regime；
- conditional method ablation。

同节点先 stage local data 并测 data_wait；不要跨节点 DDP。研究室与实习资源默认不混用私有资产，只同步公开 code/config/metrics/manifest。

## 10. 写回 / 人审

每次运行：
- 实验卡结果
- P## only if real observed pain/success
- C## only with evidence
- logs/YYYY-MM-DD.md
- small commit/push

触发人审：
- 任一 R# seed 出现可投级 natural effect / regime law / method lever；
- E14 / E16形成 data principle；
- E13形成 predictive-object regime；
- E17形成 specialization↔reuse frontier；
- E11显示 belief/active-information 真正 load-bearing；
- E18出现 failure→repair mapping；
- E06/E07形成跨task law；
- science C##→L2；
- 需要改ACTIVE调度；
- 同一 program 多个 seed在真实实验后持续无scientific yield。

在预注册决策表范围内自主继续，不每跑一个job就停。