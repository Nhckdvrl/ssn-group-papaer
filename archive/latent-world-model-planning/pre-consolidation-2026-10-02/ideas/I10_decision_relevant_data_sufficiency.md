# I10 — Decision-Relevant Data Sufficiency / Query-Conditioned Excitation

- **状态：** SEED / M3 broad-growth candidate
- **母问题：**

> **为了支持某一类 planning queries / candidate decisions，world model 的训练数据到底需要激发哪些 action-effect directions？**

P94 告诉我们：要识别完整 controlled transition，behavior policy 需要足够 conditional action excitation。  
P38 告诉我们：planner 并不总需要完整 mechanism；需要保留什么取决于 query、candidate set 和 planner。

I10 研究两者之间的桥，而不是回避两者。

---

## 1. 核心 tension

### Data-side：P94

对完整 controlled transition，P94 用 conditional action covariance

\[
\Sigma_{\rm tr}(\pi)=\mathbb E_s[\operatorname{Cov}_\pi(a\mid s)]
\]

以及最弱方向

\[
\rho_{\rm tr}(\pi)=\lambda_{\min}(\Sigma_{\rm tr})
\]

刻画 transition identifiability。

当某些 action direction excitation 弱时：
- on-policy error 可以很小；
- counterfactual error 可以被放大；
- goal-conditioned planning 会坏。

### Decision-side：P38 / value-equivalence lineage

但一个 planner 不一定需要把所有 action-effect directions 都识别清楚：
- query 决定哪些 physical variations 相关；
- candidate set 决定需要多精细的 response differences；
- coarse decision 可能只需很小的 decision-relevant subspace；
- value-equivalence / VAML / PAML 早就说明完整 model 不是唯一目标。

因此：

> **global transition identifiability 可能是比某个具体 decision 所需更强的条件。**

---

## 2. 最干净的 first hypothesis family

不要一开始声称新 theorem。先做一个可证伪的 controlled phenomenon：

> 两个 behavior datasets 具有相同的 global action-excitation spectrum / 相同 global rho，但 excitation 主轴相对 planning query / candidate differences 的方向不同。  
> 如果 decision 真正只依赖其中某些 action-effect directions，那么两份数据会对不同 queries 产生**互换的 planning reliability**，而 global rho / average prediction MSE 解释不了这种交换。

### 2D intuition

设两个 dataset 的 conditional action covariance 拥有相同 eigenvalues，只旋转 eigenvectors。

- Dataset X：high-excitation axis 更接近 x；
- Dataset Y：high-excitation axis 更接近 y；
- 两者 trace / determinant / minimum eigenvalue 相同。

构造：
- Qx：candidate outcome 主要依赖 x-action effect；
- Qy：主要依赖 y-action effect。

预测：

\[
X: Q_x \gg Q_y,\qquad
Y: Q_y \gg Q_x.
\]

如果成立，就说明 “how much action coverage” 不够，**coverage orientation relative to decision matters**。

---

## 3. 候选构念：Decision-Relevant Excitation

暂不冻结公式。要求必须能从 planner/query/candidate set 推出，而不是事后拟合一个相关量。

可能从 candidate-difference subspace 出发：

\[
\Delta \mathcal A_C = \operatorname{span}\{a_i-a_j\}.
\]

在局部线性近似

\[
z' = Az + Ba
\]

下，若 query cost 对 state 的梯度为 \(g_q\)，action 对 query response 的一阶 sensitivity 是

\[
B^\top g_q.
\]

因此 data sufficiency 可以看 decision-relevant subspace 上的 projected excitation，而不是所有 action directions 的 global minimum eigenvalue。

候选 oracle statistic：

\[
\rho_{\rm dec}(q,C,\pi)
=
\lambda_{\min}
\left(
P_{q,C}^\top \Sigma_{\rm tr}(\pi)P_{q,C}
\right).
\]

其中 \(P_{q,C}\) 是 decision-relevant basis。

**这只是 seed。E16 若不支持，不保公式。**

---

## 4. Related work 是四条生长线，不是四堵墙

### P94 Controlled-WM Identifiability
给 full transition identification 的 data-side condition。  
I10 问：**specific decision 是否只需要 projected condition？**

### P38 What Must a WM Distinguish?
给 query/candidate/planner-dependent sufficiency。  
I10 问：这种 sufficiency 如何反过来约束 **training data requirement**？

### Value Equivalence / VAML / PAML / TOM
已经提出：
- 只需对 value/policy/planner 重要的 model accuracy；
- policy-relevant experience 应被重点建模。

I10 不能 claim “decision-aware modeling is new”。  
它要把这个原则接到 **behavior-policy excitation / latent visual WM / planner candidate regret**。

### MIST-WM / task-informed active system identification
已经做：
- task-relevant latent factor probing；
- physical-property-sensitive exploration。

I10 不能 claim “task-informed exploration is new”。  
它要研究：

> **planner query/candidate family 具体需要哪些 action-effect directions 被 offline data 识别？**

---

## 5. 为什么这可能比 I09 更大

I09 是一个具体 failure：
> trajectory-derived semantic labels 可能继承 behavior route geometry。

I10 问的是更广泛的数据问题：
> **什么时候一份数据对一个 decision 是“够的”？**

它可以统一：
- P94 action excitation；
- P38 decision sufficiency；
- MIST informative probing；
- FACT failure-consequence data；
- PLDM data regimes。

如果 E16 出现强 law，I10 可以成为 M3 的主 paper，I09 成为 supporting example。

---

## 6. 论文级最低证据链

1. **Controlled phenomenon**  
   same global excitation spectrum / similar global MSE，但 query-specific decision reliability 互换。
2. **New predictor / law**  
   decision-relevant excitation 比 global rho、state/action coverage、MSE 更能预测 candidate regret。
3. **Visual latent WM**  
   不只 linear synthetic；至少一个 pixels→latent planning substrate。
4. **Cross-query / candidate generality**  
   不只一个 goal。
5. **Data intervention**  
   固定 data budget，补足 decision-relevant directions 能改善 planning。
6. **Nearest baselines**  
   random/exploratory data、global-excitation-maximizing data、task-informed/uncertainty baseline 中的可实现代表。
7. **Closed-loop consequence**  
   candidate rank/regret + task success。

---

## 7. 可能自然长出的 method

如果 law 成立，最小方法可能是：
- offline trajectory selection / reweighting；
- active data collection 时优先 excite planner-relevant directions；
- reusable generic dataset + small query-specific补充数据；
- candidate-aware replay buffer；
- multi-query coverage allocation。

不预先设计复杂 world-model architecture。

---

## 8. Stop / redirect

- global rho 已足以解释所有 query regret → I10 不成立；
- query dependence 只在 toy，visual substrate 消失 → 降级；
- decision-relevant statistic 只能用 test-time privileged ground truth 计算 → 只作 oracle，继续找 train-time proxy；
- MIST/task-informed baseline 完全解决且没有新的 planner-specific distinction → 收敛为 related-work confirmation；
- 不同 query 需要完全不同数据且没有低维规律 → 转向 **data specialization vs reuse**，而不是硬拟合一个 scalar。

- **对应实验：** [E16](../experiments/E16_decision_relevant_excitation.md)
