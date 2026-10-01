# Latent World Model Planning — 紧凑世界模型的表示、动力学与决策可靠性

## 状态

**PROPOSED / literature-hardened / execution-ready / no GPU results。**  
用户要求把这里建设成可直接交给本地 agent 驻留、广泛实验、持续挖 idea 的 workbench。2026-10-02 已完成第二轮深挖：不再把“prediction ≠ planning”当主旨，而是建立 paper lineage、problem×method map、claim ownership、oracle decomposition、4 个活跃 SEED + 1 个 PARKED seed、E00–E07 决定性实验程序。

**没有成立的科学主张。** 下面的 I## 是有文献来源、可被实验否定的探索种子，不是论文结论。状态仍为 PROPOSED；不自动占用现有 ACTIVE-MAIN / ACTIVE-EXPLORE。

**目标会议：** ICLR / ICML / NeurIPS；若最终贡献以视觉表示/机器人视觉为核心再考虑 CVPR。  
**资源边界：** [RESOURCES](../../RESOURCES.md)：多独立 GPU 槽位、弱互联/弱 I/O；优先单卡/单节点、checkpoint 复用、并行评测与多 seed，不做跨节点大训练。

## 入口：本地 agent 按这个顺序读

1. [PAPER_LINEAGE](PAPER_LINEAGE.md)：从 DINO-WM / PLDM / OGBench 到 2026 representation、dynamics、planner、hierarchy、理论/诊断工作的 idea-growth 与 claim ownership。
2. [PROBLEM_METHOD_MAP](PROBLEM_METHOD_MAP.md)：data→representation→dynamics→metric→proposal→time→execution 七层地图、oracle ladder、关键交互。
3. [POSITIONING](POSITIONING.md)：顶会尺度锚点、2026 直接 collision/compression map、不能再当 headline 的红区、三个 surviving regions。
4. [EXPERIMENT_PROGRAM](EXPERIMENT_PROGRAM.md)：共享 substrate、Gate A/B、I01–I04 的 E00–E07、并行策略与统计卫生。
5. [LOCAL_AGENT_PROMPT](LOCAL_AGENT_PROMPT.md)：可直接复制给执行机 agent 的启动提示。
6. [ASSETS](ASSETS.md)：repo / checkpoint / data / protocol / 资源风险。
7. [HANDOFF](HANDOFF.md)：最短执行路线和证据门。
8. [CLAIMS](CLAIMS.md) / [PAIN_LOG](PAIN_LOG.md)：真实实验结果才允许升级。

第一轮调查索引保留在 [LATENT_PLANNING_SURVEY](../../library/themes/video-world-models/LATENT_PLANNING_SURVEY.md)；第二轮 hardening 以后，**PAPER_LINEAGE + PROBLEM_METHOD_MAP + POSITIONING 是领域判断的 authority**。

## 为什么这块值得驻留

它不是“18M 模型容易跑所以做”。母问题已经被 ICML/NeurIPS/ICLR 级工作反复证明重要：latent representation、recursive dynamics、decision metric、search、temporal abstraction 与 offline data structure 都会改变 planning。与此同时，2026 的直接近邻已经非常密集，因此普通 recipe sweep、更多 seed、再加一个 reachability/inverse/multi-step loss 都没有足够 novelty。

这个 workbench 的优势是：小型开源模型 + 可重置 simulator + offline trajectories + planner 内部 candidate 可观测，使我们能**对同一个端到端系统做强干预与 oracle decomposition**；大量独立 GPU 能用于 paired datasets、train seeds、candidate audit、planner budgets 与跨环境确认，而不需要多节点同步。

## 红区：可测，不得直接当新发现

- predictive accuracy ≠ planning quality；
- latent L2 ≠ real progress / candidate quality；
- finite-budget reachability / temporal-distance head；
- generic multi-step/open-loop training；
- inverse dynamics / action consistency；
- generic CEM proposal / subgoal / hierarchy / variable chunks；
- generic long-horizon failure；
- generic OOD robustness；
- “world model 应用 task success 评估”。

直接 ownership 与论文链见 [POSITIONING](POSITIONING.md) 与 [PAPER_LINEAGE](PAPER_LINEAGE.md)。

## 当前最值得挖的三个 region

### R-A / I01 — Behavior-policy geometry contamination（当前第一优先）
RC-aux / TD-JEPA 一类方法从 trajectory order/gap 构造 reachability/progress supervision；offline GCRL 的 quasimetric 工作则明确区分 behavior future statistics 与 optimal goal distance。

真正可成为我们的 delta 的不是“trajectory gap 不是真 shortest path”，而是：

> **在 environment dynamics、local transition support、one-step training samples 被控制时，只改变 behavior path / episode organization，是否会系统改变 trajectory-supervised latent-WM 的 learned planning geometry、candidate ordering 与 closed-loop control？**

