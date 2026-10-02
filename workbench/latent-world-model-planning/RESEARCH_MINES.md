# Research Mines — 在重要 research program 里长出自己的 paper

更新：2026-10-02。  
规则 authority：[NOVELTY_GROWTH_RULES](NOVELTY_GROWTH_RULES.md)。  
Program map：[RESEARCH_PROGRAMS](RESEARCH_PROGRAMS.md)。

> **这里不再寻找“完全空白的题”。**  
> 我们寻找的是：一个社区持续关心的母问题中，哪些关键认识仍未闭合；然后通过强 baseline + 受控实验 + 多条件铺开，发展新的 distinction / law / mechanism / method / narrative。

科学 claim = 0。下面都是 mining programs / seeds，不是预先宣布的论文结论。

---

# 0. 先修正旧工作台的错误倾向

旧版本虽然写了 problem-led，但实际上仍容易变成：

```text
找到一个 broad problem
→ 搜到很多近邻
→ 不断加“exact delta”
→ 问题越来越窄
→ 最后只剩没人研究的小残差
```

现在改为：

```text
重要 research program
→ 深读近邻，理解每个 atomic claim
→ 找 tension / boundary / interaction / missing regime
→ 多个 cheap seeds并行挖
→ 一个 seed被吸收 ≠ program关闭
→ 真实实验出现 load-bearing signal
→ narrative / method 从证据长出来
```

**近邻密集可以提高 program 优先级，因为它说明 community care；只会提高 baseline/positioning 的证据要求。**

---

# R1 — Data & Identifiability: 什么经验让 world model 真正可规划？

完整 program：[RESEARCH_PROGRAMS `R1](RESEARCH_PROGRAMS.md)。

## 已知的不同答案

- PLDM：data regime改变 method behavior；
- P94：conditional action excitation决定 controlled transition identifiability；
- QRL / IEL：behavior hitting-time统计不等于 optimal controllability；
- RC-aux / Temporal-Distance JEPA：trajectory supervision能注入 planning semantics；
- Do-JEPA / FIRM：same-reset counterfactual branches；
- Task-Sufficient WM：active probing收集 informative trajectories；
- WorldTest：单一路径经验不代表 environment-level knowledge。

**这些结果共同说明 R1 很重要，不说明 R1 被做完。**

## 当前活跃 seeds

### I09 / E14 — behavior-route imprint
问 trajectory-derived planning semantics 是否过度继承 behavior route / tempo。  
现在是一个**具体诊断 seed**，不是 R1 的唯一故事。

### I12 / E16 — equal-budget data value
固定 transition budget，比较：
- state coverage；
- action excitation；
- route diversity；
- counterfactual branches；
- 后续可加 active probing / failure-recovery data。

目标是挖出：
> 哪种 experience 在什么 environment/planning regime 下最有 planning value？

### I06 / E08–E10 — negative-role decomposition
只作为 R1 的一个局部机制：
semantic reachability label 与 global geometry regularization是否混用。

## 允许发展的新 narrative

- action excitation是必要但不充分；
- multi-route data比更多IID transitions更值钱；
- counterfactual branch data只在某类 contact/ambiguity regime有高边际价值；
- failure/recovery data比successful expert data更能校准 planner；
- active probing应针对 decision boundary，而不是 prediction error；
- general-purpose data collection 与 query-aware collection存在可预测 frontier。

这些都不能因为 P94 / PLDM / Task-Sufficient WM 做过一个点就桌面否定。

---

# R2 — Predictive Abstraction: world model 到底该预测什么？

完整 program：[RESEARCH_PROGRAMS `R2](RESEARCH_PROGRAMS.md)。

## 已有方法形成 continuum

```text
one-step explicit dynamics
      ↓
recursive / structured dynamics
      ↓
direct arbitrary-horizon future
      ↓
trajectory distribution / branches
      ↓
successor / occupancy prediction
      ↓
macro / hierarchical transition
      ↓
amortized planner / policy
      ↓
hybrid
```

