# 关闭记录 — Pragmatic Inference Calibration — 2026-10-03

- **决定人：** 用户（本会话明确指令）；执行者root。
- **人类指令：** “清理一下实验遗产吧，这个题我们不做了，但是环境和模型可以暂时保留”。授权已给定，不再要求重复确认。
- **证据类别：** H：用户终止继续投入；A/C：有限检验提供实验与测量可行性背景。baseline、系统measurement、positioning、论文形态卡已完成后作出此决定，不使用桌面近邻判断自动关线。
- **理由：** 用户明确停止本题；有限重建未形成可迁移的新条件结构。没有声明原territory在逻辑上不成立，也不推测用户未说明的其他理由。
- **证据：** [E65](experiments/E65-global-answer-transport.md)三表述×两来源split，global映射误差降低90.9%–96.2%；残余human距离均值.004–.019，CI不支持等价零。E66原human桥梁成立但三态许可未裁决；E67阶段pair控制114/128、97/128，顺序未过gate；E68正常Qwen控制128/128、127/128，不构成论文增量。详细数字/CI见[验收](logs/finite-reconstruction-2026-10-03.md)。
- **学到的事实：** 基线数据类别不能自动转成候选级许可；人群分布不是内在belief；全局答案变尖可预测任务分布变化；UI/任务/顺序/控制必须与同一研究对象对应。
- **状态变更：** PROPOSED→CLOSED；README、总登记表、终态账本同步。无作业/队列运行，不新增探索。
- **首次清理时保留：** 环境、全部模型及revision/completion markers、约20MiB辅助环境包、最终四实验卡/六汇总/关闭记录/论文卡。
- **首次清理时删除：** 本地任务raw/data/标注/上游副本/PDF/图/日志、旧实验脚本/卡片/中间汇总/缓存；[实际清单](results/project-retirement-2026-10-03.json)。当时模型922项元数据未变，环境路径与依赖保留。
- **后续清理（2026-10-03）：** 用户明确同意删除全部模型；已移除`/data1/xiangding/work/pragmatic-inference-calibration/models`下20个模型目录及9个关联清单文件，环境、`pdf-tools`、`download-tools`保留。模型约361GiB；删除后`/data1`显示约3.1TiB可用空间。
- **恢复边界：** 旧代码/小汇总可从[Git快照](https://github.com/Nhckdvrl/ssn-group-papaer/tree/51a578c10b6ca1e7337669281a890e1f84265614/workbench/pragmatic-inference-calibration)恢复；未进Git的raw已实际删除，不能从Git恢复。原公开数据以后可以重新取得，不保留本地副本。
- **重开：** 仅人明确重新授权；没有agent自动重开条件或定时监控。
- **跨项目：** 模型与环境可复用，测量教训留本目录与论文知识库；不再新建失败题目卡扩大记录。
