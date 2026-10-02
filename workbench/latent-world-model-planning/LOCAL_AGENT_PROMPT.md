# Local Agent Prompt — latent-world-model-planning

把本文件作为执行机 agent 的启动提示。**不要从头找题，也不要因为某个现有实验卡写得最详细就把它当主论文。**

---

你正在 `Nhckdvrl/ssn-group-papaer/workbench/latent-world-model-planning/` 工作。

## 最终目标

从 compact latent world-model planning 中发展一篇 **ICLR / ICML / NeurIPS / CVPR 级**论文。

我们的资源优势不是多节点大预训练，而是很多独立 GPU：适合强 baseline、受控 intervention、多 seed、多环境、oracle audit、idea iteration。网络/磁盘/节点通信差，不做跨节点大训练。

最重要的是 **problem-led research**：

> 找到这个领域真正关心、会改变模型/方法设计的 failure / tension；  
> 用实验把问题压实；  
> 再让方法从问题本身自然长出来。

禁止把“我做了一个新 probe，某个位置行为奇怪”当研究目标。内部读数只有连接到 candidate decision / regret / closed-loop behavior 时才有科学重量。

当前科学 claim = 0；M#/I# 全是 mining seeds，不是结论。

## 必读顺序

1. root `AGENTS.md`
2. root `RESOURCES.md`
3. `workbench/README.md`
4. 本目录 `README.md`
5. **`NOVELTY_GROWTH_RULES.md`**
6. `FIELD_PROBLEM_MAP_2026.md`
7. **`RESEARCH_PROGRAMS.md`**
8. `PAPER_LINEAGE.md`
9. **`RESEARCH_MINES.md`**
10. `LITERATURE_LEDGER.md`
11. `PROBLEM_METHOD_MAP.md`
12. `POSITIONING.md`
13. `EXPERIMENT_PROGRAM.md`
14. `ASSETS.md`
15. `HANDOFF.md`
16. `CLAIMS.md` / `PAIN_LOG.md`
17. I07–I12 + I03/I06
18. E00–E18

然后运行：

```bash
python3 tools/process/check.py
```

ERROR 先修；WARN 理解后处理。不要为清 warning 机械修改科研内容。

## 三个容易混名的 JEPA 必须分清

- **Bagatella et al. TD-JEPA**, ICLR 2026 Oral, `facebookresearch/td_jepa`：zero-shot RL / successor features / implicit long-horizon predictive representation。
- **Bai & Xiong Temporal-Distance JEPA**, arXiv 2607.25337, `HKBU-KnowComp/Temporal-Distance-JEPA`：LeWM/CEM planning，trajectory temporal distance + heuristic negatives。
- **D-JEPA: A Decision-Aligned Latent World Model**, arXiv 2609.24749：candidate-local ordinal decision alignment，又是另一条线。

Temporal-Distance repo历史 config 仍叫 `td_jepa`。跨repo manifest只用 `bagatella_td_jepa` / `temporal_distance_jepa` / `decision_aligned_d_jepa`，禁止裸 acronym 聚合。

# 1. 先继承 research programs，不重新 hunt empty gap

**最重要的规则：**
- paper 可以拥有一个 atomic claim；
- paper 不能拥有整个 research program；
- “近邻很多”通常说明 community care，不是自动降级；
- 一个 seed撞车 / null / 被baseline吸收，只 park seed，必须回 parent R# 继续挖；
- 直接近邻若要作为“不能做”的理由，至少深读 method + experiments + related work + limitations；abstract-only只能导航。

当前 programs：

### R1 — Data & Identifiability
**母问题：** 什么 experience 才能让 world model识别 counterfactual action effects / controllability并真正服务planning？

现有工作分别回答 action excitation、trajectory geometry、counterfactual branches、active probing等局部答案。

活跃：
- I09/E14 behavior-route semantics；
- I12/E16 equal-budget data value；
- I06/E08–E10 negative-role subdiagnostic。

E14若失败，**不要写 R1失败**；转 E16 / active probing / counterfactual data / failure-recovery data。

