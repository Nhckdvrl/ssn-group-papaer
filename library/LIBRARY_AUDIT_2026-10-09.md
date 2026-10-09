# 知识库结构审计与整理 — 2026-10-09

## 审计对象与事实

以 GitHub `main` 原始完整 Git tree 为基准：`library/` 下 **19 个主题目录**、主题内 **268 个文件**（其中 `incremental-language-processing` 149、`pragmatic-inference` 69）、`deep/` 26 个 Markdown 长文、`sources/` 两个来源索引，再加顶部的 `README.md`、`KEY_PAPERS.md`、`TERRITORY_BANK.md`。这不是 268 条论文：许多是同主题文献、索引、扩展稿或扫描材料。

发现四类结构问题：

1. **主入口漏掉 4 个实际存在的主题**：`in-context-evidence-structure`、`incremental-language-processing`、`latent-world-models`、`pragmatic-inference`。主页过时，还引用了已停止的旧主线。
2. **编号冲突**：多语言 `KEY_PAPERS.md` 76 条记录只有 56 个不同编号（后追加段落复用 `ML35–ML48`）；NPC 21 条记录仅 18 个编号（复用 `NPC13–NPC15`）。多语言还存在同一论文在多个证据主题下重复解读，不能把“出现多次”误计为不同论文。
3. **知识与项目状态混淆**：部分主题页用 `workbench/xxx` 裸路径引用不再存在的计划，独立 desk-only 的模型差分计划本应是文献/方法知识，而不是长期占一个执行项目。
4. **层级不均匀**：2016–2026 的大量深读卡集中在语言处理、语用两个主题；`deep/` 存大篇历史谱系。目录体量大并非等于可以安全删重复内容，精读笔记有细粒度的 provenance / 反例 / 近邻增量。

## 已实际修复

- 顶部 [README](README.md) 作为**唯一导航入口**，列出 19/19 主题；说明科学知识、项目状态、论文草稿的存放边界，并区分深读卡与 `deep/` 历史大文。
- 两个 `KEY_PAPERS.md` 的冲突行改成唯一 ID（后续 `ML57–ML76`，`NPC19–NPC21`），完整保存每条论文描述、链接和研究角度；更正 [前缀索引](KEY_PAPERS.md)。旧编号曾指向多个不同来源，历史引用需要配合论文标题消歧。
- [模型差分测量专题](themes/interpretability-representation/MODEL_DIFFING_MEASUREMENT.md) 承接被删除工作台的 research question、强基线、实验矩阵、证据有效性和直接先验；对已有的 [工具地图](themes/interpretability-representation/INTERPRETABILITY_TOOLING_2026.md) 采用交叉链接，不重复一份独立 workbench。
- 清理 `interpretability-representation`、`architecture-memory`、`scientific-fm-ai4quant` 中明显失效的 workbench 指向。**科学 FM 的已有知识仍保留**，但不再表示 AI4Quant 独立项目在做。
- 把两个 NPC 工作台恢复保留；未动它们的实验之外的历史研究计划。

## 检验范围与仍需注意的事项

- 检查过顶部导航、主题首页及若干关键索引的**实际 Markdown 相对链接**；与旧项目相关的**代码格式裸路径**也专门做了人工核查。没有声称完成全部 265 篇主题 Markdown 的全文链路/科学事实复核。
- 多语言同论文重复出现在不同主题节（如 parallel-data 与 resource-regime）**暂不删除**；不同角度有价值。将来可由领域 owner 将共享 paper card 与主题旁注分离，但不应一次性重写现有结论。
- 题材页旧的热度数字及 2026 年研究“所有权”判断仍保持当时证据时间戳，**不是最新文献自动更新**。
- `workbench/` 的状态改动只依照用户已明确指令；AI agent 不得用知识库历史标签自动暂停任何方向。
