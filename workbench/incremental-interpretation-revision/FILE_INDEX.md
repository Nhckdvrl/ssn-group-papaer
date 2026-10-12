# 文件索引（2026-10-12）

当前入口：[README](README.md) → [审计](AUDIT_2026-10-12.md) → [本地知识库](knowledge/README.md) → [执行说明](EXECUTION_BRIEF.md)。Agent同时读 [AGENTS](AGENTS.md)。

## 唯一实质知识库

`knowledge/`承接原外围主题149份文件。原论文卡直接位于其下；历史总图 FIELD_MAP、REVISION_READING_INDEX、REVISION_RESEARCH_SYNTHESIS 与 READING_LEDGER 原样保留。LEGACY_README保留原主题入口。新解释以 RESEARCH_SYNTHESIS_2026-10-12 与 PRIMARY_SOURCE_REVIEW_2026-10-12 为准；[迁移清单](knowledge/MIGRATION.json)记录来源版本、文件名和身份边界。

## 不重建第二份实验历史

[EXPLORATION_RECORD](EXPLORATION_RECORD.md)逐项覆盖现存103卡，配 [原机器库存](results/EXPLORATION_INVENTORY_2026-10-08.json)检索；原 [EXPLORATION_SUMMARY](EXPLORATION_SUMMARY.md)是10月8日总结。[CLAIMS](CLAIMS.md)、[PAIN_LOG](PAIN_LOG.md)、`experiments/`、`ideas/`、`logs/`均保留历史、反证和更正。

E01/E11/E51/E53为部分完成；E97/E100含不可用模型；E108未运行。编号E02/E56–58/E61–62没有卡，不补造。卡片DONE不认证测量有效，更不认证贡献。

## 代码与结果

[结果入口](results/README.md) / [完整资产清单](results/ANALYSIS_ASSETS.json)区分Git小摘要、外置大图/CSV、固定历史版本。原机器路径与SHA不是本次已读取的证明。

新增 [forward_preflight.py](scripts/forward_preflight.py)由 E93 runner 在扩大运行前调用；[回归测试](tests/test_forward_preflight.py)、[CPU验证](audit/CPU_VERIFICATION_2026-10-12.json)只验证代码与合成例，不是原模型复跑。

旧 ROUTE/EXECUTION_BRIEF 从各自当前入口的固定commit链接恢复；不要把历史授权、在途任务或paper卡中的“下一步”当今天命令。旧未合并审计分支不作为当前主入口。
