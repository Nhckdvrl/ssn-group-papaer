# Field Problem Map 2026 — compact / latent world models for planning

更新：2026-10-02。  
目标：不是枚举论文，而是回答 **这个领域为什么不断产生顶会论文、社区真正关心什么、哪些问题已被压缩、哪些 pressure 仍适合我们用多卡实验吞吐量去挖。**

> 原则：这里不存在“完全没人做”的大空白。我们找的是 **已有强工作证明重要、但核心认识还不闭合** 的 problem territory。novelty 应来自新的 distinction / failure law / regime / identification / minimal repair，而不是“某个模块第一次加在 LeWM 上”。

---

# 0. 一张总图：world model 要成为 decision model，需要经过什么

```text
observations / offline trajectories
          │
          │  what is identifiable?
          ▼
      internal state
  ┌───────┼────────┐
  │       │        │
what exists?  what is hidden?  what can actions change?
  │       │        │
  ▼       ▼        ▼
representation / belief / intervention structure
          │
          ▼
action-conditioned predictive structure
  ├─ point dynamics
  ├─ stochastic / branching futures
  ├─ successor / occupancy abstraction
  └─ temporal hierarchy
          │
          ▼
planner-facing semantics
  ├─ metric / cost
  ├─ proposal / verifier
  ├─ H/K / action chunk
  └─ goal / query interface
          │
          ▼
candidate choice under finite compute
          │
          ▼
real closed-loop outcome
          │
          └──── execution feedback / adaptation ────┐
                                                    │
                                                    └→ model/belief
```

2025–2026 的研究爆发，本质上是在逐层否定一些过去默认成立的等号：

```text
good pixels          ≠ useful state
good representation  ≠ usable planning metric
good 1-step forecast ≠ stable rollout
good rollout         ≠ good action discrimination
good model           ≠ good search
good search          ≠ good temporal interface
observed trajectory  ≠ environment controllability
same image           ≠ same physical state
one predicted future ≠ all plausible futures
good ID performance  ≠ robustness under dynamics/query/behavior shift
```

这也是为什么领域还有研究空间：**不是缺一个新 loss，而是这些等号在什么条件下成立、何时失效、该把结构放在哪一层，仍没有统一答案。**

---

# 1. Problem Family A — What is the right state? Representation, observability, belief

## 母问题

> world model 的“state”究竟要保留什么，才能既支持 goal comparison，又足以预测 action consequence？

### 第一阶段：从 pixel reconstruction 到 abstract latent
- PlaNet / Dreamer / TD-MPC 系列：latent imagination可直接支持control，不需要像素全重建。
- DINO-WM：pretrained visual features本身可以作为planning state。
- LeWM / JEPA-WMs：甚至无需大 frozen encoder，可end-to-end学 compact predictive latent。

### 第二阶段：semantic state不等于 planning state
- Temporal Straightening：trajectory curvature决定Euclidean planner conditioning。
- SCALE / ATLAS / AnisoWM / DA-LeWM：latent marginal、relational geometry、candidate ranking是不同问题。
- SMWM / AC-MTM / PSG-JEPA：action / proprio / physical grounding迫使latent保control-relevant信息。

### 第三阶段：一个 observation 不是一个 physical state
- FIRM-WM：goal-comparable configuration 与 history-dependent dynamics state 分角色。
- UWM-JEPA：POMDP下需要携带 compatible hidden futures的belief structure。
- Flow Equivariant WM：partial observation下的structured memory。
- Physically Viable WM：appearance相同但 latent physics不同，intervention outcome可完全不同。
- Branch-JEPA：point-valued successor无法表达多future support。

## 已饱和的 headline

- “pretrained visual representation不一定适合control”
- “latent需要action-aware”
- “POMDP需要history/memory”
- “same image可能隐藏不同physics”
- “需要uncertainty / multimodal future”
- “把goal state和dynamic state拆开”

## 仍存在的 pressure

最有意义的不再是提出这些概念，而是**找 decision boundary**：