E03 用同 raw transitions、同 local window、只改 long-pair metadata 做最干净 identification；E04 再用 shortest-ish / detour / route-mixture 和 navigation oracle 建 behavior→geometry→decision 链。若只 head 变、decision 不变，I01 降级，不包装。

### R-B / I02 — Optimizer-induced support drift
不是重复“offline model exploitation”。要找的是 compact latent CEM 中：

`optimizer iteration → support drift → model optimism → false elite → environment regret`

的完整可重复链，并和 action magnitude、PLDM uncertainty、ACID/MEND 一类 verifier 区分。E05。

### R-C / I03 — Bottleneck relocation / regime
不是方法大排名。E06 的 oracle ladder 分 representation/metric、dynamics、proposal、horizon/target；只有 goal distance / candidate margin / data support 等少数变量能**跨任务预测 bottleneck 与 intervention ranking**，才升级。E07 再做 interaction confirm。

I04 是 DA-LeWM decision-alignment 的 replication/calibration，默认从属于 I02/I03；I05 history/POMDP 已 PARK，等 clean substrate 或实测 history effect 再开。

## 执行图

```text
E00 resource/native smoke
  ↓
E01 baseline parity + candidate logger + replay/oracle harness
  ↓
E02 known decision-alignment replication / measurement calibration
  ├─ E03 → E04     I01 primary
  ├─ E05          I02 independent evaluation lane
  └─ E06 → E07    I03 regime / interaction lane
```

不是要求机械跑完。每张卡都有阳性对照、噪声/MIE、混杂与预先决策表；结果过不了 gate 就停止扩展该 lead，把 GPU 给下一条有信息增益的比较。

## 论文形态卡（当前版本）

- **当前一句话主旨：** 尚未形成，科学 claim = 0；先用强 baseline + oracle decomposition + paired interventions 找 load-bearing mismatch。
- **可接受形态：** 新 failure/identification + minimal repair；新 regime law + adaptive principle；representation/dynamics design + 因果/受控证据。
- **不可接受形态：** benchmark 刷分；“RC-aux + loss”；单个 toy anomaly；普通 correlation；把复现/更多 seed 当贡献。
- **manuscript-critical contributions：** 尚无（❌，等待 E03–E07）。
- **证据目标：** native reproduction；相同 candidate/data manifests；paired environment consequence；≥2 substrates/任务后再扩大；train-seed variance 与 episode CI 分开；必要时 oracle intervention。
- **最危险 compression：** DA-LeWM、RC-aux/TD-JEPA、SALT、Temporal Straightening、IMWM/SAGE/LeFlow、Planning Limits、quasimetric GCRL。
- **目标会议：** ICLR / ICML / NeurIPS；不因模型小降低问题尺度。

## D1–D6

| 项目 | 当前 |
|---|---|
| D1 强基线 | ❌ 未本地运行；E00/E01 已预注册 |
| D2 可复用资产 | ⚠️ 公共 repo/data/checkpoint 入口已核对；本机下载/环境/hash 待 local agent |
| D3 痛点 | ⚠️ 文献/协议风险 R01–R10；真实 P## = 0 |
| D4 系统测量 | ⚠️ candidate/oracle/result schema + E02–E07 已设计；结果 = 0 |
| D5 定位 | ✅ 第二轮 direct-neighbor/ownership hardening 已完成到 2026-10-02；执行中仍要滚动扫最新 arXiv |
| D6 idea 组合 | ✅ I01–I04 SEED，I05 PARKED；每个有来源/近邻/delta/决定性 pilot |

## 决策记录

- 2026-10-02：登记为 PROPOSED，资源条件写入根目录。
- 2026-10-02：第一轮调查不足以直接开实验；继续深挖。
- 2026-10-02：完成 literature hardening。新增完整 lineage / problem-method / positioning / experiment program；把“prediction≠planning”等宽 claim 划入红区；I01 behavior-policy geometry 作为第一优先 mining lane，I02/I03 为独立备选，I04 校准，I05 parked。
- 未经用户/人审，不改变 ACTIVE 容量；本地 agent 被分配此 workbench 时可按 [LOCAL_AGENT_PROMPT](LOCAL_AGENT_PROMPT.md) 自主执行，不需每个实验回来请示。

## 资产位置

代码/权重/数据不进本 repo；真实路径、revision/hash 和可访问地点在执行时写 [ASSETS](ASSETS.md)。raw candidate traces / rollouts 留节点，git 只保存 manifest、摘要、实验卡与结果表。

**执行入口：** [LOCAL_AGENT_PROMPT.md](LOCAL_AGENT_PROMPT.md) → E00。