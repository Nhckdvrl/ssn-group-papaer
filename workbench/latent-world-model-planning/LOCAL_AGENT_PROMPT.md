# Local Agent Prompt — latent-world-model-planning

把本文件作为执行机 agent 的启动提示。**不要从头找题，也不要因为某个现有实验卡写得最详细就把它当主论文。**

---

你正在 `Nhckdvrl/ssn-group-papaer/workbench/latent-world-model-planning/` 工作。

## 最终目标

从 compact latent world-model planning 中发展一篇 **ICLR / ICML / NeurIPS / CVPR 级**论文。

我们的资源优势不是多节点大预训练，而是很多独立 GPU：适合强 baseline、受控 intervention、多 seed、多环境、oracle audit、idea iteration。网络/磁盘/节点通信差，不做跨节点大训练。

最重要的是 **problem-led research**：

> 找到这个领域真正关心、会改变模型/方法设计的 failure / tension；  
> 用实验把问题压实；  
> 再让方法从问题本身自然长出来。

禁止把“我做了一个新 probe，某个位置行为奇怪”当研究目标。内部读数只有连接到 candidate decision / regret / closed-loop behavior 时才有科学重量。

当前科学 claim = 0；M#/I# 全是 mining seeds，不是结论。

## 必读顺序

1. root `AGENTS.md`
2. root `RESOURCES.md`
3. `workbench/README.md`
4. 本目录 `README.md`
5. **`FIELD_PROBLEM_MAP_2026.md`**
6. `PAPER_LINEAGE.md`
7. **`RESEARCH_MINES.md`**
8. `LITERATURE_LEDGER.md`
9. `PROBLEM_METHOD_MAP.md`
10. `POSITIONING.md`
11. `EXPERIMENT_PROGRAM.md`
12. `ASSETS.md`
13. `HANDOFF.md`
14. `CLAIMS.md` / `PAIN_LOG.md`
15. I09 / I08 / I07
16. I06 / I03
17. E00–E15

然后运行：

```bash
python3 tools/process/check.py
```

ERROR 先修；WARN 理解后处理。不要为清 warning 机械修改科研内容。

## 两个 TD-JEPA 必须分清

- **Bagatella et al. TD-JEPA**, ICLR 2026 Oral, `facebookresearch/td_jepa`：zero-shot RL / successor features / implicit long-horizon predictive representation。
- **Bai & Xiong Temporal-Distance JEPA**, arXiv 2607.25337, `HKBU-KnowComp/Temporal-Distance-JEPA`：LeWM/CEM planning，trajectory temporal distance + heuristic negatives。

后者历史 config 仍叫 `td_jepa`。任何实验、日志和 checkpoint 都写作者/全名，禁止混淆。

# 1. 先继承 problem map，不重新 brainstorm

当前优先级不是平级：

1. **M3 / I09 = Tier A1 / first pilot**
2. **M2 / I08 = Tier A2 / second pilot**
3. **M1 / I07 = Tier B / conditional cheap oracle**

### M1 / I07 — Observable goal ≠ control belief（conditional）

image goal 描述可观测配置，但 control 可能依赖隐藏 velocity/contact/friction/regime。

真正要问：
- same/near-identical observation 下 hidden state 是否改变最优 candidate action？
- native deterministic/history latent 是否因此产生真实 action regret？
- history什么时候够，什么时候必须保留 multi-hypothesis belief/uncertainty？

Physically Viable WM、FIRM-WM、UWM-JEPA、Branch-JEPA、Flow Equivariant WM 已占大量 broad hidden-state / belief / multimodal-future space。我们的空间只剩：**finite history 后仍存在的 actionable ambiguity + candidate regret + regime distinction**。history能解决就停止，不造 belief method。

### M2 / I08 — Predictive-computation placement（Tier A2）

explicit JEPA-WM 把 dynamics 保留成可 rollout model、部署时 search；Bagatella TD-JEPA 等把 long-horizon structure amortize 进 representation/policy。

真正要问：
- reward/goal redefinition
- unseen objective
- dynamics/layout shift
- horizon
- data coverage
- train compute vs deployment compute
- **task/query information budget**
- arbitrary-action counterfactual query

是否产生稳定、可预测的 regime boundary。

不要只回答“谁分数高”。

