# Game NPC Agents

**实验暂停。** E85及此前已启动任务均结束，自有worker/GPU释放，无待运行队列；恢复须用户明确指令。工作台PROPOSED、I04 PROMISING、C01–C06既有等级保持，论文正文暂缓。

中心问题：**有自身身份和目的的NPC，面对玩家提出、执行和改变合作办法，怎样选择、修订或拒绝，并产生真实游戏后果？** 当前优先矿区A（人物设定与实际战略行为），其他NPC领域仍开放。

## 阅读入口

| 需要了解什么 | 唯一入口 |
|---|---|
| 从最初接手到E85：为何实验、结果、纠偏与未解问题 | [整体进度报告](PROJECT_PROGRESS_REPORT_2026-10-16.md) |
| 已成立主张、证据等级与撤回记录 | [CLAIMS](CLAIMS.md) |
| 当前研究候选与痛点 | [ideas](ideas/README.md) · [PAIN_LOG](PAIN_LOG.md) |
| 工作规则、暂停、资源和授权 | [AGENTS](AGENTS.md) |
| 已恢复的系统、环境、缓存与资产 | [BASELINES](BASELINES.md) |
| 领域、强近邻、论文与源码事实 | [knowledge](knowledge/README.md) |
| 原始设计与完整结果说明 | [experiments](experiments/README.md)，79张卡的索引在整体报告附表 |
| 最终统计、负结果、来源和成本 | [results](results/README.md) |
| 保留代码、复算与旧文件精确恢复 | [scripts](scripts/README.md) |
| 按日过程记录 | [logs/2026-10-16](logs/2026-10-16.md)及同目录其他日期 |

阶段报告已合并为一份整体报告，运行设置/独有范围回到实验卡，历史决定回到按日日志；不再多页复制“最新完成”。一次性脚本、重复综合笔记和重复图导出从当前树清理，原始负结果和最终统计保留。清理前完整版本为Git `af7564ff`，不另建归档目录。

完整raw、世界状态、模型及权重在`/home/xiang/.cache/game-npc-research/`，具体pin/路径按manifest；GitHub的轻量结果不等于raw已异地备份。目录整理没有启动研究实验或改变科学结论。
