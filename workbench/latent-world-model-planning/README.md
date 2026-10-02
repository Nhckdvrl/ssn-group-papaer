# Latent World Model Planning — 紧凑世界模型的表示、动力学与决策可靠性

## 状态

**PROPOSED / literature-hardened / execution-ready / no GPU results。**  
2026-10-02 已完成多轮 literature + code hardening：不再把“prediction ≠ planning”当主旨；已建立 paper lineage、problem×method map、claim ownership、code audit、oracle decomposition，以及可直接交给本地 agent 的实验程序。

**科学 claim 仍为 0。** I## 都是可被实验否定的 mining seeds，不是结论。状态保持 PROPOSED，不自动占用现有 ACTIVE-MAIN / ACTIVE-EXPLORE。

**目标会议：** ICLR / ICML / NeurIPS；视觉贡献足够时考虑 CVPR。  
**资源边界：** [RESOURCES](../../RESOURCES.md)：多独立 GPU 槽位、弱互联/弱 I/O；优先单卡/单节点、checkpoint 复用、多 seed/多环境并行，不做跨节点大训练。

## 本地 agent 阅读顺序

1. [PAPER_LINEAGE](PAPER_LINEAGE.md)：P01–P64 直接/邻接工作，重点是 mother question、idea leap、决定性实验、related-work distance 和 claim ownership。
2. [LITERATURE_LEDGER](LITERATURE_LEDGER.md)：阅读深度、venue 状态、代码 readiness、何时必须回原文。
3. [PROBLEM_METHOD_MAP](PROBLEM_METHOD_MAP.md)：data→representation→dynamics→metric→search→time→execution 七层图与 oracle ladder。
4. [POSITIONING](POSITIONING.md)：顶会锚点、2026 collision map、红区、当前 mining regions。
5. [EXPERIMENT_PROGRAM](EXPERIMENT_PROGRAM.md)：shared substrate、gates、并行策略、统计卫生。
6. [LOCAL_AGENT_PROMPT](LOCAL_AGENT_PROMPT.md)：直接给执行机 agent。
7. [ASSETS](ASSETS.md)：repo / checkpoint / data / protocol / 资源风险。
8. [HANDOFF](HANDOFF.md)：最短执行路线。
9. [CLAIMS](CLAIMS.md) / [PAIN_LOG](PAIN_LOG.md)：只有真实实验才升级。

第一轮 [LATENT_PLANNING_SURVEY](../../library/themes/video-world-models/LATENT_PLANNING_SURVEY.md) 保留作来源索引；当前领域判断以 PAPER_LINEAGE / LEDGER / PROBLEM_METHOD_MAP / POSITIONING 为准。

## 为什么这个 territory 值得驻留

不是因为“小模型好跑”。DINO-WM、PLDM、Temporal Straightening、RC-aux 等已经证明 compact latent planning 的 representation、geometry、data、dynamics 与 planner interface 是顶会级母问题。2026 又快速出现 SALT、DA-LeWM、AD-WM、Planning Limits、Control Theory of Predictability、Traj-LeWM、CGS、Do-JEPA、FIRM-WM 等，说明领域活跃但**普通增量已高度拥挤**。

对我们的资源，这里有一个很稀缺的优势：**模型小 + offline trajectories + 可重置 simulator + planner candidates可观察**。因此几十张独立 GPU 可以用来做受控干预、多 seed、candidate audit、oracle replacement 和跨任务确认，而不需要高速多节点同步。

## 红区：只能当 baseline / measurement

- predictive accuracy ≠ planning quality；
- latent L2 ≠ real progress；
- representation中有信息但objective不会用；
- generic reachability / temporal distance；
- generic multi-step/open-loop training；
- inverse dynamics / physical grounding；
- generic action discrimination；
- generic path-aware cost；
- generic CEM proposal / subgoal / hierarchy；
- generic planner-reachable/off-support model exploitation；
- generic long-horizon failure；
- generic closed-loop evaluation / OOD robustness。

详见 [POSITIONING](POSITIONING.md)。

## 当前 mining 优先级

### I06 — Semantic negatives or geometric repulsion?（**第一优先**）

这是深挖论文 + 代码后留下的最具体 tension。

TD-JEPA：
- 把 random cross-trajectory/batch goals推到 temporal-distance margin外；
- 原文**明确承认 reachable false negatives**；
- 但 published ablation 中去掉 cross-trajectory hinge 又系统伤 planning。

RC-aux：
- batch/cross-trajectory goals直接得到 reachability 0-label；
- temporal hard negatives已经负责 budget identifiability；
- pinned code中的 cross negatives同样只是 batch permutation，不检查 environment connectivity。

CGCIVL (ICML 2025) 又明确说明 trajectory identity 不等于 connected/unconnected；标准 contrastive negatives也并不等价于逐pair声明“不可达”。

因此真正的问题是：

> **这些 heuristic negatives 的规划收益，到底来自正确的 reachability/distance semantics，还是来自 non-semantic global repulsion / scale / dispersion regularization？**

