# Novelty Growth Rules — 有近邻 ≠ 没空间（2026-10-02）

> 本文件是 latent-world-model-planning 的**硬规则**。  
> 目的：防止研究流程把“相关工作多”误当“方向不能做”，最后只剩没人关心的小残差或零方向。

## 1. 四个层次必须分开

### L-Territory — 领域
例如：
- latent world models for planning
- world models under partial observability
- data for action-conditioned world models

**论文不可能“拥有”整个 territory。**

### L-Program — 持续研究计划
例如：
- 什么数据让 world model 真正可用于 counterfactual planning？
- predictive structure 应该显式 rollout、直接多步预测、successor/occupancy abstraction，还是 hybrid？
- world model 应该多 task-specific，才能兼顾决策效率和跨 query reuse？

一个 program 里连续出现很多 ICML/ICLR/NeurIPS 论文，通常说明**问题重要且仍在生长**，不是自动负面信号。

### L-Atomic claim — 原子主张
例如：
- “trajectory curvature regularization 能改善 Euclidean latent planning”
- “conditional action excitation 控制 transition identifiability”
- “budget-conditioned reachability auxiliary 改善 finite-horizon planning”

**只有这一层可以被直接近邻实质占有。**

### L-Implementation — 具体实现
例如一个 head、一项 loss、某个 sampler。

Implementation 撞车甚至不一定杀 atomic claim；可能还有更简单/更强/不同假设的实现。

---

## 2. related work 的正确用法

每篇强近邻都回答五件事：

1. **它证明什么问题值得做？**
2. **它接受了什么旧前提？**
3. **它打破了哪个前提 / 暴露了哪个 pressure？**
4. **它具体拥有哪个 atomic claim？**
5. **它的新结果让下一层问题变成什么？**

禁止只写：
> “某某 paper 做过 X，所以 X 不能做。”

应该写：
> “P 做了 X，在假设 A/B、setting S、planner Q 下得到 Y；因此 X 的 existence claim 已占，但 program 中还留下条件边界、交互、泛化、统一解释、不同 supervision / data / planner 下的行为，以及由这些新认识导出的 method。”

---

## 3. novelty 不等于“没人做过”

顶会 novelty 可以来自：

- **new problem formulation**：把旧的 broad complaint压成真正 load-bearing 的对象；
- **new distinction**：过去混在一起的两种 failure / supervision / information role被拆开；
- **regime law**：已有方法 A/B 都有效，但我们找出什么时候哪一个有效；
- **interaction**：两个已知因素相互作用产生新的失败/能力；
- **mechanism / identification**：已有现象背后真正承重变量；
- **unification**：多条 seemingly different methods其实在修同一基本对象；
- **counterexample / boundary**：已有 claim 在自然 regime失效或需要额外条件；
- **method**：由诊断自然导出的新训练目标/architecture/planner/data policy；
- **data principle**：哪类经验真正识别 decision-relevant dynamics；
- **compute principle**：训练、task inference、test-time planning compute 应放在哪里；
- **transfer / reuse law**：task-specific alignment 与 unseen query/generalization 的边界；
- **strong comparative science**：controlled experiments推翻一个领域默认设计假设；
- **benchmark / protocol**：如果它揭示此前系统性看不见的真实能力缺口。

这些都不要求 territory 空白。

---

## 4. “拥挤”只改变证据负担，不自动改变研究价值

### 高度活跃 program
例如 representation geometry / decision-aligned WMs。

含义：
- reviewer baseline更强；
- claim必须精确；
- 需要更强实验/理论；
- **同时也说明社区很关心。**

### 低论文密度角落
不自动加分。可能只是：
- 问题不重要；
- benchmark太人为；
- effect太小；
- 没人愿意投入。

**不能用“空白度”代替“科学价值”。**

---

## 5. 直接 collision 的认定标准

只有同时满足大部分条件，才能说“atomic claim 已基本撞车”：

- 同 mother question；
- 同 setting / information access；
- 同 causal treatment 或核心 independent variable；
- 同 downstream consequence；
- 同方法原理或理论对象；
- 同主要证据链；
- 我们目前没有更强 boundary / interaction / mechanism / generalization / method delta。

即便 atomic claim 撞车：
- **保留 parent program**；
- 把近邻变成 baseline；
- 继续问“它的结果在什么条件下成立、为什么、如何组合、如何泛化”。

---

## 6. Abstract-only 不能杀方向

对于会改变当前选题的直接近邻：

- 摘要 / 搜索 snippet = **NAVIGATION ONLY**；
- 至少读 main method + experiments + related work + limitations；
- 如果 paper 会被当作“这个方向没空间”的理由，必须再读：
  - setting / input information；
  - strongest baselines；
  - decisive ablations；
  - negative/null results；
  - appendix中会改变结论的 protocol details。

没有做到这些，只能登记 pressure，不能关闭 program。

---

## 7. Reviewer compression 应该怎么用

“你这不就是 X 吗？”是**写作/定位压力测试**，不是桌面 kill switch。

正确流程：

\`\`\`text
近邻 X
  ↓
我们现在与 X 很像
  ↓
先问：能否通过实验找到新的 condition / mechanism / interaction / boundary？
  ├─ 能 → 继续 program
  └─ 暂时不能 → park 当前 seed，不关闭 parent program
\`\`\`

禁止：

\`\`\`text
搜到 X
  ↓
标题相似
  ↓
整个方向禁止
\`\`\`

---

## 8. Workbench 中 seed 被否定后怎么办

一个 seed 可以因为以下原因 park/refute：
- phenomenon不存在；
- stronger baseline吸收；
- treatment无效；
- effect只停在probe；
- exact atomic claim已有更完整工作。

然后必须回到它的 **research program**：

1. 更新“这个 seed 教会了我们什么”；
2. 重新读 direct neighbors；
3. 对 program 做 2–3 个研究动作：
   - boundary
   - interaction
   - reattribution
   - active intervention
   - successful-case dissection
   - data/compute scaling
4. 生成新的 seed。

只有 program 经过强 baseline + 系统 measurement + 多个 seed 后，人类 scientific-yield review 才能暂停。

---

## 9. 对本 workbench 的具体约束

### 不允许这样写
- “FIRM 做过 belief，因此 POMDP 不做。”
- “P94 做过 behavior policy，因此 data semantics 不做。”
- “PLDM 做过 model-based vs model-free，因此 predictive abstraction 不做。”
- “P38 做过 query sufficiency，因此 specialization/reuse 不做。”
- “AdaJEPA 做过 adaptation，因此 trust/recovery 不做。”

### 应该这样用
- FIRM / UWM / PVWM → **state/belief program 的强坐标与 baseline**；
- P94 / QRL / CGCIVL / MIST-like active probing → **data & identifiability program 的不同答案**；
- PLDM / Bagatella TD-JEPA / Jumpy / Universal Horizon / LeWM → **predictive abstraction continuum**；
- P38 / WorldTest / Value Equivalence / Task-Sufficient WM → **specialization vs reuse program**；
- PLDM uncertainty / MEND / AdaJEPA / Feedback WM / IMWM → **trust, adaptation, compute-routing program**。

---

## 10. 最终 novelty test

论文候选阶段才要求回答：

> **在一个社区已经认可的重要母问题里，我们新增了什么此前不知道、而且会改变模型设计/训练数据/规划方式/评测方式的认识？**

不是：

> “有没有一篇论文和我们标题里出现相同名词？”

