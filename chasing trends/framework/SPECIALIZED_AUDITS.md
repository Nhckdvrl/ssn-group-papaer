# Specialized Audits

这份文件收纳 **只在特定 candidate 上触发** 的专项审计。它不是每题都要逐项打勾的 40 条 checklist；若某类风险不存在，就不要机械套用。

总原则：

> 先判断 candidate 的 load-bearing risk，再调用对应 audit。

---

# 1. Evidence / artifact audits

## Public Artifact Maturity

公开页面不等于可实验。按当前可用性区分：

- **A — Runnable matched artifact**：权重/代码可跑，且存在有意义的 matched pair。
- **B — Runnable but heavy/confounded**：可跑，但成本高或多个变量一起变化。
- **C — Technical report/model card only**：可做 pressure/taste calibration，不能当 pilot 资产。
- **D — Announced / coming soon**：未来承诺，不计入当前 feasibility。
- **F — Proprietary only**：只提供 frontier pressure。

## Development Tree

base→instruct、SFT→RL、stage checkpoints、0.9B→7B 等很有价值，但必须画 change map：

- data mixture
- token budget
- optimizer/schedule
- tokenizer
- architecture
- objective
- teacher
- scaffold/harness
- context length
- post-training stage

只有主要变量较少的 edge 才接近自然实验。bundled stage 只能发现 phenomenon，不能直接归因。

## Minimum Scale of Causal Visibility

记录：

- production scale
- smallest proxy scale
- proxy token budget
- effect first visible at
- second-scale confirmation
- method/effect ranking 是否跨 scale 保持

若核心现象只有 >100B、巨量 tokens 或 proprietary traffic 才可见，默认只作 inspiration。

## Proxy Fidelity

cheap proxy 必须回答：

- 预测 full-scale 的什么 quantity？
- effect sign / method ranking / mechanism metric 是否跨 scale 保持？
- proxy 与 downstream consumer 是否有实证桥？
- 哪种 regime change 可能让 proxy 反转？
- 最小 larger-scale confirmation 是什么？

> 便宜不是 fidelity。

---

# 2. Evaluator / oracle / specification audits

## Evaluator Qualification

任何 verifier、unit test、LLM judge、simulator、success checker 在承担 correctness authority 前至少检查：

- obvious non-solution 能否通过；
- near-miss mutation 能否拒绝；
- 是否有格式/长度/visible-test/环境 shortcut；
- timeout、crash、extraction failure 如何进 denominator；
- task duplication / cluster 是否虚增 sample size；
- 重跑稳定性；
- 修 evaluator 后是否用新的 failure population 重新 qualification。

## Oracle Role Separation

同一 artifact 可能分别承担：

- exploration oracle
- reward oracle
- certification oracle
- transition oracle
- teacher oracle

角色越多，越要审 leakage / reward hacking / circular evaluation。

> 能提供 useful feedback，不代表有资格宣告 correctness。

## Specification Source

对 coding / agent / scientific environment，明确 desired behavior 来自：

- natural-language instruction
- unit/hidden tests
- reference program
- demonstration/trajectory
- simulator
- numerical/physical contract
- human feedback
- source code
- reward model/judge

必须区分：

> specification source ≠ exploration oracle ≠ reward oracle ≠ final certification。

---

# 3. Training / supervision audits

## Recipe / Stage Audit

涉及 training dynamics 时，不把“第几阶段/第几个 checkpoint”本身当 causal variable。

优先研究：

- current uncertainty
- gradient/update quantity
- data/model-relative state
- objective term
- directly measurable representation/use

若结论随 optimizer、budget、data mixture、model family 轻易改写，警惕 training biography。

## Supervision-Mask Audit

对 agent / multimodal trajectory 画：

```
state/observation → action → consequence → next action
```

标出：

- 哪些进入 loss；
- 哪些只做 context；
- 哪些完全 mask；
- 哪些变量虽然 deployment 不输出，但 downstream planning/RL 需要模型内部预测。

关键原则：

