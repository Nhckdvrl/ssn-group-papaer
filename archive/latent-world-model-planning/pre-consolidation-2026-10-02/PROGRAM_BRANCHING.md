# Program Branching — 一个 seed 结束后怎么继续挖（2026-10-02）

> 目的：本地 agent 不得把单个 seed 当整个方向。  
> 每个 pilot 的结果都必须回答：**它让 parent R# 的哪种解释更可信/更弱？下一条最便宜、最有区分力的 research action 是什么？**

---

# R1 — Data & Identifiability

## Seed A: E14 behavior-route semantics

### A1 — route treatment改变 learned planning semantics + candidate regret，且 support/excitation controls 后仍成立
**解释：** higher-order trajectory organization 是独立于 local transition identifiability 的 data axis。

下一步至少选二：
1. 第二 objective（RC-aux / another temporal-planning objective）确认；
2. 第二 topology / contact-rich task；
3. multi-route mixture sweep，寻找 route-entropy / path-efficiency law；
4. 用 local Bellman / quasimetric / multi-route aggregation做 **mechanism-guided correction**；
5. 接 I12/E16，问 route diversity相对 action excitation / counterfactual branches 的 data value。

可能 story：
> Offline trajectories do not merely identify dynamics; they install a behavior-dependent planning geometry. Which aspects of data recover environment controllability?

### A2 — effect被 conditional action excitation 完全解释
**不是失败。** 这说明 P94-style identifiability 是当前 substrate 的主要 bottleneck。

下一步：
1. 转 E16 equal-budget data value：action excitation vs same-reset branches；
2. 研究 **global excitation vs decision-relevant excitation**；
3. query/candidate-specific action directions（R1↔R3 bridge）；
4. active acquisition：如何用最少额外 actions补最弱 decision-relevant directions。

可能 story：
> Global behavior diversity is not what matters; decision-relevant excitation governs planning data efficiency.

### A3 — effect被 state/action coverage解释，LeWM control也同幅漂移
下一步：
1. PLDM-style coverage regime，但进一步找 **which coverage dimension predicts candidate regret**；
2. equal transition budget下 coverage vs excitation；
3. failure/recovery coverage；
4. active coverage policy vs passive random。

不要继续“route semantics”。

### A4 — learned temporal/reachability geometry明显变，但 candidate/closed-loop不变
这是非常有价值的 **non-load-bearing result**。

下一步：
1. current-state / goal-state / planner-side oracle replacement；
2. 复用 P97 思路：直接 intervention internal geometry，测真正 bottleneck；
3. 找什么 regime（far goal / obstacle / low margin）geometry才开始承重；
4. 若始终不承重，转“planning-aligned representation metrics are overemphasized” comparative science。

### A5 — route treatment几乎不改变任何东西
park I09。R1转：
- I12/E16；
- failure outcome coverage；
- active probing；
- causal shortcut / mediation；
- query-aware data acquisition。

---

## Seed B: E16 equal-budget data value

### B1 — action excitation dominates across tasks
不要写“P94 again”。

下一步：
- local/global excitation decomposition；
- decision-relevant projected excitation；
- active data collection targeting weak directions；
- test whether same-reset branches are redundant once excitation sufficient。

### B2 — counterfactual branches dominate at equal budget
下一步：
- branch count vs state breadth frontier；
- which states deserve branching？
- active branch selection near decision boundary；
- passive broad data + sparse branches hybrid。

### B3 — route diversity / long-horizon structure dominates only at far horizon
下一步：
- horizon-conditioned data curriculum；
- predictive-object interaction（R1↔R2）；
- temporal objective vs explicit dynamics；
- derive data allocation law vs target horizon。

### B4 — failure data dominates candidate ranking despite similar prediction
下一步：
- FACT-like failure-aware control but on compact latent planning；
- candidate-hard-negative / failure-boundary acquisition；
- R1↔R5: failure data improves which recovery action?

### B5 — no single data type dominates; strong interactions
这可能是最好的结果。

目标从“best data”转成：
> **data components are complementary; environment/planner regime determines optimal composition.**

可长：
- small data allocation optimizer；
- scaling law；
- active mixture curriculum。

---

# R2 — Predictive Abstraction

## Seed: E13 continuum endpoints

### C1 — explicit wins when tasks/queries change; implicit wins fixed-task tight-compute
这是理想 regime law。

下一步：
1. 加一个中间 predictive object（Universal Horizon / Jumpy / hybrid）；
2. hold-out query/horizon验证 boundary；
3. derive adaptive placement rule；
4. compare training compute amortization break-even。

可能 narrative：
> Where prediction lives should depend on task volatility and deployment budget.

### C2 — explicit dominates everywhere after fair task-information accounting
不要马上关 R2。

问：
- implicit method是否 task inference/interface不匹配？
- long horizon / repeated-task / extreme latency regime是否还没到？
- direct arbitrary-horizon是否比 successor family更合适？
- fixed policy family vs arbitrary-action query是否是关键变量？