LeWM、SALT、Branch/Flow、Universal Horizon、Bagatella TD-JEPA、Jumpy WM、HWM、LeFlow、TD-MPC2 等只是这条 continuum 上不同设计点。

## 当前 seed

### I08 / E13
先用 common task/data/utility 对 continuum 两端做小 matched pilot，同时分开：
1. training compute；
2. task/query information；
3. deployment compute。

**E13不是“explicit vs implicit论文”。**  
它的任务是找到下一步应该在哪个 axis 挖：
- horizon？
- query变化？
- arbitrary action flexibility？
- data support？
- stochasticity？
- deployment budget？

如果出现 boundary，再加入一个中间 predictive object验证。

## 可长 narrative

- predictive object随 horizon / query flexibility发生 phase switch；
- direct horizon比recursive rollout更适合某种 long-range regime，但失去 counterfactual compositionality；
- successor/occupancy高效但在 unseen reward/query 下出现可预测 failure；
- hybrid model应按 horizon / uncertainty动态选择 predictive object；
- model structure与 planner search depth之间有可计算的 matching law。

---

# R3 — Specialization vs Reuse: world model 应该多 task-specific？

完整 program：[RESEARCH_PROGRAMS `R3](RESEARCH_PROGRAMS.md)。

## 为什么这是 program，不是被 P38 “占了”

P38 *What Must a WM Distinguish?* 已经证明：
- query/candidate/planner决定 information requirement；
- query-conditioned joint model在seen objective强；
- unseen objective上优势缩水；
- modular query-guided proposal + query-independent prediction是一个好设计。

这是一个**强起点**。

但仍有大量研究对象：
- query进 encoder / dynamics / metric / proposal / verifier 的差异；
- query dimensionality；
- finite capacity；
- multi-query training；
- planner change；
- candidate distribution change；
- task-specific data acquisition；
- transfer to new goal language / reward / physical query。

## 当前 seed

### I10 / E17 — query placement × reuse
同一 compact visual WM stack 下，控制 query注入层，画 seen-query efficiency ↔ unseen-query reuse frontier。

不是为了证明“conditioning hurts generalization”；是为了找到：
> **什么信息应该 task-specific，什么 predictive structure应该保持 reusable？**

## 可长 narrative

- selective conditioning；
- modular representation/dynamics split；
- query-dependent capacity allocation；
- universal predictor + specialized proposal；
- multi-query training principle；
- specialization degree随 query family complexity变化。

---

# R4 — State / Belief / Information Gathering: 什么才是正确的 predictive state？

完整 program：[RESEARCH_PROGRAMS `R4](RESEARCH_PROGRAMS.md)。

FIRM、UWM-JEPA、Branch-JEPA、Physically Viable WM、Flow Equivariant WM等都在这个 program 内。

**不再写“近邻太多所以只剩一个很窄 residual”。**

它们告诉我们：
- hidden physics是真问题；
- memory/belief是真问题；
- multiple futures是真问题；
- query-conditioned physical abstraction是真问题。

接下来可以问：
- memory何时够？
- uncertainty何时必须显式保留？
- planner怎么消费belief？
- 什么时候需要主动 sensing / probing？
- goal-comparable state和dynamic belief如何分工？
- hidden physics能否在线识别？

## 当前 seed

I07 / E11 仍是最便宜入口：
> observation/history ambiguity 是否真的改变 action choice？

若 E11这个具体 seed没有现象，**只 park I07，不关闭 R4**。  
下一步可以转 active disambiguation / risk-aware planning / hidden-physics identification。

---

# R5 — Trust / Repair / Bypass: world model 什么时候值得信？

