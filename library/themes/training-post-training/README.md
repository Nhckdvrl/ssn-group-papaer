# 训练：预训练、SFT、蒸馏与 RL 后训练（Training dynamics）

**范围：** 训练动态：预训练数据与缩放、SFT、蒸馏、RLVR/偏好优化、学习信号的来源与副作用。
**更新：** 2026-09-30（按题材重组；内容从 `KEY_PAPERS.md`、`TERRITORY_BANK.md`、`deep/` 迁移或索引而来，未改写）。

## 1. 热度（`tools/venue_corpus`，顶会 main 接收数；ICLR 括号内为切片接收率 / 全会基准）

正则：`\b(RLVR|GRPO|DPO|RLHF|supervised fine[- ]tuning|distillation|pretraining data)\b`（粗筛，数字是量级参考）

| NeurIPS2024 | ICLR2025 | ICML2025 | NeurIPS2025 | ICLR2026 | ICML2026 | ACL2025 | EMNLP2025 | ACL2026 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 201 | 260（37% / 基准 32%） | 180 | 429 | 604（31% / 基准 27%） | 595 | 137 | 170 | 290 |

## 2. Territory 笔记（原 `TERRITORY_BANK.md`）

### T01 — Post-training / learning-signal dynamics

**Why keep inhabiting it**

Modern post-training is no longer just “SFT vs DPO vs RL”. Strong work increasingly asks what the actual learning signal is doing: which samples/tokens update the policy, what the pretrained prior contributes, where calibration/diversity move, and which behaviors are written vs merely elicited.

**Recurring assumptions worth auditing**

- all tokens in a trajectory contribute equally;
- correct and incorrect samples are symmetric learning signals;
- reward unit = optimization unit;
- benchmark gain implies the intended mechanism improved;
- a stage label (SFT/RL/etc.) is itself a scientific variable.

**Baseline / observation first**

Use strong open recipes and checkpoints; inspect learning curves, sample classes, entropy, calibration, behavior retention, and modest recipe perturbations before proposing mechanism.

**High-risk failure mode**

One optimizer / LR / budget trajectory becomes a “law”.

**Anchors:** PT01–PT09, B06–B09.

## 3. 关键论文与本目录文件

- [`KEY_PAPERS.md`](KEY_PAPERS.md)

## 4. 深读材料：`library/deep/` 中与本题材相关的章节

- [`deep/academic/GENEALOGIES_01.md`](../../deep/academic/GENEALOGIES_01.md)
  - LINEAGE 1 — RLVR：从“RL 能否激发 reasoning”到“到底什么 learning signal 在起作用”
- [`deep/academic/GENEALOGIES_02.md`](../../deep/academic/GENEALOGIES_02.md)
  - LINEAGE 6 — Pretraining Scaling：从 N/D/Compute 的光滑规律，到 data composition / repetition / capacity allocation
  - LINEAGE 7 — SFT：从“教会模型怎么回答”到“它到底怎样修改已有 knowledge”
  - LINEAGE 8 — Distillation：从“更强 teacher”到“teacher signal 必须对 student 可学习”
- [`deep/academic/GENEALOGIES_03.md`](../../deep/academic/GENEALOGIES_03.md)
  - LINEAGE 14 — Optimization / SAM：成功方法的“原始解释”本身也会成为后续研究对象
- [`deep/industry/GENEALOGIES_03.md`](../../deep/industry/GENEALOGIES_03.md)
  - INDUSTRY GENEALOGY I12 — Long-horizon RL changes the meaning of an “iteration”
  - INDUSTRY GENEALOGY I16 — Self-evolution: from model-generated data to model-modified training machinery
- [`deep/open-artifacts/FRONTIER_DEEP_DIVE.md`](../../deep/open-artifacts/FRONTIER_DEEP_DIVE.md)
  - 8. OpenBMB MiniCPM5-2B — tiny model, unusually rich post-training artifact
  - 11. Cognition — long-horizon asynchronous coding as the post-training regime
  - 12. Poolside — local agentic coding as a model-design constraint
- [`deep/open-artifacts/GENEALOGIES_01.md`](../../deep/open-artifacts/GENEALOGIES_01.md)
  - STARTUP GENEALOGY S02 — Pretraining data order: randomization stops being a harmless default
  - STARTUP GENEALOGY S08 — Failure memory: from difficulty-aware self-play to diagnosis-aware curriculum
- [`deep/open-artifacts/GENEALOGIES_11_FINAL_FRONTIER_WAVE.md`](../../deep/open-artifacts/GENEALOGIES_11_FINAL_FRONTIER_WAVE.md)
  - S115 — Coverage → residual capability: learner-relative data construction after broad data saturation
  - S123 — An SFT loss mask can silently determine later RL exploration

## 5. 博客 / 报告（`../../sources/BLOGS_REPORTS.md`）

- B06 — Nathan Lambert / Interconnects — A recipe for frontier model post-training
- B07 — Nathan Lambert / Interconnects — The state of post-training in 2025
- B09 — Nathan Lambert / Interconnects — 2025 year in review
- B10 — DAPO project page

## 6. 最新 arXiv 入口

- 全题材通用：`../../sources/AWESOME_LISTS.md`（awesome 列表、daily-arXiv 镜像、PaperNotes、spotlight 归档）

## 7. 本仓库相关 workbench / 历史

- `archive/candidates/S03_GOAL_RELATIVE_STOPPING/`
- `archive/candidates/L19_LONG_TO_SHORT_TRANSFER/`
- `archive/good/L11_TASK_GRADIENT_PRESSURE/`
