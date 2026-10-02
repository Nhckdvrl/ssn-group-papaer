# Latent World Model Planning — 紧凑世界模型的表示、动力学与决策可靠性

## 状态

**PROPOSED / literature-hardened / execution-ready / no GPU results。**  
2026-10-02 已完成多轮 literature + code hardening：不再把“prediction ≠ planning”当主旨；已建立 paper lineage、problem×method map、claim ownership、code audit、oracle decomposition，以及可直接交给本地 agent 的实验程序。

**科学 claim 仍为 0。** I## 都是可被实验否定的 mining seeds，不是结论。状态保持 PROPOSED，不自动占用现有 ACTIVE-MAIN / ACTIVE-EXPLORE。

**目标会议：** ICLR / ICML / NeurIPS；视觉贡献足够时考虑 CVPR。  
**资源边界：** [RESOURCES](../../RESOURCES.md)：多独立 GPU 槽位、弱互联/弱 I/O；优先单卡/单节点、checkpoint 复用、多 seed/多环境并行，不做跨节点大训练。

## 本地 agent 阅读顺序

1. [NOVELTY_GROWTH_RULES](NOVELTY_GROWTH_RULES.md)：**硬规则：有近邻 ≠ 没空间；只允许 atomic claim 被占，不允许一篇 paper 封锁整个 research program。**
2. [FIELD_PROBLEM_MAP_2026](FIELD_PROBLEM_MAP_2026.md)：全领域 problem map；看社区关心什么、不同工作在回答母问题的哪一部分。
3. [RESEARCH_PROGRAMS](RESEARCH_PROGRAMS.md)：R1–R5 五个持续 research programs，是最高层科研入口。
4. [PAPER_LINEAGE](PAPER_LINEAGE.md)：P01–P113，重点是 mother question、idea leap、决定性实验、related-work distance 和 atomic claim ownership。
5. [RESEARCH_MINES](RESEARCH_MINES.md)：把 R1–R5 转成 6 个可实验 seeds；seed失败不关闭 program。
6. [LITERATURE_LEDGER](LITERATURE_LEDGER.md)：阅读深度、venue 状态、代码 readiness、何时必须回原文。
7. [PROBLEM_METHOD_MAP](PROBLEM_METHOD_MAP.md)：data→representation→dynamics→metric→search→time→execution 七层图与 oracle ladder。
8. [POSITIONING](POSITIONING.md)：顶会锚点、2026 collision map、红区、当前 mining regions。
9. [EXPERIMENT_PROGRAM](EXPERIMENT_PROGRAM.md)：shared substrate、gates、并行策略、统计卫生。
10. [LOCAL_AGENT_PROMPT](LOCAL_AGENT_PROMPT.md)：直接给执行机 agent。
11. [ASSETS](ASSETS.md)：repo / checkpoint / data / protocol / 资源风险。
12. [HANDOFF](HANDOFF.md)：最短执行路线。
13. [CLAIMS](CLAIMS.md) / [PAIN_LOG](PAIN_LOG.md)：只有真实实验才升级。

第一轮 [LATENT_PLANNING_SURVEY](../../library/themes/video-world-models/LATENT_PLANNING_SURVEY.md) 保留作来源索引；当前领域判断以 **FIELD_PROBLEM_MAP_2026 / PAPER_LINEAGE / RESEARCH_MINES / POSITIONING** 为准。

## 为什么这个 territory 值得驻留

不是因为“小模型好跑”。DINO-WM、PLDM、Temporal Straightening、RC-aux 等已经证明 compact latent planning 的 representation、geometry、data、dynamics 与 planner interface 是顶会级母问题。2026 又快速出现 SALT、DA-LeWM、AD-WM、Planning Limits、Control Theory of Predictability、Traj-LeWM、CGS、Do-JEPA、FIRM-WM 等，说明领域活跃但**普通增量已高度拥挤**。

对我们的资源，这里有一个很稀缺的优势：**模型小 + offline trajectories + 可重置 simulator + planner candidates可观察**。因此几十张独立 GPU 可以用来做受控干预、多 seed、candidate audit、oracle replacement 和跨任务确认，而不需要高速多节点同步。

## 已建立的原子 claim：不能单独当 headline，但完全可以成为更大新 story 的 ingredient

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

## 当前 research programs

**2026-10-02 第三轮校准：** 不再把 workbench 压成几个“剩余空白”。近邻密集说明母问题重要；我们在 program 内通过不同 seeds 找自己的 novelty。详见 [RESEARCH_PROGRAMS](RESEARCH_PROGRAMS.md)。

