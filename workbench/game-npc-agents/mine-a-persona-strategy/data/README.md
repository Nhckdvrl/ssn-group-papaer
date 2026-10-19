# 矿区A：数据与资产入口

**矿区A已终止。** 本页保存既有数据的归属与位置，不生成数据、不重新采样、不移动大raw或修改来源；证据保留不构成后续运行授权。

## 当前资产

| 资产 | 位置与用途 |
|---|---|
| 最终统计、来源／资格、负结果、成本与审计JSON／JSONL | [results](../results/README.md)，保留全部原文件内容 |
| 原实验设置、统计口径与输入版本 | [experiments](../experiments/README.md)，79张编号卡及未运行设计 |
| 已取消合作路径草案的来源索引 | [来源核对](../results/COOPERATION_PATH_SOURCE_REVIEW_2026-10-17.json)，不是新实验数据或已确认holdout |
| 完整输入、模型输出、实际投递、逐步世界状态、原生事件及失败 | `/home/xiang/.cache/game-npc-research/runs/`，按各E## manifest读取 |
| 作者源码、原quest／graph档案、论文PDF／文本与版本 | `/home/xiang/.cache/game-npc-research/sources/`及原manifest所列位置 |
| 依赖与本地环境／模型／权重 | 原cache、Conda／venv与各实验manifest；见[矿区A基线](../BASELINES.md) |
| 可复算代码及依赖边界 | [scripts](../scripts/README.md)；文件存在不代表已获准执行 |

E70–E77在`runs/e70_*`至`e77_*`；E80为`e80_*`；E81／E84按各模型profile与full目录。E85最终outcome只取`runs/e85_{gemma,32b}_recover_s{0,1}/`；旧profile／full只作精确输入、成本和历史范围，不拼成新的独立样本。其他全部E##的路径、SHA和版本以原卡／JSON／manifest为准。

## 本次迁移与历史路径

2026-10-18按用户要求，将矿区A从领域外层分离。迁移前完整版本为`caedd5c8b3a0ad041538300f2644ff1e1bc151cc`；结果、图件和大raw不因目录变化改写。历史JSON、manifest及实验命令里的路径和hash仍描述**当时**输入，不把它们替换成新来源。

| 迁移前相对`game-npc-agents/`的路径 | 当前位置 |
|---|---|
| `experiments/`、`results/`、`scripts/`、`ideas/` | `mine-a-persona-strategy/`下的同名目录 |
| 13–17日重复过程日志 | 已从当前树删除，精确历史与当前简短维护见[logs](../logs/README.md) |
| `CLAIMS.md`、`PAIN_LOG.md`、整体报告及原研究规则 | `mine-a-persona-strategy/`下同名文件 |
| `knowledge/persona-behavior/`中的领域理解／文献定位 | `mine-a-persona-strategy/knowledge/` |
| 同目录原来的6份实验、源码使用审计与轨迹读回 | `mine-a-persona-strategy/results/audits/`，不留在知识库 |
| `knowledge/papers/`中的矿区A定向论文卡 | `mine-a-persona-strategy/knowledge/papers/`；通用卡仍在外层 |
| `knowledge/GOAL_CONTROL_REVIEW.md`的17日矿区定位补核 | 并入[合作与目标定位](../knowledge/COOPERATION_AND_GOAL_POSITIONING.md#field-review-2026-10-17)，不另留重复补核页；通用谱系仍在外层 |
| 通用`SOURCES_AND_STATUS_2026-10-14.md` | 全部来源表及阅读边界并入外层领域地图的来源章节 |
| `/home/xiang/.cache/game-npc-research/`及远端资产 | 原位置不变 |

历史精确复现须按原记录取对应Git版本的代码，尤其旧报告会校验driver／dependency SHA；当前仅为适应迁移修正必要的本地路径。读取旧源码的示例：

```bash
git show caedd5c8:workbench/game-npc-agents/scripts/native_partner_performance.py
```

旧版本删除文件的恢复入口仍见[scripts说明](../scripts/README.md)。GitHub保存的轻量结果不等于完整raw已有异地备份；本次没有复制模型、原始轨迹或改变任何测量值。
