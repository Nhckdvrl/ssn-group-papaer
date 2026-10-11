# 可解释性与表征分析（Interpretability / representation）

**范围：** 机制可解释性与表征分析：SAE/转码器/电路、探针与干预、steering、模型差分、跨模型表征、训练中的机制形成。
**更新：** 2026-09-30（按题材重组；内容从 `KEY_PAPERS.md`、`TERRITORY_BANK.md`、`deep/` 迁移或索引而来，未改写）。

## 1. 热度（`tools/venue_corpus`，顶会 main 接收数；ICLR 括号内为切片接收率 / 全会基准）

正则：`mechanistic interpretab|sparse auto[- ]?encoders?|\bSAEs?\b|steering vectors?|activation steering|linear probes?`（粗筛，数字是量级参考）

| NeurIPS2024 | ICLR2025 | ICML2025 | NeurIPS2025 | ICLR2026 | ICML2026 | ACL2025 | EMNLP2025 | ACL2026 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 33（34% / 基准 32%） | 40 | 50 | 89（31% / 基准 27%） | 105 | 16 | 31 | 39 |

## 2. Territory 笔记（原 `TERRITORY_BANK.md`）

### T06 — Mechanistic interpretability / model science

**Why keep inhabiting it**

The frontier has moved beyond “find another neuron/head”. By 2025–2026, major pressure sits on the **validity of mechanistic evidence itself**: what the causal mediator is, whether an explanation is identified or merely one convenient decomposition, whether interventions reflect natural computation, and whether an interpretation provides actionable information beyond cheaper behavioral/logit baselines.

**Recurring assumptions worth auditing**

- neuron / SAE feature / circuit edge is the right causal unit;
- readable or linearly decodable representation = naturally used representation;
- higher IIA / attribution score = better mechanistic explanation;
- a more expressive alignment map is always better;
- one SAE dictionary is a canonical feature inventory;
- structurally different circuits imply different mechanisms;
- successful steering proves the steered direction is the natural mechanism;
- a narrow model organism is representative of broad post-training;
- internal interpretability has comparative advantage over black-box/logit/activation-difference baselines.

**Natural observations**

- mediator complexity vs held-out intervention generalization;
- negative-control success/failure (random/wrong-task models, shuffled variables);
- cross-seed / cross-method explanation stability;
- structural difference vs functional interchangeability;
- intervention naturality / off-manifold effects;
- proxy metric vs practical/actionable outcome;
- internal model-diff signals vs simple output/logit differences;
- explanation transfer across prompts, distributions, checkpoints, and model pairs.

**Baseline / observation first**

Start from MIB / causal abstraction / SAEBench / established model-diffing harnesses. Reproduce strong simple baselines and negative controls before proposing a new mediator, SAE, circuit algorithm, or steering method.

**High-risk failure modes**

- behavior anomaly → synthetic task → probe/SAE/DAS → “mechanism”;
- another SAE/probe/lens without changing a scientific inference;
- using only one toy or narrow fine-tune and generalizing to LLM mechanisms;
- treating a flexible analysis pipeline's fit as evidence that the model itself implements the proposed abstraction.

**Deep map:** `INTERPRETABILITY_LANDSCAPE_2026.md`（本目录）  
**Tool map:** `INTERPRETABILITY_TOOLING_2026.md`（本目录）  
**Anchors:** MI01–MI05 plus MIB, SAEBench, causal abstraction, Non-Linear Representation Dilemma, 2026 SAE consistency / model-diffing work.

## 3. 关键论文与本目录文件

- [`INTERPRETABILITY_LANDSCAPE_2026.md`](INTERPRETABILITY_LANDSCAPE_2026.md)
- [`INTERPRETABILITY_TOOLING_2026.md`](INTERPRETABILITY_TOOLING_2026.md)
- **[MODEL_DIFFING_MEASUREMENT.md](MODEL_DIFFING_MEASUREMENT.md)** — 将原 desk-only workbench 的实验设计、强基线、证据效度与研究谱系凝练成可复用的知识卡（2026-10-09）。
- [`KEY_PAPERS.md`](KEY_PAPERS.md)

## 4. 深读材料：`library/deep/` 中与本题材相关的章节

- [`deep/academic/GENEALOGIES_01.md`](../../deep/academic/GENEALOGIES_01.md)
  - LINEAGE 3 — ICL Mechanism：一个极拥挤问题如何连续改变 explanatory primitive
- [`deep/academic/GENEALOGIES_04.md`](../../deep/academic/GENEALOGIES_04.md)
  - LINEAGE 17 — CoT Faithfulness：从“CoT看起来合理吗”到“到底要用什么 intervention定义 faithful”
- [`deep/industry/FRONTIER_DEEP_DIVE.md`](../../deep/industry/FRONTIER_DEEP_DIVE.md)
  - 3. OpenAI — GPT-6 Astra: CoT monitorability changed premise

## 5. 博客 / 报告（`../../sources/BLOGS_REPORTS.md`）

- B03 — Anthropic — The engineering challenges of scaling interpretability
- B04 — Anthropic Interpretability research index
- B05 — Anthropic — Open-sourcing circuit-tracing tools

## 6. 最新 arXiv 入口

- [ruizheliUOA/Awesome-Interpretability-in-Large-Language-Models](https://github.com/ruizheliUOA/Awesome-Interpretability-in-Large-Language-Models)
- [cooperleong00/Awesome-LLM-Interpretability](https://github.com/cooperleong00/Awesome-LLM-Interpretability)
- [zepingyu0512/awesome-SAE](https://github.com/zepingyu0512/awesome-SAE)
- [itsqyh/Awesome-LMMs-Mechanistic-Interpretability](https://github.com/itsqyh/Awesome-LMMs-Mechanistic-Interpretability)
- 全题材通用：`../../sources/AWESOME_LISTS.md`（awesome 列表、daily-arXiv 镜像、PaperNotes、spotlight 归档）

## 7. 本仓库相关 workbench / 历史

- `workbench/mechanism-population-dynamics/`
- **模型差分独立 workbench 已撤销**；不再将此题材误标为正在开展的项目。见 [模型差分知识卡](MODEL_DIFFING_MEASUREMENT.md)。
- [Shape/OLMo 历史架构/表征混杂审计](../architecture-memory/SHAPE_OLMO_CLOSEOUT.md)（旧 workbench 已删除）
