# E14 — Behavior-policy intervention on planning semantics

- **状态：** PLANNED / **M3 first scientific pilot**
- **对应：** I09 / M3
- **问题：** 在 environment dynamics 不变时，改变 generating behavior policy，trajectory-derived planning objectives 是否把 behavior route / tempo 写进 deployed planning semantics，并进一步改变 candidate ranking / closed-loop MPC？
- **不是：** “data distribution matters”；“suboptimal data hurts”；“behavior path != shortest path”。这些 broad statements 已有 PLDM / quasimetric / CGCIVL 等 ownership。
- **与 VOID E03/E04 的区别：** E03/E04 只改 long-episode factorization，而 pinned Temporal-Distance JEPA / RC-aux 主要 loss 只读取 short clips，treatment 对 objective 不可见。本 E14 必须改变 objective 实际看到的 trajectory pairs / temporal gaps。

## Stage A — public-regime discovery（便宜，只看 sensitivity）

### A1 topology
OGBench locomaze 官方 generator 已提供：
- `navigate`：长 episode 内反复去随机目标；
- `stitch`：近目标、短 episode；
- `explore`：每 10 step 改随机方向；
- `path`：去单一目标后停留（generator支持，标准 commands 未全部发布该 dataset）。

这些 regime 会同时改变 goal schedule / occupancy / horizon / action distribution，所以 **A1 不能承担因果 claim**。用途是快速找：
- 哪个 objective 最敏感；
- 哪个 environment 有足够 effect size；
- 哪些 support bins 仍有重叠。

### A2 contact-rich
OGBench manipulation generator：
- `play`：non-Markovian PlanOracle 按 precomputed plan；
- `noisy`：Markov closed-loop oracle + per-episode Gaussian noise + optional random actions。

同样只作 broad discovery。

## Stage B — controlled behavior intervention（真正决定 M3 去留）

首选 TwoRoom / PointMaze-like topology。

固定：
- environment / dynamics；
- start-goal manifest；
- episode count；
- transition budget；
- render / action scaling；
- eval starts/goals；
- model architecture / optimizer / steps。

至少生成：
1. **DIRECT**：近 shortest / oracle-guided route；
2. **DETOUR**：同 start-goal，但人为插入可控绕路 / loop；
3. **MIXED**（若前两者有明显 effect）：同 pair 混合多条 route。

每条 trajectory 保存：
- observed path length；
- oracle shortest length / certified bound；
- path efficiency = observed / shortest；
- route class；
- local transition/action statistics。

## Support / identifiability matching — 这是本实验成败关键

**P94 `On the Identifiability of Controlled World Models` 是新的强 confound。** 它已证明 behavior policy 的 conditional action variation 会决定 controlled transition identifiability，并进一步影响 counterfactual planning。若 DIRECT/DETOUR 的差异只是 action excitation不同，M3没有新意。

因此 E14 除普通 coverage 外，还必须估计/匹配 **conditional action excitation**。连续状态下可用 state bins / kNN neighborhoods / learned state clusters 估计：
- local action covariance；
- minimum eigenvalue / effective rank；
- action residual after local mean policy；
- weakly excited action directions。

若能直接用 simulator state/qpos-qvel做 measurement-only estimate，优先使用；不把它喂给 pixels-only model。

M3 真正想留下的 residual question 是：

> **在 conditional action excitation 与 one-step transition evidence都足够、且两数据 regime近似匹配时，higher-order route/temporal organization本身是否仍系统改变 trajectory-derived planning semantics？**

这正是与 P94 的 exact delta。

## Support matching — 普通 coverage 也必须控制

不能只说“环境一样”。

至少报告：
- state occupancy histogram / kNN density overlap；
- action histogram / norm / direction overlap；
- **conditional action covariance / excitation overlap（P94 control）**；
- one-step transition nearest-neighbor support；
- start-goal distribution equality；
- local velocity / qpos/qvel distribution（若有）；
- effective sample size after matching / reweighting。

优先顺序：
1. 生成时匹配；
2. stratified subsampling；
3. propensity / density reweighting；
4. 若仍严重不重叠，诚实标为 broad distribution shift，不给 behavior-semantic causal claim。

### 更强的 matched variant（若可行）
从相同 primitive/local-transition pool 构造不同 multi-step route frequency，使 one-step marginals尽量接近、higher-order co-occurrence / temporal gap不同。  
**不要**为了追求形式完美，重新造一个与现实 planner不兼容的 toy MDP；先用真实 benchmark 找信号。

## Methods

首轮：
1. **LeWM**：non-temporal-supervision control；
2. **Bai/Xiong Temporal-Distance JEPA**：trajectory temporal semantics；
3. **RC-aux**：只在 #2 显示 signal 后接，作为第二 objective family。

不先加新 loss。

## Measurement chain

### Supervision semantics
- observed temporal gap；
- cross-pair / negative type；
- learned TD / reachability score；
- environment shortest/geodesic oracle。

### Dynamics guard
- one-step prediction；
- matched multi-step rollout；
- action sensitivity。

### Planner-consumed consequence
固定 candidate pools：
- random / mid / elite；
- learned score vs environment utility rank；
- selected-action regret；
- route-class bias；
- candidate flip between behavior-trained models。

### Closed-loop
同 fixed eval manifest：
- success；
- steps-to-goal / task cost；
- failure route category。

### Auxiliary only
- latent visualization；
- behavior-regime classifier probe；
- linear probes。

这些不能自己成为主结论。

## Positive / negative controls

- **Positive:** Temporal-Distance JEPA 的 learned temporal cost应对明显不同 temporal statistics有响应，否则 harness可能没接对。
- **Negative:** LeWM 若在严格 matched local support 下也产生同等幅度 decision drift，先解释普通 data coverage / representation shift。
- **Oracle:** environment D* / shortest route本身在各训练 regime间不变。
- **Protocol:** H/K/action-block/candidate budget固定；先过 LeWMRO-style time-index sanity。

## First-run budget

不要全矩阵。

1. topology env；
2. DIRECT vs DETOUR；
3. LeWM + Temporal-Distance JEPA；
4. 1 train seed exploratory；
5. fixed 50–100 start-goal candidate audit；
6. 只有 candidate/closed-loop effect超过 noise 才加 seeds / RC-aux。

## Gate

- **G0:** training supervision实际因 behavior treatment而变化；否则设计无效。
- **G1:** state/action/local-transition support **以及 conditional action excitation** overlap可接受；否则只作distribution-shift / identifiability记录。
- **G2:** learned planning semantics在 DIRECT/DETOUR 间系统变化。
- **G3:** fixed-candidate rank/regret或selected action出现稳定变化。
- **G4:** closed-loop consequence成立。
- **G5:** LeWM control明显更弱，或能被一个 planning-aware-specific mechanism解释。
- **G6:** 第二 objective / task structure复现 → M3可进入 E15 / paper-hypothesis 阶段。

如果只过 G2 不过 G3/G4：不升级。  
如果 G3/G4 全被 support variables预测：收敛到 coverage，不强写 behavior semantics。

## 结果
未运行。
