# 下一轮科研选题搜索启动提示词

你现在接手 `Nhckdvrl/ssn-group-papaer/ssn-taste`。

完整方法只读：

> **`SEARCH_GUIDE_ZH.md`**

repo 最新状态是唯一正式状态源。先读 `README.md`、`SELECTED_TOPICS.md`、当前 selected registrations、最近 commits。

## 当前正式 selected

以 repo 最新内容为准。当前应为：

- S04 — Event Boundary / Situation Model Updating
- S06 — Deliberation / Evidence Reweighting
- S07 — Where Does Surprise Go?
- S10 — Thinking-for-Speaking / Event Construal
- S11 — Value vs Measurement Precision
- S12 — Definition vs World-Fact Contextual Updating

Selected 不是正向 taste exemplar；failed 只做 anti-resurrection。

---

# 本轮首要偏好：Method-Driven Search

这一轮优先寻找下面这种论文形态，**training-free 或 training-based 都可以**：

> **已有强方法 / paradigm**
> → **发现稳定的现象性缺陷 / bottleneck / paradox**
> → **定位为什么会坏**
> → **缺陷自然推出针对性改进方法**
> → **主流 benchmark 明显涨点**
> → **ablation 证明真正有效的是哪一部分**
> → **analysis / mechanism 回证方法确实修复了原 failure**

核心不是“纯分析已有方法”，也不是“随便加个 module 刷分”。

我们想要的是：

> **Diagnosis-driven method paper.**

即：

> **方法由 failure diagnosis 推出来；ablation 和 mechanism 又回头验证 diagnosis。**

---

## 开局先大量读这种论文，不要立刻 brainstorm

优先查最近 12–18 个月：

- ACL / EMNLP / NAACL / TACL
- ICLR / ICML / NeurIPS
- 必要时 CVPR / multimodal
- 大公司 / 强团队 technical reports

重点找以下两类。

### A. Training-free

例如：

- decoding / selective intervention；
- test-time scaling / adaptive budget；
- attention / KV / cache intervention；
- model merging；
- contrastive / guided decoding；
- speculative decoding；
- inference-time grounding / verification；
- activation intervention；
- inference scheduling。

每篇都提炼：

> **baseline failure → diagnosis → training-free fix → gains → ablation**

### B. Training-based

例如：

- SFT / RL / preference optimization 的 failure；
- rollout / sampling / advantage / reward design；
- supervision signal mismatch；
- representation/state alignment；
- multimodal grounding / forgetting；
- training instability / collapse；
- objective / deployment distribution gap。

每篇提炼：

> **training failure → causal diagnosis → redesigned objective/sampling/supervision → gains → training dynamics / ablation**

---

# 本轮优先搜的 failure pressure

不要限制在这些，但优先关注：

1. **compute allocation 错**
   - overthinking / underthinking；
   - 大部分 token/branch 没价值；
   - 固定 budget 不适应难度；
   - expensive method 在大量 easy region 浪费算力。

2. **proxy / objective 错位**
   - verifier / reward / value model 与真实目标错位；
   - exact criterion 过严；
   - token-level objective 与 sequence-level goal 错位；
   - offline/base-policy signal 到部署策略时失准。

3. **training / post-training 破坏已有能力**
   - reasoning 增强但 perception / grounding / calibration / diversity 下降；
   - instruction tuning 损害 base capability；
   - compression / adapter / merge 在深层 state collapse；
   - stronger model 反而让 RL signal 饱和。

4. **exploration / diversity collapse**
   - stochastic samples 只是 lexical diversity，没有 semantic diversity；
   - group-relative RL advantage variance 消失；
   - self-refinement 锚定旧错误；
   - search/verifier 只探索 base policy 附近。

5. **局部优化与端到端目标冲突**
   - 单 token / 单 step 更省，但生成变长导致总成本更高；
   - intermediate score 上升但 final quality 不涨；
   - local routing / pruning / sparse attention 改善 proxy，却伤害 generation。

6. **multimodal / long-context changed regime**
   - text 方法直接搬到 multimodal 后 perception 成 bottleneck；
   - reasoning 越长越忘视觉输入；
   - local detail 与 global context trade-off；
   - long-context compression 保留 token 信息但丢 state/use capability。

---

# Candidate Gate：先诊断，再设计方法

每个候选先写六行：

1. **Existing method/paradigm**
2. **Stable failure / paradox**
3. **Evidence this failure is real**
4. **Hypothesized bottleneck / mechanism**
5. **Targeted intervention implied by diagnosis**
6. **Benchmark + ablation that would verify the story**

