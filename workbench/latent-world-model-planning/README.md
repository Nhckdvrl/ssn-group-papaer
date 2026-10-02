# Latent World Model Planning — 紧凑世界模型的表示、动力学与决策可靠性

## 状态

**PROPOSED / literature-hardened / execution-ready / no GPU results。**  
2026-10-02 已完成多轮 literature + code hardening：不再把“prediction ≠ planning”当主旨；已建立 paper lineage、problem×method map、claim ownership、code audit、oracle decomposition，以及可直接交给本地 agent 的实验程序。

**科学 claim 仍为 0。** I## 都是可被实验否定的 mining seeds，不是结论。状态保持 PROPOSED，不自动占用现有 ACTIVE-MAIN / ACTIVE-EXPLORE。

**目标会议：** ICLR / ICML / NeurIPS；视觉贡献足够时考虑 CVPR。  
**资源边界：** [RESOURCES](../../RESOURCES.md)：多独立 GPU 槽位、弱互联/弱 I/O；优先单卡/单节点、checkpoint 复用、多 seed/多环境并行，不做跨节点大训练。

## 本地 agent 阅读顺序

1. [FIELD_PROBLEM_MAP_2026](FIELD_PROBLEM_MAP_2026.md)：**全领域 problem map / saturation map**，先理解社区真正关心什么、哪些 broad story 已拥挤。
2. [PAPER_LINEAGE](PAPER_LINEAGE.md)：P01–P92，重点是 mother question、idea leap、决定性实验、related-work distance 和 claim ownership。
3. [RESEARCH_MINES](RESEARCH_MINES.md)：**problem-led 主入口**；从 related-work tension 选 pressure region，不从某个 loss 出发找钉子。
4. [LITERATURE_LEDGER](LITERATURE_LEDGER.md)：阅读深度、venue 状态、代码 readiness、何时必须回原文。
5. [PROBLEM_METHOD_MAP](PROBLEM_METHOD_MAP.md)：data→representation→dynamics→metric→search→time→execution 七层图与 oracle ladder。
6. [POSITIONING](POSITIONING.md)：顶会锚点、2026 collision map、红区、当前 mining regions。
7. [EXPERIMENT_PROGRAM](EXPERIMENT_PROGRAM.md)：shared substrate、gates、并行策略、统计卫生。
8. [LOCAL_AGENT_PROMPT](LOCAL_AGENT_PROMPT.md)：直接给执行机 agent。
9. [ASSETS](ASSETS.md)：repo / checkpoint / data / protocol / 资源风险。
10. [HANDOFF](HANDOFF.md)：最短执行路线。
11. [CLAIMS](CLAIMS.md) / [PAIN_LOG](PAIN_LOG.md)：只有真实实验才升级。

第一轮 [LATENT_PLANNING_SURVEY](../../library/themes/video-world-models/LATENT_PLANNING_SURVEY.md) 保留作来源索引；当前领域判断以 **FIELD_PROBLEM_MAP_2026 / PAPER_LINEAGE / RESEARCH_MINES / POSITIONING** 为准。

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

## 当前 problem-led mining program

**2026-10-02 再校准：** workbench 不再由某个局部 objective（例如 heuristic negatives）定义。我们先问领域级真实问题，再把 loss/probe 当定位工具。最新调查以 [RESEARCH_MINES](RESEARCH_MINES.md) 为主入口。

### M1 / I07 — Observable goal ≠ control state：partial observability 下的 belief-aware visual planning

核心不是“多给历史帧”，而是：**image goal 只描述可观测配置，但最优动作可能取决于不可见的 velocity / contact / friction / regime。** FIRM-WM 已占 goal/dynamic factorization，UWM-JEPA 已占 belief-space prediction；我们的空间只能是把 observation aliasing 压到 **candidate action regret + closed-loop planning**，并找出 deterministic history 何时足够、何时 explicit belief / uncertainty 才 load-bearing。

第一 gate：E11。若只是 probe 变化而动作不变，直接停。

### M2 / I08 — Explicit rollout vs implicit predictive abstraction

TMLR 2026 *What Drives Success in Physical Planning with JEPA-WMs?* 已明确区分 explicit autoregressive WM 与 Bagatella **TD-JEPA** 式 implicit long-horizon predictive representation，并把 training/inference/generalization trade-off 的直接比较留作 future work。

我们不做 leaderboard，而问：**reward/goal shift、dynamics/layout shift、horizon、data coverage、deployment search budget 等变量能否形成可预测的 explicit/implicit/hybrid regime boundary？**

第一 matched pilot：E13。注意 Bagatella TD-JEPA 与 Bai/Xiong Temporal-Distance JEPA 是两篇不同工作。

