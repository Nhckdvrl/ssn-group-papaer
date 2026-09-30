# 推理与测试时计算（Reasoning / test-time compute）

**范围：** 推理能力与测试时计算：CoT、采样/搜索/验证、计算分配、隐式推理、CoT 忠实性与可监控性。
**更新：** 2026-09-30（按题材重组；内容从 `KEY_PAPERS.md`、`TERRITORY_BANK.md`、`deep/` 迁移或索引而来，未改写）。

## 1. 热度（`tools/venue_corpus`，顶会 main 接收数；ICLR 括号内为切片接收率 / 全会基准）

正则：`(test[- ]time (scaling|compute)|chain[- ]of[- ]thought|latent reasoning|reasoning models?)`（粗筛，数字是量级参考）

| NeurIPS2024 | ICLR2025 | ICML2025 | NeurIPS2025 | ICLR2026 | ICML2026 | ACL2025 | EMNLP2025 | ACL2026 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 39 | 55（31% / 基准 32%） | 58 | 296 | 357（30% / 基准 27%） | 320 | 77 | 160 | 213 |

## 2. Territory 笔记（原 `TERRITORY_BANK.md`）

### T02 — Reasoning / test-time compute as a policy

**Why keep inhabiting it**

The field moved from “does more reasoning help?” to **where, when, and how compute should be spent**.

**Recurring assumptions**

- more samples are uniformly useful;
- every reasoning step has equal marginal value;
- final-answer verification is enough;
- problem difficulty can be treated as a single scalar;
- explicit CoT is the only useful computation carrier.

**Natural observations**

- failure onset;
- marginal value of additional branches;
- compute allocation by state;
- search/verification disagreement;
- when extra computation stops helping.

**High-risk failure mode**

Another adaptive-compute heuristic with no new scientific object.

**Anchors:** RS01–RS04, PT05, B08–B09.

## 3. 关键论文与本目录文件

- [`KEY_PAPERS.md`](KEY_PAPERS.md)

## 4. 深读材料：`library/deep/` 中与本题材相关的章节

- [`deep/academic/GENEALOGIES_01.md`](../../deep/academic/GENEALOGIES_01.md)
  - LINEAGE 1 — RLVR：从“RL 能否激发 reasoning”到“到底什么 learning signal 在起作用”
  - LINEAGE 2 — Test-Time Scaling：从“多采样”到“何时、哪里、以什么 policy 花 compute”
- [`deep/academic/GENEALOGIES_03.md`](../../deep/academic/GENEALOGIES_03.md)
  - LINEAGE 11 — Multimodal Reasoning：text 作为默认 reasoning medium 开始被重新审视
- [`deep/academic/GENEALOGIES_04.md`](../../deep/academic/GENEALOGIES_04.md)
  - LINEAGE 17 — CoT Faithfulness：从“CoT看起来合理吗”到“到底要用什么 intervention定义 faithful”
- [`deep/industry/GENEALOGIES_03.md`](../../deep/industry/GENEALOGIES_03.md)
  - INDUSTRY GENEALOGY I11 — Reasoning effort: from inference knob to trained conditional policy
- [`deep/industry/FRONTIER_DEEP_DIVE.md`](../../deep/industry/FRONTIER_DEEP_DIVE.md)
  - 3. OpenAI — GPT-6 Astra: CoT monitorability changed premise
- [`deep/open-artifacts/GENEALOGIES_05.md`](../../deep/open-artifacts/GENEALOGIES_05.md)
  - S49 — Extra compute outside language reveals the true abstraction: an operator, not "reasoning"
  - S54 — Cross-domain synthesis: test-time compute only has meaning relative to error cost
  - S55 — "Thinking" is becoming a dangerously overloaded product word

## 5. 博客 / 报告（`../../sources/BLOGS_REPORTS.md`）

- B08 — Nathan Lambert / Interconnects — A taxonomy for next-generation reasoning models
- B09 — Nathan Lambert / Interconnects — 2025 year in review

## 6. 最新 arXiv 入口

- [EIT-NLP/Awesome-Latent-CoT](https://github.com/EIT-NLP/Awesome-Latent-CoT)
- [YU-deep/Awesome-Latent-Space](https://github.com/YU-deep/Awesome-Latent-Space)
- [multimodal-art-projection/LatentCoT-Horizon](https://github.com/multimodal-art-projection/LatentCoT-Horizon)
- 全题材通用：`../../sources/AWESOME_LISTS.md`（awesome 列表、daily-arXiv 镜像、PaperNotes、spotlight 归档）

## 7. 本仓库相关 workbench / 历史

- `archive/good/L12_REASONING_DECISION_INVARIANCE/`
- `archive/candidates/L29_COT_CONTROL_GAIN/`
- `archive/candidates/L44_REASONING_AUTOMATICITY/`
