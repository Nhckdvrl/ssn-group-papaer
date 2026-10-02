# E01：Parent substrate 与标签可识别性审计（2026-10-02）

- **状态：** DONE
- **类型：** REPRO（D1/D2，不计自由探索配额）
- **对应：** C01、C02、P01
- **问题（一句话）：** 原始任务、评分、标签和人类数据是否支持本地复现，哪些数据能识别 warranted/unwarranted inference？
- **设置：** 固定三个 parent 的 Git SHA、数据 SHA256；读全文含附录、evaluation 代码、完整公开数据。CPU 静态审计与硬件 preflight；不生成模型行为。
- **读数：** 原始行数、语言/phenomenon 数、答案平衡、重复项、非空字段、原始评分与所缺配置；license 标签与 inference-choice 标签分开，缺失为 null。Wavelength graded human distribution 保持 graded。
- **阳性对照：** 原 CSV 首末项跨格式往返一致；金标回灌 scorer 100%、错标 0%；oracle 与交换答案 fixtures 验证解析。
- **噪声地板 + MIE：** 静态计数/hash 完全可重复；任何丢项或捏造标签阻止后续推断。技术审计无人群 CI，不报告伪 CI。
- **混杂审计：** 固定字段映射/来源版本；不同难度任务的 accuracy 差不能直接解释 bias；训练污染未知；sampling 暂无关；无筛项。
- **决策表（跑之前写）：** A protocol/标签齐全 → E02 原样复现；B 缺配置 → 记录 reproduction gap，先客观评分与现代模型 smoke，不声称复现官方数字；C 无 inference-choice 或 matched literal pair → SDT 不可识别，不自动补造标签；不确定 → 全量核对并写未核对项。
- **算力预算：** 0 GPU·时，CPU 与下载。**实际：** 待记录。

## 结果
待运行。
