# Latent World Model Planning — 紧凑世界模型的表示、动力学与决策可靠性

## 状态

**PROPOSED / literature-hardened / execution-ready / no GPU results。**  
2026-10-02 已完成多轮 literature + code hardening：不再把“prediction ≠ planning”当主旨；已建立 paper lineage、problem×method map、claim ownership、code audit、oracle decomposition，以及可直接交给本地 agent 的实验程序。

**科学 claim 仍为 0。** I## 都是可被实验否定的 mining seeds，不是结论。状态保持 PROPOSED，不自动占用现有 ACTIVE-MAIN / ACTIVE-EXPLORE。

**目标会议：** ICLR / ICML / NeurIPS；视觉贡献足够时考虑 CVPR。  
**资源边界：** [RESOURCES](../../RESOURCES.md)：多独立 GPU 槽位、弱互联/弱 I/O；优先单卡/单节点、checkpoint 复用、多 seed/多环境并行，不做跨节点大训练。

## 本地 agent 阅读顺序

1. [FIELD_PROBLEM_MAP_2026](FIELD_PROBLEM_MAP_2026.md)：**全领域 problem map / saturation map**，先理解社区真正关心什么、哪些 broad story 已拥挤。
2. [PAPER_LINEAGE](PAPER_LINEAGE.md)：P01–P94，重点是 mother question、idea leap、决定性实验、related-work distance 和 claim ownership。
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

**2026-10-02 第二轮 hardening 后：** 当前不是“哪个 component 还能改”，而是优先追三个 field-level pressures。详见 [FIELD_PROBLEM_MAP_2026](FIELD_PROBLEM_MAP_2026.md) 与 [RESEARCH_MINES](RESEARCH_MINES.md)。

### M3 / I09 — behavior trajectories ≠ environment controllability（**Tier A1 / first pilot**）

RC-aux / Bai-Xiong Temporal-Distance JEPA 从 offline trajectory 的 order/gap/cross samples 学 reachability/progress。Broad “behavior statistics ≠ optimal control” 已被 quasimetric GCRL、CGCIVL、PLDM占据；我们的 exact pressure 是：

> **真实改变 generating behavior policy，在尽量匹配 local transition support 与 conditional action excitation 后，planning-aware latent WM 是否仍把 higher-order behavior route / tempo 写进 deployed planning semantics，并改变同一 test candidate 的 ordering / MPC？**

第一 gate：E14。OGBench公开的 `navigate/stitch/explore`、`play/noisy`只用于 cheap sensitivity；真正 identification 需要 fixed start-goal 的 DIRECT vs DETOUR/LOOP matched data，并显式匹配/审计 P94 指出的 conditional action covariance / excitation。

### M2 / I08 — predictive-computation placement（**Tier A2 / second pilot**）

TMLR 2026 JEPA-WM study 已明确区分 explicit rollout 与 implicit predictive representation，并把 training/inference/generalization trade-off 的 direct comparison 留作 future direction。2026 的 Universal Horizon / Jumpy WM 等又说明这其实是一个 continuum，而不是二分。

我们问：

> **task/query information、reward/goal shift、horizon、data coverage、dynamics shift、training compute、deployment compute，能否预测 explicit / arbitrary-horizon / implicit / hybrid 哪类 predictive object 更合适？**

第一 matched pilot：E13，优先 OGBench Cube pixels。重要 confound：Bagatella TD-JEPA official eval做 reward inference（约10k replay samples并用 OGBench `physics` relabel），而 image-goal MPC拿 goal observation；**task/query information budget必须单独记账。**

### M1 / I07 — observable goal ≠ control belief（**Tier B / conditional**）

Physically Viable WM、FIRM-WM、UWM-JEPA、Branch-JEPA、Flow Equivariant WM、Action-Sufficient Goal Representations 已经占了大量 broad hidden-state / belief / multimodal-future space。因此只保留更窄的问题：

> **给定 planner 实际拥有的 finite observation-action history 后，是否仍有多个 action-relevant hidden hypotheses，导致真实 best-action flip 和 baseline planner regret？**

E11只做 cheap oracle。finite history能消掉 ambiguity 就 STOP，不造 belief method。

### I06 / I03

- **I06 / E08–E10**：M3 的 heuristic-negative 子诊断，不再因为便宜就默认做主论文。
- **I03 / E06–E07**：三条 mine 共用 oracle/bottleneck 工具；只有形成跨 task predictive regime law 才独立升级。

### WATCH

Goal/query interface、test-time adaptation、latent actions、efficiency 都重要，但 2026 已非常拥挤；当前作为 stress axes / baselines，不单独抢题。

## 执行图

```text
                    E00 resource/native smoke
                              ↓
                E01 baseline + replay/logger
                 ↙             ↓               ↘
       E14 M3 first       E13 M2 second       E11 M1 conditional
       behavior policy    compute placement    ambiguity oracle
           ↓                   ↓                    ↓
     conditional E15      regime confirm       conditional E12
           ↘
     E08 → E09 → E10   (M3 negative-role subdiagnostic)

E02/E06 = common decision/oracle calibration
E03/E04 = VOID
E05 = conditional diagnostic only
```

