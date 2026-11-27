# scripts

尚未编写。计划结构与要求见 [RESEARCH_PLAN §8](../RESEARCH_PLAN.md)：

- `gen_carrier.py`、`teacher_logits.py`、`train_student.py`、`encode_metrics.py`、`eval_rules.py`、`prep.py`；
- 每个脚本先在 0.5B 模型、100 条数据上冒烟，再扩展；
- 所有结果 json 都要写入配置、代码 commit、模型 / 数据 hash、硬件与 wall-clock。