如果第 4 和第 5 没有直接对应关系，KILL。

不要：

> 先发明一个方法 → 再找 failure 给它讲故事。

应该是：

> failure → diagnosis → method。

---

# Method Seed 的硬 Gate

只有同时满足以下条件才进入 full audit：

- baseline 是社区真实使用的强方法，不是弱 strawman；
- failure 在多个条件 / subset / model 上稳定，而不是偶然掉点；
- why-care 一句话懂；
- method 是 diagnosis 的直接修复，不是 arbitrary tweak；
- 有一个小实验能先确认 failure / bottleneck；
- 有现实 benchmark 可以验证最终收益；
- 可以设计关键 ablation：
  - 去掉针对 bottleneck 的组件，gain 应明显消失；
  - 替代解释能被排除；
- gain 不能主要来自：
  - 更多 tokens；
  - 更多 samples；
  - 更多训练数据；
  - 更多参数；
  - 更强 teacher；
  - 巨大 compute increase；
- 不需要 model zoo / hyperparameter matrix 才能讲清楚。

---

# Novelty Check 仍然严格

这种题型更容易掉进：

> “paper A 的缺陷 + 一个常规修补方法。”

所以必须检查：

> **nearest prior 是否已经发现同一个 failure，并提出 essentially same fix？**

允许：
- prior 观察到 failure，但没有找到正确 bottleneck；
- prior 方法处理症状，我们找到更根本原因并推出不同 intervention；
- changed regime 让老方法的关键 assumption 首次失效。

不算 novelty：
- 换 loss；
- 换 model；
- 换 benchmark；
- 多一个 regularizer；
- paper A × paper B；
- 同一个 fix 做得更复杂。

---

# 搜索时特别学习这些 2026 论文的“故事结构”

不要复制题材，只学方法形成方式：

- **Less is More / MTI**：发现 uncertainty 高度局部化 → 只在关键 token intervention。
- **FLy speculative decoding**：exact-match verification 会错误拒绝语义正确 draft → 放宽 verification，但保持 correctness。
- **PlaM**：multimodal finetuning 出现分层 degradation → 用分析结果决定在哪些层 merge base LM。
- **Active-Look**：zoom 与 highlight 各有互补 failure → uncertainty/disagreement 决定何时用哪种视觉操作。
- **Too Correct to Learn / Mixed-CUTS**：强模型在简单 RL 数据上过度正确、group advantage variance 消失 → 有约束的 exploration 恢复训练信号。
- **SADA**：context-to-parameter 方法 deeper-layer hidden-state collapse → state alignment + 更合理 input interface。
- **Evolutionary Guided Decoding**：static value model 的 base-policy distribution gap → iterative value exploration/refinement。
- **VAPO / PAPO**：多模态长推理的核心瓶颈变成 perception / visual forgetting → 训练目标直接增加视觉 grounding signal。
- **CURE**：self-improvement 依赖 test-time 不存在的 external feedback，且旧错误会 anchoring → jointly train solve/critique/re-explore，并丢掉旧解。
- **Plan-and-Budget / SyncThink**：固定 reasoning budget 导致 over/under-thinking → adaptive test-time allocation / termination。

真正要找的是：

> **还有哪个强方法存在类似“非常具体、可测、可修”的 failure？**

---

# 搜索纪律

仍然遵守：

- Sasano 明确评价优先；
- 不追热点本身，但可以研究热门方法的**基础 failure**；
- 允许最终 0 survivor；
- 不救 seed；
- 不赌一个完全未知 anomaly；
- 不用 benchmark/data/evaluator 作为主要贡献；
- mechanism 是为了证明方法为什么有效，不是为了装饰。

如果连续 2–3 个候选都在同一 lineage 死亡，Global Reset，换方法家族。

---

# 最终输出

一个真正过线的候选应能写成：

> **现有方法 M 在条件 C 下系统性出现 failure F。**
>
> **我们发现 F 主要由 bottleneck B 导致，而不是常见解释 A。**
>
> **因此提出 intervention I，直接修复 B。**
>
> **I 在标准 benchmark 上提升 X，同时降低/不增加成本 Y。**
>
> **关键 ablation 显示去掉 B-targeted component 后收益消失，并且 mechanism metric 与最终 gain 同方向变化。**

然后只有：

> **PILOT-AUTHORIZED**

或

> **KILL**

不要 SERIOUS / maybe。

本轮首要目标不是再找一个“纯科学问题”，而是：

> **找到一个有真实 failure diagnosis、能推出方法、能刷 benchmark、又能通过 ablation/mechanism 讲清楚为什么有效的题。**
