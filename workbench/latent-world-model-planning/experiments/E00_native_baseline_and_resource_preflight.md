# E00 — 原生基线与资源预检

- **状态：** PLANNED
- **对应：** C00（建设主张）；R01/R02/R05（风险核对，不是已观测现象）。
- **类型：** BUILD / baseline / resource measurement；不是新方法有效性实验。
- **跑前登记日期：** 2026-10-02；尚未分配执行节点，尚未运行。
- **目的：** 确认一个官方小任务具备可追溯数据、正确模型加载、可工作的规划闭环和可测成本，再决定是否扩大实验。
- **默认对象：** LeWM 原生 TwoRoom；若节点已有另一任务的可追溯完整资产，允许先用该任务，执行前写明变更与原因。
- **阳性对照：** 官方发布 checkpoint 的原生评测路径；若源状态可重放，核对一个已知可达示范的动作／终点／成功判定。不能可靠重放时，显式标记并使用官方支持的简单可达任务检查接口，不冒充 oracle。
- **阴性／无效性对照：** 随机或固定动作检查 wrapper 和记录链；无动作重复观测检查预处理；诊断性打乱 action 仅用于检查接线，不作为能力 claim。
- **噪声地板：** 相同模型、相同环境／planner seed 重跑一个 episode，记录成功、轨迹和耗时波动；不同硬件的浮点／渲染差异单独记。工程 smoke 的少量 episode 不用于估计论文级成功率差异。
- **读数：** checkpoint missing/unexpected keys；episode/split/hash；完整 resolved config；peak VRAM；data wait、train step time、planner cost calls、env/render time、完整 episode wall-clock；异常与失败原因。
- **算力：** 初次限 1 张授权 GPU、低环境并发；不默认多卡，不默认完整训练。先有限训练步确认梯度／保存／恢复，再按实测速度和正式实验目标另立训练卡。
- **决策表（跑之前写）：** 闭环正确且成本可测 → 创建正式原生复现卡并选择一个接触任务扩展；闭环失败但定位为依赖／renderer／I/O → 保留结果并修复该层或换同领域成熟实现；checkpoint／数据 provenance 不明 → 不比较性能，先补资产；成本高于可用预算 → 减少非核心数据／并发或调整实现，不以一次 smoke 关闭 territory；结果不确定 → 重放阳性对照并报告未定位因素。

## 运行前必须填入日志

执行节点匿名标签与授权范围；GPU/CPU/RAM/磁盘空间；代码 commit 和 dependency lock；数据／模型 revision 与校验和；具体命令；预检 episode 清单、种子与训练步数；资源停止条件。

禁止在运行结束后才选择 episode、阈值或“成功的 seed”。不得把这张预检卡直接升级成完整 baseline reproduction 或方法实验。

## 结果

未运行。无结果文件、无耗时估计、无 L1 及以上证据。
