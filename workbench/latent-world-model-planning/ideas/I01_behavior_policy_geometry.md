# I01：Trajectory-factorization dependence — planning geometry 是否继承 behavior routing？（2026-10-02）

- **状态：** SEED / first-priority mining lane
- **来源：** 不是“空白”。它来自一条具体的 related-work 张力：RC-aux / TD-JEPA / Traj-LeWM 从 observed trajectories 构造 planning-aware long-range supervision；TD-JEPA 原文把 observed temporal gap 视为 shortest distance 的 upper-bound/surrogate，RC-aux 也明确说 trajectory offset 不是 ground-truth shortest reachability；NeurIPS 2025 Quasimetric GCRL 与 ICLR 2026 Multistep Quasimetric 则明确区分 behavior future statistics 与 optimal goal-reaching structure。Temporal Straightening 也提醒 suboptimal trajectories 可扭曲 temporal geometry。详见 `PAPER_LINEAGE.md` P04–P06/P14/P15/P42/P51。
- **研究动作：** 干预/反事实 + 重新归因 + 引入成熟构念（behavior-invariance / quasimetric）+ 最小修复。
- **工作构念：** **trajectory-factorization dependence / route imprinting**。同一个 empirical transition graph / local one-step evidence 可以被组织成不同合法 trajectories；如果 planning geometry 是 environment controllability 的属性，那么只改变这种 factorization/routing 不应任意改变最终 decision geometry。

## 如果为真，真正够强的主张

> 在 **environment dynamics、raw local transition multiset、one-step training windows 与视觉内容被控制** 时，只改变这些 transition 如何被合法地串成 trajectories / routes，就能系统改变 trajectory-supervised JEPA planner 学到的 reachability/progress geometry，进而翻转 CEM candidate ordering 与 closed-loop decisions；说明这类“planning-aligned” long-range supervision 可能学习到 behavior-routing geometry，而不是仅由 environment controllability 决定的 geometry。

这比“trajectory temporal gap 不是 shortest path”强得多；后者已有论文明确承认。

若上述链成立，第二部分才研究：能否用 **local dynamics / Bellman / quasimetric consistency、multi-route aggregation 或 interval/lower-bound target** 提供更强的 trajectory-factorization invariance。

## 最干净的 identification：valid trajectory refactorization

首个 pilot 不做任意 metadata corruption，而做**合法 cut-and-splice / refactorization**：

1. 从 navigation 数据构建 transition multigraph；
2. 找共享状态/等价 junction，使两段真实 trajectory 可以在 junction 处合法拼接；
3. A/B 使用**完全相同的 raw transition multiset**；
4. local one-step / fixed-history windows 的 multiset hash 保持一致；
5. 只让 long-range within-trajectory pair membership / temporal gap statistics 改变；
6. environment MDP、visual observations、actions、dataset size、optimization exposure 不变。

另外可以做一个更弱但很便宜的 **split-only segmentation sensitivity**：仅把长 episode 切成多段，检查方法是否对 logging boundary 敏感。它可作为 sanity check，但单独成立不够顶会。

## 不同结果各带来的信息增益

- **A：supervision target → learned geometry → fixed-candidate ranking → closed-loop 都随 refactorization 改**  
  → 这是 I01 的核心链；进 E04 natural behavior route intervention，再研究最小 correction。
- **B：target/head 变，但 candidate ranking/control 不变**  
  → proxy 确实 behavior-dependent，但不是 load-bearing；不包装 paper。
- **C：RC-aux/TD-JEPA 对 valid refactorization 基本 invariant**  
  → 强负结果；研究它的哪个结构抵消了 behavior imprinting，可能转成“为什么简单 proxy 比理论担心的更 robust”。
- **D：LeWM/local control baseline 也变**  
  → local sample/augmentation/context 没控制干净；实验作废，不能归因。
- **E：只有 split-only 有效、valid splice 无效**  
  → 多半是 logging-boundary artifact，不够强，除非现实数据 pipeline 中广泛存在并有实际 consequence。

## 最近直接近邻与 exact delta

| 近邻 | 它已经拥有的 claim | 我们必须多走的一步 |
|---|---|---|
| RC-aux | trajectory offset proxy + finite-budget reachability | 同 local dynamics evidence 的 **trajectory factorization intervention**，并连接到 real candidate/control |
| TD-JEPA | observed step order/gap mined directed progress；gap 是 D* upper-bound/surrogate | 不再证明 surrogate 有偏；证明 route/factorization **非不变性**是否成为真实 MPC failure |
| QRL / Multistep Quasimetric | suboptimal behavior data 下恢复 optimal goal-reaching distance | 把 behavior-vs-optimal distinction迁入 latent-WM training objective，并做 visual MPC consequence |
| Temporal Straightening / CGS | local trajectory/control geometry regularization | 作为不依赖 long-range path labels 的 negative/control family，检验 route sensitivity 是否特属于 trajectory-supervision |
| Behavior-Invariant Task Rep (ICML'26) | offline meta-RL 中 task latent 对 behavior policy invariant | 不能泛称“behavior-invariant representation”；我们的对象是 **planning geometry + same local dynamics + route factorization + MPC** |
| Traj-LeWM | full-trajectory preference / failed-rollout path cost | 说明 path supervision 的 route semantics 是否 stable，而不是再提一个 trajectory head |

## 最便宜的决定性 pilot

[E03](../experiments/E03_trajectory_partition_invariance.md)

- **阳性对照：** A/B refactorization 后，预注册的一组 long-range pairs 的 membership / temporal target 必须按构造改变；local transition + one-step-window hashes 必须完全一致。
- **阴性对照：** LeWM one-step baseline；有余力时加 Temporal Straightening 或 CGS 这种 local-transition geometry method，预期对 long-range trajectory refactorization 更不敏感。
- **噪声地板 + MIE：** 相同 dataset view + seed 的 manifest 与 evaluation repeat；E02 后冻结 ranking/regret MIE。只有 geometry/head 变化不够，至少 fixed-pool decision metric 必须超过噪声。
- **决策表：** A → E04；B → PARK scientific claim；C → robustness follow-up 但不强行救原 story；D → VOID 重做 identification。

## 顶会 story 的最低形态

如果最后只是：
> “我们切了 trajectory，RC-aux head 变了。”

不够。

可能够的形态必须接近：
1. **Identification:** same local dynamics evidence, different valid trajectory factorization；
2. **Failure:** existing trajectory-supervised planner learns different geometry and makes different decisions；
3. **Principle:** planning geometry should be invariant to behavior routing / logging factorization beyond what dynamics imply；
4. **Minimal repair:** dynamics-defined/local-consistency or multi-route objective restores invariance；
5. **Scope:** ≥2 trajectory-supervised methods + ≥2 task regimes；navigation exact oracle + contact-rich consequence；
6. **Strong controls:** LeWM/local-geometry negative controls + quasimetric/optimal-distance conceptual baseline。

- **预期论文形态：** 失败模式 + identification + minimal repair；若能形式化则加理论/受控。
- **排序打分（1–3）：** 证据 1 · 增量清楚度 3 · 形态匹配 3 · 成本 3 · 可完成性 3 · 不同结果的信息增益 3
- **最大 compression risk：** reviewer 说“MC temporal distance 本来就是 behavior dependent”。回答必须靠 same-transition refactorization + latent-MPC consequence + invariance repair，而不是措辞。