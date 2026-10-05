# PAIN_LOG — Incremental Interpretation & Revision

| ID | 日期 | 痛点 / 异常 | 复现条件 | 影响 | 下一动作 |
|---|---|---|---|---|---|
| P00 | 2026-10-05 | 直接近邻很强：ACL 2025/2026 已覆盖 GP 难度/人机比较；ACL SRW 2026 已覆盖 recovery dynamics；Findings ACL 2026 已覆盖 delayed lexical disambiguation mechanism | 文献定位 | generic GP/ambiguity story 会被立即压缩 | 把 GP 固定为 calibration；novelty 必须来自 revision structure / condition / consequence / account |
| P01 | 2026-10-05 | E00 question-type 与答案极性完全混杂（simple 全 Yes、GP question 全 No） | 276 upstream QA / 69 sets | simple>GP 不能单独证明 GP-specific 能力损失 | 主检验同题 GP/nonGP 配对；E01 构造要检查极性与语义判定 |
| P02 | 2026-10-05 | Jurayj 实际 43/19/28；blocker 与 verb substitution 不是统一的同义操作，部分 MV/RR passive 不自然 | pinned TSV 全量 audit | 自动生成会误标 gold 或把语义变化当修订响应 | 逐条审计 canonical variants，报告词汇和结构条件，保留排除记录 |

| P03 | 2026-10-05 | E00 同模型 GP effect 随 reg/rev 反向；16-prefix pooled −2.81 pp，prompt range 65.22 pp；repeat probability drift 0.0865 | 全量 E00、原协议/原生 chat/一句恢复对照 | positive control 尚不稳定，不能进入 E01 | E03 正交 query/demo/interface/instruction，并核对 FP32 数值 |

| P04 | 2026-10-05 | 1.7B 重现正方向 +19.84 pp，但 nonGP lingering accuracy=30.71%；raw specificity DiD CI 跨 0；No 的含义/输出标签/语用补全未区分 | E04 全量固定 protocol | 方向复现不等于 GP-specific interpretation instrument 已有效 | E05 改 response label/明确 assertion meaning，原题/gold 不变 |

| P05 | 2026-10-05 | Amouyal hyp5_14 simple 题写 tomato 而句子 tomatoes；hyp5_18 题问 floor 但句子 road；Jurayj 原句 had rode / burglers / boooks，部分构造主动诊断缺论元 | 逐条输入校对，全部在对应新推理之前发现 | 发布数据也不能当作 gold oracle；旧复现保留字节/标签，不能事后悄改 | E06 全69 + 事前登记67-set source-question clean；Jurayj 对称 quarantine / 不可用诊断标记；raw留cache |

| P06 | 2026-10-05 | E06 GP main-subject角色控制0–5.80%，object No题最高100%；nonGP两角色正确且event初始Yes组合31.88–47.83% | 全69 sets、两order×一句恢复；67 clean同结论 | 单个role-No/event-No不能当revision proxy；问句任务影响与语用补全仍竞争 | 人审选修复分支；术语替换未检验，不归因；不选prompt赢家 |