执行：
- **E08**：零训练 semantic audit；
- **E09**：FULL / no-negative / oracle-valid / count-matched / repulsion decomposition；
- **E10**：只有 E09 支持 role conflation 才做 oracle-free role separation。

这条线的最低顶会形态不是“发现 false negatives”，而是 **new distinction + mechanism reattribution + planning consequence + role-separated repair**。

### I03 — Bottleneck relocation / regime law（**第二优先**）

各近期论文已经分别把瓶颈归因到 metric、dynamics、counterfactual action distinction、search、replanning-time index、horizon/target。我们不再做方法排名，而用 oracle ladder问：

> goal distance、candidate margin、planner-reachable fidelity、replanning ratio 等少数变量，能否跨任务预测哪个 layer 成为 binding bottleneck，并预测哪种 intervention 有效？

E06 → E07。没有跨任务 predictive variable 就不升级。

### PARKED

- **I01 trajectory-factorization / route imprinting：PARKED。** 代码审计发现 pinned TD-JEPA/RC-aux 主要监督只读取短 loaded windows；若保持这些 windows完全相同、只改更长 episode factorization，loss几乎看不到 treatment。E03/E04 已在运行前 VOID。
- **I02 optimizer support drift：PARKED。** P40 已直接 formalize planner-reachable/off-manifold divergence，再加经典 offline MBRL，generic story太近。
- **I05 history/POMDP：PARKED。**

I04 仍只是 E02 decision-alignment calibration，不独立抢主线。

## 执行图

```text
E00 resource/native smoke
  ↓
E01 baseline parity + logger + replay/oracle harness
  ├──────────────→ E08 zero-training negative semantics audit
  ↓
E02 known decision-alignment calibration
  ├─ E09 → E10   I06 primary
  └─ E06 → E07   I03 secondary

E03/E04 = VOID (pre-run, invalidated by code audit)
E05 = conditional diagnostic only
```

每张有效卡都有阳性对照、MIE、混杂和 stop/go 条件。卡多用于**加速决定性比较和 confirmatory evidence**，不是铺满 Cartesian product。

## 论文形态卡

- **当前主旨：** 尚未形成；science claim = 0。
- **最强 seed：** I06，来源于 published limitation + published ablation + implementation semantics + offline GCRL邻域，而不是空白猜测。
- **可接受形态：** 重新归因+minimal repair；新 failure/identification；跨 regime law + adaptive principle。
- **不可接受形态：** RC-aux+loss、再测一次 false negative、单个 toy anomaly、普通 correlation、更多seed/benchmark。
- **manuscript-critical contributions：** ❌ 等 E08–E10 / E06–E07。
- **证据目标：** strong native reproduction；pair/candidate-level oracle；fixed-candidate regret；closed-loop consequence；train-seed variance；至少两个方法/任务后再扩大。
- **危险近邻：** TD-JEPA、RC-aux、CGCIVL/QRL、DA-LeWM/AD-WM、Temporal Straightening/CGS、Control Theory、Hidden Failure Modes、Planning Limits。
- **目标会议：** ICLR / ICML / NeurIPS；不因模型小降低问题尺度。

## D1–D6

| 项目 | 当前 |
|---|---|
| D1 强基线 | ❌ 本地未运行；E00/E01预注册 |
| D2 可复用资产 | ⚠️ LeWM/RC-aux/TD-JEPA/stable-worldmodel等官方代码与pin已审；执行机下载/hash待填 |
| D3 痛点 | ⚠️ literature/code risks已登记；真实 P## = 0 |
| D4 系统测量 | ⚠️ candidate/oracle schema + E02/E06–E10已设计；GPU结果=0 |
| D5 定位 | ✅ P01–P64 + venue/code/read-depth ledger；执行中继续滚动扫最新近邻 |
| D6 idea组合 | ✅ I06/I03/I04 SEED；I01/I02/I05 PARKED；E03/E04 pre-run VOID |

## 决策记录

- 2026-10-02：登记 PROPOSED，资源条件写入根目录。
- 2026-10-02：第一轮调查不足，继续深挖。
- 2026-10-02：建立 P01–P64 lineage / ownership / oracle maps；generic support-drift I02 PARKED。
- 2026-10-02：**代码级审计否定原 I01 identification design**：short-window loss看不到“只改长 episode factorization”的treatment；E03/E04未运行即 VOID。
- 2026-10-02：由 TD-JEPA/RC-aux negative sampler + TD-JEPA false-negative limitation/ablation + CGCIVL邻域，生成 I06；注册 E08–E10，升级为第一优先 mining lane。
- 未经人审不改变 ACTIVE 容量；执行 agent可在 experiment-card 决策范围内自主继续，不需要每个job回来问。

## 资产位置

大数据/checkpoint/raw candidate traces不进git；节点路径、revision/hash写 [ASSETS](ASSETS.md)。git只保存代码、manifest、实验卡、摘要和主张账本。

**执行入口：** [LOCAL_AGENT_PROMPT.md](LOCAL_AGENT_PROMPT.md) → E00；dataset可读后 E08 可与 E01/E02并行。