完整 program：[RESEARCH_PROGRAMS `R5](RESEARCH_PROGRAMS.md)。

现有方法：
- uncertainty penalty；
- hallucination detector；
- intuition hybrid；
- feedback correction；
- test-time adaptation；
- adaptive replanning；
- subgoal / horizon shortening。

这些是不同 **recovery actions**。

真正未统一的是：
> 检测到不同 failure pressure 后，应该采取哪一种 recovery action？

## 当前 seed

### I11 / E18
不先训练 router。  
对同一 planning state，用 environment reset 得到不同 recovery action 的真实 utility lift，再看已有 signal能不能预测 intervention ranking。

如果存在：
```text
failure type / signal
      ↓
best recovery action
```
的稳定 mapping，才值得方法化。

## 可长 narrative

- world-model trust policy；
- adaptive planning compute；
- horizon/replan/adapt router；
- failure-type-specific recovery；
- detect→repair而不是detect-only。

---

# Cross-cutting — Planner/Query/Decision consequence

所有 R1–R5 都共享：

### Planner contract
记录：
- candidate source；
- planner stage；
- H/K；
- search budget；
- query；
- metric；
- candidate margin。

### Actionability gate
内部变化最终问：
- candidate ordering变了吗？
- candidate availability变了吗？
- selected action变了吗？
- real regret/success变了吗？

但这不是说 internal phenomenon 没价值；它可以是**发现 mechanism 的中间证据**。只是不能让一个完全没有决策后果的小 probe独自承担整个 paper。

---

# 当前 6 个活跃 seeds

| seed | program | 角色 |
|---|---|---|
| I09 / E14 | R1 | behavior-route / trajectory-semantics probe |
| I12 / E16 | R1 | equal-budget data-value probe |
| I08 / E13 | R2 | predictive-object frontier probe |
| I10 / E17 | R3 | specialization↔reuse probe |
| I07 / E11 | R4 | state/belief actionable ambiguity probe |
| I11 / E18 | R5 | trust/recovery-routing probe |

I06 / E08–E10 和 I03 / E06–E07 是共享/局部 diagnostics。

这符合 workbench 的“3–6个活跃 seed”规则；**同时实际跑的 pilot仍不超过2个**。

---

# 首轮执行组合

不要一次跑 6 条大实验。

## Wave A — 最便宜、最高 information gain

1. **E14**：TwoRoom route-data intervention；验证 R1 trajectory semantics 是否有实质 pressure。
2. **E18**：优先 released checkpoint / evaluation-only trust-recovery oracle；验证 R5 是否存在不同 recovery action winner。

dataset/sampler ready 时，E08可CPU并行。

## Wave B — common substrate ready 后

3. **E13**：R2 predictive-object matched pilot。
4. **E17**：R3 query-placement小矩阵。

## Wave C — 按资产触发

5. **E11**：R4 cheap aliasing/action oracle。
6. **E16**：若 R1 仍最强，扩到 equal-budget data value，而不是只把 E14 route effect做得越来越窄。

---

# Seed stop ≠ Program stop

例：

- E14最后被 P94 excitation完全解释  
  → **I09 park**；  
  → R1 转向 E16 active/counterfactual data value。

- E13没出现 explicit/implicit切换  
  → I08当前设置 park；  
  → R2 可以转 stochasticity / query flexibility / direct-horizon vs recursive。

- E17结果完全复制P38  
  → I10当前 seed park；  
  → R3仍可转 capacity / multi-query / query-aware data。

- E11短history全部解决  
  → I07 park；  
  → R4仍可研究 hidden parameter active identification。

- E18一个方法总是最好  
  → I11 park；  
  → R5可能收敛到该 recovery mechanism 的 failure boundary。

**绝对禁止把上面写成“整个方向被杀”。**

---

# 什么样的 paper narrative 最值得追

我们不预注册最终 narrative，但优先以下形态：

1. **一个重要 program 的新 principle**；
2. **两个已有答案之间的 regime boundary**；
3. **新 distinction + minimal method**；
4. **data / compute / query allocation law**；
5. **统一多个已有 method 的 common mechanism**；
6. **强 comparative science 导出新的 design rule**。

这才是多卡大面积实验最终要服务的东西。
