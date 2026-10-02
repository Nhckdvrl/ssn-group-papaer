# HANDOFF — latent-world-model-planning

状态：**PROPOSED / literature+code-hardened / execution-ready / no local GPU result yet**。  
完整启动词见 [LOCAL_AGENT_PROMPT](LOCAL_AGENT_PROMPT.md)，实验细节见 [EXPERIMENT_PROGRAM](EXPERIMENT_PROGRAM.md)。

## 0. 不要从一个 loss 重新找钉子

领域 hardening 已经证明两个事实：

1. compact latent-WM 不是缺“小技巧”，而是同时存在 **state definition、predictive abstraction placement、offline supervision semantics、planner interface** 等真实问题；
2. 一个看起来漂亮的实验若 treatment 对真实 implementation 不可见，应该在跑 GPU 前就杀掉。旧 I01/E03–E04 就是这样 VOID 的。

当前科学入口由 [FIELD_PROBLEM_MAP_2026](FIELD_PROBLEM_MAP_2026.md) + [RESEARCH_MINES](RESEARCH_MINES.md) 决定，优先级不是平级：

1. **M3/I09 = Tier A1 / first scientific pilot**：behavior-policy trajectory semantics vs environment controllability；E14 → conditional E15。
2. **M2/I08 = Tier A2 / second scientific pilot**：predictive-computation placement frontier；E13 → conditional regime confirmation / hybrid test。
3. **M1/I07 = Tier B / conditional**：finite-history 后仍存在的 actionable hidden ambiguity；E11 → conditional E12。
4. **I06/E08–E10**：M3 的低成本 negative-role 子诊断，不再默认主论文。
5. **I03/E06–E07**：共享 bottleneck/oracle tool；只有形成 cross-task predictive regime law 才可能独立升级。

I01/I02 = PARKED；I05 = SUPERSEDED by I07；E03/E04 = VOID。

本 workbench 的原则不是“必须先有方法”，而是：

> **先找到 community-relevant 的 actionable failure / tension，再用最小干预理解原因；方法应该从问题中长出来。**

## 1. authority

1. root AGENTS.md / workbench/EXECUTION.md
2. experiment card 跑前内容
3. FIELD_PROBLEM_MAP_2026.md
4. RESEARCH_MINES.md
5. POSITIONING.md
6. EXPERIMENT_PROGRAM.md
7. PAPER_LINEAGE.md / LITERATURE_LEDGER.md
8. 本文件
9. 旧 LATENT_PLANNING_SURVEY.md

任何 manuscript-critical事实最终回原论文/官方代码。

## 2. native layer 与 common audit layer

**Native layer**：官方repo各自环境，固定commit/checkpoint/config，先复制官方protocol。  
**Common audit layer**：统一candidate trace、sampler manifest、oracle/replay、result schema。

不先把所有method重写到一个framework。Bai/Xiong Temporal-Distance JEPA official repo因为已含 LeWM/RC-aux variants，是 M3/I06 **工程上优先的共同起点**；但其中variants是否精确等价于各原论文，必须另做provenance核对。

## 3. 执行顺序

### E00 / E01 — common substrate
先把一个 compact explicit WM 的 native闭环、candidate logging、environment replay/oracle 跑通。不要为了统一框架先重写全部方法。

### E14 — M3 FIRST
真正改变 **generating behavior policy**，而不是只改 episode metadata。

第一轮：
- 公开 OGBench `navigate/stitch/explore` / `play/noisy` 只做 sensitivity discovery；
- 科学 pilot 必须进入 fixed start-goal 的 DIRECT vs DETOUR/LOOP；
- 同时量化 state/action/one-step-transition support overlap；
- 先 LeWM + Bai/Xiong Temporal-Distance JEPA，1 seed；
- learned score变化不够，必须走到 fixed-candidate rank/regret，最好再到 closed-loop。

只有 support/coverage 不能解释的 planning-aware-specific behavior imprint 才值得继续 E15 / second objective。

### E08 — M3 cheap subdiagnostic
dataset/sampler可读后即可并行。它审计 heuristic negative 的 semantic validity，但 **E08 本身永远不是 paper result**。

### E13 — M2 SECOND
common substrate 稳定后接 Bagatella TD-JEPA 与 explicit JEPA-WM/LeWM。优先 OGBench Cube pixels。

必须分开三本账：
1. training compute；
2. **task/query information budget**；
3. deployment compute。

Bagatella official OGBench evaluation约用 10k replay samples，并通过 OGBench `physics` relabel task reward再做 reward inference；这和 image-goal MPC 拿 goal observation不是相同 task specification。不能把这个差异偷塞进“inference cost”。

目标是找 explicit / arbitrary-horizon / implicit / hybrid 的 **regime frontier**，不是比较平均分。

### E11 — M1 CONDITIONAL
只做 cheap oracle，不先训练 belief architecture：
same RGB/different hidden state sanity → 加 native finite history → history能解则 STOP → 只有仍存在 action-relevant ambiguity且 baseline有candidate regret，才 E12。

### E02 / E06
作为 M2/M3 anomaly 的 common decision / bottleneck定位仪器，不先铺大矩阵。

**并行原则：** 第一轮允许 E14、E13、E11、E08 各做最小 existence test；随后只把大量 GPU 集中给过 gate 的 mine。

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

Phase 1 不铺大矩阵：
1. E14 DIRECT/DETOUR + LeWM/Temporal-Distance JEPA 各 1 seed；
2. E13 一组 OGBench Cube matched native/common audit；
3. E11 oracle only；
4. E08 CPU / dataset audit。

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
- **E14** 出现 support-controlled、对 candidate/closed-loop load-bearing 的 behavior imprint；
- **E13** 出现跨 task 可预测的 computation-placement regime boundary；
- **E11** 在 finite history 后仍出现稳定 actionable ambiguity；
- E09/E10 解释出 M3 的 load-bearing negative mechanism；
- E06/E07出现跨task regime law；
- science C##→L2；
- 需要改ACTIVE调度；
- 连续两个lead被强近邻/简单baseline吸收。

在预注册决策表范围内自主继续，不每跑一个job就停。