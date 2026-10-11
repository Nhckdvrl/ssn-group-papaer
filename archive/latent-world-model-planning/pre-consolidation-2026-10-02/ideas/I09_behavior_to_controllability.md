# I09 — Local dynamics identifiable, global planning semantics still behavior-dependent?

- **状态：** SEED / **Tier A1 primary problem mine**
- **一句话母问题：**

> 当 action-conditioned world model 的 **local transition 已经可识别**、conditional action excitation 也充分时，为什么 trajectory-derived planning supervision 仍可能学到 **behavior-policy hitting time / route geometry**，而不是 environment 的 optimal controllability？

这比“data distribution matters”更强，也比“behavior path ≠ shortest path”更具体。

---

## 1. 新 distinction：local transition identifiability ≠ global controllability identifiability

### 已有工作解决了 local identification

**P94 — On the Identifiability of Controlled World Models** 已经把 local controlled prediction 问得很清楚：

- representation identifiability受 predictable-signal spectral margin控制；
- controlled transition identifiability受 conditional action excitation
  \[
  \rho_{\mathrm{tr}}(\pi)
  =
  \lambda_{\min}
  \left(
  \mathbb E_s[\operatorname{Cov}(a\mid s)]
  \right)
  \]
  控制；
- \(\rho_{\mathrm{tr}}\) 小时，可以 on-policy prediction 很好但 counterfactual action response 很差；
- 这种差异会直接伤 fixed-candidate goal-conditioned planning。

所以：

> **只要 E14 的 DIRECT / DETOUR 数据 action excitation 不一样，任何 planning 差异都有一个更简单、已经被 P94 理论化的解释。**

I09 必须把它排掉。

### 但 trajectory-derived planner semantics还有另一个 identification problem