### M3 / I09 — Dataset-induced planning semantics：behavior trajectory ≠ environment controllability

RC-aux / Bai-Xiong Temporal-Distance JEPA 从 offline trajectory 的 order/gap/negative 学 reachability/progress。Quasimetric GCRL、CGCIVL、PLDM 已告诉我们 broad data bias 不是新概念；真正未决的是：**planning-aware WM 是否把 behavior policy 的 route/tempo 写进 deployed planning semantics，并改变 MPC candidate ranking 与闭环控制？**

旧 I01/E03–E04 已因“只重切长 episode、short-window loss不可见”而 VOID。新 E14 必须真的改变 behavior policy / pair distribution，而不是换 metadata。

### I06 — semantic negatives vs geometric regularization：降为 M3 的低成本 slice

E08/E09/E10 仍保留，因为它能便宜地审 heuristic negative 的 semantic role 与 global repulsion role；但**它不再因为文档最完整就自动成为论文主旨**。只有出现能解释更大 data-semantics / planning failure 的机制时才升级。

### I03 — bottleneck regime law：共享诊断，不先当 paper

E06/E07 保留为 oracle ladder / regime mapping。如果它最终发现少数变量能跨 task 预测 binding bottleneck 和 intervention ranking，才可能自己升级；否则只是帮助 M1–M3 定位问题。

### WATCH

Goal/query interface 与 model reuse 很重要，但 P38 *What Must a World Model Distinguish for Planning?* 和 Grounded World Model 已非常直接；当前作为所有方法的 transfer stress axis，不单独抢题。

## 执行图

```text
                    E00 resource/native smoke
                              ↓
                E01 baseline + replay/logger
                 ↙            ↓             ↘
       E11 M1 aliasing     E14 M3 behavior     E13 M2 explicit↔implicit
       decision oracle     policy intervention  matched regime pilot
           ↓                    ↓                    ↓
     conditional E12      conditional E15        regime confirmation
                                ↘
                         E08/E09 I06 subdiagnostic

E02/E06 = common decision/oracle calibration
E03/E04 = VOID（旧 treatment 对 short-window loss 结构上不可见）
E05 = conditional diagnostic only
```

**多卡的用途：** 一条 mine 过了 proof-of-problem gate 后，再迅速铺 seeds / regimes / environments / baselines；不是同时把三个 mine 都跑成巨型 Cartesian grid。

## 论文形态卡

- **当前主旨：** 尚未形成；science claim = 0。
- **当前 problem mines：** M1/I07 belief-aware observation aliasing；M2/I08 explicit↔implicit predictive abstraction；M3/I09 behavior→controllability semantics。I06 是 M3 的低成本机制 slice，I03 是共享 oracle/regime 工具。
- **可接受形态：** 新的 actionable failure/distinction；跨 regime law；由诊断自然导出的 minimal repair / hybrid principle；或能改变方法设计的 identification result。
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
| D5 定位 | ✅ P01–P74 + venue/code/read-depth ledger；执行中继续滚动扫最新近邻 |
| D6 idea组合 | ✅ problem-led M1/I07、M2/I08、M3/I09；I06降为M3子诊断，I03为共享regime工具；I01/I02 PARKED，I05由I07 supersede；E03/E04 pre-run VOID |

## 决策记录

- 2026-10-02：登记 PROPOSED，资源条件写入根目录。
- 2026-10-02：第一轮调查不足，继续深挖。
- 2026-10-02：建立 P01–P74 lineage / ownership / oracle maps；generic support-drift I02 PARKED。
- 2026-10-02：**代码级审计否定原 I01 identification design**：short-window loss看不到“只改长 episode factorization”的treatment；E03/E04未运行即 VOID。
- 2026-10-02：由 Bai/Xiong Temporal-Distance JEPA / RC-aux negative sampler + false-negative limitation/ablation + CGCIVL邻域，生成 I06；注册 E08–E10。
- 2026-10-02：进一步按 **problem-led / actionable** 标准重构 mining：新增 M1/I07 observation-aliasing→belief planning、M2/I08 explicit↔implicit frontier、M3/I09 behavior→controllability semantics；I06降为M3子诊断，不再默认主论文。
- 未经人审不改变 ACTIVE 容量；执行 agent可在 experiment-card 决策范围内自主继续，不需要每个job回来问。

## 资产位置

大数据/checkpoint/raw candidate traces不进git；节点路径、revision/hash写 [ASSETS](ASSETS.md)。git只保存代码、manifest、实验卡、摘要和主张账本。

**执行入口：** [LOCAL_AGENT_PROMPT.md](LOCAL_AGENT_PROMPT.md) → E00；dataset可读后 E08 可与 E01/E02并行。