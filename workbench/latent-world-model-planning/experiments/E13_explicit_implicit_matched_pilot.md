# E13 — Predictive-computation placement frontier: matched pilot

- **状态：** PLANNED / **M2 second scientific pilot**
- **对应：** I08 / M2
- **问题：** reward-free offline learning中，predictive/planning computation应留在 explicit action-conditioned rollout + test-time search，还是 amortize到 successor/policy representation，或直接任意-horizon / hybrid结构？什么 regime 决定？
- **不是：** “LeWM vs TD-JEPA 谁分高”；“test-time search慢”；“implicit deployment快”。

## Strongest collision before running anything

**PLDM / Learning from Reward-Free Offline Data (NeurIPS 2025)** 已经系统比较 model-based latent planning vs multiple GCRL/model-free methods，并操纵：
- data quality；
- trajectory length / stitching；
- dataset size；
- random policy data；
- unseen layouts；
- new tasks；
- inference latency / replanning interval。

**Byravan et al. 2021 planner-amortization** 又已经研究 MPC + learned proposal 与 planner-to-policy distillation。

所以 E13 的 outcome不能是一张“什么时候 model-based vs policy更好”的表。

E13只有在能把差异定位到 **predictive object itself**，并超过 PLDM 的宏观比较，才有论文潜力。

## Direct literature anchor

TMLR 2026 *What Drives Success in Physical Planning with JEPA-WMs?* 已明确区分 explicit vs implicit world-model-like approaches，并把 **training cost / inference cost / generalization trade-off 的 direct empirical comparison** 留作 future direction。

当前代表：
- explicit: DINO-WM / JEPA-WM / LeWM；
- implicit: Bagatella TD-JEPA (ICLR 2026 Oral)；
- direct arbitrary-horizon / occupancy: Universal Horizon Models / Jumpy World Models；
- hybrid: TD-MPC2-like。

因此第一轮只比较 continuum 两端；中间方法只有发现 regime signature 后才加入。

## Common substrate

### First choice: OGBench Cube-single, pixels
原因：
- Bagatella TD-JEPA official repo原生支持 `cube-single-play-v0` pixels；
- stable-worldmodel / LeWM 生态也有 OGBench Cube；
- 同 environment / data family / success checker；
- 可扩 Scene/Puzzle 做第二 task structure。

### Native facts already audited
Bagatella TD-JEPA OGBench pixel launcher：
- 1,000,000 training steps；
- batch size 256；
- DrQ encoder feature dim 256；
- official eval 10 episodes/task；
- `num_inference_samples=10_000`。

其 reward inference：
- 从 train replay buffer采样 next observations；
- 用 OGBench task relabeler读取 `physics` 计算 task rewards；
- 将 rewards + next observations交给 model reward-inference routine。

这意味着它与 image-goal MPC 的 **task information interface不同**。这是必须控制的 confound，不是小实现细节。

## Q0 — 先做 GOAL-Z query bridge（极便宜但决定公平性）

TD-JEPA paper的 official test-time task inference是：

[
z_r = C_psi^{-1}mathbb E[psi(s)r(s)]
]

（具体实现用 least squares）。

但 official OGBench training code会把 next-state task embedding作为 training latent，并在 `scale_train_goals=True` 时执行 covariance scaling后 projection。因此先做一个 common-protocol probe：

```text
goal observation g
→ psi(g)
→ training-matched inverse-cov scaling
→ project_z
→ pi_z
```

比较：
- `GOAL-Z`：一张 goal observation；
- `GOAL-Z-k`：goal neighborhood / k positive exemplars；
- `REWARD-Z-N`：official reward inference with N reward-labeled states；
- official `REWARD-Z-10k`。

记录：
- latent cosine / norm；
- first-action agreement；
- rollout success；
- goal-distance bins。

**GOAL-Z 是 exploratory common-interface diagnostic，不是论文官方 baseline。**

决策：
- GOAL-Z接近 reward inference → 后续 M2 优先用 same-goal-information comparison；
- GOAL-Z很弱 → 保留 reward inference，但 task-info budget必须作为 regime axis；
- GOAL-Z只有某些 goal neighborhood有效 → 这说明 task abstraction granularity本身是 confound，需要显式记录。

