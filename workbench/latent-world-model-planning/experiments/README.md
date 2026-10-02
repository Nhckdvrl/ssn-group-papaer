# 实验索引｜菜单，不是关卡链

每个ID只有一个当前文件。以下全为未运行计划；可根据原生资产和新结果在运行前修订。新方法与解释实验可以并行，不要求E00→E01→所有诊断→方法严格串行。

| ID | 当前文件 | 用途 |
|---|---|---|
| E00 | [原生闭环](E00_native_baseline_and_resource_preflight.md) | 资源、加载、训练/控制接口 |
| E01 | [强基线与共用读数](E01_baseline_parity_and_candidate_logging.md) | 逐步建设，不阻止合理原型 |
| E11 | [状态/信息](E11_observation_aliasing_decision_oracle.md) | R4；I07 |
| E13 | [预测/计算](E13_explicit_implicit_matched_pilot.md) | R2；I08 |
| E14 | [轨迹监督](E14_behavior_policy_semantics_intervention.md) | R1；I09 |
| E16 | [数据配方](E16_equal_budget_data_value.md) | R1；I12 |
| E17 | [任务对齐/复用](E17_query_placement_reuse.md) | R3；I10 |
| E18 | [可靠使用/恢复](E18_trust_recovery_routing.md) | R5；I11 |
| E19 | [变化后的更新](E19_revaluation_frontier.md) | R2/R3/R5；I13 |

E02/E05/E06/E07候选/支持/oracle等诊断、E08–E10 negative实验、E12/E15历史后续方法卡已保留在[历史实验目录](../../../archive/latent-world-model-planning/pre-consolidation-2026-10-02/experiments/)，可以按需要复用，不再是许可门槛。E03/E04原metadata-only设计的无效记录保留，不重写成已运行null。

## 迁移与编号

旧E16的三份data-value/decision-excitation方案合并到当前E16；旧E17、E18各两份合并。旧文件逐项映射见[整理记录](../logs/2026-10-02-consolidation.md)。历史ID不重新分配；新增从E20起。

## 成果记录

运行前记问题、改动、对照、主读数和实际预算；运行后保存raw output/config/hash和失败情况，区分探索/确认。更严格的混杂控制由主张决定，不能把早期“条件没完全匹配”当作禁止继续改方法的理由。


## 第一波建议矩阵（可根据E00资产/计时修改）

**A / E16 — Planner-Boundary Branching (PBB)：** 首轮用一个可可靠reset的导航任务，比较NO-ADD、IID、coverage/excitation、global uncertainty、task-relevant uncertainty、decision-critical六种acquisition，1个train seed只找量级。若有明显差异，保留2–3个策略铺≥3训练seed，再加Push-T/Cube类操作任务与2–3个data budgets。真正的资源优势体现在这些独立训练可并行，不是先跑完整Cartesian product。

**B / E13 — Planner-Stage Multi-Fidelity：** 首轮用released LeWM/Fast-LeWM在两个小任务比较pure recursive、pure Fast、random high-fidelity refine、top-M refine、elite-boundary refine；优先fixed-wallclock和same candidate bank。出现compute-quality signal后才训练shared dual-head或加入DeepJEPA/长期方法。

E17/E18可以在已有checkpoint可复用时机会性并行，但不因为第一波A/B更具体就关闭R3–R5。任何pilot拿到异常或强收益后，先复核协议，再将卡数集中到最有信息增益的分支。
