# AI4Quant Research Topic Search

> 独立于仓库原有 NLP / Agent / Vision 等选题线的 AI4Quant 研究选题工作区。

## 目标

寻找能够形成 **ICML / ICLR / NeurIPS Main** 级 scientific contribution 的 AI4Quant 问题；若 scientific object 涉及 LLM / language / agents，则同时以 **ACL / EMNLP / NAACL Main / TACL** 校准。

这里不收录“AI 方法 + 金融数据集 → 更高 Sharpe”式项目，也不把普通 AI4Finance successor paper 当成默认生成器。

核心搜索原则：

> 不问“AI 能给 quant 做什么”；分别理解 AI 当前真正不知道什么、quant 当前真正不知道什么，再寻找两者在哪里发生结构性碰撞。

## 目录

- `selected/`：已经通过 ownership / novelty / feasibility / minimum-pilot 审查、允许真正开始实验的题。
- `failed/`：本轮已经搜索、审计并明确 KILL / HOLD / 降级的题，防止后续重复复活。
- `NEXT_SEARCH_HANDOFF.md`：下一轮继续找新题的交接文档；包含本轮流程复盘、好题标准、动态 search heartbeat 与可直接复制的下一轮开场指令。

## 当前状态

当前正式 `PILOT-AUTHORIZED`：

1. **State Coverage ≠ Exposure Coverage** — *The Geometry of Data in Multivariate Foundation Models*
2. **Forecast Skill ≠ Structural Skill** — *Do Multivariate Foundation Models Actually Learn Error-Correcting Structure?*

每个正式题目单独注册在 `selected/<topic>/README.md` 中。

## 注册纪律

一个题只有在下面条件基本过关后才能进入 `selected/`：

- Mother question 在不知道方法名时仍然重要；
- AI 与 finance 两边都 load-bearing；
- 至少存在两个可信 competing answers；
- positive / negative / nonlinear 结果都具有科学信息；
- closest owner 不能直接写出我们的核心 scientific conclusion；
- 存在低成本、decisive 的 E01；
- 不依赖“模型赚钱了”才能成立；
- 能清楚说明为什么是 2026 年现在才变得可答。

其余题统一进入 `failed/FAILED_TOPICS.md`，标注 KILL / HOLD / SERIOUS-but-not-authorized 及原因。