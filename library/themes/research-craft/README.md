# 研究方法、测量与选题技艺（Research craft / measurement / re-attribution）

**范围：** 研究方法与选题技艺：谱系式读论文、强基线与再归因、负结果、测量有效性、从业界/开源资产中读出研究压力。
**更新：** 2026-09-30（按题材重组；内容从 `KEY_PAPERS.md`、`TERRITORY_BANK.md`、`deep/` 迁移或索引而来，未改写）。

## 1. 热度（`tools/venue_corpus`，顶会 main 接收数；ICLR 括号内为切片接收率 / 全会基准）

正则：`(re[- ]?evaluat|reproducib|negative result|evaluation (artifact|validity)|confound)`（粗筛，数字是量级参考）

| NeurIPS2024 | ICLR2025 | ICML2025 | NeurIPS2025 | ICLR2026 | ICML2026 | ACL2025 | EMNLP2025 | ACL2026 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 102 | 62（36% / 基准 32%） | 45 | 138 | 125（20% / 基准 27%） | 148 | 25 | 38 | 80 |

## 2. Territory 笔记（原 `TERRITORY_BANK.md`）

### T09 — Re-attribution / negative results / measurement

**Role**

This is a **question-forming source**, not a preferred benchmark-paper track.

Strong negative work often shows:

> the reported phenomenon is real, but the accepted explanation / measurement is wrong.

**Recurring targets**

- metric vs actual capability;
- parser/post-processing artifacts;
- decoding vs learned distribution;
- model effect vs scale/recipe effect;
- proxy vs deployed decision.

**Natural first move**

Make the strongest baseline boringly correct, then find where the claimed story survives.

**Anchors:** RC01, XD01–XD03, B01, B03.

### T10 — Cross-domain method formation: diffusion / optimization / CV

**Role**

Use these fields to learn **how questions are formed**, not to mechanically transfer methods.

Useful patterns:
- method zoo → explicit design space;
- endpoint explanation → trajectory dynamics;
- weak baseline → strong baseline overturns narrative;
- one global schedule → state/sample-dependent allocation.

**Anchors:** RC01, XD01–XD03, B14–B15.

## 3. 关键论文与本目录文件

- [`KEY_PAPERS.md`](KEY_PAPERS.md)
- [`LITERATURE_MAP.md`](LITERATURE_MAP.md)
- [`PAPER_AUTOPSIES.md`](PAPER_AUTOPSIES.md)

## 4. 深读材料：`library/deep/` 中与本题材相关的章节

- [`deep/academic/GENEALOGIES_01.md`](../../deep/academic/GENEALOGIES_01.md)
  - LINEAGE 4 — Diffusion Fast Sampling：从 solver competition 到 design-space attribution，再到局部 compute allocation
  - 6. 五条 lineage 放在一起后，新看到的 meta-pattern
- [`deep/academic/GENEALOGIES_03.md`](../../deep/academic/GENEALOGIES_03.md)
  - LINEAGE 13 — Negative / Limits Papers：强 paper 不一定发明新能力，也可以重新定位“问题到底在哪”
  - LINEAGE 14 — Optimization / SAM：成功方法的“原始解释”本身也会成为后续研究对象
- [`deep/academic/GENEALOGIES_04.md`](../../deep/academic/GENEALOGIES_04.md)
  - 19. 四条新 lineage的交叉分析
- [`deep/industry/GENEALOGIES_01.md`](../../deep/industry/GENEALOGIES_01.md)
  - INDUSTRY GENEALOGY I3 — Bare-model benchmark → model × harness × budget × tokenizer
  - INDUSTRY GENEALOGY I5 — Recent method hype → easy-regime success → objective exposed by a harder regime
  - INDUSTRY GENEALOGY I6 — Frontier AI begins changing the research-production process itself
- [`deep/industry/GENEALOGIES_02.md`](../../deep/industry/GENEALOGIES_02.md)
  - INDUSTRY GENEALOGY I9 — Product usage → evaluation abstraction → training loop
- [`deep/industry/FRONTIER_DEEP_DIVE.md`](../../deep/industry/FRONTIER_DEEP_DIVE.md)
  - 2. OpenAI — internal research acceleration: bottleneck migration in the research process
  - 8. Anthropic — evaluation conditions themselves are now part of model capability
  - 14. Cross-company convergence: five frontier shifts that appear independently
  - 15. Industry reports also reveal what NOT to chase
  - 16. Industry-derived research-pressure ledger
  - 17. What industrial material changed in our research taste
  - 18. Execution-transfer ranking
  - 19. Next industry-reading targets
  - 20. Current bottom line
- [`deep/industry/FRONTIER_SCAN.md`](../../deep/industry/FRONTIER_SCAN.md)
  - 5. Industry → academia 转译梯子
- [`deep/open-artifacts/FRONTIER_DEEP_DIVE.md`](../../deep/open-artifacts/FRONTIER_DEEP_DIVE.md)
  - 9. IFM K2-Horizon — checkpoint transparency as a scientific affordance
  - 13. Arcee AI — checkpoint lineage as a research instrument
  - 17. A new reading axis: research-instrument value
  - 18. Instrument-value gate for future topic search
  - 19. Recent startup/model-card technical-thesis map
  - 20. What is becoming saturated even in startup-land
  - 21. Most important startup-vs-incumbent difference
  - 22. Current execution-value highlights
  - 23. Final rule for HF scanning