> “部署时不输出”不等于“训练时不该预测”。

## Teacher / Learner Relation

涉及 distillation/self-training 时，不用“teacher quality”作单标量。检查：

- student capacity
- student rollout distribution
- supervision complexity
- current student state
- teacher/student mismatch 是否真正可测

generic “teacher 太强学生学不会”已经是 crowded surface。

## Pretraining Value Decomposition

“pretraining helps”至少拆成：

- peak downstream performance
- sample efficiency
- adaptation speed
- environment/object transfer
- in-context task learning
- robustness/recovery
- representation reuse

不要把这些合成一个“预训练有效”。

---

# 4. Long-horizon / state / correction audits

## Failure-Onset Localization

长 trajectory 最终失败时先问：

- failure 从哪一步开始可预测？
- onset 有什么 observable/internal change？
- onset 前 prefix 是否仍有效？
- onset 后是否只是 error cascade / bad basin？
- rollback 到 onset 是否足够？
- local intervention 是否优于全程 intervention？

若 onset 不可辨识，不要硬套 local repair。

## Long-Horizon Failure Class

先区分：

- **Missing persistent state**：状态没保存/表示。
- **Accumulating state error**：小误差长期漂移。
- **Localized bad transition**：局部 onset 进入坏 basin。
- **Shared-knowledge failure**：多 worker/session 不知道彼此证据。
- **Resource-state failure**：状态存在但维护/读取成本爆炸。

不同类需要不同方法；“long context/memory”不是统一问题。

## Multi-Timescale Correction

只有在测到不同 error time constants 时，fast/slow、local/global 双时标才有机制意义。

至少需要：

- error vs horizon curve；
- local correction解决哪类快误差；
- residual slow drift；
- correction frequency × cost × quality frontier。

---

# 5. Representation / consumer / modality audits

## Representation × Consumer

representation benchmark 不等于 intrinsic representation quality。记录：

- consumer/readout 是 linear probe、MLP、PFN、finetune 还是 policy head；
- consumer 改变是否会改变 representation ranking；
- improvement 来自 representation 还是 downstream inference algorithm；
- sample regime 变化时结论是否稳定。

## Domain Structure Placement

“注入 domain knowledge”必须具体到结构放在哪里：

- tokenization
- objective
- training distribution/prior
- explicit context/metadata
- architecture
- evaluation contract

只换领域数据继续预训练，默认 scientific pressure 不足。

## Modality Extension Placement

新增 speech/vision/action/sensor 时比较：

- full integration
- selective sharing/separation
- frozen backbone + learned interface

选择边界必须由 forgetting、gradient conflict、interface ceiling 或 task structure 的 evidence 决定。

## Multi-Rate Modality

time-aligned 不等于同一变化速度。记录每个 modality 的：

- sampling rate
- intrinsic timescale
- event sparsity
- prediction horizon
- state lifetime
- correction frequency
- latency sensitivity

不同 prediction offset / asynchronous update 必须由 temporal statistics 推出。

## World-Model Consumer Contract

先写 world model 的 consumer：

- renderer
- simulator
- planner
- policy representation
- synthetic-data engine

不同 consumer 需要不同 fidelity。视觉更逼真不自动等于 planner/simulator 更好。

---

# 6. Resource / compute / deployment audits

## Operator-First Test

遇到 “thinking / TTC / adaptive compute / deliberation” 先删除术语，写：

```
state X --operator O--> X' --evidence E--> continue/stop
```

回答：

- state 是什么；
- operator 重复什么；
- evidence / stopping signal 是什么；
- compute 何时支付；
- operator 是否改变外部环境；
- 为什么同等 compute 不直接放到 base architecture/training。

这样可避免把 search、denoising、active sensing、latent recurrence 全部误当同一“thinking”。

## Real Resource, Not Proxy Resource

必须区分：

- FLOPs
- wall-clock latency
- memory/KV cache
- number of samples/rollouts
- search cost
- discovery cost
- final deployment cost