## 三本预算账

### 1. Training compute
- steps / samples；
- GPU-hours；
- peak VRAM；
- encoder size；
- augmentation；
- dataset bytes actually read。

### 2. Task/query information
- goal image / goal state；
- known reward function；
- reward-labeled inference samples N；
- privileged state / physics是否参与 task relabel；
- interaction episodes（若有）。

### 3. Deployment compute
- model forward calls；
- candidate rollouts；
- search iterations；
- wall-clock / action；
- memory。

**不能把 query-information advantage折进“inference compute”一项。**

## Minimal experiment

### P0 — native sanity
各自在 official protocol 上复现 direction，确认实现正确。

### P1 — common task utility
同 OGBench single-task success checker和 fixed task list。Q0若证明GOAL-Z可用，增加 **same single-goal-observation** common protocol；否则不假装 task interface相同。

保留两种 task interface，**不强行假装相同**：
- explicit: goal observation / goal state；
- implicit: reward inference。

第一张图应该直接展示三维 trade-off：
`task success × task-info budget × deployment compute`，而不是单一 success。

### P2 — task-information sweep
Bagatella TD-JEPA:
- N = small / medium / official 10k reward-inference samples；
- 若可行，state vs pixel relabel information单独标。

explicit:
- one goal observation；
- multiple goal exemplars（若自然支持）；
- 不给额外 oracle reward标签。

**OpTI-BFM (ICLR 2026)** 已直接研究 BFM reward task inference burden，所以本 sweep 只是 fairness/accounting，不是 novelty。

### P3 — horizon
same task family下 near / medium / far goal bins。

### P4 — objective/query shift
训练 data/dynamics不变，切 unseen task/reward/goal composition。

### P5 — dynamics/layout shift
仅 P1–P4 出现 meaningful frontier后做。

## P6 — predictive-object isolation（只有前面有 switch 才做）

一旦两端出现稳定 relative-ranking switch，再加入 **一个中间 predictive object**：
- Universal Horizon Model；
- Jumpy WM；
- 或 TD-MPC2 hybrid。

然后问：
- 中间方法是否落在由同一个 regime variable预测的位置？
- 还是原来的 switch 其实只是 actor/search implementation差异？

若中间方法不支持 continuum explanation，M2应该收缩或停止，不事后画漂亮曲线。

## What counts as a result

### 可能有科学价值
- explicit 在 low task-info / high task-redefinition regime占优，而 implicit 在 repeated/fixed task + tight deployment compute占优；
- 一个简单 observable (task-info budget, horizon, query novelty, deployment compute) 在多个task上预测 family ranking；
- direct-horizon / hybrid方法填补两端之间可预测区域；
- hold-out regime能提前预测哪种 computation placement更合适。

### 不够
- explicit平均分更高；
- implicit快很多；
- 一个方法训练更久所以更强；
- state输入胜pixel；
- 只画 Pareto但没有可迁移的 regime law。

## Confounds

- reward function vs goal observation不是等价 task specification；
- Bagatella official reward inference使用 privileged `physics` relabeler；
- offline datasets / preprocessing若不同，不能叫 matched；
- task success definition必须统一；
- train compute与deployment compute分开；
- inference sample N与search candidate N含义不同；
- actor/policy family capacity与explicit optimizer budget都可能成为bottleneck；
- native hyperparameter tuning不能偷偷只为一边做。

## Gate

- **G0:** native baselines可复现；
- **G1:** common task utility与data revision对齐；
- **G2:** 至少一个 regime variable造成稳定 relative-ranking change，而不是固定winner；
- **G3:** compute + task-information confounds不能完全解释；
- **G4:** second task structure复现；
- **G5:** hold-out regime预测成立。

过 G2 后才接一个中间 family（Universal Horizon / Jumpy / TD-MPC2）验证是否真是 continuum。  
没过 G2：M2不扩矩阵。

## 结果
未运行。
