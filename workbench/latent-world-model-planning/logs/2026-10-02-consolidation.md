# 2026-10-02｜目录收敛与研究流程修正

## 基线与范围

来源commit：`8d01cbac2ca4d1f72ada0456efbbc11865d28df7`。
原latent subtree：`68694221bb6aec22b5ea28d488893c36dbcf953a`。

原目录21份顶层Markdown、24份实验卡、17份idea卡、1份日志，共63文件；未发现该subtree含代码、权重或实验结果文件。CLAIMS明确没有本地科学结果。

## 保留

完整原tree原样挂到`archive/latent-world-model-planning/pre-consolidation-2026-10-02/`，其tree SHA必须等于上述原SHA。原CLAIMS blob `7b53f3654085b724c4c728147d0877e94e9d7f78`、原日志blob `c832174d5759c7fa6dfeaf15b160931030540ecd`同时留在当前工作台。归档不构成认可旧的方向关闭/全文阅读声明；只保存可追溯材料。

## 归并表

| 原文件/组 | 当前归属 |
|---|---|
| RESEARCH_PROGRAMS、RESEARCH_MINES、FIELD_PROBLEM_MAP、PROBLEM_METHOD_MAP、DATA_PLANNABILITY_MAP | RESEARCH_PLAN 的问题—方法地图与R1–R5 |
| METHOD_LIBRARY、PROGRAM_BRANCHING、NOVELTY_GROWTH_RULES、NOVELTY_STRATEGY、POSITIONING | RESEARCH_PLAN 中方法生长与证据阶段；原文完整归档 |
| HANDOFF、LOCAL_AGENT_PROMPT、EXPERIMENT_PROGRAM | LOCAL_AGENT_PROMPT + experiments/README +唯一实验卡 |
| PAPER_LINEAGE、LITERATURE_LEDGER、CORE_PAPER_GROWTH_CASES | literature/README索引完整快照；新CORE_READINGS是本轮定向复核范围 |
| PAPER_SHAPE_TARGET | RESEARCH_PLAN §10、ASSETS §6；原文完整归档 |
| 最新I13/E19 revaluation | 当前同号保留，去掉强制普适law门槛 |
| ASSETS | 当前ASSETS保留关键入口/协议；原完整版本归档 |
| PAIN_LOG | 当前实际记录格式与风险摘要；旧风险不冒充实测 |
| E00/E01/E11/E13/E14 | 保留ID与当前唯一文件，修订研究许可/公平性 |
| E16_data_value_for_actionable_wm、E16_decision_relevant_excitation、E16_equal_budget_data_value | 当前E16_equal_budget_data_value |
| E17_query_placement_reuse、E17_query_placement_reuse_frontier | 当前E17_query_placement_reuse |
| E18_trust_recovery_oracle、E18_trust_recovery_routing | 当前E18_trust_recovery_routing |
| I10_decision_relevant_data_sufficiency | 当前I12的数据设计，历史原ID不覆盖 |
| I10_query_placement_reuse、I10_query_specialization_reuse | 当前I10_query_placement_reuse |
| I11_trust_recovery_routing、I11_trust_repair_routing | 当前I11_trust_recovery_routing |
| I12_data_value_for_planning、I12_equal_budget_data_value | 当前I12_equal_budget_data_value |
| I01–I06与其他旧E卡 | 历史保留、按需复用；不自动关闭对应母问题 |

## 研究逻辑修正

已有近邻作为强基线和灵感，不是禁入理由；方法探索从一开始允许。探索、确认与因果归因分阶段。取消残差-only、必须名次翻转/普适定律、必须oracle齐全才准改方法等局部门槛；不改变根目录研究诚信、资源与人审规则。

R1不是只问多门路线，R2不是只比两篇论文，R4不以信息不可辨造成的oracle差距指责模型；R5允许直接测试可部署策略。新颖性叙事仍必须对应实质方法/认识与证据，不能靠改名。

## 检查范围

整理初始基线为3bf456f；发布前读到新增6次提交至8d01cba，已合并I13/E19与资源形态要求，完整归档以最新tree为准。

本轮执行拟提交文件的结构、唯一ID、Markdown链接与字段检查；提交后读取tree/ref确认归档SHA及主张/日志保留。完整全仓`tools/process/check.py`需要所有其他workbench内容；当前容器无法解析GitHub域名，未声称完成全仓checker或GPU复现。实际检查结果见同目录validation记录。

实际GPU训练=0，环境评测=0，新科学主张=0。PROPOSED和其他ACTIVE分配保持不变。
