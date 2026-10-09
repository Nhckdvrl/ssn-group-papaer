# 架构、记忆与长上下文（Architecture / memory / long context）

**范围：** 架构与记忆：循环/混合架构、长上下文与 KV、压缩记忆、稀疏注意力、部署驱动的架构不对称。
**更新：** 2026-09-30（按题材重组；内容从 `KEY_PAPERS.md`、`TERRITORY_BANK.md`、`deep/` 迁移或索引而来，未改写）。

## 1. 热度（`tools/venue_corpus`，顶会 main 接收数；ICLR 括号内为切片接收率 / 全会基准）

正则：`(state space models?|\bmamba\b|linear attention|hybrid (architecture|model)|long[- ]context|KV[- ]cache)`（粗筛，数字是量级参考）

| NeurIPS2024 | ICLR2025 | ICML2025 | NeurIPS2025 | ICLR2026 | ICML2026 | ACL2025 | EMNLP2025 | ACL2026 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 111 | 146（36% / 基准 32%） | 93 | 183 | 201（31% / 基准 27%） | 230 | 70 | 57 | 85 |

## 2. Territory 笔记（原 `TERRITORY_BANK.md`）

### T03 — Iterative / recurrent-depth computation

**Why keep inhabiting it**

Looped and depth-recurrent models reopen a basic architecture assumption: depth normally means distinct parameters. They let us separate **parameter count, number of computation steps, inter-visit state, and explicit vs latent reasoning**.

**Recurring assumptions**

- each additional computation step needs new parameters;
- latent repeated computation behaves like deeper feed-forward computation;
- the full residual stream must cross every visit;
- recurrence naturally preserves a stable “workspace”.

**Natural observations**

- what changes across visits;
- minimum state required between visits;
- task/depth dependence of state demand;
- whether useful computation is reconstructive, persistent, or repeatedly recreated.

**High-risk failure mode**

Synthetic tasks define the mechanism we later “discover”; or incomparable training recipes are treated as architecture-only controls.

**Anchors:** AR06–AR07, AR09, MI05, B02.

### T04 — Memory / long context / knowledge location

**Why keep inhabiting it**

“Memory” now spans several physically different objects: attention KV, recurrent state, compressive memory, test-time learned memory, external retrieval, prompt context, adapters, and runtime-generated state/weights.

**Recurring assumptions**

- compressed state substitutes for exact access;
- retention = accessibility;
- long-context success implies stored information is usable under the same query;
- retrieval, persistent state, and parameter adaptation are interchangeable.

**Natural observations**

- exact vs compressed memory demand;
- what information survives compression;
- when queries become informative enough to retrieve;
- persistence after removing exact context;
- write/read/persistence/interference trade-offs.

**High-risk failure mode**

Rebranding ordinary RAG/KV pruning as “memory science”.

**Anchors:** AR01–AR08, B11–B12.

## 3. 关键论文与本目录文件

- [`KEY_PAPERS.md`](KEY_PAPERS.md)

## 4. 深读材料：`library/deep/` 中与本题材相关的章节

- [`deep/academic/GENEALOGIES_02.md`](../../deep/academic/GENEALOGIES_02.md)
  - LINEAGE 9 — Architecture / Inductive Bias：不是“换 backbone”，而是问 architecture 把什么 computation 变得自然
- [`deep/industry/GENEALOGIES_01.md`](../../deep/industry/GENEALOGIES_01.md)
  - INDUSTRY GENEALOGY I1 — Chat request → agent loop → persistent-state economics
- [`deep/industry/GENEALOGIES_03.md`](../../deep/industry/GENEALOGIES_03.md)
  - INDUSTRY GENEALOGY I15 — Frontier models optimize across multiple sparsity axes
- [`deep/industry/FRONTIER_DEEP_DIVE.md`](../../deep/industry/FRONTIER_DEEP_DIVE.md)
  - 1. OpenAI — GPT-5.6: efficiency stops being a model property
  - 4. DeepSeek-V4.1-Flash — agent workloads create input/output compute asymmetry
- [`deep/open-artifacts/FRONTIER_DEEP_DIVE.md`](../../deep/open-artifacts/FRONTIER_DEEP_DIVE.md)
  - 5. Liquid AI — deployment constraints define the learning problem
  - 10. Zyphra — architecture, hardware stack and non-language foundation models
  - 15. Meituan LongCat — deployment reality moves the sparse-attention bottleneck
- [`deep/open-artifacts/GENEALOGIES_01.md`](../../deep/open-artifacts/GENEALOGIES_01.md)
  - STARTUP GENEALOGY S05 — Global state vs per-observation redundancy
  - STARTUP GENEALOGY S07 — Autoregressive vs diffusion language modeling becomes deployment-mode unification
- [`deep/open-artifacts/GENEALOGIES_07_FAILURE_SCALE_CONTINUAL_STRUCTURED.md`](../../deep/open-artifacts/GENEALOGIES_07_FAILURE_SCALE_CONTINUAL_STRUCTURED.md)
  - S74 — Where should live knowledge live?
- [`deep/open-artifacts/GENEALOGIES_10_LONG_HORIZON_STATE_AND_CORRECTION.md`](../../deep/open-artifacts/GENEALOGIES_10_LONG_HORIZON_STATE_AND_CORRECTION.md)
  - S105 — Four distinct notions of "long-horizon state"
  - S106 — New general distinction: persistent-state design vs correction design
- [`deep/open-artifacts/GENEALOGIES_11_FINAL_FRONTIER_WAVE.md`](../../deep/open-artifacts/GENEALOGIES_11_FINAL_FRONTIER_WAVE.md)
  - S114 — Sparse attention selector training: dense attention is not necessarily the correct teacher
  - S120 — Live data can be compiled into runtime weights: another distinct knowledge location

## 5. 博客 / 报告（`../../sources/BLOGS_REPORTS.md`）

- B02 — Alex L. Zhang — Language Model “Shape” (2026)
- B11 — Google Research — Titans + MIRAS: Helping AI have long-term memory
- B12 — state-spaces/mamba official repository

## 6. 最新 arXiv 入口

- 全题材通用：`../../sources/AWESOME_LISTS.md`（awesome 列表、daily-arXiv 镜像、PaperNotes、spotlight 归档）

## 7. 本仓库相关 workbench / 历史

- `workbench/shape-olmo/`
- `archive/candidates/CT05_EXACT_MEMORY_DEMAND/`
