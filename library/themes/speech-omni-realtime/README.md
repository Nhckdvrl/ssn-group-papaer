# 语音、全模态与实时交互（Speech / omni / realtime）

**范围：** 语音与全模态模型、全双工/实时交互、语音 tokenizer、快慢系统。
**更新：** 2026-09-30（按题材重组；内容从 `KEY_PAPERS.md`、`TERRITORY_BANK.md`、`deep/` 迁移或索引而来，未改写）。

## 1. 热度（`tools/venue_corpus`，顶会 main 接收数；ICLR 括号内为切片接收率 / 全会基准）

正则：`\b(speech|spoken|full[- ]duplex|audio language model|omni[- ]modal)\b`（粗筛，数字是量级参考）

| NeurIPS2024 | ICLR2025 | ICML2025 | NeurIPS2025 | ICLR2026 | ICML2026 | ACL2025 | EMNLP2025 | ACL2026 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 45 | 55（30% / 基准 32%） | 30 | 69 | 71（23% / 基准 27%） | 67 | 73 | 93 | 95 |

## 2. Territory 笔记（原 `TERRITORY_BANK.md`）

### T07 — Omni / speech / realtime interaction

**Why keep inhabiting it**

Speech introduces something text systems largely avoid: **physical time**. Streaming, overlap, turn-taking, codec rate, semantic/acoustic information, and latency become model variables rather than serving details.

By 2026 the territory extends beyond speech modeling itself: grounded agents increasingly observe partial input, generate, call tools, receive results, and run background tasks **while interaction continues**. This makes the transition from sequential/turn-based capability to realtime/streaming/asynchronous capability a reusable scientific object rather than a serving detail.

**Recurring assumptions**

- ASR→LLM→TTS decomposition is lossless;
- text is a sufficient intermediate representation;
- turn boundaries are discrete and externally known;
- semantic vs acoustic tokenization is a complete factorization.

**Natural observations**

- interruption / overlap handling;
- information lost at text bottlenecks;
- latency-quality tradeoffs;
- where turn-taking information lives;
- whether streaming changes representation requirements.

**High-risk failure mode**

Pure system-latency engineering with no scientific quantity.

**Anchors:** VO01–VO12.

**Current workbench:** `../../../workbench/realtime-agent-capability-transition/README.md`.

## 3. 关键论文与本目录文件

- [`KEY_PAPERS.md`](KEY_PAPERS.md)

## 4. 深读材料：`library/deep/` 中与本题材相关的章节

- [`deep/academic/GENEALOGIES_03.md`](../../deep/academic/GENEALOGIES_03.md)
  - LINEAGE 12 — Speech/Audio：从“内容 token 序列”转向“时间同步本身就是建模变量”
- [`deep/academic/GENEALOGIES_04.md`](../../deep/academic/GENEALOGIES_04.md)
  - LINEAGE 16 — Speech Tokenization：tokenizer不是前处理，它决定 speech LM 到底能学什么
- [`deep/industry/GENEALOGIES_01.md`](../../deep/industry/GENEALOGIES_01.md)
  - INDUSTRY GENEALOGY I2 — Turn-based interaction → continuous control → re-derived discrete state
- [`deep/industry/FRONTIER_DEEP_DIVE.md`](../../deep/industry/FRONTIER_DEEP_DIVE.md)
  - 10. ByteDance Seed — realtime multimodal interaction changes the event structure
- [`deep/open-artifacts/GENEALOGIES_01.md`](../../deep/open-artifacts/GENEALOGIES_01.md)
  - STARTUP GENEALOGY S03 — Full-duplex speech splits into multiple different scientific problems
- [`deep/open-artifacts/GENEALOGIES_02.md`](../../deep/open-artifacts/GENEALOGIES_02.md)
  - S19 — Audio generation now contains two opposing unification strategies
- [`deep/open-artifacts/GENEALOGIES_03.md`](../../deep/open-artifacts/GENEALOGIES_03.md)
  - S29 — Negative-result preservation: startup technical reports can be more useful than final-model papers
  - S29.1 ZONOS2: importing LLM MoE assumptions into audio breaks
  - S29.2 GQA is faster but worse in early ZONOS2 ablations
  - S29.3 Speaker embedding: more information creates a shortcut
  - S29.4 The repair is representation filtering + staged training
  - S29.5 Raw bytes beat phonemization only after scale changes the trade-off
- [`deep/open-artifacts/GENEALOGIES_04.md`](../../deep/open-artifacts/GENEALOGIES_04.md)
  - S35 — "Realtime" decomposes into multiple clocks
  - S36 — Full-duplex tool use introduces a second output clock
  - S37 — Multimodal realtime world models are multirate dynamical systems
  - S41 — Conversation-conditioned TTS vs full-duplex SpeechLM: same user experience, different model boundary
- [`deep/open-artifacts/GENEALOGIES_05.md`](../../deep/open-artifacts/GENEALOGIES_05.md)
  - S51 — Audio foundation models disagree on what should be unified
  - S52 — StepAudio 3 Gen unifies audio at the representation/generative-operator level
  - S53 — Audio generation also shows that "fast inference" is task-dependent compression
- [`deep/open-artifacts/GENEALOGIES_09_HARNESS_MATURITY_AUTORESEARCH_PROXY.md`](../../deep/open-artifacts/GENEALOGIES_09_HARNESS_MATURITY_AUTORESEARCH_PROXY.md)
  - S97 — Qwen-Audio-VAE: representation quality includes producer throughput

## 6. 最新 arXiv 入口

- 全题材通用：`../../sources/AWESOME_LISTS.md`（awesome 列表、daily-arXiv 镜像、PaperNotes、spotlight 归档）

## 7. 本仓库相关 workbench / 历史

- `workbench/realtime-computation-boundaries/`
- `workbench/realtime-agent-capability-transition/`
- `workbench/omni-recon/`