### R1 — Data & Identifiability：什么经验让 world model 真正可规划？
已有 PLDM、P94、quasimetric/IEL、RC-aux、Do-JEPA/FIRM、Task-Sufficient WM 等分别回答 data regime、action excitation、hitting-time geometry、counterfactual branches、active probing。

**这不是关闭理由，而是一个完整 research program。**

当前 seeds：
- **I09/E14**：behavior-route / trajectory-semantics imprint；
- **I12/E16**：equal-budget data value，比较 coverage / excitation / route diversity / counterfactual branches；
- **I06/E08–E10**：semantic negatives 只是一个局部机制。

### R2 — Predictive Abstraction：world model 到底应该预测什么？
LeWM / SALT / Branch/Flow / Universal Horizon / Bagatella TD-JEPA / Jumpy WM / HWM / hybrid methods 形成 continuum：

\`\`\`text
one-step → direct horizon → distribution/path → successor/occupancy → macro/hierarchy → amortized/hybrid
\`\`\`

**I08/E13** 是入口：先找 horizon/query/compute/data regime 下 predictive object 的相对优势，不把它写成两方法排行榜。

### R3 — Specialization vs Reuse：world model 应该多 task-specific？
Value Equivalence、Goal-Aware Prediction、P38、WorldTest、Rank-One Corner、Task-Sufficient WM、Grounded WM都证明这个母问题重要。

**I10/E17**：控制 query information进入 representation / dynamics / metric / proposal 的位置，研究 seen-query decision efficiency 与 unseen-query reuse 的 frontier。

### R4 — State / Belief / Active Information
FIRM、UWM-JEPA、Branch-JEPA、Physically Viable WM、Flow Equivariant WM不是“堵死”这条线，而是证明 hidden state / belief / physical identifiability 是真实问题。

**I07/E11** 是最便宜 existence probe；若短 history 能解决，只淘汰当前 seed，R4 可继续转 active disambiguation / risk-aware planning / hidden-physics identification。

### R5 — Trust / Repair / Bypass：什么时候该相信 imagination？
PLDM uncertainty、MEND、IMWM、AdaJEPA、Feedback WM、AdaReP、Planning Limits 等提供不同 recovery actions，但没有统一回答：

> 检测到哪种 failure 时，应该 replan、shorten horizon、adapt、feedback-correct、increase search，还是 fallback？

**I11/E18**：先做 recovery-action oracle，再看 reliability signals是否能预测 intervention ranking。

## 当前 6 个活跃 seeds

| Seed | Program | Pilot |
|---|---|---|
| I09 behavior-route semantics | R1 | E14 |
| I12 data value for planning | R1 | E16 |
| I08 predictive-object frontier | R2 | E13 |
| I10 query specialization/reuse | R3 | E17 |
| I07 actionable belief ambiguity | R4 | E11 |
| I11 trust/recovery routing | R5 | E18 |

I03/E06–E07、I06/E08–E10、E02 是共享 diagnostics。  
**seed 被近邻吸收或 pilot 否掉，只 park seed，不关闭 R#。**

## 执行图

\`\`\`text
                    E00 / E01 shared substrate
                             ↓
           ┌─────────────────┼──────────────────┐
           │                 │                  │
      Wave A            Wave B              conditional
  E14 (R1 seed)     E13 (R2 seed)          E11 (R4)
  E18 (R5 seed)     E17 (R3 seed)             │
      │                 │                     │
  E08 cheap diag     next regime          next R4 seed
      │
  if R1 strongest → E16 equal-budget data value

E02 / E06 = common candidate + bottleneck oracle
\`\`\`

仓库通用规则仍是**同时实际跑的 pilot ≤2**。Wave A 先取最高 information-gain 的两个；拿到结果后立即更新 program map，再启动下一组。

**多卡用途：** pilot只用少量卡分科学分支；某个 program出现 natural failure / surprising boundary / strong method lever 后，再迅速铺 seeds × regimes × environments × nearest baselines。

## 论文形态卡

- **当前主旨：** 尚未形成；science claim = 0。
- **当前 programs：** R1 data/identifiability；R2 predictive abstraction；R3 specialization/reuse；R4 state/belief；R5 trust/recovery。当前6个 seeds = I07–I12（其中 I09/I08/I07为旧线重解释，I10–I12为新增）。
- **可接受形态：** 新的 actionable failure/distinction；跨 regime law；由诊断自然导出的 minimal repair / hybrid principle；或能改变方法设计的 identification result。
- **不可接受形态：** RC-aux+loss、再测一次 false negative、单个 toy anomaly、普通 correlation、更多seed/benchmark。
- **manuscript-critical contributions：** ❌；目前处于 program mining。E14/E18/E13/E17/E11/E16 的任务是让 paper narrative 从真实结果中生长。
- **证据目标：** strong native reproduction；pair/candidate-level oracle；fixed-candidate regret；closed-loop consequence；train-seed variance；至少两个方法/任务后再扩大。
- **危险近邻：** RC-aux、Bai/Xiong Temporal-Distance JEPA、quasimetric/CGCIVL/PLDM、Controlled-WM Identifiability P94（M3）；Bagatella TD-JEPA、Universal Horizon、Jumpy WM、TD-MPC2（M2）；FIRM-WM、UWM-JEPA、Physically Viable WM、Branch-JEPA（M1）；以及 DA-LeWM/D-JEPA、Control Theory、Hidden Failure Modes 等共享近邻。
- **目标会议：** ICLR / ICML / NeurIPS；不因模型小降低问题尺度。

## D1–D6

| 项目 | 当前 |
|---|---|
| D1 强基线 | ❌ 本地未运行；E00/E01预注册 |
| D2 可复用资产 | ⚠️ LeWM/RC-aux/TD-JEPA/stable-worldmodel等官方代码与pin已审；执行机下载/hash待填 |
| D3 痛点 | ⚠️ literature/code risks已登记；真实 P## = 0 |
| D4 系统测量 | ⚠️ common oracle/candidate schema + E02/E06/E08；program pilots E11–E18 已注册；GPU结果=0 |
| D5 定位 | ✅ FIELD_PROBLEM_MAP + P01–P113 lineage / venue/code/read-depth ledger；执行中继续滚动扫最新近邻 |
| D6 idea组合 | ✅ R1–R5 research programs + 6 active seeds（I07–I12）；I03/I06为diagnostics；I01/I02 PARKED，I05由I07 supersede；E03/E04 pre-run VOID |

## 决策记录

- 2026-10-02：登记 PROPOSED，资源条件写入根目录。
- 2026-10-02：第一轮调查不足，继续深挖。
- 2026-10-02：建立并持续扩展 paper lineage / ownership / oracle maps；generic support-drift I02 PARKED。
- 2026-10-02：**代码级审计否定原 I01 identification design**：short-window loss看不到“只改长 episode factorization”的treatment；E03/E04未运行即 VOID。
- 2026-10-02：由 Bai/Xiong Temporal-Distance JEPA / RC-aux negative sampler + false-negative limitation/ablation + CGCIVL邻域，生成 I06；注册 E08–E10。
- 2026-10-02：进一步按 **problem-led / actionable** 标准重构 mining：新增 M1/I07、M2/I08、M3/I09；I06降为M3子诊断。
- 2026-10-02：第二轮 proceedings/arXiv hardening 扩到 **P01–P113**；Physically Viable WM / Branch-JEPA / UWM / FIRM 等使 broad M1明显更拥挤，故降为 conditional；OGBench generator/code audit 与 explicit↔implicit native-protocol audit 后，优先级改为 **M3 → M2 → M1 conditional**。
- 2026-10-02：**P94 Controlled-WM Identifiability** 进一步压缩 M3：behavior policy 的 conditional action excitation 已被证明会决定 transition identification/counterfactual planning，因此 E14 只有在 excitation + local support 已控制后，higher-order trajectory semantics 仍留下 decision imprint 才有独立空间。
- 2026-10-02：**第三轮校准：正式取消“近邻越多→题越窄”的逻辑。** 新增 NOVELTY_GROWTH_RULES 与 R1–R5 RESEARCH_PROGRAMS；atomic claim可被占，parent program不能被单篇工作自动关闭；新增 I10–I12 / E16–E18。
- 未经人审不改变 ACTIVE 容量；执行 agent可在 experiment-card 决策范围内自主继续，不需要每个job回来问。

## 资产位置

大数据/checkpoint/raw candidate traces不进git；节点路径、revision/hash写 [ASSETS](ASSETS.md)。git只保存代码、manifest、实验卡、摘要和主张账本。

**执行入口：** [LOCAL_AGENT_PROMPT.md](LOCAL_AGENT_PROMPT.md) → E00/E01 → Wave A（E14 + E18，最多2个pilot）→ Wave B（E13 + E17）→ 按 program 证据触发 E11/E16；E08可低成本并行诊断。