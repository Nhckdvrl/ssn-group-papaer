# Territory｜紧凑latent world model与规划

状态：PROPOSED；不改变ACTIVE容量。目标ICLR/ICML/NeurIPS，视觉贡献适合时考虑CVPR；不降低问题尺度来匹配小模型。

**当前唯一入口：** [工作台README](../../workbench/latent-world-model-planning/README.md)。研究地图、方法路线和实验由[RESEARCH_PLAN](../../workbench/latent-world-model-planning/RESEARCH_PLAN.md)维护，本卡不再复制一套排序/门槛。

保留的母问题：R1数据与可规划性；R2预测对象与规划计算；R3任务对齐与复用；R4状态/记忆/不确定性；R5可靠使用与恢复。近邻是研究基础，不把某论文覆盖一个子问题视为整个territory结束。

资源优势是多独立GPU实验吞吐量，而非多节点大模型训练。原生强基线、方法试验、系统测量并行；局部seed失败不自动关闭母问题，方法从探索开始就允许。

尚无本地GPU结果或已成立科学claim。2026-10-02已将重复入口与I/E编号合并，旧材料完整保留在[历史快照](../../archive/latent-world-model-planning/pre-consolidation-2026-10-02/)。
