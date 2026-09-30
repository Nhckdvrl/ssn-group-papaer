# 跨语言能力形成（Cross-lingual capability）

**范围：** 跨语言能力的形成：双语/平行数据、共享概念空间、多语言推理、语言特异表示。
**更新：** 2026-09-30（按题材重组；内容从 `KEY_PAPERS.md`、`TERRITORY_BANK.md`、`deep/` 迁移或索引而来，未改写）。

## 1. 热度（`tools/venue_corpus`，顶会 main 接收数；ICLR 括号内为切片接收率 / 全会基准）

正则：`(multilingual|cross[- ]lingual)`（粗筛，数字是量级参考）

| NeurIPS2024 | ICLR2025 | ICML2025 | NeurIPS2025 | ICLR2026 | ICML2026 | ACL2025 | EMNLP2025 | ACL2026 |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 24 | 29（37% / 基准 32%） | 6 | 37 | 47（25% / 基准 27%） | 34 | 118 | 139 | 138 |

## 2. Territory 笔记（原 `TERRITORY_BANK.md`）

### T14 — Cross-lingual capability formation / multilingual learning dynamics

**Why keep inhabiting it**

Modern multilingual LMs exhibit translation, NLU transfer, reasoning transfer, factual consistency, language control and shared internal representations, but recent controlled work shows these do **not** behave like one scalar “multilingual ability”.

A useful pressure is that explicit bilingual bridges can be nearly indispensable for translation while other cross-lingual tasks remain strong; meanwhile middle-layer semantic alignment can be causally important for NLU, language-specific representation can interfere with reasoning, and factual transfer is often weak/frequency-dominated.

**Recurring assumptions worth auditing**

- shared vocabulary / parallel data is necessary for cross-lingual transfer;
- stronger representation alignment always means stronger functional transfer;
- word/sentence/concept alignment is interchangeable;
- translation, NLU, reasoning and factual transfer rely on the same bridge;
- English-pivot structure is universal multilingual structure;
- final-model geometry reveals how multilinguality formed;
- more language-specific signal is always beneficial for target-language performance.

**Natural observations**

- capability-specific sensitivity to bilingual-data removal;
- lexical vs sentence vs concept alignment over training;
- transfer vs alignment dissociations;
- early vs late cross-lingual transfer;
- language-specific vs language-neutral information by layer;
- shared routing/parameter use across languages;
- target-language generation vs central semantic/reasoning computation;
- factual transfer after controlling prior exposure.

**Baseline / observation first**

Use existing expensive interventions and public trajectories before training anything large:

- MONOWEB/FINEWEB intervention models;
- XLM-R Across Time;
- BLOOM checkpoints;
- OLMo-7B factual-acquisition trajectory;
- MEXA/DALI/shared-concept-space causal tooling;
- False Friends / Macaroni for cheap controlled pretraining.

**High-risk failure modes**

- another “language X is worse than English” benchmark;
- correlating language distance/resource size with performance;
- treating English alignment as the scientific endpoint;
- one more code-switching recipe without a changed premise;
- synthetic-only mechanism claims;
- recreating company-scale multilingual pretraining/scaling studies.

**Deep map:** `CROSS_LINGUAL_CAPABILITY_FORMATION_2026.md`（本目录）  
**Anchors:** ML01–ML56.

**Current high-information pressure:** the simple “translation/parallel alignment is a causal proxy for multilinguality” lead is demoted by ICLR 2026 direct prior. The surviving pressure is a cross-paper conflict: explicit parallel alignment sometimes improves broader reasoning/understanding (JGP, OpenSeal, multi-way aligned CPT) but in already multilingual/balanced pretraining its incremental effect can collapse mainly to translation (MONOWEB, From Translation to Multilinguality). Audit whether the role of parallel data changes with prior target-language competence / acquisition regime.

## 3. 关键论文与本目录文件

- [`CROSS_LINGUAL_CAPABILITY_FORMATION_2026.md`](CROSS_LINGUAL_CAPABILITY_FORMATION_2026.md)
- [`KEY_PAPERS.md`](KEY_PAPERS.md)

## 4. 深读材料：`library/deep/` 中与本题材相关的章节

- （无）

## 6. 最新 arXiv 入口

- 全题材通用：`../../sources/AWESOME_LISTS.md`（awesome 列表、daily-arXiv 镜像、PaperNotes、spotlight 归档）

## 7. 本仓库相关 workbench / 历史

- `workbench/cross-lingual-acquisition-regimes/`