### R2 — Predictive Abstraction
**母问题：** world model 应学习 one-step、direct horizon、path distribution、successor occupancy、macro transition还是hybrid？

活跃：
- I08/E13。

E13不是两方法排行榜；它用于找下一条 regime axis。若端点没有切换，转 stochasticity / horizon / query flexibility / intermediate predictive object，而不是关闭 R2。

### R3 — Specialization vs Reuse
**母问题：** query/task conditioning 应放在哪一层，才能兼顾 seen-query decision efficiency 与 unseen-query/planner reuse？

活跃：
- I10/E17。

P38 / Value Equivalence / WorldTest / Task-Sufficient WM 是这条 program 的强坐标，不是封锁线。

### R4 — State / Belief / Information Gathering
**母问题：** partial observability / hidden physics 下，正确 predictive state 是 point / memory / belief / active information gathering 哪一种？

活跃：
- I07/E11。

若短 history解决当前 aliasing seed，park I07当前版本；R4可转 active disambiguation、belief-consuming planner、hidden-physics identification。

### R5 — Trust / Repair / Bypass
**母问题：** world model 不可靠时，何时 replan、shorten horizon、adapt、feedback-correct、increase compute或fallback？

活跃：
- I11/E18。

IMWM / AdaJEPA / Feedback WM / AdaReP / MEND 是不同 recovery action 的已知答案；我们先找 failure-type→best-repair mapping。

### Shared diagnostics
- I03/E06–E07 = bottleneck oracle；
- I06/E08–E10 = R1局部机制；
- E02 = candidate decision calibration。

# 2. Step 0 — 资产盘点与 E00

先看机器已有 repo/env/data/checkpoint，禁止重复下载。

写回 ASSETS 状态：

```
public entry
→ downloaded + hash
→ loadable
→ smoke passed
→ native numeric reproduction
→ instrumented common audit
```

不同 repo 可不同 venv。不要为统一 framework 破坏 native baseline。

E00 单 GPU：
- dataset/checkpoint可读
- env/action/goal/success checker
- encode→rollout→plan→act
- train step
- planner call
- VRAM
- env/render time
- I/O wait

不要上来跑满 100 epochs。

# 3. Step 1 — E01 common substrate

至少：
- 一个 explicit compact WM native checkpoint / native protocol；
- candidate logger旁路；
- env reset/replay；
- true candidate utility；
- H/K/action block/scoring index manifest；
- TwoRoom或类似 topology + 一个 contact-rich environment 的入口。

native result 与 common audit result分开。

# 4. First-wave program mining：每次最多2个 pilot

仓库规则仍是 simultaneously running pilots ≤ 2。不要因为有很多卡就同时启动6个方向的大矩阵。

## Wave A

### E14 — R1 / I09
TwoRoom / topology下改变 behavior route；support + action excitation审计；fixed-candidate / closed-loop consequence。

目的不是把 I09做到底，而是回答：
> R1 中 trajectory organization是否值得继续？

### E18 — R5 / I11
优先 released checkpoints / evaluation-first。对同一 planning state执行不同 recovery actions，构建 oracle intervention ranking。

目的：
> R5 是否存在“不同 failure需要不同 repair”的真实结构？

E08若dataset ready可作为低成本旁路 audit，不占GPU主pilot。

## Wave B

Wave A 任一分支进入等待/完成后启动：

### E13 — R2 / I08
predictive-object continuum的最小 matched pilot。三本账：
- training compute；
- task/query information；
- deployment compute。

### E17 — R3 / I10
query-placement × seen/unseen reuse 小矩阵。

## Conditional / next seeds

### E11 — R4 / I07
cheap environment oracle；不先训练belief model。

### E16 — R1 / I12
若 R1仍有科学压力，固定 transition budget比较 coverage / action excitation / route diversity / counterfactual branches 的 planning value。

**重要：** E14/E18/E13/E17/E11/E16 的顺序是当前 information-gain 排程，不是哪个 program“更有资格”。任何新结果都可以改变排序。

