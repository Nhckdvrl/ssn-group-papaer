> **二次清理记录：** 本文件描述首次整理后的 18 个工作台快照；本轮已进一步移除 6 个 CLOSED 工作台，当前为 **12** 个。详细清理与 Git 历史恢复见 [PRUNING_2026-10-09.md](../archive/PRUNING_2026-10-09.md)。

# Workbench 整理决策与边界（2026-10-09）

## 有效的用户决定

- **保留** `npc-persona-behavior-grounding`、`npc-deception-investigability`（原样保留两份 README，虽未有实验，仍是可关注的方向）。
- **删除当前仓库树中的 workbench**：`ai4quant`、`hybrid-adaptation`（桌面提案，不保留在 archive/workbenches）。
- **先吸收为知识，再删工作台**：`model-diffing-measurement` → [模型差分测量知识卡](../library/themes/interpretability-representation/MODEL_DIFFING_MEASUREMENT.md)。专题不标成活跃研究；原提案可用 Git 历史定位（删除 HEAD 文件不等于重写历史）。
- **明确继续** `mechanism-population-dynamics`：论文版本、实验和结果全部保留。10 月 8 日旧停止说法不再作为当前决定。

## Workbench 当前范围

原 21 个研究目录，删除 3 个未开始实测的方向，**保留 18 个**（其中两个 NPC 恢复）。保留的真实实验工作台均未移动或删除。只更新总索引和 mechpop / ICES 的状态文案。没有改动 GPU 任务、实验产物、论文源码或模型权重。

| 分类 | 项目 | 处理 |
|---|---|---|
| 当前仍在推进的研究 | `mechanism-population-dynamics`、`in-context-evidence-structure`、`real-time-causalization-capability-preservation` | 保留；按用户最新科研状态判断，不依赖旧 PAUSED 字样 |
| 进行了大量实测、当前是否排卡分开记录 | `latent-world-model-planning`、`data-centric-rsi`、`incremental-interpretation-revision`、`cross-lingual-acquisition-regimes` | 保留成果、代码与下一步记录 |
| 可复用的实证/harness | `video-world-model-temporal-interfaces`、`scoped-context-state`、`realtime-agent-capability-transition`、`realtime-computation-boundaries`、`omni-recon`、`shape-olmo`、`pragmatic-inference-calibration`、`moe-route-preference` | 保留，不因为 CLOSED/PAUSED 直接删真实资产 |
| 有明确想法或重开条件的未执行方向 | `npc-persona-behavior-grounding`、`npc-deception-investigability`、`multi-llm-collaboration` | **保留**；不能简单按没有脚本就删除 |
| 无意继续的工作台 | `ai4quant`、`hybrid-adaptation` | **从 HEAD 删除**，不创建新 archive 副本 |
| 已吸收进知识库 | `model-diffing-measurement` | **从 HEAD 删除**，实验对比设计、文献近邻与风险保留在 `library/` |

## 知识库额外整理

当前 19 个题材的导航、编号冲突、死链接/过时项目引用和独立项目与知识资产的边界已同步处理；见 [知识库审计](../library/LIBRARY_AUDIT_2026-10-09.md)。有研究价值的领域论文、阅读卡和历史谱系仍留在知识库。

**备注：** 本文是项目资产盘点，不赋予任何自动开关线权限。
