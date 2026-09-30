# MoE 与路由（MoE / routing）

**范围：** MoE 与路由：路由决策、专家特化、路由效用。
**更新：** 2026-09-30（按题材重组；内容从 `KEY_PAPERS.md`、`TERRITORY_BANK.md`、`deep/` 迁移或索引而来，未改写）。

## 1. 热度（`tools/venue_corpus`，顶会 main 接收数；ICLR 括号内为切片接收率 / 全会基准）

正则：`mixture[- ]of[- ]experts|\bMoE\b`（粗筛，数字是量级参考）

| NeurIPS2024 | ICLR2025 | ICML2025 | NeurIPS2025 | ICLR2026 | ICML2026 | ACL2025 | EMNLP2025 | ACL2026 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 40 | 51（35% / 基准 32%） | 42 | 81 | 92（26% / 基准 27%） | 147 | 23 | 22 | 37 |

## 2. Territory 笔记（原 `TERRITORY_BANK.md`）

### T05 — MoE / sparse routing / structured decisions

**Why keep inhabiting it**

Routing is a clean place to study the gap between **scores, surrogates, discrete Top-K decisions, specialization, and downstream utility**.

**Recurring assumptions**

- router score ranks true expert utility;
- pairwise preference implies Top-K adoption;
- load balance and specialization are aligned;
- better local route value necessarily improves generation.

**Natural observations**

- decision-consistency failures;
- outside-set competitors;
- expert specialization across training;
- route utility vs router logits;
- downstream sensitivity to route interventions.

**High-risk failure mode**

Good diagnostic signal → endless loss search.

**Anchors:** MOE01–MOE03; repository observation `../../../workbench/moe-route-preference/README.md`.

## 3. 关键论文与本目录文件

- [`KEY_PAPERS.md`](KEY_PAPERS.md)

## 4. 深读材料：`library/deep/` 中与本题材相关的章节

- [`deep/industry/GENEALOGIES_03.md`](../../deep/industry/GENEALOGIES_03.md)
  - INDUSTRY GENEALOGY I15 — Frontier models optimize across multiple sparsity axes

## 6. 最新 arXiv 入口

- 全题材通用：`../../sources/AWESOME_LISTS.md`（awesome 列表、daily-arXiv 镜像、PaperNotes、spotlight 归档）

## 7. 本仓库相关 workbench / 历史

- `workbench/moe-route-preference/`
- `archive/candidates/CT03_COUNTERFACTUAL_CREDIT_MOE_ROUTING/`
