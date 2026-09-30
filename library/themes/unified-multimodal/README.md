# 理解与生成 / 多模态（Unified multimodal understanding & generation）

**范围：** 理解与生成：统一多模态模型（同一模型既理解又生成）、VLM、视觉 token 压缩、多模态推理的中间表示。
**更新：** 2026-09-30（按题材重组；内容从 `KEY_PAPERS.md`、`TERRITORY_BANK.md`、`deep/` 迁移或索引而来，未改写）。

## 1. 热度（`tools/venue_corpus`，顶会 main 接收数；ICLR 括号内为切片接收率 / 全会基准）

正则：`unified (multimodal )?(models?|understanding and generation)|understanding and generation`（粗筛，数字是量级参考）

| NeurIPS2024 | ICLR2025 | ICML2025 | NeurIPS2025 | ICLR2026 | ICML2026 | ACL2025 | EMNLP2025 | ACL2026 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 23 | 31（41% / 基准 32%） | 10 | 49 | 66（34% / 基准 27%） | 49 | 14 | 11 | 15 |

## 2. Territory 笔记

（原 `TERRITORY_BANK.md` 中没有单独条目；见下方深读材料与 `search/our-taste/TERRITORY_SCAN_2026-09-30.md`。）

## 3. 关键论文与本目录文件

- （暂无；新精读的论文卡放在本目录）

## 4. 深读材料：`library/deep/` 中与本题材相关的章节

- [`deep/academic/GENEALOGIES_03.md`](../../deep/academic/GENEALOGIES_03.md)
  - LINEAGE 10 — VLM：从“把 vision 接进 LLM”到“视觉信息在 LLM 内到底应以什么生命周期存在”
  - LINEAGE 11 — Multimodal Reasoning：text 作为默认 reasoning medium 开始被重新审视
- [`deep/academic/GENEALOGIES_04.md`](../../deep/academic/GENEALOGIES_04.md)
  - LINEAGE 15 — Vision-Language Pretraining Objective：从“选 contrastive 还是 generative”到“一个模型怎样同时保留不同任务需要的信息”
  - 19. 四条新 lineage的交叉分析
- [`deep/industry/GENEALOGIES_03.md`](../../deep/industry/GENEALOGIES_03.md)
  - INDUSTRY GENEALOGY I14 — From “general multimodal understanding” to action-centric world understanding
- [`deep/industry/FRONTIER_DEEP_DIVE.md`](../../deep/industry/FRONTIER_DEEP_DIVE.md)
  - 9. Google DeepMind — video understanding becomes active perception
- [`deep/open-artifacts/GENEALOGIES_07_FAILURE_SCALE_CONTINUAL_STRUCTURED.md`](../../deep/open-artifacts/GENEALOGIES_07_FAILURE_SCALE_CONTINUAL_STRUCTURED.md)
  - S76 — Spatial/3D foundation models place geometry in different parts of the system
- [`deep/open-artifacts/GENEALOGIES_11_FINAL_FRONTIER_WAVE.md`](../../deep/open-artifacts/GENEALOGIES_11_FINAL_FRONTIER_WAVE.md)
  - S113 — Adding a new modality: full integration, parameter separation, or frozen-backbone extension are competing abstractions
  - S124 — Multimodal systems may need different prediction horizons for different modalities
  - S125 — Structured perception: the basic evidence unit can be a set of observed states, not one observation

## 5. 博客 / 报告（`../../sources/BLOGS_REPORTS.md`）

- B14 — Lilian Weng — What are Diffusion Models?

## 6. 最新 arXiv 入口

- [Purshow/Awesome-Unified-Multimodal](https://github.com/Purshow/Awesome-Unified-Multimodal)
- [OpenEnvision/Awesome-Multimodal-Modeling](https://github.com/OpenEnvision/Awesome-Multimodal-Modeling)
- [friedrichor/Awesome-Multimodal-Papers](https://github.com/friedrichor/Awesome-Multimodal-Papers)
- 全题材通用：`../../sources/AWESOME_LISTS.md`（awesome 列表、daily-arXiv 镜像、PaperNotes、spotlight 归档）