### M3 / I09 — Behavior trajectories ≠ environment controllability（Tier A1）

RC-aux / Temporal-Distance JEPA 从 behavior trajectory 的 order/gap/negative 学 planning semantics。

真正要问：
- 改变真实 generating behavior policy 后，learned reachability/progress 是否系统变化？
- local predictive fidelity相近时，candidate ordering / MPC是否仍随 behavior route/tempo漂移？
- 这种 imprint能否跨两个 objective/task structure复现？

旧 I01/E03-E04 只改 long-episode metadata而不改变 short-window loss，已 VOID。不要复活。

### I06

semantic negatives vs geometric regularization 是 M3 的 cheap subdiagnostic。可以早跑 E08，但**不得因为便宜/详细就默认它是论文题**。

### I03

oracle bottleneck ladder 是公共诊断。除非出现 cross-task predictive regime law，否则不独立升级。

# 2. Step 0 — 资产盘点与 E00

先看机器已有 repo/env/data/checkpoint，禁止重复下载。

写回 ASSETS 状态：

```
public entry
→ downloaded + hash
→ loadable
→ smoke passed
→ native numeric reproduction
→ instrumented common audit
```

不同 repo 可不同 venv。不要为统一 framework 破坏 native baseline。

E00 单 GPU：
- dataset/checkpoint可读
- env/action/goal/success checker
- encode→rollout→plan→act
- train step
- planner call
- VRAM
- env/render time
- I/O wait

不要上来跑满 100 epochs。

# 3. Step 1 — E01 common substrate

至少：
- 一个 explicit compact WM native checkpoint / native protocol；
- candidate logger旁路；
- env reset/replay；
- true candidate utility；
- H/K/action block/scoring index manifest；
- TwoRoom或类似 topology + 一个 contact-rich environment 的入口。

native result 与 common audit result分开。

# 4. Problem-existence pilots：第一轮可以并行，但都保持小

## E14 — M3 behavior-policy intervention（FIRST）

先看 [E14](experiments/E14_behavior_policy_semantics_intervention.md) 的 staged protocol。

第一轮：
- 公开 OGBench `navigate/stitch/explore` 或 `play/noisy` 只做 **sensitivity discovery**；
- 真正的 scientific pilot 用 fixed start-goal 的 DIRECT vs DETOUR/LOOP；
- 必须定量报告 state/action/local-transition support overlap；
- 先 LeWM + Bai/Xiong Temporal-Distance JEPA，1 seed；
- fixed candidate ranking/regret + closed-loop 才是 gate。

不要把普通 data coverage shift写成 behavior-semantics finding。

真正收集/构造不同 **behavior policy** 的 offline trajectories：

- direct/efficient
- random/suboptimal
- detour/looping
- route-biased
- mixed

首轮只 2–3 种。

环境 dynamics不变。尽量匹配：
-样本量
- state coverage
- action coverage
- local transition support
- start/goal distribution

无法匹配就定量报告 overlap，不假装因果识别已完成。

先跑 Bai/Xiong Temporal-Distance JEPA / RC-aux 中最容易复现的一个，再加 LeWM non-temporal control；出现稳定 effect 后才第二 objective。

关键不是 learned score变了，而是：
- environment shortest/geodesic关系变没变？
- fixed candidate ranking/regret变没变？
- closed-loop变没变？
- local dynamics error是否基本稳定？

## E08 — I06 cheap audit

可以和 E11/E14 同时跑，主要 CPU。

必须 instrument **真实 sampler**，不是另写一个想象中的 negative generator。

输出 semantic validity / unknown / count / margin/budget strata。

但 E08 本身永远不是 paper result；它只决定 M3 中 negative-role是否值得继续 E09。

## E13 — M2 predictive-computation placement（SECOND）

common substrate稳定后启动。优先 OGBench Cube pixels。

explicit：
- JEPA-WM / LeWM family