# 5. 方法什么时候允许出现

新方法优先来自真实 evidence，但**不禁止 method-led exploration**：如果一个成熟方法原理（quasimetric、belief filtering、structured dynamics、active probing、adaptive compute等）在 program 中给出明确、可检验的新预测，可以直接注册成 seed。不能做的是“因为喜欢一个模块所以随便找benchmark”。

当前证据入口包括：
- R1：data role / identifiability / intervention value；
- R2：predictive-object regime；
- R3：specialization↔reuse frontier；
- R4：belief / active information need；
- R5：failure→repair mapping；
- shared oracle：某 layer 被确定为 binding bottleneck。

优先最小解释。

不要：
- RC-aux + 一个 loss；
- LeWM + 一个 module；
- “换成更复杂 Transformer”；
- 因为某个 probe看起来差就做 regularizer；
- 先有喜欢的 method 再找 benchmark。

# 6. 共同 attribution rules

- probe变、decision不变 → 不是主 finding；
- prediction error变、candidate ranking不变 → 不夸大；
- candidate pool没有好plan → 不只修 metric；
- true dynamics仍失败 → 不只怪 predictor；
- encoded-real score就错 → metric/representation；
- H/K/scoring-index control能救 → protocol layer；
- behavior intervention同时改变 coverage → 先拆 coverage；
- history能完全解 alias → 不声称 belief必要；
- explicit/implicit比较没匹配 data/task/compute → 不做 scientific ranking；
- oracle方法只作 measurement / upper bound，不冒充 deployable method。

# 7. 多 GPU 怎么用

第一轮每个 **program seed** 都只做 small decisive pilot；同时实际运行不超过2个。

一旦某条过 gate，再把独立卡用于：
- train seeds
- behavior regimes
- aliasing strength
- hidden-factor family
- goal/reward shifts
- candidate budgets
- confirmatory environment
- ablation / nearest baseline

同节点先 stage local data；1→2→4 jobs测 I/O 退化。不要跨节点 DDP。

大量 GPU 的价值是 **加速 scientific iteration**，不是扩大单次训练规模，也不是铺没有判别力的 Cartesian product。

# 8. 文献与 novelty 是滚动的

2026 latent WM 更新极快。每次出现以下情况都重扫直接近邻：

- 某个 E## 出现明显 anomaly；
- idea准备从 SEED → paper hypothesis；
- C## 升 L2；
- 要设计方法；
- 要跨 benchmark；
- candidate / 投稿前。

深读新近邻时记录：

```
mother question
old assumption
pressure / counterexample
idea leap
method
data / benchmark
decisive experiment
nearest related work
exact delta
claim ownership
what it closes
what it opens
```

不要只加 citation。

# 9. 写回

每 run：
- 对应 experiment card
- raw大文件留节点；git写 hash/path/summary
- PAIN_LOG 只记真实 P##
- CLAIMS 只记 evidence-backed C##
- logs/YYYY-MM-DD.md
- small commit/push

每次新 experiment 先写 card / amendment，再跑。

# 10. 什么时候人审

- E11出现明确 actionable aliasing且 history baseline仍失败；
- E14出现跨objective/task的 behavior imprint；
- E13出现 stable explicit/implicit regime boundary；
- E09说明 negative真正 load-bearing role；
- E06/E07形成 cross-task regime law；
- C## 到 L2；
- 需要改变 ACTIVE 资源调度；
- 一个 seed被近邻/简单baseline吸收后，需要回 parent R# 产生新seed；
- 同一 program 连续多个 seed在系统measurement后都无scientific yield，才触发人审是否暂停 program。

汇报只需：
1. E## / commit / artifact hash
2. 最重要数字 + CI / train-seed variance
3. 这个结果解决了哪个 **problem question**
4. 排除哪些平凡解释
5. 最近 direct neighbor pressure
6. 下一组最便宜决定性实验
7. 真正需要人决定的事

**不要把工程进度当科研进度。**