若加入合理 regimes仍 dominated，可形成：
> explicit task-agnostic dynamics are more reusable than current implicit abstractions under matched information budgets.

### C3 — implicit dominates everywhere
问：
- explicit planner budget是否不足？
- candidate proposal/search是不是瓶颈？
- arbitrary new cost/query下是否仍如此？
- perfect search/oracle candidate能否改变？

可能转向 search amortization / learned proposal，而不是结束 R2。

### C4 — ranking只跟 deployment compute走
研究对象变成：
> train-time amortization ↔ test-time search compute frontier。

可以做 compute principle，但必须跨 task / hardware-independent proxy（model calls/FLOPs）而不是单机 latency表。

### C5 — stochastic/contact task使 point models全坏，distribution/path方法才恢复
这时 Path-Space / Branch/Flow 从 method library进入：
- mean vs finite-support vs flow/path；
- uncertainty是否被planner真正消费；
- epistemic/aleatoric拆分。

---

# R3 — Specialization vs Reuse

## Seed: E17 query placement

### D1 — query-conditioned dynamics seen强、unseen明显掉；proposal/cost conditioning保reuse
自然 story：
> **specialize search, not physics.**

下一步：
- query complexity / dimensionality；
- model capacity；
- candidate-set adaptivity；
- second environment；
- selective modular architecture。

### D2 — query-conditioned representation既seen强又unseen不掉
这不是“没tradeoff”。

问：
- current queries是否太相似；
- capacity是否足够把通用+专用全部装下；
- query family dimension扩大后什么时候出现closure competition？
- Rank-One style objective dimensionality sweep。

可能 story：
> specialization is free until predictive closure exceeds latent capacity.

### D3 — query conditioning几乎无增益
下一步：
- current representation是否已含全部 needed info；
- planner/objective才是 bottleneck？
- task-relevant variables是否只需要cost读取而无需model specialization？
- TC-WM / TaskSense的优势是否只在 clutter/high-dimensional action regime？

### D4 — best placement随 planner/candidate generator改变
非常强的 R3 result。

可长：
> Query information should enter where the planner creates information bottlenecks, not at a universally fixed model layer.

---

# R4 — State / Belief / Information Gathering

## Seed: E11 actionable ambiguity

### E1 — finite history完全解决
park当前 belief seed，但R4继续：
- longer-lived hidden physics；
- occlusion；
- active info need；
- stochastic branching。

可形成一个 boundary：
> memory is sufficient for transient aliasing; explicit belief is only needed beyond history-identifiable regimes.

### E2 — history后仍 ambiguity，但 expected-action robust strategy已足够
belief representation可能不需要，planner robust objective更关键。

转：
- robust/risk-aware planning；
- minimax/expected cost；
- action-insensitive ambiguity measure。

### E3 — multi-hypothesis belief改善 prediction，但不改 action
internal uncertainty不承重。
转：
- active decision boundary；
- only evaluate ambiguity among action-changing hypotheses；
- belief consumption interface。

### E4 — belief改变 action，且 active probe比passive belief更值钱
这可长成 R4+R1：
> when should an agent resolve uncertainty before acting?

比较:
- maintain belief；
- robust action；
- probe environment；
- short-horizon information gathering。

---

# R5 — Trust / Repair / Bypass

## Seed: E18 recovery-action oracle

### F1 — one recovery action几乎总赢
router没必要。

下一步：
- 找这个repair的 failure boundary；
- 为什么它普适？
- compute/latency极端下是否切换？
- method简化。

例如 always replan胜 → 做 AdaReP-style minimal cadence law而非 router。

### F2 — best repair随 failure type明显切换
这是理想 signal。

下一步：
1. failure taxonomy；
2. simple existing signals预测 oracle action；
3. second task；
4. tiny router；
5. compute-aware utility。

### F3 — signals能检测“bad”，但不能预测哪种 repair
非常有意思：
> **failure detection is not repair diagnosis.**

下一步：
- intervention-derived features；
- one-step test action；
- causal attribution oracle；
- active verify step。

### F4 — detector score很好，但任何 repair都不提升 utility
说明 failure不可恢复或出现太晚。
转：
- earlier detection；
- active prevention；
- data collection（R1 failure data）；
- task abort/safety。

### F5 — recovery method ranking主要由 compute budget决定
转：
> compute-aware recovery allocation / metareasoning.

---

# Seed completion record

每个 seed结束必须附：

```text
Seed:
Observed result:
Which parent-program belief changed?
What old explanation survived?
What explanation weakened?
Nearest papers reinterpreted:
Two next research actions:
Why these are higher information gain than local optimization:
Decision: continue seed / park seed / promote claim
```

不允许：
> E14没显著，所以R1没戏。

允许：
> E14排除了route-order imprint作为R1的主要机制；P94 excitation解释增强。下一seed转 equal-budget excitation vs branching。
