# 视频生成与世界模型（Video / world models）

**范围：** 可交互视频世界模型、real-time causalization / distillation、控制与响应、长程记忆 / persistent state、world-model evaluation、紧凑 latent world model 与规划。  
**更新：** 2026-10-02（seam-specific 主线降级；新主线切到 real-time conversion capability preservation）。

## Problem map

| Problem axis | 领域真正关心的问题 | 代表工作 |
|---|---|---|
| **Control / responsiveness** | 新 action 能否及时、准确、细粒度生效 | Astra；Vid2World；ActionSplice；ForgeWM |
| **Long-horizon memory / persistence** | 离开后再回来，场景/物体/状态是否仍然存在 | Long-Context SSM；WorldMem；WorldPlay；Infinite-World |
| **Real-time conversion** | bidirectional / multi-step video model 如何变 causal few-step 而不过度损失能力 | Self Forcing；MotionStream；Causal Forcing；ForgeWM |
| **Geometry / physics / state** | 世界是否维护空间结构、动态状态和物理后果 | PlayWorld；WorldArena；Cloning Deterministic Worlds |
| **General interaction** | navigation、subject action、event editing、perspective switching | WBench；WorldPlay2 |
| **Efficiency** | 固定 memory / KV / sparse attention 下维持质量与交互 | Yume1.5；WorldPlay2；近期 sparse/KV work |

**校准：problem-driven 完全可以是顶会工作，但 problem 必须对应 world model 的 load-bearing capability。** 实现级 anomaly 只有在能解释/损伤这些能力时才有 paper scale。

## 当前 territories
- **ACTIVE-MAIN：[`real-time-causalization-capability-preservation`](../../../workbench/real-time-causalization-capability-preservation/)**  
  完整调查：[`REALTIME_CAUSALIZATION_SURVEY.md`](REALTIME_CAUSALIZATION_SURVEY.md)
- **PROPOSED：[`latent-world-model-planning`](../../../workbench/latent-world-model-planning/)**  
  保留原调查：[`LATENT_PLANNING_SURVEY.md`](LATENT_PLANNING_SURVEY.md)
- **PAUSED diagnostic asset：[`video-world-model-temporal-interfaces`](../../../workbench/video-world-model-temporal-interfaces/)**

## Method / ownership map
- **Vid2World (ICLR 2026)**：video diffusion causalization 的宽故事。
- **Self Forcing (NeurIPS 2025 Spotlight)**：self-rollout / train-test gap。
- **MotionStream (ICLR 2026)**：bidirectional teacher → causal streaming student + real-time rollout。
- **Causal Forcing (ICML 2026)**：bidirectional teacher 与 AR student 的 architectural gap。
- **Astra (ICLR 2026)**：history memory 与 responsiveness 的 trade-off。
- **ForgeWM (2608.14022)**：Stage 0/1/2/3 progressive recipe + stage-wise inference ablation。
- **ActionSplice (2609.08230)**：chunk sampling 中途 action retargeting。
- **WBench / PlayWorld / R2M-Bench**：evaluation 向 interaction adherence、persistent state、closed-loop objective、relative-memory controls 发展。

因此新主线不能只是“causalization 会掉点”“stage 分数不同”或“chunk action responsiveness 有问题”；必须进一步做到 capability-specific、factorized attribution、cross-lineage / counterexample-aware。

## Evaluation map
- **视觉**：quality / temporal artifact / consistency
- **控制**：action sign、gain、trajectory error、short-event fidelity、response latency
- **长期状态**：revisit relative consistency、persistent object/state、rollout drift
- **交互**：multi-turn adherence / closed-loop objective
- **系统**：FPS、first-frame latency、steady-state latency、VRAM / KV growth
- **公平性**：同 scene/action/noise 可配对时优先 paired；避免 self-calibration 掩盖过/欠响应

## 资源边界
见根目录 `RESOURCES.md`。优先公开 stage checkpoints、frozen inference、大量横向 measurement；1B–8B 单卡/单节点优先。多张卡用于 stage × scene × seed × metric 的独立并行，不从零训练 foundation world model。

## 深读
- [`REALTIME_CAUSALIZATION_SURVEY.md`](REALTIME_CAUSALIZATION_SURVEY.md)
- [`LATENT_PLANNING_SURVEY.md`](LATENT_PLANNING_SURVEY.md)
- `library/deep/academic/GENEALOGIES_04.md`
- `library/deep/open-artifacts/GENEALOGIES_10_LONG_HORIZON_STATE_AND_CORRECTION.md`
- `library/deep/open-artifacts/GENEALOGIES_11_FINAL_FRONTIER_WAVE.md`