- history能否消除 ambiguity？
- ambiguity是 epistemic（hidden parameter/state）还是 aleatoric（intrinsic stochastic transition）？
- planner什么时候只需 point estimate，什么时候需要 full belief / set of futures？
- goal-comparable state与control-belief需要怎样交互？
- uncertainty如果存在，planner应如何消费——expected cost、robust cost、information gathering、abstain？

## 资源适配

**高。** 可以用小 simulator精确控制 hidden variables / ambiguity，并用 candidate oracle做 causal audit。  
**但 novelty collision 很高。** 所以 M1只保留 conditional mine：必须从 decision regret / regime law切入。

---

# 2. Problem Family B — Does the model know intervention effects, or only observed correlations?

## 母问题

> factual trajectory里看到“动作后发生了什么”，并不意味着模型知道“换一个动作会发生什么”。

这直接决定 MPC 能否比较 candidate actions。

### 近期 lineage
- ActSWM：不同 action futures collapse / context collapse。
- AD-WM / PhyLatent：counterfactual action discrimination。
- Do-JEPA / FIRM-WM：same-reset physical intervention branches直接提供 action effect evidence。
- Physically Viable WM：latent physical variables决定 intervention response。
- What Must a WM Distinguish?：mechanism / response / decision sufficiency分层。

## 已饱和

- “factual prediction ≠ counterfactual control”
- “不同action的future要分开”
- “same-reset interventions更好”
- “world model要causal/action-grounded”

## 还可用在哪里

作为 M1/M3 的**鉴别工具**：
- 若behavior data semantics失真，究竟是trajectory metric问题，还是action effect本来就没identify？
- 若belief模型失败，是hidden state没识别还是counterfactual action effect没识别？

不单独开新 mine。

---

# 3. Problem Family C — Prediction vs planner-consumed geometry / decision relation

## 母问题

> 世界模型可以把未来“预测得像”，但 planner 消费的是一个 cost / ordering / local candidate relation。

### lineage
- Temporal Straightening：curvature。
- RC-aux：finite-budget reachability。
- Temporal-Distance JEPA：trajectory-mined directed progress cost。
- DA-LeWM：Plan-Real / CEM-stage ranking。
- CGS：action displacement geometry。
- Objective Is the Bottleneck：信息存在但L2 objective坏。
- D-JEPA：decision-local candidate relation + executed ordinal evidence。
- DRPE：error是否落在decision-relevant dimensions。

## 领域现在关心的不是“metric matters”

而是：
- planner在哪个 candidate distribution上消费它？
- coarse/fine decision需要什么分辨率？
- ranking margin多小时 prediction error会flip decision？
- training objective学的是环境关系、behavior关系还是candidate局部关系？
- planner/query改变时，这种 alignment 能否复用？

## 已饱和

几乎所有 generic metric-alignment story都进入红区。  
这也是为什么 I04 / E02 只能作为 measurement calibration。

## 对我们

这层是**读数层**而不是默认选题层。M2/M3任何结果都必须在这里落地到 candidate ordering。

---

# 4. Problem Family D — What dynamics object should be predicted?

## 母问题

> 是 one-step point transition、multi-step trajectory、distribution、structured operator，还是 policy occupancy？

### point / recursive dynamics
- LeWM / JEPA-WMs。
- SALT：error propagation operator；one-step更差但planning更好。
- Bilinear WM：structured transition。
- Fast-LeWM / variable-length WM：direct multi-horizon。

### stochastic / multi-future
- Flow-JEPA：trajectory distribution。
- Branch-JEPA：finite-support latent successors。
- Var-JEPA：probabilistic JEPA formulation。
- UWM-JEPA：belief-space hidden futures。

### occupancy / temporal abstraction
- Bagatella TD-JEPA：successor-feature / long-horizon policy dynamics。
- Jumpy World Models：policy-induced occupancy across timescales。
- HWM / Dual-WM / FF-JEPA：hierarchical/multi-timescale state transitions。

## 已饱和

- one-step不够；
- recursive error会累积；
- multimodal dynamics需要distribution；
- hierarchy / variable horizon；
- structured dynamics更稳定。

## 未闭合的真正问题

这几种 predictive object **各在什么 regime 是最小充分结构？**