implicit：
- **Bagatella TD-JEPA (ICLR'26 Oral)**

第一轮 1–2 common datasets/environments，保留 native protocol并建立 common audit。

必须分开记三本账：
- **training compute**：steps / GPU-hours / VRAM；
- **task/query information**：goal image、reward function、reward-labeled inference samples、privileged relabel信息；
- **deployment compute**：model calls / candidates / wall time。

Bagatella TD-JEPA official OGBench eval会采样约 10k replay states并用 OGBench `physics` relabel reward；不能和“一张goal image”当同等task information。

最小 regime：
1. ID goal/reward
2. reward/goal redefinition
3. layout/dynamics shift
4. near vs far horizon

只要结果是“方法 A 一直更高”，不要急着写 paper；继续问这是 training compute、task-information、function class、search budget还是 generalization 的哪一项。

## E11 — M1 actionable ambiguity（CONDITIONAL）

只做 oracle，不先训练。

顺序：same RGB/different velocity sanity → 给2–3 frame/native history → history能解就STOP → 只有仍相容的 hidden friction/contact/regime/stochastic branch才看 candidate regret → baseline确实混淆才 E12。

# 5. 方法什么时候允许出现

新方法只可来自真实 evidence：

- E11：history无法解决的 actionable belief ambiguity；
- E14：behavior policy imprint真实改变 planning；
- E13：明确的 explicit/implicit regime boundary；
- E08/E09：semantic role 与 regularization role真的分离；
- E06：某个 layer被 oracle replacement确定为 binding bottleneck。

优先最小解释。

不要：
- RC-aux + 一个 loss；
- LeWM + 一个 module；
- “换成更复杂 Transformer”；
- 因为某个 probe看起来差就做 regularizer；
- 先有喜欢的 method 再找 benchmark。

# 6. 共同 attribution rules

- probe变、decision不变 → 不是主 finding；
- prediction error变、candidate ranking不变 → 不夸大；
- candidate pool没有好plan → 不只修 metric；
- true dynamics仍失败 → 不只怪 predictor；
- encoded-real score就错 → metric/representation；
- H/K/scoring-index control能救 → protocol layer；
- behavior intervention同时改变 coverage → 先拆 coverage；
- history能完全解 alias → 不声称 belief必要；
- explicit/implicit比较没匹配 data/task/compute → 不做 scientific ranking；
- oracle方法只作 measurement / upper bound，不冒充 deployable method。

# 7. 多 GPU 怎么用

第一轮每个 mine 都只做 **small decisive pilot**。

一旦某条过 gate，再把独立卡用于：
- train seeds
- behavior regimes
- aliasing strength
- hidden-factor family
- goal/reward shifts
- candidate budgets
- confirmatory environment
- ablation / nearest baseline

同节点先 stage local data；1→2→4 jobs测 I/O 退化。不要跨节点 DDP。

大量 GPU 的价值是 **加速 scientific iteration**，不是扩大单次训练规模，也不是铺没有判别力的 Cartesian product。

# 8. 文献与 novelty 是滚动的

2026 latent WM 更新极快。每次出现以下情况都重扫直接近邻：

- 某个 E## 出现明显 anomaly；
- idea准备从 SEED → paper hypothesis；
- C## 升 L2；
- 要设计方法；
- 要跨 benchmark；
- candidate / 投稿前。

深读新近邻时记录：

```
mother question
old assumption
pressure / counterexample
idea leap
method
data / benchmark
decisive experiment
nearest related work
exact delta
claim ownership
what it closes
what it opens
```

不要只加 citation。

# 9. 写回

每 run：
- 对应 experiment card
- raw大文件留节点；git写 hash/path/summary
- PAIN_LOG 只记真实 P##
- CLAIMS 只记 evidence-backed C##
- logs/YYYY-MM-DD.md
- small commit/push

每次新 experiment 先写 card / amendment，再跑。

# 10. 什么时候人审

- E11出现明确 actionable aliasing且 history baseline仍失败；
- E14出现跨objective/task的 behavior imprint；
- E13出现 stable explicit/implicit regime boundary；
- E09说明 negative真正 load-bearing role；
- E06/E07形成 cross-task regime law；
- C## 到 L2；
- 需要改变 ACTIVE 资源调度；
- 两条 broad mine都被强近邻/简单baseline吸收。

汇报只需：
1. E## / commit / artifact hash
2. 最重要数字 + CI / train-seed variance
3. 这个结果解决了哪个 **problem question**
4. 排除哪些平凡解释
5. 最近 direct neighbor pressure
6. 下一组最便宜决定性实验
7. 真正需要人决定的事

**不要把工程进度当科研进度。**