- [`deep/open-artifacts/GENEALOGIES_01.md`](../../deep/open-artifacts/GENEALOGIES_01.md)
  - STARTUP GENEALOGY S06 — Measurement noise can come from training, not evaluation sampling
  - STARTUP GENEALOGY S10 — Public checkpoints as experimental interventions
- [`deep/open-artifacts/GENEALOGIES_02.md`](../../deep/open-artifacts/GENEALOGIES_02.md)
  - S11 — Full-scale model development often contains its own cheap-proxy science
  - S12 — Open training pipelines can preserve intermediate failures, not only successful checkpoints
  - S20 — The strongest open artifacts increasingly expose a "research ladder"
  - S21 — New execution gate: Proxy Fidelity
  - S22 — Current strongest startup/HF research-taste examples from this batch
  - S23 — Current anti-patterns strengthened by this scan
  - S24 — What this changes in future search
- [`deep/open-artifacts/GENEALOGIES_03.md`](../../deep/open-artifacts/GENEALOGIES_03.md)
  - S31 — Open model cards should preserve failure provenance
  - S32 — Current startup/open-lab source types are now visibly different
  - S33 — Updated artifact-selection heuristic
  - S34 — Current conclusion
- [`deep/open-artifacts/GENEALOGIES_04.md`](../../deep/open-artifacts/GENEALOGIES_04.md)
  - S40 — Failure discovery can become an active policy
  - S42 — Some trending HF models are instruments, not research-thesis sources
  - S43 — Artifact transparency and scientific explanation are orthogonal
  - S44 — Updated four-axis artifact score
  - S45 — Current cross-domain principle: state is increasingly multirate and consumer-relative
  - S46 — Current conclusion
- [`deep/open-artifacts/GENEALOGIES_05.md`](../../deep/open-artifacts/GENEALOGIES_05.md)
  - S56 — Updated cheap-artifact shortlist from this batch
  - S57 — New screening rule: Operator First
  - S58 — Current conclusion
- [`deep/open-artifacts/GENEALOGIES_07_FAILURE_SCALE_CONTINUAL_STRUCTURED.md`](../../deep/open-artifacts/GENEALOGIES_07_FAILURE_SCALE_CONTINUAL_STRUCTURED.md)
  - S72 — Failure provenance can be a positive research artifact
  - S73 — Open model fleets: final weights → development tree
  - S78 — New meta-genealogy: failure and openness change what a small lab can study
  - S79 — New hard rules from this batch
  - S80 — Current low-cost artifacts from this batch
  - S81 — Current conclusion
- [`deep/open-artifacts/GENEALOGIES_09_HARNESS_MATURITY_AUTORESEARCH_PROXY.md`](../../deep/open-artifacts/GENEALOGIES_09_HARNESS_MATURITY_AUTORESEARCH_PROXY.md)
  - S96 — X-AuT: cheap behavioral probes can screen compression choices before full repair
  - S98 — New canonical rule: trend maturity needs a different reading strategy
  - S99 — Research-instrument assessment for this batch
  - S100 — Current conclusion
- [`deep/open-artifacts/GENEALOGIES_10_LONG_HORIZON_STATE_AND_CORRECTION.md`](../../deep/open-artifacts/GENEALOGIES_10_LONG_HORIZON_STATE_AND_CORRECTION.md)
  - S107 — Failure-Onset Localization Gate
  - S108 — Multi-Timescale Correction Gate
  - S109 — Research Memory Provenance Gate
  - S110 — Artifact / execution audit
- [`deep/open-artifacts/GENEALOGIES_11_FINAL_FRONTIER_WAVE.md`](../../deep/open-artifacts/GENEALOGIES_11_FINAL_FRONTIER_WAVE.md)
  - S116 — Latest-release freshness and public-artifact maturity are separate axes
  - S117 — Final rule: changed premise beats company name, recency, and benchmark strength
  - S118 — Final new hard gates
  - S119 — Broad literature calibration stopping rule
  - S126 — Final artifact/freshness corrections
  - S127 — Final additions to canonical taste
  - S128 — Broad scan is now closed for real

## 5. 博客 / 报告（`../../sources/BLOGS_REPORTS.md`）

- B01 — Andrej Karpathy — A Recipe for Training Neural Networks
- B03 — Anthropic — The engineering challenges of scaling interpretability
- B16 — DeepSeek Research & News
- B17 — Qwen Research
- B18 — Google Research Blog
- B23 — PaperNotes

## 6. 最新 arXiv 入口

- 全题材通用：`../../sources/AWESOME_LISTS.md`（awesome 列表、daily-arXiv 镜像、PaperNotes、spotlight 归档）

## 7. 本仓库相关 workbench / 历史

- `search/PROCESS_DIAGNOSIS_2026-09-30.md`
- `failed/REAUDIT_2026-09-30.md`
- `tools/venue_corpus/`