理论 token/FLOP reduction 若不能转成 operator-compatible speedup，不能直接宣称 efficiency。

---

# 7. Industry / startup / HF audits

## Industry → Academia Bridge

industry-derived seed 必须写：

- industry observation
- 为什么 academia 难观察
- strip 掉哪些 proprietary scale/resource
- underlying pressure
- academic nearest prior
- cheap causal echo
- proxy 为什么合法
- proxy 何时失效
- full-project compute ceiling

公司材料可以证明 pressure 真实，但通常不足以单独证明 mechanism。

## Product Knob Watch

多家公司显式暴露的 knob（effort、routing、context、memory、tool use、latency/cost mode 等）说明它已经成为 operational object。

这提高：

> pressure reality

但降低：

> surface novelty。

## Failure Provenance

优先重视公开：

- failed architecture
- specialization regression
- instability
- scale boundary
- train/inference mismatch
- deployment failure
- evaluator failure
- intermediate checkpoint

的报告。若一个 lab/company 持续公开“claim → failure → revision”，可作为 longitudinal lineage 读。

## Recency

区分：

- original paper/report date
- model-card date
- checkpoint update
- runtime/quantization/packaging update

不能因为 2025 paper 在 2026 HF trending 就当成 2026 scientific frontier。

---

# 8. Trend maturity / method-composition audits

## Trend Maturity

出现以下信号时，surface 通常进入 consolidation：

- evaluation correction
- matched-budget baseline
- held-out audit
- reproduction/negative result
- model–method compatibility paper
- boundary-condition paper

此时默认少做“第 N 个 variant”，多看 attribution、compatibility、capability floor、measurement。

## Convergence ≠ Novelty

多家公司都采用一个 pattern：

- 提高 operational reality prior；
- 降低 surface novelty prior。

下一问应下沉到 unresolved relation，而不是复制 pattern。

## Mechanism Composition

反对的是无 causal role 的 module stacking，不是反对组合本身。

多模块方法只有在以下情况下有科学意义：

- 每个 module 对应不同 failure source；
- interaction 在实验前有 prediction；
- factorial/pairwise test 支持 additive/sub-additive/super-additive 关系；
- full combination 确实必要。

---

# 9. Auto-research / research-memory audits

## Auto-Research Protocol

“agent 跑了很多 experiment”不是 evidence。至少公开：

- objective
- preservation constraints
- acceptance tolerance
- development / held-out environments
- search budget
- candidate provenance
- held-out 是否反馈回搜索
- independent review/verification
- final integration rule

> held-out failure 一旦继续驱动修改，held-out 就成为 development set。

并分开报告：

- discovery/search cost
- final method cost
- deployment cost

## AI-Research Role Decomposition

“AI scientist”先拆成：

- problem selection
- method proposal
- experiment design
- implementation
- execution
- analysis
- evidence interpretation
- selection
- stopping/redirect
- final judgment

implementation 自动化强，不代表 selection/judgment 已自动化。

## Research Memory Provenance

research memory 不只存对话。至少考虑：

- artifact
- claim
- parent lineage
- negative result
- reproduction
- failed verification
- conflict
- open hypothesis
- provenance
- executable state

审计 duplicate-search、monoculture、evidence independence、verification independence、attention effect。

---

# 10. 使用方式

正式 candidate 不需要把本文件全部逐条跑一遍。

先在 registration 中写：

> **Load-bearing risks**

再只调用相关 audit。

例如：

- RLVR candidate：Recipe + Evaluator + Proxy + Trend Maturity。
- VLA candidate：Modality + Multi-Rate + World-Model Consumer + Artifact Maturity。
- agent/coding candidate：Evaluator + Oracle + Specification + Auto-Research。
- industry-derived candidate：Industry Bridge + Minimum Scale + Proxy Fidelity。
- long-horizon candidate：Failure Onset + Failure Class + Multi-Timescale。

如果一个项目需要同时调用十几个专项 audit 才能说清：

> 往往不是“我们还不够严谨”，而是题本身开始失控。
