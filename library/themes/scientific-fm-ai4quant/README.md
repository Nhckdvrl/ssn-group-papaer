# 科学基础模型与 AI4Quant（Scientific FMs / AI4Quant）

**范围：** 科学基础模型（基因组、分子、表格、时间序列）与 AI4Quant。
**更新：** 2026-09-30（按题材重组；内容从 `KEY_PAPERS.md`、`TERRITORY_BANK.md`、`deep/` 迁移或索引而来，未改写）。

## 1. 热度（`tools/venue_corpus`，顶会 main 接收数；ICLR 括号内为切片接收率 / 全会基准）

正则：`(foundation models? for (genomics|molecul|materials|time series|tabular)|time[- ]series foundation|tabular foundation|genomic (language|foundation)|quantitative (finance|trading))`（粗筛，数字是量级参考）

| NeurIPS2024 | ICLR2025 | ICML2025 | NeurIPS2025 | ICLR2026 | ICML2026 | ACL2025 | EMNLP2025 | ACL2026 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 | 6（17% / 基准 32%） | 15 | 22 | 25（27% / 基准 27%） | 37 | 0 | 0 | 0 |

## 2. Territory 笔记（原 `TERRITORY_BANK.md`）

### T11 — AI4Quant / structured multivariate models

Current repository territories:
- `../../../workbench/ai4quant/territories/state-coverage-vs-exposure-coverage.md`
- `../../../workbench/ai4quant/territories/forecast-skill-vs-structural-skill.md`

Use finance only when it supplies a load-bearing structural oracle, intervention, or decision consequence—not merely a new dataset.

## 3. 关键论文与本目录文件

- （暂无；新精读的论文卡放在本目录）

## 4. 深读材料：`library/deep/` 中与本题材相关的章节

- [`deep/industry/FRONTIER_DEEP_DIVE.md`](../../deep/industry/FRONTIER_DEEP_DIVE.md)
  - 13. OpenAI GPT-Rosalind — scientific evaluation shifts from question answering to executed research workflow
- [`deep/open-artifacts/GENEALOGIES_02.md`](../../deep/open-artifacts/GENEALOGIES_02.md)
  - S13 — Tabular foundation models are converging on synthetic SCM priors, but disagree on the computation unit
  - S14 — Time-series foundation models can make intermediate checkpoints part of the training objective
- [`deep/open-artifacts/GENEALOGIES_05.md`](../../deep/open-artifacts/GENEALOGIES_05.md)
  - S47 — Tabular foundation models: synthetic prior → in-context predictor → fit-time computation
  - S50 — TimesFM-3 is the opposite lesson: put cross-variable computation into the forward pass
- [`deep/open-artifacts/GENEALOGIES_06_SCIENTIFIC_FM.md`](../../deep/open-artifacts/GENEALOGIES_06_SCIENTIFIC_FM.md)
  - S59 — Genomic FM design exposes a three-way conflict: sequence length, supervision resolution, and biological function
  - S60 — Carbon: coarse tokenization creates a supervision-resolution problem
  - S61 — JEPA-DNA: token reconstruction may be the wrong semantic target
  - S62 — Carbon vs JEPA-DNA: two different answers to "what should DNA pretraining learn?"
  - S63 — NASA–IBM Lunar FM: known nuisance variables should not always be inferred from pixels
  - S64 — Genos-m: specialization changes the prior over biological diversity
  - S65 — Botanic1: architecture should match the sequence process, not the dominant ML fashion
  - S66 — Domain structure can enter at five distinct places
  - S67 — A useful scientific-FM pattern: known nuisance vs unknown signal
  - S68 — Another useful pattern: scientific tokenization is a claim about invariance
  - S69 — Research-instrument value is unusually high in scientific FMs
  - S70 — Scientific FM anti-patterns
  - S71 — Current conclusion
- [`deep/open-artifacts/GENEALOGIES_07_FAILURE_SCALE_CONTINUAL_STRUCTURED.md`](../../deep/open-artifacts/GENEALOGIES_07_FAILURE_SCALE_CONTINUAL_STRUCTURED.md)
  - S75 — Molecular foundation models: representation is only half the system
- [`deep/open-artifacts/GENEALOGIES_08_SCIENTIFIC_EXPERIENCE_AND_STATE.md`](../../deep/open-artifacts/GENEALOGIES_08_SCIENTIFIC_EXPERIENCE_AND_STATE.md)
  - S82 — Scientific code → executable experience
  - S83 — Scientific interaction → dual adaptation of harness and model
  - S84 — Scientific codebases can become environments in different ways
  - S85 — Scientific world model: unify the predictive principle, not necessarily the raw modality
  - S86 — Unified token space vs native structural evidence
  - S87 — Discovery Foundation Models: agenda vs validated object
  - S88 — New scientific-FM taxonomy: where does the domain's causal structure enter?
  - S89 — A new warning: "unification" can happen at different layers
  - S90 — Research-instrument audit for this batch
  - S91 — Current conclusion

## 6. 最新 arXiv 入口

- 全题材通用：`../../sources/AWESOME_LISTS.md`（awesome 列表、daily-arXiv 镜像、PaperNotes、spotlight 归档）

## 7. 本仓库相关 workbench / 历史

- `workbench/ai4quant/`
