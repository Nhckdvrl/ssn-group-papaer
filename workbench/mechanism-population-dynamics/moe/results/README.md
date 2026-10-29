# 结果导航：三条主张怎样复核

当前科学结论见[MoE入口](../README.md)，证据等级与解释修订见[CLAIMS](../../CLAIMS.md)。本页只定位结果文件。

| 要复核的论证 | 主要完整文件 | 原始数据/来源 | 独立公式复核 |
|---|---|---|---|
| 相近品质、选择部署与R/S依赖分离 | [E162 summary](e162/summary.json) | [manifest](e162/manifest.json)、[plan](e162/plan.json) | [报告](e162_independent_audit/report.json) |
| 低预算性质的载体与完整质量 | [E156 transfer contrasts](e156/transfer_contrasts.json)、[全来源](e156/summary.json) | [manifest](e156/manifest.json)、[plan](e156/plan.json) | [报告](e156_independent_audit/report.json) |
| 相同函数的伙伴作用 | [E159 summary](e159/summary.json) | [manifest](e159/manifest.json)、[plan](e159/plan.json) | [报告](e159_independent_audit/report.json) |
| 相同函数实际消息的原配关系 | [E160正式summary](e160/retry_1/summary.json) | [正式manifest](e160/retry_1/manifest.json)；父目录保留首轮中断费用 | [报告](e160/retry_1/independent_report.json) |
| 局部几何能否解释实际消息重用 | [E163 summary](e163/summary.json) | [manifest](e163/manifest.json)、[继承范围](e163/native_inheritance.json) | [报告](e163/independent_audit.json) |
| 性质来源与实际路由通路、新55学科范围 | [E164完整矩阵](e164/summary.json) | [manifest](e164/manifest.json)、[plan](e164/plan.json)、[退出/成本](e164/execution_complete.json) | [报告](e164/independent_audit.json) |
| 另一成熟谱系的整机趋势与组件性质反向 | [E165完整矩阵](e165/summary.json) | [manifest](e165/manifest.json)、[plan](e165/plan.json)、[退出/成本](e165/execution_complete.json) | [报告](e165/independent_audit.json) |

[四面板主图](e163/figures/research_spine.png)对应[逐项来源SHA/JSON路径](e163/research_spine.json)，不新增统计检验。完整任务正确率、NLL、KL、两学科、全部来源/方向和预锁成功次集仍在各summary中。

E164/E165分别用`reproduce.py E164 all`、`reproduce.py E165 all`复现；E166目前只有冻结plan/CPU预检和运行监督，尚无完整科学结果。旧四项核心spine保持原组成与来源。CPU复核：`~/.venvs/mechpop/bin/python -B moe/scripts/reproduce.py spine verify`；从本工作台根执行，说明见[scripts](../scripts/README.md)。

## 读文件时的约定

- `manifest.status=complete`及监督退出记录共同确认完成；raw在外部耐久缓存，manifest给绝对路径/SHA/bytes。大权重和原始数组不进Git。
- `plan`绑定输入/配置/源码；`summary`是统计；`artifact_seal`绑定精确源码/输入/结果包和恢复。精确位置见[ASSETS](../ASSETS.md)。
- `attempt_*`、失败源码、旧budget与监督是证据，保留原事实。E163 PAB完整native继承，旧worker终态未观测；fresh校准/抽样/完整cross和新worker终态校验的范围在原卡，不能互相替代。
- E160/E163相同raw点值的CI有轻微差异：各用自己预先冻结的重采样种子，不改写旧区间。输入bootstrap不是训练seed。
- 早期受控结果按[实验索引](../experiments/INDEX.md)查找；E143未运行，E158原逐层网格未取得，不能从编号或缓存目录猜完成状态。
- `directory_cleanup_2026-10-29.json`只记本轮目录/文档/生成缓存整理；前一批约222.47GB重复副本清理仍见[原凭证](cleanup_2026-10-28.json)。科研原始资产未因文档整理删除。
