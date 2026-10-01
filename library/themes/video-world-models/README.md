# 视频生成与世界模型（Video / world models）

**范围：** 视频生成、可交互世界模型、分块/因果化生成、控制接口、长程一致性；潜在世界模型与目标条件规划。
**更新：** 2026-10-02（新增紧凑 latent planning 调查；旧深读材料与统计保留）。

## 1. 热度（`tools/venue_corpus`，顶会 main 接收数；ICLR 括号内为切片接收率 / 全会基准）

正则：`(world models?|video generation|video diffusion)`（粗筛，数字是量级参考）

| NeurIPS2024 | ICLR2025 | ICML2025 | NeurIPS2025 | ICLR2026 | ICML2026 | ACL2025 | EMNLP2025 | ACL2026 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 75 | 106（39% / 基准 32%） | 63 | 160 | 196（35% / 基准 27%） | 181 | 6 | 7 | 17 |

上述为既有宽切片统计，不代表 latent planning 的独立热度或接收率；本轮未重新运行 venue corpus。

## 2. Territory 笔记

- [紧凑潜在世界模型与规划 territory](../../../search/our-taste/LATENT_WORLD_MODEL_PLANNING.md)：单卡／单节点独立实验、共享模型与环境、保留多个研究分支。
- 其他既有方向见深读材料与 `search/our-taste/TERRITORY_SCAN_2026-09-30.md`。

## 3. 关键论文与本目录文件

- [LATENT_PLANNING_SURVEY.md](LATENT_PLANNING_SURVEY.md)：系统调查、相邻领域比较、五条谱系、核心论文卡、claim ownership、压力地图和逐篇阅读范围。更新到 2026-09-28 的直接后续；不是已复现报告。

## 4. 深读材料：`library/deep/` 中与本题材相关的章节

- [`deep/academic/GENEALOGIES_04.md`](../../deep/academic/GENEALOGIES_04.md)
  - LINEAGE 18 — Video / World Models：从“生成未来画面”到“什么 latent variable真正承载可迁移 dynamics”
- [`deep/open-artifacts/GENEALOGIES_01.md`](../../deep/open-artifacts/GENEALOGIES_01.md)
  - STARTUP GENEALOGY S04 — World model: video prediction → persistent state → action operator → deployable simulator
- [`deep/open-artifacts/GENEALOGIES_02.md`](../../deep/open-artifacts/GENEALOGIES_02.md)
  - S16 — "World model" is fragmenting by downstream contract
  - S17 — World-model papers are beginning to ask which property is actually load-bearing
- [`deep/open-artifacts/GENEALOGIES_04.md`](../../deep/open-artifacts/GENEALOGIES_04.md)
  - S38 — Multiplayer world models introduce shared hidden state
  - S39 — World-model fidelity → decision fidelity
- [`deep/open-artifacts/GENEALOGIES_10_LONG_HORIZON_STATE_AND_CORRECTION.md`](../../deep/open-artifacts/GENEALOGIES_10_LONG_HORIZON_STATE_AND_CORRECTION.md)
  - S102 — Long-horizon streaming geometry: local uncertainty → slow global drift
  - S103 — Persistent world state: local observation history → global latent state
  - S104 — Long-form autoregressive failure: intervene at onset, not globally
- [`deep/open-artifacts/GENEALOGIES_11_FINAL_FRONTIER_WAVE.md`](../../deep/open-artifacts/GENEALOGIES_11_FINAL_FRONTIER_WAVE.md)
  - S112 — World-model quality is defined by the consumer contract, not one universal fidelity metric

## 6. 最新 arXiv 入口

- 全题材通用：`../../sources/AWESOME_LISTS.md`（awesome 列表、daily-arXiv 镜像、PaperNotes、spotlight 归档）

## 7. 本仓库相关 workbench / 历史

- [video-world-model-temporal-interfaces](../../../workbench/video-world-model-temporal-interfaces/)：已有视频控制接口主线，状态以 workbench 登记表为准。
- [latent-world-model-planning](../../../workbench/latent-world-model-planning/)：2026-10-02 新登记 PROPOSED，不更改已有 ACTIVE 调度。执行入口为其 HANDOFF／E00。
- [资源与基础设施边界](../../../RESOURCES.md)：用户确认的多卡、弱互联／弱 I/O 条件。