这直接连接 M2：
- arbitrary action sequence query → explicit transition可能不可替代；
- fixed/known policy family → successor/occupancy可能更高效；
- long horizon → policy/macro abstraction；
- stochastic hidden branch → distribution/belief；
- new reward/query → task-agnostic explicit prediction可能更可复用。

这比再设计一个 transition block更值得挖。

---

# 5. Problem Family E — Where should planning computation live?

## 母问题

> 学模型后还要不要search？search多少？哪些planning结构应该在training阶段amortize？

### explicit test-time planning
DINO-WM / PLDM / LeWM / JEPA-WMs + CEM/MPPI/GD。

### learned proposal / planner
GC-IDM、IMWM、SAGE、LeFlow、RP1、Parallel Stochastic Gradient Planning。

### temporal abstraction
Jumpy WM、HWM、Dual-WM、FF-JEPA、Anchored Planning。

### implicit zero-shot predictive representation
Bagatella TD-JEPA / successor-feature line。

### hybrid
TD-MPC2 等 policy/value + short model search。

## 当前最重要的 unresolved question

P09 TMLR 已明确指出 explicit / implicit 的 trade-off：
- explicit：training较轻、task-agnostic、可hardcode arbitrary cost / supplied action；test-time iterative planning贵；
- implicit：training重，把predictive structure摊入representation/policy；test-time快，但 objective / policy-family/generalization有边界；
- hybrid介于两者。

**目前没有一个足够清楚的 empirical regime map。**

所以 M2不是“比较两个模型”，而是研究：

```text
task/query flexibility
× horizon
× dynamics shift
× data coverage
× train compute
× inference budget
→ optimal location of predictive/planning computation?
```

## 资源适配

**中高。** native TD-JEPA pixel runs是 1M–2M updates，不是 RC-aux 那么轻；但完全是独立单卡job，正适合多卡并行。  
难点是 protocol matching，不是多节点scale。

---

# 6. Problem Family F — What does offline data actually identify?

## 母问题

> dataset里存在 transition，不代表 dataset的 trajectory organization、behavior policy、episode identity 等 metadata 等于 environment 的 optimal controllability。

### 已知理论/经验
- PLDM：data quality/diversity/layout/stitching改变model-based/model-free表现。
- **Controlled-WM Identifiability (P94)**：behavior policy 的 conditional action excitation 决定受控 transition 是否可识别，并直接影响 counterfactual reachable set 与 planning。
- OGBench：专门分开 stitching / long horizon / stochasticity。
- Quasimetric GCRL：behavior future statistics与optimal goal distance不等价。
- Multistep Quasimetric：local Bellman optimality与global Monte-Carlo stability张力。
- CGCIVL：cross-trajectory pair不能只凭trajectory identity判connected。
- RC-aux：论文自己把trajectory offset称 empirical finite-budget proxy。
- Temporal-Distance JEPA：same-trajectory gap + heuristic cross-trajectory negatives直接进入planner semantics。

## broad claim 已经被占

“offline data bias matters”当然不新。  
“behavior path ≠ shortest path”也不新。

## M3 的 exact pressure

现代 compact JEPA planner开始**把trajectory-derived statistics直接写进 deployed metric/reachability representation**。

因此新的可识别问题是：

> 在 environment dynamics保持不变时，改变 generating behavior policy 是否会系统性改变 model 的 **planner-consumed semantics**，并改变同一 test candidate pool 的 ordering / closed-loop choice？

这是 data problem、representation problem、planning problem的交叉处。

### 真正的因果难点
behavior policy同时改变：
- state occupancy；
- action support；
- route frequency；
- transition support；
- temporal path length。

所以必须用 matched/weighted support metrics与non-temporal LeWM control，不能看到分数变就归因“behavior geometry”。**尤其要控制 conditional action excitation；否则 P94 已经提供更直接解释。**

M3 剩下的真正空间因此被压得更干净：**当 one-step transition / action-effect identifiability 已经相近时，higher-order trajectory order/gap 监督是否仍产生 behavior-route imprint？**

## 资源适配

**极高。** 主要成本是多数据regime × 小模型 × seeds × task。正是多独立GPU最擅长。

---

# 7. Problem Family G — Goal/query generality vs decision alignment

