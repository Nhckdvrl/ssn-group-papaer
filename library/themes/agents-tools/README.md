# 智能体、工具与交互（Agents / tools / interaction）

**范围：** 单/多智能体的工具使用、长程任务、harness 与环境、交互式任务状态、部署负载。
**更新：** 2026-09-30（按题材重组；内容从 `KEY_PAPERS.md`、`TERRITORY_BANK.md`、`deep/` 迁移或索引而来，未改写）。

## 1. 热度（`tools/venue_corpus`，顶会 main 接收数；ICLR 括号内为切片接收率 / 全会基准）

正则：`\b(LLM|language model)[- ]based agents?|\bagentic\b|tool[- ]use|tool calling`（粗筛，数字是量级参考）

| NeurIPS2024 | ICLR2025 | ICML2025 | NeurIPS2025 | ICLR2026 | ICML2026 | ACL2025 | EMNLP2025 | ACL2026 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 15 | 38（36% / 基准 32%） | 26 | 91 | 178（29% / 基准 27%） | 262 | 49 | 51 | 164 |

## 2. Territory 笔记（原 `TERRITORY_BANK.md`）

### T12 — Agents / search / tools

**Role:** mostly deployment-pressure and experimental-object source; not a default execution track.

Useful scientific objects:
- adaptive information acquisition;
- memory/action coupling;
- search-state evolution;
- tool semantics vs executed effects;
- long-horizon credit / correction.

**Risk**

Environment, tool schema, evaluator, and simulator engineering can dominate the scientific contribution.

**Anchors:** B08, B13.

## 3. 关键论文与本目录文件

- [`KEY_PAPERS.md`](KEY_PAPERS.md)

## 4. 深读材料：`library/deep/` 中与本题材相关的章节

- [`deep/industry/GENEALOGIES_01.md`](../../deep/industry/GENEALOGIES_01.md)
  - INDUSTRY GENEALOGY I1 — Chat request → agent loop → persistent-state economics
  - INDUSTRY GENEALOGY I3 — Bare-model benchmark → model × harness × budget × tokenizer
  - INDUSTRY GENEALOGY I4 — Static training environment → deployment-derived curriculum → learned world model
- [`deep/industry/GENEALOGIES_02.md`](../../deep/industry/GENEALOGIES_02.md)
  - INDUSTRY GENEALOGY I7 — Static capability → environment learning → experience internalization
  - INDUSTRY GENEALOGY I9 — Product usage → evaluation abstraction → training loop
  - INDUSTRY GENEALOGY I10 — More interaction time → predictable improvement, but not all time is equivalent
- [`deep/industry/GENEALOGIES_03.md`](../../deep/industry/GENEALOGIES_03.md)
  - INDUSTRY GENEALOGY I12 — Long-horizon RL changes the meaning of an “iteration”
  - INDUSTRY GENEALOGY I13 — Agent data moves from answer supervision to executable artifact supervision
- [`deep/industry/FRONTIER_DEEP_DIVE.md`](../../deep/industry/FRONTIER_DEEP_DIVE.md)
  - 1. OpenAI — GPT-5.6: efficiency stops being a model property
  - 5. Microsoft — GitHub Copilot production telemetry: agent traffic is not chatbot traffic
  - 6. Microsoft — agent workflows should not be opaque sequences
  - 7. Microsoft — Echoverse: environment quantity is no longer the bottleneck
  - 11. NVIDIA — “one frontier model for every call” is no longer the agent architecture
- [`deep/open-artifacts/FRONTIER_DEEP_DIVE.md`](../../deep/open-artifacts/FRONTIER_DEEP_DIVE.md)
  - 3. Prime Intellect — the harness becomes mutable state
  - 4. Sakana AI — harness optimization and memory as separate objects
  - 11. Cognition — long-horizon asynchronous coding as the post-training regime
  - 12. Poolside — local agentic coding as a model-design constraint
