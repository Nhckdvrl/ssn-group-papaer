# I06：Semantic negatives or geometric repulsion?（2026-10-02）

- **状态：** SEED / **first-priority mining lane**
- **来源：** 直接近邻内部的真实 tension，而不是“找空白”：
  1. **TD-JEPA** 明确用 cross-trajectory goals 做 hinge negatives，并在原文承认 trajectories share reachable states 时会有 false negatives；但 removing cross-trajectory hinge 在 Push-T 的 3-seed ablation 中又让所有 planner settings 变差。
  2. **RC-aux** 把 batch/cross-trajectory goals直接标成 reachability y=0，而同轨迹 temporal hard negatives才负责 budget identifiability；论文自己也强调 trajectory-derived labels只是 empirical proxy。
  3. **CGCIVL (ICML 2025)** 从相反方向证明 cross-trajectory pair 不能仅凭 trajectory identity 判 connected/unconnected。
  4. 标准 Contrastive RL / InfoNCE 中 negatives 主要承担 marginal normalization / density-ratio 对照，不等价于逐 pair 声明“不可达”。
- **研究动作：** 重新归因 + 引入构念 + oracle audit + 反事实/干预 + 最小修复。

## 母问题

> **当 plan-aware world model 把“来自另一条 trajectory / batch sample”直接当作 far 或 unreachable supervision 时，模型到底从这些 negatives 学到了什么？**

论文叙事通常给它们 planning semantic：
- TD-JEPA：off-trajectory cost 应至少超过 margin；
- RC-aux：cross-trajectory pair 在 budget h 内不可达。

但 sampling rule 本身只知道“不是当前 sample/trajectory”，不一定知道 MDP reachability。于是同一个 negative term 可能同时承担两种不同职责：

1. **semantic role**：告诉 planner 哪些 state-goal pair 真正不可达 / 超出 budget；
2. **geometric role**：提供 global separation、scale、dispersion 或 optimization pressure，使 representation / head 不塌成局部解。

## 如果为真，真正够强的主张

> Plan-aware latent world models can obtain substantial planning gains from heuristic cross-trajectory negatives even when a nontrivial fraction of those negatives are semantically reachable. The gain comes from a mixture of **semantic reachability supervision** and **non-semantic geometric regularization**. Conflating the two distorts planning calibration; separating them yields a more semantically faithful geometry without sacrificing—and potentially improving—closed-loop planning.

这不是“false negatives exist”。TD-JEPA 已经公开承认。必须完成 **semantic validity → mechanism reattribution → planning consequence → role-separating intervention** 四步。

## 关键 statistical distinction

### Contrastive negative
在 InfoNCE / density-ratio 解释里，negative sample来自 replay marginal，作用是 normalization/reference distribution；一个 sampled negative “其实未来可达”并不自动等价于错误的 binary semantic label。

### Semantic negative
TD-JEPA/RC-aux 对 pair 施加绝对 planning constraint：
- TD-JEPA：dψ(zs,zg) >= m；
- RC-aux：Rφ(zs,zg,h) = 0。

这里 pair 是否真的满足 “far/out-of-budget” 会直接影响 planning semantics。

**I06 的 novelty 要落在这种 semantic-negative conflation，而不是 generic contrastive-learning false negatives。**

## 最近近邻与 exact delta

| 近邻 | 已有 claim | I06 必须多走的一步 |
|---|---|---|
| TD-JEPA | cross-trajectory hinge有用；承认 reachable false negatives | 不重复 limitation；量化 semantic fidelity，并解释为什么有错误标签仍能带来 planning gain |
| RC-aux | batch negatives防 arbitrary reachability；temporal hard negatives识别 budget | 分离 cross-negative 的“unreachable semantic”与“global separation”作用，比较 calibrated reachability + planning |
| CGCIVL (ICML'25) | cross-trajectory pairs需区分 connected/unconnected | 从 offline value estimation 扩到 **visual latent-WM planning cost/head + MPC consequence** |
| Contrastive RL | replay-marginal negatives可实现 density-ratio/value learning | 说明 normalization negative 与 explicit semantic negative不是一回事 |
| Temporal Straightening / CGS | 不依赖 cross-trajectory semantic labels的 local geometry | 作为 negative-free / local-structure control，判断 global separation是否能由其它结构替代 |

## 不同结果各带来什么 information gain

- **A：false-negative rate高；FULL > NO-XNEG；ORACLE-VALID进一步改善 calibration/decision**  
  → heuristic negative确实有 semantic contamination；继续设计 non-privileged filtering/unknown-label方法。
- **B：false-negative rate高；FULL > NO-XNEG；ORACLE-VALID-only反而变差，但 count/gradient-matched non-semantic repulsion恢复 performance**  
  → **最有意思**：published gain主要不是“正确 negative semantics”，而是 geometric regularization；进入 role separation。
- **C：false-negative rate低，或几乎全是 oracle-valid negatives**  
  → concern在当前 benchmark不 load-bearing；I06 park，不制造更极端数据。
- **D：false negatives高，但 FULL/NO-XNEG/ORACLE-filtered planning差异都在 noise 内**  
  → semantic impurity存在但对 decision无后果；不升级。
- **E：TD-JEPA有该现象，RC-aux没有（或反之）**  
  → method-specific mechanism；可转成更窄的 method study，不强行统一。
- **F：简单 temporal-hard-negative-only / local geometry baseline 已完全取代 heuristic negatives**  
  → 可能形成“negative semantics unnecessary”更简单 story，但必须跨方法/任务确认。

## 决定性 pilot

E08：**先不训练新模型**。直接运行原训练 sampler / pair-construction 逻辑，配合 TwoRoom privileged state / environment oracle，测这些“negative”到底有多少是真 negative。

然后才是 E09：FULL vs NO-XNEG vs ORACLE-VALID/censored vs matched regularization。

如果 E09 指向 role conflation，再运行 E10。

## 顶会 story 的最低形态

不能止于：
> “TD-JEPA 有 X% false negatives。”

可能够的 paper 需要：

1. **New distinction:** contrastive/reference negatives vs planning-semantic negatives；
2. **Audit:** 至少 2 个 plan-aware WM objectives、至少 2 个 environments，oracle/observed evidence验证 semantic validity；
3. **Surprise:** semantically wrong negatives nonetheless are load-bearing，或 filtering them系统改善 decision；
4. **Mechanism:** negative semantic calibration vs geometric scale/dispersion/optimization分解；
5. **Repair:** role-separated objective，training-time不依赖 test oracle；
6. **Consequence:** fixed-candidate ranking/regret + closed-loop success；
7. **Scope:** topology + 至少一个 contact-rich setting；不能只做 TwoRoom toy。

- **预期论文形态：** 重新归因 + failure/identification + minimal repair。
- **排序（1–3）：** 证据 2（论文 limitation + ablation + code semantics） · 增量清楚度 3 · 形态匹配 3 · pilot成本 3 · 可完成性 3 · 不同结果信息增益 3
- **最大 compression risk：** “false negatives in contrastive learning is old.”  
  回答必须是：这里 negatives 被赋予**explicit reachability/distance semantics and used by a planner**；我们分解的是 semantic correctness 与 regularization utility 对真实 control 的不同作用。