## 母问题

> 一个 world model 要支持多少种未来 query？为了一个 planner/goal 学得越“对齐”，会不会越失去 generality / reuse？

### 直接压力
- What Must a WM Distinguish?：query + candidate + planner决定所需sufficiency；query-conditioned joint model在seen objective更强，但unseen objective优势缩小；提出 modular “query tells where to look, action-conditioned model predicts what happens”。
- WorldTest（ICML'26）：world model应支持 multiple environment-level queries。
- Grounded WM：language semantic query进入WM-MPC。
- WorldTest / decision-centric evaluation：claim必须与use一致。

## 为什么暂时 WATCH

问题非常重要，但 P38 已经把**query-conditioned specialization vs reusable prediction**讲得很直接。  
若我们单独做“planning alignment损害generalization”，容易被压缩。

当前作为 M2/M3 的必测 stress：
- same model换goal/reward；
- planner/cost换掉；
- seen→unseen objective；
- candidate generator换掉。

如果实验中出现特别强的 alignment-reuse trade-off，再重新注册 mine。

---

# 8. Problem Family H — Distribution shift, test-time adaptation, feedback

## lineage

AdaJEPA：MPC闭环每次 transition自监督gradient update。  
Sandwich-Residuals：只学小 predictor residual。  
ReDRAW：少量 target data校准 latent dynamics residual。  
Feedback WM：不更新参数，用online observer-style feedback state。  
PLDM / offline MBRL：uncertainty / OOD support。

## 结论

这是**真实问题，但不是低竞争空间**。generic：
- frozen model遇shift坏；
- online update能救；
- residual比full FT省；
- feedback correction有用；

都已有直接工作。

### 对我们
把 shift 当作 M2 的 regime variable、M1 belief recovery variable、M3 data-semantic stress，不单开 adaptation paper。

---

# 9. Problem Family I — Action interface / latent action / cross embodiment

2026 ICML已经非常密集：
- Learning Latent Action WMs in the Wild；
- Cross-Embodiment Robot Foundation WMs with Latent Actions；
- Co-Evolving Latent Action WMs；
- DiLA；
- action-parameterization invariance；
- DDP-WM等 action/local dynamics work。

这是重要方向，但：
- 数据/视频量与I/O更重；
- 多embodiment资产复杂；
- 与本 workbench “compact single-GPU controlled science”优势不完全一致。

除非 baseline实验自然暴露 action-interface pressure，否则不主动切入。

---

# 10. Problem Family J — Efficiency / scale / generative world models

包括：
- Fast-LeWM / DDP-WM / Bilinear WM / RP1；
- CompACT；
- latent-action video WM；
- PERSIST / Infinite-World / large interactive video WM。

这些可以给我们“社区尺度”与方法灵感，但不是资源最匹配的主矿。

尤其 PERSIST / Infinite-World 的问题是 persistent 3D/video simulation，科学与算力/I/O对象都不同。不要因为都叫 world model 就把 compact latent planning workbench漂到大video generation。

---

# 11. 2026 saturation matrix

| pressure | importance | 2026 crowding | controlled experiment leverage | our resource fit | current role |
|---|---:|---:|---:|---:|---|
| representation geometry | very high | **very high** | high | high | baseline/readout |
| decision metric / ranking | very high | **very high** | very high | high | common audit |
| recursive dynamics | high | **very high** | high | high | baseline |
| stochastic multimodality | high | high after Branch/Flow/UWM | high | high | M1 control, not standalone |
| action counterfactual effect | very high | **high** | very high | high | oracle/control |
| search/proposal | high | **very high** | high | high | baseline |
| long horizon/hierarchy | high | **very high** | high | high | regime variable |
| POMDP/history | very high | high | very high | high | **M1 conditional** |
| behavior→controllability identification | high | medium-high after P94 | **very high** | **very high** | **M3 primary but sharpened** |
| explicit↔implicit predictive computation | very high | medium | high | medium-high | **M2 primary** |
| query generality/reuse | very high | high after P38/WorldTest | high | high | WATCH/stress |
| test-time adaptation | high | **high** | high | high | baseline/WATCH |
| latent action/cross embodiment | high | **high** | medium | low-medium | outside first wave |
| efficient architecture | high | **high** | high | medium | outside first wave |