RC-aux / Temporal-Distance JEPA 并不只学 \(p(s'|s,a)\)。  
它们进一步从 trajectory order / gap / episode identity构造 planner-facing semantics：

- RC-aux：
  - observed pair gap \(\Delta\)；
  - \(h\ge \Delta\) → reachable positive；
  - \(h<\Delta\) → temporal hard negative；
  - cross-batch goals → negative。
- Temporal-Distance JEPA：
  - same-trajectory step gap → directed temporal distance target；
  - cross-trajectory goals → far/negative heuristic。

这里 supervision 的统计对象不是 one-step transition，而是 **behavior trajectory**。

---

## 2. 一个关键 one-sided fact

设环境真正 shortest hitting time 为

\[
d^\*(s,g)
\]

行为轨迹中观察到从 \(s\) 到 \(g\) 花了

\[
\Delta_\pi(s,g)
\]

步。

只要轨迹真实可执行，就一定有：

\[
d^\*(s,g) \le \Delta_\pi(s,g)
\]

因此 observation 给的是 **upper bound**，不是 exact shortest distance。

这意味着：

### 安全语义

如果

\[
h \ge \Delta_\pi(s,g)
\]

那么至少有一条已观察路径在 \(h\) 步内到达，故：

\[
d^\*(s,g)\le h
\]

positive reachability 是 certified 的。

### 不安全语义

如果

\[
h < \Delta_\pi(s,g)
\]

不能推出

\[
d^\*(s,g)>h
\]

因为 behavior 可能走了 detour。

所以 RC-aux-style temporal hard negative 在 suboptimal / looping behavior下，语义上可能只是：

> “**这条观测路径没在 h 步内到**”

而不是：

> “**环境里不存在 h 步内路径**”。

Temporal-Distance JEPA 把 \(\Delta_\pi\) 当 directed progress target 同样可能学 behavior path length，而不是 \(d^\*\)。

这是 I09 最核心的 identification gap。

---

## 3. 为什么这不是 quasimetric GCRL 的简单重复

已有：
- Offline GCRL with Quasimetric Representations；
- Multistep Quasimetric；
- CGCIVL；
- PLDM；
- TempDATA；

已经告诉我们：

> Monte-Carlo / behavior-future statistics 与 optimal goal distance并不天然相同。

所以不能把上面的不等式本身当贡献。

### I09 必须多走三步

1. **Modern visual latent-WM objective consequence**
   - RC-aux / Temporal-Distance JEPA 这种 supervision 直接改 encoder / planning head / deployed MPC cost。
2. **Local dynamics-identifiability control**
   - 控制 P94 的 action excitation / local transition support 后，仍观察 higher-order behavior-route imprint。
3. **Decision consequence**
   - same fixed candidate pool ranking / regret；
   - selected action；
   - closed-loop success。

如果只做“temporal label 与 shortest path相关性”，不够。

---

## 4. 最强 possible story

若实验支持，最强 narrative 不是：

> “RC-aux labels有noise。”

而是：

> **Local transition identifiability does not imply global planning-semantic identifiability.**
>
> A visual latent world model can identify how actions move the state locally, yet trajectory-derived planning objectives can still inherit behavior-policy hitting-time geometry. This makes two models trained in the same environment disagree on reachability/progress solely because the data-generating policy took different routes. We identify the one-sided semantics of observed trajectory gaps, show the resulting bias changes candidate ranking and closed-loop planning, and derive a policy-invariant / censor-aware alternative.

这是一个 field-level distinction：

\[
\boxed{
\text{identify } f(s,a)
\;\not\Rightarrow\;
\text{identify } d^\*(s,g)
}
\]

尤其当 \(d^\*\) 是通过 behavior trajectory labels直接学，而不是由 local transition model + planning推出来时。

---

## 5. 最强 identification 设计：transition-equivalent, trajectory-different

P94 迫使我们控制 local action excitation；P95/IEL 又说明 hitting-time regression本身已有 trajectory-label mismatch项。要让 I09 真正站住，最有力的受控实验不是简单“expert vs random”，而是尽可能构造：

[
D_A approx D_B quad 	ext{in one-step transition evidence}
]

但：

[
D_A 
eq D_B quad 	ext{in higher-order trajectory co-occurrence / observed gaps}
]

也就是：

> **同样的局部 dynamics 证据，不同的 trajectory organization。**

旧 I01/E03失败，是因为 treatment连 short-window objective都看不到；新的 E14-B2 则相反：
- one-step transition bag近似保持；
- **short-window temporal pair/gap distribution必须改变**；
- 所以 trajectory-semantic objective能看到 treatment，而 pure local predictor理论上应更 invariant。

如果这个 control 成立，并出现：

[
	ext{LeWM stable}
]

但：

[
	ext{TD-JEPA / RC-aux planner semantics drift}
]

故事会比普通 data-ablation强很多。

这仍需自然 behavior-policy结果作外部有效性；不能只靠人工重排数据写paper。

---

## 6. E14 应该检验什么

### Treatment

同 environment、同 start-goal family：

- DIRECT behavior；
- DETOUR / LOOP behavior；
- MIXED routes。

### 必须匹配 / audit

- state occupancy；
- action marginal；
- **conditional action covariance / \(\rho_{\rm tr}\) proxy**；
- local one-step transition support；
- transition count；
- start-goal distribution。

### 关键目标

尽量做到：

\[
\text{local dynamics evidence}
\approx
\text{same}
\]

但：

\[
\Delta_{\pi_1}(s,g)
\neq
\Delta_{\pi_2}(s,g)
\]

然后看：

\[
C_{\pi_1}(s,g)
\neq
C_{\pi_2}(s,g)
\]

是否进一步导致：

\[
\text{candidate ranking / selected action}
\]

变化。

### Positive control

Temporal-Distance JEPA / RC-aux 对 route-length treatment应比 plain LeWM 更敏感。

### Negative control

如果 plain LeWM 同样出现等量 drift，先解释 local support / representation shift，不升级。

---

## 7. 如果现象成立，方法如何自然长

不预注册某一个答案，但方法空间已经能按 semantics 排序：

### A. One-sided / censored reachability supervision
observed route只提供：

\[
d^\*(s,g)\le \Delta
\]

所以：
- observed feasible path → certified positive；
- insufficient observed speed → unknown，而非自动 negative；
- negative需要真正 lower bound / certified impossibility。

### B. Multi-route aggregation
多个 behavior routes：
- min observed gap 作为更紧 upper bound；
- distribution / interval而不是单条路径 exact target。

### C. Local Bellman / quasimetric consistency
用 local transitions约束最短控制结构，而不是把 Monte-Carlo path length直接当 truth。

### D. Separate semantics from geometry regularization
如果 heuristic negatives的收益主要来自 representation repulsion，复用 I06：
- semantic channel只承担有依据的 reachability；
- geometry/uniformity另做 regularization。

**注意：** A–D 都有邻近思想，真正方法贡献必须由 E14 的机制结果来决定，不提前认领。

---

## 8. Reviewer compression tests

### “这不就是 P94 action coverage？”
只有当我们没控制 conditional action excitation 时，是。  
I09 的 exact delta是 **P94 local identifiability 已满足以后** 的 higher-order temporal-semantics dependence。

### “这不就是 quasimetric RL / IEL？”
Broad behavior-vs-optimal distance确实是；P95 IEL甚至显式回归 trajectory hitting-time labels、使用 low hitting-time expectile，并在理论里包含 trajectory-label mismatch。  
所以 I09 不能以“学 directed hitting time”或“加 quasimetric/triangle consistency”作为默认贡献。它需要证明一个更具体的 **visual latent-WM failure**：在 local dynamics evidence / action excitation近似相同的情况下，planning-aligned trajectory auxiliaries仍产生 behavior-dependent MPC semantics。若 correction最终只是 IEL/QRL移植，则不够。

### “suboptimal demonstration当然路径更长。”
当然。  
贡献不是这个常识，而是：
- published planning-aware objectives是否把这个常识错误地硬编码成 global semantics；
- 这种错误在什么 regime 真正改变 decision；
- 如何在不使用 test oracle的情况下保留 planning收益又移除 policy dependence。

### “只是换数据分布。”
E14如果无法匹配 local support / action excitation，就接受这个 criticism并停。

---

## 9. 升级条件

I09 从 SEED → paper hypothesis 至少需要：

1. DIRECT / DETOUR 的 \(\rho_{\rm tr}\) proxy 与 local support近似匹配；
2. one-step / counterfactual local dynamics fidelity差异不足以解释结果；
3. trajectory-derived score / reachability明显随 behavior route变化；
4. same fixed candidate pool rank/regret被改变；
5. closed-loop有 consequence；
6. LeWM control弱于 trajectory-semantic methods；
7. 第二 objective family或第二 task structure复现。

只满足 3 不满足 4–5：不升级。

---

## 10. 对应资产

- E14：主 identification pilot；
- E15：只有 E14 支持后才设计 policy-invariant/censor-aware correction；
- E08/E09：cross-negative role子机制；
- P94：conditional action-excitation control；
- QRL / multistep quasimetric / CGCIVL：conceptual nearest neighbors；
- LeWM：local predictive baseline/control。
