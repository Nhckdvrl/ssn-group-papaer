# E16 — Query-Conditioned / Decision-Relevant Excitation

- **状态：** PLANNED / theory+controlled pilot
- **对应：** I10 / M3 Data-Centric Plannability
- **目标：** 检验 global controlled-transition identifiability 是否比 specific planning decision 所需更强，并寻找 query/candidate-sensitive data sufficiency law。

---

## Phase A — linear controlled sanity（CPU / tiny GPU）

设：

\[
z_{t+1}=Az_t+Ba_t+\epsilon_t.
\]

observation 可先 identity，再加 nonlinear invertible map。

### Data construction

构造多个 behavior policies：
- conditional action covariance eigenvalues 完全相同；
- 只旋转 covariance eigenvectors；
- state distribution 尽量相同；
- sample count 固定。

2D action 例：
- Dataset X：high excitation 主要沿 x；
- Dataset Y：high excitation 主要沿 y；
- 两者 global rho / trace / determinant 相同。

### Query / candidate families

至少：
- Qx：candidate outcome 主要由 x-action effect 决定；
- Qy：主要由 y-direction 决定；
- Qmix：两者都重要；
- coarse vs fine candidate margins。

### Measurements

- on-policy prediction error；
- global counterfactual error；
- P94 global rho；
- query-specific candidate rank / regret；
- simple closed-loop plan success；
- projected/query-aware excitation候选统计量。

### decisive pattern

最有价值结果：

\[
\rho_{\rm tr}(X)=\rho_{\rm tr}(Y)
\]

且 global MSE 近似相同，但：

\[
Regret(X,Q_x)<Regret(Y,Q_x),
\]

\[
Regret(Y,Q_y)<Regret(X,Q_y).
\]

并且同一个 query-aware statistic 预先解释这组 swap。

这会把“action coverage”从 global property 推到 **decision-relative property**。

---

## Phase B — query/candidate resolution

P38 强调 candidate set / resolution 也改变所需 distinctions，因此在同一 query 上改变：
- coarse candidate set；
- fine near-tie candidate set；
- planner early/random candidates vs late/elite candidates。

问题：

> candidate margin 变小时，是否需要更强/更广的 decision-relevant excitation？

若同一个 statistic 同时解释 query 和 margin effect，story 明显增强。

---

## Phase C — compact visual latent WM

首选简单可控环境，而不是直接上复杂 robotics。

### Candidate 1: TwoRoom / 2D action
通过 behavior action-noise covariance orientation / route policy 控制不同 directions 的 conditional excitation。

Queries：
- 不同 door/goal geometry；
- 不同 candidate action banks；
- same visual encoder / same model size。

### Candidate 2: DMC PointMass / Reacher
选择真正依赖不同 action-effect directions 的 goal families。

模型：
- LeWM / JEPA-WM baseline；
- 若需要第二 family，再加入一个 structured/action-sensitive WM。

### 必须避免
如果 rotating action covariance 同时巨大改变 state occupancy：
- 做 short-horizon reset-based collection；
- matching/reweighting；
- 记录 occupancy overlap；
- 或先用 controlled-reset environment 隔离。

---

## Phase D — data intervention under fixed budget

如果 A–C 成立：

比较相同 transition budget：
1. random / isotropic；
2. global-excitation optimized；
3. query/candidate-relevant selection/reweighting；
4. optional task-informed exploration baseline。

读数：
- planning regret；
- success；
- counterfactual prediction in relevant vs irrelevant directions；
- unseen-query transfer。

### 关键测试

query-specific data optimization 会不会：
- 提升 seen query；
- 伤 unseen query？

这自然连接 **plannability vs reuse**。

---

## 统计

- synthetic：至少 20 random systems / B matrices，避免只挑一个 orientation；
- visual pilot：1 seed existence 后，3–5 train seeds；
- candidate-level bootstrap cluster by start/query；
- query family 作为 held-out unit，不把每个 candidate 当独立 n；
- exploratory statistic 与 confirmatory statistic 分开冻结。

---

## Gate

- **G0:** same global spectrum / comparable occupancy protocol 成立；
- **G1:** query×data-orientation interaction 稳定且方向可预测；
- **G2:** global MSE / global rho 不能解释；
- **G3:** simple decision-relevant statistic 解释 swap；
- **G4:** visual latent WM 复现；
- **G5:** fixed-budget data selection 能改善 decision；
- **G6:** second task/query family + held-out prediction。

只有 G1–G3：理论/controlled finding。  
到 G4–G6：才有强顶会 method/story 潜力。

## 结果

未运行。
