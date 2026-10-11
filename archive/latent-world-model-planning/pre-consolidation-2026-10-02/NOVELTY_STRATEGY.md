# Novelty Strategy — overlap is allowed; ownership must be real

更新：2026-10-02。

> **这个 workbench 不追求“完全没人做过”。**  
> AI 研究里真正重要的是：母问题本身有价值、已有工作证明社区关心、related work 之间仍有 tension / missing regime / unexplained failure，而我们的实验能长出一个**可拥有的新认识**。

## 1. 什么不算撞车

下面这些情况**不能因为“有人做过”就 kill**：

- 同一个母问题下，别人只覆盖了一种 regime；
- 同一 broad claim 下，决定性变量不同；
- 别人提出了一个 method，但没有解释何时有效/失效；
- 两篇论文给出不同答案，但 protocol / data / task 不同；
- 同一 failure 在另一领域出现过，但没有在 latent-WM planning 的 decision chain 中被识别；
- 别人做了 representation / value / policy 层，我们研究 planner-consumed semantics；
- 别人给出 theorem，我们可以研究 realistic regime 中哪一项真的 load-bearing；
- 别人做了一个修复，我们可以发现它为什么有效、什么时候不该用、或者它实际上修的是另一件事。

**related work 的存在通常是好事：它证明 mother question 有价值，并给我们 baseline / intervention / reviewer vocabulary。**

## 2. 真正的 novelty ownership 有哪些形态

### A. New problem distinction
把一个 broad complaint拆成两个此前混在一起、但会导致不同方法选择的问题。

例子：
- information exists ≠ planner metric can consume it；
- behavior statistics ≠ environment controllability；
- task/query information budget ≠ deployment compute。

### B. New regime law
不是“方法A比B好”，而是：

> 当变量 X / Y 进入某个 regime 时，bottleneck 或 method ranking 系统改变。

这类工作允许所有 components 都已有先例，只要 **regime law 是新的、可预测、跨任务成立**。

### C. New causal identification
某个大家都观察到的现象有多个解释；我们用 intervention / oracle 把它们拆开。

例：
- data coverage vs conditional action excitation vs higher-order trajectory semantics；
- representation failure vs dynamics failure vs search failure。

### D. Reattribution
已有 method 真的有效，但主流解释不完整/不对；我们证明 load-bearing mechanism 是另一项，并导出更简单或更通用的设计。

### E. Method from diagnosis
方法本身可以非常小，只要：
1. 问题是真实且重要；
2. 诊断指出一个明确 bottleneck；
3. 方法是自然后果；
4. 强 baseline + scope 证明不是 trick。

### F. Strong comparative science
PLDM / JEPA-WMs 这类工作说明：
**系统比较本身也能顶会**，前提是比较导出 field-level conclusion，而不是 leaderboard。

## 3. 什么才是真正该 kill 的

不是“有 related work”，而是：

- exact claim + exact regime + exact intervention + exact consequence 都已有直接工作；
- 新实验只是在换 benchmark / encoder / loss coefficient；
- 即使现象成立，也不会改变模型设计、方法选择或领域理解；
- 只能靠刻意构造一个非常窄 toy 才出现；
- downstream decision / closed-loop 完全不受影响；
- 所谓 novelty 只剩命名差异；
- 强 baseline/最简单解释一上来就完全吸收。

## 4. 对 M3 的纠偏：不要压成一个极窄残差

M3 的母问题应该保持足够大：

> **What planning semantics can be identified from offline trajectories, and which parts are inherited from the behavior that generated them?**

P94 证明 conditional action excitation 影响 controlled-transition identifiability；QRL/CGCIVL证明 behavior statistics与 optimal controllability有区别；RC-aux/Temporal-Distance JEPA把 trajectory order/gap/negative直接写进 planning supervision。

这些不是把 M3 “做没了”，而是给 M3 三个坐标轴：

1. **local action-effect identification** — action excitation / transition support；
2. **long-horizon behavioral statistics** — route frequency / temporal gap / occupancy / policy family；
3. **planner semantics** — reachability / progress / candidate ranking / closed-loop choice。

我们真正要实验性发现的是：**这三层之间怎么耦合，哪些 published objectives在什么 regime 学到 environment structure，什么 regime学到 behavior imprint。**

即使最后发现 P94 的 action excitation解释了 70%，而 route semantics只解释 30%，也不等于失败；如果这种 decomposition 是新且可预测的，它本身可能就是论文。

## 5. 对 M2 的纠偏：不要把它做成“公平比较工程”

M2 的大问题保持：

> **Where should predictive structure live, and how much of the future should be made explicit?**

现有方法形成一条连续谱：

- one-step explicit dynamics；
- direct k-step / arbitrary-horizon predictor；
- stochastic / branching future；
- policy-conditioned successor / occupancy；
- learned proposal / amortized planner；
- hybrid policy + short rollout。

“有人做过每一种”并不意味着没空间。相反，**正因为每一种都有人做，而没有统一原则说明什么时候该选哪一种，才有 M2。**

E13 的 compute / task-information accounting 是为了让比较可信，不是把 M2缩成 accounting paper。

真正目标：
- 找到少数 regime variables；
- 解释为什么 predictive abstraction的最优位置会移动；
- 最好导出 adaptive / hybrid rule。

## 6. 对 M1 的纠偏

POMDP、belief、hidden physics都有人做，不代表 M1必死。

但 M1 当前 collision 确实比 M2/M3高，所以先 cheap pilot。

如果实验发现一个非常自然、普遍、且现有 FIRM/UWM/Branch-JEPA 都没解决的 action-level failure，**允许重新升主线**；不要因为 related work多就拒绝看结果。

## 7. 本地 agent 的 novelty gate

每个 promising result 都写一张“ownership test”：

```text
Mother problem:
Closest 3–5 works:
What they actually establish:
Our observation:
Same or different regime?
Same or different causal variable?
Same or different downstream consequence?
What would a reviewer compress us to?
What experiment would prove we are not that?
If method follows, why is it the minimal consequence?
```

只有这个表无法形成 substantive delta 时才降级。

## 8. 最终标准

目标不是找到“空白”。

目标是：

> **在一个社区已经证明重要的母问题中，通过大量高质量实验发现一个新的、可被清楚命名和验证的规律 / 区分 / 机制 / 方法，并让 related work 成为我们叙事的生长路径，而不是障碍。**