**多卡用途：** 第一轮每条只做 cheapest decisive pilot；哪条先出现 natural failure + decision consequence + clean intervention leverage，再把独立 GPU 大面积铺 seeds / regimes / environments / nearest baselines。

## 论文形态卡

- **当前主旨：** 尚未形成；science claim = 0。
- **当前 problem mines：** **Tier A1 M3/I09 behavior→controllability semantics；Tier A2 M2/I08 predictive-computation placement；Tier B M1/I07 irreducible actionable ambiguity。** I06=M3子诊断，I03=共享oracle/regime工具。
- **可接受形态：** 新的 actionable failure/distinction；跨 regime law；由诊断自然导出的 minimal repair / hybrid principle；或能改变方法设计的 identification result。
- **不可接受形态：** RC-aux+loss、再测一次 false negative、单个 toy anomaly、普通 correlation、更多seed/benchmark。
- **manuscript-critical contributions：** ❌ 等 E14/E13/E11 proof-of-problem；只有过 gate 的 mine 才继续长 claim/method。
- **证据目标：** strong native reproduction；pair/candidate-level oracle；fixed-candidate regret；closed-loop consequence；train-seed variance；至少两个方法/任务后再扩大。
- **危险近邻：** RC-aux、Bai/Xiong Temporal-Distance JEPA、quasimetric/CGCIVL/PLDM、Controlled-WM Identifiability P94（M3）；Bagatella TD-JEPA、Universal Horizon、Jumpy WM、TD-MPC2（M2）；FIRM-WM、UWM-JEPA、Physically Viable WM、Branch-JEPA（M1）；以及 DA-LeWM/D-JEPA、Control Theory、Hidden Failure Modes 等共享近邻。
- **目标会议：** ICLR / ICML / NeurIPS；不因模型小降低问题尺度。

## D1–D6

| 项目 | 当前 |
|---|---|
| D1 强基线 | ❌ 本地未运行；E00/E01预注册 |
| D2 可复用资产 | ⚠️ LeWM/RC-aux/TD-JEPA/stable-worldmodel等官方代码与pin已审；执行机下载/hash待填 |
| D3 痛点 | ⚠️ literature/code risks已登记；真实 P## = 0 |
| D4 系统测量 | ⚠️ common oracle/candidate schema + E02/E06/E08 + M1–M3 cards E11–E15 已设计；GPU结果=0 |
| D5 定位 | ✅ FIELD_PROBLEM_MAP + P01–P94 lineage / venue/code/read-depth ledger；执行中继续滚动扫最新近邻 |
| D6 idea组合 | ✅ **M3/I09 Tier A1、M2/I08 Tier A2、M1/I07 Tier B conditional**；I06=M3子诊断，I03=共享regime工具；I01/I02 PARKED，I05由I07 supersede；E03/E04 pre-run VOID |

## 决策记录

- 2026-10-02：登记 PROPOSED，资源条件写入根目录。
- 2026-10-02：第一轮调查不足，继续深挖。
- 2026-10-02：建立并持续扩展 paper lineage / ownership / oracle maps；generic support-drift I02 PARKED。
- 2026-10-02：**代码级审计否定原 I01 identification design**：short-window loss看不到“只改长 episode factorization”的treatment；E03/E04未运行即 VOID。
- 2026-10-02：由 Bai/Xiong Temporal-Distance JEPA / RC-aux negative sampler + false-negative limitation/ablation + CGCIVL邻域，生成 I06；注册 E08–E10。
- 2026-10-02：进一步按 **problem-led / actionable** 标准重构 mining：新增 M1/I07、M2/I08、M3/I09；I06降为M3子诊断。
- 2026-10-02：第二轮 proceedings/arXiv hardening 扩到 **P01–P94**；Physically Viable WM / Branch-JEPA / UWM / FIRM 等使 broad M1明显更拥挤，故降为 conditional；OGBench generator/code audit 与 explicit↔implicit native-protocol audit 后，优先级改为 **M3 → M2 → M1 conditional**。
- 2026-10-02：**P94 Controlled-WM Identifiability** 进一步压缩 M3：behavior policy 的 conditional action excitation 已被证明会决定 transition identification/counterfactual planning，因此 E14 只有在 excitation + local support 已控制后，higher-order trajectory semantics 仍留下 decision imprint 才有独立空间。
- 未经人审不改变 ACTIVE 容量；执行 agent可在 experiment-card 决策范围内自主继续，不需要每个job回来问。

## 资产位置

大数据/checkpoint/raw candidate traces不进git；节点路径、revision/hash写 [ASSETS](ASSETS.md)。git只保存代码、manifest、实验卡、摘要和主张账本。

**执行入口：** [LOCAL_AGENT_PROMPT.md](LOCAL_AGENT_PROMPT.md) → E00/E01 → **E14 first**, E13 second, E11 conditional；dataset可读后 E08 可作为 M3 子诊断并行。