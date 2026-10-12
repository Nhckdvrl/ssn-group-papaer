# Incremental Interpretation & Revision — 可不断修订的研究知识库

**这不是搬运的论文文件夹，而是本 workbench 的认知中枢。** 文献源、实验历史、竞争理论与未来问题在此互相校验。它不服从 E108，也不要求保留I06/I07/I08旧故事。用户要求新增论文和研究认知**直接在 `workbench/incremental-interpretation-revision/knowledge/` 维护**，外围 `library/` 不再写第二套实质内容。

## 从知识而非文件开始

1. [**领域的科学认识总图**](00_STATE_OF_THE_FIELD.md)：本研究到底有哪几个不同构念、经典→现代思想如何递进、哪些结论是反证。
2. [**逐实验逆向拆解论文**](01_IDEA_LINEAGE_DEEP_READ.md)：逐个实验返回作者结果未知的时刻，拆竞争假说和设计动机；包括本轮完整补读的[Christianson 2001](christianson2001-thematic-roles-linger.md)、[Ceháková 2023](cehakova2023-diverse-reanalyses.md)、[Maina-Kilaas 2026](mainakilaas2026-digging-in.md)。
3. [**语义对象、因果识别与测量构念**](02_CONSTRUCT_AND_MEASUREMENT.md)：No≠世界Not、old-error reduction≠new-dependency formation；source patch/score/QA各测什么。
4. [**文献–实验交叉证据图**](03_EVIDENCE_GRAPH.md)：103张历史E卡最强正反证如何限制我们对文献的理解。
5. [**开放问题与分歧预测**](04_OPEN_PROBLEMS_AND_TESTS.md)：供自主选题，不是固定路线、静态实验菜单。
6. [**阅读与未完成校验账**](05_READING_AGENDA.md)：本轮到底读了什么、哪些旧卡要重新核验及残余阅读债务。

## 以科学问题为单位的深层专题（不是重复paper摘要）

- [01 重分析理论冲突](topics/01_REANALYSIS_THEORY.md)：2001–2026经典实验怎样区分旧痕迹、局部结构、语用、回视与任务效应。
- [02 LLM加工与测量有效性](topics/02_LM_PROCESSING_AND_VALIDITY.md)：从surprisal到自然新依赖，模型×任务×材料的识别界限。
- [03 因果绑定与真正使用](topics/03_CAUSAL_BINDING_AND_USE.md)：Hanna与Gur的实验为什么会区分机制，回看E55–90哪里还不能归因。
- [04 Belief更新与评分目标](topics/04_BELIEF_REVISION_CREDIT.md)：Belief-R、ABBEL和E91–107各自测什么，代数分解不等于神经记忆。
- [05 从领域认识长出idea](topics/05_HOW_IDEAS_GROW.md)：逐个实验回到未知结果时刻，学习最邻近论文的科学推理动作。
- [关键主张变更账](EPISTEMIC_CORRECTIONS.md)：发现过并纠正过的误记/过强推断；新反证必须更新这里。

## 所有论文怎样查？

从[**全库论文图谱 PAPER_ATLAS**](PAPER_ATLAS.md)按七个问题族查（人类修订、LM加工、测量、因果绑定、belief状态、奖励选择、方法桥接）；[结构化PAPER_CATALOG](PAPER_CATALOG.json)登记144份规范卡与3份兼容别名及其阅读状态边界。主题卡可以互相引用，但同一论文只有一个规范内容，不因为两次阅读生成两份正文。

## 历史与现代分层，不覆盖实验真相

原来的[FIELD_MAP](FIELD_MAP.md)、[阅读主索引](REVISION_READING_INDEX.md)、[历史大综述](REVISION_RESEARCH_SYNTHESIS.md)、[原阅读账](READING_LEDGER.json)为**历史版本**；阅读数与“下一步”不等于现在的科学结论。原149份迁移资产和SHA在[MIGRATION](MIGRATION.json)可追溯。本轮新合成[RESEARCH_SYNTHESIS](RESEARCH_SYNTHESIS_2026-10-12.md)、[原文复核](PRIMARY_SOURCE_REVIEW_2026-10-12.md)继续保留，但如与认识总图冲突，以来源更近期、明确标注实读范围和反证的记录为准，必须在变更日志里声明而不是暗改。

**权责**：历史实验证据看[科学审计](../AUDIT_2026-10-12.md)和[源E卡](../EXPLORATION_RECORD.md)；知识库以[维护协议](LITERATURE_MAINTENANCE.md)持续更新。文献自报精读不能自动核准，论文所属P0是研究相关性不是论文好坏；未经原文校对的事实不要当成它的特定结论。