- [`deep/open-artifacts/GENEALOGIES_01.md`](../../deep/open-artifacts/GENEALOGIES_01.md)
  - STARTUP GENEALOGY S01 — Fixed harness → online harness adaptation → harness as data-generating state
  - STARTUP GENEALOGY S09 — Long-horizon R&D agents: final success separates from research process
- [`deep/open-artifacts/GENEALOGIES_02.md`](../../deep/open-artifacts/GENEALOGIES_02.md)
  - S18 — BlueLM-GUI: deployment closes the training/evaluation loop
- [`deep/open-artifacts/GENEALOGIES_03.md`](../../deep/open-artifacts/GENEALOGIES_03.md)
  - S25 — Model selection → learned cognition allocation
  - S26 — Code/UI as executable state → generated interface as world state
  - S30 — Orchestrator model vs self-modifying harness: two different answers to system complexity
- [`deep/open-artifacts/GENEALOGIES_07_FAILURE_SCALE_CONTINUAL_STRUCTURED.md`](../../deep/open-artifacts/GENEALOGIES_07_FAILURE_SCALE_CONTINUAL_STRUCTURED.md)
  - S77 — Executable artifacts have multiple roles; do not collapse them
- [`deep/open-artifacts/GENEALOGIES_09_HARNESS_MATURITY_AUTORESEARCH_PROXY.md`](../../deep/open-artifacts/GENEALOGIES_09_HARNESS_MATURITY_AUTORESEARCH_PROXY.md)
  - S92 — Harness evolution: representation → adaptation → evaluation correction → compatibility
  - S93 — SoL-Pi: auto-research must itself obey experimental discipline
  - S94 — Harness trend maturity: appearance of evaluation-correction papers is itself a signal
  - S95 — Atria Dawn: "AI scientist" becomes a division-of-labor problem
- [`deep/open-artifacts/GENEALOGIES_10_LONG_HORIZON_STATE_AND_CORRECTION.md`](../../deep/open-artifacts/GENEALOGIES_10_LONG_HORIZON_STATE_AND_CORRECTION.md)
  - S101 — Collective research memory: transcript memory → claim/provenance DAG
- [`deep/open-artifacts/GENEALOGIES_11_FINAL_FRONTIER_WAVE.md`](../../deep/open-artifacts/GENEALOGIES_11_FINAL_FRONTIER_WAVE.md)
  - S121 — Working software can be a specification source, not only a verifier
  - S122 — Composition can be scientific when interactions are the hypothesis

## 5. 博客 / 报告（`../../sources/BLOGS_REPORTS.md`）

- B02 — Alex L. Zhang — Language Model “Shape” (2026)
- B13 — Lilian Weng — LLM Powered Autonomous Agents
- B15 — Lilian Weng — Diffusion Models for Video Generation

## 6. 最新 arXiv 入口

- [jiaxianyan/icml-2026-agent-papers](https://github.com/jiaxianyan/icml-2026-agent-papers)
- [js-lee-AI/awesome-llm-agent-papers](https://github.com/js-lee-AI/awesome-llm-agent-papers)
- [VoltAgent/awesome-ai-agent-papers](https://github.com/VoltAgent/awesome-ai-agent-papers)
- [zjunlp/LLMAgentPapers](https://github.com/zjunlp/LLMAgentPapers)
- [yxf203/Awesome-Efficient-Agents](https://github.com/yxf203/Awesome-Efficient-Agents)
- [WooooDyy/LLM-Agent-Paper-List](https://github.com/WooooDyy/LLM-Agent-Paper-List)
- [Paitesanshi/LLM-Agent-Survey](https://github.com/Paitesanshi/LLM-Agent-Survey)
- [AGI-Edgerunners/LLM-Agents-Papers](https://github.com/AGI-Edgerunners/LLM-Agents-Papers)
- 全题材通用：`../../sources/AWESOME_LISTS.md`（awesome 列表、daily-arXiv 镜像、PaperNotes、spotlight 归档）

## 7. 本仓库相关 workbench / 历史

- `workbench/realtime-agent-capability-transition/`
- `workbench/scoped-context-state/`
