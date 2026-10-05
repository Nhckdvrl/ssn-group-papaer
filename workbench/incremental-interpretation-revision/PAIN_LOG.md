# PAIN_LOG — Incremental Interpretation & Revision

| ID | 日期 | 痛点 / 异常 | 复现条件 | 影响 | 下一动作 |
|---|---|---|---|---|---|
| P00 | 2026-10-05 | 直接近邻很强：ACL 2025/2026 已覆盖 GP 难度/人机比较；ACL SRW 2026 已覆盖 recovery dynamics；Findings ACL 2026 已覆盖 delayed lexical disambiguation mechanism | 文献定位 | generic GP/ambiguity story 会被立即压缩 | 把 GP 固定为 calibration；novelty 必须来自 revision structure / condition / consequence / account |
| P01 | 2026-10-05 | E00 question-type 与答案极性完全混杂（simple 全 Yes、GP question 全 No） | 276 upstream QA / 69 sets | simple>GP 不能单独证明 GP-specific 能力损失 | 主检验同题 GP/nonGP 配对；E01 构造要检查极性与语义判定 |
| P02 | 2026-10-05 | Jurayj 实际 43/19/28；blocker 与 verb substitution 不是统一的同义操作，部分 MV/RR passive 不自然 | pinned TSV 全量 audit | 自动生成会误标 gold 或把语义变化当修订响应 | 逐条审计 canonical variants，报告词汇和结构条件，保留排除记录 |