“crowding”不是kill criterion；它只决定我们需要多强的 exact delta。

---

# 12. 当前 research-mine judgement

## Tier A — should receive first real GPU/data experiments

### M3 / I09 — behavior trajectory semantics → controllability
**为什么留下：**
- 与RC-aux/Temporal-Distance JEPA直接相关；
- 不是论文已经明确解掉的 broad question；
- 与QRL/CGCIVL形成清晰related-work tension；
- 可做真正intervention；
- 容易连接candidate ranking + closed-loop；
- 资源极匹配；
- 结果为正/负都能快速改变后续研究方向。

**最大风险：** 被coverage shift解释。  
所以 E14 的价值完全取决于 support matching/audit。

### M2 / I08 — explicit ↔ implicit predictive computation frontier
**为什么留下：**
- P09 TMLR正文明确承认 direct empirical comparison / compute-generalization tradeoff仍开放；
- P65、P80、TD-MPC2等让它成为一个真正的 design continuum；
- 对“world model究竟应该是什么”有母问题尺度；
- 结果如果形成 regime law，不是小trick。

**最大风险：** native protocol apples-to-oranges。  
因此必须先做小 matched study，不一开始大矩阵。

## Tier B — cheap proof-of-problem, then decide

### M1 / I07 — observable-goal vs control-belief
**为什么降级：**
P75/FIRM/UWM/Branch/Flow等已经占据大量 broad novelty。

**为什么不删：**
这些工作仍没有完全回答：
> compact reward-free image-goal MPC 中，history-resolvable aliasing 与 irreducible belief uncertainty的 **action-regret boundary** 是什么？

E11非常便宜；如果出现惊人的自然failure，仍可能重新升Tier A。

## Shared scientific instruments

- E02 candidate decision audit；
- E06 oracle bottleneck ladder；
- I06/E08 heuristic-negative semantic audit。

它们帮助**发现/解释 paper**，但默认不是paper本身。

---

# 13. 什么结果值得把几十张卡铺开

只在出现下面任一信号后：

### M3
同一环境、matched local support下，behavior policy改变 → planner semantics稳定漂移 → same candidate pool ordering翻转 → closed-loop后果；且至少第二objective复现。

### M2
一个简单 regime variable（例如 objective shift / horizon / test compute）在多个task上预先预测 explicit vs implicit/hybrid ranking；hold-out regime仍成立。

### M1
同/近同observation下存在真实 action flip；native history baseline仍产生系统 regret；belief/multi-hypothesis correction只在可预测的 ambiguity regime有增益。

如果只得到：
- probe显著；
- latent图好看；
- average prediction error变；
- 一个toy有异常；
- 多跑seed后p值更小；

**不要扩大。**

---

# 14. 顶会 narrative 模板不是固定“failure + loss”

这个领域的强论文至少有四种合法生长方式：

### A. New failure / distinction → minimal repair
例：SALT、RC-aux、Temporal Straightening。

### B. Regime law → adaptive/hybrid principle
这是 M2 最理想形态。

### C. Identification result → changes how methods should be trained/evaluated
这是 M3 如果方法很简单甚至不需要新architecture时的形态。

### D. Strong comparative science → overturns a common design assumption
PLDM / JEPA-WMs 是先例。  
但必须是 controlled comparison 导出新的 field-level understanding，不是 leaderboard。

---

# 15. 对本地 agent 的最终研究准则

> **不要问“还能加什么模块？”**  
> 问“现有最好方法在什么自然条件下做出了错误决策？这个错误是哪个领域默认假设被破坏？哪个最小 intervention 能区分相互竞争的解释？”

> **不要找完全空白。**  
> 找 related work 之间有真实 tension、每一边都有强证据、但它们没有告诉我们“什么时候哪一个成立”的位置。

> **不要因为卡多就跑全矩阵。**  
> 先用 1–4 张卡把 scientific branch 分开；一旦出现 load-bearing signal，再用多GPU把 scope / seeds / environments迅速打透。
