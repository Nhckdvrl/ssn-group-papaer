# VLA 与具身智能（VLA / embodied）

**范围：** 视觉-语言-动作模型、动作表示与分块、具身预训练与适配。
**更新：** 2026-09-30（按题材重组；内容从 `KEY_PAPERS.md`、`TERRITORY_BANK.md`、`deep/` 迁移或索引而来，未改写）。

## 1. 热度（`tools/venue_corpus`，顶会 main 接收数；ICLR 括号内为切片接收率 / 全会基准）

正则：`vision[- ]language[- ]action|\bVLAs?\b`（粗筛，数字是量级参考）

| NeurIPS2024 | ICLR2025 | ICML2025 | NeurIPS2025 | ICLR2026 | ICML2026 | ACL2025 | EMNLP2025 | ACL2026 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 5 | 7（58% / 基准 32%） | 5 | 33 | 58（35% / 基准 27%） | 76 | 1 | 7 | 7 |

## 2. Territory 笔记（原 `TERRITORY_BANK.md`）

### T08 — VLA / action representation / embodied control

**Why keep inhabiting it**

Robotics turns sequence-model design into a closed-loop question. Action interface, chunking, tokenization, control frequency, feedback delay, and multimodality all become load-bearing.

**Recurring assumptions**

- one-step actions are the natural output;
- text-like tokenization is adequate for continuous control;
- larger chunks always reduce compounding error;
- semantic pretraining transfers cleanly to action;
- offline action quality predicts closed-loop behavior.

**Natural observations**

- action representation bottlenecks;
- chunk horizon vs feedback;
- tokenization failure at high frequency;
- open-loop vs closed-loop gaps;
- transfer across embodiments/action spaces.

**High-risk failure mode**

Data collection and benchmark construction become the paper.

**Anchors:** VLA01–VLA05.

## 3. 关键论文与本目录文件

- [`KEY_PAPERS.md`](KEY_PAPERS.md)

## 4. 深读材料：`library/deep/` 中与本题材相关的章节

- [`deep/academic/GENEALOGIES_01.md`](../../deep/academic/GENEALOGIES_01.md)
  - LINEAGE 5 — Robotics / VLA：成功的 action abstraction 怎样不断制造下一代问题
- [`deep/industry/GENEALOGIES_02.md`](../../deep/industry/GENEALOGIES_02.md)
  - INDUSTRY GENEALOGY I8 — Deployment constraint → representation/training objective
- [`deep/industry/GENEALOGIES_03.md`](../../deep/industry/GENEALOGIES_03.md)
  - INDUSTRY GENEALOGY I14 — From “general multimodal understanding” to action-centric world understanding
- [`deep/industry/FRONTIER_DEEP_DIVE.md`](../../deep/industry/FRONTIER_DEEP_DIVE.md)
  - 12. Mistral — Robostral Navigate: embodiment invariance is designed into the action representation
- [`deep/open-artifacts/GENEALOGIES_02.md`](../../deep/open-artifacts/GENEALOGIES_02.md)
  - S15 — Robotics pretraining value is being redefined
- [`deep/open-artifacts/GENEALOGIES_03.md`](../../deep/open-artifacts/GENEALOGIES_03.md)
  - S27 — Robot pretraining value: initialization → adaptation mode
  - S28 — Robotics adaptation is already splitting into several channels
- [`deep/open-artifacts/GENEALOGIES_05.md`](../../deep/open-artifacts/GENEALOGIES_05.md)
  - S48 — Test-time compute in robotics: spend computation before irreversible action
- [`deep/open-artifacts/GENEALOGIES_10_LONG_HORIZON_STATE_AND_CORRECTION.md`](../../deep/open-artifacts/GENEALOGIES_10_LONG_HORIZON_STATE_AND_CORRECTION.md)
  - S111 — Current conclusion
- [`deep/open-artifacts/GENEALOGIES_11_FINAL_FRONTIER_WAVE.md`](../../deep/open-artifacts/GENEALOGIES_11_FINAL_FRONTIER_WAVE.md)
  - S111 — Robot pretraining value decomposes: peak task learning, environment transfer, and in-context task learning are different claims

## 6. 最新 arXiv 入口

- 全题材通用：`../../sources/AWESOME_LISTS.md`（awesome 列表、daily-arXiv 镜像、PaperNotes、spotlight 归档）
